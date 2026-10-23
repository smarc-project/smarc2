import rclpy
from geographic_msgs.msg import GeoPoint
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from std_msgs.msg import Float32, Int8, String
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener

from sam_captain.SAMStatusPublisher import SAMStatusPublisher
from dead_reckoning_msgs.msg import Topics as DRTopics
from sam_msgs.msg import Topics as SamTopics
from smarc_msgs.msg import DVL, GeofenceStatusStamped, Topics as SmarcTopics


class SAMCaptain(Node):
    def __init__(self) -> None:
        super().__init__("sam_captain")
        self.get_logger().info("SAM Captain Node has been started.")

        # TODO parameters

        self._create_tf_listener()
        self._status_publisher = SAMStatusPublisher(self, self._tf_buffer)
        self._create_status_publishers()
        self._create_status_subscribers()

        # status string
        self.nav_str_pub = self.create_publisher(
            String, SamTopics.STATUS_STRING_TOPIC, 10
        )
        self._status_str_timer = self.create_timer(1.0, self._status_str_callback)

        # health check related
        self._max_battery_age: float = 1.0  # TODO: set max battery age in seconds
        self._max_nav_age: float = 1.0  # TODO: set max nav age in seconds
        self._battery_threshold: float = 0.3
        self._vehicle_health: Int8 = Int8()  # TODO: set initial vehicle health state
        self._vehicle_health.data = (
            SmarcTopics.VEHICLE_HEALTH_WAITING
        )  # TODO: set initial vehicle health state
        self._vehicle_health_reason: str = (
            "Initial state"  # TODO: set initial vehicle health reason
        )

        self._vehicle_health_pub = self.create_publisher(
            Int8, SmarcTopics.VEHICLE_HEALTH_TOPIC, 10
        )

        self._health_check_timer = self.create_timer(1.0, self._pub_vehicle_health)

    def _create_tf_listener(self) -> None:
        """Create the TF listener used for dead-reckoning-to-UTM transforms."""
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self)

    def _create_status_publishers(self) -> None:
        """Create publishers used by the status and navigation callbacks."""
        status = self._status_publisher
        status.battery_percent_pub = self.create_publisher(
            Float32, SmarcTopics.BATTERY_PERCENT_TOPIC, 10
        )
        status.odom_pub = self.create_publisher(Odometry, SmarcTopics.ODOM_TOPIC, 10)
        status.depth_pub = self.create_publisher(
            Float32, SmarcTopics.DEPTH_TOPIC, 10
        )
        status.latlon_pub = self.create_publisher(
            GeoPoint, SmarcTopics.POS_LATLON_TOPIC, 10
        )
        status.heading_pub = self.create_publisher(
            Float32, SmarcTopics.HEADING_TOPIC, 10
        )
        status.course_pub = self.create_publisher(
            Float32, SmarcTopics.COURSE_TOPIC, 10
        )
        status.speed_pub = self.create_publisher(
            Float32, SmarcTopics.SPEED_TOPIC, 10
        )
        status.altitude_pub = self.create_publisher(
            Float32, SmarcTopics.ALTITUDE_TOPIC, 10
        )

    def _create_status_subscribers(self) -> None:
        """Create subscriptions that feed the status and navigation callbacks."""
        status = self._status_publisher
        self._battery_status_sub = self.create_subscription(
            BatteryState, SamTopics.BATTERY_STATUS_TOPIC, status._battery_callback, 10
        )
        self._odom_sub = self.create_subscription(
            Odometry, DRTopics.DR_ODOM_TOPIC, status._odom_callback, 10
        )
        self._utm_sub = self.create_subscription(
            String, SamTopics.UTM_ZONE_BAND, status._utm_callback, 10
        )
        self._dvl_sub = self.create_subscription(
            DVL, SamTopics.DVL_TOPIC, status._dvl_callback, 10
        )
        self._geofence_status_sub = self.create_subscription(
            GeofenceStatusStamped,
            SmarcTopics.GEOFENCE_STATUS_TOPIC,
            status._geofence_status_callback,
            10,
        )

    def _pub_vehicle_health(self) -> None:
        """Evaluate and publish the vehicle health state."""
        prev_health = self._vehicle_health
        prev_reason = self._vehicle_health_reason
        self._vehicle_health.data, self._vehicle_health_reason = (
            self._evaluate_vehicle_health()
        )
        self.get_logger().info(
            f"Publishing vehicle health: {self._vehicle_health}, reason: {self._vehicle_health_reason}"
        )
        self._vehicle_health_pub.publish(self._vehicle_health)

        if self._vehicle_health.data != prev_health.data:
            self.get_logger().warn(
                f"Vehicle health state changed from {self._health_str(prev_health.data)} to {self._health_str(self._vehicle_health.data)}"
            )
            self.get_logger().warn(
                f"Vehicle health reason changed from '{prev_reason}' to '{self._vehicle_health_reason}'"
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
        battery_percent = self._status_publisher.battery_percent
        is_fresh_battery = self._status_publisher.battery_is_fresh(
            self._max_battery_age
        )
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
        is_nav_fresh = self._status_publisher.global_navigation_is_fresh(
            self._max_nav_age
        )
        if not is_nav_fresh:
            return (
                SmarcTopics.VEHICLE_HEALTH_WAITING,
                ">>>>>>>> Nav publisher not fresh <<<<<<<<",
            )
        if self._status_publisher.geofence_is_outside():
            return (
                SmarcTopics.VEHICLE_HEALTH_WAITING,
                ">>>>>>>> Geofence outside <<<<<<<<<<"
            )

        return (
            SmarcTopics.VEHICLE_HEALTH_READY,
            "=========== All checks passed ===========\n"
            "=========== Vehicle health ready ===========",
        )

    def _status_str_callback(self) -> None:
        """Publish a status string containing the latest nav and system status information."""
        nav_status = self._status_publisher.nav_status_str()
        sys_str = self._status_publisher.status_str()
        msg = String()
        msg.data = f"{nav_status}\n{sys_str}"
        self.get_logger().info(f"Publishing status string: {msg.data}")
        self.nav_str_pub.publish(msg)


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
