"""The ``waraps_officer`` node: ROS topics in and out of ``WarapsOfficer``.

Nothing here decides anything. Each subscription hands its message to the
officer, and each output the officer has is a publisher here.
"""

import rclpy
from rclpy.node import Node
from smarc_action_base.gentler_action_client import GentlerActionClient
from smarc_msgs.msg import Topics
from std_msgs.msg import Empty, Int8, String

from waraps_officer.commands import dumps
from waraps_officer.officer import WarapsOfficer


class Ros2WarapsOfficer:
    def __init__(self, node: Node) -> None:
        gp = node.declare_parameter
        robot_name = gp('robot_name', '').value
        if not robot_name:
            raise ValueError('robot_name parameter is required')
        pulse_rate = gp('pulse_rate', 1.0).value
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
            # No client-wide timeout: each task's own timeout goes with its goal in send().
            client_factory=lambda ros_name: GentlerActionClient(node, ros_name),
            name=robot_name,
            rate_hz=pulse_rate,
            liveliness_s=gp('task_liveliness_timeout', 10.0).value,
            health_timeout_s=gp('health_timeout_s', 10.0).value,
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
            lambda msg: officer.handle_exec_command(msg.data, self._now_s()),
            10,
        )
        node.create_subscription(
            String,
            Topics.WARA_PS_TST_COMMAND_TOPIC,
            lambda msg: officer.handle_tst_command(msg.data, self._now_s()),
            10,
        )
        node.create_subscription(
            String,
            Topics.WARA_PS_ABORT_TOPIC,
            lambda msg: officer.abort_all(self._now_s()),
            10,
        )
        node.create_subscription(
            String,
            Topics.WARA_PS_ACTION_SERVER_HB_TOPIC,
            lambda msg: officer.track_action_server(msg.data, self._now_s()),
            10,
        )
        node.create_subscription(
            Int8,
            Topics.VEHICLE_HEALTH_TOPIC,
            lambda msg: officer.update_vehicle_health(msg.data, self._now_s()),
            10,
        )
        self._level1_sub = node.create_subscription(
            String,
            Topics.WARA_PS_HEARTBEAT_TOPIC,
            self._learn_agent_uuid_once,
            10,
        )
        node.create_timer(1.0 / pulse_rate, lambda: officer.publish_status(self._now_s()))
        node.create_timer(1.0 / gp('tick_rate', 10.0).value, lambda: officer.advance_tasks(self._now_s()))
        node.get_logger().info(f"waraps_officer '{robot_name}', pulse {pulse_rate} Hz")

    def _now_s(self) -> float:
        return self._node.get_clock().now().nanoseconds * 1e-9

    def _learn_agent_uuid_once(self, msg: String) -> None:
        """The agent uuid never changes, so stop listening once the officer has it."""
        if self._officer.learn_agent_uuid(msg.data) and self._level1_sub is not None:
            self._node.destroy_subscription(self._level1_sub)
            self._level1_sub = None


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
