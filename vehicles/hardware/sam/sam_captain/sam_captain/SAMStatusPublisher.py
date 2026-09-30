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
        pass

    def _create_publishers(self):
        self.battery_percent_pub = self._node.create_publisher(Float32, SmarcTopics.BATTERY_PERCENT_TOPIC, 10)
        self.vehicle_health_pub = self._node.create_publisher(Int8, SmarcTopics.VEHICLE_HEALTH_TOPIC, 10)
        self.heartbeat_pub = self._node.create_publisher(Empty, SmarcTopics.BT_HEARTBEAT_TOPIC, 10)
        self.abort_pub = self._node.create_publisher(Empty, SmarcTopics.ABORT_TOPIC, 10)
        self.status_str_pub = self._node.create_publisher(String, "status_string", 10) # TODO: change this placeholder to smarc_topics

    def _create_subbscribers(self):
        pass