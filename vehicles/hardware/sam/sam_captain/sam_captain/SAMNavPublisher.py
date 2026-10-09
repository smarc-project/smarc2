from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Int8, Float32, String
from nav_msgs.msg import Odometry
from geographic_msgs.msg import GeoPoint

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


class SAMNavPublisher:
    """Derive navigation data from SAM and publish to smarc topics."""

    def __init__(self, node: Node):
        self._node = node
        self._node.get_logger().info("SAMNavPublisher has been initialized.")
        self._node.declare_parameter("robot_name", "sam")
        self.robot_name = (
            self._node.get_parameter("robot_name").get_parameter_value().string_value
        )
        self.odom_frame = f"{self.robot_name}/odom"
        self.utm_frame = None
        self.prev_pose_utm = None
        self.current_pose_utm = None
        self._latest_depth = None
        self._latest_altitude = None
        self._latest_latlon = None
        self._latest_heading = None
        self._latest_course = None
        self._latest_speed = None
        self._create_tf_listener()
        self._create_publishers()
        self._create_subscribers()

    def _create_tf_listener(self):
        """Creates a TF listener to transform poses between different frames."""
        self._node.get_logger().info(f"Using odom frame: {self.odom_frame}")
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self._node)

    def _create_publishers(self):
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
        self.vehicle_health_pub = self._node.create_publisher(
            Int8, SmarcTopics.VEHICLE_HEALTH_TOPIC, 10
        )

    def _create_subscribers(self):
        """Subscribe to DR and UTM updates."""
        self.odom_sub = self._node.create_subscription(
            Odometry, DRTopics.DR_ODOM_TOPIC, self._odom_callback, 10
        )
        self.utm_sub = self._node.create_subscription(
            String, SamTopics.UTM_ZONE_BAND, self._utm_callback, 10
        )
        self.vehicle_health_sub = self._node.create_subscription(
            Int8, SmarcTopics.VEHICLE_HEALTH_TOPIC, self._vehicle_health_callback, 10
        )

    def _odom_callback(self, msg: Odometry):
        """Publish odom and derived navigation from each pose update."""
        self.odom_pub.publish(msg)
        self._latest_depth = msg.pose.pose.position.z
        self.depth_pub.publish(Float32(data=self._latest_depth))

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
        self._latest_altitude = latlon_msg.altitude
        self.latlon_pub.publish(latlon_msg)
        self.altitude_pub.publish(Float32(data=self._latest_altitude))

        if self.prev_pose_utm is None:
            return

        course_msg = compute_course_from_two_poses(
            self.prev_pose_utm, self.current_pose_utm
        )
        speed_msg = compute_speed_from_two_poses(
            self.prev_pose_utm, self.current_pose_utm
        )
        self._latest_course = course_msg.data
        self._latest_speed = speed_msg.data
        self.course_pub.publish(course_msg)
        self.speed_pub.publish(speed_msg)

    def _utm_callback(self, msg):
        """Update UTM frame and reset pose."""
        if msg.data != self.utm_frame:
            self.utm_frame = msg.data
            # Course and speed must not span two different UTM frames.
            self.prev_pose_utm = None
            self.current_pose_utm = None
            self._node.get_logger().info(f"Using UTM frame: {self.utm_frame}")

    def _odom_to_utm(self, msg: Odometry):
        """Transform an odometry pose into the active UTM frame."""
        if not self.utm_frame:
            self._node.get_logger().warn(
                "UTM frame not set, cannot publish global navigation data."
            )
            return None

        try:
            source_frame = msg.header.frame_id or self.odom_frame
            utm_transform = self.tf_buffer.lookup_transform(
                self.utm_frame, source_frame, msg.header.stamp
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

    def _vehicle_health_callback(self, msg: Int8):
        #  TODO: add geofence check to vehicle health
        self.vehicle_health_pub.publish(msg)

    # TODO: add geofence check to vehicle health
    def _check_geofence(self):
        pass

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

    def _value_or_na(self, value, unit):
        """Return a formatted string for a value or 'N/A' if None."""
        return f"{value:.2f} {unit}" if value is not None else "N/A"
