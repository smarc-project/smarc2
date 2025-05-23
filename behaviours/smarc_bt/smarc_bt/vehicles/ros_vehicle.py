#!/usr/bin/python3

from rclpy.node import Node
import tf2_ros
from tf_transformations import euler_from_quaternion

from std_msgs.msg import Empty, Bool
from sensor_msgs.msg import NavSatFix, BatteryState
from smarc_msgs.msg import Topics, FloatStamped

from typing import Type

from .vehicle import IVehicleState, IVehicleStateContainer
from .sensor import Sensor, SensorNames


class ROSVehicle(IVehicleStateContainer):
    def __init__(self,
                 node: Node,
                 vehicle_state_type: Type[IVehicleState],
                 links_message):
        """
        A ROS-connected vehicle-type agnostic vehicle state that fills in its sensor data from ros.
        vehicle_state_type is a class that is/extends VehicleState
        links_message is a ros message that contains BASE_LINK as a field
        """
        self._node = node

        # self explanatory...
        self._link_suffix = node.declare_parameter("link_suffix", "").value
        self._robot_name = node.declare_parameter("robot_name", "sam0").value
        self._link_separator = node.declare_parameter("tf_link_separator_char", "/").value
        tf_update_period = node.declare_parameter("tf_update_period", 0.1).value

        default_reference_frame = f"{self._robot_name}{self._link_separator}{links_message.ODOM_LINK}{self._link_suffix}"
        reference_frame = node.declare_parameter("reference_frame", default_reference_frame).value

    
        self._vehicle_state = vehicle_state_type(self._robot_name, reference_frame)

        # over-ride this in specific vehicles as needed.
        # but we shall have it here too as a sane default
        default_base_link = f"{self._robot_name}{self._link_separator}{links_message.BASE_LINK}{self._link_suffix}"
        self._robot_base_link = node.declare_parameter("base_link", default_base_link).value

        self._log(f"Using base_link:{self._robot_base_link} under reference frame:{reference_frame}")

        self._tf_buffer = tf2_ros.buffer.Buffer()
        self._tf_listener = tf2_ros.transform_listener.TransformListener(self._tf_buffer, node)

        self._gps_sub = node.create_subscription(NavSatFix, Topics.GPS_TOPIC, self._gps_cb, 10)
        self._heading_sub = node.create_subscription(FloatStamped, Topics.HEADING_TOPIC, self._heading_cb, 10)
        self._battery_sub = node.create_subscription(BatteryState, Topics.BATTERY_TOPIC, self._battery_cb, 10)
        self._tf_update_timer = node.create_timer(tf_update_period, self.update_tf)

        self._abort_pub = node.create_publisher(Empty, Topics.ABORT_TOPIC, 10)
        self._abort_sub = node.create_subscription(Empty, Topics.ABORT_TOPIC, self._abort_cb, 10)
        self._heartbeat_pub = node.create_publisher(Empty, Topics.HEARTBEAT_TOPIC, 10)
        self._vehicle_healthy_sub = node.create_subscription(Bool, Topics.VEHICLE_READY_TOPIC, self._vehicle_healthy_cb, 10)


    def update_tf(self):
        try:
            latest = self._tf_buffer.get_latest_common_time(self._robot_base_link, self._vehicle_state._reference_frame)
            tf_stamped = self._tf_buffer.lookup_transform(self._robot_base_link,
                                                          self._vehicle_state._reference_frame,
                                                          latest)

        except Exception as ex:
            self._log(f"Vehicle state could not update position, exception:\n{ex}")
            return
    
        seconds = tf_stamped.header.stamp.sec
        translation = tf_stamped.transform.translation
        self._vehicle_state.update_sensor(SensorNames.POSITION, [translation.x, translation.y, translation.z], seconds)
        quat = tf_stamped.transform.rotation
        rpy = euler_from_quaternion([quat.x, quat.y, quat.z, quat.w])
        self._vehicle_state.update_sensor(SensorNames.ORIENTATION_EULER, rpy, seconds)


    def abort(self):
        self._abort_pub.publish(Empty())
        return True

    def heartbeat(self):
        self._heartbeat_pub.publish(Empty())
        return True

    def _abort_cb(self, data: Empty):
        self._vehicle_state.abort()

    def _vehicle_healthy_cb(self, data: Bool):
        sec, _ = self._node.get_clock().now().seconds_nanoseconds()
        self._vehicle_state.update_sensor(SensorNames.VEHICLE_HEALTHY, [data.data], sec)

    def _gps_cb(self, data: NavSatFix):
        self._vehicle_state.update_sensor(SensorNames.GLOBAL_POSITION, [data.latitude, data.longitude], data.header.stamp.sec)

    def _heading_cb(self, data: FloatStamped):
        self._vehicle_state.update_sensor(SensorNames.GLOBAL_HEADING_DEG, [data.data], data.header.stamp.sec)

    def _battery_cb(self, data: BatteryState):
        self._vehicle_state.update_sensor(SensorNames.BATTERY, [data.voltage, data.percentage], data.header.stamp.sec)
        
    def _log(self, s:str):
        self._node.get_logger().info(s)


    @property
    def vehicle_state(self) -> Type[IVehicleState]:
        return self._vehicle_state

    def __str__(self) -> str:
        return self._vehicle_state.__str__()
    
    def __getitem__(self, key:str) -> Sensor:
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

