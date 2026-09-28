# TODO: SMARCPublisher class that converts sam msgs to smarc msgs
import rclpy
from rclpy.node import Node
from std_msgs.msg import Empty, Int8, Float32, Float64, String
from nav_msgs.msg import Odometry
from geographic_msgs.msg import GeoPoint

from smarc_msgs.msg import Topics as SmarcTopics

class SMARCPublisher:
    def __init__(self, node: Node):
        self._node = node
        # TODO: read parameters
        # TODO: create subscribers
        self._create_publishers()
        pass

    def _create_publishers(self):
        self.odom_pub = self._node.create_publisher(Odometry, SmarcTopics.ODOM_TOPIC, 10)
        self.depth_pub = self._node.create_publisher(Float32, SmarcTopics.DEPTH_TOPIC, 10)
        self.latlon_pub = self._node.create_publisher(GeoPoint, SmarcTopics.POS_LATLON_TOPIC, 10)
        self.heading_pub = self._node.create_publisher(Float32, SmarcTopics.HEADING_TOPIC, 10)
        self.course_pub = self._node.create_publisher(Float32, SmarcTopics.COURSE_TOPIC, 10)
        self.speed_pub = self._node.create_publisher(Float32, SmarcTopics.SPEED_TOPIC, 10)
        self.altitude_pub = self._node.create_publisher(Float32, SmarcTopics.ALTITUDE_TOPIC, 10)
        # TODO: fix battery status in smarc_msgs
        # self.battery_status_pub = self._node.create_publisher(Float32, SmarcTopics.BATTERY_STATUS_TOPIC, 10)
        self.battery_percent_pub = self._node.create_publisher(Float32, SmarcTopics.BATTERY_PERCENT_TOPIC, 10)
        self.vehicle_health_pub = self._node.create_publisher(Int8, SmarcTopics.VEHICLE_HEALTH_TOPIC, 10)
        self.heartbeat_pub = self._node.create_publisher(Empty, SmarcTopics.BT_HEARTBEAT_TOPIC, 10)
        self.abort_pub = self._node.create_publisher(Empty, SmarcTopics.ABORT_TOPIC, 10)

    def _create_subscribers(self):
        pass

    ### nav ###
    def _odom_callback(self, msg):
        # TODO /dr/odom -> /smarc/odom (ODOM_TOPIC)
        # TODO /dr/odom -> /smarc/depth (DEPTH_TOPIC)
        # TODO /dr/odom -> /smarc/altitude (ALTITUDE_TOPIC)
        # TODO /dr/odom -> /smarc/latlon (LATLON_TOPIC)
        # TODO /dr/odom -> /smarc/course (COURSE_TOPIC)
        # TODO /dr/odom -> /smarc/speed (SPEED_TOPIC)
        # TODO /dr/odom -> /smarc/heading (HEADING_TOPIC)
        pass

    ### status ###
    def _battery_callback(self, msg):
        # TODO core/battery_status -> /smarc/battery_status (BATTERY_STATUS_TOPIC)
        # TODO core/battery_status -> /smarc/battery_percent (BATTERY_PERCENT_TOPIC)
        pass

    def _abort_callback(self, msg):
        # TODO /core/abort -> waraps/abort (WASA_PS_ABORT_TOPIC)
        pass

    def _heartbeat_callback(self, msg):
        # TODO core/heartbeat -> waraps/action_server_heartbeat (WARA_PS_ACTION_SERVER_HB_TOPIC)
        pass

    def _vehicle_health_callback(self, msg):
        pass

    ### tf ###
    def _tf_callback(self, msg):
        # TODO get tf from odom
        pass

    def _utm_callback(self, msg):
        pass
    
    def _odom_to_utm(self, msg):
        # TODO if no utm return
        # TODO convert odom to utm
        pass