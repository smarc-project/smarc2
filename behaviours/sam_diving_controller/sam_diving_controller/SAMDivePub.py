#!/usr/bin/python3
import sys
import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32, Float64, Bool
from smarc_msgs.msg import ThrusterRPM, PercentStamped
from smarc_control_msgs.msg import Topics as ControlTopics
from sam_msgs.msg import Topics as SamTopics
from sam_msgs.msg import ThrusterAngles, ThrusterRPMs

from sam_diving_controller.IDivePub import ActuatorStates

from .ParamUtils import DivingModelParam

try:
    from .IDivePub import IDivePub, MissionStates
except:
    from IDivePub import IDivePub, MissionStates

class SAMDivePub(IDivePub):
    """
    Implements the simple interface we defined in IDiveView for the SAM AUV.
    """
    def __init__(self, node: Node, dive_sub, param) -> None:

        self._node = node
        self._dive_sub = dive_sub
        self.param = param

        self._actuator_state = None

        # Publishers
        self._vbs_pub = node.create_publisher(PercentStamped, SamTopics.VBS_CMD_TOPIC, 10)
        self._lcg_pub = node.create_publisher(PercentStamped, SamTopics.LCG_CMD_TOPIC, 10)
        self._rpm1_pub = node.create_publisher(ThrusterRPM, SamTopics.THRUSTER1_CMD_TOPIC, 10)
        self._rpm2_pub = node.create_publisher(ThrusterRPM, SamTopics.THRUSTER2_CMD_TOPIC, 10)
        self.thrust_rpms_pub = node.create_publisher(ThrusterRPMs, "core/thruster_rpms_cmd", qos_profile=10)
        self._thrust_vector_pub = node.create_publisher(ThrusterAngles, SamTopics.THRUST_VECTOR_CMD_TOPIC, 10)
        self._joy_thrust_vector_pub = node.create_publisher(Float64, ControlTopics.ELEVATOR_PID_CTRL, 10)
        self._joy_assisted_driving_pub = node.create_publisher(Bool, ControlTopics.ASSIST_ENABLE, qos_profile=10)

        # Messages
        self._vbs_msg = PercentStamped()
        self._lcg_msg = PercentStamped()
        self._t1_msg = ThrusterRPM()
        self._t2_msg = ThrusterRPM()
        self.rpm_msg = ThrusterRPMs()
        self._thrust_vector_msg = ThrusterAngles()
        self._joy_tv_msg = Float64()

        self._vbs_msg.value = self.param['vbs_u_neutral']
        self._lcg_msg.value = self.param['lcg_u_neutral']
        self._thrust_vector_msg.thruster_horizontal_radians = self.param['tv_u_neutral']
        self._thrust_vector_msg.thruster_vertical_radians = self.param['tv_u_neutral']
        self._t1_msg.rpm = self.param['rpm_u_neutral']
        self._t2_msg.rpm = self.param['rpm_u_neutral']

    def _loginfo(self, s):
        self._node.get_logger().info(s)


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


    def set_rpm(self, rpm1: float, rpm2: float) -> None:
        """
        Set RPMs
        """
        self._t1_msg.rpm = int(rpm1)
        self._t2_msg.rpm = int(rpm2)
        self.rpm_msg.thruster_1_rpm = int(rpm1)
        self.rpm_msg.thruster_2_rpm = int(rpm2)

    def set_thrust_vector(self, horizontal_tv: float, vertical_tv: float) -> None:
        """
        Set thrust vector
        """
        self._thrust_vector_msg.thruster_horizontal_radians = float(horizontal_tv)
        self._thrust_vector_msg.thruster_vertical_radians = float(vertical_tv)


    def set_stern(self, u_tv_ver):
        self._joy_tv_msg.data = float(u_tv_ver)


    def set_actuator_states(self, actuator_state, node_name):

        old_state = self._actuator_state
        self._actuator_state = actuator_state

        if self._actuator_state != old_state:
            self._loginfo(f"DiveController state: from {node_name}: {old_state} --> {self._actuator_state}")

    def get_actuator_states(self):
        return self._actuator_state


    def update(self) -> None:
        """
        Publish all actuator values
        """

        if self._actuator_state == ActuatorStates.DISENGAGED:
            #self._loginfo(f"Actuators disengaged")
            return
        
        if self._actuator_state == ActuatorStates.NEUTRAL:
            self._vbs_pub.publish(self._vbs_msg)
            self._lcg_pub.publish(self._lcg_msg)
            self._rpm1_pub.publish(self._t1_msg)
            self._rpm2_pub.publish(self._t2_msg)
            self._thrust_vector_pub.publish(self._thrust_vector_msg)

            self.set_actuator_states(ActuatorStates.DISENGAGED, "DP")

        else:
            self._vbs_pub.publish(self._vbs_msg)
            self._lcg_pub.publish(self._lcg_msg)
            self._rpm1_pub.publish(self._t1_msg)
            self._rpm2_pub.publish(self._t2_msg)
            self._thrust_vector_pub.publish(self._thrust_vector_msg)

    def joy_update(self):
        """
        Publish all actuator values
        """
        self._joy_assisted_driving_msg = Bool()
        self._joy_assisted_driving_msg.data = True
        self._vbs_pub.publish(self._vbs_msg)
        self._lcg_pub.publish(self._lcg_msg)
        self._joy_thrust_vector_pub.publish(self._joy_tv_msg)
        self._joy_assisted_driving_pub.publish(self._joy_assisted_driving_msg)

