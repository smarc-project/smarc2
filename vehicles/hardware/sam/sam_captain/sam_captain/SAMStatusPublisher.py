# TODO: publish sam status to smarc data topics
# status includes: battery, abort, heartbeat, vehicle health, abort
from rclpy.node import Node
from std_msgs.msg import Float32, Int8, Empty, String
from smarc_msgs.msg import Topics as SmarcTopics

class SAMStatusPublisher:
    def __init__(self, node: Node):
        self._node = node
        self._create_publishers()
        self._node.get_logger().info('SAMStatusPublisher publishers have been created.')

        self._create_publishers()
        self._create_subscribers()

    def _create_publishers(self):
        self.battery_percent_pub = self._node.create_publisher(Float32, SmarcTopics.BATTERY_PERCENT_TOPIC, 10)
        self.vehicle_health_pub = self._node.create_publisher(Int8, SmarcTopics.VEHICLE_HEALTH_TOPIC, 10)
        self.heartbeat_pub = self._node.create_publisher(Empty, SmarcTopics.BT_HEARTBEAT_TOPIC, 10)
        self.abort_pub = self._node.create_publisher(Empty, SmarcTopics.ABORT_TOPIC, 10)
        self.status_str_pub = self._node.create_publisher(String, "status_string", 10) # TODO: change this placeholder to smarc_topics
        
        self._node.get_logger().info('SAMStatusPublisher publishers have been created.')

    def _create_subscribers(self):
        self.abort_sub = self._node.create_subscription(Empty, SmarcTopics.ABORT_TOPIC, self._abort_callback, 10)
        self.bt_heartbeat_sub = self._node.create_subscription(Empty, SmarcTopics.HEARTBEAT_TOPIC, self._heartbeat_callback, 10)
        self.vehicle_health_sub = self._node.create_subscription(Int8, SmarcTopics.VEHICLE_HEALTH_TOPIC, self._vehicle_health_callback, 10)
        self.battery_status_sub = self._node.create_subscription(Float32, SmarcTopics.BATTERY_STATUS_TOPIC, self._battery_callback, 10)

        self._node.get_logger().info('SAMStatusPublisher subscribers have been created.')

    def _abort_callback(self, msg: Empty):
        self.abort_pub.publish(msg)

    def _heartbeat_callback(self, msg: Empty):
        self.heartbeat_pub.publish(msg)

    def _vehicle_health_callback(self, msg: Int8):
        #  TODO: add geofence check to vehicle health
        self.vehicle_health_pub.publish(msg)

    def _battery_callback(self, msg: Float32):
        self.battery_percent_pub.publish(msg)