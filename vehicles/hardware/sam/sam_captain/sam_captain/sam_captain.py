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

        # TODO: call status publisher
        self.status_publisher = SAMStatusPublisher(self)
        self.get_logger().info("SAMStatusPublisher has been created.")



    # def _create_tf_listener(self) -> None:
    #     """Create the TF listener used for dead-reckoning-to-UTM transforms."""
    #     self._tf_buffer = Buffer()
    #     self._tf_listener = TransformListener(self._tf_buffer, self)

    # def _create_status_subscribers(self) -> None:
    #     """Create subscriptions that feed the status and navigation callbacks."""
    #     self._battery_status_sub = self.create_subscription(
    #         BatteryState, SamTopics.BATTERY_STATUS_TOPIC, self._battery_callback, 10
    #     )
    #     self._odom_sub = self.create_subscription(
    #         Odometry, DRTopics.DR_ODOM_TOPIC, self._odom_callback, 10
    #     )
    #     self._utm_sub = self.create_subscription(
    #         String, SamTopics.UTM_ZONE_BAND, self._utm_callback, 10
    #     )
    #     self._dvl_sub = self.create_subscription(
    #         DVL, SamTopics.DVL_TOPIC, self._dvl_callback, 10
    #     )
    #     self._geofence_status_sub = self.create_subscription(
    #         GeofenceStatusStamped,
    #         SmarcTopics.GEOFENCE_STATUS_TOPIC,
    #         self._geofence_status_callback,
    #         10,
    #     )

    # def _pub_vehicle_health(self) -> None:
    #     """Evaluate and publish the vehicle health state."""
    #     prev_health = self._vehicle_health
    #     prev_reason = self._vehicle_health_reason
    #     self._vehicle_health.data, self._vehicle_health_reason = (
    #         self._evaluate_vehicle_health()
    #     )
    #     self.get_logger().info(
    #         f"Publishing vehicle health: {self._vehicle_health}, reason: {self._vehicle_health_reason}"
    #     )
    #     self._vehicle_health_pub.publish(self._vehicle_health)

    #     if self._vehicle_health.data != prev_health.data:
    #         self.get_logger().warn(
    #             f"Vehicle health state changed from {self._health_str(prev_health.data)} to {self._health_str(self._vehicle_health.data)}"
    #         )
    #         self.get_logger().warn(
    #             f"Vehicle health reason changed from '{prev_reason}' to '{self._vehicle_health_reason}'"
    #         )

    # def _health_str(self, health_state: int) -> str:
    #     """Return a readable name for a SMARC vehicle-health state."""
    #     health_names = {
    #         SmarcTopics.VEHICLE_HEALTH_READY: "READY",
    #         SmarcTopics.VEHICLE_HEALTH_WAITING: "WAITING",
    #         SmarcTopics.VEHICLE_HEALTH_ERROR: "ERROR",
    #     }
    #     return health_names.get(health_state, f"UNKNOWN({health_state})")

    # def _evaluate_vehicle_health(self) -> tuple[int, str]:
    #     """Evaluate the health of the vehicle based on various inputs."""
    #     battery_percent = self._status_publisher.battery_percent
    #     is_fresh_battery = self._status_publisher.battery_is_fresh(
    #         self._max_battery_age
    #     )
    #     if battery_percent is None or not is_fresh_battery:
    #         return (
    #             SmarcTopics.VEHICLE_HEALTH_WAITING,
    #             ">>>>>>>> Battery not fresh or None <<<<<<<<",
    #         )

    #     if battery_percent < self._battery_threshold:
    #         return (
    #             SmarcTopics.VEHICLE_HEALTH_ERROR,
    #             ">>>>>>>> Battery below threshold <<<<<<<<",
    #         )
    #     is_nav_fresh = self._status_publisher.global_navigation_is_fresh(
    #         self._max_nav_age
    #     )
    #     if not is_nav_fresh:
    #         return (
    #             SmarcTopics.VEHICLE_HEALTH_WAITING,
    #             ">>>>>>>> Nav publisher not fresh <<<<<<<<",
    #         )
    #     if self._status_publisher.geofence_is_outside():
    #         return (
    #             SmarcTopics.VEHICLE_HEALTH_WAITING,
    #             ">>>>>>>> Geofence outside <<<<<<<<<<"
    #         )

    #     return (
    #         SmarcTopics.VEHICLE_HEALTH_READY,
    #         "=========== All checks passed ===========\n"
    #         "=========== Vehicle health ready ===========",
    #     )

    # def _status_str_callback(self) -> None:
    #     """Publish a status string containing the latest nav and system status information."""
    #     nav_status = self._status_publisher.nav_status_str()
    #     sys_str = self._status_publisher.status_str()
    #     msg = String()
    #     msg.data = f"{nav_status}\n{sys_str}"
    #     self.get_logger().info(f"Publishing status string: {msg.data}")
    #     self.nav_str_pub.publish(msg)

    # TODO: add othher callbacks (battery, dvl, geofence, odom, utm)

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
