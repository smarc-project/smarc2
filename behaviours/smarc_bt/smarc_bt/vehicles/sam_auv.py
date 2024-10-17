#!/usr/bin/python3

from rclpy.node import Node
import rclpy.time as time

from smarc_msgs.msg import DVL, ThrusterFeedback
from sam_msgs.msg import Topics as SamTopics
from sam_msgs.msg import Links as SamLinks
from sam_msgs.msg import PercentStamped
from smarc_msgs.msg import Leak
from sensor_msgs.msg import FluidPressure

from .ros_vehicle import ROSVehicle
from .vehicle import UnderwaterVehicleState, SensorNames


class SAMAuv(ROSVehicle):
    def __init__(self,
                 node: Node):
        super().__init__(node, UnderwaterVehicleState, SamLinks)
        # The super-class handles everything except the sam-specific subscriptions :D


        # so we sub to sam-specific stuff
        self._dvl_sub = node.create_subscription(DVL, SamTopics.DVL_TOPIC, self._dvl_cb, 10)
        self._depth_sub = node.create_subscription(FluidPressure, SamTopics.DEPTH_TOPIC, self._depth_cb, 10)
        self._leak_sub = node.create_subscription(Leak, SamTopics.LEAK_TOPIC, self._leak_cb, 10)
        self._vbs_sub = node.create_subscription(PercentStamped, SamTopics.VBS_FB_TOPIC, self._vbs_cb, 10)
        self._lcg_sub = node.create_subscription(PercentStamped, SamTopics.LCG_FB_TOPIC, self._lcg_cb, 10)
        self._thruster1_fb_sub = node.create_subscription(ThrusterFeedback, SamTopics.THRUSTER1_FB_TOPIC, self._t1_cb, 10)
        self._thruster2_fb_sub = node.create_subscription(ThrusterFeedback, SamTopics.THRUSTER2_FB_TOPIC, self._t2_cb, 10)

        self._t1 = None
        self._t2 = None

    def _dvl_cb(self, data:DVL):
        self._vehicle_state.update_sensor(SensorNames.ALTITUDE, [data.altitude], data.header.stamp.sec)

    def _depth_cb(self, data:DVL):
        # 9806.65 Pa ~= 1m water
        # 101325 Pa = 1 atmo
        water_pressure = (data.fluid_pressure - 101325)
        water_depth = water_pressure / 9806.65
        self._vehicle_state.update_sensor(SensorNames.DEPTH, [water_depth], data.header.stamp.sec)

    def _leak_cb(self, data:Leak):
        sec,_ = time.Time().seconds_nanoseconds()
        self._vehicle_state.update_sensor(SensorNames.LEAK, [data.value], sec)

    def _vbs_cb(self, data:PercentStamped):
        self._vehicle_state.update_sensor(SensorNames.VBS, [data.value], data.header.stamp.sec)

    def _lcg_cb(self, data:PercentStamped):
        self._vehicle_state.update_sensor(SensorNames.LCG, [data.value], data.header.stamp.sec)

    def _t1_cb(self, data:ThrusterFeedback):
        self._t1 = data.rpm.rpm
        self._vehicle_state.update_sensor(SensorNames.THRUSTERS, [self._t1, self._t2], data.header.stamp.sec)

    def _t2_cb(self, data:ThrusterFeedback):
        self._t2 = data.rpm.rpm
        self._vehicle_state.update_sensor(SensorNames.THRUSTERS, [self._t1, self._t2], data.header.stamp.sec)


def test_sam_auv():
    import rclpy, sys
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("test_sam_auv")
    v = SAMAuv(node)

    def update():
        nonlocal v
        print(v)

    node.create_timer(0.5, update)
    rclpy.spin(node)
