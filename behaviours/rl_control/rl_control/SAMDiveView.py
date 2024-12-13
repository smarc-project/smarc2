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


def test_view():
    """
    How will we know this is working as intended? By running it!
    Check setup.py to see how this function can be run with ros2
    Use `ros2 run basic_depth_pitch_control test_view` to run this.
    """
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("SAMDiveView_test")
    view = SAMDiveView(node)

    print("start test view")

    lcg = 0.0
    vbs = 0.0
    rpm = 500
    hor_tv = 0.1
    ver_tv = -0.1

    i = 0

    # a simple "controller" to give the View _something_ to do.
    def loop():
        nonlocal lcg
        nonlocal vbs
        nonlocal rpm
        nonlocal hor_tv
        nonlocal ver_tv
        nonlocal i

        rpm *= -1
        hor_tv *= -1
        ver_tv *= -1
        i += 1.0
        vbs += i
        lcg += i

        view.set_rpm(rpm)
        view.set_thrust_vector(hor_tv, ver_tv)
        view.set_lcg(lcg)
        view.set_vbs(vbs)

        view.update()

    loop_period = 1
    node.create_timer(loop_period, loop)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


# Could also run this without ros2
if __name__ == "__main__":
    test_view()
