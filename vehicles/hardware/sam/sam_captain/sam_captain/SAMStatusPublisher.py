import math

from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from rclpy.time import Time
from nav_msgs.msg import Odometry
from sensor_msgs.msg import BatteryState
from std_msgs.msg import Float32, String

from tf2_ros import LookupException, ConnectivityException, ExtrapolationException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from tf2_geometry_msgs import do_transform_pose

from dead_reckoning_msgs.msg import Topics as DRTopics
from sam_msgs.msg import Topics as SamTopics
from smarc_msgs.msg import DVL, GeofenceStatusStamped, Topics as SmarcTopics

from smarc_utilities.georef_utils import (
    compute_course_from_two_poses,
    convert_enu_pose_to_heading,
    convert_utm_to_latlon,
)

class SAMStatusPublisher:
    """Bridge SAM status inputs into SMaRC status and navigation topics."""

    def __init__(self, node: Node) -> None:
        self._node = node
        self._node.declare_parameter("robot_name", "sam")
        self.robot_name = (
            self._node.get_parameter("robot_name").get_parameter_value().string_value
        )
        self.odom_frame = f"{self.robot_name}/odom"
        self.utm_frame: str | None = None
        self.prev_pose_utm: PoseStamped | None = None
        self.current_pose_utm: PoseStamped | None = None
        self._latest_depth: float | None = None
        self._latest_altitude: float | None = None
        self._latest_latlon: GeoPoint | None = None
        self._latest_heading: float | None = None
        self._latest_course: float | None = None
        self._latest_speed: float | None = None
        self._last_global_navigation_time: Time | None = None
        self._battery_percent: float | None = None
        self._last_battery_time: Time | None = None
        self._geofence_status: GeofenceStatusStamped | None = None
        self._last_geofence_status_time: Time | None = None
        self._max_geofence_status_age: float = 3.0
        self._create_tf_listener()
        self._create_publishers()
        self._create_subscribers()

    @property
    def battery_percent(self) -> float | None:
        """Return the most recently received battery charge fraction."""
        return self._battery_percent

    def _create_tf_listener(self) -> None:
        """Create the TF listener used to transform odometry into UTM."""
        self._node.get_logger().info(f"Using odom frame: {self.odom_frame}")
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self._node)

    def _create_publishers(self) -> None:
        """Create publishers for the battery and derived navigation topics."""
        self.battery_percent_pub = self._node.create_publisher(
            Float32, SmarcTopics.BATTERY_PERCENT_TOPIC, 10
        )
        self.odom_pub = self._node.create_publisher(
            Odometry, SmarcTopics.ODOM_TOPIC, 10
        )
        self.depth_pub = self._node.create_publisher(
            Float32, SmarcTopics.DEPTH_TOPIC, 10
        )
        self.latlon_pub = self._node.create_publisher(
            GeoPoint, SmarcTopics.POS_LATLON_TOPIC, 10
        )
        self.heading_pub = self._node.create_publisher(
            Float32, SmarcTopics.HEADING_TOPIC, 10
        )
        self.course_pub = self._node.create_publisher(
            Float32, SmarcTopics.COURSE_TOPIC, 10
        )
        self.speed_pub = self._node.create_publisher(
            Float32, SmarcTopics.SPEED_TOPIC, 10
        )
        self.altitude_pub = self._node.create_publisher(
            Float32, SmarcTopics.ALTITUDE_TOPIC, 10
        )

        self._node.get_logger().info("SAMStatusPublisher publishers have been created.")

    def _create_subscribers(self) -> None:
        """Subscribe to SAM status, navigation, and geofence updates."""
        self.battery_status_sub = self._node.create_subscription(
            BatteryState, SamTopics.BATTERY_STATUS_TOPIC, self._battery_callback, 10
        )
        self.odom_sub = self._node.create_subscription(
            Odometry, DRTopics.DR_ODOM_TOPIC, self._odom_callback, 10
        )
        self.utm_sub = self._node.create_subscription(
            String, SamTopics.UTM_ZONE_BAND, self._utm_callback, 10
        )
        self.dvl_sub = self._node.create_subscription(
            DVL, SamTopics.DVL_TOPIC, self._dvl_callback, 10
        )
        self._geofence_status_sub = self._node.create_subscription(
            GeofenceStatusStamped,
            SmarcTopics.GEOFENCE_STATUS_TOPIC,
            self._geofence_status_callback,
            10,
        )

        self._node.get_logger().info(
            "SAMStatusPublisher subscribers have been created."
        )

    def _dvl_callback(self, msg: DVL) -> None:
        """Publish DVL-derived altitude."""
        self._latest_altitude = msg.altitude
        self.altitude_pub.publish(Float32(data=self._latest_altitude))

    def _geofence_status_callback(self, msg: GeofenceStatusStamped) -> None:
        """Cache the latest geofence status and its local receipt time."""
        self._geofence_status = msg
        self._last_geofence_status_time = self._node.get_clock().now()

    def _odom_callback(self, msg: Odometry) -> None:
        """Publish odom and derived navigation from each pose update."""
        self.odom_pub.publish(msg)
        # Dead reckoning is ENU, whereas the SMaRC depth convention is positive down.
        self._latest_depth = -msg.pose.pose.position.z
        self.depth_pub.publish(Float32(data=self._latest_depth))

        linear_velocity = msg.twist.twist.linear
        self._latest_speed = math.sqrt(
            linear_velocity.x**2
            + linear_velocity.y**2
            + linear_velocity.z**2
        )
        self.speed_pub.publish(Float32(data=self._latest_speed))

        pose_utm = self._odom_to_utm(msg)
        if pose_utm is None:
            return

        self.prev_pose_utm = self.current_pose_utm
        self.current_pose_utm = pose_utm

        heading_msg = convert_enu_pose_to_heading(pose_utm.pose)
        self._latest_heading = heading_msg.data
        self.heading_pub.publish(heading_msg)

        latlon_msg = convert_utm_to_latlon(pose_utm)
        latlon_msg.altitude = msg.pose.pose.position.z
        self._latest_latlon = latlon_msg
        self._last_global_navigation_time = self._node.get_clock().now()
        self.latlon_pub.publish(latlon_msg)

        if self.prev_pose_utm is None:
            return

        course_msg = compute_course_from_two_poses(
            self.prev_pose_utm, self.current_pose_utm
        )
        if course_msg is None:
            return
        self._latest_course = course_msg.data
        self.course_pub.publish(course_msg)

    def _utm_callback(self, msg: String) -> None:
        """Update UTM frame and reset pose."""
        if msg.data != self.utm_frame:
            self.utm_frame = msg.data
            # Global values and course must not span two different UTM frames.
            self.prev_pose_utm = None
            self.current_pose_utm = None
            self._latest_latlon = None
            self._latest_heading = None
            self._latest_course = None
            self._last_global_navigation_time = None
            self._node.get_logger().info(f"Using UTM frame: {self.utm_frame}")

    def _battery_callback(self, msg: BatteryState) -> None:
        if msg.percentage is None or not math.isfinite(msg.percentage):
            self._node.get_logger().warn(
                "Battery percentage not available, not publishing."
            )
            return
        self._battery_percent = msg.percentage
        self._last_battery_time = self._node.get_clock().now()
        self.battery_percent_pub.publish(Float32(data=self._battery_percent))

    def _odom_to_utm(self, msg: Odometry) -> PoseStamped | None:
        """Transform an odometry pose into the active UTM frame."""
        if not self.utm_frame:
            self._node.get_logger().warn(
                "UTM frame not set, cannot publish global navigation data."
            )
            return None

        try:
            source_frame = msg.header.frame_id or self.odom_frame
            utm_transform = self._tf_buffer.lookup_transform(
                self.utm_frame, source_frame, Time.from_msg(msg.header.stamp)
            )

            pose_utm = PoseStamped()
            pose_utm.header.frame_id = self.utm_frame
            pose_utm.header.stamp = msg.header.stamp
            pose_utm.pose = do_transform_pose(msg.pose.pose, utm_transform)
            return pose_utm
        except (
            LookupException,
            ConnectivityException,
            ExtrapolationException,
        ) as error:
            self._node.get_logger().error(
                f"Failed to transform odometry to {self.utm_frame}: {error}"
            )
            return None

    def global_navigation_is_fresh(self, max_age_seconds: float) -> bool:
        """Return whether a recent UTM-derived latitude/longitude is available."""
        return self._latest_latlon is not None and self._is_fresh(
            self._last_global_navigation_time, max_age_seconds
        )

    def battery_is_fresh(self, max_age_seconds: float) -> bool:
        """Return whether a valid battery reading was received recently."""
        return self._is_fresh(self._last_battery_time, max_age_seconds)

    def geofence_is_fresh(self) -> bool:
        """Return whether a geofence status was received within its allowed age."""
        return self._is_fresh(
            self._last_geofence_status_time, self._max_geofence_status_age
        )

    def geofence_is_outside(self) -> bool:
        """Return whether the current, fresh geofence status reports outside."""
        return (
            self.geofence_is_fresh()
            and self._geofence_status is not None
            and self._geofence_status.status == GeofenceStatusStamped.STATUS_OUTSIDE
        )

    def _value_or_na(self, value: float | None, unit: str) -> str:
        """Return a formatted string for a value or 'N/A' if None."""
        return f"{value:.2f} {unit}" if value is not None else "N/A"

    def _is_fresh(self, received_at: Time | None, max_age_seconds: float) -> bool:
        if received_at is None or max_age_seconds < 0:
            return False
        return (self._node.get_clock().now() - received_at).nanoseconds <= (
            max_age_seconds * 1e9
        )

    def status_str(self) -> str:
        """Create a status string for SAM status data."""
        battery = (
            f"{self._battery_percent * 100:.1f}%"
            if self._battery_percent is not None
            else "N/A"
        )
        return (
            "Status:\n"
            f"  Battery Percent: {battery}\n"
        )

    def nav_status_str(self) -> str:
        """Create a status string for navigation data."""
        position = "N/A"
        if self._latest_latlon is not None:
            position = (
                f"{self._latest_latlon.latitude:.6f}, "
                f"{self._latest_latlon.longitude:.6f}"
            )

        utm_frame = self.utm_frame or "N/A"
        depth = self._value_or_na(self._latest_depth, "m")
        altitude = self._value_or_na(self._latest_altitude, "m")
        heading = self._value_or_na(self._latest_heading, "deg")
        course = self._value_or_na(self._latest_course, "deg")
        speed = self._value_or_na(self._latest_speed, "m/s")

        return (
            "Navigation:\n"
            f"  UTM Frame: {utm_frame}\n"
            f"  Position: {position}\n"
            f"  Depth: {depth}\n"
            f"  Altitude: {altitude}\n"
            f"  Heading: {heading}\n"
            f"  Course: {course}\n"
            f"  Speed: {speed}\n"
        )