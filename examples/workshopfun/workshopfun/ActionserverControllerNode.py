#!/usr/bin/python3

import rclpy, sys, time
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.executors import MultiThreadedExecutor

from smarc_mission_msgs.action import GotoWaypoint
from smarc_mission_msgs.msg import Topics as MissionTopics

from .IThrustView import IThrustView



class ActionserverController():
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

        # create an action server, simple stuff
        # the action name here should be in a Topics message
        # like how we have topic names in the other files here.
        # I am skipping that now.
        self._as = ActionServer(
            node = self._node,
            action_type = GotoWaypoint, 
            action_name = MissionTopics.GOTO_WP_ACTION,
            goal_callback = self._goal_cb,
            execute_callback = self._execute_cb,
            cancel_callback = self._cancel_cb)
        

    def _goal_cb(self, goal_handle):
        self._node.get_logger().info("Goal received")
        # When could this be useful?
        # When an action really doesn't want to
        # change/accept goals without a proper
        # cancel/pre-emption.
        #
        # Or for example if the goal is not "good"
        # by some definition. Like if its a "go to point" action
        # then the goal really should have the _point_ in it.
        # Otherwise the action server should reject the goal.
        return GoalResponse.ACCEPT


    def _cancel_cb(self, goal_handle:ServerGoalHandle):
        self._node.get_logger().info("Cancelled")
        # When could this be useful? 
        # For example for a one-time-only action like "drop weight"
        # that can not be cancelled. 
        # Whatever tries to cancel it should be notified of this.
        return CancelResponse.ACCEPT


    async def _execute_cb(self, goal_handle:ServerGoalHandle) -> GotoWaypoint.Result:
        self._node.get_logger().info("Executing...")

        # the goal_handle object carries the request from the client
        # this request object is whatever is defined in the .action file
        # and can be examined with `ros2 interface` commands
        request = goal_handle.request
        requested_rpm = request.waypoint.travel_rpm
        self._node.get_logger().info(f"RPMing:{requested_rpm}")

        seconds = 10
        for i in range(seconds):
            # skip the model here, no computation needed
            # for this example.
            self._view.set_rpm(requested_rpm)
            self._view.update()

            # give some feedback to the client
            fb_msg = GotoWaypoint.Feedback()
            fb_msg.feedback_message = f"{seconds-i} seconds left of {requested_rpm}RPMs"
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
    controller = ActionserverController(node, view)

    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)


if __name__ == "__main__":
    main()