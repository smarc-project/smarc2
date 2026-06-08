#!/usr/bin/python3

import rclpy, sys, math, time
import numpy as np
from enum import Enum

from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.time import Time, Duration
from rclpy.timer import Timer
from rclpy.qos import QoSProfile, ReliabilityPolicy, QoSDurabilityPolicy
from rclpy.callback_groups import ReentrantCallbackGroup

from tf2_ros import Buffer, TransformListener
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster
from tf2_ros.transform_broadcaster import TransformBroadcaster

from std_msgs.msg import Float32, Int8, String, Bool
from std_srvs.srv import Trigger
from sensor_msgs.msg import NavSatFix, Joy, BatteryState, JoyFeedback
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TwistStamped, Pose, PoseStamped, TransformStamped, QuaternionStamped, PointStamped, Vector3Stamped, Quaternion
from geographic_msgs.msg import GeoPoint
from tf2_msgs.msg import TFMessage

from psdk_interfaces.msg import PositionFused, ControlMode, EscData, SingleBatteryInfo, EscStatusIndividual
from smarc_msgs.msg import Topics as SmarcTopics
from smarc_msgs.msg import GeofenceStatusStamped
from dji_msgs.msg import Links as DjiLinks
from dji_msgs.msg import Topics as DjiTopics
from dji_msgs.msg import PsdkTopics as PSDKTopics


