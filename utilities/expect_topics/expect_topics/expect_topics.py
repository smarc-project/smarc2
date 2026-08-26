#!/usr/bin/env python3

import importlib
import subprocess
import sys
import time
import traceback
from pathlib import Path
from ament_index_python.packages import get_package_share_directory

import yaml

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    QoSProfile,
    ReliabilityPolicy,
    DurabilityPolicy,
    HistoryPolicy,
)

from rosidl_runtime_py.utilities import get_message


def resolve_topic(topic_spec: str) -> str:
    """
    Resolve either a literal ROS topic name or a Python constant.

    Examples:
        "/sam/core/odom"
            -> "/sam/core/odom"

        "smarc_msgs.msg::Topics.ODOM_TOPIC"
            -> value of smarc_msgs.msg.Topics.ODOM_TOPIC

        "dji_msgs.msg::PsdkTopics.GPS_POSITION"
            -> value of dji_msgs.msg.PsdkTopics.GPS_POSITION
    """

    if "::" not in topic_spec:
        return topic_spec

    try:
        module_name, attribute_path = topic_spec.split("::", 1)

        if not module_name:
            raise ValueError("module name is empty")

        if not attribute_path:
            raise ValueError("attribute path is empty")

        module = importlib.import_module(module_name)

        value = module
        for attribute in attribute_path.split("."):
            value = getattr(value, attribute)

    except Exception as exc:
        raise RuntimeError(
            f"Could not resolve topic '{topic_spec}': {exc}"
        ) from exc

    if not isinstance(value, str):
        raise RuntimeError(
            f"Topic '{topic_spec}' resolved to {value!r}, "
            f"which is {type(value).__name__}, not str"
        )

    return value


def parse_qos(qos_config: dict | None) -> QoSProfile:
    """
    Parse optional QoS configuration from YAML.

    Example:

        qos:
          reliability: best_effort
          durability: volatile
          depth: 10

    Defaults:
        reliability: reliable
        durability: volatile
        history: keep_last
        depth: 10
    """

    if qos_config is None:
        qos_config = {}

    if not isinstance(qos_config, dict):
        raise RuntimeError("'qos' must be a dictionary")

    depth = qos_config.get("depth", 10)

    if not isinstance(depth, int) or depth <= 0:
        raise RuntimeError(
            f"QoS depth must be a positive integer, got {depth!r}"
        )

    reliability_str = str(
        qos_config.get("reliability", "reliable")
    ).lower()

    durability_str = str(
        qos_config.get("durability", "volatile")
    ).lower()

    history_str = str(
        qos_config.get("history", "keep_last")
    ).lower()

    reliability_map = {
        "reliable": ReliabilityPolicy.RELIABLE,
        "best_effort": ReliabilityPolicy.BEST_EFFORT,
        "system_default": ReliabilityPolicy.SYSTEM_DEFAULT,
    }

    durability_map = {
        "volatile": DurabilityPolicy.VOLATILE,
        "transient_local": DurabilityPolicy.TRANSIENT_LOCAL,
        "system_default": DurabilityPolicy.SYSTEM_DEFAULT,
    }

    history_map = {
        "keep_last": HistoryPolicy.KEEP_LAST,
        "keep_all": HistoryPolicy.KEEP_ALL,
        "system_default": HistoryPolicy.SYSTEM_DEFAULT,
    }

    if reliability_str not in reliability_map:
        raise RuntimeError(
            f"Unknown QoS reliability '{reliability_str}'. "
            f"Expected one of: {', '.join(reliability_map)}"
        )

    if durability_str not in durability_map:
        raise RuntimeError(
            f"Unknown QoS durability '{durability_str}'. "
            f"Expected one of: {', '.join(durability_map)}"
        )

    if history_str not in history_map:
        raise RuntimeError(
            f"Unknown QoS history '{history_str}'. "
            f"Expected one of: {', '.join(history_map)}"
        )

    return QoSProfile(
        history=history_map[history_str],
        depth=depth,
        reliability=reliability_map[reliability_str],
        durability=durability_map[durability_str],
    )


