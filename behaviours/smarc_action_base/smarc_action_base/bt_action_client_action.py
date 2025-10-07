from py_trees.common import Status
from py_trees.behaviour import Behaviour
from rclpy.node import Node

from smarc_action_base.smarc_action_base import ActionClientState, ActionType
from smarc_msgs.action import BaseAction
from wasp_bt.bt.client import BTActionClient

from typing import Callable


class FuncToStatus(Behaviour):
    def __init__(self,
                 name: str,
                 func: Callable[[], bool|None],
                 fail_on_none: bool = True,
                 running_on_none: bool = False):
        super().__init__(name)
        self._func = func
        self._fail_on_none = fail_on_none
        self._running_on_none = running_on_none

        assert not (fail_on_none and running_on_none), "Cannot have both fail_on_none and running_on_none set to True."
        assert fail_on_none or running_on_none, "At least one of fail_on_none or running_on_none must be True."

    def update(self) -> Status:
        res = self._func()

        if res is None and self._fail_on_none: return Status.FAILURE
        if res is None and self._running_on_none: return Status.RUNNING
        
        if res: return Status.SUCCESS
        else: return Status.FAILURE

    

class A_ActionClient(Behaviour):
    def __init__(self,
                 node: Node,
                 action_client_name: str,
                 bt_action_name: str|None = None):
        
        if bt_action_name is None:
            bt_action_name = action_client_name
            
        super().__init__(f"A_ActionClient({bt_action_name})")
        
        self._ac = BTActionClient(
            node=node,
            action_name=action_client_name,
            action_type=ActionType(BaseAction)
        )

        self._cancel_response = None
        self._feedback_message = None
        self._goal_response = None
        self._result = None

        self._failure_states = [
            ActionClientState.DISCONNECTED,
            ActionClientState.ERROR,
            ActionClientState.REJECTED,
            ActionClientState.CANCELLED
        ]

        self._success_states = [
            ActionClientState.DONE
        ]

        self._running_states = [
            ActionClientState.SENT,
            ActionClientState.ACCEPTED,
            ActionClientState.RUNNING,
            ActionClientState.CANCELLING
        ]

        self._goal_str: str | None = None

    @property
    def state(self) -> ActionClientState:
        return self._ac.state

    @property
    def got_goal(self) -> bool:
        return self._goal_str is not None
    

    def setup(self, **kwargs) -> None:
        self._ac._setup(**kwargs)


    def set_goal(self, msg_str: str) -> None:
        # Give the goal message to send when the action is run
        # Should be a string of a JSON
        self._goal_str = msg_str

    def initialise(self) -> None: # this function is called when this Action is ticked for the first time
        if self._goal_str is None:
            self.feedback_message = "No goal string set! Use set_goal() to set a goal before ticking this Action."
            self.stop(Status.FAILURE)
            return
        
        # if previously running, get the client ready for a new run
        if self._ac.state in self._running_states:
            self.feedback_message = "Clearing previous goal and getting ready for a new run..."
            self._ac.cancel_goal(self._ac.cancel_callback)

        self.feedback_message = None
        

    def terminate(self, new_status: Status) -> None:
        if new_status == Status.INVALID:
            # Only try to cancel if the goal is still active
            if self._ac.state in self._running_states:
                self.feedback_message = "Preempted by higher priority in tree, cancelling goal"
                self._ac.cancel_goal(self._ac.cancel_callback)
            else:
                self.feedback_message = f"Preempted with Action Client state: {self._ac.state}"
   

        elif new_status == Status.SUCCESS:
            # action is finished proper. get ready for a next run.
            self.feedback_message = "Action finished. Ready for next run."

        if new_status == Status.FAILURE:
            # action did not finish proper.
            # should be handled by the rest of the tree
            self.feedback_message = f"Action failed. Action Client state: {self._ac.state}"


        # reset the client to ready state
        self._ac.get_ready()
        return



    def update(self) -> Status:
        s = self._ac.state

        # if it was cancelled, get the client ready for a new run for later
        if s == ActionClientState.CANCELLED:
            # change state to ready
            self.feedback_message = "Action cancelled. Ready for next run."
            self._ac.get_ready()    
            return Status.RUNNING

        if s == ActionClientState.READY:
            goal = BaseAction.Goal()
            goal.goal.data = self._goal_str 
            self._ac.send_goal(goal)
            self.feedback_message = f"Goal sent to action client:\n{self._goal_str}"
            return Status.RUNNING
        
        if s in self._running_states:
            self.feedback_message = self._ac.feedback_message
            return Status.RUNNING

        if s in self._failure_states:
            self.feedback_message = f"Action client in failure state: {s}. Check logs for more info."
            return Status.FAILURE
        
        if s in self._success_states:
            self.feedback_message = "Action client succeeded."
            return Status.SUCCESS
    

        self.feedback_message = f"Unexpected status:{s}?!"
        return Status.FAILURE