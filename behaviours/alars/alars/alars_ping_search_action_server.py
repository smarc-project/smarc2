#!/usr/bin/python3

import json
import sys
from typing import Callable

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.duration import Duration
from rclpy.time import Time


import py_trees as pt
from py_trees.behaviour import Behaviour
from py_trees.composites import Selector as Fallback
from py_trees.composites import Sequence, Parallel
from py_trees.decorators import Inverter
from py_trees.common import Status, ParallelPolicy
from py_trees.trees import BehaviourTree

from std_msgs.msg import String, Float32, Int32
from geographic_msgs.msg import GeoPointStamped, GeoPoint
from geometry_msgs.msg import  PointStamped, PoseStamped, PoseWithCovarianceStamped

from tf2_ros import Buffer, TransformListener

from smarc_action_base.bt_action_client_action import A_ActionClient, FuncToStatus
from smarc_action_base.gentler_action_server import GentlerActionServer
from smarc_action_base.smarc_action_base import ActionClientState

from alars.alars_common import DroneState

from smarc_msgs.msg import Topics as SmarcTopics
from dji_msgs.msg import Topics as DJITopics



class AlarsPingSearch():
    def __init__(self,
                 node: Node):
            
            self._node : Node = node

            self.act_move_to_high = A_ActionClient(node, 'move_to', 'move_to_high')
            self.act_move_to_low = A_ActionClient(node, 'move_to', 'move_to_low')
            self.act_ping1 = A_ActionClient(node, 'smarc_modem_ping', 'ping1')
            self.act_ping2 = A_ActionClient(node, 'smarc_modem_ping', 'ping2')
            self.act_ping3 = A_ActionClient(node, 'smarc_modem_ping', 'ping3')
            self.act_move_to_estimate_ping = A_ActionClient(node, 'move_to', 'move_to_estimate_ping')

            self._node.declare_parameter('robot_name', 'M350')
            self._robot_name : str = self._node.get_parameter('robot_name').get_parameter_value().string_value
            self._drone_state = DroneState(node, self._robot_name)

            
            self._action_clients = [
                self.act_move_to_high,
                self.act_move_to_low,
                self.act_ping1,
                self.act_ping2,
                self.act_ping3,
                self.act_move_to_estimate_ping,
            ]


            self._drone_geopoint : GeoPoint|None = None
            self._node.create_subscription(GeoPoint,
                                           SmarcTopics.POS_LATLON_TOPIC,
                                           lambda msg: setattr(self, "_drone_geopoint", msg),
                                           10)

            self._auv_position_estimate_pings : GeoPointStamped|None = None
            self._node.create_subscription(GeoPointStamped,
                                           DJITopics.SUCCOR_ESTIMATE_TOPIC,
                                           lambda msg: setattr(self, "_auv_position_estimate_pings", msg),
                                           10)

            self._auv_position_estimate_visual : PoseWithCovarianceStamped|None = None
            self._node.create_subscription(PoseWithCovarianceStamped,
                                           DJITopics.PROJECTED_AUV_POSE_WITH_COV_TOPIC,
                                           lambda msg: setattr(self, "_auv_position_estimate_visual", msg),
                                           10)

            
            

            self._reset_states()


            self._bt : BehaviourTree|None = None
            self._prev_str : str = ""

            status_str_pub = self._node.create_publisher(String, 'alars_ping_search/status', 10)
            def publish_status():
                msg = String()
                msg.data = self._status_str
                status_str_pub.publish(msg)
            self._node.create_timer(1.0, publish_status)

            self._as = GentlerActionServer(
                node,
                'alars_ping_search',
                self._on_goal_received,
                self._on_cancel_received,
                self._prepare_loop,
                self._loop_inner,
                self._give_feedback,
                loop_frequency = 5
            )

            self._goal : dict = {
                "waypoints": [],
                "modem_to_ping": None,
                "modem_depth": None,
                "dipping_altitude": None,
                "max_pings": None
            }


    def _reset_states(self) -> None:
        self.ping_index : int = 0
        self.ping_count : int = 0
        self.done : bool = False
        self._auv_position_estimate_pings = None
        self._auv_position_estimate_visual = None

        for ac in self._action_clients:
            ac.terminate(Status.INVALID)
        self.log("States reset")

    
    def _loop_inner(self) -> bool|None:
        if self._bt is None:
            self.log("Behaviour tree not set up, failing?!")
            return False
                    
        self._bt.tick()

        str = "States:\n"
        # str = pt.display.ascii_tree(self._bt.root, show_status=True)
        str += self._status_str
        if str != self._prev_str:
            self.log("\n" + str)
            self._prev_str = str


        status = self._bt.root.status 
        if self.done:
            self.log("We have succeeded at ping search!")
            return True
        
        if status == Status.FAILURE:
            self.log("We have failed ping search")
            self._reset_states()
            return False

        return None


    def setup(self) -> bool:
        self.log("Setting up actions...")

        for ac in self._action_clients:
            ac.setup()
            if ac.state != ActionClientState.READY:
                self.log(f"{ac.name} failed to setup! State: {str(ac.state)}")
                return False
        
        self.log("All actions setup successfully!")


        do_go_to_estimate_ping = Sequence("SQ Go to ping estimate", memory=True, children=[
            FuncToStatus("Set goal", self._set_goal_move_to_estimate_ping),
            self.act_move_to_estimate_ping,
            FuncToStatus("Mark done", self._mark_done)
        ])

        go_to_estimate = self._post_pre_act(
            title = "Go to estimate",
            post_condition = lambda: self._auv_position_estimate_visual is not None,
            post_title = "Reached estimate",
            pre_condition = lambda: self._auv_position_estimate_pings is not None,
            pre_title = "Have AUV position estimate",
            act = do_go_to_estimate_ping
        )

        

        do_ping = Sequence("SQ Do ping", memory=True, children=[
            FuncToStatus("Set goal high", self._set_goal_move_to_ping_high),
            self.act_move_to_high,
            FuncToStatus("Set goal low", self._set_goal_move_to_ping_low),
            self.act_move_to_low,
            FuncToStatus("Do ping", self._set_goal_ping),
            pt.decorators.FailureIsSuccess(
                name="Some pings",
                child=Sequence("SQ Ping attempts", memory=False, children=[
                    self.act_ping1,
                    self.act_ping2,
                    self.act_ping3
                ])
            ),
            FuncToStatus("Count ping", self._count_ping)
        ])

        ping = self._post_pre_act(
            title = "Ping",
            post_condition = lambda: self._auv_position_estimate_pings is not None,
            post_title = "Have AUV position estimate",
            pre_condition = lambda: self.ping_count < self._goal['max_pings'],
            pre_title = "Have not exceeded max pings",
            act = do_ping
        )

        root = Fallback("FB Root", memory=False, children=[
            go_to_estimate,
            ping
        ])
       
        self._bt = BehaviourTree(root)

        return True        



    def log(self, msg: str):
        self._node.get_logger().info(msg)


    def _on_goal_received(self, goal_request: dict) -> bool:
        self.log(f"Received new goal request: {goal_request}")
        self._reset_states()

        # make sure all required fields are present
        try:
            if not (goal_request.keys() >= self._goal.keys()):
                self.log("Goal request missing required fields, rejecting.")
                self.log(f"Missing fields: {self._goal.keys() - goal_request.keys()}")
                return False
        except Exception as e:
            self.log(f"Exception while checking goal request fields: {e}")
            return False

        self.log("Goal request has all required fields, values will be checked by actions themselves.")
        self._goal = goal_request

        return True


    def _on_cancel_received(self) -> bool:
        self.log("Received goal cancel request.")
        self._reset_states()
        return True
    
    def _prepare_loop(self) -> None:
        self._reset_states()

    
    @property
    def _status_str(self) -> str:
        tip = self._bt.tip() if self._bt is not None else None
        if tip is None:
            tip_str = "-"
        else:
            tip_str = f"{tip.name}({tip.status}):{tip.feedback_message}"
        str = ""
        str += f"Tip: {tip_str}"
        str += f"\nPing idx: {self.ping_index+1}/{len(self._goal['waypoints'])}"
        str += f"\nPing count: {self.ping_count}/{self._goal['max_pings']}"
        str += f"\nAUV position estimate (pings): {self._auv_position_estimate_pings}"
        str += f"\nAUV position estimate (visual): {self._auv_position_estimate_visual}"
        return str
    


    def _set_goal(self, action_client: A_ActionClient, goal_dict: dict) -> bool:
        try:
            action_client.set_goal(json.dumps(goal_dict))
            self.log(f"Set goal for {action_client.name}.")
            return True
        except Exception as e:
            self.log(f"Failed to set goal for {action_client.name}: {e}")
            return False


    

    
    def _set_goal_move_to_ping_high(self) -> bool:
        if self.ping_index >= len(self._goal['waypoints']):
            self.log("Ping index out of range, cannot set goal.")
            return False
        
        ping_position = self._goal['waypoints'][self.ping_index]
        goal_dict = {
            "waypoint" : {
                "latitude": ping_position["latitude"],
                "longitude": ping_position["longitude"],
                "altitude": ping_position["altitude"],
                "tolerance": ping_position["tolerance"],
            },
            "speed":"fast"
        }
        return self._set_goal(self.act_move_to_high, goal_dict)


    def _set_goal_move_to_ping_low(self) -> bool:
        if self.ping_index >= len(self._goal['waypoints']):
            self.log("Ping index out of range, cannot set goal.")
            return False
        
        ping_position = self._goal['waypoints'][self.ping_index]
        goal_dict = {
            "waypoint" : {
                "latitude": ping_position["latitude"],
                "longitude": ping_position["longitude"],
                "altitude": self._goal["dipping_altitude"],
                "tolerance": ping_position["tolerance"],
            },
            "speed":"standard"
        }
        return self._set_goal(self.act_move_to_low, goal_dict)

    def _set_goal_move_to_estimate_ping(self) -> bool:
        if self._auv_position_estimate_pings is None:
            self.log("No AUV position estimate, cannot set goal.")
            return False
        
        gp = self._auv_position_estimate_pings.position
        ping_position = self._goal['waypoints'][0]
        alt = ping_position["altitude"] 
        goal_dict = {
            "waypoint" : {
                "latitude": gp.latitude,
                "longitude": gp.longitude,
                "altitude": alt,
                "tolerance": 1.0,
            },
            "speed":"fast"
        }
        return self._set_goal(self.act_move_to_estimate_ping, goal_dict)


    def _set_goal_ping(self) -> bool:
        goal_dict = {
            "mode":"ping",
            "modem_id": self._goal["modem_to_ping"],
            "depth": self._goal["modem_depth"],
            "retry_count": 3,
            "task_timeout": 30.0
        }
        self._set_goal(self.act_ping1, goal_dict)
        self._set_goal(self.act_ping2, goal_dict)
        return self._set_goal(self.act_ping3, goal_dict)


    def _count_ping(self) -> bool:
        self.ping_index += 1
        self.ping_index %= len(self._goal['waypoints'])
        self.ping_count += 1
        return True

    def _mark_done(self) -> bool:
        self.done = True
        return True
    

    def _post_pre_act(self,
                      title: str,
                      post_condition: Callable[[], bool], 
                      post_title: str,
                      pre_condition: Callable[[], bool], 
                      pre_title: str,
                      act: Behaviour) -> Fallback:
        """
        Pre-Condition, Action, Post-Condition subtree template.
        The action will only be attempted if the pre-condition is true.
        The subtree will only return success if the post-condition is true after the action.
        """
        subtree = Fallback(f"FB {title}", memory=False)
        subtree.add_child(FuncToStatus(post_title, post_condition))
        action_seq = Sequence(f"SQ Try <{act.name}>", memory=True)
        action_seq.add_child(FuncToStatus(pre_title, pre_condition))
        action_seq.add_child(act)
        subtree.add_child(action_seq)
        return subtree



    def _give_feedback(self) -> str:
        return self._status_str


def main():
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("alars_ping_search_action_server")
    alars_ping_search = AlarsPingSearch(node)
    setup_success = alars_ping_search.setup()

    if not setup_success:
        node.get_logger().error("Failed to setup alars_ping_search, shutting down.")
        rclpy.shutdown()
        return

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    rclpy.spin(node, executor=executor)
    rclpy.shutdown()


if __name__ == "__main__":
    main()