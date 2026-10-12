# TODO: publish sam status to smarc data topics
# status includes: battery, abort, heartbeat, vehicle health, abort
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from std_msgs.msg import Float32, Empty
from smarc_msgs.msg import Topics as SmarcTopics
from sam_msgs.msg import Topics as SamTopics


class SAMStatusPublisher:
    def __init__(self, node: Node):
        self._node = node
        self._create_publishers()
        self._node.get_logger().info("SAMStatusPublisher publishers have been created.")
        self._battery_percent = None
        self._heartbeat_received = False
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
        self.abort_pub = self._node.create_publisher(Empty, SamTopics.ABORT_TOPIC, 10)
        # self.status_str_pub = self._node.create_publisher(String, SamTopics.STATUS_STRING_TOPIC, 10)

        self._node.get_logger().info("SAMStatusPublisher publishers have been created.")

    def _create_subscribers(self):
        self.abort_sub = self._node.create_subscription(
            Empty, SamTopics.ABORT_TOPIC, self._abort_callback, 10
        )
        self.bt_heartbeat_sub = self._node.create_subscription(
            Empty, SmarcTopics.BT_HEARTBEAT_TOPIC, self._heartbeat_callback, 10
        )
        self.battery_status_sub = self._node.create_subscription(
            BatteryState, SmarcTopics.BATTERY_PERCENT_TOPIC, self._battery_callback, 10
        )

        self._node.get_logger().info(
            "SAMStatusPublisher subscribers have been created."
        )

    def _abort_callback(self, msg: Empty):
        self._abort_latched = True
        self.abort_pub.publish(msg)

    def _heartbeat_callback(self, msg: Empty):
        self._heartbeat_received = True
        self.heartbeat_pub.publish(msg)

    def _battery_callback(self, msg: Float32):
        if msg.percentage is None:
            self._node.get_logger().warn(
                "Battery percentage not available, not publishing."
            )
            return
        self._battery_percent = msg.data
        self.battery_percent_pub.publish(Float32(data=self._battery_percent))

    def status_str(self) -> str:
        """Create a status string for SAM status data."""
        # if self._vehicle_health == SmarcTopics.VEHICLE_HEALTH_READY:
        #     health = "READY"
        # elif self._vehicle_health == SmarcTopics.VEHICLE_HEALTH_ERROR:
        #     health = "ERROR"
        # else:
        #     health = "WAITING"

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
