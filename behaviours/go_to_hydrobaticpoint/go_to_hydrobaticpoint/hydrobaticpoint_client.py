import rclpy
from action_msgs.msg import GoalStatus
from geographic_msgs.msg import GeoPoint
from rclpy.action import CancelResponse
from rclpy.action.client import ClientGoalHandle
from rclpy.node import Node
from smarc_action_base.smarc_action_base import (
    ActionFeedback,
    ActionResult,
    ActionType,
    SMARCActionClient,
)
from smarc_mission_msgs.action import BaseAction
from geometry_msgs.msg import Pose, PoseStamped

from go_to_hydrobaticpoint.hydrobaticpoint_action import ActionComponent as ActC
from go_to_hydrobaticpoint.hydrobaticpoint_action import HydrobaticPointAction


class HydropointClient(SMARCActionClient):
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
        self._json_ops = HydrobaticPointAction()
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
            ActC.FEEDBACK,
        )

    def result_callback(self, result: ActionResult, status: GoalStatus):
        """Result when a goal is sent to the server."""
        self.logger.info(f"Waypoint reached boolean: {result}")

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

    def send_hydropoint(self, hydro_pt: PoseStamped):
        """Request hydropoint be sent to server.

        Interface for external usage of client.
        """
        goal_msg = BaseAction.Goal()
        goal_msg.goal = self._json_ops.encode(hydro_pt)
        self.send_goal(goal_msg, server_timeout_sec=1)

    def _test_geopoint(self):
        """For testing geopoint setting."""
        hydropoint = PoseStamped()
        hydropoint.header.frame_id = "mocap"
        hydropoint.pose.position.x = 3.
        hydropoint.pose.position.y = 0.
        hydropoint.pose.position.z = 1.
        hydropoint.pose.orientation.x = 0.
        hydropoint.pose.orientation.y = 0.
        hydropoint.pose.orientation.z = 0.
        hydropoint.pose.orientation.w = 1.
        self.logger.info(f"Sending hydropoint {hydropoint}")
        self.send_hydropoint(hydropoint)


def main(args=None):
    rclpy.init(args=args)
    node_name = "hydropoint_client"
    node = Node(node_name)
    action_type = ActionType(BaseAction)
    setpoint = HydropointClient(node, "go_to_hydropoint", action_type)
    setpoint._test_geopoint()
    rclpy.spin(node)


if __name__ == "__main__":
    main()
