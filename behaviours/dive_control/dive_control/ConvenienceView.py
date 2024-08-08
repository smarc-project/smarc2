#!/usr/bin/python3
import sys
import rclpy
from rclpy.node import Node

import numpy as np

from smarc_msgs.msg import ThrusterRPM
from sam_msgs.msg import Topics as SamTopics
from sam_msgs.msg import ThrusterAngles

from smarc_control_msgs.msg import Topics as ControlTopics
from smarc_control_msgs.msg import ControlError, ControlInput, ControlReference, ControlState

from geometry_msgs.msg import PoseStamped, TransformStamped, PoseWithCovarianceStamped

try:
    from .IDiveView import IDiveView
except:
    from IDiveView import IDiveView

class ConvenienceView(IDiveView):
    """
    Implements convenience topic publishers for debugging
    """
    def __init__(self, node: Node, controller, model) -> None:
        self._state_pub = node.create_publisher(ControlState, ControlTopics.STATES_CONV, 10)
        self._ref_pub = node.create_publisher(ControlReference, ControlTopics.REF_CONV, 10)
        self._error_pub = node.create_publisher(ControlError, ControlTopics.CONTROL_ERROR_CONV, 10)
        self._input_pub = node.create_publisher(ControlInput, ControlTopics.CONTROL_INPUT_CONV, 10)
        self._waypoint_pub = node.create_publisher(PoseWithCovarianceStamped, ControlTopics.WAYPOINT_CONV, 10)


        self._state_msg = None
        self._ref_msg = None
        self._error_msg = None
        self._input_msg = None
        self._waypoint = None
        self._waypoint_msg = None
        self._goal_tolerance = None

        self._node = node
        self._controller = controller
        self._model = model

        self._previous_print = ""


    def _loginfo(self, s):
        self._node.get_logger().info(s)

    def update(self) -> None:
        self._update_state()
        self._update_ref()
        self._update_error()
        self._update_input()
        self._update_waypoint()
        self._print_state()


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

    def _update_waypoint(self) -> None:
        self._waypoint = self._controller.get_waypoint()
        self._goal_tolerance = self._controller.get_goal_tolerance()

        if self._waypoint is None:
            return

        self._waypoint_msg = PoseWithCovarianceStamped()
        self._waypoint_msg.header = self._waypoint.header
        self._waypoint_msg.pose.pose = self._waypoint.pose
        self._waypoint_msg.pose.pose.orientation.w = 1.0
        cov = np.zeros([6,6])
        cov[0][0] = self._goal_tolerance
        cov[1][1] = self._goal_tolerance
        cov[2][2] = self._goal_tolerance
        cov_vec = cov.reshape(36)
        self._waypoint_msg.pose.covariance = cov_vec.tolist()

        self._waypoint_pub.publish(self._waypoint_msg)

    def _print_state(self) -> None:
        # Get all info and print it
        s = "Dive Control States:\n"
        if self._state_msg is None:
            s += f"No state msg yet."
        else:
            s += "States:\n"
            s += f"   x: {self._state_msg.pose.x:.3f}, "\
                 f"y: {self._state_msg.pose.y:.3f}, "\
                 f"z: {self._state_msg.pose.z:.3f}, "\
                 f"roll: {self._state_msg.pose.roll:.3f}, "\
                 f"pitch: {self._state_msg.pose.pitch:.3f}, "\
                 f"yaw: {self._state_msg.pose.yaw:.3f}\n"
            s += f"   DiveController mission state: {self._controller.get_mission_state()}\n"

        if self._input_msg is None:
            s += f"No inputs yet\n"
        else:
            s += f"Actuators:\n"
            s += f"   VBS: {self._input_msg.vbs:.3f}, "\
                 f"LCG: {self._input_msg.lcg:.3f}, "\
                 f"TV ver: {self._input_msg.thrustervertical:.3f}, "\
                 f"TV hor: {self._input_msg.thrusterhorizontal:.3f}, "\
                 f"RPM: {self._input_msg.thrusterrpm:.3f}\n"

        if self._waypoint_msg is None:
            s += "No Waypoint Yet\n"
        else:
            distance = self._controller.get_distance()
            heading = self._controller.get_heading()
            dive_pitch = self._controller.get_dive_pitch()

            s += f"Waypoint Following\n"
            s += f"   distance: {distance:.3f}, "\
                 f"heading: {heading:.3f}, "\
                 f"dive pitch: {dive_pitch:.3f}\n"

        if self._error_msg is None:
            s += "No control yet\n"
        else:
            s += f"Control Error:\n"
            s += f"   depth: {self._error_msg.z:.3f}, "\
                 f"pitch: {self._error_msg.pitch:.3f}, "\
                 f"heading: {self._error_msg.heading:.3f}\n"

        s += f"[-----]\n"

        # so we dont spam the terminal with the same string forever
        if s == self._previous_print:
            return

        self._loginfo(s)
        self._previous_print = s

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
