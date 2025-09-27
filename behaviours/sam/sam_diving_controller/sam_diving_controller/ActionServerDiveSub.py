#!/usr/bin/python3

import time 
import json
import threading

import numpy as np

from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.action.server import ServerGoalHandle
from rcl_interfaces.msg import ParameterDescriptor

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
import rclpy
from rclpy.action import ActionClient, ActionServer, CancelResponse, GoalResponse
from rclpy.action.client import ClientGoalHandle
from rclpy.action.server import ServerGoalHandle
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node
from rclpy.task import Future
from rclpy.type_support import check_for_type_support
from rclpy.time import Duration, Time
from rosidl_parser.definition import Action
from std_msgs.msg import String

from smarc_action_base.smarc_ros_types import ActionFeedback, ActionGoal, ActionResult

from smarc_action_base.smarc_action_base import (
    ActionResult,
    ActionType,
    SMARCActionServer,
)
from smarc_mission_msgs.action import BaseAction
from smarc_msgs.msg import Topics as SmarcTopics
from smarc_control_msgs.msg import Topics as ControlTopics

from tf2_geometry_msgs import do_transform_pose_stamped
from tf2_ros import Buffer, TransformException, TransformListener

from sam_path_following.path_action import ActionComponent as ActC
from sam_path_following.path_action import PathAction
from go_to_hydrobaticpoint.hydrobaticpoint_action import HydrobaticPointAction

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

