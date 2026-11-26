"""The ``waraps_officer`` node: ROS topics in and out of ``WarapsOfficer``.

Nothing here decides anything. Each subscription hands its message to the
officer, and each output the officer has is a publisher here.
"""

import rclpy
from rclpy.node import Node
from smarc_msgs.msg import Topics
from std_msgs.msg import Empty, Int8, String

from waraps_officer.commands import dumps
from waraps_officer.officer import WarapsOfficer
from waraps_officer.ros_clock import now_s


class Ros2WarapsOfficer:
    def __init__(self, node: Node) -> None:
        robot_name = node.declare_parameter('robot_name', '').get_parameter_value().string_value
        if not robot_name:
            raise ValueError('robot_name parameter is required')
        pulse_rate = node.declare_parameter('pulse_rate', 1.0).get_parameter_value().double_value
        tick_rate = node.declare_parameter('tick_rate', 10.0).get_parameter_value().double_value
        liveliness_s = node.declare_parameter('task_liveliness_timeout', 10.0).get_parameter_value().double_value
        health_timeout_s = node.declare_parameter('health_timeout_s', 10.0).get_parameter_value().double_value
        self._node = node

        self._direct_info_pub = node.create_publisher(String, Topics.WARA_PS_DIRECT_EXECUTION_INFO_TOPIC, 10)
        self._tst_info_pub = node.create_publisher(String, Topics.WARA_PS_TST_EXEC_INFO_TOPIC, 10)
        self._exec_response_pub = node.create_publisher(String, Topics.WARA_PS_EXEC_RESPONSE_TOPIC, 10)
        self._exec_feedback_pub = node.create_publisher(String, Topics.WARA_PS_EXEC_FEEDBACK_TOPIC, 10)
        self._tst_response_pub = node.create_publisher(String, Topics.WARA_PS_TST_RESPONSE_TOPIC, 10)
        self._tst_feedback_pub = node.create_publisher(String, Topics.WARA_PS_TST_FEEDBACK_TOPIC, 10)
        self._executing_tasks_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_EXECUTING_TASKS_TOPIC, 10)
        self._abort_pub = node.create_publisher(Empty, Topics.ABORT_TOPIC, 10)
        self._health_pub = node.create_publisher(Int8, Topics.OFFICER_HEALTH_TOPIC, 10)

        self._officer = WarapsOfficer(
            client_factory=lambda ros_name: gentler_client(node, ros_name),
            name=robot_name,
            rate_hz=pulse_rate,
            liveliness_s=liveliness_s,
            health_timeout_s=health_timeout_s,
            publish_abort=lambda: self._abort_pub.publish(Empty()),
            publish_health=lambda level: self._health_pub.publish(Int8(data=level)),
            publish_exec_response=lambda payload: self._exec_response_pub.publish(String(data=dumps(payload))),
            publish_tst_response=lambda payload: self._tst_response_pub.publish(String(data=dumps(payload))),
            publish_exec_feedback=lambda payload: self._exec_feedback_pub.publish(String(data=dumps(payload))),
            publish_tst_feedback=lambda payload: self._tst_feedback_pub.publish(String(data=dumps(payload))),
            publish_direct_execution_info=lambda payload: self._direct_info_pub.publish(String(data=dumps(payload))),
            publish_tst_execution_info=lambda payload: self._tst_info_pub.publish(String(data=dumps(payload))),
            publish_executing_tasks=lambda payload: self._executing_tasks_pub.publish(String(data=dumps(payload))),
        )

        officer = self._officer
        node.create_subscription(
            String,
            Topics.WARA_PS_EXEC_COMMAND_TOPIC,
            lambda msg: officer.handle_exec_command(msg.data, now_s(node)),
            10,
        )
        node.create_subscription(
            String,
            Topics.WARA_PS_TST_COMMAND_TOPIC,
            lambda msg: officer.handle_tst_command(msg.data, now_s(node)),
            10,
        )
        node.create_subscription(
            String,
            Topics.WARA_PS_ABORT_TOPIC,
            lambda msg: officer.abort_all(now_s(node)),
            10,
        )
        node.create_subscription(
            String,
            Topics.WARA_PS_ACTION_SERVER_HB_TOPIC,
            lambda msg: officer.track_action_server(msg.data, now_s(node)),
            10,
        )
        node.create_subscription(
            Int8,
            Topics.VEHICLE_HEALTH_TOPIC,
            lambda msg: officer.update_vehicle_health(msg.data, now_s(node)),
            10,
        )
        self._level1_sub = node.create_subscription(
            String,
            Topics.WARA_PS_HEARTBEAT_TOPIC,
            self._learn_agent_uuid_once,
            10,
        )
        node.create_timer(1.0 / pulse_rate, lambda: officer.publish_status(now_s(node)))
        node.create_timer(1.0 / tick_rate, lambda: officer.advance_tasks(now_s(node)))
        node.get_logger().info(f"waraps_officer '{robot_name}', pulse {pulse_rate} Hz")

    def _learn_agent_uuid_once(self, msg: String) -> None:
        """The agent uuid never changes, so stop listening once the officer has it."""
        if self._officer.learn_agent_uuid(msg.data) and self._level1_sub is not None:
            self._node.destroy_subscription(self._level1_sub)
            self._level1_sub = None


def gentler_client(node: Node, ros_name: str) -> object:
    from smarc_action_base.gentler_action_client import ClientReport, GentlerActionClient
    from smarc_action_base.smarc_action_base import ActionClientState

    class _Client:
        """Hands the goal its own timeout. The client keeps one timeout_s for its life."""

        def __init__(self) -> None:
            self._client = GentlerActionClient(node, ros_name, timeout_s=None)

        @property
        def state(self) -> ActionClientState:
            return self._client.state

        def poll(self) -> ClientReport:
            return self._client.poll()

        def send(self, goal_json: str, timeout_s: float | None) -> bool:
            self._client._timeout_s = timeout_s
            return self._client.send(goal_json)

        def cancel(self) -> None:
            self._client.cancel()

        def get_ready(self) -> None:
            self._client.get_ready()

        def server_alive(self, timeout_s: float = 0.0) -> bool:
            return self._client.server_alive(timeout_s=timeout_s)

    return _Client()


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = Node('waraps_officer')
    Ros2WarapsOfficer(node)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
