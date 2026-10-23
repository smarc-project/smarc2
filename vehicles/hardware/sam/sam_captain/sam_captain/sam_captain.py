import math
import rclpy
from rclpy.time import Time
from geographic_msgs.msg import GeoPoint
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from std_msgs.msg import Float32, Int8, String

from sam_captain.SAMStatusPublisher import SAMStatusPublisher
from dead_reckoning_msgs.msg import Topics as DRTopics
from sam_msgs.msg import Topics as SamTopics
from smarc_msgs.msg import DVL, GeofenceStatusStamped, Topics as SmarcTopics
from smarc_utilities.georef_utils import (
    compute_course_from_two_poses,
    convert_enu_pose_to_heading,
    convert_utm_to_latlon,
)
from tf2_geometry_msgs import do_transform_pose
from tf2_ros import ConnectivityException, ExtrapolationException, LookupException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener

class SAMCaptain(Node):
    def __init__(self) -> None:
        super().__init__("sam_captain")
        self.get_logger().info("SAM Captain Node has been started.")
        # TODO parameters
        self.declare_parameter('robot_name', 'sam')
        self.robot_name = (
            self.get_parameter('robot_name').get_parameter_value().string_value
        )
        self.odom_frame = f'{self.robot_name}/odom'

        self.latest_battery_percent: float | None = None
        self.latest_odom: Odometry | None = None
        self.latest_depth: float | None = None
        self.latest_altitude: float | None = None
        self.latest_latlon: GeoPoint | None = None
        self.latest_heading: float | None = None
        self.latest_course: float | None = None
        self.latest_speed: float | None = None
        self.latest_geofence_status: GeofenceStatusStamped | None = None

        self.utm_frame: str | None = None
        self.previous_pose_utm: PoseStamped | None = None
        self.current_pose_utm: PoseStamped | None = None
        self.last_battery_time: Time | None = None
        self.last_global_navigation_time: Time | None = None
        self.last_geofence_status_time: Time | None = None

        self.max_battery_age = 1.0
        self.max_nav_age = 1.0
        self.max_geofence_status_age = 3.0
        self.battery_threshold = 0.3

        # tf and sub
        self._create_tf_listener()
        self._create_status_subscribers()

        # status publisher
        self.status_publisher = SAMStatusPublisher(self)
        self.get_logger().info("SAMStatusPublisher has been created.")


    def _create_tf_listener(self) -> None:
        """Create the TF listener used for dead-reckoning-to-UTM transforms."""
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self)

    def _create_status_subscribers(self) -> None:
        """Create subscriptions that feed the status and navigation callbacks."""
        self._battery_status_sub = self.create_subscription(
            BatteryState, SamTopics.BATTERY_STATUS_TOPIC, self._battery_callback, 10
        )
        self._odom_sub = self.create_subscription(
            Odometry, DRTopics.DR_ODOM_TOPIC, self._odom_callback, 10
        )
        self._utm_sub = self.create_subscription(
            String, SamTopics.UTM_ZONE_BAND, self._utm_callback, 10
        )
        self._dvl_sub = self.create_subscription(
            DVL, SamTopics.DVL_TOPIC, self._dvl_callback, 10
        )
        self._geofence_status_sub = self.create_subscription(
            GeofenceStatusStamped,
            SmarcTopics.GEOFENCE_STATUS_TOPIC,
            self._geofence_status_callback,
            10,
        )

    def _battery_callback(self, msg: BatteryState) -> None:
        if msg.percentage is None:
            self.get_logger().warn('Battery percentage not available.')
            return
        self.latest_battery_percent = msg.percentage
        self._last_battery_time = self.get_clock().now()

    def _odom_callback(self, msg: Odometry) -> None:
        self.latest_odom = msg
        self.latest_depth = -msg.pose.pose.position.z
        velocity = msg.twist.twist.linear
        self.latest_speed = math.sqrt(
            velocity.x**2 + velocity.y**2 + velocity.z**2
        )

        pose_utm = self._odom_to_utm(msg)
        if pose_utm is None:
            return

        self._previous_pose_utm = self._current_pose_utm
        self._current_pose_utm = pose_utm
        self.latest_heading = convert_enu_pose_to_heading(pose_utm.pose).data

        latlon = convert_utm_to_latlon(pose_utm)
        latlon.altitude = msg.pose.pose.position.z
        self.latest_latlon = latlon
        self._last_global_navigation_time = self.get_clock().now()

        if self._previous_pose_utm is None:
            return
        course = compute_course_from_two_poses(
            self._previous_pose_utm, self._current_pose_utm
        )
        if course is not None:
            self.latest_course = course.data

    def _utm_callback(self, msg: String) -> None:
        if msg.data == self.utm_frame:
            return
        self.utm_frame = msg.data
        self._previous_pose_utm = None
        self._current_pose_utm = None
        self.latest_latlon = None
        self.latest_heading = None
        self.latest_course = None
        self._last_global_navigation_time = None
        self.get_logger().info(f'Using UTM frame: {self.utm_frame}')

    def _dvl_callback(self, msg: DVL) -> None:
        self.latest_altitude = msg.altitude

    def _geofence_status_callback(self, msg: GeofenceStatusStamped) -> None:
        self.latest_geofence_status = msg
        self._last_geofence_status_time = self.get_clock().now()

    def _odom_to_utm(self, msg: Odometry) -> PoseStamped | None:
        if not self.utm_frame:
            self.get_logger().warn(
                'UTM frame not set, cannot publish global navigation data.'
            )
            return None
        try:
            source_frame = msg.header.frame_id or self.odom_frame
            transform = self._tf_buffer.lookup_transform(
                self.utm_frame, source_frame, Time.from_msg(msg.header.stamp)
            )
            pose_utm = PoseStamped()
            pose_utm.header.frame_id = self.utm_frame
            pose_utm.header.stamp = msg.header.stamp
            pose_utm.pose = do_transform_pose(msg.pose.pose, transform)
            return pose_utm
        except (LookupException, ConnectivityException, ExtrapolationException) as error:
            self.get_logger().error(
                f'Failed to transform odometry to {self.utm_frame}: {error}'
            )
            return None

def main(args=None):
    rclpy.init(args=args)

    sam_captain = SAMCaptain()

    rclpy.spin(sam_captain)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    sam_captain.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
