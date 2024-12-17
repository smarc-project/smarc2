#!/usr/bin/python3

import time

from geometry_msgs.msg import PoseStamped
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.node import Node
from smarc_mission_msgs.action import GotoWaypoint
from smarc_mission_msgs.msg import Topics as MissionTopics


try:
    from .RLMissionController import RLMissionController
    from .RLMissionController import MissionStates
except:
    from RLMissionController import RLMissionController
    from RLMissionController import MissionStates


class RLMissionActionServer(RLMissionController):
    """
    A controller example that implements an action server to allow
    another node to control its execution, params, etc.
    """

    def __init__(self, node: Node):
        super().__init__(node)

        # We get the waypoint from the action server instead
        node.destroy_subscription(self.waypoint_sub)

        self._as = ActionServer(
            node=self._node,
            action_type=GotoWaypoint,
            action_name=MissionTopics.GOTO_WP_ACTION,
            goal_callback=self._goal_cb,
            execute_callback=self._execute_cb,
            cancel_callback=self._cancel_cb)

        self._waypoint = None
        self._goal_frame = None
        self._goal_handle = None

        self._loginfo("Dive Action Server started")

    def _goal_cb(self, goal_handle):

        self._loginfo("Goal received")

        self.set_mission_state(MissionStates.RECEIVED, "AS")

        self._goal_handle = goal_handle
        self._waypoint = goal_handle.waypoint
        self._goal_frame = self._waypoint.pose.header.frame_id
        self._requested_rpm = self._waypoint.travel_rpm
        self._goal_tolerance = self._waypoint.goal_tolerance

        self._waypoint.pose.pose.position.z = -self._waypoint.travel_depth

        self._save_wp(self._waypoint.pose)  # get the proper pose

        goal_msg_str = f'Frame: {self._waypoint.pose.header.frame_id}\
                         pos x: {self._waypoint.pose.pose.position.x}\
                         pos y: {self._waypoint.pose.pose.position.y}'

        self._loginfo(goal_msg_str)

        return GoalResponse.ACCEPT

    def _save_wp(self, wp):
        self._waypoint_global = PoseStamped()
        self._waypoint_global.header.stamp = wp.header.stamp
        self._waypoint_global.header.frame_id = wp.header.frame_id
        self._waypoint_global.pose.position.x = wp.pose.position.x
        self._waypoint_global.pose.position.y = wp.pose.position.y
        self._waypoint_global.pose.position.z = wp.pose.position.z
        self._waypoint_global.pose.orientation.x = wp.pose.orientation.x
        self._waypoint_global.pose.orientation.y = wp.pose.orientation.y
        self._waypoint_global.pose.orientation.z = wp.pose.orientation.z
        self._waypoint_global.pose.orientation.w = wp.pose.orientation.w

        self._received_waypoint = True

    async def _execute_cb(self, goal_handle: ServerGoalHandle) -> GotoWaypoint.Result:

        self._loginfo("Executing...")

        result = GotoWaypoint.Result()
        fb_msg = GotoWaypoint.Feedback()

        while True:
            if self._mission_state == MissionStates.RECEIVED:
                self.update()
                self.set_mission_state(MissionStates.ACCEPTED, "AS")

            if self.get_distance() is not None:
                distance = self.get_distance()

                if self._mission_state == MissionStates.ACCEPTED \
                        and distance > self._waypoint.goal_tolerance:
                    self.set_mission_state(MissionStates.RUNNING, "AS")

                if distance <= self._waypoint.goal_tolerance \
                        and self._mission_state == MissionStates.RUNNING:
                    self._loginfo(f"Mission complete. Distance:{distance} <= Tolerance:{self._waypoint.goal_tolerance}")
                    break

                fb_msg.feedback_message = f"Distance to waypoint: {distance:.2f}"
                fb_msg.distance_remaining = distance
                goal_handle.publish_feedback(fb_msg)

                time.sleep(0.1)
            else:
                self._loginfo("get distance is none?")

        goal_handle.succeed()
        result.reached_waypoint = True
        self._waypoint.travel_rpm = 0.0
        self._requested_rpm = self._waypoint.travel_rpm
        self.set_mission_state(MissionStates.COMPLETED, "AS")

        return result

    def _cancel_cb(self, goal_handle: ServerGoalHandle):
        self._loginfo("Cancelled")
        self.set_mission_state(MissionStates.CANCELLED, "AS")
        self._loginfo("Everything set to neutral")

        return CancelResponse.ACCEPT

    def set_feedback_msg(self, msg):
        return msg
