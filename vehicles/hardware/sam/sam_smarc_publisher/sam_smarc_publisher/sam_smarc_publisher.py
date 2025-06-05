import rclpy
from rclpy.node import Node
from rclpy.time import Time

from geometry_msgs.msg import PoseStamped
from geographic_msgs.msg import GeoPoint
from nav_msgs.msg import Odometry
from std_msgs.msg import Empty, Int8, Float32

from smarc_msgs.msg import Topics as SmarcTopics
from smarc_msgs.msg import DVL
from sam_msgs.msg import Topics as SamTopics
from dead_reckoning_msgs.msg import Topics as DRTopics
from sensor_msgs.msg import BatteryState

from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from tf2_ros import LookupException, ConnectivityException, ExtrapolationException
from tf2_geometry_msgs import do_transform_pose

from smarc_utilities.georef_utils import convert_enu_pose_to_heading, convert_utm_to_latlon

class SAMSMARCPublisher(Node):
    def __init__(self):
        super().__init__('sam_smarc_publisher')
        self.get_logger().info('SAM SMaRC Publisher Node has been started.')
        self._create_tf_listener()

        self._create_abort_pubsub()
        self._create_bt_heartbeat_pubsub()
        self._create_altitude_pubsub()
        self._create_battery_status_pubsub()

        self._create_odom_pubsub()

    def _create_tf_listener(self):
        self.declare_parameter('utm_zone', '34')
        self.utm_zone = self.get_parameter('utm_zone').get_parameter_value().string_value
        self.declare_parameter('utm_band', 'V')
        self.utm_band = self.get_parameter('utm_band').get_parameter_value().string_value

        self.utm_frame = f'utm_{self.utm_zone}_{self.utm_band}'
        self.get_logger().info(f'Using UTM frame: {self.utm_frame}')
        self.odom_frame = 'odom'
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

    def _create_abort_pubsub(self):
        self.abort_pub = self.create_publisher(Empty, SmarcTopics.ABORT_TOPIC, 10)
        self.abort_sub = self.create_subscription(Empty, SamTopics.ABORT_TOPIC, self.abort_callback, 10)

    def abort_callback(self, msg):
        self.abort_pub.publish(msg)

    def _create_bt_heartbeat_pubsub(self):
        self.bt_heartbeat_pub = self.create_publisher(Empty, SmarcTopics.BT_HEARTBEAT_TOPIC, 10)
        self.bt_heartbeat_sub = self.create_subscription(Empty, SamTopics.HEARTBEAT_TOPIC, self.heartbeat_callback, 10)

    def heartbeat_callback(self, msg):
        self.bt_heartbeat_pub.publish(msg)

    def _create_vehicle_health_pubsub(self):
        self.vehicle_health_pub = self.create_publisher(Int8, SmarcTopics.VEHICLE_HEALTH_TOPIC, 10)
        self.vehicle_health_sub = self.create_subscription(Int8, SamTopics.VEHICLE_HEALTH_TOPIC, self.vehicle_health_callback, 10)

    def vehicle_health_callback(self, msg):
        self.vehicle_health_pub.publish(msg)

    def _create_battery_status_pubsub(self):
        self.battery_percent_pub = self.create_publisher(BatteryState, SmarcTopics.BATTERY_PERCENT_TOPIC, 10)
        self.battery_status_sub = self.create_subscription(BatteryState, SamTopics.BATTERY_STATUS_TOPIC, self.battery_status_callback, 10)
    
    def battery_status_callback(self, msg):
        self.battery_percent_pub.publish(msg)

    def _create_altitude_pubsub(self):
        self.altitude_pub = self.create_publisher(Float32, SmarcTopics.ALTITUDE_TOPIC, 10)
        self.altitude_sub = self.create_subscription(DVL, SamTopics.DVL_TOPIC, self.dvl_callback, 10)

    def dvl_callback(self, msg):
        """
        Callback for the DVL topic. It publishes the altitude to the SMaRC topic.
        """
        self.altitude_pub.publish(Float32(data=msg.altitude))

    def _create_odom_pubsub(self):
        """
        Creates subscription from Odometry data.
        Also create all publishers for SMaRC topics that are derived from the odometry data.
        """
        self.prev_odom_msg = None
        self.current_odom_msg = None
        self.odom_sub = self.create_subscription(Odometry, DRTopics.DR_ODOM_TOPIC, self.odom_callback, 10)

        self.odom_pub = self.create_publisher(Odometry, SmarcTopics.ODOM_TOPIC, 10)
        self.depth_pub = self.create_publisher(Float32, SmarcTopics.DEPTH_TOPIC, 10)
        self.latlon_pub = self.create_publisher(GeoPoint, SmarcTopics.POS_LATLON_TOPIC, 10)
        self.heading_pub = self.create_publisher(Float32, SmarcTopics.HEADING_TOPIC, 10)

        #TODO: Publish course and speed
        self.course_pub = self.create_publisher(Float32, SmarcTopics.COURSE_TOPIC, 10)
        self.speed_pub = self.create_publisher(Float32, SmarcTopics.SPEED_TOPIC, 10)

    def odom_callback(self, msg):
        """
        Callback for the Odometry topic. It publishes the odometry data to the SMaRC topic.
        It also publishes the heading, course, speed, depth and latitude/longitude.
        """
        # Updaate Odom messages
        self.prev_odom_msg = self.current_odom_msg
        self.current_odom_msg = msg

        # Publish the odometry message
        self.odom_pub.publish(msg)
        self.depth_pub.publish(Float32(data=msg.pose.pose.position.z))

        try:
            timestamp = msg.header.stamp
            self.get_logger().info(f'Transforming odometry from {self.odom_frame} to {self.utm_frame} at time {timestamp}')
            utm_transform = self.tf_buffer.lookup_transform(self.utm_frame, self.odom_frame, timestamp)

            transform_pose = PoseStamped()
            transform_pose.pose = do_transform_pose(msg.pose.pose, utm_transform)
            transform_pose.header.frame_id = self.utm_frame
            transform_pose.header.stamp = timestamp

            compass_heading_msg = convert_enu_pose_to_heading(transform_pose.pose)
            self.heading_pub.publish(compass_heading_msg)

            latlon_msg = convert_utm_to_latlon(transform_pose)
            self.latlon_pub.publish(latlon_msg)

        except (LookupException, ConnectivityException, ExtrapolationException) as e:
            self.get_logger().error(f'Failed to transform odometry: {e}')
            return



def main(args=None):
    rclpy.init(args=args)
    node = SAMSMARCPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info('Shutting down SAM SMaRC Publisher Node.')
        node.destroy_node()
        rclpy.shutdown()