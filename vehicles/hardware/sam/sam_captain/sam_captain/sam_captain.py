import rclpy
from rclpy.node import Node
from sam_captain.SAMNavPublisher import SAMNavPublisher
from sam_captain.SAMStatusPublisher import SAMStatusPublisher
from sam_msgs.msg import Topics as SamTopics


class SAMCaptain(Node):
    def __init__(self):
        super().__init__("sam_captain")
        self.get_logger().info("SAM Captain Node has been started.")
        self._nav_publisher = SAMNavPublisher(self)
        self._status_publisher = SAMStatusPublisher(self)

        # TODO: create status_string publisher and timer callback

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
