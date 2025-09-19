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
from smarc_msgs.msg import Topics as SmarcTopics
from lolo_msgs.msg import Topics as LoloTopics
from std_msgs.msg import Empty
from std_msgs.msg import String
import json
from enum import Enum


class EmergencyLevel(Enum):
    """Enum for emergency levels."""
    NO_EMERGENCY = 0
    EMERGENCY = 1


class EmergencyServer(SMARCActionServer):
    """Action point server that handle EmergencyAbort messages.

    Attributes:
        logger: shorthand for `node.get_logger()`
        robot_name: provided robot name from launch file
        target_frame: frame that goal's should be transformed to
    """

    def __init__(
        self,
        node: Node,
        action_name,
        action_type: ActionType,
    ):
        super().__init__(
            node,
            action_name,
            action_type,
            SmarcTopics.WARA_PS_ACTION_SERVER_HB_TOPIC,
        )
        self.logger = node.get_logger()
        self.declare_parameters()
        self.declare_publishers()
        self.abort_active = False

        self.logger.set_level(rclpy.logging.LoggingSeverity.DEBUG)

    def declare_parameters(self):
        """Declares parameters for the node."""
        node = self._node
        self._pub_frequency = node.declare_parameter("pub_frequency", 1).value

    def declare_publishers(self):
        """Declares all of node's publishers."""
        node = self._node
        self._abort_pub = node.create_publisher(
            Empty,
            LoloTopics.LOLO_ABORT,
            10,
        )
        self.logger.info("Publisher for Abort created.")

    def publish_emergency_messages(self):
        """ Just publish the abort topics. """
        msg = Empty()
        self._abort_pub.publish(msg)

    def execution_callback(self, goal_handle: ServerGoalHandle) -> ActionResult:
        """Primary execution callback where goal's are handled after acceptance.

        Args:
            goal_handle: handle to control server and add callbacks

        Returns:
            A populated ActionResult message
        """
        self.logger.info("Executing emergency abort goal...")
        rate = self._node.create_rate(self._pub_frequency)
        self.abort_active = True
        result_msg = self.action_type.Result

        while self.abort_active:
            # Check if we've been cancelled!
            if goal_handle.is_cancel_requested:
                self.logger.info("Emergency action was cancelled by client!")
                goal_handle.canceled()
                break

            self.publish_emergency_messages()
            self.publish_feedback(
                goal_handle,
                "Abort in progress. Sending abort to Lolo!",
            )
            rate.sleep()
        rate.destroy()

        result_msg.success = True
        return result_msg

    def _parse_goal(self, goal_request: ActionType.Goal) -> EmergencyLevel:
        """Parses the goal request and extracts the emergency level Enum."""
        goal_msg = goal_request.goal
        self.logger.info(f"Received goal request: {goal_msg}")
        level_json = goal_msg.data
        level_dict = json.loads(level_json)
        emergency_level = level_dict["level"]
        self.logger.info(f"Parsed emergency level: {emergency_level}")
        emergency_level = int(emergency_level)
        return EmergencyLevel(emergency_level)


    def goal_callback(self, goal_request: ActionType.Goal) -> GoalResponse:
        """Considers a goal validity and evaluates whether it should be accepted or not.

        Args:
            goal_request (ActionType.Goal): Goal message

        Returns:
            response: Either GoalResponse.Accept or GoalResponse.Reject

        """
        emergency_level = self._parse_goal(goal_request)

        if emergency_level == EmergencyLevel.NO_EMERGENCY:
            self.logger.info("No emergency abort requested. Rejecting goal.")
            return GoalResponse.REJECT
        elif emergency_level == EmergencyLevel.EMERGENCY:
            self.logger.info("Emergency abort requested.")
            return GoalResponse.ACCEPT
        else:
            self.logger.error(f"Invalid emergency level {emergency_level} requested")
            return GoalResponse.REJECT

    def cancel_callback(self, goal_handle: ServerGoalHandle) -> CancelResponse:
        """Handles canceling of goal requests.

        Args:
            goal_handle: handle

        Returns:
            Cancel response as ACCEPT
        """
        self.logger.info("Canceling goal...")
        self.abort_active = False
        return CancelResponse.ACCEPT

    def publish_feedback(self, goal_handle: ServerGoalHandle, message: str) -> None:
        """Publishes feedback to the client.

        Args:
            goal_handle: handle to control server and add callbacks
            message: feedback message to be published
        """
        feedback_msg = self.action_type.Feedback
        feedback_msg.feedback = String()
        feedback_msg.feedback.data = message
        goal_handle.publish_feedback(feedback_msg)
        # self.logger.info(f"Published feedback: {message}")


def main(args=None):
    rclpy.init(args=args)
    node_name = "emergency_server"
    node = rclpy.node.Node(node_name)
    action_type = ActionType(BaseAction)
    emergency_server = EmergencyServer(node, "emergency_action", action_type)
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()
