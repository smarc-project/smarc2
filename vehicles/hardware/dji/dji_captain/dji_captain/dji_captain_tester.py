#!/usr/bin/env python3

import sys
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile

from std_msgs.msg import Float32, Int8, String
from sensor_msgs.msg import Joy
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped
from geographic_msgs.msg import GeoPoint

from smarc_msgs.msg import Topics as SmarcTopics
from dji_msgs.msg import Topics as DjiTopics
from dji_msgs.msg import PsdkTopics as PSDKTopics


class DjiCaptainPubTest():
    def __init__(self, node: Node):
        self._node = node

        self._node.declare_parameter("timeout_sec", 10.0)
        self.TIMEOUT_SEC = (
            self._node.get_parameter("timeout_sec")
            .get_parameter_value()
            .double_value
        )

        self.received = {}

        expected_topics = [
            (DjiTopics.CAPTAIN_STATUS_STR_TOPIC, String),
            (DjiTopics.LABELED_UTM_TOPIC, String),
            (DjiTopics.BASE_LINK_IN_MAP_TOPIC, PoseStamped),

            (SmarcTopics.VEHICLE_HEALTH_TOPIC, Int8),
            (SmarcTopics.ODOM_TOPIC, Odometry),
            (SmarcTopics.HEADING_TOPIC, Float32),
            # skip course and speed because the psdk faker publishes
            # 0 velocity, so there is no course or speed...
            # (SmarcTopics.COURSE_TOPIC, Float32),
            (SmarcTopics.SPEED_TOPIC, Float32),
            (SmarcTopics.POS_LATLON_TOPIC, GeoPoint),
            (SmarcTopics.BATTERY_PERCENT_TOPIC, Float32),
            (SmarcTopics.ALTITUDE_TOPIC, Float32),
        ]

        # Keep subscription objects alive.
        self.subscriptions_ = []

        for topic, msg_type in expected_topics:
            self.received[topic] = False

            sub = self._node.create_subscription(
                msg_type,
                topic,
                lambda msg, topic=topic: self._topic_cb(topic),
                10,
            )
            self.subscriptions_.append(sub)

        self.start_time = self._node.get_clock().now()
        self.done = False
        self.success = False

        self.timer = self._node.create_timer(0.1, self._check)

        self._node.get_logger().info(
            f"Waiting up to {self.TIMEOUT_SEC:.1f}s for "
            f"{len(self.received)} expected topics..."
        )

    def _topic_cb(self, topic):
        if self.received[topic]:
            return

        self.received[topic] = True
        self._node.get_logger().info(f"Received: {topic}")

    def _check(self):
        if self.done:
            return

        # Finish immediately if everything arrived.
        if all(self.received.values()):
            self.success = True
            self.done = True
            self._node.get_logger().info("SUCCESS: all expected topics received.")
            return

        elapsed = (self._node.get_clock().now() - self.start_time).nanoseconds * 1e-9

        if elapsed >= self.TIMEOUT_SEC:
            missing = [
                topic
                for topic, got_it in self.received.items()
                if not got_it
            ]

            self.success = False
            self.done = True

            self._node.get_logger().error(
                "FAILURE: timed out waiting for topics:\n  "
                + "\n  ".join(missing)
            )


def main(args=None):
    rclpy.init(args=args)
    node = Node("dji_captain_tester")

    tester = DjiCaptainPubTest(node)

    while rclpy.ok() and not tester.done:
        rclpy.spin_once(node, timeout_sec=0.1)

    success = tester.success

    node.destroy_node()
    rclpy.shutdown()

    # Gotta tell bash success/fail
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()