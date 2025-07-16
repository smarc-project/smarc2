import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
import math
import tf_transformations

class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('fake_target_publisher')
        self.publisher_ = self.create_publisher(PoseStamped, 'proxops/target', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0.0

    def timer_callback(self):
        msg = PoseStamped()
        msg.header.frame_id = 'map'
        msg.header.stamp = self.get_clock().now().to_msg()

        msg.pose.position.x = 50 + 40*math.cos(self.i)
        msg.pose.position.y = 50 + 40*math.sin(self.i)

        q = tf_transformations.quaternion_from_euler(0, 0, self.i+0.25*math.pi)
        msg.pose.orientation.x = q[0]
        msg.pose.orientation.y = q[1]
        msg.pose.orientation.z = q[2]
        msg.pose.orientation.w = q[3]

        self.publisher_.publish(msg)
        self.get_logger().info("Publishing")
        self.i += 0.01


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()