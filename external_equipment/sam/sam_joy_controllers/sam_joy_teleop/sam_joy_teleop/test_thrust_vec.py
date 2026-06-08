#!/usr/bin/env python3

import math
import numpy as np

import rclpy
from rclpy.node import Node
from sam_msgs.msg import ThrusterAngles, Topics
from smarc_msgs.msg import ThrusterRPM
import numpy as np


class CircularThrustVectorPublisher(Node):
    def __init__(self):
        super().__init__("circular_thrust_vector_publisher")

        # Publisher for thrust vector angles
        self.vector_pub = self.create_publisher(
            ThrusterAngles, "/sam/core/thrust_vector_cmd", qos_profile=1
        )

        self.rudder_max_angle = np.deg2rad(7)
        self.rpm_fwd = 500
        self.rpm_bwd = -600
        self.n_sim = 30 # length of primitive
        self.total_iterations = 300

        self.thrust1_pub = self.create_publisher(ThrusterRPM, "/sam/core/thruster1_cmd",  qos_profile=1)
        self.thrust2_pub = self.create_publisher(ThrusterRPM, "/sam/core/thruster2_cmd",  qos_profile=1)

        # Timer to update and send commands
        self.timer_period = 0.1  # 10 Hz
        # self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.turbo_turn("left")

        # Internal state for angle calculation
        self.t = 0.0
        # self.get_logger().info("Circular thrust vector publisher started.")

    def turbo_turn(self, direction):
        self.get_logger().info("Testing turbo turn.")

        u = np.array([0, 50, 0, self.rudder_max_angle, self.rpm_fwd, self.rpm_fwd])

        i = 0
        # while ros node is ok
        while rclpy.ok()  and i < self.total_iterations:

            # Set the rudder angle and the thruster commands based on the direction of the turn        
            u[3] = self.rudder_max_angle if direction == "left" else -self.rudder_max_angle
            # Start with forward motion 
            u[4] = u[5] = self.rpm_fwd

            for j in range(0, self.n_sim):
            
                msg = ThrusterAngles()
                msg.header.stamp = self.get_clock().now().to_msg()
                msg.thruster_vertical_radians = u[2]
                msg.thruster_horizontal_radians = u[3]
                self.vector_pub.publish(msg)    
            
                rpm_msg = ThrusterRPM()        
                rpm_msg.rpm = -u[4]
                self.thrust1_pub.publish(rpm_msg)
                rpm_msg.rpm = u[5]
                self.thrust2_pub.publish(rpm_msg) 

            # Alternate the rudder angle to perform a turn in place
            u[3] *= -1 
            # Alternate the direction of the thrusters to perform a turn in place
            u[5] = u[4] = self.rpm_bwd if np.sign(u[4]) > 0 else self.rpm_fwd
            i += 1

    def timer_callback(self):
        # Circle radius in radians
        radius = np.deg2rad(-7)  # Must match actuator limits from your original code
        frequency = 0.2  # Hz, how many full cycles per second
        omega = 2 * math.pi * frequency

        # Compute current angle vector (simple circular motion)
        horizontal = 0.0 # radius * math.cos(omega * self.t)
        vertical = radius  # radius * math.sin(omega * self.t)

        # Create and publish message
        msg = ThrusterAngles()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.thruster_horizontal_radians = horizontal
        msg.thruster_vertical_radians = vertical
        self.vector_pub.publish(msg)

        rpm_msg = ThrusterRPM()
        rpm_msg.rpm = 400
        self.thrust1_pub.publish(rpm_msg)
        rpm_msg.rpm = 400
        self.thrust2_pub.publish(rpm_msg)

        self.get_logger().info(
            f"Published vector: h={horizontal:.3f}, v={vertical:.3f}",
            throttle_duration_sec=1,
        )

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


if __name__ == "__main__":
    main()
