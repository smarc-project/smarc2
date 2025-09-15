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
    ActionClientState,
)
from smarc_mission_msgs.action import BaseAction
from geometry_msgs.msg import Pose, PoseStamped
from smarc_control_msgs.msg import Topics as ControlTopics
from nav_msgs.msg import Path

from sam_path_following.path_action import ActionComponent as ActC
from sam_path_following.path_action import PathAction


class PathClient(SMARCActionClient):
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
        self._json_ops = PathAction()
        self.logger.set_level(rclpy.logging.LoggingSeverity.INFO)
        self.goal_processed = False

        # Wait for server
        # while not self._client.wait_for_server(timeout_sec=1.) and rclpy.ok():
        #     self.logger.info(f"Node {action_name} waiting for go_to_hydropoint server")

        self.logger.info(f"Node {action_name} connected to go_to_hydropoint server")

    def declare_parameters(self):
        """Location to declare parameters."""
        pass


    def run(self):
        pass
        #self.logger.info("Subscribing to mocap hydro point topic")
        #self.mocap_goal_sub = self._node.create_subscription(PoseStamped, 
        #                                                     ControlTopics.MOCAP_HYDROPOINT,
        #                                                     self.mocap_hydro_cb, 1)


    def send_path(self, path: Path):

        if not self.goal_processed:

            if self.state != ActionClientState.SENT:

                if self.state == ActionClientState.ACCEPTED or self.state == ActionClientState.RUNNING:
                    self.goal_processed = True
                    #self._node.destroy_subscription(self.mocap_goal_sub)
                    return

                self.logger.info(f"Sending trajectory")
                goal_msg = BaseAction.Goal()
                goal_msg.goal = self._json_ops.encode(path)
                self.send_goal(goal_msg)


    def goal_response_callback(self, goal_handle: ClientGoalHandle):
        """Result when a goal is sent to the server."""
        if not goal_handle.accepted:
            self.logger.info("Goal was not accepted")
            return
        else:
            self.logger.info("Goal was accepted")


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


def main(args=None):
    rclpy.init(args=args)
    node_name = "mocap_hydropoint_client"
    node = Node(node_name)
    action_type = ActionType(BaseAction)
    setpoint = HydropointClient(node, "go_to_hydropoint", action_type)
    setpoint.run()
    # setpoint._test_geopoint()
    rclpy.spin(node)


if __name__ == "__main__":
    main()
