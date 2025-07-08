#!/usr/bin/python3

from rclpy.node import Node
import tf2_ros
from tf_transformations import euler_from_quaternion

from std_msgs.msg import Float32, Int8
from geographic_msgs.msg import GeoPoint

from std_msgs.msg import Empty, Bool
from std_msgs.msg import String
from sensor_msgs.msg import NavSatFix, BatteryState
from smarc_msgs.msg import Topics
from nav_msgs.msg import Odometry
from typing import Type

from .vehicle import IVehicleState, IVehicleStateContainer
from .sensor import Sensor, SensorNames


class GenericSMaRCVehicle(IVehicleStateContainer):
    def __init__(self,
                 node: Node,
                 vehicle_state_type: Type[IVehicleState]):
        """
        A simpler version of a ROS-connected vehicle-type agnostic vehicle state that fills in its sensor data from ros.
        vehicle_state_type is a class that is/extends VehicleState
        """
        self._node = node

        # self explanatory...
        self._robot_name = node.declare_parameter("robot_name", "sam0").value

        self._vehicle_state = vehicle_state_type(self._robot_name, "odom") # hardcoded reference frame #TODO: this is a hack, should be fixed in the future


        self._gps_sub = node.create_subscription(GeoPoint, Topics.POS_LATLON_TOPIC, self._gps_cb, 10)
        self._heading_sub = node.create_subscription(Float32, Topics.HEADING_TOPIC, self._heading_cb, 10)
        self._course_sub = node.create_subscription(Float32, Topics.COURSE_TOPIC, self._course_cb, 10)
        self._battery_sub = node.create_subscription(Float32, Topics.BATTERY_PERCENT_TOPIC, self._battery_cb, 10)
        self._speed_sub = node.create_subscription(Float32, Topics.SPEED_TOPIC, self._speed_cb, 10)
        self._depth_sub = node.create_subscription(Float32, Topics.DEPTH_TOPIC, self._depth_cb, 10)

        self._odom_sub = node.create_subscription(Odometry, Topics.ODOM_TOPIC, self._odom_cb, 10)
        
        self._abort_pub = node.create_publisher(Empty, Topics.ABORT_TOPIC, 10)
        self._abort_sub = node.create_subscription(Empty, Topics.ABORT_TOPIC, self._abort_cb, 10)

        self._heartbeat_pub = node.create_publisher(Empty, Topics.BT_HEARTBEAT_TOPIC, 10)
        self._vehicle_healthy_sub = node.create_subscription(Int8, Topics.VEHICLE_HEALTH_TOPIC, self._vehicle_healthy_cb, 10)

    def current_time(self) -> float:
        sec, _ = self._node.get_clock().now().seconds_nanoseconds()
        return sec

    def abort(self):
        self._abort_pub.publish(Empty())
        self._vehicle_state.abort()
        self._log(f"Vehicle {self._robot_name} aborted.")
        return True

    def heartbeat(self):
        self._heartbeat_pub.publish(Empty())
        return True

    def _abort_cb(self, data: Empty):
        self._vehicle_state.abort()

    def _vehicle_healthy_cb(self, data: Bool):
        sec = self.current_time()
        self._vehicle_state.update_sensor(SensorNames.VEHICLE_HEALTHY, [data.data], sec)

    def _gps_cb(self, data: GeoPoint):
        sec = self.current_time()
        self._vehicle_state.update_sensor(SensorNames.GLOBAL_POSITION, [data.latitude, data.longitude], sec)
        self._vehicle_state.update_sensor(SensorNames.ALTITUDE, [data.altitude], sec)

    def _depth_cb(self, data: Float32):
        sec = self.current_time()
        self._vehicle_state.update_sensor(SensorNames.DEPTH, [data.data], sec)

    def _heading_cb(self, data: Float32):
        sec = self.current_time()
        self._vehicle_state.update_sensor(SensorNames.GLOBAL_HEADING_DEG, [data.data], sec)

    def _course_cb(self, data: Float32):
        sec = self.current_time()
        self._vehicle_state.update_sensor(SensorNames.COURSE_DEG, [data.data], sec)

    def _speed_cb(self, data: Float32):
        sec = self.current_time()
        self._vehicle_state.update_sensor(SensorNames.SPEED, [data.data], sec)

    def _battery_cb(self, data: BatteryState):
        sec = self.current_time()
        self._vehicle_state.update_sensor(SensorNames.BATTERY, [data.data], sec)

    def _odom_cb(self, data: Odometry):

        # read rpy from odometry message
        orientation = data.pose.pose.orientation
        rpy = euler_from_quaternion([orientation.x, orientation.y, orientation.z, orientation.w])
        sec = self.current_time()
        # self._vehicle_state.update_sensor(SensorNames.POSITION, [data.pose.pose.position.x, data.pose.pose.position.y, data.pose.pose.position.z], sec)
        self._vehicle_state.update_sensor(SensorNames.ORIENTATION_EULER, [rpy[0], rpy[1], rpy[2]], sec)

        
    def _log(self, s:str):
        self._node.get_logger().info(s)


    @property
    def vehicle_state(self) -> Type[IVehicleState]:
        return self._vehicle_state

    def __str__(self) -> str:
        return self._vehicle_state.__str__()
    
    def __getitem__(self, key:str) -> Sensor:
        return self._vehicle_state[key]
