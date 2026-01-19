#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sam_msgs.msg import ThrusterAngles, Topics
import math
from smarc_msgs.msg import ThrusterRPM

class CircularThrustVectorPublisher(Node):

    def __init__(self):
        super().__init__('circular_thrust_vector_publisher')

        # Publisher for thrust vector angles
        self.vector_pub = self.create_publisher(
            ThrusterAngles,
            "/sam/core/thrust_vector_cmd",
            qos_profile=1
        )

        self.thrust1_pub = self.create_publisher(ThrusterRPM, "/sam/core/thruster1_cmd",  qos_profile=1)
        self.thrust2_pub = self.create_publisher(ThrusterRPM, "/sam/core/thruster2_cmd",  qos_profile=1)

        # Timer to update and send commands
        self.timer_period = 0.1  # 10 Hz
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        # Internal state for angle calculation
        self.t = 0.0
        self.get_logger().info("Circular thrust vector publisher started.")

    def timer_callback(self):
        # Circle radius in radians
        radius = 0.1  # Must match actuator limits from your original code
        frequency = 0.2  # Hz, how many full cycles per second
        omega = 2 * math.pi * frequency

        # Compute current angle vector (simple circular motion)
        horizontal = 0.0 #radius * math.cos(omega * self.t)
        vertical = 0.0 #radius * math.sin(omega * self.t)

        # Create and publish message
        msg = ThrusterAngles()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.thruster_horizontal_radians = horizontal
        msg.thruster_vertical_radians = vertical
        self.vector_pub.publish(msg)

        rpm_msg = ThrusterRPM()        
        rpm_msg.rpm = 0
        self.thrust1_pub.publish(rpm_msg)
        rpm_msg.rpm = 0
        self.thrust2_pub.publish(rpm_msg) 

        self.get_logger().info(f"Published vector: h={horizontal:.3f}, v={vertical:.3f}", throttle_duration_sec=1)

        self.t += self.timer_period

def main(args=None):
    rclpy.init(args=args)
    node = CircularThrustVectorPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