class HydropointServer(SMARCActionServer, DiveSub):
    """Action point server that handle GotoGeopoint messages.

    Attributes:
        logger: shorthand for `node.get_logger()`
        robot_name: provided robot name from launch file
        target_frame: frame that goal's should be transformed to
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

        self.param = param
        self._node = node

        SMARCActionServer.__init__(self,
            node,
            action_name,
            action_type,
            SMaRCTopics.WARA_PS_ACTION_SERVER_HB_TOPIC,
        )
        DiveSub.__init__(self,self._node, self.param)

        self.logger = node.get_logger()
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(
            self._tf_buffer, self._node, spin_thread=True
        )
        self.declare_parameters()

        # We get the waypoint from the action server instead
        node.destroy_subscription(self.waypoint_sub)

        self.logger.set_level(rclpy.logging.LoggingSeverity.INFO)
        self._json_ops: HydrobaticPointAction = HydrobaticPointAction()

        self.logger.info("Hydropoint AS created")

    def _save_wp(self, wp):
        self._waypoint_global = wp

        self.logger.info(f"Global WP frame: {self._waypoint_global.header.frame_id}")

        self._received_waypoint = True

    def _tol_check(self, delta):
        """Checks if vehicle is within tolerance of setpoint.

        Args:
            delta (float): distance to setpoint

        Returns:
            tol_check (bool): true if vehicle is within zone
        """
        if delta > self._setpoint_tol:
            return False
        else:
            return True

    @staticmethod
    def _str_posestamp(pose: PoseStamped):
        """Helper function to print PoseStamped Messages nicely."""
        return f"\nFrame: {pose.header.frame_id}\nPosition: {pose.pose.position}\nOrientation: {pose.pose.orientation}"

    def declare_parameters(self):
        """Declares all of node's parameters in a single location."""
        node = self._node
        #self.robot_name = node.declare_parameter("robot_name", "Quadrotor").value
        self._target_frame_param = node.declare_parameter("target_frame", "odom").value

        self._distance_frame_param = node.declare_parameter(
            "distance_frame",
            "base_link",
            ParameterDescriptor(
                description="Frame for which the distance to target will be computed (usually base_link)"
            ),
        ).value

        self._distance_frame_suffix = node.declare_parameter(
            "distance_frame_suffix",
            "_gt",
            ParameterDescriptor(
                description="Frame suffix for distance frame. Commonly is '_gt' for ground truth if applicable"
            ),
        ).value

        self._frame_suffix = node.declare_parameter(
            "frame_suffix",
            "_gt",
            ParameterDescriptor(
                description="Frame suffix for transform. Commonly is '_gt' for ground truth if applicable"
            ),
        ).value

        self._setpoint_tol: float = node.declare_parameter(
            "setpoint_tolerance",
            1.25,
            ParameterDescriptor(
                description="Setpoint tolerance for when the goal is considered achieved (Euclidean norm)."
            ),
        ).value

        # self._setpoint_topic = node.declare_parameter(
        #     "setpoint_topic",
        #     "go_to_setpoint",
        #     ParameterDescriptor(
        #         description="Topic to publish setpoint targets to. Will be prepended with 'robot_name'"
        #     ),
        # ).value

        self._goal_threshold = (
            node.declare_parameter(
                "goal_threshold",
                10,
                ParameterDescriptor(
                    description="Distance threshold in meters where a goal should be rejected. (Euclidean Norm)"
                ),
            ).value
        )

        self.target_frame = (
            f"{self.robot_name}/{self._target_frame_param}{self._frame_suffix}"
        )
        self.logger.info(f"Target frame {self.target_frame}")

        self.distance_frame = f"{self.robot_name}/{self._distance_frame_param}{self._distance_frame_suffix}"
        self.logger.info(f"Distance frame {self.distance_frame}")


    def goal_callback(self, goal_request: ActionType.Goal) -> GoalResponse:
        """Considers a goal validity and evaluates whether it should be accepted or not.

        Args:
            goal_request (ActionType.Goal): Goal message

        Returns:
            response: Either GoalResponse.Accept or GoalResponse.Reject

        """
        goal_request = goal_request.goal
        self.logger.info(f"goal_request: {goal_request}, actC.GOAL: {ActC.GOAL}")
        hydro_setpoint = self._json_ops.decode(goal_request, 0)
        self.logger.info(f"Recieved setpoint at {hydro_setpoint}")
        pose_stamped = hydro_setpoint
        try:
            dist = self.compute_distance(pose_stamped)
        except TransformException as err:
            err_str = "Could not successfully compute transform. Rejecting goal!\n"
            exec_up = TransformException(err_str)
            exec_up.__cause__ = err
            # Adding error message to traceback for debug log.
            self.logger.info(err_str)
            self.logger.debug(traceback.format_exc())
            return GoalResponse.REJECT

        if dist >= self._goal_threshold:
            err_str = f"Rejecting goal due to violating distance threshold. Criteria: {dist:.1f} >= {self._goal_threshold:.1f}"
            self.logger.info(err_str)

            # providing additional details if possible about error
            try:
                pose = self.get_robot_pose_in_msg_frame(pose_stamped)
                err_str = "Robot pose in message frame is:" + self._str_posestamp(pose)
                self.logger.debug(err_str)
            except TransformException:
                pass
            return GoalResponse.REJECT
        # Saves and accepts as all criteria fulfilled
        self._save_wp(pose_stamped)
        return GoalResponse.ACCEPT

    def compute_distance(self, pose_stamped: PoseStamped) -> float:
        """Euclidean distance to target.

        Args:
            pose_stamped: current location of target in utm frame
        Returns:
            distance: euclidean distance to target
        Raises:
            TransformException when transform fails
        """
        try:
            override_frame = self.distance_frame
            pose_transformed: PoseStamped = self.transform_goal(
                pose_stamped, override_target=override_frame
            )
            self.logger.debug(
                "Position after transform:" + self._str_posestamp(pose_transformed)
            )
        except TransformException as err:
            err_str = "Failed to compute transform when computing distance to target"
            raise TransformException(err_str) from err

        pose_delta = pose_transformed.pose
        delta = np.sqrt(
            (pose_delta.position.x) ** 2
            + (pose_delta.position.y) ** 2
            + (pose_delta.position.z) ** 2
        )

        # TODO: add orientation errors

        return delta

    def transform_goal(
        self,
        pose_stamped: PoseStamped,
        override_target: str | None = None,
    ) -> PoseStamped:
        """Provides transformed point from pose_stamped.header.frame_id to self.target_frame.

        Raises:
            TransformException when transformation fails allowing for caller to handle exception

        Returns:
            PoseStamped in specified frame
        """
        if override_target is None:
            t = self._tf_buffer.lookup_transform(
                target_frame=self.target_frame,
                source_frame=pose_stamped.header.frame_id,
                time=Time(seconds=0),
                timeout=Duration(seconds=2),
            )
        else:
            t = self._tf_buffer.lookup_transform(
                target_frame=override_target,
                source_frame=pose_stamped.header.frame_id,
                time=Time(seconds=0),
                timeout=Duration(seconds=2),
            )
        # based on ReadMe in repository
        return do_transform_pose_stamped(pose_stamped, t)

    def get_robot_pose_in_msg_frame(self, pose_stamped: PoseStamped) -> PoseStamped:
        """Provides robot position in message frame.

        Useful for showing user how far away the drone is from the target and understand why goal is rejected

        Raises:
            TransformException when transformation fails allowing for caller to handle exception

        Returns:
            pose: pose in specified frame
        """

        t = self._tf_buffer.lookup_transform(
            target_frame=pose_stamped.header.frame_id,
            source_frame=self.target_frame,
            time=rclpy.time.Duration(seconds=0),
            timeout=Duration(seconds=2),
        )
        # based on ReadMe in repository
        return do_transform_pose_stamped(PoseStamped(), t)

    def execution_callback(self, goal_handle: ServerGoalHandle) -> ActionResult:
        """Primary execution callback where goal's are handled after acceptance.

        Args:
            goal_handle: handle to control server and add callbacks

        Returns:
            A populated ActionResult message
        """
        result_msg = self.action_type.Result
        hydropoint = self._json_ops.decode(goal_handle.request.goal, 0) #ActC.GOAL)
        self.logger.info(f"Hydropoint sent: {hydropoint}")

        # Action succeeded
        status = self.feedback_loop(hydropoint, goal_handle)
        if status == "cancelled":
            self.logger.info("Goal was cancelled by client.")
            self.set_mission_state(MissionStates.CANCELLED, "AS")
            result_msg.success = False
            return result_msg
        
        self.set_mission_state(MissionStates.COMPLETED, "AS")
        result_msg.success = True

        return result_msg

    def feedback_loop(self, pose_stamped: PoseStamped, goal_handle: ServerGoalHandle):
        """Abstracted feedback loop where tolerance checks are conducted.

        Args:
            pose_stamped: target location
            goal_handle: passed in to enable feedback publishing
        """
        rate = self._node.create_rate(2)
        d = self.compute_distance(pose_stamped)
        feedback = self.action_type.Feedback
        tol_check = self._tol_check(d)
        start_time = self._node.get_clock().now()
        while not tol_check:
            current_time = self._node.get_clock().now()
            elapsed = (current_time - start_time).nanoseconds / 1e9  # seconds
            self.set_mission_state(MissionStates.RUNNING, "AS")

            #self.logger.info(f"elapsed: {elapsed}")

            if elapsed > 50:
                self.logger.info("Goal was cancelled by timeout.")
                goal_handle.abort()
                return "cancelled"

            if goal_handle.is_cancel_requested:
                self.logger.info("Goal was cancelled by client.")
                goal_handle.canceled()
                return "cancelled"
            
            feedback.feedback = self._json_ops.encode(d)
            goal_handle.publish_feedback(feedback)
            rate.sleep()
            d = self.compute_distance(pose_stamped)
            tol_check = self._tol_check(d)
            self.logger.debug(f"Tol check result: {tol_check}, Distance: {d} m.")
        rate.destroy()

        return "done"

    def cancel_callback(self, goal_handle: ServerGoalHandle) -> CancelResponse:
        """Handles canceling of goal requests.

        Args:
            goal_handle: handle

        Returns:
            Cancel response as ACCEPT
        """
        self.logger.info("Cancelled!")
        self.set_mission_state(MissionStates.CANCELLED, "AS")

        return CancelResponse.ACCEPT



