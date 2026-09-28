# TODO: sam_captain node
#       publish smarc topics
#       tf tree
#       vehicle health data
#       safety and authorization

import rclpy
from rclpy.node import Node
from sam_captain.SMARCPublisher import SMARCPublisher

class SAMCaptain(Node):
    def __init__(self):
        super().__init__('sam_captain')
        self.get_logger().info('SAM Captain Node has been started.')
        self._smarc_publisher = SMARCPublisher(self)
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


if __name__ == '__main__':
    main()