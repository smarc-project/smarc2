from nav_msgs.msg import Odometry
from std_msgs.msg import Float32, String, Int8
from geographic_msgs.msg import GeoPoint

from sam_msgs.msg import Topics as SamTopics
from smarc_msgs.msg import Topics as SmarcTopics

class SAMStatusPublisher:
    """Publish status topics for the SAM Captain node."""
    def __init__(self, cap) -> None:
        self.cap = cap

        # TODO: add this to parameters
        self._max_battery_age = 1.0
        self._max_nav_age = 1.0
        self._battery_threshold = 0.3

        # health
        self._vehicle_health = Int8(data=SmarcTopics.VEHICLE_HEALTH_WAITING)
        self._vehicle_health_reason = 'Initial state'

        self._odom_pub = self.cap.create_publisher(Odometry, SmarcTopics.ODOM_TOPIC, 10)
        self._depth_pub = self.cap.create_publisher(Float32, SmarcTopics.DEPTH_TOPIC, 10)
        self._altitude_pub = self.cap.create_publisher(Float32, SmarcTopics.ALTITUDE_TOPIC, 10)
        self._latlon_pub = self.cap.create_publisher(GeoPoint, SmarcTopics.POS_LATLON_TOPIC, 10)
        self._heading_pub = self.cap.create_publisher(Float32, SmarcTopics.HEADING_TOPIC, 10)
        self._course_pub = self.cap.create_publisher(Float32, SmarcTopics.COURSE_TOPIC, 10)
        self._speed_pub = self.cap.create_publisher(Float32, SmarcTopics.SPEED_TOPIC, 10)
        self._battery_percent_pub = self.cap.create_publisher(Float32, SmarcTopics.BATTERY_PERCENT_TOPIC, 10)
        self._status_string_pub = cap.create_publisher(String, SamTopics.STATUS_STRING_TOPIC, 10)
        self._vehicle_health_pub = cap.create_publisher(Int8, SmarcTopics.VEHICLE_HEALTH_TOPIC, 10)

        self._publish_timer = cap.create_timer(0.1, self._publish_status)

    def _value_or_na(self, value: float | None, unit: str) -> str:
        """Return a formatted string for a value or 'N/A' if None."""
        return f"{value:.2f} {unit}" if value is not None else "N/A"

    def status_str(self) -> str:
        """Create a status string for SAM status and nav data."""
        battery = (
            f"{self.cap.latest_battery_percent:.1f}%"
            if self.cap.latest_battery_percent is not None
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
        # self.cap.get_logger().info("Publishing SAM status and navigation data.")
        if self.cap.latest_battery_percent is not None:
            self._battery_percent_pub.publish(Float32(data=self.cap.latest_battery_percent))
        if self.cap.latest_odom is not None:
            self._odom_pub.publish(self.cap.latest_odom)
        if self.cap.latest_depth is not None:
            self._depth_pub.publish(Float32(data=self.cap.latest_depth))
        if self.cap.latest_altitude is not None:
            self._altitude_pub.publish(Float32(data=self.cap.latest_altitude))
        if self.cap.latest_latlon is not None:
            self._latlon_pub.publish(self.cap.latest_latlon)
        if self.cap.latest_heading is not None:
            self._heading_pub.publish(Float32(data=self.cap.latest_heading))
        if self.cap.latest_course is not None:
            self._course_pub.publish(Float32(data=self.cap.latest_course))
        if self.cap.latest_speed is not None:
            self._speed_pub.publish(Float32(data=self.cap.latest_speed))
        
        # status string
        status = self.status_str()
        self._status_string_pub.publish(String(data=status))
        self.cap.get_logger().info(f"Published status string:\n{status}")

        self._pub_vehicle_health()

        # self.cap.get_logger().info("Published SAM status and navigation data.")

    # -------- Health evaluation --------
    def _pub_vehicle_health(self) -> None:
        """Evaluate and publish the vehicle health state."""
        prev_health = self._vehicle_health
        prev_reason = self._vehicle_health_reason
        health, reason = self._evaluate_vehicle_health()
        self._vehicle_health = Int8(data=health)
        self._vehicle_health_reason = reason

        self.cap.get_logger().info(
            f"Publishing vehicle health: {health}, reason: {reason}"
        )
        self._vehicle_health_pub.publish(self._vehicle_health)

        if health != prev_health.data:
            self.cap.get_logger().warn(
                f"Vehicle health state changed from {self._health_str(prev_health.data)} to {self._health_str(health)}"
            )
            self.cap.get_logger().warn(
                f"Vehicle health reason changed from '{prev_reason}' to '{reason}'"
            )

    def _health_str(self, health_state: int) -> str:
        """Return a readable name for a SMARC vehicle-health state."""
        health_names = {
            SmarcTopics.VEHICLE_HEALTH_READY: "READY",
            SmarcTopics.VEHICLE_HEALTH_WAITING: "WAITING",
            SmarcTopics.VEHICLE_HEALTH_ERROR: "ERROR",
        }
        return health_names.get(health_state, f"UNKNOWN({health_state})")

    def _evaluate_vehicle_health(self) -> tuple[int, str]:
        """Evaluate the health of the vehicle based on various inputs."""
        battery_percent = self.cap.latest_battery_percent
        is_fresh_battery = self.cap.battery_is_fresh(self._max_battery_age)
        if battery_percent is None or not is_fresh_battery:
            return (
                SmarcTopics.VEHICLE_HEALTH_WAITING,
                ">>>>>>>> Battery not fresh or None <<<<<<<<",
            )

        if battery_percent < self._battery_threshold:
            return (
                SmarcTopics.VEHICLE_HEALTH_ERROR,
                ">>>>>>>> Battery below threshold <<<<<<<<",
            )
        is_nav_fresh = self.cap.global_navigation_is_fresh(self._max_nav_age)
        if not is_nav_fresh:
            return (
                SmarcTopics.VEHICLE_HEALTH_WAITING,
                ">>>>>>>> Nav publisher not fresh <<<<<<<<",
            )
        if self.cap.geofence_is_outside():
            return (
                SmarcTopics.VEHICLE_HEALTH_WAITING,
                ">>>>>>>> Geofence outside <<<<<<<<<<"
            )

        return (
            SmarcTopics.VEHICLE_HEALTH_READY,
            "=========== All checks passed ===========\n"
            "=========== Vehicle health ready ===========",
        )