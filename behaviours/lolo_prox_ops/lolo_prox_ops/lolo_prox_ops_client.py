import rclpy
from action_msgs.msg import GoalStatus
from geographic_msgs.msg import GeoPoint
from rclpy.action.client import ClientGoalHandle
from rclpy.node import Node
import json
from smarc_action_base.smarc_action_base import (
    ActionFeedback,
    ActionResult,
    ActionType,
    SMARCActionClient,
)
from smarc_mission_msgs.action import BaseAction
from std_msgs.msg import String

from lolo_depth_move_to.depth_move_to_goal import DepthMoveToGoal
#from lolo_depth_move_to.action_parsing import ActionSubMsg as ActMsg
#from lolo_depth_move_to.action_parsing import DepthMoveToActionParsing


class ProxOpsClient(SMARCActionClient):
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
        #self._json_ops = DepthMoveToActionParsing()
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
        #self.dist_rem = self._json_ops.decode(
        #    feedback_msg.feedback,
        #    ActMsg.FEEDBACK,
        #)

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

    def _test_actionserver(self):
        """For testing geopoint setting."""
        self.logger.info(f"Sending goal to action server")
        goal_msg = BaseAction.Goal()
        parameters = {}
        parameters['hej1'] = 123
        parameters['hej2'] = 321
        str_msg = String()
        str_msg.data = json.dumps(parameters)
        goal_msg.goal = str_msg
        self.send_goal(goal_msg)


def main(args=None):
    rclpy.init(args=args)
    node_name = "lolo_move_to_client"
    node = Node(node_name)
    action_type = ActionType(BaseAction)
    setpoint = ProxOpsClient(node, "/lolo_prox_ops", action_type)
    setpoint._test_actionserver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        setpoint.cancel_goal() #Does not work?
        node.get_logger().info("Shutting down lolo prox ops acation server")
        
    finally:
        rclpy.shutdown()
        node.destroy_node()
        rclpy.shutdown()



if __name__ == "__main__":
    main()
