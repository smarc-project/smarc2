import rclpy
from smarc_mission_msgs.action import BaseAction
from smarc_mission_msgs.msg import Topics
from smarc_action_base.smarc_action_base import (
    ActionFeedback,
    ActionResult,
    ActionType,
    SMARCActionClient,
    ActionClientState,
)

# from rclpy.action.client import ClientGoalHandle
from rclpy.node import Node
from rclpy.task import Future
from rclpy.type_support import check_for_type_support
from smarc_action_base.smarc_ros_types import ActionFeedback, ActionGoal, ActionResult
from action_msgs.msg import GoalStatus


class BTActionClient(SMARCActionClient):
    """Client for sending BT action requests to vehicles.

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
        self.logger.set_level(rclpy.logging.LoggingSeverity.DEBUG)
        self._action_name = action_name
        self.feedback_message = ''

    def feedback_callback(self, feedback_msg: ActionFeedback):
        """Result when a goal is sent to the server."""
        self.logger.debug(f"Received feedback {feedback_msg.feedback}")
        self.feedback_message = feedback_msg.feedback.data
        self._feedback_received = True

    def result_callback(self, result: ActionResult, status: GoalStatus):
        """Result when a goal is sent to the server."""
        self.logger.info(f"Waypoint reached boolean: {result}")
        
        if result.success:
            self.state = ActionClientState.DONE
            return self.get_goal_success()
        else:
            self.state = ActionClientState.ERROR
            return self.get_goal_error()
        
    
    def cancel_callback(self, response):
        """Result when a goal is cancelled."""
        
        if len(response.goals_canceling) > 0:
            self.logger.info(f"Successfully cancelled goal")
            self.state = ActionClientState.CANCELLED
        else:
            self.logger.info(f"Failed to cancel goal")
            self.state = ActionClientState.ERROR


    def goal_response_callback(self, goal_handle: ActionGoal):
        if not goal_handle.accepted:
            self.logger.info("Goal was not accepted")
            
        else:
            self.logger.info("Goal was accepted")
            self.state = ActionClientState.ACCEPTED
            self._goal_handle = goal_handle

    def get_ready(self):
        """Get the action client ready to send goals."""
        self.state = ActionClientState.READY
        self.logger.info(f"Action client {self._action_name} is ready.")
        return True