import traceback
from unicodedata import name

import numpy as np
import rclpy
from geodesy import utm
from rclpy.action import CancelResponse, GoalResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.time import Duration, Time
from smarc_action_base.smarc_action_base import (
    ActionResult,
    ActionType,
    SMARCActionServer,
)
from smarc_mission_msgs.action import EmergencyAbort
from smarc_msgs.msg import PercentStamped, ThrusterRPM, Topics
from sam_msgs.msg import Topics as SamTopics
from std_msgs.msg import String


class EmergencyServer(SMARCActionServer):
    """Action point server that handle EmergencyAbort messages.

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
        self.declare_publishers()

        self.logger.set_level(rclpy.logging.LoggingSeverity.INFO)

    def declare_publishers(self):
        """Declares all of node's publishers."""
        node = self._node
        self._vbs_pub = node.create_publisher(
            PercentStamped,
            SamTopics.VBS_CMD_TOPIC,
            10,
        )
        self._rpm1_pub = node.create_publisher(
            ThrusterRPM,
            SamTopics.THRUSTER1_CMD_TOPIC,
            10,
        )
        self._rpm2_pub = node.create_publisher(
            ThrusterRPM,
            SamTopics.THRUSTER2_CMD_TOPIC,
            10,
        )
        self.logger.info("Publisher for VBS and Thruster RPMs created.")

    def _set_zero_thruster_rpm(self, publisher):
        """Sets the thruster RPM to zero."""
        rpm_msg = ThrusterRPM()
        rpm_msg.rpm = 0
        publisher.publish(rpm_msg)

    def _set_zero_vbs(self):
        """Sets the VBS to zero."""
        vbs_msg = PercentStamped()
        vbs_msg.value = 0.
        self._vbs_pub.publish(vbs_msg)

    def execution_callback(self, goal_handle: ServerGoalHandle) -> ActionResult:
        """Primary execution callback where goal's are handled after acceptance.
        #TODO: Send CANCEL signal to all GOTOWAYPOINT actions!

        Args:
            goal_handle: handle to control server and add callbacks

        Returns:
            A populated ActionResult message
        """
        self.logger.info("Executing emergency abort goal...")
        result_msg = self.action_type.Result

        # Set the thruster RPM to zero
        self.publish_feedback(goal_handle, "Setting thruster1 RPM to zero...")
        self._set_zero_thruster_rpm(self._rpm1_pub)
        self.publish_feedback(goal_handle, "Setting thruster2 RPM to zero...")
        self._set_zero_thruster_rpm(self._rpm2_pub)
        # Set the VBS to zero
        self.publish_feedback(goal_handle, "Setting VBS to zero...")
        self._set_zero_vbs()
        goal_handle.succeed()

        result_msg.success = True
        return result_msg

    def goal_callback(self, goal_request: ActionType.Goal) -> GoalResponse:
        """Considers a goal validity and evaluates whether it should be accepted or not.

        Args:
            goal_request (ActionType.Goal): Goal message

        Returns:
            response: Either GoalResponse.Accept or GoalResponse.Reject

        """
        emergency_level = goal_request.level
        if emergency_level == EmergencyAbort.Goal.NO_EMERGENCY:
            self.logger.info("No emergency abort requested. Rejecting goal.")
            return GoalResponse.REJECT
        elif emergency_level == EmergencyAbort.Goal.EMERGENCY:
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
        self.logger.info(f"Published feedback: {message}")

def main(args=None):
    rclpy.init(args=args)
    node_name = "emergency_server"
    node = rclpy.node.Node(node_name)
    action_type = ActionType(EmergencyAbort)
    emergency_server = EmergencyServer(node, "emergency_abort", action_type)
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()
