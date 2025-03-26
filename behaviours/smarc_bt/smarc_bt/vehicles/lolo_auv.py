#!/usr/bin/python3

import json
from std_msgs.msg import String
from rclpy.node import Node

from smarc_msgs.msg import DVL, ThrusterFeedback
from lolo_msgs.msg import Topics as LoloTopics
from lolo_msgs.msg import Links as LoloLinks
from smarc_msgs.msg import Leak, PercentStamped
from smarc_msgs.msg import Topics as SMaRCTopics
from sensor_msgs.msg import FluidPressure

from .ros_vehicle import ROSVehicle
from .vehicle import UnderwaterVehicleState, SensorNames


class LoloAuv(ROSVehicle):
    def __init__(self, node: Node):
        super().__init__(node, UnderwaterVehicleState, LoloLinks)
        # The super-class handles everything except the sam-specific subscriptions :D

        # Modify heartbeat
        self._heartbeat_pub = node.create_publisher(String, SMaRCTopics.HEARTBEAT_TOPIC, 10)
        # self._heartbeat_pub = node.create_publisher(String, "lolo_auv/heartbeat", 10) # for testing

        # Set up a timer to publish the heartbeat periodically
        self._heartbeat_timer = node.create_timer(1.0, self.heartbeat)  # Publish every 1 second

        # Lolo-specific subscriptions
        self._leak_sub = node.create_subscription(Leak, LoloTopics.LEAK_TOPIC, self._leak_cb, 10)

        self._t1 = None
        self._t2 = None
        self._t3 = None
        self._t4 = None

    def heartbeat(self):
        heartbeat_data = {
            "agent-type": "subsurface",
            "agent-uuid": "123",
            "levels": [],
            "name": "fakest_lol0_you_ve_ever_seen",
            "rate": 1.0,
            "stamp": self._node.get_clock().now().to_msg().sec + self._node.get_clock().now().to_msg().nanosec * 1e-9,
            "type": "HeartBeat"
        }
        msg = String()
        msg.data = json.dumps(heartbeat_data)
        self._heartbeat_pub.publish(msg)
        self._node.get_logger().info('Published mock Heartbeat message')

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
    
    def _t3_cb(self, data:ThrusterFeedback):
        self._t3 = data.rpm.rpm
        self._vehicle_state.update_sensor(SensorNames.THRUSTERS, [self._t1, self._t2, self._t3], data.header.stamp.sec)

    def _t4_cb(self, data:ThrusterFeedback):
        self._t4 = data.rpm.rpm
        self._vehicle_state.update_sensor(SensorNames.THRUSTERS, [self._t1, self._t2, self._t3, self._t4], data.header.stamp.sec)



def test_lolo_auv():
    import rclpy, sys
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("test_lolo_auv")
    v = LoloAuv(node)

    def update():
        nonlocal v
        print(v)

    node.create_timer(0.5, update)
    rclpy.spin(node)


if __name__ == "__main__":
    test_lolo_auv()
    # test_ros_vehicle()
