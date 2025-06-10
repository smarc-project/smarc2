import rclpy
from action_msgs.msg import GoalStatus
from geographic_msgs.msg import GeoPoint
from rclpy.action.client import ClientGoalHandle
from rclpy.node import Node
from smarc_action_base.smarc_action_base import (
    ActionFeedback,
    ActionResult,
    ActionType,
    SMARCActionClient,
)
from smarc_mission_msgs.action import BaseAction

from lolo_loiter.loiter_goal import LoiterGoal
from lolo_loiter.action_parsing import ActionSubMsg as ActMsg
from lolo_loiter.action_parsing import LoiterActionParsing


class LoiterClient(SMARCActionClient):
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
        self._json_ops = LoiterActionParsing()
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
            self.logger.info("Successfully cancelled goal.")
        else:
            self.logger.info("Unsuccessfully cancelled goal.")

    def cancel_geopoint(self):
        """Interacts with action server to cancel action.

        Returns:
            Boolean where true signifies a goal was successfully cancelled. False if not true.

        """
        self.cancel_goal(self.cancel_callback)

    def send_loiter(self, loiter_goal: LoiterGoal):
        """Request geopoint be sent to server.

        Interface for external usage of client.
        """
        goal_msg = BaseAction.Goal()
        goal_msg.goal = self._json_ops.encode(loiter_goal)
        self.send_goal(goal_msg)

    def _test_loiter(self):
        """For testing geopoint setting."""
        goal = LoiterGoal()
        goal.timeout = 600
        self.logger.info(f"Sending Loiter goal:\n{goal}")
        self.send_loiter(goal)


def main(args=None):
    rclpy.init(args=args)
    node_name = "lolo_loiter_client"
    node = Node(node_name)
    action_type = ActionType(BaseAction)
    setpoint = LoiterClient(node, "auv_loiter", action_type)
    setpoint._test_loiter()
    rclpy.spin(node)


if __name__ == "__main__":
    main()
