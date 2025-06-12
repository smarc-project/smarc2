#!/usr/bin/python3

import time 
import json
import threading

from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.action.server import ServerGoalHandle

from smarc_mission_msgs.action import BaseAction
from smarc_mission_msgs.msg import Topics as MissionTopics
from smarc_msgs.msg import Topics as SMaRCTopics

from smarc_utilities.georef_utils import convert_latlon_to_utm

from geometry_msgs.msg import PoseStamped 
from geographic_msgs.msg import GeoPoint
from std_msgs.msg import String

import traceback
from functools import partial
import enum
import threading
from typing import Any, Callable

from action_msgs.msg import GoalStatus
from action_msgs.srv import CancelGoal

# ROS Imports
from rclpy.action import ActionClient, ActionServer, CancelResponse, GoalResponse
from rclpy.action.client import ClientGoalHandle
from rclpy.action.server import ServerGoalHandle
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node
from rclpy.task import Future
from rclpy.type_support import check_for_type_support
from rosidl_parser.definition import Action
from std_msgs.msg import String

from smarc_action_base.smarc_ros_types import ActionFeedback, ActionGoal, ActionResult

from smarc_action_base.smarc_action_base import (
    ActionResult,
    ActionType,
    SMARCActionServer,
)


try:
    from .DiveSub import DiveSub
    from .IDivePub import IDivePub, MissionStates
except: 
    from DiveSub import DiveSub
    from IDivePub import IDivePub, MissionStates


class DiveActionServerSub(SMARCActionServer, DiveSub):
    """Action Server base class

    Attributes:
        action_type: Action type for retrieving empty Goal, Feedback, and Result messages
    """

    def __init__(
        self,
        node: Node,
        action_name: str,
        action_type: ActionType,
        param, 
        heartbeat_topic: str,
        heartbeat_period: float = 1,
        **kwargs,
    ):
        """Action Server base class initialization function

        Args:
            node: ros2 node
            action_name: name of action client/server in ros
            action_type: ros2 message action type
            heartbeat_topic: Wara-PS heartbeat topic (can be found in smarc_msgs Topics.msg file)
            heartbeat_period: period in seconds of heartbeat timer
        """
        self.param = param
        self._node = node

        SMARCActionServer.__init__(self,
            node,
            action_name,
            action_type,
            SMaRCTopics.WARA_PS_ACTION_SERVER_HB_TOPIC,
        )
        DiveSub.__init__(self,self._node, self.param)

        self._goal_frame = None
        self._goal_handle = None

        self._loginfo("Dive Action Server started")


    def _save_wp(self, wp):
        self._waypoint_global = PoseStamped()
        self._waypoint_global.header.stamp = wp.header.stamp
        self._waypoint_global.header.frame_id = wp.header.frame_id
        self._waypoint_global.pose.position.x = wp.point.x
        self._waypoint_global.pose.position.y = wp.point.y
        self._waypoint_global.pose.position.z = wp.point.z
        self._waypoint_global.pose.orientation.x = 0.0
        self._waypoint_global.pose.orientation.y = 0.0
        self._waypoint_global.pose.orientation.z = 0.0
        self._waypoint_global.pose.orientation.w = 1.0

        self._loginfo(f"Global WP frame: {self._waypoint_global.header.frame_id}")

        self._received_waypoint = True

    def goal_callback(self, goal_request) -> GoalResponse:
        """
        Implement goal acceptance or rejection logic in this callback method.

        Return:
            goal_response: GoalResponse.ACCEPT or GoalResponse.REJECT
        """
        self._loginfo("Goal received")

        self.set_mission_state(MissionStates.RECEIVED, "AS")

        self._goal_handle = goal_request.goal
        fmt_dict = json.loads(goal_request.goal.data)
        geopoint = GeoPoint()
        geopoint.latitude = float(fmt_dict["waypoint"]["latitude"])
        geopoint.longitude = float(fmt_dict["waypoint"]["longitude"])
        geopoint.altitude = 0.0 #float(fmt_dict["waypoint"]["altitude"])
        self._target_rpm = float(fmt_dict["waypoint"]["rpm"])
        self._target_depth = float(fmt_dict["waypoint"]["target_depth"])
        self._goal_tolerance = float(fmt_dict["waypoint"]["tolerance"])
        
        self._waypoint_point = convert_latlon_to_utm(geopoint)

        if self._target_depth < 0:
            self.set_mission_state(MissionStates.REJECTED, "AS")
            err_str = f"Target depth {self._target_depth} < 0. SAM can't fly"
            self._node.get_logger().error(err_str)
            return GoalResponse.REJECT

        self._waypoint_point.point.z = -self._target_depth

        self._save_wp(self._waypoint_point)

        self._requested_rpm = self._target_rpm

        goal_msg_str = f'Frame: {self._waypoint_global.header.frame_id}\
                         pos x: {self._waypoint_global.pose.position.x}\
                         pos y: {self._waypoint_global.pose.position.y}'
        self._loginfo(goal_msg_str)

        return GoalResponse.ACCEPT

    def execution_callback(self, goal_handle: ServerGoalHandle) -> ActionResult:
        """
        Primary execution callback.

        Here your action server will do most of the heavy lifting of computing whatever it needs to.

        WARN: Ensure every iteration in the execution callback and feedback loop you check if the is_valid_goal()
            ROS does not natively cancel these execution callbacks

        Returns:
            result: A populated `self.action_type.Result` or more generically a ROS ActionType.Result()
        """
        self._loginfo("Executing...")

        result = BaseAction.Result()
        fb_msg = BaseAction.Feedback()

        str_msg = String()
        fmt_dict = {}

        while True:
            if self._mission_state == MissionStates.CANCELLED:
                goal_handle.canceled()
                result.success = False
                return result

            if self._mission_state == MissionStates.RECEIVED:
                self._loginfo(f"AS: received")
                self.update()
                self.set_mission_state(MissionStates.ACCEPTED, "AS")

            if self.get_distance() is not None:
                distance = self.get_distance()
                self._loginfo(f"AS: got distance")

                if self._mission_state == MissionStates.ACCEPTED\
                    and distance > self._goal_tolerance:
                    self.set_mission_state(MissionStates.RUNNING, "AS")
                    self._loginfo(f"AS: running")

                if distance <= self._goal_tolerance\
                    and self._mission_state == MissionStates.RUNNING:
                    self._loginfo(f"Mission complete. Distance:{distance} <= Tolerance:{self._goal_tolerance}")
                    break
                
                fmt_dict["distance_remaining"] = distance 
                str_msg.data = json.dumps(fmt_dict)
                fb_msg.feedback = str_msg
                goal_handle.publish_feedback(fb_msg)

                time.sleep(0.1)
            else:
                pass

        goal_handle.succeed()
        result.success = True
        self._requested_rpm = 0.0
        self.set_mission_state(MissionStates.COMPLETED, "AS")

        return result


    def cancel_callback(self, goal_handle) -> CancelResponse:
        """
        Implement goal cancel logic in this method.

        Return:
            cancel_response: CancelResponse.ACCEPT or CancelResponse.REJECT
        """
        self._loginfo("Cancelled")

        self.set_mission_state(MissionStates.CANCELLED, "AS")

        return CancelResponse.ACCEPT