class ExpectTopics(Node):

    def __init__(self):
        super().__init__("expect_topics")

        self.declare_parameter("timeout_sec", 10.0)
        self.declare_parameter("topics_file", "")

        self.timeout_sec = (
            self.get_parameter("timeout_sec")
            .get_parameter_value()
            .double_value
        )

        config_dir = Path(
            get_package_share_directory("expect_topics"),
            "config"
        )
        topics_file = (
            self.get_parameter("topics_file")
            .get_parameter_value()
            .string_value
        )
        topics_file = Path(config_dir, topics_file).expanduser()

        if self.timeout_sec <= 0:
            raise RuntimeError(
                f"'timeout_sec' must be > 0, got {self.timeout_sec}"
            )

        if not topics_file:
            raise RuntimeError(
                "'topics_file' ROS parameter must point to a YAML file"
            )

        yaml_config = self._load_yaml(topics_file)
        self.expected_topics = self._validate_topics(yaml_config)
        self.expected_nodes = self._validate_and_namespace_nodes(yaml_config)

        # Keyed by the resolved ROS topic/node name.
        self.received_topics: dict[str, bool] = {}
        self.received_nodes: dict[str, bool] = {}

        # Keep subscription objects alive.
        self.subs = []

        for entry in self.expected_nodes:
            node_name = entry["name"]

            if node_name in self.received_nodes:
                raise RuntimeError(f"Duplicate node name: '{node_name}'")

            self.received_nodes[node_name] = False
            self.get_logger().info(f"Expecting node: {node_name}")


        for entry in self.expected_topics:
            topic_spec = entry["topic"]
            type_name = entry["type"]

            topic = resolve_topic(topic_spec)

            if topic in self.received_topics:
                raise RuntimeError(f"Duplicate topic after resolution: '{topic}'")

            try:
                msg_type = get_message(type_name)
            except Exception as exc:
                raise RuntimeError(
                    f"Failed to load message type '{type_name}' "
                    f"for topic '{topic_spec}': {exc}"
                ) from exc

            qos = parse_qos(entry.get("qos"))

            self.received_topics[topic] = False

            if topic == topic_spec:
                self.get_logger().info(f"Expecting: {topic} [{type_name}]")
            else:
                self.get_logger().info(
                    f"Expecting: {topic} [{type_name}] "
                    f"<- {topic_spec}"
                )

            subscription = self.create_subscription(
                msg_type,
                topic,
                lambda msg, topic=topic: self._topic_callback(topic),
                qos,
            )

            self.subs.append(subscription)

        self.done = False
        self.success = False

        # Use monotonic wall time so the timeout still works if ROS sim time
        # is enabled but /clock has not started yet.
        self.start_time = time.monotonic()

        self.timer = self.create_timer(0.1, self._check)
        self.node_timer = self.create_timer(1.0, self._check_nodes)

        self.get_logger().info(
            f"Waiting up to {self.timeout_sec:.1f}s for "
            f"{len(self.received_topics)} expected topic(s)..."
        )


    def _load_yaml(self, filename: str) -> dict:
        path = Path(filename).expanduser()

        if not path.is_file():
            raise RuntimeError(f"Topics YAML file does not exist: '{path}'")

        try:
            with path.open("r") as f:
                config = yaml.safe_load(f)
        except Exception as exc:
            raise RuntimeError(f"Failed to load YAML file '{path}': {exc}") from exc

        if not isinstance(config, dict):
            raise RuntimeError(f"YAML root in '{path}' must be a dictionary")

        return config


    def _validate_and_namespace_nodes(self, config: dict) -> list[dict]:
        nodes = config.get("nodes")

        if not isinstance(nodes, list):
            raise RuntimeError("YAML must contain a 'nodes' list")
        if not nodes:
            raise RuntimeError("YAML 'nodes' list is empty")

        for index, entry in enumerate(nodes):
            if not isinstance(entry, dict):
                raise RuntimeError(f"nodes[{index}] must be a dictionary")
            if "name" not in entry:
                raise RuntimeError(f"nodes[{index}] is missing 'name'")

            node_name = entry["name"]

            if not isinstance(node_name, str) or not node_name:
                raise RuntimeError(f"nodes[{index}].name must be a non-empty string")

            if node_name[0] != "/":
                node_name = f"{self.get_namespace()}/{node_name}" if self.get_namespace() else f"/{node_name}"

            entry["name"] = node_name

        return nodes

    def _validate_topics(self, config: dict) -> list[dict]:
        topics = config.get("topics")

        if not isinstance(topics, list):
            raise RuntimeError("YAML must contain a 'topics' list")

        if not topics:
            raise RuntimeError("YAML 'topics' list is empty")

        for index, entry in enumerate(topics):

            if not isinstance(entry, dict):
                raise RuntimeError(f"topics[{index}] must be a dictionary")

            if "topic" not in entry:
                raise RuntimeError(f"topics[{index}] is missing 'topic'")

            if "type" not in entry:
                raise RuntimeError(f"topics[{index}] is missing 'type'")

            topic_spec = entry["topic"]
            type_name = entry["type"]

            if not isinstance(topic_spec, str) or not topic_spec:
                raise RuntimeError(f"topics[{index}].topic must be a non-empty string")

            if not isinstance(type_name, str) or not type_name:
                raise RuntimeError(f"topics[{index}].type must be a non-empty string")

            if "qos" in entry and not isinstance(entry["qos"], dict):
                raise RuntimeError(f"topics[{index}].qos must be a dictionary")

        return topics

    def _topic_callback(self, topic: str):
        # if it exists, and received, skip
        # if it doesnt exist, skip it too
        if self.received_topics.get(topic, True):
            return

        self.received_topics[topic] = True

        received_count = sum(self.received_topics.values())
        total_count = len(self.received_topics)

        self.get_logger().info(
            f"Received: {topic} "
            f"({received_count}/{total_count})"
        )

    def _node_callback(self, node_name: str):
        # if it exists, and received, skip
        # if it doesnt exist, skip it too
        if self.received_nodes.get(node_name, True):
            return

        self.received_nodes[node_name] = True

        received_count = sum(self.received_nodes.values())
        total_count = len(self.received_nodes)

        self.get_logger().info(
            f"Detected node: {node_name} "
            f"({received_count}/{total_count})"
        )

    def _check_nodes(self):
        try:
            result = subprocess.run(
                ["ros2", "node", "list"],
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception as exc:
            self.get_logger().warning(f"Failed to run 'ros2 node list': {exc}")
            return

        if result.returncode != 0:
            stderr = result.stderr.strip()
            self.get_logger().warning(
                f"'ros2 node list' failed with code {result.returncode}: {stderr}"
            )
            return

        for node_name in result.stdout.splitlines():
            node_name = node_name.strip()
            if not node_name:
                continue
            self._node_callback(node_name)

    def _check(self):

        if self.done:
            return

        if all(self.received_topics.values()) and all(self.received_nodes.values()):

            self.success = True
            self.done = True

            elapsed = time.monotonic() - self.start_time

            self.get_logger().info(
                f"SUCCESS: all {len(self.received_topics)} expected topics "
                f"and {len(self.received_nodes)} expected nodes "
                f"received in {elapsed:.2f}s."
            )

            self.timer.cancel()
            self.node_timer.cancel()
            return

        elapsed = time.monotonic() - self.start_time

        if elapsed < self.timeout_sec:
            return

        self.success = False
        self.done = True

        missing_topics = [
            topic
            for topic, received in self.received_topics.items()
            if not received
        ]

        received_topics = [
            topic
            for topic, got_it in self.received_topics.items()
            if got_it
        ]

        missing_nodes = [
            node
            for node, received in self.received_nodes.items()
            if not received
        ]

        received_nodes = [
            node
            for node, got_it in self.received_nodes.items()
            if got_it
        ]

        message = (
            f"FAILURE: timeout after {elapsed:.2f}s.\n"
            f"Received {len(received_topics)}/{len(self.received_topics)} topics.\n"
            f"Received {len(received_nodes)}/{len(self.received_nodes)} nodes.\n"
            f"Missing {len(missing_topics)} topic(s):"
        )

        for topic in missing_topics:
            message += f"\n  - {topic}"

        message += f"\nMissing {len(missing_nodes)} node(s):"

        for node in missing_nodes:
            message += f"\n  - {node}"

        self.get_logger().error(message)

        self.timer.cancel()
        self.node_timer.cancel()


def main(args=None):

    rclpy.init(args=args)

    node = None
    success = False

    try:
        node = ExpectTopics()

        while rclpy.ok() and not node.done:
            rclpy.spin_once(
                node,
                timeout_sec=0.1,
            )

        success = node.success

    except KeyboardInterrupt:
        print(
            "[ERROR] Topic/Node reception test interrupted.",
            file=sys.stderr,
            flush=True,
        )
        success = False

    except Exception as exc:
        print(
            f"[ERROR] Topic/Node reception test setup failed: {exc}",
            file=sys.stderr,
            flush=True,
        )
        traceback.print_exc(file=sys.stderr)
        success = False

    finally:
        if node is not None:
            node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()