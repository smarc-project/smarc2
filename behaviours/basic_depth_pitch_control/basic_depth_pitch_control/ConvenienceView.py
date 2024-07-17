#!/usr/bin/python3
import sys
import rclpy
from rclpy.node import Node

from smarc_msgs.msg import ThrusterRPM
from sam_msgs.msg import Topics as SamTopics
from sam_msgs.msg import ThrusterAngles

from smarc_control_msgs.msg import Topics as ControlTopics
from smarc_control_msgs.msg import ControlError, ControlInput, ControlReference, ControlState

from geometry_msgs.msg import PoseStamped, TransformStamped

try:
    from .IDiveView import IDiveView
except:
    from IIDiveView import IDiveView

class ConvenienceView(IDiveView):
    """
    Implements convenience topic publishers for debugging
    """
    def __init__(self, node: Node, controller, model) -> None:
        self._state_pub = node.create_publisher(ControlState, ControlTopics.STATES_CONV, 10)
        self._ref_pub = node.create_publisher(ControlReference, ControlTopics.REF_CONV, 10)
        self._error_pub = node.create_publisher(ControlError, ControlTopics.CONTROL_ERROR_CONV, 10)
        self._input_pub = node.create_publisher(ControlInput, ControlTopics.CONTROL_INPUT_CONV, 10)


        self._state_msg = None
        self._ref_msg = None
        self._error_msg = None
        self._input_msg = None

        self._controller = controller
        self._model = model


    def _loginfo(self, s):
        self._node.get_logger().info(s)

    def update(self) -> None:
        self._update_state()
        self._update_ref()
        self._update_error()
        self._update_input()


    def _update_state(self) -> None:
        self._state_msg = self._model.get_state()

        if self._state_msg is None:
            return

        self._state_pub.publish(self._state_msg)

    def _update_ref(self) -> None:
        self._ref_msg = self._model.get_ref()

        if self._ref_msg is None:
            return

        self._ref_pub.publish(self._ref_msg)

    def _update_error(self) -> None:
        self._error_msg = self._model.get_error()

        if self._error_msg is None:
            return

        self._error_pub.publish(self._error_msg)

    def _update_input(self) -> None:
        self._input_msg = self._model.get_input()

        if self._input_msg is None:
            return

        self._input_pub.publish(self._input_msg)


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
