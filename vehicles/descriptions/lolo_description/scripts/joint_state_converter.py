#!/usr/bin/env python3
"""Publish LoLo actuator feedback as joint states for RViz visualization."""

import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float32
from lolo_msgs.msg import Topics


class LoloJointStateConverter(Node):

    def __init__(self):
        super().__init__("joint_state_converter")

        # Names must match the URDF joint names (no robot namespace prefix).
        self.positions = {
            "elevator_joint": 0.0,
            "rudder_port_joint": 0.0,
            "rudder_stbd_joint": 0.0,
            "elevon_port_joint": 0.0,
            "elevon_stbd_joint": 0.0,
            "thruster_port_joint": 0.0,
            "thruster_stbd_joint": 0.0,
            "vert_thruster_front_port_joint": 0.0,
            "vert_thruster_front_stbd_joint": 0.0,
            "vert_thruster_back_port_joint": 0.0,
            "vert_thruster_back_stbd_joint": 0.0,
        }

        self.port_rpm = 0.0
        self.stbd_rpm = 0.0
        self.last_time = self.get_clock().now()

        self.publisher = self.create_publisher(JointState, "joint_states", 10)

        # Control-surface feedback (angles in radians).
        self.create_subscription(
            Float32, Topics.ELEVATOR_FB, self.elevator_callback, 10)
        self.create_subscription(
            Float32, Topics.RUDDER_FB, self.rudder_callback, 10)
        self.create_subscription(
            Float32, Topics.ELEVON_PORT_FB, self.elevon_port_callback, 10)
        self.create_subscription(
            Float32, Topics.ELEVON_STBD_FB, self.elevon_stbd_callback, 10)

        # Main-thruster feedback (RPM).
        self.create_subscription(
            Float32, Topics.THRUSTER_PORT_FB, self.thruster_port_callback, 10)
        self.create_subscription(
            Float32, Topics.THRUSTER_STBD_FB, self.thruster_stbd_callback, 10)

        self.create_timer(0.2, self.timer_callback)  # 5 Hz

    def elevator_callback(self, msg):
        self.positions["elevator_joint"] = -msg.data

    def rudder_callback(self, msg):
        self.positions["rudder_port_joint"] = msg.data
        self.positions["rudder_stbd_joint"] = msg.data

    def elevon_port_callback(self, msg):
        self.positions["elevon_port_joint"] = -msg.data

    def elevon_stbd_callback(self, msg):
        self.positions["elevon_stbd_joint"] = -msg.data

    def thruster_port_callback(self, msg):
        self.port_rpm = msg.data

    def thruster_stbd_callback(self, msg):
        self.stbd_rpm = msg.data

    def timer_callback(self):
        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds / 1e9
        self.last_time = now

        # Avoid an angle jump when simulated time starts or jumps during replay.
        if dt < 0 or dt > 1.0:
            dt = 0.0

        # Rotate main propellers at 10% of their measured RPM for RViz.
        scale = 0.1 * 2.0 * math.pi / 60.0
        self.positions["thruster_port_joint"] -= self.port_rpm * scale * dt
        self.positions["thruster_stbd_joint"] += self.stbd_rpm * scale * dt
        # Vertical thrusters remain at zero; not super fun to visualize.

        state = JointState()
        state.header.stamp = now.to_msg()
        state.name = list(self.positions.keys())
        state.position = list(self.positions.values())
        self.publisher.publish(state)


def main(args=None):
    rclpy.init(args=args)
    node = LoloJointStateConverter()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
