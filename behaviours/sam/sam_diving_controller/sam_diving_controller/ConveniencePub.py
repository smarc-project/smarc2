#!/usr/bin/python3
import sys
import rclpy
from rclpy.node import Node
from rclpy.clock import Clock

import numpy as np

from smarc_control_msgs.msg import Topics as ControlTopics
from smarc_control_msgs.msg import ControlError, ControlInput, ControlReference, ControlState

from geometry_msgs.msg import PoseWithCovarianceStamped, PoseStamped, Pose
from nav_msgs.msg import Odometry, Path

try:
    from .IDivePub import IDivePub
except:
    from IDivePub import IDivePub

class ConveniencePub(IDivePub):
    """
    Implements convenience topic publishers for debugging
    """
    def __init__(self, node: Node, dive_sub, dive_controller) -> None:

        self._node = node

        self._robot_name = self._node.get_parameter('robot_name').get_parameter_value().string_value

        #self._state_pub = node.create_publisher(ControlState, ControlTopics.STATES_CONV, 10)
        self._state_pub = node.create_publisher(Odometry, ControlTopics.STATES_CONV, 10)
        self._ref_pub = node.create_publisher(ControlReference, ControlTopics.REF_CONV, 10)
        self._error_pub = node.create_publisher(ControlError, ControlTopics.CONTROL_ERROR_CONV, 10)
        self._input_pub = node.create_publisher(ControlInput, ControlTopics.CONTROL_INPUT_CONV, 10)
        #self._waypoint_pub = node.create_publisher(PoseWithCovarianceStamped, ControlTopics.WAYPOINT_CONV, 10)
        self._waypoint_pub = node.create_publisher(Odometry, ControlTopics.WAYPOINT_CONV, 10)
        self._mpc_pred_pub = node.create_publisher(Path, ControlTopics.MPC_PRED, 10)

        self._state_msg = None
        self._ref_msg = None
        self._error_msg = None
        self._input_msg = None
        self._waypoint = None
        self._waypoint_msg = None
        self._goal_tolerance = None
        self._dive_mode = None

        self._node = node
        self._dive_sub = dive_sub
        self._dive_controller = dive_controller

        self._previous_print = ""


    def _loginfo(self, s):
        self._node.get_logger().info(s)


    def _update_state(self) -> None:
        self._state_msg = self._dive_controller.get_state()

        if self._state_msg is None:
            return

        self._state_pub.publish(self._state_msg)

    def _update_ref(self) -> None:
        self._ref_msg = self._dive_controller.get_ref()

        if self._ref_msg is None:
            return

        self._ref_pub.publish(self._ref_msg)

    def _update_error(self) -> None:
        self._error_msg = self._dive_controller.get_error()

        if self._error_msg is None:
            return

        self._error_pub.publish(self._error_msg)

    def _update_input(self) -> None:
        self._input_msg = self._dive_controller.get_input()

        if self._input_msg is None:
            return

        self._input_pub.publish(self._input_msg)

    def _update_waypoint(self) -> None:
        #self._waypoint = self._dive_sub.get_waypoint_in_odom()
        self._waypoint = self._dive_controller.get_wp()
        self._goal_tolerance = self._dive_sub.get_goal_tolerance()

        if self._waypoint is None:
            return

        #self._waypoint_msg = PoseWithCovarianceStamped()
        #self._waypoint_msg.header.frame_id = self._robot_name + 'odom'
        #self._waypoint_msg.pose.pose = self._waypoint
        #self._waypoint_msg.pose.pose.orientation.w = 1.0
        #cov = np.zeros([6,6])
        #cov[0][0] = np.sqrt(self._goal_tolerance)
        #cov[1][1] = np.sqrt(self._goal_tolerance)
        #cov[2][2] = np.sqrt(self._goal_tolerance)
        #cov_vec = cov.reshape(36)
        #self._waypoint_msg.pose.covariance = cov_vec.tolist()

        #self._waypoint_pub.publish(self._waypoint_msg)
        self._waypoint_pub.publish(self._waypoint)


    def _publish_predicted_path(self):
        x_pred = self._dive_controller.get_mpc_pred()
        current_attitude = np.array([1, 0, 0, 0])

        now = self._node.get_clock().now()

        predicted_path_msg = Path()
        predicted_path_msg.header.stamp = now.to_msg()
        predicted_path_msg.header.frame_id = 'mocap'

        for i, predicted_state in enumerate(x_pred):
            # Calculate future time offset
            future_time = now + rclpy.duration.Duration(seconds=i * 0.1)

            # Create PoseStamped
            pose_stamped = self._vector2PoseMsg('mocap', predicted_state[0:3], predicted_state[3:7])
            #pose_stamped = self._vector2PoseMsg('mocap', predicted_state[0:3], current_attitude)
            pose_stamped.header.stamp = future_time.to_msg()
            pose_stamped.header.frame_id = 'mocap'

            predicted_path_msg.poses.append(pose_stamped)

        self._mpc_pred_pub.publish(predicted_path_msg)


    def _vector2PoseMsg(self, frame_id, position, attitude):
        pose_msg = PoseStamped()
        pose_msg.header.stamp = self._node.get_clock().now().to_msg()
        pose_msg.header.frame_id = frame_id
        # FIXME: Check these!
        # Some NED -> ENU conversion for plotting...?
        pose_msg.pose.position.x = float(position[0])
        pose_msg.pose.position.y = float(position[1])
        pose_msg.pose.position.z = float(position[2])
        pose_msg.pose.orientation.w = float(attitude[0])
        pose_msg.pose.orientation.x = float(attitude[1])
        pose_msg.pose.orientation.y = float(attitude[2])
        pose_msg.pose.orientation.z = float(attitude[3])

        return pose_msg


    def _print_state(self) -> None:
        # Get all info and print it
        s = "Dive Control States:\n"
        if self._state_msg is None:
            s += f"No state msg yet."
        else:
            s += "States:\n"
            s += f"   x: {self._state_msg.pose.pose.position.x:.3f}, "\
                 f"y: {self._state_msg.pose.pose.position.y:.3f}, "\
                 f"z: {self._state_msg.pose.pose.position.z:.3f}, "\
            # TODO: State is now an odom message, fix the angles, since they're quaternions.
                 #f"roll: {self._state_msg.pose.pose.orientation.roll:.3f}, "\
                 #f"pitch: {self._state_msg.pose.pose.pitch:.3f}, "\
                 #f"yaw: {self._state_msg.pose.yaw:.3f}\n"
            s += f"   DiveController mission state: {self._dive_sub.get_mission_state()}\n"

        if self._input_msg is None:
            s += f"No inputs yet\n"
        else:
            s += f"Dive Mode: {self._dive_controller.get_dive_mode()}\n"
            s += f"Actuators:\n"
            s += f"   VBS: {self._input_msg.vbs:.3f}, "\
                 f"LCG: {self._input_msg.lcg:.3f}, "\
                 f"TV stern: {self._input_msg.thrustervertical:.3f}, "\
                 f"TV rudder: {self._input_msg.thrusterhorizontal:.3f}, "\
                 f"RPM: {self._input_msg.thrusterrpm:.3f}\n"

        if self._waypoint_msg is None:
            s += "No Waypoint Yet\n"
        else:
            distance = self._dive_sub.get_distance()
            heading = self._dive_sub.get_heading()
            dive_pitch = self._dive_sub.get_dive_pitch()

            # Somehow we get None every now and then and that crashes everything. 
            distance_str = f"{distance:.3f}" if distance is not None else "None"
            heading_str = f"{heading:.3f}" if heading is not None else "None"
            dive_pitch_str = f"{dive_pitch:.3f}" if dive_pitch is not None else "None"

            s += f"Waypoint Following\n"
            s += f"   distance: " + distance_str + \
                 f" heading: " + heading_str + \
                 f" dive pitch: " + dive_pitch_str + "\n"

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


    def update(self) -> None:
        self._update_state()
        self._update_ref()
        self._update_error()
        self._update_input()
        self._update_waypoint()
        self._print_state()
        self._publish_predicted_path()