class PathServer(SMARCActionServer, DiveSub):
    """Action point server that handle GotoGeopoint messages.

    Attributes:
        logger: shorthand for `node.get_logger()`
        robot_name: provided robot name from launch file
        target_frame: frame that goal's should be transformed to
    """

    def __init__(self, node: Node, action_name, action_type: ActionType, param):

        self.param = param
        self._node = node

        SMARCActionServer.__init__(self,
            node,
            action_name,
            action_type,
            SMaRCTopics.WARA_PS_ACTION_SERVER_HB_TOPIC,
        )
        DiveSub.__init__(self,self._node, self.param)

        self.logger = node.get_logger()

        self.path = None
        self.path_len = None
        self.current_idx = 0

        #self.declare_parameters()

        self.logger.set_level(rclpy.logging.LoggingSeverity.INFO)

        self._json_ops: PathAction = PathAction()

        self._loginfo("Path Action Server started")


    # TODO: Cancel process. Need to stop the controller as well, similar to the wp action server.

#    def declare_parameters(self):
#        """Declares all of node's parameters in a single location."""
#
#        # TODO: Which ones are actually needed?
#
#        node = self._node
#        self.robot_name = node.declare_parameter("robot_name", "Quadrotor").value
#        self._target_frame_param = node.declare_parameter("target_frame", "odom").value
#
#        self._distance_frame_param = node.declare_parameter(
#            "distance_frame",
#            "base_link",
#            ParameterDescriptor(
#                description="Frame for which the distance to target will be computed (usually base_link)"
#            ),
#        ).value
#
#        self._distance_frame_suffix = node.declare_parameter(
#            "distance_frame_suffix",
#            "_gt",
#            ParameterDescriptor(
#                description="Frame suffix for distance frame. Commonly is '_gt' for ground truth if applicable"
#            ),
#        ).value
#
#        self._frame_suffix = node.declare_parameter(
#            "frame_suffix",
#            "_gt",
#            ParameterDescriptor(
#                description="Frame suffix for transform. Commonly is '_gt' for ground truth if applicable"
#            ),
#        ).value
#
#        self._setpoint_tol: float = node.declare_parameter(
#            "setpoint_tolerance",
#            0.25,
#            ParameterDescriptor(
#                description="Setpoint tolerance for when the goal is considered achieved (Euclidean norm)."
#            ),
#        ).value
#
#        # self._setpoint_topic = node.declare_parameter(
#        #     "setpoint_topic",
#        #     "go_to_setpoint",
#        #     ParameterDescriptor(
#        #         description="Topic to publish setpoint targets to. Will be prepended with 'robot_name'"
#        #     ),
#        # ).value
#
#        self._goal_threshold = (
#            node.declare_parameter(
#                "goal_threshold",
#                10,
#                ParameterDescriptor(
#                    description="Distance threshold in meters where a goal should be rejected. (Euclidean Norm)"
#                ),
#            ).value
#        )
#
#        self.target_frame = (
#            f"{self.robot_name}/{self._target_frame_param}{self._frame_suffix}"
#        )
#        self.logger.info(f"Target frame {self.target_frame}")
#
#        self.distance_frame = f"{self.robot_name}/{self._distance_frame_param}{self._distance_frame_suffix}"
#        self.logger.info(f"Distance frame {self.distance_frame}")

    def _save_path(self, path):
        """
        Convert path from list to numpy array.
        """
        self.path = np.asarray(path)
        self.logger.info(f"AS: saved path")


    def goal_callback(self, goal_request: ActionType.Goal) -> GoalResponse:
        """Considers a goal validity and evaluates whether it should be accepted or not.

        Args:
            goal_request (ActionType.Goal): Goal message

        Returns:
            response: Either GoalResponse.Accept or GoalResponse.Reject

        """
        # TODO: Think of whether you want to reject any goal. For now, accept
        # everything, as we assume the planner to know what it's doing.
        goal_request = goal_request.goal
        path = self._json_ops.decode(goal_request, ActC.GOAL)
        self.logger.info(f"Recieved path")
        self._save_path(path)
        self.path_len = len(self.path) # TODO: Check which index to use, 0 or 1

        # Accepts as all criteria fulfilled
        return GoalResponse.ACCEPT


    def execution_callback(self, goal_handle: ServerGoalHandle) -> ActionResult:
        """Primary execution callback where goal's are handled after acceptance.

        Args:
            goal_handle: handle to control server and add callbacks

        Returns:
            A populated ActionResult message
        """
        result_msg = self.action_type.Result
        status = self.feedback_loop(goal_handle)
        if status == "cancelled":
            self.logger.info("Goal was cancelled by client.")
            result_msg.success = False
            return result_msg
        
        self.set_mission_state(MissionStates.COMPLETED, "AS")
        result_msg.success = True
        return result_msg

    def feedback_loop(self, goal_handle: ServerGoalHandle):
        """Abstracted feedback loop where tolerance checks are conducted.

        Args:
            pose_stamped: target location
            goal_handle: passed in to enable feedback publishing
        """
        rate = self._node.create_rate(2)
        feedback = self.action_type.Feedback

        while self.current_idx < self.path_len:

            self.set_mission_state(MissionStates.RUNNING, "AS")
            if goal_handle.is_cancel_requested:
                self.logger.info("Goal was cancelled by client.")
                goal_handle.canceled()
                return "cancelled"
            
            feedback.feedback = self._json_ops.encode(float(self.current_idx)) #- NOTE: the encode returns nonetype value if not float
            goal_handle.publish_feedback(feedback)
            rate.sleep()

        goal_handle.succeed()
        rate.destroy()
        return "done"


    def cancel_callback(self, goal_handle: ServerGoalHandle) -> CancelResponse:
        """Handles canceling of goal requests.

        Args:
            goal_handle: handle

        Returns:
            Cancel response as ACCEPT
        """

        self._loginfo("Cancelled")

        self.set_mission_state(MissionStates.CANCELLED, "AS")

        return CancelResponse.ACCEPT

