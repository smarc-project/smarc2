from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from std_msgs.msg import Float32, Empty
from smarc_msgs.msg import Topics as SmarcTopics
from sam_msgs.msg import Topics as SamTopics


class SAMStatusPublisher:
    """Bridge SAM status inputs and retain the latest safety-relevant state."""

    def __init__(self, node: Node):
        self._node = node
        self._battery_percent = None
        self._last_battery_time = None
        self._heartbeat_received = False
        self._last_heartbeat_time = None
        self._abort_latched = False
        self._create_publishers()
        self._create_subscribers()

    def _create_publishers(self):
        self.battery_percent_pub = self._node.create_publisher(
            Float32, SmarcTopics.BATTERY_PERCENT_TOPIC, 10
        )
        self.heartbeat_pub = self._node.create_publisher(
            Empty, SmarcTopics.BT_HEARTBEAT_TOPIC, 10
        )
        self.abort_pub = self._node.create_publisher(
            Empty, SmarcTopics.ABORT_TOPIC, 10
        )

        self._node.get_logger().info("SAMStatusPublisher publishers have been created.")

    def _create_subscribers(self):
        self.abort_sub = self._node.create_subscription(
            Empty, SamTopics.ABORT_TOPIC, self._abort_callback, 10
        )
        self.bt_heartbeat_sub = self._node.create_subscription(
            Empty, SamTopics.HEARTBEAT_TOPIC, self._heartbeat_callback, 10
        )
        self.battery_status_sub = self._node.create_subscription(
            BatteryState, SamTopics.BATTERY_STATUS_TOPIC, self._battery_callback, 10
        )

        self._node.get_logger().info(
            "SAMStatusPublisher subscribers have been created."
        )

    def _abort_callback(self, msg: Empty):
        self._abort_latched = True
        self.abort_pub.publish(msg)

    def _heartbeat_callback(self, msg: Empty):
        self._heartbeat_received = True
        self._last_heartbeat_time = self._node.get_clock().now()
        self.heartbeat_pub.publish(msg)

    def _battery_callback(self, msg: BatteryState):
        if msg.percentage is None:
            self._node.get_logger().warn(
                "Battery percentage not available, not publishing."
            )
            return
        self._battery_percent = msg.percentage
        self._last_battery_time = self._node.get_clock().now()
        self._node.get_logger().info(
            f"Publishing battery percentage: {self._battery_percent:.2f}%"
        )
        self.battery_percent_pub.publish(Float32(data=self._battery_percent))

    def battery_is_fresh(self, max_age_seconds: float) -> bool:
        """Return whether a valid battery reading was received recently."""
        return self._is_fresh(self._last_battery_time, max_age_seconds)

    def heartbeat_is_fresh(self, max_age_seconds: float) -> bool:
        """Return whether a SAM heartbeat was received recently."""
        return self._is_fresh(self._last_heartbeat_time, max_age_seconds)

    def _is_fresh(self, received_at, max_age_seconds: float) -> bool:
        if received_at is None:
            return False
        return (self._node.get_clock().now() - received_at).nanoseconds <= (
            max_age_seconds * 1e9
        )

    def status_str(self) -> str:
        """Create a status string for SAM status data."""
        battery = (
            f"{self._battery_percent:.1f}%"
            if self._battery_percent is not None
            else "N/A"
        )
        heartbeat = "RECEIVED" if self._heartbeat_received else "WAITING"
        abort = "ACTIVE" if self._abort_latched else "NOT ACTIVE"

        return (
            "Status:\n"
            # f">> Vehicle Health: {health}\n"
            f">> Abort: {abort}\n"
            f">> Heartbeat: {heartbeat}\n"
            f"  Battery Percent: {battery}\n"
        )
