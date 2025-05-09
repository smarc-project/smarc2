import abc
import traceback
from functools import partial
import enum
from typing import Any

from action_msgs.msg import GoalStatus
from action_msgs.srv import CancelGoal

# ROS Imports
from rclpy.action import ActionClient, ActionServer, CancelResponse, GoalResponse
from rclpy.action.client import ClientGoalHandle
from rclpy.action.server import ServerGoalHandle
from rclpy.node import Node
from rclpy.task import Future
from rclpy.type_support import check_for_type_support
from rosidl_parser.definition import Action
from std_msgs.msg import String

from smarc_action_base.smarc_ros_types import ActionFeedback, ActionGoal, ActionResult


class ActionClientState(enum.Enum):
    DISCONNECTED = "DISCONNECTED"
    READY = "READY"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    RUNNING = "RUNNING"
    DONE = "DONE"
    CANCELLED = "CANCELLED"
    CANCELLING = "CANCELLING"
    ERROR = "ERROR"

    def __str__(self):
        return self.name


def _validate_state(input_state: Any) -> ActionClientState:
    """Validates if provided state is correct

    Args:
        input_state: value to change the state too

    Returns:
        Validated ActionClientState

    Raises:
        ValueError: error message to help debug
    """
    if isinstance(input_state, (ActionClientState,)):
        return input_state
    else:
        err_str = f"Expected type {type(ActionClientState).__name__}, but received {type(input_state).__name__}"
        raise ValueError(err_str)


