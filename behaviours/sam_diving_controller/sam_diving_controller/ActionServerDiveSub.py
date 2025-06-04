#!/usr/bin/python3

import time 
import json

from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.action.server import ServerGoalHandle

from smarc_mission_msgs.action import BaseAction
from smarc_mission_msgs.msg import Topics as MissionTopics
from smarc_msgs.msg import Topics as SMaRCTopics

from smarc_utilities.georef_utils import convert_latlon_to_utm

from geometry_msgs.msg import PoseStamped 
from std_msgs.msg import String

try:
    from .DiveSub import DiveSub
    from .IDivePub import IDivePub, MissionStates
except: 
    from DiveSub import DiveSub
    from IDivePub import IDivePub, MissionStates


class DiveActionServerSub(DiveSub):
    """
    A controller example that implements an action server to allow
    another node to control its execution, params, etc.
    """
    # FIXME: Updating to new action server structure
    # - Change action type to BaseAction
    # - add json parser
    # - add heartbeat
    def __init__(self,
                 node: Node,
                 dive_pub: IDivePub,
                 param):

        self._node = node
        self._dive_pub = dive_pub
        self.param = param

        super().__init__(self._node, self._dive_pub, self.param)

        # We get the waypoint from the action server instead
        node.destroy_subscription(self.waypoint_sub)

        self._as = ActionServer(
            node = self._node,
            action_type = BaseAction,
            action_name = 'move_to',
            goal_callback = self._goal_cb,
            execute_callback = self._execute_cb,
            cancel_callback = self._cancel_cb)

        self._parsed_action_name: str | None = None
        self._action_name = 'move_to'

        heartbeat_period = 1
        self._heartbeat_topic = SMaRCTopics.WARA_PS_ACTION_SERVER_HB_TOPIC
        self._hb_timer = self._node.create_timer(heartbeat_period, self._heartbeat_cb)
        self._hb_pub = self._node.create_publisher(String, self._heartbeat_topic, 5)
        self._hb_msg = String()
        self._hb_msg.data = self.parsed_action_name


        self._waypoint = None
        self._goal_frame = None
        self._goal_handle = None

        self._loginfo("Dive Action Server started")

    def _heartbeat_cb(self):
        """Sends out topic to Wara-PS on specified heartbeat timer cadence."""
        self._hb_pub.publish(self._hb_msg)
        
        
    @property
    def parsed_action_name(self):
        """Action name with namespace included."""
        if self._parsed_action_name is None:
            self._parsed_action_name = self._construct_hb_msg()
        return self._parsed_action_name

    
    def _construct_hb_msg(self) -> str:
        """Constructs heartbeat message with proper namespace.

            Some documentation that maybe useful: <https://design.ros2.org/articles/actions.html>
        Returns:
            heartbeat message prepended with namespace
        """
        namespace = self._node.get_namespace()
        msg_str = self.combine_ns_and_action(namespace, self._action_name)
        self._node.get_logger().info(
            f"[action-base] Parsed out action server name for Wara-PS: {msg_str}"
        )
        return msg_str

    def combine_ns_and_action(self, namespace: str, action_name: str):
        """Constructs heartbeat message with proper namespace.

            Some documentation that maybe useful: <https://design.ros2.org/articles/actions.html>
        Returns:
            heartbeat message prepended with namespace
        """
        if namespace == "/":
            namespace = ""
        msg_str = f"{namespace}/{action_name}"
        return msg_str

    def _goal_cb(self, goal_handle):

        self._loginfo("Goal received")

        self.set_mission_state(MissionStates.RECEIVED, "AS")

        self._goal_handle = goal_handle
        fmt_dict = json.loads(goal_handle.data)
        geopoint = GeoPoint()
        geopoint.latitude = float(fmt_dict["waypoint"]["latitude"])
        geopoint.longitude = float(fmt_dict["waypoint"]["longitude"])
        geopoint.altitude = float(fmt_dict["waypoint"]["altitude"])
        
        desired_speed = float(fmt_dict["speed"])    # NOTE: This is a string "fast" or "slow"

        self._waypoint_global = convert_latlon_to_utm(geopoint)

        # Check z and altitude.
        self._waypoint_global.point.z = geopoint.altitude

        self._save_wp(self._waypoint_global)

        # NOTE: Check for distance or so to reject the goal

        #self._goal_frame = self._waypoint.pose.header.frame_id

        if desired_speed.lower() == "fast":
            self._requested_rpm = 1500
        elif desired_speed.lower() == "normal":
            self._requested_rpm = 1000
        else:
            self._requested_rpm = 500

        self._goal_tolerance = 2.0 #self._waypoint.goal_tolerance    # Not there anymore

        goal_msg_str = f'Frame: {self._waypoint.pose.header.frame_id}\
                         pos x: {self._waypoint.pose.pose.position.x}\
                         pos y: {self._waypoint.pose.pose.position.y}'

        self._loginfo(goal_msg_str)


        return GoalResponse.ACCEPT
    

    def _save_wp(self, wp):
        # FIXME: Update with new action server/client structure
        self._waypoint_global = PoseStamped()
        self._waypoint_global.header.stamp = wp.header.stamp
        self._waypoint_global.header.frame_id = wp.header.frame_id
        self._waypoint_global.pose.position.x = wp.point.x
        self._waypoint_global.pose.position.y = wp.point.y
        self._waypoint_global.pose.position.z = wp.point.z
        self._waypoint_global.pose.orientation.x = 0
        self._waypoint_global.pose.orientation.y = 0
        self._waypoint_global.pose.orientation.z = 0
        self._waypoint_global.pose.orientation.w = 1

        self._loginfo(f"Global WP frame: {self._waypoint_global.header.frame_id}")

        # TODO: Get the proper RPM from the waypoint

        self._received_waypoint = True


    async def _execute_cb(self, goal_handle:ServerGoalHandle) -> BaseAction.Result:

        self._loginfo("Executing...")

        result = BaseAction.Result()
        fb_msg = BaseAction.Feedback()

        while True:
            if self._mission_state == MissionStates.RECEIVED:
                self.update()
                self.set_mission_state(MissionStates.ACCEPTED, "AS")

            if self.get_distance() is not None:
                distance = self.get_distance()

                if self._mission_state == MissionStates.ACCEPTED\
                    and distance > self._goal_tolerance:
                    self.set_mission_state(MissionStates.RUNNING, "AS")

                if distance <= self._goal_tolerance\
                    and self._mission_state == MissionStates.RUNNING:
                    self._loginfo(f"Mission complete. Distance:{distance} <= Tolerance:{self._goal_tolerance}")
                    break
                
                fb_msg.feedback_message = f"Distance to waypoint: {distance:.2f}"
                fb_msg.distance_remaining = distance
                goal_handle.publish_feedback(fb_msg)

                time.sleep(0.1)
            else:
                pass
                #self._loginfo("get distance is none?")

        goal_handle.succeed()
        result.reached_waypoint = True
        self._waypoint.travel_rpm = 0.0
        self._requested_rpm = self._waypoint.travel_rpm
        self.set_mission_state(MissionStates.COMPLETED, "AS")

        return result


    def _cancel_cb(self, goal_handle:ServerGoalHandle):
        self._loginfo("Cancelled")

        self.set_mission_state(MissionStates.CANCELLED, "AS")

        self._dive_pub.set_vbs(0)
        self._dive_pub.set_lcg(50)
        self._dive_pub.set_thrust_vector(0.0, 0.0) 
        self._dive_pub.set_rpm(0, 0)

        self._loginfo("Everything set to neutral")

        return CancelResponse.ACCEPT

    def set_feedback_msg(self,msg):
        return msg

