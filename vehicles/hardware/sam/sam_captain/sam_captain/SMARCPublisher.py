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
        # TODO: create publishers
        # TODO: create subscribers
        pass

    def _create_publishers(self):
        pass

    def _create_subscribers(self):
        pass

    ### nav ###
    def _odom_callback(self, msg):
        # TODO /dr/odom -> /smarc/odom (ODOM_TOPIC)
        # TODO /dr/odom -> /smarc/depth (DEPTH_TOPIC)
        # TODO /dr/odom -> /smarc/altitude (ALTITUDE_TOPIC)
        # TODO /dr/odom -> /smarc/latlon (LATLON_TOPIC)
        # TODO /dr/odom -> /smarc/course (COURSE_TOPIC)
        # TODO /dr/odom -> /smarc/speed (POS_LATLON_TOPIC)
        # TODO /dr/odom -> /smarc/heading (HEADING_TOPIC)
        pass

    ### status ###
    def _battery_callback(self, msg):
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