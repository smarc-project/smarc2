#!/usr/bin/python3

import rclpy.time as time
from rclpy.node import Node
import tf2_ros
from tf_transformations import euler_from_quaternion

from sensor_msgs.msg import NavSatFix, BatteryState
from smarc_msgs.msg import Topics, FloatStamped

try:
    from vehicle import IVehicleState
except:
    from .vehicle import IVehicleState
    
from typing import Type


class ROSVehicle():
    def __init__(self,
                 node: Node,
                 vehicle_state_type: Type[IVehicleState]):
        """
        A ROS-connected vehicle-type agnostic vehicle state that fills in its sensor data from ros.
        vehicle_state_type is a class that is/extends VehicleState
        """
        self._node = node

        # self explanatory...
        name = node.declare_parameter("robot_name", "sam0").value
        reference_frame = node.declare_parameter("reference_frame", "odom").value
        tf_update_period = node.declare_parameter("tf_update_period", 0.1).value
        
        self._vehicle_state = vehicle_state_type(name, reference_frame)

        self._robot_base_link = name + "_base_link"

        self._tf_buffer = tf2_ros.buffer.Buffer()
        self._tf_listener = tf2_ros.transform_listener.TransformListener(self._tf_buffer, node)

        self._gps_sub = node.create_subscription(NavSatFix, Topics.GPS_TOPIC, self._gps_cb, 10)
        self._heading_sub = node.create_subscription(FloatStamped, Topics.HEADING_TOPIC, self._heading_cb, 10)
        self._battery_sub = node.create_subscription(BatteryState, Topics.BATTERY_TOPIC, self._battery_cb, 10)
        self._tf_update_timer = node.create_timer(tf_update_period, self.update_tf)

        

    def update_tf(self):
        try:
            tf_stamped = self._tf_buffer.lookup_transform(self._robot_base_link,
                                                          self._vehicle_state._reference_frame,
                                                          time.Time())
        except Exception as ex:
            self._log_info(f"Vehicle state could not update position, exception:\n{ex}")
            return
    
        seconds = tf_stamped.header.stamp.sec
        translation = tf_stamped.transform.translation
        self._vehicle_state.update_sensor("position", [translation.x, translation.y, translation.z], seconds)
        quat = tf_stamped.transform.rotation
        rpy = euler_from_quaternion([quat.x, quat.y, quat.z, quat.w])
        self._vehicle_state.update_sensor("orientation_euler", rpy, seconds)

    def _gps_cb(self, data: NavSatFix):
        self._vehicle_state.update_sensor("global_position", [data.latitude, data.longitude], data.header.stamp.sec)

    def _heading_cb(self, data: FloatStamped):
        self._vehicle_state.update_sensor("global_heading_deg", [data.data], data.header.stamp.sec)

    def _battery_cb(self, data: BatteryState):
        self._vehicle_state.update_sensor("battery", [data.voltage, data.percentage], data.header.stamp.sec)
        

    def _log_info(self, s:str):
        self._node.get_logger().info(s)


    def __str__(self):
        return self._vehicle_state.__str__()
    
    def __getitem__(self, key:str):
        return self._vehicle_state[key]



def test_ros_vehicle():
    import sys, rclpy
    try:
        from vehicle import VehicleState
    except:
        from .vehicle import VehicleState

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("test_ros_vehicle")
    v = ROSVehicle(node, VehicleState)

    def update():
        nonlocal v
        print(v)

    node.create_timer(0.5, update)
    rclpy.spin(node)

