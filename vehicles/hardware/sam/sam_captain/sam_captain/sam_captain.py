import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sam_captain.SAMNavPublisher import SAMNavPublisher
from sam_captain.SAMStatusPublisher import SAMStatusPublisher
from sam_msgs.msg import Topics as SamTopics


class SAMCaptain(Node):
    def __init__(self):
        super().__init__("sam_captain")
        self.get_logger().info("SAM Captain Node has been started.")
        self._nav_publisher = SAMNavPublisher(self)
        self._status_publisher = SAMStatusPublisher(self)

        # TEST, will remove later
        self.nav_str_pub = self.create_publisher(String, SamTopics.STATUS_STRING_TOPIC, 10)
        # self._publish_nav()
        self._status_str_timer = self.create_timer(1.0, self._publish_status_string)


    # def _publish_nav(self):
    #     self.get_logger().info("Publishing nav status string.")
    #     # msg = self._nav_publisher.nav_status_str()
    #     msg = String()
    #     msg.data = "TEST NAV STATUS STRING"
    #     self.nav_str_pub.publish(msg)
    
    # TODO: create status_string publisher and timer callback
    def _publish_status_string(self):
        # self.get_logger().info("Publishing status string.")
        nav_status = self._nav_publisher.nav_status_str()
        sys_str = self._status_publisher.status_str()
        # debug
        # self.get_logger().info(f"Nav status: {nav_status}")
        # self.get_logger().info(f"System status: {sys_str}")

        msg = String()
        msg.data = f"{nav_status}\n{sys_str}"
        self.get_logger().info(f"Publishing status string: {msg.data}")
        self.nav_str_pub.publish(msg)

    # TODO: create sam_health_checker to check if vehicle_health is ready, error or waiting
    def _health_check_callback(self):
        pass
    # TODO: create sam_captain_status_str callback to publish status string
    def _status_str_callback(self):
        # TODO: call nav_status_str and status_str
        # TODO: combine string
        # TODO: publish combined string
        pass


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