def combine_ns_and_action(namespace: str, action_name: str):
    """Constructs heartbeat message with proper namespace.

        Some documentation that maybe useful: <https://design.ros2.org/articles/actions.html>
    Returns:
        heartbeat message prepended with namespace
    """
    if namespace == "/":
        namespace = ""
    msg_str = f"{namespace}/{action_name}"
    return msg_str


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
        heartbeat_topic: str,
        heartbeat_period: float = 1,
        **kwargs,
    ):
        """Action Server base class initialization function

        Args:
            node: ros2 node
            action_name: name of action client/server in ros
            action_type: ros2 message action type
            heartbeat_topic: Wara-PS heartbeat topic (can be found in smarc_msgs Topics.msg file)
            heartbeat_period: period in seconds of heartbeat timer
        """
        self._node: Node = node
        self.action_type = action_type
        self._action_name: str = action_name
        self._parsed_action_name: str | None = None
        self._server = ActionServer(
            self._node,
            self.action_type.ros_type,
            action_name,
            self.execution_callback,
            **kwargs,
        )
        self._heartbeat_topic = heartbeat_topic
        self._server.register_goal_callback(self._wrap_goal_callback)
        self._server.register_cancel_callback(self._wrap_cancel_callback)
        self._hb_timer = self._node.create_timer(heartbeat_period, self._heartbeat_cb)
        self._hb_pub = self._node.create_publisher(String, heartbeat_topic, 5)
        self._hb_msg = String()
        # TODO: NEED TO PARSE Namespace here
        self._hb_msg.data = self.parsed_action_name

    def _heartbeat_cb(self):
        """Sends out topic to Wara-PS on specified heartbeat timer cadence."""
        self._hb_pub.publish(self._hb_msg)

    @property
    def parsed_action_name(self):
        """Action name with namespace included."""
        if self._parsed_action_name is None:
            self._parsed_action_name = self._construct_hb_msg()
        return self._parsed_action_name

    def _construct_hb_msg(self) -> str:
        """Constructs heartbeat message with proper namespace.

            Some documentation that maybe useful: <https://design.ros2.org/articles/actions.html>
        Returns:
            heartbeat message prepended with namespace
        """
        namespace = self._node.get_namespace()
        msg_str = combine_ns_and_action(namespace, self._action_name)
        self._node.get_logger().info(
            f"Parsed out action server name for Wara-PS: {msg_str}"
        )
        return msg_str

    @abc.abstractmethod
    def execution_callback(self, goal_handle: ServerGoalHandle) -> ActionResult:
        """
        Primary execution callback.

        Here your action server will do most of the heavy lifting of computing whatever it needs to.

        Returns:
            result: A populated `self.action_type.Result` or more generically a ROS ActionType.Result()
        """
        pass

    def _wrap_cancel_callback(self, goal_handle) -> CancelResponse:
        """Wraps user callback in try and except to prevent failed cancellation requests due to exceptions."""
        try:
            return self.cancel_callback(goal_handle)
        except Exception as err:
            logger = self._node.get_logger()
            trace = traceback.format_exc()
            err_str = f"User provided callback failed with exception. See exception below:\n{err}\n"
            logger.error(err_str + trace)
            return CancelResponse.REJECT

    @abc.abstractmethod
    def cancel_callback(self, goal_handle) -> CancelResponse:
        """
        Implement goal cancel logic in this method.

        Return:
            cancel_response: CancelResponse.ACCEPT or CancelResponse.REJECT
        """
        pass

    def _wrap_goal_callback(self, goal_request) -> GoalResponse:
        """Wraps user callback in try and except to prevent failed goal requests not responding due to exceptions."""
        try:
            return self.goal_callback(goal_request)
        except Exception as err:
            logger = self._node.get_logger()
            trace = traceback.format_exc()
            err_str = f"User provided callback failed with exception. See exception below:\n{err}\n"
            logger.error(err_str + str(trace))
            return GoalResponse.REJECT

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
        _goal_handle: internal handle to goal to help register callbacks as user needs them
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
        self._action_name = action_name
        self._goal_handle: ClientGoalHandle | None = None
        self._state: ActionClientState = ActionClientState.DISCONNECTED
        self._setup()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, val):
        try:
            self._state = _validate_state(val)
            name = combine_ns_and_action(self._node.get_namespace(), self._action_name)
            self._node.get_logger().info(f"Client State ({name}) is {self._state}")
        except ValueError as err:
            self._state = ActionClientState.ERROR
            err_str = traceback.format_exc()
            self._node.get_logger().error(f"{err_str}")

    def _setup(self):
        server_status = False
        while not server_status:
            self._node.get_logger().info("Waiting for server to start.")
            server_status = self._client.wait_for_server(timeout_sec=1.0)
        self._node.get_logger().info("Server found.")
        self.state = ActionClientState.READY

    def get_goal_success(self) -> ActionClientState:
        """Success response for proper client state updating."""
        return ActionClientState.DONE

    def get_goal_error(self) -> ActionClientState:
        """Error response for proper client state updating."""
        return ActionClientState.ERROR

    def _wrap_feedback_callback(self, feedback):
        """Simplifies feedback callback by extracting values from future."""
        # setting state to running whenever feedback is being received
        self.state = ActionClientState.RUNNING
        feedback: ActionFeedback = feedback.feedback
        self.feedback_callback(feedback)

    def _wrap_result_callback(self, future: Future):
        """Simplifies result response callback extracting values from future."""
        result: ActionResult = future.result().result
        status: GoalStatus = future.result().status
        response = self.result_callback(result, status)
        valid_response = response is ActionClientState.DONE or response is ActionClientState.ERROR
        if valid_response:
            self.state = response
        else:
            err_str = "Provided return value from result callback must be either "
            err_str += f"{ActionClientState.DONE} or {ActionClientState.ERROR}. "
            err_str += f"Provided value is {response}"
            raise ValueError(err_str)

    def _wrap_goal_response_callback(self, future: Future):
        """Simplifies goal response callback extracting values from future.

        Does preemptive checking on goal success to setup future callbacks.
        """
        self._goal_handle = future.result()
        if self._goal_handle.accepted:
            self.state = ActionClientState.ACCEPTED
            self._get_result()
        else:
            self.state = ActionClientState.REJECTED
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
    def result_callback(
        self,
        result: ActionResult,
        status: GoalStatus,
    ) -> ActionClientState:
        """Implement callback to parse out the result of an action server task.

        Returns:
            Must return ActionClientState.DONE or ActionClientState.ERROR for higher level state management
            **Values can be accessed via `self.get_goal_success()` and `self.get_goal_error()`**
            Return values are checked at runtime.
        """
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
        # checking before user to see if goal got cancelled already (duplicate check but necessary)
        if len(result.goals_canceling) > 0:
            self.state = ActionClientState.CANCELLED
        user_callback(result)

    def cancel_goal(self, callback: callable):
        """Sends goal cancellation and setups up cancellation callback for caller.

        The callback function provided accepts the CancelGoal Response object.
            - Docs on Structure: https://docs.ros2.org/foxy/api/action_msgs/srv/CancelGoal.html
        """
        if self._goal_handle is not None:
            self.state = ActionClientState.CANCELLING
            future = self._goal_handle.cancel_goal_async()
            func = partial(self._wrap_cancel_callback, callback)
            future.add_done_callback(func)
        else:
            self._node.get_logger().debug(
                "No goal present to cancel. Skipping cancellation."
            )

    def send_goal(self, goal_msg: ActionGoal):
        """Send goal to action server via an asynchronous callback.

        Args:
            goal_msg: a populated ActionGoal message that will be sent to action server

        **Lower Level Details**
        Establishes hooks to `self.goal_response_callback` and `self.feedback_callback` for the user.

        Args:
            goal_msg: a filled out goal message to request the server to complete
        """

        self.state = ActionClientState.SENT
        self._send_goal_future = self._client.send_goal_async(
            goal_msg, feedback_callback=self._wrap_feedback_callback
        )

        self._send_goal_future.add_done_callback(self._wrap_goal_response_callback)
