"""A client for GentlerActionServer that you poll instead of subclass.

The server side of BaseAction is GentlerActionServer. This is the matching
client: it hides the four SMARCActionClient callbacks, keeps the last feedback
string, and lets a loop ask "what is up" with poll(). An optional timeout
cancels the goal from the client side when the server takes too long.

    client = GentlerActionClient(node, 'move_to', timeout_s=120.0)
    if client.server_alive() and client.send(json.dumps(goal)):
        while client.poll().running:
            ...
    client.get_ready()
"""

from dataclasses import dataclass

from action_msgs.msg import GoalStatus
from action_msgs.srv import CancelGoal
from rclpy.node import Node
from rclpy.time import Time
from smarc_msgs.action import BaseAction

from smarc_action_base.smarc_action_base import ActionClientState, ActionType, SMARCActionClient


@dataclass(frozen=True)
class ClientReport:
    """What poll() returns."""
    state: ActionClientState
    feedback: str
    elapsed_s: float
    timed_out: bool
    cancel_refused: bool = False

    @property
    def running(self) -> bool:
        return self.state in SMARCActionClient.RUNNING_STATES

    @property
    def finished(self) -> bool:
        """Nothing more will happen to this goal, for better or worse."""
        return self.state is ActionClientState.DONE or self.state in SMARCActionClient.FAILURE_STATES

    @property
    def succeeded(self) -> bool:
        return self.state is ActionClientState.DONE


class GentlerActionClient(SMARCActionClient):
    def __init__(self, node: Node, action_name: str, timeout_s: float | None = None):
        super().__init__(node, action_name, ActionType(BaseAction))
        self._timeout_s = timeout_s
        self.feedback_message = ''
        self._sent_at: Time | None = None
        self._timed_out = False
        self._cancel_pending = False
        self._cancel_refused = False
        self._cancel_open = False
        self._result_seen = False

    def server_alive(self, timeout_s: float = 1.0) -> bool:
        """One wait for the server. Moves an idle client to READY or DISCONNECTED.

        Wall time. This is looking for a process, and a paused sim clock would never expire it.
        """
        return self._setup(num_iters=1, timeout=timeout_s)

    def get_ready(self) -> None:
        """Forget the last goal so a new one can be sent."""
        self.feedback_message = ''
        self._sent_at = None
        self._timed_out = False
        self._cancel_pending = False
        self._cancel_refused = False
        self._cancel_open = False
        self._result_seen = False
        self.state = ActionClientState.READY

    def send(self, goal_json: str) -> bool:
        """Send a goal. False when the client is not READY."""
        if self.state is not ActionClientState.READY:
            self._logerr(f'Not sending a goal while {self.state}.')
            return False
        goal = self.action_type.Goal
        goal.goal.data = goal_json
        self.feedback_message = ''
        self._timed_out = False
        self._cancel_pending = False
        self._cancel_refused = False
        self._cancel_open = False
        self._result_seen = False
        self._goal_handle = None        # the previous goal's handle must not be cancelled by mistake
        self._sent_at = self._node.get_clock().now()
        self.send_goal(goal)
        return True

    def cancel(self) -> None:
        """Ask the server to stop. One request stays open until it is refused.

        Feedback sets the state back to RUNNING while that request is open, so
        a later ``cancel()`` returns instead of sending another. A refusal
        leaves the goal running and sets ``cancel_refused`` on the next poll.
        An accepted cancel stays CANCELLING until the result. A cancel that
        arrives before the server has answered the goal request (no goal
        handle yet; the first feedback can beat that answer) is kept and sent
        as soon as the goal is accepted.
        """
        if self._cancel_open:
            return
        if self.state not in self.RUNNING_STATES or self.state is ActionClientState.CANCELLING:
            return
        self._cancel_refused = False
        if self._goal_handle is None:
            self._cancel_pending = True
            return
        self._cancel_open = True
        self.cancel_goal(self._on_cancel_response)

    def _on_cancel_response(self, response) -> None:
        """A rejected cancel leaves the goal running. A late response is not this goal.

        The open flag stays set until a refusal, so feedback cannot send the
        cancel again. The base client marks an accepted cancel CANCELLED before
        the result; that is put back to CANCELLING until ``result_callback``.
        ``ERROR_GOAL_TERMINATED`` means the goal already ended.
        """
        if not self._cancel_open:
            return
        if response is not None and len(response.goals_canceling) > 0:
            if not self._result_seen:
                self.state = ActionClientState.CANCELLING
            return
        # Jazzy answers a user REJECT with ERROR_NONE and an empty list.
        # ERROR_GOAL_TERMINATED means the goal had already ended.
        refused = (
            CancelGoal.Response.ERROR_NONE,
            CancelGoal.Response.ERROR_REJECTED,
        )
        if response is None or response.return_code not in refused:
            return
        self._cancel_open = False
        self._cancel_refused = True
        if self.state is ActionClientState.CANCELLING:
            self.state = ActionClientState.RUNNING

    def poll(self) -> ClientReport:
        """Current state and feedback. Cancels the goal if the timeout has passed."""
        elapsed = 0.0 if self._sent_at is None else self._elapsed_s()
        if (self._timeout_s is not None and elapsed > self._timeout_s
                and self.state in self.RUNNING_STATES and not self._timed_out):
            self._logerr(f'No result after {elapsed:.1f} s, cancelling.')
            self._timed_out = True
            self.cancel()
        return ClientReport(
            self.state, self.feedback_message, elapsed, self._timed_out, self._cancel_refused)

    def _elapsed_s(self) -> float:
        return (self._node.get_clock().now() - self._sent_at).nanoseconds * 1e-9

    # SMARCActionClient callbacks. Users of this class do not see these.

    def feedback_callback(self, feedback_msg):
        self.feedback_message = feedback_msg.feedback.data

    def goal_response_callback(self, goal_handle):
        if self._cancel_pending:
            self._cancel_pending = False
            self.cancel()

    def result_callback(self, result, status) -> ActionClientState:
        self._result_seen = True
        if result.success:
            return ActionClientState.DONE
        if status == GoalStatus.STATUS_CANCELED:
            return ActionClientState.CANCELLED
        return ActionClientState.ERROR
