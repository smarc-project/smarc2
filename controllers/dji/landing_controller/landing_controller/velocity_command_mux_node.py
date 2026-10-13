from typing import Optional

import rclpy
from dji_msgs.msg import LandingReference, Links as DJILinks, Topics as DJITopics
from geometry_msgs.msg import TwistStamped, Vector3Stamped
from rclpy.node import Node
from rclpy.time import Time


class VelocityCommandMuxNode(Node):
    """Gate controller commands and manager overrides before publishing DJI cmd_vel.

    Stale references or commands produce zeros. After control is disabled, a
    bounded zero flush stops the last command. An optional Vector3Stamped
    output mirrors the final linear velocity for the hook Kalman filter.
    """

    def __init__(self, **node_kwargs) -> None:
        super().__init__("landing_velocity_command_mux", **node_kwargs)

        # Topics and fallback frame.
        self.declare_parameter("robot_name", "M350")
        robot_name = str(self.get_parameter("robot_name").value)

        # Publish through the DJI captain's cmd_vel abstraction.
        self.declare_parameter("controller_command_topic", DJITopics.CONTROLLER_CMD_TOPIC)
        self.declare_parameter("reference_topic", DJITopics.REFERENCE_TOPIC)
        self.declare_parameter("output_topic", DJITopics.VELOCITY_SETPOINT_TOPIC)

        # Optional Vector3Stamped mirror for HookKalmanFilter.
        self.declare_parameter("mirror_vector_topic", "")

        # Fallback only. Normally the actual frame comes from the
        # LandingReference / controller command.
        self.declare_parameter("controller_frame", f"{robot_name}/{DJILinks.BASE_LINK}")

        # Watchdog timing.
        self.declare_parameter("publish_rate_hz", 50.0)
        self.declare_parameter("controller_timeout_s", 0.15)
        self.declare_parameter("reference_timeout_s", 0.25)
        self.declare_parameter("zero_flush_cycles", 8)

        self._latest_command: Optional[TwistStamped] = None
        self._latest_reference: Optional[LandingReference] = None
        self._was_enabled = False
        self._flush_remaining = 0

        controller_topic = str(self.get_parameter("controller_command_topic").value)
        reference_topic = str(self.get_parameter("reference_topic").value)
        self.create_subscription(TwistStamped, controller_topic, self._command_callback, 20)
        self.create_subscription(LandingReference, reference_topic, self._reference_callback, 20)

        output_topic = str(self.get_parameter("output_topic").value)
        self._publisher = self.create_publisher(TwistStamped, output_topic, 20)
        self.get_logger().info(f"Landing velocity mux output: {output_topic} [TwistStamped]")

        mirror_topic = str(self.get_parameter("mirror_vector_topic").value)
        self._mirror_publisher = None
        if mirror_topic:
            self._mirror_publisher = self.create_publisher(Vector3Stamped, mirror_topic, 20)
            self.get_logger().info(
                "Mirroring final landing velocity command as "
                f"Vector3Stamped on {mirror_topic}"
            )

        rate = float(self.get_parameter("publish_rate_hz").value)
        if rate <= 0.0:
            raise ValueError("publish_rate_hz must be positive")
        self.create_timer(1.0 / rate, self._publish)

    def _command_callback(self, message: TwistStamped) -> None:
        self._latest_command = message

    def _reference_callback(self, message: LandingReference) -> None:
        self._latest_reference = message

    @staticmethod
    def _age(now: Time, stamp) -> float:
        return max(0.0, (now - Time.from_msg(stamp)).nanoseconds * 1e-09)

    def _fallback_frame(self) -> str:
        return str(self.get_parameter("controller_frame").value)

    def _reference_frame(self) -> str:
        """Prefer the controller frame published by the landing manager."""
        if self._latest_reference is not None and self._latest_reference.controller_frame:
            return str(self._latest_reference.controller_frame)

        return self._fallback_frame()

    def _zero_message(self, now: Time, frame_id: Optional[str] = None) -> TwistStamped:
        message = TwistStamped()
        message.header.stamp = now.to_msg()
        message.header.frame_id = frame_id if frame_id else self._reference_frame()
        return message

    def _publish_output(self, message: TwistStamped) -> None:
        self._publisher.publish(message)
        if self._mirror_publisher is None:
            return

        mirror = Vector3Stamped()
        mirror.header = message.header
        mirror.vector = message.twist.linear
        self._mirror_publisher.publish(mirror)

    def _publish(self) -> None:
        now = self.get_clock().now()

        # Reference watchdog
        if self._latest_reference is None:
            self.get_logger().info(
                "Velocity mux inactive: no landing reference",
                throttle_duration_sec=2.0,
            )
            self._handle_disabled(now)
            return

        reference_age = self._age(now, self._latest_reference.header.stamp)
        reference_timeout = float(self.get_parameter("reference_timeout_s").value)
        if reference_age > reference_timeout:
            self.get_logger().warning(
                "Velocity mux inactive: landing reference stale "
                f"({reference_age:.3f}s > "
                f"{reference_timeout:.3f}s)",
                throttle_duration_sec=2.0,
            )
            self._handle_disabled(now)
            return

        # Manager enable
        if not self._latest_reference.control_enabled:
            self.get_logger().info(
                "Velocity mux inactive: control disabled by "
                "landing manager",
                throttle_duration_sec=2.0,
            )
            self._handle_disabled(now)
            return

        # Safety override
        if self._latest_reference.override_active:
            output = self._zero_message(now, self._reference_frame())
            output.twist.linear.x = float(self._latest_reference.override_velocity.x)
            output.twist.linear.y = float(self._latest_reference.override_velocity.y)
            output.twist.linear.z = float(self._latest_reference.override_velocity.z)
            self._publish_output(output)
            self._was_enabled = True
            self._flush_remaining = int(self.get_parameter("zero_flush_cycles").value)
            return

        # Controller watchdog
        if self._latest_command is None:
            self.get_logger().warning(
                "Velocity mux enabled but no controller command "
                "has been received",
                throttle_duration_sec=2.0,
            )
            self._publish_output(self._zero_message(now, self._reference_frame()))
            return

        controller_age = self._age(now, self._latest_command.header.stamp)
        controller_timeout = float(self.get_parameter("controller_timeout_s").value)
        if controller_age > controller_timeout:
            self.get_logger().warning(
                "Velocity mux enabled but controller command stale "
                f"({controller_age:.3f}s > "
                f"{controller_timeout:.3f}s)",
                throttle_duration_sec=2.0,
            )
            self._publish_output(self._zero_message(now, self._reference_frame()))
            self._was_enabled = True
            self._flush_remaining = int(self.get_parameter("zero_flush_cycles").value)
            return

        # Normal LQR command
        command_frame = (
            self._latest_command.header.frame_id
            if self._latest_command.header.frame_id
            else self._reference_frame()
        )
        output = self._zero_message(now, command_frame)
        output.twist.linear.x = float(self._latest_command.twist.linear.x)
        output.twist.linear.y = float(self._latest_command.twist.linear.y)
        output.twist.linear.z = float(self._latest_command.twist.linear.z)
        output.twist.angular.x = float(self._latest_command.twist.angular.x)
        output.twist.angular.y = float(self._latest_command.twist.angular.y)
        output.twist.angular.z = float(self._latest_command.twist.angular.z)
        self._publish_output(output)
        self._was_enabled = True
        self._flush_remaining = int(self.get_parameter("zero_flush_cycles").value)

    def _handle_disabled(self, now: Time) -> None:
        if self._was_enabled:
            self._was_enabled = False
            self._flush_remaining = int(self.get_parameter("zero_flush_cycles").value)
        if self._flush_remaining <= 0:
            return

        self._publish_output(self._zero_message(now, self._reference_frame()))
        self._flush_remaining -= 1


def main(args=None) -> None:
    rclpy.init(args=args)
    node = VelocityCommandMuxNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

        # ROS may already have shut the context down while handling SIGINT.
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
