import abc
from argparse import Action
from typing import TypeVar

# ROS Imports
from rclpy.action import ActionClient, ActionServer, GoalResponse, CancelResponse
from rclpy.action.client import ClientGoalHandle
from rclpy.task import Future
from action_msgs.msg import GoalStatus
from rclpy.action.server import ServerGoalHandle
from rclpy.node import Node
from rclpy.type_support import check_for_type_support

from smarc_action_client.smarc_ros_types import ActionType, ActionFeedback, ActionGoal, ActionResult

class SMARCActionServer(abc.ABC):
    """Action Server base class

    Attributes: 
        action_type: 
    """
    def __init__(self, node: Node, action_name: str, action_type: ActionType, **kwargs):
        self._node = node
        self.action_type = action_type
        self._server = ActionServer(
            self._node,
            self.action_type.ros_type,
            action_name,
            self.execution_callback,
            **kwargs,
        )
        self._server.register_goal_callback(self.goal_callback)
        self._server.register_cancel_callback(self.cancel_callback)

    @abc.abstractmethod
    def execution_callback(self, goal_handle: ServerGoalHandle) -> ActionResult:
        """
        Primary execution callback.

        Here your action server will do most of the heavy lifting of computing whatever it needs to.

        Returns:
            result: A populated `self.action_type.Result` or more generically a ROS ActionType.Result()
        """
        pass

    @abc.abstractmethod
    def cancel_callback(self, goal_handle) -> CancelResponse:
        """
        Implement goal cancel logic in this method.

        Return:
            cancel_response: CancelResponse.ACCEPT or CancelResponse.REJECT
        """
        pass

    @abc.abstractmethod
    def goal_callback(self, goal_request) -> GoalResponse:
        """
        Implement goal acceptance or rejection logic in this callback method.

        Return:
            goal_response: GoalResponse.ACCEPT or GoalResponse.REJECT
        """
        pass


class SMARCActionClient(abc.ABC):
    def __init__(self, node: Node, action_name: str, action_type: ActionType, **kwargs):
        self._node = node
        self.action_type = action_type
        self._client: ActionClient = ActionClient(
            self._node,
            self.action_type.ros_type,
            action_name,
            **kwargs,
        )

    def _wrap_feedback_callback(self, feedback):
        """Simplifies feedback callback by extracting values from future."""
        feedback: ActionFeedback = feedback.feedback
        self.feedback_callback(feedback)

    def _wrap_result_callback(self, future: Future):
        """Simplifies result response callback extracting values from future."""
        result: ActionResult = future.result().result
        status: GoalStatus = future.result().status
        self.result_callback(result, status)

    def _wrap_goal_response_callback(self, future: Future):
        """Simplifies goal response callback extracting values from future."""
        self._goal_handle = future.result()
        self.goal_response_callback(self._goal_handle)

    @abc.abstractmethod
    def feedback_callback(self, feedback_msg: ActionFeedback):
        """Callback where feedback is provided from the action server."""
        pass

    @abc.abstractmethod
    def goal_response_callback(self, goal_handle: ClientGoalHandle):
        """Result when a goal is sent to the server."""
        pass

    @abc.abstractmethod
    def result_callback(self, result: ActionResult, status: GoalStatus):
        """Callback that is executed when a result comes back from the action server."""
        pass

    def get_result(self, goal_handle: ClientGoalHandle):
        """Send request to get result.

        Args:
            goal_handle: handle provided in `goal_response_callback`.

        """
        self._result_future = goal_handle.get_result_async()
        self._result_future.add_done_callback(self.result_callback)

    def send_goal(self, goal_msg: ActionGoal, server_timeout_sec=0.5):
        """Send goal to action server via an asynchronous callback.

        Establishes hook to feedback and goal callback for user behind the scenes

        Args:
            goal_msg: a filled out goal message to request the server to complete
        """
        self._client.wait_for_server(timeout_sec=server_timeout_sec)

        self._send_goal_future = self._client.send_goal_async(
            goal_msg, feedback_callback=self._wrap_feedback_callback
        )

        self._send_goal_future.add_done_callback(self._wrap_goal_response_callback)
