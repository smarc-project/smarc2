#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import math


class PosePublisher(Node):
    def __init__(self):
        super().__init__('pose_publisher')

        from rclpy.parameter import Parameter
        self.set_parameters([
            Parameter('use_sim_time', Parameter.Type.BOOL, True)
        ])
        
        self.publisher_ = self.create_publisher(PoseStamped, '/M350/move_to_setpoint', 10)
        timer_period = 0.1  # 10 Hz
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.get_logger().info('Publishing PoseStamped at 10 Hz on /M350/move_to_setpoint')


    def euler_to_quaternion(self, roll, pitch, yaw):
        """
        Convert Euler angles (in radians) to Quaternion.
        """
        qx = math.sin(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) - math.cos(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
        qy = math.cos(roll/2) * math.sin(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.cos(pitch/2) * math.sin(yaw/2)
        qz = math.cos(roll/2) * math.cos(pitch/2) * math.sin(yaw/2) - math.sin(roll/2) * math.sin(pitch/2) * math.cos(yaw/2)
        qw = math.cos(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
        return qx, qy, qz, qw


    def timer_callback(self):
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "M350/map"

        # Example setpoint (you can change this as needed)
        msg.pose.position.x = 0.0
        msg.pose.position.y = -15.0 # 0.0 #-15.0   # auv position
        msg.pose.position.z = 7.0 # 8.7 # 1.0 # 5.0  #8.7


        # Orientation: yaw = 45° east
        roll, pitch, yaw = 0.0, 0.0, math.radians(0.0)
        qx, qy, qz, qw = self.euler_to_quaternion(roll, pitch, yaw)

        msg.pose.orientation.x = qx
        msg.pose.orientation.y = qy
        msg.pose.orientation.z = qz
        msg.pose.orientation.w = qw


        self.publisher_.publish(msg)
        self.get_logger().debug(f'Publishing: {msg}')


def main(args=None):
    rclpy.init(args=args)
    node = PosePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()