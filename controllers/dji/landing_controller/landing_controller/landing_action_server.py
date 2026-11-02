"""Landing action lifecycle used by the landing manager node."""

import json
import math
from threading import Event
from typing import Callable, Optional

from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node
from rclpy.time import Time
from smarc_msgs.action import BaseAction
from smarc_msgs.msg import Topics as SmarcTopics
from std_msgs.msg import String


class LandingActionServer:
    """
    Handle goals, results, cancellation and feedback through FSM callbacks.
    """

    def __init__(
        self,
        node: Node,
        accept_landing: Callable[[], bool],
        start_landing: Callable[[str], None],
        abort_landing: Callable[[str], bool],
        finish_landing: Callable[[str], None],
        get_feedback: Callable[[], str],
        *, state_lock,
    ) -> None:
        self._node = node
        self._accept_landing = accept_landing
        self._start_landing = start_landing
        self._abort_landing = abort_landing
        self._finish_landing = finish_landing
        self._get_feedback = get_feedback
        self._state_lock = state_lock
        self._wake_event = Event()
        self._goal_handle = None
        self._goal_request = None
        self._pending = False
        self._result: Optional[bool] = None
        self._cancel_requested = False
        self._goal_started_at: Optional[Time] = None
        self._goal_timeout = float(node.get_parameter("default_timeout").value)
        if not math.isfinite(self._goal_timeout) or self._goal_timeout <= 0.0:
            raise ValueError("default_timeout must be finite and positive")

        action_name = node.get_parameter("action_name").value
        self._server = ActionServer(
            node, BaseAction, action_name, self._execute_landing,
            goal_callback=self._on_goal_received,
            cancel_callback=self._on_cancel_received,
            callback_group=ReentrantCallbackGroup(),
        )
        self._heartbeat_publisher = node.create_publisher(
            String, SmarcTopics.WARA_PS_ACTION_SERVER_HB_TOPIC, 5,
        )
        self._heartbeat_timer = node.create_timer(
            1.0, lambda: self._heartbeat_publisher.publish(
                String(data=node.resolve_topic_name(action_name)),
            ),
        )
        self._feedback_timer = node.create_timer(0.1, self._give_feedback)

    @property
    def pending(self) -> bool:
        """Include accepted goals that have not started or returned a result yet."""
        with self._state_lock:
            return self._pending

    def timed_out(self, now: Time) -> bool:
        with self._state_lock:
            if self._goal_started_at is None or not self._pending or self._result is not None:
                return False
            elapsed = max(0.0, (now - self._goal_started_at).nanoseconds * 1e-9)
            return elapsed >= self._goal_timeout

    def set_result(self, success: bool) -> None:
        """Record the FSM result once, before its landing state is reset."""
        with self._state_lock:
            if self._pending and self._result is None:
                self._result = success
                self._wake_event.set()

    def _on_goal_received(self, request: BaseAction.Goal) -> GoalResponse:
        try:
            goal = json.loads(request.goal.data)
            if not isinstance(goal, dict):
                raise ValueError("expected a JSON object")
            timeout = float(goal.get("timeout", self._node.get_parameter("default_timeout").value))
            if not math.isfinite(timeout) or timeout <= 0.0:
                raise ValueError("timeout must be finite and positive")
        except (TypeError, ValueError, OverflowError) as error:
            self._node.get_logger().info(f"Rejecting landing goal: {error}")
            return GoalResponse.REJECT

        with self._state_lock:
            if self._pending or not self._accept_landing():
                self._node.get_logger().info("Rejecting landing goal: landing is busy")
                return GoalResponse.REJECT

            # Reserve the attempt before execution starts, including against auto-start.
            self._pending = True
            self._goal_request = request
            self._result = None
            self._cancel_requested = False
            self._wake_event.clear()
            self._goal_timeout = timeout
            return GoalResponse.ACCEPT

    def _prepare_loop(self, goal_handle: ServerGoalHandle) -> None:
        with self._state_lock:
            self._goal_handle = goal_handle
            if not self._cancel_requested and not goal_handle.is_cancel_requested and self._result is None:
                self._start_landing("landing action requested")
                self._goal_started_at = self._node.get_clock().now()

    def _loop_inner(self) -> Optional[bool]:
        """Return None while running, True on success or False on failure."""
        with self._state_lock:
            return self._result

    def _execute_landing(self, goal_handle: ServerGoalHandle) -> BaseAction.Result:
        try:
            self._prepare_loop(goal_handle)
            while self._node.context.ok():
                with self._state_lock:
                    self._wake_event.clear()
                    if goal_handle.is_cancel_requested:
                        goal_handle.canceled()
                        return BaseAction.Result(success=False)
                    outcome = self._loop_inner()
                    # ROS marks the goal CANCELING after the cancel callback returns.
                    # Wait for that transition before reporting it as CANCELED.
                    if outcome is not None and not self._cancel_requested:
                        if outcome:
                            goal_handle.succeed()
                        else:
                            goal_handle.abort()
                        return BaseAction.Result(success=outcome)

                # Wake immediately on a result; poll at 10 Hz otherwise. Wall time
                # keeps cancellation responsive when the simulation clock is paused.
                self._wake_event.wait(timeout=0.1)
            return BaseAction.Result(success=False)
        finally:
            with self._state_lock:
                self._goal_handle = None
                self._goal_request = None
                self._pending = False
                self._result = None
                self._goal_started_at = None
                self._cancel_requested = False
                self._finish_landing("landing action complete")

    def _on_cancel_received(self, goal_handle: ServerGoalHandle) -> CancelResponse:
        with self._state_lock:
            # A delayed cancellation for an older goal must not affect a new one,
            # including the interval before the new execution callback starts.
            if (not self._pending or self._result is not None
                    or goal_handle.request is not self._goal_request):
                return CancelResponse.REJECT
            if self._goal_started_at is not None:
                if not self._abort_landing("landing action cancelled"):
                    return CancelResponse.REJECT
            # The action can finish now; independent timers complete climb and hold.
            self._cancel_requested = True
            self.set_result(False)
            return CancelResponse.ACCEPT

    def _give_feedback(self) -> None:
        with self._state_lock:
            if self._goal_handle is None or self._result is not None:
                return
            feedback = BaseAction.Feedback()
            feedback.feedback.data = self._get_feedback()
            self._goal_handle.publish_feedback(feedback)

    def destroy(self) -> None:
        """Release the action server, heartbeat publisher and feedback timers."""
        self._server.destroy()
        self._node.destroy_timer(self._heartbeat_timer)
        self._node.destroy_timer(self._feedback_timer)
        self._node.destroy_publisher(self._heartbeat_publisher)
