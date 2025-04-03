import json
from typing import Type
from rclpy.node import Node
from std_msgs.msg import String
from smarc_msgs.msg import Topics
from smarc_bt.vehicles.sensor import Sensor, SensorNames
from smarc_bt.vehicles.vehicle import IVehicleState


class WaraPSVehicle():

    def __init__(self, 
                 node:Node, 
                 vehicle_state:Type[IVehicleState], 
                 wara_ps_dict:dict = None,
                 ):
                        
        # common definitions, independent of vehicle
        
        self._node = node
        self._robot_name = node.get_parameter("robot_name").value
        self._vehicle_state = vehicle_state

        # Publishers for WARA-PS topics
        self._wara_ps_heartbeat_pub = node.create_publisher(String, Topics.WARA_PS_HEARTBEAT_TOPIC, 10)
        self._wara_ps_position_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_POSITION_TOPIC, 10)
        self._wara_ps_heading_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_HEADING_TOPIC, 10)
        self._wara_ps_course_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_COURSE_TOPIC, 10)
        self._wara_ps_speed_pub = node.create_publisher(String, Topics.
        WARA_PS_SENSOR_SPEED_TOPIC, 10)
        self._wara_ps_sensor_info_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_INFO_TOPIC, 10)


        self._wara_ps_dict = wara_ps_dict

        self._heartbeat_data = {
            "agent-type": self._wara_ps_dict["agent-type"],
            "agent-uuid": self._wara_ps_dict["agent-uuid"],
            "levels": self._wara_ps_dict["levels"],
            "name": self._wara_ps_dict["name"],
            "rate": self._wara_ps_dict["pulse_rate"],
            "stamp": "",
            # "stamp": self._node.get_clock().now().to_msg().sec + self._node.get_clock().now().to_msg().nanosec * 1e-9,
            "type": "HeartBeat"
        }

        self._sensor_info_msg = {
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
        
        to_beat = self._to_publish(prev_time, now_time)

        if to_beat:
            # update the heartbeat data
            self._heartbeat_data["stamp"] = now_time
            
            # publish the heartbeat data
            msg = String()
            msg.data = json.dumps(self._heartbeat_data)
            self._wara_ps_heartbeat_pub.publish(msg)
            self._node.get_logger().info('Published Heartbeat message')
        
        return to_beat
    
    def wara_ps_lvl1(self, prev_time, now_time):
        
        to_pub = self._to_publish(prev_time, now_time)

        if to_pub:
            # 1. publish sensor data
            msg = String()
            msg.data = json.dumps(self._sensor_info_msg)
            self._wara_ps_sensor_info_pub.publish(msg)

                                      
            position_msg = {
                "latitude": self._vehicle_state[SensorNames.GLOBAL_POSITION]['lat'],
                "longitude": self._vehicle_state[SensorNames.GLOBAL_POSITION]['lon'],
                "altitude": -self._vehicle_state[SensorNames.DEPTH][0],
                "type": "GeoPoint"
            }
            msg = String()
            msg.data = json.dumps(position_msg)
            self._wara_ps_position_pub.publish(msg)
            self._node.get_logger().info('Published Position message')


            #TODO: this stuff is strings, but wara-ps expects floats. Our json bridge only handles strings. Github Issue exists for this.

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

        return to_pub