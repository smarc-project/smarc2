import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from smarc_control_msgs.msg import Topics as ControlTopics

import numpy as np

class PosePublisher(Node):
    def __init__(self):
        super().__init__('pose_publisher')
        self.publisher_ = self.create_publisher(PoseStamped, ControlTopics.MOCAP_HYDROPOINT, 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "KTHTank World/mocap"  

        # Hula position
        msg.pose.position.x = 6.75
        msg.pose.position.y = 0.0
        msg.pose.position.z = 0.0

        msg.pose.orientation.x = 0.0
        msg.pose.orientation.y = 0.0
        msg.pose.orientation.z = np.sqrt(2)
        msg.pose.orientation.w = np.sqrt(2)

        self.publisher_.publish(msg)
        #self.get_logger().info('Publishing: "%s"' % msg)

def main(args=None):
    rclpy.init(args=args)
    node = PosePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

