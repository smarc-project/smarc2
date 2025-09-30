import rclpy
import json

from collections.abc import Callable

from rclpy.action import CancelResponse, GoalResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.node import Node

from smarc_action_base.smarc_action_base import (
    ActionResult,
    ActionType,
    SMARCActionServer,
)
from smarc_msgs.action import BaseAction
from smarc_msgs.msg import Topics as SmarcTopics


class GentlerActionServer(SMARCActionServer):
    """Action server that wraps the BaseAction for gentler interactions.
    """
    def __init__(self,
                 node: Node,
                 action_name : str,
                 on_goal_received : Callable[[dict], bool],
                 on_cancel_received : Callable[[], bool],
                 prepare_loop : Callable[[], None],
                 loop_inner: Callable[[], bool | None],
                 give_feedback: Callable[[], str],
                 loop_frequency: float = 5.0):
        
        super().__init__(
            node,
            action_name,
            ActionType(BaseAction),
            SmarcTopics.WARA_PS_ACTION_SERVER_HB_TOPIC)
        
        self._on_goal_received :   Callable[[dict], bool]    = on_goal_received
        self._on_cancel_received : Callable[[], bool]        = on_cancel_received
        self._prepare_loop :       Callable[[], None]        = prepare_loop
        self._loop_inner :         Callable[[], bool | None] = loop_inner
        self._give_feedback :      Callable[[], str]         = give_feedback
        self._loop_frequency :     float                     = loop_frequency


    def goal_callback(self, goal_request) -> GoalResponse:
        return  GoalResponse.ACCEPT if self._on_goal_received(json.loads(goal_request.goal.data)) else GoalResponse.REJECT


    def cancel_callback(self, goal_handle: ServerGoalHandle) -> CancelResponse:
        return  CancelResponse.ACCEPT if self._on_cancel_received() else CancelResponse.REJECT
    

    def execution_callback(self, goal_handle) -> ActionResult:
        result_msg = BaseAction.Result()
        feedback_msg = BaseAction.Feedback()

        self._prepare_loop()

        rate = self._node.create_rate(self._loop_frequency)

        while rclpy.ok() and not goal_handle.is_cancel_requested:
            loop_status : bool|None = self._loop_inner()
            if loop_status is None:
                # loop continues, not successful or failed yet
                feedback_msg.feedback.data = self._give_feedback()
                goal_handle.publish_feedback(feedback_msg)
            else:
                result_msg.success = loop_status
                rate.destroy()
                if result_msg.success:
                    goal_handle.succeed()
                else:
                    goal_handle.abort()
                return result_msg
            
            rate.sleep()
        
        result_msg.success = False
        goal_handle.canceled()
        return result_msg


        
    