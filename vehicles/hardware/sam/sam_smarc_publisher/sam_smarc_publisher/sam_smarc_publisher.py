import rclpy
from rclpy.node import Node
from rclpy.time import Time

from geometry_msgs.msg import PoseStamped
from geographic_msgs.msg import GeoPoint
from nav_msgs.msg import Odometry
from std_msgs.msg import Empty, Int8, Float32, Float64, String

from smarc_msgs.msg import Topics as SmarcTopics
from smarc_msgs.msg import DVL
from sam_msgs.msg import Topics as SamTopics
from dead_reckoning_msgs.msg import Topics as DRTopics
from sensor_msgs.msg import BatteryState

from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from tf2_ros import LookupException, ConnectivityException, ExtrapolationException
from tf2_geometry_msgs import do_transform_pose

from smarc_utilities.georef_utils import (convert_enu_pose_to_heading, convert_utm_to_latlon,
                                          compute_course_from_two_poses, compute_speed_from_two_poses)

class SAMSMARCPublisher(Node):
    def __init__(self):
        super().__init__('sam_smarc_publisher')
        self.get_logger().info('SAM SMaRC Publisher Node has been started.')
        self.declare_parameter('robot_name', 'sam')
        self.robot_name = self.get_parameter('robot_name').get_parameter_value().string_value
        self.utm_frame = None
        self.create_subscription(String, SamTopics.UTM_ZONE_BAND, self._utm_callback, 10)

        self._create_abort_pubsub()
        self._create_bt_heartbeat_pubsub()
        self._create_altitude_pubsub()
        self._create_battery_status_pubsub()

        self._create_tf_listener()
        self._create_odom_pubsub()

    def _utm_callback(self, msg):
        # commented out because the first ever one is almost always bad, we are in water :,)
        # if self.utm_frame is not None:
        #     return
        if msg.data != self.utm_frame:
            self.utm_frame = msg.data
            self.get_logger().info(f'Using UTM frame: {self.utm_frame}')

    def _create_tf_listener(self):
        self.odom_frame = f'{self.robot_name}/odom'
        self.get_logger().info(f'Using odom frame: {self.odom_frame}')
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
        self.battery_percent_pub = self.create_publisher(Float32, SmarcTopics.BATTERY_PERCENT_TOPIC, 10)
        self.battery_status_sub = self.create_subscription(BatteryState, SamTopics.BATTERY_STATUS_TOPIC, self.battery_status_callback, 10)
    
    def battery_status_callback(self, msg):

        # extract the battery percentage from the BatteryState message
        if msg.percentage is not None:
            battery_percentage = msg.percentage * 100.0
        else:
            # don't publish if percentage is not available
            self.get_logger().warn('Battery percentage not available, not publishing.')
            return
        # create a Float32 message to publish
        msg = Float32()
        msg.data = battery_percentage
        # self.get_logger().info(f'Publishing battery percentage: {battery_percentage}%')
        self.battery_percent_pub.publish(msg)

    def _create_altitude_pubsub(self):
        self.altitude_pub = self.create_publisher(Float32, SmarcTopics.ALTITUDE_TOPIC, 10)
        

    def _create_odom_pubsub(self):
        """
        Creates subscription from Odometry data.
        Also create all publishers for SMaRC topics that are derived from the odometry data.
        """
        self.prev_pose_utm = None
        self.current_pose_utm = None
        self.odom_sub = self.create_subscription(Odometry, DRTopics.DR_ODOM_TOPIC, self.odom_callback, 10)

        self.odom_pub = self.create_publisher(Odometry, SmarcTopics.ODOM_TOPIC, 10)
        self.depth_pub = self.create_publisher(Float32, SmarcTopics.DEPTH_TOPIC, 10)
        self.latlon_pub = self.create_publisher(GeoPoint, SmarcTopics.POS_LATLON_TOPIC, 10)
        self.heading_pub = self.create_publisher(Float32, SmarcTopics.HEADING_TOPIC, 10)

        self.course_pub = self.create_publisher(Float32, SmarcTopics.COURSE_TOPIC, 10)
        self.speed_pub = self.create_publisher(Float32, SmarcTopics.SPEED_TOPIC, 10)

    def odom_callback(self, msg):
        """
        Callback for the Odometry topic. It publishes the odometry data to the SMaRC topic.
        It also publishes the heading, course, speed, depth and latitude/longitude.
        """
        # Publish the odometry message
        self.odom_pub.publish(msg)
        self.depth_pub.publish(Float32(data=msg.pose.pose.position.z))

        if not self.utm_frame:
            self.get_logger().warn('UTM frame not set, will not attempt to transform.')
            return

        try:
            timestamp = msg.header.stamp
            utm_transform = self.tf_buffer.lookup_transform(self.utm_frame, self.odom_frame, timestamp)

            transform_pose = PoseStamped()
            transform_pose.pose = do_transform_pose(msg.pose.pose, utm_transform)
            transform_pose.header.frame_id = self.utm_frame
            transform_pose.header.stamp = msg.header.stamp

            # Update prev and current UTM poses
            self.prev_pose_utm = self.current_pose_utm
            self.current_pose_utm = transform_pose

            compass_heading_msg = convert_enu_pose_to_heading(transform_pose.pose)
            self.heading_pub.publish(compass_heading_msg)

            latlon_msg = convert_utm_to_latlon(transform_pose)
            latlon_msg.altitude = msg.pose.pose.position.z
            self.latlon_pub.publish(latlon_msg)
            self.altitude_pub.publish(Float32(data=latlon_msg.altitude))

            if self.current_pose_utm is not None and self.prev_pose_utm is not None:
                course_msg = compute_course_from_two_poses(self.prev_pose_utm, self.current_pose_utm)
                self.course_pub.publish(course_msg)
                speed_msg = compute_speed_from_two_poses(self.prev_pose_utm, self.current_pose_utm)
                self.speed_pub.publish(speed_msg)
            else:
                self.get_logger().warn('Previous or current pose is None, cannot compute course or speed.')

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