class PSDKFaker():
    def __init__(self, node: Node):
        self._node = node

        self._node.declare_parameter("robot_name", "M350")
        self.ROBOT_NAME : str = self._node.get_parameter("robot_name").get_parameter_value().string_value

        qos_best_effort10 = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT, durability=QoSDurabilityPolicy.VOLATILE)

        self._gps_publisher = node.create_publisher(
            NavSatFix,
            PSDKTopics.GPS_POSITION,
            qos_profile=qos_best_effort10)
        
        self._position_fused_publisher = node.create_publisher(
            PositionFused,
            PSDKTopics.POSITION_FUSED,
            qos_profile=qos_best_effort10)
        
        self._home_point_publisher = node.create_publisher(
            NavSatFix,
            PSDKTopics.HOME_POINT,
            qos_profile=qos_best_effort10)
        
        self._attitude_publisher = node.create_publisher(
            QuaternionStamped,
            PSDKTopics.ATTITUDE,
            qos_profile=qos_best_effort10)
        
        self._control_mode_publisher = node.create_publisher(
            ControlMode,
            PSDKTopics.CONTROL_MODE,
            qos_profile=qos_best_effort10)
        
        if self.ROBOT_NAME == "M350":
            self._battery_publisher = node.create_publisher(
                BatteryState,
                PSDKTopics.BATTERY,
                qos_profile=qos_best_effort10)
        if self.ROBOT_NAME == "FC30":
            self._single_batt1_publisher = node.create_publisher(
                SingleBatteryInfo,
                PSDKTopics.SINGLE_BATT1,
                qos_profile=qos_best_effort10)

            self._single_batt2_publisher = node.create_publisher(
                SingleBatteryInfo,
                PSDKTopics.SINGLE_BATT2,
                qos_profile=qos_best_effort10)

        self._velocity_ground_publisher = node.create_publisher(
            Vector3Stamped,
            PSDKTopics.VELOCITY_GROUND_FSD,
            qos_profile=qos_best_effort10)
        
        self._angular_rate_ground_publisher = node.create_publisher(
            Vector3Stamped,
            PSDKTopics.ANGULAR_RATE_GND_FSD,
            qos_profile=qos_best_effort10)
        
        self._esc_data_publisher = node.create_publisher(
            EscData,
            PSDKTopics.ESC_DATA,
            qos_profile=qos_best_effort10)
        
        self._joy_publisher = node.create_publisher(
            Joy,
            PSDKTopics.RC,
            qos_profile=qos_best_effort10)

        self._psdk_timer = node.create_timer(0.1, self.pub_psdk)


        node.create_service(
            srv_type=Trigger,
            srv_name=PSDKTopics.TAKE_CONTROL_SRV,
            callback=lambda req, res: Trigger.Response(success=True, message="Fakin it")
        )

        node.create_service(
            srv_type=Trigger,
            srv_name=PSDKTopics.RELEASE_CONTROL_SRV,
            callback=lambda req, res: Trigger.Response(success=True, message="Fakin it")
        )

        node.create_service(
            srv_type=Trigger,
            srv_name=PSDKTopics.TAKEOFF_SRV,
            callback=lambda req, res: Trigger.Response(success=True, message="Fakin it")
        )

        node.create_service(
            srv_type=Trigger,
            srv_name=PSDKTopics.LAND_SRV,
            callback=lambda req, res: Trigger.Response(success=True, message="Fakin it")
        )

        node.create_service(
            srv_type=Trigger,
            srv_name=PSDKTopics.PROPS_ON_SRV,
            callback=lambda req, res: Trigger.Response(success=True, message="Fakin it")
        )

        node.create_service(
            srv_type=Trigger,
            srv_name=PSDKTopics.PROPS_OFF_SRV,
            callback=lambda req, res: Trigger.Response(success=True, message="Fakin it")
        )


    def pub_psdk(self):
        # KTH F building :) 
        # 59.348397,18.0718507

        # Publish fake GPS data
        gps_msg = NavSatFix()
        gps_msg.latitude = 59.348397
        gps_msg.longitude = 18.0718507
        gps_msg.altitude = 10.0
        self._gps_publisher.publish(gps_msg)

        # Publish fake position fused data
        pos_fused_msg = PositionFused()
        pos_fused_msg.position.x = 1.0
        pos_fused_msg.position.y = 2.0
        pos_fused_msg.position.z = 3.0
        self._position_fused_publisher.publish(pos_fused_msg)

        # Publish fake home point data
        home_point_msg = NavSatFix()
        home_point_msg.latitude = math.radians(59.348397)
        home_point_msg.longitude = math.radians(18.0718507)
        home_point_msg.altitude = 10.0
        self._home_point_publisher.publish(home_point_msg)

        # Publish fake attitude data
        attitude_msg = QuaternionStamped()
        attitude_msg.quaternion.x = 0.0
        attitude_msg.quaternion.y = 0.0
        attitude_msg.quaternion.z = 0.0
        attitude_msg.quaternion.w = 1.0
        self._attitude_publisher.publish(attitude_msg)

            

        if self.ROBOT_NAME == "M350":
            # Publish fake battery data
            battery_msg = BatteryState()
            battery_msg.percentage = 0.99
            self._battery_publisher.publish(battery_msg)

            control_mode_msg = ControlMode()
            control_mode_msg.control_auth = 1
            control_mode_msg.device_mode = 4
            self._control_mode_publisher.publish(control_mode_msg)

            esc_data = EscData()
            esc = EscStatusIndividual()
            esc.speed = 1000
            escs = [esc]*4
            esc_data.esc = escs
            self._esc_data_publisher.publish(esc_data)



        if self.ROBOT_NAME == "FC30":
            # Publish fake single battery 1 data
            single_batt1_msg = SingleBatteryInfo()
            single_batt1_msg.capacity_percentage = 0.99
            self._single_batt1_publisher.publish(single_batt1_msg)

            # Publish fake single battery 2 data
            single_batt2_msg = SingleBatteryInfo()
            single_batt2_msg.capacity_percentage = 0.99
            self._single_batt2_publisher.publish(single_batt2_msg)

            control_mode_msg = ControlMode()
            control_mode_msg.control_auth = 0
            control_mode_msg.device_mode = 3
            control_mode_msg.control_mode = 4
            self._control_mode_publisher.publish(control_mode_msg)


            esc_data = EscData()
            esc = EscStatusIndividual()
            esc.speed = 500
            escs = [esc]*8
            esc_data.esc = escs
            self._esc_data_publisher.publish(esc_data)


def main():
    rclpy.init(args=sys.argv)
    node = Node("PSDK_FAKER_NODE")

    faker = PSDKFaker(node)

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()

if __name__ == "__main__":
    main()