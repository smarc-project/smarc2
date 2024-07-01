#!/usr/bin/python3

import rclpy, sys, time
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.executors import MultiThreadedExecutor

from smarc_mission_msgs.action import GotoWaypoint
from smarc_mission_msgs.msg import Topics as MissionTopics

from .IThrustView import IThrustView

from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener

import tf2_geometry_msgs.tf2_geometry_msgs

from geometry_msgs.msg import PoseStamped, TransformStamped


class GoToWaypointActionServerController():
    """
    A controller example that implements an action server to allow
    another node to control its execution, params, etc.

    This is basically an annotated version of the example server found here:
    https://github.com/ros2/examples/tree/humble/rclpy/actions/minimal_action_server/examples_rclpy_minimal_action_server
    There are examples of single-goal servers, queueing etc.
    """
    def __init__(self,
                 node: Node,
                 view: IThrustView):

        self._node = node
        self._view = view

        self._as = ActionServer(
            node = self._node,
            action_type = GotoWaypoint,
            action_name = MissionTopics.GOTO_WP_ACTION,
            goal_callback = self._goal_cb,
            execute_callback = self._execute_cb,
            cancel_callback = self._cancel_cb)

        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self._node)

        self._robot_base_link = 'sam0/base_link_gt'
        self._goal_frame = None

        self._tf_goal_to_body = None

        self._states = None

        self._waypoint = None
        self._mission_state = None
        self._goal_handle = None
        self._distance_to_target = None

        self._loginfo("AS started")


    def _loginfo(self, s):
        self._node.get_logger().info(s)


    def _goal_cb(self, goal_handle):
        self._loginfo("Goal received")
        # When could this be useful?
        # When an action really doesn't want to
        # change/accept goals without a proper
        # cancel/pre-emption.
        #
        # Or for example if the goal is not "good"
        # by some definition. Like if its a "go to point" action
        # then the goal really should have the _point_ in it.
        # Otherwise the action server should reject the goal.

        # TODO: Set some flag that allows the model to start doing its thing
        # Could be superflous tho, since the model might not have a waypoint if we don't get one in the first place.

        self._goal_handle = goal_handle
        self._waypoint = goal_handle.waypoint
        self._goal_frame = self._waypoint.pose.header.frame_id

        goal_msg_str = f'Frame: {self._waypoint.pose.header.frame_id}\
                         pos x: {self._waypoint.pose.pose.position.x}\
                         pos y: {self._waypoint.pose.pose.position.y}'

        self._loginfo(goal_msg_str)

        self._mission_state = "GOAL ACCEPTED"

        return GoalResponse.ACCEPT


    def _update_tf(self):
        if self._goal_frame is None:
            return

        try:
            self._tf_goal_to_body = self._tf_buffer.lookup_transform(self._robot_base_link,
                                                          self._goal_frame,
                                                          rclpy.time.Time(seconds=0))
        except Exception as ex:
            self._loginfo(
                f'Could not transform {self._robot_base_link} to {self._goal_frame}: {ex}')
            return


#    def _update_states(self):

    def get_mission_state(self):
        return self._mission_state


    def get_tf_base_link(self):
        return self._tf_goal_to_body


    def get_waypoint(self):
        # the goal_handle object carries the request from the client
        # this request object is whatever is defined in the .action file
        # and can be examined with `ros2 interface` commands
        if self._waypoint is None:
            return None

        requested_goal = PoseStamped()
        requested_goal.header.stamp = self._waypoint.pose.header.stamp
        requested_goal.header.frame_id = self._waypoint.pose.header.frame_id
        requested_goal.pose.position.x = self._waypoint.pose.pose.position.x
        requested_goal.pose.position.y = self._waypoint.pose.pose.position.y
        requested_goal.pose.position.z = self._waypoint.pose.pose.position.z
        requested_goal.pose.orientation.x = self._waypoint.pose.pose.orientation.x
        requested_goal.pose.orientation.y = self._waypoint.pose.pose.orientation.y
        requested_goal.pose.orientation.z = self._waypoint.pose.pose.orientation.z
        requested_goal.pose.orientation.w = self._waypoint.pose.pose.orientation.w

        return requested_goal


    def get_requested_rpm(self):

        if self._waypoint is None:
            return 0

        return self._waypoint.travel_rpm


    def get_goal_tolerance(self):

        if self._waypoint is None:
            return 0

        return self._waypoint.goal_tolerance


    def set_distance_to_target(self,distance):
        #self._loginfo("set distance")
        self._distance_to_target = distance

    def set_mission_state(self,state):
        self._mission_state = state


    def set_feedback_msg(self,msg):
        return msg


    def get_states(self):
        return self._states


    def update(self):
        """
        All the things when updating
        """
        self._update_tf()
        #self._update_states()


    def _cancel_cb(self, goal_handle:ServerGoalHandle):
        self._loginfo("Cancelled")
        # When could this be useful? 
        # For example for a one-time-only action like "drop weight"
        # that can not be cancelled. 
        # Whatever tries to cancel it should be notified of this.

        self._mission_state = "CANCELLED"

        return CancelResponse.ACCEPT


    async def _execute_cb(self, goal_handle:ServerGoalHandle) -> GotoWaypoint.Result:
        # FIXME: Use this to tell the action client that stuff is happening and when you're done
        # Probably needs some connection to the waypoint following model, set some states in the
        # controller or so to do things.
        #
        # The important part is the .succeed() and ther result message.

        self._loginfo("Executing...")

        result = GotoWaypoint.Result()
        fb_msg = GotoWaypoint.Feedback()


        while True:
            if self._distance_to_target is not None:
                if self._distance_to_target <= self._waypoint.goal_tolerance\
                        and self._mission_state == "RUNNING":
                    self._loginfo("breaking")
                    break
                
                fb_msg.feedback_message = f"Distance to waypoint: {self._distance_to_target}"
                fb_msg.distance_remaining = self._distance_to_target
                goal_handle.publish_feedback(fb_msg)

                time.sleep(0.1)

        goal_handle.succeed()
        result.reached_waypoint = True
        self._waypoint.travel_rpm = 0.0
        self._mission_state = "COMPLETED"

        return result



def main():
    # when creating the _object_ rather than the _class_, we use the concrete classes
    from .SAMThrustView import SAMThrustView

    # create a node and our objects in the usual manner.
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("ActionServerNode")
    view = SAMThrustView(node)
    controller = GoToWaypointActionServerController(node, view)

    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)


if __name__ == "__main__":
    main()
