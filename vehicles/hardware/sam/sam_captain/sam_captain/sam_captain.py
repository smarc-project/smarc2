import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int8
from sam_captain.SAMNavPublisher import SAMNavPublisher
from sam_captain.SAMStatusPublisher import SAMStatusPublisher
from sam_msgs.msg import Topics as SamTopics
from smarc_msgs.msg import GeofenceStatusStamped, Topics as SmarcTopics


class SAMCaptain(Node):
    def __init__(self):
        super().__init__("sam_captain")
        self.get_logger().info("SAM Captain Node has been started.")

        # TODO parameters

        # call publisher classes
        self._nav_publisher = SAMNavPublisher(self)
        self._status_publisher = SAMStatusPublisher(self)

        # status string
        self.nav_str_pub = self.create_publisher(
            String, SamTopics.STATUS_STRING_TOPIC, 10
        )
        self._status_str_timer = self.create_timer(1.0, self._status_str_callback)

        # geofence related
        self._geofence_status = None
        self._last_geofence_status_time = None
        self._max_geofence_status_age = 3.0
        self._geofence_status_sub = self.create_subscription(
            GeofenceStatusStamped,
            SmarcTopics.GEOFENCE_STATUS_TOPIC,
            self._geofence_status_callback,
            10,
        )

        # health check related
        self._max_battery_age = 1.0  # TODO: set max battery age in seconds
        self._max_nav_age = 1.0  # TODO: set max nav age in seconds
        self._max_heartbeat_age = 1.0  # TODO: set max heartbeat age in seconds
        self._battery_threshold = 0.3
        self._vehicle_health = Int8() # TODO: set initial vehicle health state
        self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_WAITING # TODO: set initial vehicle health state
        self._vehicle_health_reason = "Initial state" # TODO: set initial vehicle health reason

        self._vehicle_health_pub = self.create_publisher(Int8, SamTopics.VEHICLE_HEALTH_TOPIC, 10)

        self._health_check_timer = self.create_timer(1.0, self._pub_vehicle_health)

    def _pub_vehicle_health(self):
        # self.get_logger().info(">>>>>>>>>>>>>>>>>> Mock vehicle health check <<<<<<<<<<<<<<<<")
        prev_health = self._vehicle_health
        prev_reason = self._vehicle_health_reason
        self._vehicle_health.data, self._vehicle_health_reason = self._evaluate_vehicle_health()
        self.get_logger().info(f"Publishing vehicle health: {self._vehicle_health}, reason: {self._vehicle_health_reason}")
        self._vehicle_health_pub.publish(self._vehicle_health)

        if self._vehicle_health.data != prev_health.data:
            self.get_logger().warn(f"Vehicle health state changed from {self._health_str(prev_health.data)} to {self._health_str(self._vehicle_health.data)}")
            self.get_logger().warn(f"Vehicle health reason changed from '{prev_reason}' to '{self._vehicle_health_reason}'")

    def _health_str(self, health_state: int) -> str:
        """Return a readable name for a SMARC vehicle-health state."""
        health_names = {
            SmarcTopics.VEHICLE_HEALTH_READY: "READY",
            SmarcTopics.VEHICLE_HEALTH_WAITING: "WAITING",
            SmarcTopics.VEHICLE_HEALTH_ERROR: "ERROR",
        }
        return health_names.get(health_state, f"UNKNOWN({health_state})")

    def _evaluate_vehicle_health(self):
        is_abort = self._status_publisher._abort_latched
        if is_abort:
            return SmarcTopics.VEHICLE_HEALTH_ERROR, "!!!!!!!!!!! Abort latched !!!!!!!!!!!"
        
        # is_heartbeat = self._status_publisher._heartbeat_received
        # if not is_heartbeat:
        #     return SmarcTopics.VEHICLE_HEALTH_WAITING, ">>>>>>>> No heartbeat received <<<<<<<<"
        if not self._status_publisher.heartbeat_is_fresh(self._max_heartbeat_age):
            return (
                SmarcTopics.VEHICLE_HEALTH_WAITING,">>>>>>>> Heartbeat missing or stale <<<<<<<<",)
        battery_percent = self._status_publisher._battery_percent
        is_fresh_battery = self._status_publisher.battery_is_fresh(self._max_battery_age)
        if battery_percent is None or not is_fresh_battery:
            return SmarcTopics.VEHICLE_HEALTH_WAITING, ">>>>>>>> Battery not fresh or None <<<<<<<<"
        
        if battery_percent < self._battery_threshold:
            return SmarcTopics.VEHICLE_HEALTH_ERROR, ">>>>>>>> Battery below threshold <<<<<<<<"
        
        # if self._geofence_status is None:
        #     return SmarcTopics.VEHICLE_HEALTH_WAITING, ">>>>>>>> No geofence status received <<<<<<<<"
        if not self._geofence_status_is_fresh():
            return (
                SmarcTopics.VEHICLE_HEALTH_WAITING,
                ">>>>>>>> Geofence status missing or stale <<<<<<<<",
            )
        is_nav_fresh = self._nav_publisher.global_navigation_is_fresh(
            self._max_nav_age
        )
        if not is_nav_fresh:
            return SmarcTopics.VEHICLE_HEALTH_WAITING, ">>>>>>>> Nav publisher not fresh <<<<<<<<"
        
        return SmarcTopics.VEHICLE_HEALTH_READY, "=========== All checks passed ==========="

    def _geofence_status_callback(self, msg: GeofenceStatusStamped):
        # self.get_logger().info(f"Received geofence status: {msg.status}")
        self._geofence_status = msg
        self._last_geofence_status_time = self.get_clock().now()

    def _geofence_status_is_fresh(self) -> bool:
        if self._last_geofence_status_time is None:
            return False
        age_ns = (self.get_clock().now() - self._last_geofence_status_time).nanoseconds
        return age_ns <= self._max_geofence_status_age * 1e9

    def _status_str_callback(self):
        nav_status = self._nav_publisher.nav_status_str()
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
