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

        self._robot_base_link = 'sam0_base_link'
        self._goal_frame = 'odom'

        self._tf_goal_to_body = None

        self._states = None

        self._goal_handle = None

#        self._found_tf = False
#
#        tf_update_period = 0.1
#        self._tf_update_timer = node.create_timer(tf_update_period, self.update_tf)


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

        return GoalResponse.ACCEPT


    def _update_tf(self):
        try:
            self._tf_goal_to_body = self._tf_buffer.lookup_transform(self._robot_base_link,
                                                          self._goal_frame,
                                                          rclpy.time.Time(seconds=0))
        except Exception as ex:
            self._loginfo(
                f'Could not transform {self._robot_base_link} to {self._goal_frame}: {ex}')
            return


#        seconds = tf_stamped.header.stamp.sec
#        translation = tf_stamped.transform.translation
#        self._vehicle_state.update_sensor(SensorNames.POSITION, [translation.x, translation.y, translation.z], seconds)
#        quat = tf_stamped.transform.rotation
#        rpy = euler_from_quaternion([quat.x, quat.y, quat.z, quat.w])
#        self._vehicle_state.update_sensor(SensorNames.ORIENTATION_EULER, rpy, seconds)

#    def _update_states(self):


    def get_tf_base_link(self):
        return self._tf_goal_to_body


    def get_waypoint(self):
        # the goal_handle object carries the request from the client
        # this request object is whatever is defined in the .action file
        # and can be examined with `ros2 interface` commands
#        request = self._goal_handle.request
        requested_rpm = 100000 #request.waypoint.travel_rpm

#        requested_goal = PoseStamped()
#        requested_goal.header.stamp = request.waypoint.pose.header.stamp
#        requested_goal.header.frame_id = request.waypoint.pose.header.frame_id
#        requested_goal.pose.position.x = request.waypoint.pose.pose.position.x
#        requested_goal.pose.position.y = request.waypoint.pose.pose.position.y
#        requested_goal.pose.position.z = request.waypoint.pose.pose.position.z
#        requested_goal.pose.orientation.x = request.waypoint.pose.pose.orientation.x
#        requested_goal.pose.orientation.y = request.waypoint.pose.pose.orientation.y
#        requested_goal.pose.orientation.z = request.waypoint.pose.pose.orientation.z
#        requested_goal.pose.orientation.w = request.waypoint.pose.pose.orientation.w
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
        return CancelResponse.ACCEPT


    async def _execute_cb(self, goal_handle:ServerGoalHandle) -> GotoWaypoint.Result:
        # TODO: That's where you put the heading control and all things related to it.
        self._loginfo("Executing...")

#        if not self._found_tf:
#            self._loginfo("No TF yet")
#            return

        # The follwoing is a boiler plate until all calculations are in place.

        seconds = 1
        horizontal_tv = 0.1
        vertical_tv = 0.0
        requested_rpm = 1000
        for i in range(seconds):
            # skip the model here, no computation needed
            # for this example.
            self._view.set_rpm(requested_rpm)
            self._view.set_thrust_vector(horizontal_tv, vertical_tv)
            self._view.update()

            # give some feedback to the client
            fb_msg = GotoWaypoint.Feedback()
            fb_msg.feedback_message = f"{seconds-i} seconds left of {requested_rpm}RPMs"
            fb_msg.distance_remaining = 1.0
            goal_handle.publish_feedback(fb_msg)

            # just a normal sleep is OK here, since this action is _the_ thing
            # running on this thread, and this function is defined async, meaning
            # the caller of this function knows that we will take a while...
            time.sleep(1)

        self._view.set_rpm(0)
        self._view.update()

        # must set the success state otherwise ros will assume "aborted"
        goal_handle.succeed()
        # this callback must return a result
        result = GotoWaypoint.Result()
        result.reached_waypoint = True
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
