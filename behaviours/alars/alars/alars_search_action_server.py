#!/usr/bin/python
import rclpy
import json
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from geometry_msgs.msg import  PointStamped
from smarc_utilities.georef_utils import convert_latlon_to_utm
from alars_auv_search_planner.search_planner_controller import SearchPlannerController
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PointStamped
from collections.abc import Callable
from rclpy.action import CancelResponse, GoalResponse
from rclpy.action.server import ServerGoalHandle
from smarc_action_base.smarc_action_base import (
    ActionResult,
    ActionType,
    SMARCActionServer,
)
from smarc_mission_msgs.action import AlarsSearchAction
from smarc_msgs.msg import Topics as SmarcTopics
import inspect


class SearchPlannerAction():
    def __init__(self,
                 node: Node,
                 action_name: str):
        self._node = node
        self.spcontroller = SearchPlannerController()

        # Initialize the action server with the node and action name
        # Give it all the necessary callbacks
        self._as = GentlerActionServer(
            node,
            "alars_search",
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency = 1/self.spcontroller.model_params['grid_map.update.rate'] # loop frequency defined by grid map update frequency
        )

        # Subscribe from detection topic to know when to stop search
        self._node.create_subscription(PointStamped, 
                                       self.spcontroller.model_params["topics.sam_detection"],
                                       self._sam_detection_callback,
                                       10)

        # Initialize any necessary state for your specific action
        # These have nothing to do with the action server itself
        self._looped_for = 0
        self._loop_max = 2000
        self._radius = 0
        self._gps = None
        self.sam_position = None
        self.map_seen = 0

    def _on_goal_received(self, goal_request: dict) -> bool:
        """
        Here you would typically validate the goal request
        Return True to accept the goal, False to reject it
        """ 
        self._node.get_logger().info(f"Received goal request: {goal_request}")
        self._radius : float = goal_request["radius"]
        self._gps : GeoPoint = goal_request["gps"]

        def _assert_goal_request():
            if(
                isinstance(self._gps, GeoPoint) and
                isinstance(self._gps.latitude, float) and
                isinstance(self._gps.longitude, float) and
                isinstance(self._gps.altitude, float) and
                isinstance(self._radius, float) and
                self._radius > 0
            ):
                return True
            else: return False

        return _assert_goal_request()
    
    def _on_cancel_received(self) -> bool:
        """
        Here you would typically handle the cancel request
        Return True to accept the cancel, False to reject it
        """
        self._node.get_logger().warn("Received cancel request, cancelling search")
        self.spcontroller.init_done = False # flag to stop planner and grid map update
        return True

    
    def _prepare_loop(self) -> None:
        """
        Here you would typically set up any necessary state or resources
        This is run once before the loop starts, after you accept the goal
        """
        self._node.get_logger().info("Preparing loop for action execution")
        self._looped_for = 0

        # if activated by client, quadrotor doesn't perform initial movement (assigning purposes only)
        self.spcontroller.drone_init_pos = PointStamped()
        self.spcontroller.drone_init_pos.header.frame_id = self.spcontroller.model_params['frames.id.quadrotor_odom']      

        # get search radius (range) and altitude 
        self.spcontroller.grid_map.w = self.spcontroller.grid_map.h = 2*self._radius
        self.spcontroller.planner.flight_height = self.spcontroller.planner.grid_map.flight_height = self._gps.altitude
        GPS_ping_utm = convert_latlon_to_utm(self._gps)
        self.spcontroller.GPS_ping = self.spcontroller.planner.transform_point(GPS_ping_utm, self.spcontroller.model_params['frames.id.map'])

        # (re)initialize planner (including grid map)
        self.spcontroller.grid_map.GPS_ping = self.spcontroller.GPS_ping
        self.spcontroller.reinitialize_search()

    def _loop_inner(self) -> bool | None:
        """ 
        Here you would typically perform the main logic of the action
        Return True to indicate success, False for failure, or None to continue
        This is run after _prepare_loop call at "loop_frequency" Hz
        """
        self._looped_for += 1
        if self._looped_for >= self._loop_max :
            self._node.get_logger().warn("Reached maximum loop iterations, completing action")
            self.spcontroller.init_done = False # flag to stop planner and grid map update
            return False
        elif self.sam_position is not None:
            self._node.get_logger().warn("SAM was detected, finishing search")
            self.spcontroller.init_done = False # flag to stop planner and grid map update
            return True
        
        # Update planner and grid map ()
        try:
            self.map_seen = self.spcontroller.update_grid_map()
            self.spcontroller.update_path()
            return None
        except:
            self._node.get_logger().warn("Something failed in searching, finishing action")
            self.spcontroller.init_done = False # flag to stop planner and grid map update
            return False

        
    
    def _give_feedback(self) -> str:
        feedback = f"Action is in progress: {self._looped_for}/{self._loop_max} iter., {round(self.map_seen*100,2)} % of the map was seen"
        self._node.get_logger().info(feedback)
        # Here you would typically generate feedback for the action
        # This is run after each _loop_inner call
        return feedback
    
    def _sam_detection_callback(self, msg):
        self.sam_position = msg



class GentlerActionServer(SMARCActionServer):
    """
    Action server that wraps the AlarsSearchAction for gentler interactions.
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
            ActionType(AlarsSearchAction),
            SmarcTopics.WARA_PS_ACTION_SERVER_HB_TOPIC)
        
        self._on_goal_received :   Callable[[dict], bool]    = on_goal_received
        self._on_cancel_received : Callable[[], bool]        = on_cancel_received
        self._prepare_loop :       Callable[[], None]        = prepare_loop
        self._loop_inner :         Callable[[], bool | None] = loop_inner
        self._give_feedback :      Callable[[], str]         = give_feedback
        self._loop_frequency :     float                     = loop_frequency


    def goal_callback(self, goal_request) -> GoalResponse:
        return  GoalResponse.ACCEPT if self._on_goal_received({"gps": goal_request.gps, "radius": goal_request.radius}) else GoalResponse.REJECT


    def cancel_callback(self, goal_handle: ServerGoalHandle) -> CancelResponse:
        return  CancelResponse.ACCEPT if self._on_cancel_received() else CancelResponse.REJECT
    

    def execution_callback(self, goal_handle) -> ActionResult:
        result_msg = AlarsSearchAction.Result()
        feedback_msg = AlarsSearchAction.Feedback()

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


def main():
    rclpy.init()
    node = Node("search_auv_action_node")
    
    action = SearchPlannerAction(node, "alars_search")

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.add_node(action.spcontroller)
    executor.add_node(action.spcontroller.planner)
    executor.add_node(action.spcontroller.planner.grid_map)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down Search AUV Action server")
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()