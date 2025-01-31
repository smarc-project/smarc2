#!/usr/bin/env python3

import rclpy
import math
from rclpy.node import Node
from sensor_msgs.msg import JointState
from smarc_msgs.msg import FloatStamped, ThrusterFeedback

class LoloJointStateConverter(Node):

    def elevon_port_callback(self, msg):
        state = JointState()
        state.name = ["lolo/elevon_port_joint"]
        state.position = [-msg.data]
        self.joint_state_pub.publish(state)

    def elevon_stbd_callback(self, msg):
        state = JointState()
        state.name = ["lolo/elevon_stbd_joint"]
        state.position = [-msg.data]
        self.joint_state_pub.publish(state)

    def rudder_callback(self, msg):
        state = JointState()
        state.name = ["lolo/rudder_port_joint", "lolo/rudder_stbd_joint"]
        state.position = [msg.data, msg.data]
        self.joint_state_pub.publish(state)

    def elevator_callback(self, msg):
        state = JointState()
        state.name = ["lolo/elevator_joint"]
        state.position = [-msg.data]
        self.joint_state_pub.publish(state)

    def thruster_port_callback(self, msg):
        state = JointState()
        state.name = ["lolo/thruster_joint_port"]
        self.velocities[0] = -0.1 * 2.*math.pi/60.*float(msg.rpm.rpm)
        state.velocity = [self.velocities[0]]
        self.joint_state_pub.publish(state)

    def thruster_stbd_callback(self, msg):
        state = JointState()
        state.name = ["lolo/thruster_joint_stbd"]
        self.velocities[1] = 0.1 * 2.*math.pi/60.*float(msg.rpm.rpm)
        state.velocity = [self.velocities[1]]
        self.joint_state_pub.publish(state)

    def timer_callback(self):
        state = JointState()
        state.name = ["lolo/thruster_port_joint", "lolo/thruster_stbd_joint"]
        duration = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
        state.position = [duration * vel for vel in self.velocities]
        self.joint_state_pub.publish(state)

    def __init__(self):
        super().__init__('joint_state_converter')
        self.joint_state_pub = self.create_publisher(JointState, "command_states", 10)

        self.create_subscription(FloatStamped, "core/elevon_strb_fb", self.elevon_stbd_callback, 10)
        self.create_subscription(FloatStamped, "core/elevon_port_fb", self.elevon_port_callback, 10)
        self.create_subscription(FloatStamped, "core/elevator_fb", self.elevator_callback, 10)
        self.create_subscription(FloatStamped, "core/rudder_fb", self.rudder_callback, 10)
        self.create_subscription(ThrusterFeedback, "core/thruster1_fb", self.thruster_port_callback, 10)
        self.create_subscription(ThrusterFeedback, "core/thruster2_fb", self.thruster_stbd_callback, 10)

        self.start_time = self.get_clock().now()
        self.velocities = [0., 0.]
        self.create_timer(0.1, self.timer_callback)


def main(args=None):
    rclpy.init(args=args)
    converter = LoloJointStateConverter()
    rclpy.spin(converter)
    converter.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()