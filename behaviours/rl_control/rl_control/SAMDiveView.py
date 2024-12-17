#!/usr/bin/python3
import sys

import rclpy
from rclpy.node import Node
from sam_msgs.msg import ThrusterAngles
from sam_msgs.msg import Topics as SamTopics
from smarc_msgs.msg import ThrusterRPM, PercentStamped

try:
    from .IDiveView import IDiveView
except:
    from IDiveView import IDiveView

class SAMDiveView(IDiveView):
    """
    Implements the simple interface we defined in IDiveView for the SAM AUV.
    """
    def __init__(self, node: Node) -> None:
        # Publishers
        self._vbs_pub = node.create_publisher(PercentStamped, SamTopics.VBS_CMD_TOPIC, 10)
        self._lcg_pub = node.create_publisher(PercentStamped, SamTopics.LCG_CMD_TOPIC, 10)
        self._rpm1_pub = node.create_publisher(ThrusterRPM, SamTopics.THRUSTER1_CMD_TOPIC, 10)
        self._rpm2_pub = node.create_publisher(ThrusterRPM, SamTopics.THRUSTER2_CMD_TOPIC, 10)
        self._thrust_vector_pub = node.create_publisher(ThrusterAngles, SamTopics.THRUST_VECTOR_CMD_TOPIC, 10)

        # Messages
        self._vbs_msg = PercentStamped()
        self._lcg_msg = PercentStamped()
        self._t1_msg = ThrusterRPM()
        self._t2_msg = ThrusterRPM()
        self._thrust_vector_msg = ThrusterAngles()


    def set_vbs(self, vbs: float) -> None:
        """
        Set vbs
        """
        self._vbs_msg.value = float(vbs)


    def set_lcg(self, lcg: float) -> None:
        """
        Set LCG
        """
        self._lcg_msg.value = float(lcg)


    def set_rpm(self, rpm: int) -> None:
        """
        Set RPMs
        """
        self._t1_msg.rpm = int(rpm)
        self._t2_msg.rpm = int(rpm)

    def set_thrust_vector(self, horizontal_tv: float, vertical_tv: float) -> None:
        """
        Set thrust vector
        """
        self._thrust_vector_msg.thruster_horizontal_radians = float(horizontal_tv)
        self._thrust_vector_msg.thruster_vertical_radians = float(vertical_tv)


    def update(self) -> None:
        """
        Publish all actuator values
        """
        self._vbs_pub.publish(self._vbs_msg)
        self._lcg_pub.publish(self._lcg_msg)
        self._rpm1_pub.publish(self._t1_msg)
        self._rpm2_pub.publish(self._t2_msg)
        self._thrust_vector_pub.publish(self._thrust_vector_msg)
