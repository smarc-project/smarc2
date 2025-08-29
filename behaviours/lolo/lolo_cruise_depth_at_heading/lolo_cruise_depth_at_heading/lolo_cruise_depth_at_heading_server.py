import math

import rclpy
from rclpy.action import CancelResponse, GoalResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from smarc_action_base.smarc_action_base import (
    ActionResult,
    ActionType,
    SMARCActionServer,
)
from smarc_mission_msgs.action import BaseAction
from smarc_msgs.msg import Topics

from lolo_cruise_depth_at_heading.action_parsing import ActionSubMsg as ActMsg
from lolo_cruise_depth_at_heading.action_parsing import CruiseDepthHeadingActionParsing
from virtual_lolo.lolo import Lolo


class CruiseDepthHeadingServer(SMARCActionServer):
    """Action point server to handle CruiseDepthHeading messages.

    Attributes:
        logger: shorthand for `node.get_logger()`
        robot_name: provided robot name from launch file
        target_frame: frame that goal's should be transformed to
    """

    def __init__(
        self, node: Node, action_name, action_type: ActionType,
    ):
        super().__init__(
            node,
            action_name,
            action_type,
            Topics.WARA_PS_ACTION_SERVER_HB_TOPIC,
        )
        self.logger = node.get_logger()
        self.logger.set_level(rclpy.logging.LoggingSeverity.INFO)
        self._json_ops: CruiseDepthHeadingActionParsing = CruiseDepthHeadingActionParsing()

        self.declare_parameters()
        self.vehicle = Lolo(node=node,robot_name=self._robot_name,
                            limits_filename=self._vehicle_limits_filename)


    def declare_parameters(self):
        """Declares all of node's parameters in a single location."""
        node = self._node
        self._robot_name = node.declare_parameter(
            "robot_name", self._node.get_namespace()).value
        self._update_rate = node.declare_parameter("update_rate", 10).value
        # If filename not declared, default values should be
        # set by the vehicle and not the server.
        self._vehicle_limits_filename = node.declare_parameter(
            "limits_filename", "").value

    def ned_compass_heading_to_enu(self, angle_deg: float):
        """
        Converts compass heading (0-360) in NED (0 pointing north),
        to heading (-pi to pi) in ENU.
        """
        return math.atan2(math.cos(math.radians(angle_deg)),
                          math.sin(math.radians(angle_deg)))

    def execution_callback(self, goal_handle: ServerGoalHandle) -> ActionResult:
        """Primary execution callback where goal's are handled after acceptance.

        Args:
            goal_handle: handle to control server and add callbacks

        Returns:
            A populated ActionResult message
        """
        self.logger.debug("Executing callback")
        self.logger.debug(f"{goal_handle.request}")
        result_msg = self.action_type.Result
        cruise_at_goal = self._json_ops.decode(goal_handle.request.goal, ActMsg.GOAL)

        result_msg.success = self.feedback_loop(goal_handle,
                                                int(cruise_at_goal.timeout))
        self.vehicle.reset_goal()
        return result_msg

    def send_goal_to_vehicle(self, goal):
        """Sends the goal to the vehicle object (only lolo is supported atm).

        Args:
            goal: CruiseDepthHeadingGoal instance.

        Returns:
            Boolean flag, true if the goal was accepted successfully.
        """
        return self.vehicle.set_goal(yaw_enu=self.ned_compass_heading_to_enu(goal.heading),
                                    depth=goal.target_depth,
                                    altitude=goal.min_altitude,
                                    rpm=goal.rpm,
                                    timeout=goal.timeout)

    def goal_callback(self, goal_request: ActionType.Goal) -> GoalResponse:
        """Considers a goal validity and evaluates whether it should be accepted or not.

        Args:
            goal_request (ActionType.Goal): Goal message

        Returns:
            response: Either GoalResponse.Accept or GoalResponse.Reject

        """
        goal_request = goal_request.goal
        cruise_at_goal = self._json_ops.decode(goal_request, ActMsg.GOAL)
        self.logger.info(f"Recieved CruiseDepthHeading goal with parameters:\n {cruise_at_goal}")

        if cruise_at_goal.heading > 360.0 or cruise_at_goal.heading < 0.0:
            self.logger.error(f"Rejecting goal. Heading angle of {cruise_at_goal.heading} must be within 0-360 in NED.")
            return GoalResponse.REJECT
        # Send the goal to the vehicle and check if it passed the check.
        if not self.send_goal_to_vehicle(cruise_at_goal):
            self.logger.error("Rejecting goal. Goal does not fulfill vehicle limits.")
            return GoalResponse.REJECT

        # Accepts as all criteria fulfilled
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle: ServerGoalHandle) -> CancelResponse:
        """Handles canceling of goal requests.

        Args:
            goal_handle: handle

        Returns:
            Cancel response as ACCEPT
        """
        self.vehicle.reset_goal()
        return CancelResponse.ACCEPT

    def feedback_loop(self, goal_handle: ServerGoalHandle, timeout: int) -> bool:
        """Abstracted feedback loop where tolerance checks are conducted.

        Args:
            goal_handle: passed in to enable feedback publishing
            timeout: time limit for the server to reach the goal

        Returns:
            Boolean flag, True if the goal was reached within the timeout.
        """
        rate = self._node.create_rate(self._update_rate)
        feedback = self.action_type.Feedback
        action_start_time = int(self._node.get_clock().now().nanoseconds * 1e-9)
        goal_reached = True

        # Check if we have timed out first.
        timed_out = self.timed_out(action_start_time, timeout)
        while not timed_out:
            # Check if we've been cancelled!
            if goal_handle.is_cancel_requested:
                self.logger.info("Goal was cancelled by client!")
                goal_handle.canceled()
                goal_reached = False
                break

            time_now = int(self._node.get_clock().now().nanoseconds * 1e-9)
            time_until_done = timeout - (time_now - action_start_time)
            feedback.feedback = self._json_ops.encode(float(time_until_done))
            self.logger.info(f"\nCourse following for {time_until_done} more seconds.",
                             throttle_duration_sec=10)
            goal_handle.publish_feedback(feedback)
            self.vehicle.update()
            rate.sleep()

            timed_out = self.timed_out(action_start_time, timeout)

        rate.destroy()
        return goal_reached

    def timed_out(self, start_time: int, timeout: int) -> bool:
        """Checks if action has taken too long.

        Args:
            start_time: start time of feedback_loop of action server.
            timeout: max duration allowed to reach goal.

        Returns:
            Boolean flag, true if goal should be aborted.
        """
        time_now = int(self._node.get_clock().now().nanoseconds * 1e-9)
        return True if (time_now - start_time) > timeout else False


def main(args=None):
    rclpy.init(args=args)
    node_name = "lolo_cruise_depth_at_heading_server"
    node = rclpy.node.Node(node_name)
    action_type = ActionType(BaseAction)
    lolo_cruise_at = CruiseDepthHeadingServer(node, "cruise_depth_at_heading", action_type)
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()
