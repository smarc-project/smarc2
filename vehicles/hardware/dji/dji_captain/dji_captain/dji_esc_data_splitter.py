#!/usr/bin/python3

import rclpy, sys
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.qos import QoSProfile, ReliabilityPolicy, QoSDurabilityPolicy

from std_msgs.msg import Int16
from psdk_interfaces.msg import EscData, EscStatusIndividual
from dji_msgs.msg import Topics as DjiTopics
from dji_msgs.msg import PsdkTopics as PSDKTopics


class ESCDataSplitter():
    def __init__(self, node: Node):
        self._node = node

        self._node.declare_parameter("robot_name", "M350")
        self.ROBOT_NAME : str = self._node.get_parameter("robot_name").get_parameter_value().string_value       

        qos_best_effort10 = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT, durability=QoSDurabilityPolicy.VOLATILE) 
        
        node.create_subscription(
            EscData,
            PSDKTopics.ESC_DATA,
            self._esc_cb,
            qos_profile=qos_best_effort10)
        
        self._rpm_fr_pub = node.create_publisher(Int16, DjiTopics.PROP_RPM_FR, qos_profile=qos_best_effort10)
        self._rpm_fl_pub = node.create_publisher(Int16, DjiTopics.PROP_RPM_FL, qos_profile=qos_best_effort10)
        self._rpm_br_pub = node.create_publisher(Int16, DjiTopics.PROP_RPM_BL, qos_profile=qos_best_effort10)
        self._rpm_bl_pub = node.create_publisher(Int16, DjiTopics.PROP_RPM_BR, qos_profile=qos_best_effort10)

        if self.ROBOT_NAME == "FC30":
            self._rpm_frb_pub = node.create_publisher(Int16, DjiTopics.PROP_RPM_FR_BOTTOM, qos_profile=qos_best_effort10)
            self._rpm_flb_pub = node.create_publisher(Int16, DjiTopics.PROP_RPM_FL_BOTTOM, qos_profile=qos_best_effort10)
            self._rpm_brb_pub = node.create_publisher(Int16, DjiTopics.PROP_RPM_BL_BOTTOM, qos_profile=qos_best_effort10)
            self._rpm_blb_pub = node.create_publisher(Int16, DjiTopics.PROP_RPM_BR_BOTTOM, qos_profile=qos_best_effort10)

        
    def _esc_cb(self, msg: EscData):
        escs : list[EscStatusIndividual] = msg.esc # type: ignore
        self._rpm_fr_pub.publish(Int16(data=escs[0].speed))
        self._rpm_fl_pub.publish(Int16(data=escs[1].speed))
        self._rpm_br_pub.publish(Int16(data=escs[2].speed))
        self._rpm_bl_pub.publish(Int16(data=escs[3].speed))

        if self.ROBOT_NAME == "FC30":
            self._rpm_frb_pub.publish(Int16(data=escs[4].speed))
            self._rpm_flb_pub.publish(Int16(data=escs[5].speed))
            self._rpm_brb_pub.publish(Int16(data=escs[6].speed))
            self._rpm_blb_pub.publish(Int16(data=escs[7].speed))

def main():
    rclpy.init(args=sys.argv)
    node = Node("ESCDataSplitter")
    ESCDataSplitter(node)

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()
