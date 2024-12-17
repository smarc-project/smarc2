#!/usr/bin/python3
import enum
import math

import numpy as np
import rclpy
import tf2_geometry_msgs.tf2_geometry_msgs
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from tf_transformations import euler_from_quaternion


class MissionStates(enum.Enum):
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    PAUSED = "PAUSED"
    EMERGENCY = "EMERGENCY"
    RECEIVED = "RECEIVED"
    COMPLETED = "COMPLETED"
    NONE = "NONE"
    ACCEPTED = "ACCEPTED"
    CANCELLED = "CANCELED"

    def __str__(self):
        return self.name

    def TERMINAL_STATES():
        return [MissionStates.COMPLETED,
                MissionStates.CANCELLED,
                MissionStates.STOPPED,
                MissionStates.NONE]


class RLMissionController():
    """
    Dive Controller to listen to a waypoint and provide the corresponding setpoints to the
    DivingModel within the MVC framework
    """

    def __init__(self, node: Node):

        self._node = node

        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self._node)

        # We need to declare the parameter we want to read out from the alunch file first.
        self._node.declare_parameter('robot_name')
        # TODO: add _gt as tf_suffix parameter. Then it's easier to change depending on whether we're using the sim or the real robot.
        self._robot_base_link = self._node.get_parameter('robot_name').get_parameter_value().string_value + '/base_link_gt'

        self._depth_setpoint = None
        self._pitch_setpoint = None
        self._requested_rpm = None
        self._goal_tolerance = None
        self._waypoint_global = None
        self._waypoint_body = None
        self._received_waypoint = False

        self._mission_state = MissionStates.NONE

        self._tf_base_link = None



        # TODO: Hardcoded topic _at the root_ even... david plz. how will this work with 2 sams?
        self.waypoint_sub = node.create_subscription(msg_type=Odometry, topic='/ctrl/waypoint', callback=self._wp_cb, qos_profile=10)

        self._loginfo("Dive Controller Node started")

    # Internal methods
    def _loginfo(self, s):
        self._node.get_logger().info(s)


    def _wp_cb(self, wp):
        self._waypoint_global = PoseStamped()
        self._waypoint_global.header.stamp = wp.header.stamp
        self._waypoint_global.header.frame_id = wp.header.frame_id
        self._waypoint_global.pose.position.x = wp.pose.pose.position.x
        self._waypoint_global.pose.position.y = wp.pose.pose.position.y
        self._waypoint_global.pose.position.z = wp.pose.pose.position.z
        self._waypoint_global.pose.orientation.x = wp.pose.pose.orientation.x
        self._waypoint_global.pose.orientation.y = wp.pose.pose.orientation.y
        self._waypoint_global.pose.orientation.z = wp.pose.pose.orientation.z
        self._waypoint_global.pose.orientation.w = wp.pose.pose.orientation.w

        # TODO: Get the proper RPM from the waypoint
        self._requested_rpm = 500

        self._received_waypoint = True

    def _update_tf(self):
        if self._waypoint_global is None:
            return

        try:
            self._tf_base_link = self._tf_buffer.lookup_transform(self._robot_base_link,
                                                                  self._waypoint_global.header.frame_id,
                                                                  rclpy.time.Time(seconds=0))
        except Exception as ex:
            self._loginfo(
                f"Could not transform {self._robot_base_link} to {self._waypoint_global.header.frame_id}: {ex}")
            return

    def _transform_wp(self):
        if self._waypoint_global is None:
            return

        if self._tf_base_link is None:
            return

        self._waypoint_body = tf2_geometry_msgs.do_transform_pose(self._waypoint_global.pose, self._tf_base_link)

    # Get methods
    def get_depth_setpoint(self):
        if self._waypoint_body is not None:
            self._depth_setpoint = self._waypoint_global.pose.position.z

        return self._depth_setpoint

    def get_pitch_setpoint(self):
        if self._waypoint_body is not None:
            rpy = euler_from_quaternion([
                self._waypoint_global.pose.orientation.x,
                self._waypoint_global.pose.orientation.y,
                self._waypoint_global.pose.orientation.z,
                self._waypoint_global.pose.orientation.w])

            self._pitch_setpoint = rpy[1]

        return self._pitch_setpoint

    def get_heading_setpoint(self):
        return 0.0

    def get_rpm_setpoint(self):
        return self._requested_rpm

    def get_heading(self):

        if self._waypoint_body is None:
            return None

        heading = math.atan2(self._waypoint_body.position.y, self._waypoint_body.position.x)

        return heading

    def get_distance(self):
        """
        Euclidean norm as distance from body, i.e. origin to waypoint
        """

        if self._waypoint_body is None:
            return None

        #        if self._mission_state == MissionStates.RECEIVED:
        #            self.update()
        #            self.set_mission_state(MissionStates.ACCEPTED, "DC")

        distance = math.sqrt(self._waypoint_body.position.x ** 2 + self._waypoint_body.position.y ** 2 + self._waypoint_body.position.z ** 2)

        return distance

    def get_dive_pitch(self):
        if self._waypoint_body is None:
            return None

        # With the ata2, we automatically get the desired diving pitch angle that corresponds to 
        # a ENU system, i.e. positive pitch for diving down, negative pitch for diving up
        current_depth = self.get_depth()
        depth_error = np.abs(self._waypoint_global.pose.position.z) - np.abs(current_depth)
        distance = self.get_distance()
        dive_pitch = math.atan2(depth_error, distance)

        return dive_pitch

    def get_waypoint(self):
        return self._waypoint_global

    def get_goal_tolerance(self):

        if self._goal_tolerance is None:
            return 0

        return self._goal_tolerance

    def get_mission_state(self):
        """
        This is needed when using an action server. Then it has the proper string.
        Otherwise nothing happens and the condition in the DivingModel is ignored.
        Could be fixed at one point...
        """
        return self._mission_state

    # Has methods
    def has_waypoint(self):
        return self._received_waypoint

    def set_mission_state(self, new_state, node_name):
        old_state = self._mission_state
        self._mission_state = new_state

        s = ""
        if new_state in MissionStates.TERMINAL_STATES():
            # TODO: Setting the waypoint to None kills the controller, bc it expects
            # a pose.
            # self._waypoint_global = None
            s = "(Terminal)"

        self._loginfo(f"DiveController state: from {node_name}: {old_state} --> {new_state}{s}")

    def update(self):
        """
        All the things when updating
        """
        self._update_tf()
        self._transform_wp()
