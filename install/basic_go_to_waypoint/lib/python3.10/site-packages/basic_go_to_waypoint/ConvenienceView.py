#!/usr/bin/python3
import sys
import rclpy
from rclpy.node import Node

from smarc_msgs.msg import ThrusterRPM
from sam_msgs.msg import Topics as SamTopics
from sam_msgs.msg import ThrusterAngles

from geometry_msgs.msg import PoseStamped, TransformStamped

try:
    from .IThrustView import IThrustView
except:
    from IThrustView import IThrustView

class ConvenienceView(IThrustView):
    """
    Implements convenience topic publishers for debugging
    """
    def __init__(self, node: Node, controller) -> None:
        # Just a bunch of publishers to send the given RPM to the vehicle.
        # We get the topic strings from the Topics message object so there are no hard-coded strings here!
        self._waypoint_pub = node.create_publisher(PoseStamped, "/conv/waypoint", 10)
        self._waypoint_msg = None

        self._controller = controller

    def update(self) -> None:
        self._waypoint_msg = self._controller.get_waypoint()

        if self._waypoint_msg is None:
            return

        self._waypoint_pub.publish(self._waypoint_msg)


def test_view():
    """
    How will we know this is working as intended? By running it!
    Check setup.py to see how this function can be run with ros2
    Use `ros2 run workshopfun test_view` to run this.
    """
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("SAMThrustView_test")
    view = ConvenienceView(node)

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
