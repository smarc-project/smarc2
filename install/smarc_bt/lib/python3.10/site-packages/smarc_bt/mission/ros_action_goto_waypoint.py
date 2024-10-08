#!/usr/bin/python3


from rclpy.node import Node
from rclpy.action import ActionClient
from action_msgs.srv import CancelGoal

from .ros_waypoint import ROSWP
from .i_action_client import IActionClient, ActionClientState

from smarc_mission_msgs.action import GotoWaypoint
from smarc_mission_msgs.msg import Topics as MissionTopics
from smarc_mission_msgs.msg import GotoWaypoint as GotoWaypointMsg


class ROSGotoWaypoint(IActionClient):
    def __init__(self,
                 node: Node) -> None:
        self._node = node
        self._ac = ActionClient(node,
                                action_type=GotoWaypoint,
                                action_name=MissionTopics.GOTO_WP_ACTION)
        
        self._state = ActionClientState.DISCONNECTED

        self._send_goal_future = None
        self._goal_handle = None
        self._get_result_future = None
        self._feedback_message = "Only initialized"

        self._last_wp_pub = node.create_publisher(GotoWaypointMsg, MissionTopics.BT_LAST_WP_TOPIC, 10)

    
    @property
    def feedback_message(self) -> str:
        return f"{str(self._state)}:{self._feedback_message}"
    
    @property
    def state(self) -> ActionClientState:
        return self._state
    

    def setup(self, timeout:int=10) -> bool:
        self._log(f"Waiting for action server for {timeout} seconds")
        self._action_server_availble = self._ac.wait_for_server(timeout_sec=timeout)
        if not self._action_server_availble:
            self._log(f"Action server not available!")
            self._change_state(ActionClientState.DISCONNECTED)

        self._change_state(ActionClientState.READY)
        return True    
    

    def get_ready(self):
        self._change_state(ActionClientState.READY)


    def _log(self, s):
        self._node.get_logger().info(s)


    def _change_state(self, new_state:ActionClientState):
        if new_state == self.state: return
        self._log(f"GOTOWP: {self.state} -> {new_state}")
        self._state = new_state

    
    def _server_feedback_cb(self, fb_msg):
        """
        Once the goal is accepted, it might give feedback.
        Catch it here.
        """
        self._change_state(ActionClientState.RUNNING)
        fb = fb_msg.feedback
        self._feedback_message = f"GOTOWP FB:[{fb.feedback_message}, remaining:{fb.time_remaining.sec}]"


    def _goal_response_cb(self, future):
        """
        Goal is sent, it will respond with accept/reject.
        We catch that response here.
        """
        # could have been cancelled...
        if future is None: return

        self._goal_handle = future.result()
        if not self._goal_handle.accepted:
            self._feedback_message = "Goal rejected"
            self._change_state(ActionClientState.REJECTED)
            return
        
        self._feedback_message = "Goal accepted"
        self._change_state(ActionClientState.ACCEPTED)
        # The action is apparently running now.
        # We already registered the feedback callback when we called it first
        # Now we wanna know when it is DONE done.
        self._get_result_future = self._goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self._goal_result_cb)


    def _goal_result_cb(self, future):
        # could have been cancelled...
        if future is None: return
        if future.result() is None: return

        # The goal is complete. The server is done.
        # This is the final message from it.
        self._change_state(ActionClientState.DONE)
        result = future.result().result
        result_status = future.result().status
        self._result = result.reached_waypoint

    
    def send_goal(self, wp:ROSWP) -> bool:
        if self.state != ActionClientState.READY: return False

        goal_msg = GotoWaypoint.Goal()
        goal_msg.waypoint = wp.goto_wp
        
        self._log(f"Sending goal:{goal_msg}")

        self._send_goal_future = self._ac.send_goal_async(goal=goal_msg,
                                                          feedback_callback=self._server_feedback_cb)
        self._send_goal_future.add_done_callback(self._goal_response_cb)
        self._change_state(ActionClientState.SENT)

        self._last_wp_pub.publish(wp.goto_wp)


    def cancel_response_cb(self, future):
        # could have been cancelled...
        if future is None: return

        cancel_response = future.result()
        code = cancel_response.return_code
        if code == CancelGoal.Response.ERROR_REJECTED or \
           code == CancelGoal.Response.ERROR_UNKNOWN_GOAL_ID:
            # cancellation rejected, problem!
            self._feedback_message = f"Server failed to cancel! {cancel_response}"
            self._change_state(ActionClientState.ERROR) 
            return

        if code == CancelGoal.Response.ERROR_NONE or \
           code == CancelGoal.Response.ERROR_GOAL_TERMINATED:
            # accepted
            self._feedback_message = "Server is cancelled"
            self._change_state(ActionClientState.CANCELLED)
            return
            
        # anything else is a problem we did not foresee happening
        self._feedback_message = f"Unknown cancel response! {cancel_response}"
        self._change_state(ActionClientState.ERROR)


    def cancel_goal(self):
        if self._send_goal_future is not None:
            self._send_goal_future.cancel()
            self._send_goal_future = None
        
        if self._get_result_future is not None:
            self._get_result_future.cancel()
            self._get_result_future = None

        if self._goal_handle is not None:
            cancel_future = self._goal_handle.cancel_goal_async()
            cancel_future.add_done_callback(self.cancel_response_cb)
            self._change_state(ActionClientState.CANCELLING)
            self._feedback_message = "Sent cancel goal request to server"
        else:
            self._feedback_message = "No goal to cancel?"



        


