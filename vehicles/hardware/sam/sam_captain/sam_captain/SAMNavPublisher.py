import math

from rclpy.node import Node
from rclpy.time import Time
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32, String
from nav_msgs.msg import Odometry
from geographic_msgs.msg import GeoPoint
from smarc_msgs.msg import DVL

from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from tf2_ros import LookupException, ConnectivityException, ExtrapolationException
from tf2_geometry_msgs import do_transform_pose

from smarc_msgs.msg import Topics as SmarcTopics
from dead_reckoning_msgs.msg import Topics as DRTopics
from sam_msgs.msg import Topics as SamTopics
from smarc_utilities.georef_utils import (
    compute_course_from_two_poses,
    convert_enu_pose_to_heading,
    convert_utm_to_latlon,
)


class SAMNavPublisher:
    """Derive navigation data from SAM and publish to smarc topics."""

    def __init__(self, node: Node) -> None:
        self._node = node
        self._node.get_logger().info("SAMNavPublisher has been initialized.")
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
        self._create_tf_listener()
        self._create_publishers()
        self._create_subscribers()

    def _create_tf_listener(self) -> None:
        """Creates a TF listener to transform poses between different frames."""
        self._node.get_logger().info(f"Using odom frame: {self.odom_frame}")
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self._node)

    def _create_publishers(self) -> None:
        """Create publishers for navigation topics."""
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

    def _create_subscribers(self) -> None:
        """Subscribe to DR and UTM updates."""
        self.odom_sub = self._node.create_subscription(
            Odometry, DRTopics.DR_ODOM_TOPIC, self._odom_callback, 10
        )
        self.utm_sub = self._node.create_subscription(
            String, SamTopics.UTM_ZONE_BAND, self._utm_callback, 10
        )
        self.dvl_sub = self._node.create_subscription(
            DVL, SamTopics.DVL_TOPIC, self._dvl_callback, 10
        )

    def _dvl_callback(self, msg: DVL) -> None:
        """Publish DVL-derived altitude."""
        self._latest_altitude = msg.altitude
        self.altitude_pub.publish(Float32(data=self._latest_altitude))

    def _odom_callback(self, msg: Odometry) -> None:
        """Publish odom and derived navigation from each pose update."""
        self.odom_pub.publish(msg)
        self._latest_depth = -msg.pose.pose.position.z # Odom is ENU, so depth is negative of z position
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
        self._latest_course = course_msg.data
        self.course_pub.publish(course_msg)

    def _utm_callback(self, msg: String) -> None:
        """Update UTM frame and reset pose."""
        if msg.data != self.utm_frame:
            self.utm_frame = msg.data
            # Course must not span two different UTM frames.
            self.prev_pose_utm = None
            self.current_pose_utm = None
            self._node.get_logger().info(f"Using UTM frame: {self.utm_frame}")

    def _odom_to_utm(self, msg: Odometry) -> PoseStamped | None:
        """Transform an odometry pose into the active UTM frame."""
        if not self.utm_frame:
            self._node.get_logger().warn(
                "UTM frame not set, cannot publish global navigation data."
            )
            return None

        try:
            source_frame = msg.header.frame_id or self.odom_frame
            utm_transform = self.tf_buffer.lookup_transform(
                self.utm_frame, source_frame, Time()
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
        if self._latest_latlon is None or self._last_global_navigation_time is None:
            return False
        return (
            self._node.get_clock().now() - self._last_global_navigation_time
        ).nanoseconds <= max_age_seconds * 1e9

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

    def _value_or_na(self, value: float | None, unit: str) -> str:
        """Return a formatted string for a value or 'N/A' if None."""
        return f"{value:.2f} {unit}" if value is not None else "N/A"
