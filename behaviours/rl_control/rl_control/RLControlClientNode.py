#!/usr/bin/python3

import rclpy
import sys
from action_msgs.msg import GoalStatus
from builtin_interfaces.msg import Time as Stamp
from geometry_msgs.msg import PoseStamped
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.time import Time as rcl_Time
from smarc_mission_msgs.action import GotoWaypoint
from smarc_mission_msgs.msg import Topics as MissionTopics


class DiveToWaypointActionClient():
    """
    Action Client version of the setpoint node

    A dead-simple client to call the server in this package.
    This is basically an annotated version of:
    https://github.com/ros2/examples/tree/humble/rclpy/actions/minimal_action_client
    You can find some other examples there that do slightly different things.
    """
    def __init__(self,
                 node: Node) -> None:
        self._node = node

        self._ac = ActionClient(node=self._node,
                                action_type=GotoWaypoint,
                                action_name=MissionTopics.GOTO_WP_ACTION)

        # to check if we even have a running server later
        self._goal_handle = None

    def _loginfo(self, s):
        self._node.get_logger().info(s)


    def _goal_response_cb(self, future):
        """
        We will register this method to the action client when we
        send a goal later.
        The action client will call this when we get a response from
        the server: It could accept or reject our goal, the future here
        will have that information for us to handle.
        """
        goal_handle = future.result() # wait for it
        if not goal_handle.accepted:
            self._loginfo("Goal rejected. Sadness")
            return

        self._loginfo("Goal accepted. Success, hurray")

        self._goal_handle = goal_handle

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self._get_result_cb)


    def _get_result_cb(self, future):
        result = future.result().result
        status = future.result().status
        if status == GoalStatus.STATUS_SUCCEEDED:
            self._loginfo(f"Success: {result.reached_waypoint}")
        else:
            self._loginfo(f"NOT Success: Status:{status}, result:{result.reached_waypoint}")

        rclpy.shutdown()


    def _feedback_cb(self, feedback):
        # this field contains the object we defined in smarc_mission_msgs/action/GotoWaypoint.action
        self._loginfo(f"Got feedback from server: {feedback.feedback.feedback_message}")


    def send_goal(self):

        self._loginfo("Waiting for server to come alive")
        server_is_ready = self._ac.wait_for_server(timeout_sec=30)

        if not server_is_ready:
            self._loginfo("Server was not availble, quitting!")
            rclpy.shutdown()
            return

        waypoint = PoseStamped()
        waypoint.header.frame_id = 'sam0/odom_gt'
        waypoint.header.stamp = self.rcl_time_to_stamp(self._node.get_clock().now())
        waypoint.pose.position.x = 50.0
        waypoint.pose.position.y = 0.0
        waypoint.pose.position.z = 0.0
        waypoint.pose.orientation.x = 0.0
        waypoint.pose.orientation.y = 0.0
        waypoint.pose.orientation.z = 0.0
        waypoint.pose.orientation.w = 1.0

        goal_msg = GotoWaypoint.Goal()
        goal_msg.waypoint.pose = waypoint
        goal_msg.waypoint.travel_rpm = 500.0

        self._loginfo(f"Sending goal: {goal_msg}")

        self._send_goal_future = self._ac.send_goal_async(
            goal=goal_msg,
            feedback_callback=self._feedback_cb)

        self._send_goal_future.add_done_callback(self._goal_response_cb)


    def rcl_time_to_stamp(self,time: rcl_Time) -> Stamp:
        """
        Converts rcl Time to stamp
        :param time:
        :return:
        """
        stamp = Stamp()
        stamp.sec = int(time.nanoseconds // 1e9)
        stamp.nanosec = int(time.nanoseconds % 1e9)
        return stamp

    def cancel_goal(self):
        self._loginfo("Cancel Goal")

        self._loginfo(f"Goal Handle: {self._goal_handle}")

        if self._goal_handle is not None:
            self._loginfo('Sending cancel request...')
            cancel_future = self._goal_handle.cancel_goal_async()
            cancel_future.add_done_callback(self.cancel_response_callback)

    def cancel_response_callback(self, future):
        cancel_response = future.result()
        if len(cancel_response.goals_canceling) > 0:
            self._loginfo('Goal successfully cancelled')
        else:
            self._loginfo('Goal failed to cancel')


def main():
    # create a node and our objects in the usual manner.
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("DiveActionClientNode")

    ac = DiveToWaypointActionClient(node)

    ac.send_goal()

    # To test the cancel callback
    node.create_timer(5.0, ac.cancel_goal)

    rclpy.spin(node)
    ac._loginfo("spin")


if __name__ == "__main__":
    main()
