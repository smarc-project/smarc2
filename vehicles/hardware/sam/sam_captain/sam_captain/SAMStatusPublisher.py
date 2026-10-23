# TODO: imports
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32, String
from geographic_msgs.msg import GeoPoint

from sam_msgs.msg import Topics as SamTopics
from smarc_msgs.msg import Topics as SmarcTopics

class SAMStatusPublisher:
    """Publish status topics for the SAM Captain node."""
    def __init__(self, cap) -> None:
        self.cap = cap

        self._odom_pub = self.cap.create_publisher(Odometry, SmarcTopics.ODOM_TOPIC, 10)
        self._depth_pub = self.cap.create_publisher(Float32, SmarcTopics.DEPTH_TOPIC, 10)
        self._altitude_pub = self.cap.create_publisher(Float32, SmarcTopics.ALTITUDE_TOPIC, 10)
        self._latlon_pub = self.cap.create_publisher(GeoPoint, SmarcTopics.POS_LATLON_TOPIC, 10)
        self._heading_pub = self.cap.create_publisher(Float32, SmarcTopics.HEADING_TOPIC, 10)
        self._course_pub = self.cap.create_publisher(Float32, SmarcTopics.COURSE_TOPIC, 10)
        self._speed_pub = self.cap.create_publisher(Float32, SmarcTopics.SPEED_TOPIC, 10)

        self._status_string_pub = cap.create_publisher(String, SamTopics.STATUS_STRING_TOPIC, 10)
        # TODO: timer callback to pub string
        self._publish_timer = cap.create_timer(0.1, self._publish_status)
        self.cap.get_logger().info("create timer for publishing status")

    def _value_or_na(self, value: float | None, unit: str) -> str:
        """Return a formatted string for a value or 'N/A' if None."""
        return f"{value:.2f} {unit}" if value is not None else "N/A"

    def status_str(self) -> str:
        """Create a status string for SAM status and nav data."""
        battery = (
            f"{self.cap.battery_percent * 100:.1f}%"
            if self.cap.battery_percent is not None
            else "N/A"
        )
        position = "N/A"
        if self.cap.latest_latlon is not None:
            position = (
                f"{self.cap.latest_latlon.latitude:.6f}, "
                f"{self.cap.latest_latlon.longitude:.6f}"
            )

        utm_frame = self.cap.utm_frame or "N/A"
        depth = self._value_or_na(self.cap.latest_depth, "m")
        altitude = self._value_or_na(self.cap.latest_altitude, "m")
        heading = self._value_or_na(self.cap.latest_heading, "deg")
        course = self._value_or_na(self.cap.latest_course, "deg")
        speed = self._value_or_na(self.cap.latest_speed, "m/s")

        return (
            "Status:\n"
            f"  Battery Percent: {battery}\n"
            "Navigation:\n"
            f"  UTM Frame: {utm_frame}\n"
            f"  Position: {position}\n"
            f"  Depth: {depth}\n"
            f"  Altitude: {altitude}\n"
            f"  Heading: {heading}\n"
            f"  Course: {course}\n"
            f"  Speed: {speed}\n"
        )

    def _publish_status(self) -> None:
        """Publish the latest available captain state on SMaRC status topics."""
        # TODO pub battery
        # TODO pub odom
        # TODO pub depth
        # TODO pub altitude
        # TODO pub latlon
        # TODO pub heading
        # TODO pub course
        # TODO pub speed
        # TODO pub status string
        pass

