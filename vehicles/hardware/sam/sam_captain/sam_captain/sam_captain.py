import rclpy
from rclpy.node import Node
from std_msgs.msg import String
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
        self._geofence_status_sub = self.create_subscription(
            GeofenceStatusStamped,
            SmarcTopics.GEOFENCE_STATUS_TOPIC,
            self._geofence_status_callback,
            10,
        )

        # health check related
        self._health_check_timer = self.create_timer(1.0, self._pub_vehicle_health)

    # TODO: publish vehicle health (health state from sam and smarc)
    def _pub_vehicle_health(self):
        # self.get_logger().info(">>>>>>>>>>>>>>>>>> Mock vehicle health check <<<<<<<<<<<<<<<<")
        # TODO: update health state
        # TODO publish vehicle health
        # TODO: compare current and previous health state
        # if current != previous, log: not the same!
        pass
    
    def _health_str(self, health_state: int) -> str:
        """Return a readable name for a SMARC vehicle-health state."""
        health_names = {
            SmarcTopics.VEHICLE_HEALTH_READY: "READY",
            SmarcTopics.VEHICLE_HEALTH_WAITING: "WAITING",
            SmarcTopics.VEHICLE_HEALTH_ERROR: "ERROR",
        }
        return health_names.get(health_state, f"UNKNOWN({health_state})")

    # TODO: return safety and reasons
    # WARNING -> some states are missing
    # ERROR -> faulty state
    def _evaluate_vehicle_health(self):
        # TODO: 1. check abort
        is_abort = self._status_publisher._abort_latched
        # if is_abort, reutrn error
        # TODO: 2. check heartbeat
        is_heartbeat = self._status_publisher._heartbeat_received
        # if not is_heartbeat, return waiting
        # TODO: 3. check battery
        battery_percent = self._status_publisher._battery_percent
        # if battery not fresh or None, return waiting
        # if battery_percent is less than threshold, return error
        # TODO: 4. check geofence
        # if geofence is None, return waiting
        # TODO: 5. & 6. check nav and status publishers
        # if nav or status publishers not fresh, return waiting
        # TODO: if all checks are ok, return safety and reasons
        # return ready
        pass

    def _geofence_status_callback(self, msg: GeofenceStatusStamped):
        # self.get_logger().info(f"Received geofence status: {msg.status}")
        self._geofence_status = msg

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
