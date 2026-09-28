# TODO: sam_captain node
#       publish smarc topics
#       tf tree
#       vehicle health data
#       safety and authorization

import rclpy


class SAMCaptain:
    def __init__(self):
        # TODO: init node
        # TODO call SMARCPublisher
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