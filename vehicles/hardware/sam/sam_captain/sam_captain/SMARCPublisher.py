# TODO: SMARCPublisher class that converts sam msgs to smarc msgs
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Empty, Int8, Float32, String
from nav_msgs.msg import Odometry
from geographic_msgs.msg import GeoPoint
from sensor_msgs.msg import BatteryState

from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from tf2_ros import LookupException, ConnectivityException, ExtrapolationException
from tf2_geometry_msgs import do_transform_pose

from smarc_msgs.msg import Topics as SmarcTopics
from dead_reckoning_msgs.msg import Topics as DRTopics
from sam_msgs.msg import Topics as SamTopics
from smarc_utilities.georef_utils import (
    compute_course_from_two_poses,
    compute_speed_from_two_poses,
    convert_enu_pose_to_heading,
    convert_utm_to_latlon,
)

class SMARCPublisher:
    def __init__(self, node: Node):
        self._node = node
        self._node.get_logger().info('SMARCPublisher has been initialized.')
        self._node.declare_parameter('robot_name', 'sam')
        self.robot_name = self._node.get_parameter(
            'robot_name').get_parameter_value().string_value
        self.odom_frame = f'{self.robot_name}/odom'
        self.utm_frame = None
        self.prev_pose_utm = None
        self.current_pose_utm = None
        self._create_tf_listener()
        self._create_publishers()
        self._create_subscribers()

    def _create_tf_listener(self):
        self._node.get_logger().info(f'Using odom frame: {self.odom_frame}')
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self._node)

    def _create_publishers(self):
        ### nav publishers ###
        self.odom_pub = self._node.create_publisher(Odometry, SmarcTopics.ODOM_TOPIC, 10)
        self.depth_pub = self._node.create_publisher(Float32, SmarcTopics.DEPTH_TOPIC, 10)
        self.latlon_pub = self._node.create_publisher(GeoPoint, SmarcTopics.POS_LATLON_TOPIC, 10)
        self.heading_pub = self._node.create_publisher(Float32, SmarcTopics.HEADING_TOPIC, 10)
        self.course_pub = self._node.create_publisher(Float32, SmarcTopics.COURSE_TOPIC, 10)
        self.speed_pub = self._node.create_publisher(Float32, SmarcTopics.SPEED_TOPIC, 10)
        self.altitude_pub = self._node.create_publisher(Float32, SmarcTopics.ALTITUDE_TOPIC, 10)
        ### status publishers ###
        self.battery_percent_pub = self._node.create_publisher(Float32, SmarcTopics.BATTERY_PERCENT_TOPIC, 10)
        self.vehicle_health_pub = self._node.create_publisher(Int8, SmarcTopics.VEHICLE_HEALTH_TOPIC, 10)
        self.heartbeat_pub = self._node.create_publisher(Empty, SmarcTopics.BT_HEARTBEAT_TOPIC, 10)
        self.abort_pub = self._node.create_publisher(Empty, SmarcTopics.ABORT_TOPIC, 10)

        # self._node.get_logger().info('SMARCPublisher publishers have been created.')

    def _create_subscribers(self):
        ### nav subscribers ###
        self.odom_sub = self._node.create_subscription(Odometry, DRTopics.DR_ODOM_TOPIC, self._odom_callback, 10)
        self.utm_sub = self._node.create_subscription(String, SamTopics.UTM_ZONE_BAND, self._utm_callback, 10)
        self.abort_sub = self._node.create_subscription(Empty, SamTopics.ABORT_TOPIC, self._abort_callback, 10)
        self.bt_heartbeat_sub = self._node.create_subscription(Empty, SamTopics.HEARTBEAT_TOPIC, self._heartbeat_callback, 10)
        self.vehicle_health_sub = self._node.create_subscription(Int8, SamTopics.VEHICLE_HEALTH_TOPIC, self._vehicle_health_callback, 10)
        self.battery_status_sub = self._node.create_subscription(BatteryState, SamTopics.BATTERY_STATUS_TOPIC, self._battery_callback, 10)

        # self._node.get_logger().info('SMARCPublisher subscribers have been created.')

    ### nav ###
    def _odom_callback(self, msg: Odometry):
        self.odom_pub.publish(msg)
        self.depth_pub.publish(Float32(data=msg.pose.pose.position.z))

        pose_utm = self._odom_to_utm(msg)
        if pose_utm is None:
            return

        self.prev_pose_utm = self.current_pose_utm
        self.current_pose_utm = pose_utm

        heading_msg = convert_enu_pose_to_heading(pose_utm.pose)
        self.heading_pub.publish(heading_msg)

        latlon_msg = convert_utm_to_latlon(pose_utm)
        latlon_msg.altitude = msg.pose.pose.position.z
        self.latlon_pub.publish(latlon_msg)
        self.altitude_pub.publish(Float32(data=latlon_msg.altitude))

        if self.prev_pose_utm is None:
            return

        course_msg = compute_course_from_two_poses(
            self.prev_pose_utm, self.current_pose_utm)
        speed_msg = compute_speed_from_two_poses(
            self.prev_pose_utm, self.current_pose_utm)
        self.course_pub.publish(course_msg)
        self.speed_pub.publish(speed_msg)

    ### status ###
    def _battery_callback(self, msg):
        if msg.percentage is None:
            self._node.get_logger().warn('Battery percentage not available, not publishing.')
            return
        battery_percentage = msg.percentage * 100.0
        battery_msg = Float32(data=battery_percentage)
        self.battery_percent_pub.publish(battery_msg)

    def _abort_callback(self, msg):
        self.abort_pub.publish(msg)

    def _heartbeat_callback(self, msg):
        self.heartbeat_pub.publish(msg)

    def _vehicle_health_callback(self, msg):
        self.vehicle_health_pub.publish(msg)

    def _utm_callback(self, msg):
        if msg.data != self.utm_frame:
            self.utm_frame = msg.data
            # Course and speed must not span two different UTM frames.
            self.prev_pose_utm = None
            self.current_pose_utm = None
            self._node.get_logger().info(
                f'Using UTM frame: {self.utm_frame}')
    
    def _odom_to_utm(self, msg: Odometry):
        """Transform an odometry pose into the active UTM frame."""
        if not self.utm_frame:
            self._node.get_logger().warn(
                'UTM frame not set, cannot publish global navigation data.')
            return None

        try:
            source_frame = msg.header.frame_id or self.odom_frame
            utm_transform = self.tf_buffer.lookup_transform(
                self.utm_frame, source_frame, msg.header.stamp)

            pose_utm = PoseStamped()
            pose_utm.header.frame_id = self.utm_frame
            pose_utm.header.stamp = msg.header.stamp
            pose_utm.pose = do_transform_pose(msg.pose.pose, utm_transform)
            return pose_utm
        except (LookupException, ConnectivityException,
                ExtrapolationException) as error:
            self._node.get_logger().error(
                f'Failed to transform odometry to {self.utm_frame}: {error}')
            return None
