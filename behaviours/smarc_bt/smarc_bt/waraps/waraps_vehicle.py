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
                 vehicle_state:Type[IVehicleState], wara_ps_dict:Type[dict]):
                        
        # private variables
        self._node = node
        self._vehicle_state = vehicle_state

        self._logger = node.get_logger()

        # Publishers for Level 1 WARA-PS topics
        self._wara_ps_heartbeat_pub = node.create_publisher(String, Topics.WARA_PS_HEARTBEAT_TOPIC, 10)
        self._wara_ps_position_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_POSITION_TOPIC, 10)
        self._wara_ps_heading_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_HEADING_TOPIC, 10)
        self._wara_ps_course_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_COURSE_TOPIC, 10)
        self._wara_ps_speed_pub = node.create_publisher(String, Topics.
        WARA_PS_SENSOR_SPEED_TOPIC, 10)
        self._wara_ps_roll_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_ROLL_TOPIC, 10)
        self._wara_ps_pitch_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_PITCH_TOPIC, 10)
        self._wara_ps_depth_pub = node.create_publisher(String, Topics.WARA_PS_SENSOR_DEPTH_TOPIC, 10)

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

        self._sensor_info_data = {
            "name": self._wara_ps_dict["name"],
            "rate": self._wara_ps_dict["pulse_rate"],
            "sensor-data-provided": [
                "position",
                "course",
                "speed",
                "roll",
                "pitch",
                "depth",
                "executing_tasks"
            ],

        "stamp": "",
        "type": "SensorInfo"
        }

    def wara_ps_dict(self):
        """Override default WARA-PS dictionary to use sam-specific values"""
        # self._node.get_logger().info(f"Using WARA-PS dict: {self._wara_ps_dict}")
        return self._wara_ps_dict
    

    def wara_ps_heartbeat(self, now_time):
        
        # update the heartbeat data
        self._heartbeat_data["stamp"] = now_time
        
        # publish the heartbeat data
        msg = String()
        msg.data = json.dumps(self._heartbeat_data)
        self._wara_ps_heartbeat_pub.publish(msg)
        self._node.get_logger().info('Published Heartbeat message')
        
        return True
    

    def wara_ps_lvl1(self, now_time):
        
        # 1. publish sensor info data

        self._sensor_info_data["stamp"] = now_time

        msg = String()
        msg.data = json.dumps(self._sensor_info_data)
        self._wara_ps_sensor_info_pub.publish(msg)

                                    
        position_msg = {
            "latitude": self._vehicle_state[SensorNames.GLOBAL_POSITION]['lat'],
            "longitude": self._vehicle_state[SensorNames.GLOBAL_POSITION]['lon'],
            "altitude": -self._vehicle_state[SensorNames.DEPTH][0] if self._vehicle_state[SensorNames.DEPTH][0] is not None else 0,
            "type": "GeoPoint"
        }
        msg = String()
        msg.data = json.dumps(position_msg)
        self._wara_ps_position_pub.publish(msg)
        self._node.get_logger().info('Published Position message')


        #TODO: this stuff is strings, but wara-ps expects floats. Our json bridge only handles strings. Github Issue exists for this.

        # 3. publish course data
        course_msg = String()
        course_msg.data = f"{self._vehicle_state[SensorNames.GLOBAL_HEADING_DEG][0]}" if self._vehicle_state[SensorNames.GLOBAL_HEADING_DEG][0] is not None else "0.0"
        # float
        # print(course_msg.data)
        self._wara_ps_course_pub.publish(course_msg)
        self._node.get_logger().info('Published Course message')
        
        # 4. publish speed data
        speed_msg = String()
        # speed_msg.data = f"{self._vehicle_state[SensorNames.SPEED][0]}"
        speed_msg.data = "0.0" # TODO: this is FAKE!
        # float
        self._wara_ps_speed_pub.publish(speed_msg)
        self._node.get_logger().info('Published Speed message')

        # computation to get roll and pitch from orientation quaternion

        # 5. publish roll data
        roll_msg = String()
        roll_msg.data = f"{self._vehicle_state[SensorNames.ORIENTATION_EULER]['roll']}"
        # float
        self._wara_ps_roll_pub.publish(roll_msg)
        self._node.get_logger().info('Published Roll message')

        # 6. publish pitch data
        pitch_msg = String()
        pitch_msg.data = f"{self._vehicle_state[SensorNames.ORIENTATION_EULER]['pitch']}"
        # float
        self._wara_ps_pitch_pub.publish(pitch_msg)
        self._node.get_logger().info('Published Pitch message')

        # 7. publish depth data
        depth_msg = String()
        depth_msg.data = f"{self._vehicle_state[SensorNames.DEPTH][0]}"
        # float
        self._wara_ps_depth_pub.publish(depth_msg)
        self._node.get_logger().info('Published Depth message')            

        return True
    

    if __name__ == "__main__":
        from rclpy.node import Node
        # can write a script to test this functionality, but later. 