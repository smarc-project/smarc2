import rclpy
from action_msgs.msg import GoalStatus
from rclpy.action.client import ClientGoalHandle
from rclpy.node import Node
from smarc_action_base.smarc_action_base import (
    ActionFeedback,
    ActionResult,
    ActionType,
    SMARCActionClient,
)
from smarc_mission_msgs.action import BaseAction

from lolo_cruise_depth_at_heading.cruise_depth_at_heading_goal import CruiseDepthHeadingGoal
from lolo_cruise_depth_at_heading.action_parsing import ActionSubMsg as ActMsg
from lolo_cruise_depth_at_heading.action_parsing import CruiseDepthHeadingActionParsing


class CruiseDepthHeadingClient(SMARCActionClient):
    """Client for sending Geopoint message requests to vehicles.

    Attributes:
        logger: shorthand for `node.get_logger()`
    """

    def __init__(
        self,
        node: Node,
        action_name: str,
        action_type: ActionType,
        **kwargs,
    ):
        super().__init__(node, action_name, action_type)
        self.logger = self._node.get_logger()
        self.declare_parameters()
        self._json_ops = CruiseDepthHeadingActionParsing()
        self.logger.set_level(rclpy.logging.LoggingSeverity.INFO)

    def declare_parameters(self):
        """Location to declare parameters."""
        pass

    def goal_response_callback(self, goal_handle: ClientGoalHandle):
        """Result when a goal is sent to the server."""
        if not goal_handle.accepted:
            self.logger.info("Goal was not accepted")
            return

    def feedback_callback(self, feedback_msg: ActionFeedback):
        """Result when a goal is sent to the server."""
        self.logger.debug(f"Received feedback {feedback_msg.feedback}")
        self.dist_rem = self._json_ops.decode(
            feedback_msg.feedback,
            ActMsg.FEEDBACK,
        )

    def result_callback(self, result: ActionResult, status: GoalStatus):
        """Result when a goal is sent to the server."""
        self.logger.info(f"Waypoint reached boolean: {result}")
        if result.success:
            return self.get_goal_success()
        else:
            return self.get_goal_error()

    def cancel_callback(self, response):
        """Cancellation callback.

        Args:
            response: receives CancelGoal action msg
        """
        if len(response.goals_canceling) > 0:
            self.logger.info("Successfully canceled goal.")
        else:
            self.logger.info("Unsuccessfully canceled goal.")

    def cancel_geopoint(self):
        """Interacts with action server to cancel action.

        Returns:
            Boolean where true signifies a goal was successfully canceled. False if not true.

        """
        self.cancel_goal(self.cancel_callback)

    def send_cruise_at(self, cruise_at_goal: CruiseDepthHeadingGoal):
        """Request geopoint be sent to server.

        Interface for external usage of client.
        """
        goal_msg = BaseAction.Goal()
        goal_msg.goal = self._json_ops.encode(cruise_at_goal)
        self.send_goal(goal_msg)

    def _test_cruise_at(self):
        """For testing geopoint setting."""
        goal = CruiseDepthHeadingGoal()
        goal.heading = 0.0
        goal.target_depth = 50.0
        goal.min_altitude = 20.0
        goal.rpm = 1000
        goal.timeout = 120
        self.logger.info(f"Sending CruiseDepthHeading goal:\n{goal}")
        self.send_cruise_at(goal)


def main(args=None):
    rclpy.init(args=args)
    node_name = "lolo_cruise_at_heading_client"
    node = Node(node_name)
    action_type = ActionType(BaseAction)
    setpoint = CruiseDepthHeadingClient(node, "auv_cruise_depth_at_heading", action_type)
    setpoint._test_cruise_at()
    rclpy.spin(node)


if __name__ == "__main__":
    main()
