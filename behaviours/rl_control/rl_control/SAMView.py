#!/usr/bin/python3

from nav_msgs.msg import Odometry
from rclpy.node import Node
from sam_msgs.msg import ThrusterAngles
from sam_msgs.msg import Topics as SamTopics
from smarc_control_msgs.msg import Topics as ControlTopics
from smarc_msgs.msg import ThrusterRPM, PercentStamped

try:
    from .ISAMView import ISAMView
except:
    from ISAMView import ISAMView

class SAMView(ISAMView):
    """
    Implements the simple interface we defined in IDiveView for the SAM AUV.
    """
    def __init__(self, node: Node) -> None:
        self._vbs_pub = node.create_publisher(PercentStamped, SamTopics.VBS_CMD_TOPIC, 10)
        self._lcg_pub = node.create_publisher(PercentStamped, SamTopics.LCG_CMD_TOPIC, 10)
        self._rpm1_pub = node.create_publisher(ThrusterRPM, SamTopics.THRUSTER1_CMD_TOPIC, 10)
        self._rpm2_pub = node.create_publisher(ThrusterRPM, SamTopics.THRUSTER2_CMD_TOPIC, 10)
        self._thrust_vector_pub = node.create_publisher(ThrusterAngles, SamTopics.THRUST_VECTOR_CMD_TOPIC, 10)

        self.state_sub = node.create_subscription(msg_type=Odometry, topic=ControlTopics.STATES, callback=self._states_cb, qos_profile=10)

        # Messages
        self._vbs_msg = PercentStamped()
        self._vbs_msg.value = 50.0
        self._lcg_msg = PercentStamped()
        self._lcg_msg.value = 50.0
        self._t1_msg = ThrusterRPM()
        self._t2_msg = ThrusterRPM()
        self._thrust_vector_msg = ThrusterAngles()
        self._states = Odometry()

    def _states_cb(self, msg):
       self._states = msg

    def get_state(self):
        return self._states

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
