import traceback
from unicodedata import name

import numpy as np
import rclpy
from geodesy import utm
from rcl_interfaces.msg import ParameterDescriptor
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
from go_to_hydrobaticpoint.hydrobaticpoint_client import HydropointClient
from smarc_mission_msgs.action import EmergencyAbort, BaseAction
from smarc_msgs.msg import PercentStamped, ThrusterRPM, Topics
from sam_msgs.msg import Topics as SamTopics
from std_msgs.msg import String
from typing import TypeVar

T = TypeVar("T")


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
            Topics.WARA_PS_ACTION_SERVER_HB_TOPIC,
        )
        self.logger = node.get_logger()
        self.declare_parameters()
        self.declare_publishers()
        self.declare_messages()
        self.declare_action_clients()
        self.abort_active = False

        self.logger.set_level(rclpy.logging.LoggingSeverity.DEBUG)

    @staticmethod
    def _wrap_param_declare(
        node: Node, name: str, default_value: T, param_desc: str
    ) -> T:
        """Wrapped parameter declare to enable type completion for LSP.

        Additional None protection added.
        """
        param_value = node.declare_parameter(
            name, default_value, ParameterDescriptor(description=param_desc)
        ).value
        if param_value is None:
            err_str = "This function wraps param calls to prevent None types."
            err_str = "A None parameter was discoverd violation the assumption.\n"
            err_str += "Use node.declare_parameter and directly handle None types if you must\n"
            err_str += (
                "Rewriting this function to allow None types would defeat it's purpose."
            )
            raise ValueError(err_str)
        return param_value

    def declare_parameters(self):
        """Declares parameters for the node."""
        node = self._node
        self.robot_name = self._wrap_param_declare(
            node,
            "robot_name",
            "sam",
            "Name of the robot, used for logging and topic names",
        )
        self._pub_frequency = self._wrap_param_declare(
            node,
            "pub_frequency",
            10,
            "Frequency of the RPM, VBS and LCG publishers in Hz",
        )
        self._lcg_percentage = self._wrap_param_declare(
            node,
            "lcg_percentage",
            40.0,
            "% value to publish to the LCG publisher",
        )

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
        self._lcg_pub = node.create_publisher(
            PercentStamped,
            SamTopics.LCG_CMD_TOPIC,
            10,
        )
        self.logger.info("Publisher for VBS, Thruster RPMs, LGC created.")

    def declare_messages(self):
        """Declares messages needed for the publishers."""
        self._vbs_msg = PercentStamped()
        self._vbs_msg.value = 0.0
        self._rpm_msg = ThrusterRPM()
        self._rpm_msg.rpm = 0
        self._lcg_msg = PercentStamped()
        self._lcg_msg.value = self._lcg_percentage

    def declare_action_clients(self):
        """Declare action clients needed for the server.
        Note: assume corresponding action server is running, otherwise
        this function will block indefinitely...
        On emergencyAbort action, Send CANCEL signal to all action clients."""
        self.action_clients = []
        self.logger.info("Declaring action clients...")
        hydrobatic_client = HydropointClient(
            self._node,
            "go_to_hydropoint",
            ActionType(BaseAction),
        )
        self.action_clients.append(hydrobatic_client)
        self.logger.info(
            f"Declared {len(self.action_clients)} action clients: {self.action_clients}"
        )

    def publish_emergency_messages(self):
        """Publish VBS=0, RPMs=0, LCG=self._lcg_percentage"""
        self._vbs_pub.publish(self._vbs_msg)
        self._rpm1_pub.publish(self._rpm_msg)
        self._rpm2_pub.publish(self._rpm_msg)
        self._lcg_pub.publish(self._lcg_msg)

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

        self.cancel_actions()
        while self.abort_active:
            self.publish_emergency_messages()
            self.publish_feedback(
                goal_handle,
                f"Abort in progress. Setting VBS and RPM to 0. LCG to {self._lcg_percentage}...",
            )
            rate.sleep()
        rate.destroy()

        result_msg.success = True
        return result_msg

    def cancel_actions(self):
        """Send CANCEL signal to all self.action_clients.
        Assumes that all action clients implement the cancel_geopoint method."""
        for client in self.action_clients:
            try:
                response = client.cancel_geopoint()
                self.logger.info(
                    f"Cancel response from {client._action_name}: {response}\n"
                    f"Client state: {client.state}"
                )
            except Exception as e:
                self.logger.error(
                    f"Failed to cancel action {client.action_name}: {e}"
                )
                self.logger.debug(traceback.format_exc())

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
    action_type = ActionType(EmergencyAbort)
    emergency_server = EmergencyServer(node, "emergency_action", action_type)
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()
