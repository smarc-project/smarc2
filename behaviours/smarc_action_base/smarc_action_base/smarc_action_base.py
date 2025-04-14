import abc
from functools import partial

from action_msgs.msg import GoalStatus
from action_msgs.srv import CancelGoal

# ROS Imports
from rclpy.action import ActionClient, ActionServer, CancelResponse, GoalResponse
from rclpy.action.client import ClientGoalHandle
from rclpy.action.server import ServerGoalHandle
from rclpy.node import Node
from rclpy.task import Future
from rclpy.type_support import check_for_type_support

from smarc_action_base.smarc_ros_types import ActionFeedback, ActionGoal, ActionResult


class ActionType:
    """Wrapper around ROS Action Type to provide easy dot completion.

    Attributes:
        Result: empty result message
        Feedback: empty feedback message
        Goal: empty goal message
    """

    def __init__(self, action_type):
        self._action_type = action_type
        self.validate_type()

    def validate_type(self):
        """Evaluates whether provided action type is a valid ROS action type.

        Raises:
            AttributeError: Provides additional context to user to help debug ROS error.
        """
        try:
            check_for_type_support(self._action_type)
        except AttributeError as err:
            err_str = "Provided action_type is not a valid ROS action type.\n"
            err_str += "Action types generally should be of type `from some_interface.action import MyAction"
            raise AttributeError(err_str) from err

    @property
    def ros_type(self):
        """Underlying ROS type.

        Returns:
            action: ROS action type
        """
        return self._action_type

    @property
    def Result(self) -> ActionResult:
        """Empty results message."""
        return self._action_type.Result()

    @property
    def Feedback(self) -> ActionFeedback:
        """Empty feedback message."""
        return self._action_type.Feedback()

    @property
    def Goal(self) -> ActionGoal:
        """Empty goal message."""
        return self._action_type.Goal()


class SMARCActionServer(abc.ABC):
    """Action Server base class

    Attributes:
        action_type: Action type for retrieving empty Goal, Feedback, and Result messages
    """

    def __init__(
        self,
        node: Node,
        action_name: str,
        action_type: ActionType,
        **kwargs,
    ):
        self._node: Node = node
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
    """Action client base class.


    Attributes:
        action_type: Action type for retrieving empty Goal, Feedback, and Result messages
        _goal_handle:
    """

    def __init__(self, node: Node, action_name: str, action_type: ActionType, **kwargs):
        self._node: Node = node
        self.action_type = action_type
        self._client: ActionClient = ActionClient(
            self._node,
            self.action_type.ros_type,
            action_name,
            **kwargs,
        )
        self._goal_handle: ClientGoalHandle | None = None

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
        """Simplifies goal response callback extracting values from future.

        Does preemptive checking on goal success to setup future callbacks.
        """
        self._goal_handle = future.result()
        if self._goal_handle.accepted:
            self._get_result()
        # calling inheritors function
        self.goal_response_callback(self._goal_handle)

    @abc.abstractmethod
    def feedback_callback(self, feedback_msg: ActionFeedback):
        """Implement feedback logic for each action server feedback message."""
        pass

    @abc.abstractmethod
    def goal_response_callback(self, goal_handle: ClientGoalHandle):
        """Implement handing of two goal scenarios.

        GoalResponse.ACCEPT: acceptance of the goal by action server
        GoalResponse.REJECT: rejection of the goal by action server
        """
        pass

    @abc.abstractmethod
    def result_callback(self, result: ActionResult, status: GoalStatus):
        """Implement callback to parse out the result of an action server task."""
        pass

    def _get_result(self):
        """Send request to get result.

        Args:
            goal_handle: handle provided in `goal_response_callback`.

        """
        self._result_future = self._goal_handle.get_result_async()
        self._result_future.add_done_callback(self._wrap_result_callback)

    def _wrap_cancel_callback(self, user_callback: callable, future: Future):
        """Wrapper for user's provided callback function.

        Formulated based off buried ROS documentation.
            ROS Buried Docs:
                Response from CancelGoal is a Cancel Response with fileds:
                    - goals_canceling
                    - goal_info

        Sources:
        - https://github.com/ros2/examples/blob/master/rclpy/actions/minimal_action_client/examples_rclpy_minimal_action_client/client_cancel.py
        - https://docs.ros2.org/foxy/api/action_msgs/srv/CancelGoal.html
        """
        result: ActionResult = future.result()
        user_callback(result)

    def cancel_goal(self, callback: callable):
        """Sends goal cancellation and setups up cancellation callback for caller.

        The callback function provided accepts the CancelGoal Response object.
            - Docs on Structure: https://docs.ros2.org/foxy/api/action_msgs/srv/CancelGoal.html
        """
        if self._goal_handle is not None:
            future = self._goal_handle.cancel_goal_async()
            func = partial(self._wrap_cancel_callback, callback)
            future.add_done_callback(func)
        else:
            self._node.get_logger().debug(
                "No goal present to cancel. Skipping cancellation."
            )

    def send_goal(self, goal_msg: ActionGoal, server_timeout_sec: float = 0.5):
        """Send goal to action server via an asynchronous callback.

        Args:
            server_timeout_sec: Duration for which the client should wait for the action server to be ready.
            goal_msg: a populated ActionGoal message that will be sent to action server

        **Lower Level Details**
        Establishes hooks to `self.goal_response_callback` and `self.feedback_callback` for the user.

        Args:
            goal_msg: a filled out goal message to request the server to complete
        """
        self._client.wait_for_server(timeout_sec=server_timeout_sec)

        self._send_goal_future = self._client.send_goal_async(
            goal_msg, feedback_callback=self._wrap_feedback_callback
        )

        self._send_goal_future.add_done_callback(self._wrap_goal_response_callback)
