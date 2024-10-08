#!/usr/bin/python3
import sys
import rclpy
from rclpy.node import Node

from smarc_msgs.msg import ThrusterRPM
from sam_msgs.msg import Topics as SamTopics
from sam_msgs.msg import ThrusterAngles

try:
    from .IThrustView import IThrustView
except:
    from IThrustView import IThrustView

class SAMThrustView(IThrustView):
    """
    Implements the simple interface we defined in IThrustView for the SAM AUV.
    """
    def __init__(self, node: Node) -> None:
        # Just a bunch of publishers to send the given RPM to the vehicle.
        # We get the topic strings from the Topics message object so there are no hard-coded strings here!
        self._rpm1_pub = node.create_publisher(ThrusterRPM, SamTopics.THRUSTER1_CMD_TOPIC, 10)
        self._rpm2_pub = node.create_publisher(ThrusterRPM, SamTopics.THRUSTER2_CMD_TOPIC, 10)
        self._thrust_vector_pub = node.create_publisher(ThrusterAngles, SamTopics.THRUST_VECTOR_CMD_TOPIC, 10)
        self._t1_msg = ThrusterRPM()
        self._t2_msg = ThrusterRPM()
        self._thrust_vector_msg = ThrusterAngles()

    def set_rpm(self, rpm: int) -> None:
         """
         This is the only thing that we have promised with the interface before
         """
         # great place to ensure types in messages!
         self._t1_msg.rpm = int(rpm)
         self._t2_msg.rpm = int(rpm)

    def set_thrust_vector(self, horizontal_tv: float, vertical_tv: float) -> None:
        """
        Set thrust vector
        """
        self._thrust_vector_msg.thruster_horizontal_radians = float(horizontal_tv)
        self._thrust_vector_msg.thruster_vertical_radians = float(vertical_tv)


    def update(self) -> None:
        self._rpm1_pub.publish(self._t1_msg)
        self._rpm2_pub.publish(self._t2_msg)
        self._thrust_vector_pub.publish(self._thrust_vector_msg)


def test_view():
    """
    How will we know this is working as intended? By running it!
    Check setup.py to see how this function can be run with ros2
    Use `ros2 run workshopfun test_view` to run this.
    """
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("SAMThrustView_test")
    view = SAMThrustView(node)

    print("start test view")

    rpm = 500
    hor_tv = 0.1
    ver_tv = -0.1

    # a simple "controller" to give the View _something_ to do.
    def loop():
        nonlocal rpm
        nonlocal hor_tv
        nonlocal ver_tv
        rpm *= -1
        hor_tv *= -1
        ver_tv *= -1
        view.set_rpm(rpm)
        view.set_thrust_vector(hor_tv, ver_tv)
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
