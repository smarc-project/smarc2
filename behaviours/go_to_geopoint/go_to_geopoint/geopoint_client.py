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
from smarc_mission_msgs.action import GotoGeopoint


class GeopointClient(SMARCActionClient):
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
        self.logger.debug(f"Received feedback {feedback_msg.distance_remaining}")
        self.dist_rem = feedback_msg.distance_remaining

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

    def send_geopoint(self, geo_pt: GeoPoint):
        """Request geopoint be sent to server.

        Interface for external usage of client.
        """
        goal_msg = GotoGeopoint.Goal()
        goal_msg.setpoint = GeoPoint()
        self.send_goal(goal_msg, server_timeout_sec=1)

    def _test_geopoint(self):
        """For testing geopoint setting."""
        goal_msg = GotoGeopoint.Goal()
        goal_msg.setpoint = GeoPoint()
        # https://awsm-tools.com/utm-to-lat-long?form%5Beasting%5D=652698.125&form%5Bnorthing%5D=6524250.5&form%5Bzone%5D=33&form%5Bband%5D=V&form%5Bellipsoid%5D=WGS+84
        goal_msg.setpoint.latitude = 58.850281
        goal_msg.setpoint.longitude = 17.674866
        goal_msg.setpoint.altitude = 10.0
        self.logger.info(f"Sending geopoint {goal_msg.setpoint}")
        self.send_goal(goal_msg, server_timeout_sec=1)


def main(args=None):
    rclpy.init(args=args)
    node_name = "setpoint_client"
    node = Node(node_name)
    action_type = ActionType(GotoGeopoint)
    setpoint = GeopointClient(node, "go_to_setpoint", action_type)
    setpoint._test_geopoint()
    rclpy.spin(node)


if __name__ == "__main__":
    main()
