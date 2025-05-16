#!/usr/bin/python3

from rclpy.node import Node

from drone_msgs.msg import Links as DroneLinks
from drone_msgs.msg import Topics as DroneTopics
from smarc_msgs.msg import DVL, ThrusterFeedback, Topics

from sensor_msgs.msg import FluidPressure

from .ros_vehicle import ROSVehicle
from .vehicle import VehicleState, SensorNames, Sensor
from .vehicle import DroneVehicleState

import uuid
import json
from std_msgs.msg import String
from typing import Type

class Quadrotor(ROSVehicle): #ROSVehicle
    def __init__(self,
                 node: Node):
        super().__init__(node, DroneVehicleState, DroneLinks)
        # The super-class handles everything except the sam-specific subscriptions :D
        
        self._t1 = None
        self._t2 = None
        self._t3 = None
        self._t4 = None

        # so we sub to drone-specific stuff

        self._depth_sub = node.create_subscription(FluidPressure, DroneTopics.DEPTH_TOPIC, self._depth_cb, 10)

        self._thruster1_fb_sub = node.create_subscription(ThrusterFeedback, DroneTopics.PROP1_FB_TOPIC, self._t1_cb, 10)
        self._thruster2_fb_sub = node.create_subscription(ThrusterFeedback, DroneTopics.PROP2_FB_TOPIC, self._t2_cb, 10)
        self._thruster3_fb_sub = node.create_subscription(ThrusterFeedback, DroneTopics.PROP3_FB_TOPIC, self._t3_cb, 10)
        self._thruster4_fb_sub = node.create_subscription(ThrusterFeedback, DroneTopics.PROP4_FB_TOPIC, self._t4_cb, 10)
 

    def _t1_cb(self, data:ThrusterFeedback):
        self._t1 = data.rpm.rpm
        self._vehicle_state.update_sensor(SensorNames.THRUSTERS, [self._t1, self._t2, self._t3, self._t4], data.header.stamp.sec)
    def _t2_cb(self, data:ThrusterFeedback):
        self._t2 = data.rpm.rpm
        self._vehicle_state.update_sensor(SensorNames.THRUSTERS, [self._t1, self._t2, self._t3, self._t4], data.header.stamp.sec)
    def _t3_cb(self, data:ThrusterFeedback):
        self._t3 = data.rpm.rpm
        self._vehicle_state.update_sensor(SensorNames.THRUSTERS, [self._t1, self._t2, self._t3, self._t4], data.header.stamp.sec)
    def _t4_cb(self, data:ThrusterFeedback):
        self._t4 = data.rpm.rpm
        self._vehicle_state.update_sensor(SensorNames.THRUSTERS, [self._t1, self._t2, self._t3, self._t4], data.header.stamp.sec)

    def _depth_cb(self, data:FluidPressure):
        # 9806.65 Pa ~= 1m water
        # 101325 Pa = 1 atmo
        water_pressure = (data.fluid_pressure - 101325)
        water_depth = water_pressure / 9806.65
        self._vehicle_state.update_sensor(SensorNames.DEPTH, [water_depth], data.header.stamp.sec)


            

def test_quad():
    import rclpy, sys
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("test_sam_auv")
    v = Quadrotor(node)

    def update():
        nonlocal v
        print(v)

    node.create_timer(0.5, update)
    rclpy.spin(node)

if __name__ == "__main__":
    test_quad()