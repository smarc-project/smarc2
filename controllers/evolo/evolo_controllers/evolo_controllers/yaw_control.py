#! /usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from rclpy.executors import MultiThreadedExecutor

from evolo_msgs.msg import Topics as evoloTopics
from smarc_msgs.msg import Topics as SmarcTopics
from smarc_control_msgs.msg import Topics as ControlTopics
import json

#Basic PID regulator
class yaw_control(Node):
    def __init__(self):
        super().__init__("yaw_control")
        self.logger = self.get_logger()
        self.logger.info("yaw_control!")

        self.declare_node_parameters()

        self.update_rate = float(self.get_parameter("update_rate").value)
        self.logger.info(f"update rate: {self.update_rate}")
        self.robot_name = self.get_parameter("robot_name").value

    
        self.yaw_setpoint = None
        self.yaw_setpoint_time = None

        #Control inputs.
        self.create_subscription(Float32, 
                                 f"{ControlTopics.CONTROL_YAW_TOPIC}", self.yaw_cb, 1)
        #Outputs
        self.evolo_pub = self.create_publisher(String,
                                                f"{evoloTopics.EVOLO_CAPTAIN_TO}", 1)

    def time_now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def declare_node_parameters(self):
        self.declare_parameter("update_rate", 1)
        self.declare_parameter("robot_name", "evolo")

    def yaw_cb(self, msg):
        self.yaw_setpoint = msg.data
        self.yaw_setpoint_time = self.time_now()


    def update(self):
        now = self.time_now()

        if self.yaw_setpoint_time is not None and now-self.yaw_setpoint_time < 1 and self.yaw_setpoint is not None:
            #Convert yaw to NED and degrees
            target_course = -math.degrees(self.yaw_setpoint) + 90
            while(target_course < 0):
                target_course+=360
            while(target_course >= 360):
                target_course -= 360

            #TODO send YAW command to evolo
            msg = String()

            target = {"ctt": target_course,"dtt": 100, "sogAim": "fly"}
            msg.data = json.dumps({"setTarget": target})
            self.evolo_pub.publish(msg)


            self.logger.info(f"sending target course={target_course}")

        else:
            msg = String()
            target = {"sogAim": "stop"}
            msg.data = json.dumps({"setTarget": target})
            self.evolo_pub.publish(msg)
            self.logger.info(f"sending stop")


def main(args=None, namespace=None):
    rclpy.init(args=args)
    control_node = yaw_control()

    control_node.create_timer(1.0/control_node.update_rate, control_node.update)
    executor = MultiThreadedExecutor()
    executor.add_node(control_node)
    executor.spin()
