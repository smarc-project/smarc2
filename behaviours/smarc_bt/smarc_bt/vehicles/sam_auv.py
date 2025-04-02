#!/usr/bin/python3

from rclpy.node import Node
from rclpy.parameter import Parameter

from smarc_msgs.msg import DVL, ThrusterFeedback, Topics
from sam_msgs.msg import Topics as SamTopics
from sam_msgs.msg import Links as SamLinks
from smarc_msgs.msg import Leak, PercentStamped
from sensor_msgs.msg import FluidPressure

from .ros_vehicle import ROSVehicle, WaraPSVehicle
from .vehicle import UnderwaterVehicleState, SensorNames


import json
from std_msgs.msg import String
from typing import Type

class SAMAuv(ROSVehicle): #ROSVehicle
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
        sec,_ = self._node.get_clock().now().seconds_nanoseconds()
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


# extend the SAMAuv class using WaraPSVehicle instead of ROSVehicle
class SAMAuvWaraPS(SAMAuv, WaraPSVehicle):

    def __init__(self, node: Node):
        super().__init__(node)

        self._wara_ps_dict = {
            "agent-type": "subsurface",
            "agent-uuid": self._robot_name,
            "levels": ["sensor, direct execution"],
            "name": self._robot_name,
            "pulse_rate": 1.0,
        }        
        # self._wara_ps_pitch_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_INFO_TOPIC, 10)
        # self._wara_ps_roll_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_INFO_TOPIC, 10)


    def wara_ps_dict(self):
        """Override default WARA-PS dictionary to use sam-specific values"""
        # self._node.get_logger().info(f"Using WARA-PS dict: {self._wara_ps_dict}")
        return self._wara_ps_dict
    
    def _to_publish(self, prev_time, now_time):
        # check if the time is greater than 1/self._wara_ps_dict["rate"]
        if prev_time is None:
            prev_time = now_time
            to_publish = True

        elif now_time - prev_time >= 1.0/self._wara_ps_dict["pulse_rate"]:
            prev_time = now_time
            to_publish = True
        else:
            to_publish = False

        return to_publish



    def wara_ps_heartbeat(self, prev_time, now_time):
        """Override default heartbeat to use sam-specific message"""

        to_beat = self._to_publish(prev_time, now_time)

        if to_beat:
            heartbeat_data = {
                "agent-type": self.wara_ps_dict()["agent-type"],
                "agent-uuid": self.wara_ps_dict()["agent-uuid"],
                "levels": self.wara_ps_dict()["levels"],
                "name": self.wara_ps_dict()["name"],
                "rate": self._wara_ps_dict["pulse_rate"],
                "stamp": now_time,
                # "stamp": self._node.get_clock().now().to_msg().sec + self._node.get_clock().now().to_msg().nanosec * 1e-9,
                "type": "HeartBeat"
            }
            msg = String()
            msg.data = json.dumps(heartbeat_data)
            self._wara_ps_heartbeat_pub.publish(msg)
            self._node.get_logger().info('Published Heartbeat message')
        else:
            self._node.get_logger().info('Heartbeat not sent, waiting for next tick')
        return to_beat
    
    def wara_ps_lvl1(self, prev_time, now_time):
        
        to_pub = self._to_publish(prev_time, now_time)

        if to_pub:
            # 1. publish sensor data
            sensor_info_msg = {
                "name": self._robot_name,
                "rate": self._wara_ps_dict["pulse_rate"],
                "sensor-data-provided": [
                    "position",
                    "course",
                    "speed",
                    # "roll",
                    # "pitch",
                    "executing_tasks"
                ],
            }
            msg = String()
            msg.data = json.dumps(sensor_info_msg)
            self._wara_ps_sensor_info_pub.publish(msg)
            # example
            # {
            #     "name": "Evolo",
            #     "rate": 0.1,
            #     "sensor-data-provided": [
            #         "position",
            #         "course",
            #         "speed",
            #         "roll",
            #         "pitch",
            #         "executing_tasks"
            #     ],
            #     "stamp": 1743583524,
            #     "type": "SensorInfo"
            # }

            # 2. publish position data
            # print(self._vehicle_state[SensorNames.ALTITUDE]._value_names)
                                      
            position_msg = {
                "latitude": self._vehicle_state[SensorNames.GLOBAL_POSITION]['lat'],
                "longitude": self._vehicle_state[SensorNames.GLOBAL_POSITION]['lon'],
                "altitude": 0, # self._vehicle_state[SensorNames.ALTITUDE][0], #TODO: this is fake
                "type": "GeoPoint"
            }
            # example
            # {
            #   "latitude": 0,
            #   "longitude": 0,
            #   "altitude": 0,
            #   "type": "GeoPoint"
            # }
            msg = String()
            msg.data = json.dumps(position_msg)
            self._wara_ps_position_pub.publish(msg)
            self._node.get_logger().info('Published Position message')


            #TODO: this stuff is strings, but wara-ps expects floats. Our json bridge only handles strings

            # 3. publish course data
            course_msg = String()
            course_msg.data = f"{self._vehicle_state[SensorNames.GLOBAL_HEADING_DEG][0]}"
            # float
            self._wara_ps_speed_pub.publish(course_msg)
            self._node.get_logger().info('Published Course message')
            
            # 4. publish speed data
            speed_msg = String()
            # speed_msg.data = f"{self._vehicle_state[SensorNames.SPEED][0]}"
            speed_msg.data = f"69" # TODO: this is FAKE!
            # float
            self._wara_ps_speed_pub.publish(speed_msg)
            self._node.get_logger().info('Published Speed message')

            # TODO: 5. publish roll data
            # TODO: 6. publish pitch data
            

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
