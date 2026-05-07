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



class AlarsBT():
    def __init__(self,
                 node: Node):
            
            self._node : Node = node

            self.act_search_local =  A_ActionClient(node, 'alars_search', 'search_local')
            self.act_search_global = A_ActionClient(node, 'alars_search', 'search_global')
            self.act_vulture = A_ActionClient(node, 'alars_follow_auv', 'vulture')
            self.act_recover_bouy = A_ActionClient(node, 'alars_recover', 'recover_buoy')
            self.act_recover_no_bouy = A_ActionClient(node, 'alars_recover', 'recover_no_buoy')

            self._node.declare_parameter('robot_name', 'M350')
            self._robot_name : str = self._node.get_parameter('robot_name').get_parameter_value().string_value
            self._drone_state = DroneState(node, self._robot_name)

            
            self._action_clients = [
                self.act_search_local,
                self.act_search_global,
                self.act_vulture,
                self.act_recover_bouy,
                self.act_recover_no_bouy
            ]

            
            self._node.declare_parameter('loaded_weight_kg', 1.2)
            self.LOADED_WEIGHT_KG : float = self._node.get_parameter('loaded_weight_kg').get_parameter_value().double_value
            self._load_cell_weight : float|None = None
            def load_cell_weight_cb(msg: Float32):
                self._load_cell_weight = msg.data
            self._node.create_subscription(Float32,
                                           DJITopics.LOAD_CELL_WEIGHT_TOPIC,
                                           load_cell_weight_cb,
                                           10)


            self._drone_geopoint : GeoPoint|None = None
            self._node.create_subscription(GeoPoint,
                                           SmarcTopics.POS_LATLON_TOPIC,
                                           lambda msg: setattr(self, "_drone_geopoint", msg),
                                           10)
            
            self._node.declare_parameter('auv_esitmate_max_age', 5.0)
            self.AUV_ESTIMATE_MAX_AGE : float = self._node.get_parameter('auv_esitmate_max_age').get_parameter_value().double_value
            self._auv_position_estimate : PoseWithCovarianceStamped | None = None
            def auv_position_estimate_cb(msg: PoseWithCovarianceStamped):
                self._auv_position_estimate = msg
            self._node.create_subscription(PoseWithCovarianceStamped,
                                           DJITopics.PROJECTED_AUV_POSE_WITH_COV_TOPIC,
                                           auv_position_estimate_cb,
                                           10)
            
            self._node.declare_parameter('buoy_esitmate_max_age', 5.0)
            self.BUOY_ESTIMATE_MAX_AGE : float = self._node.get_parameter('buoy_esitmate_max_age').get_parameter_value().double_value
            self._buoy_position_estimate : PoseWithCovarianceStamped | None = None
            def buoy_position_estimate_cb(msg: PoseWithCovarianceStamped):
                self._buoy_position_estimate = msg
            self._node.create_subscription(PoseWithCovarianceStamped,
                                           DJITopics.PROJECTED_BUOY_POSE_WITH_COV_TOPIC,
                                           buoy_position_estimate_cb,
                                           10)

            self._reset_states()

            # once we have seen the auv, we want to
            # 1) go on top
            # 2) progressively search around it for the buoy
            self.VULTURE_RANGES = [0.0, 1.0, 3.0, 5.0]
            self.VULTURE_SPEED_DEG = 30.0
            self.VULTURE_TIMEOUT = 30.0
            self.RECOVER_WO_BUOY_RADIUS = .75
            self.LOCAL_SEARCH_RADIUS = 10.0


            self._bt : BehaviourTree|None = None
            self._prev_str : str = ""

            status_str_pub = self._node.create_publisher(String, 'alars_bt/status', 10)
            def publish_status():
                msg = String()
                msg.data = self._status_str
                status_str_pub.publish(msg)
            self._node.create_timer(1.0, publish_status)

            self._as = GentlerActionServer(
                node,
                'alars_bt',
                self._on_goal_received,
                self._on_cancel_received,
                self._prepare_loop,
                self._loop_inner,
                self._give_feedback,
                loop_frequency = 5
            )

            self._goal : dict = {
                "search_position": {
                    "latitude": None,
                    "longitude": None,
                    "altitude": None,
                    "tolerance": None
                },
                "forward_distance": None,
                "forward_altitude": None,
                "dipping_altitude": None,
                "raising_altitude": None,
                "num_retries": None
            }


    @property
    def _is_auv_hanging(self) -> bool:
        return self._load_cell_weight is not None and self._load_cell_weight >= self.LOADED_WEIGHT_KG
    
    @property
    def _is_auv_position_live(self) -> bool:
        return not self._drone_state.msg_is_older_than(self._auv_position_estimate, self.AUV_ESTIMATE_MAX_AGE)
    
    @property
    def _is_buoy_position_live(self) -> bool:
        return not self._drone_state.msg_is_older_than(self._buoy_position_estimate, self.BUOY_ESTIMATE_MAX_AGE)
     
    @property
    def _loadcell_kg_str(self) -> str:
        if self._load_cell_weight is not None:
            return f"{self._load_cell_weight:.2f} kg"
        else:
            return "???"


    def _reset_states(self) -> None:
        self._search_fail_count : int = 0
        self._recover_fail_count : int = 0
        self._vulture_timeout_count : int = 0
        self._recovery_success : bool = False
        for ac in self._action_clients:
            ac.terminate(Status.INVALID)
        self.log("States reset")



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
        str += "\nStates:"
        str += f"\n Failed search: {self._search_fail_count}/{self._goal['num_retries']}"
        str += f"\n Failed recover: {self._recover_fail_count}/{self._goal['num_retries']}"
        str += f"\n Vulture timeouts: {self._vulture_timeout_count}/{len(self.VULTURE_RANGES)}"
        str += f"\n AUV position live: {self._is_auv_position_live}"
        str += f"\n BUOY position live: {self._is_buoy_position_live}"
        str += f"\n AUV hanging: {self._is_auv_hanging}"
        str += f"\n Load cell weight: {self._loadcell_kg_str}"

        return str


    def _loop_inner(self) -> bool|None:
        if self._bt is None:
            self.log("Behaviour tree not set up, failing?!")
            return False
                    
        self._bt.tick()

        str = pt.display.ascii_tree(self._bt.root, show_status=True)
        # str += self._status_str
        if str != self._prev_str:
            self.log("\n" + str)
            self._prev_str = str


        status = self._bt.root.status
        if self._recovery_success:
            self.log("We have ALARS'd")
            self._reset_states()
            return True
        
        if status == Status.FAILURE:
            self.log("We have failed ALARS")
            self._reset_states()
            return False

        return None
    
    def _set_goal(self, action_client: A_ActionClient, goal_dict: dict) -> bool:
        try:
            action_client.set_goal(json.dumps(goal_dict))
            self.log(f"Set goal for {action_client.name}.")
            return True
        except Exception as e:
            self.log(f"Failed to set goal for {action_client.name}: {e}")
            return False
    
    def _set_goal_recover_with_buoy(self) -> bool:
        return self._set_goal(self.act_recover_bouy, {
            "forward_distance": self._goal["forward_distance"],
            "forward_altitude": self._goal["forward_altitude"],
            "dipping_altitude": self._goal["dipping_altitude"],
            "raising_altitude": self._goal["raising_altitude"],
            "no_buoy": False, 
            "no_buoy_radius": 0.0,
        })

    def _set_goal_recover_without_buoy(self) -> bool:
        return self._set_goal(self.act_recover_no_bouy, {
            "forward_distance": self._goal["forward_distance"],
            "forward_altitude": self._goal["forward_altitude"],
            "dipping_altitude": self._goal["dipping_altitude"],
            "raising_altitude": self._goal["raising_altitude"],
            "no_buoy": True, 
            "no_buoy_radius": self.RECOVER_WO_BUOY_RADIUS
        })

    
    def _set_goal_search_global(self) -> bool:
        return self._set_goal(self.act_search_global, {
            "search_position": {
                "latitude": self._goal["search_position"]["latitude"],
                "longitude": self._goal["search_position"]["longitude"],
                "altitude": self._goal["search_position"]["altitude"],
                "tolerance": self._goal["search_position"]["tolerance"]
            }
        })
    
    def _set_goal_search_local(self) -> bool:
        last_known_auv_geopoint = self._drone_state.pose_to_geopoint(self._auv_position_estimate) if self._auv_position_estimate is not None else None
        if last_known_auv_geopoint is None: return False

        return self._set_goal(self.act_search_local, {
            "search_position": {
                "latitude": last_known_auv_geopoint.latitude,
                "longitude": last_known_auv_geopoint.longitude,
                "altitude": self._goal["search_position"]["altitude"],
                "tolerance": self.LOCAL_SEARCH_RADIUS
            }
        })
    
    def _set_goal_vulture(self) -> bool:
        return self._set_goal(self.act_vulture, {
            "follow_altitude": self._goal["search_position"]["altitude"],
            "vulture_radius": self.VULTURE_RANGES[self._vulture_timeout_count],
            "vulture_speed_deg": self.VULTURE_SPEED_DEG,
            "timeout": self.VULTURE_TIMEOUT
        })
    
    def _count_vulture_timeout(self) -> bool:
        self._vulture_timeout_count += 1
        return True
    
    def _count_search_fail(self) -> bool:
        self._search_fail_count += 1
        return True
    
    def _count_recover_fail(self) -> bool:
        self._recover_fail_count += 1
        return True
    
    def _check_recovery_success(self) -> bool:
        self._recovery_success = self._is_auv_hanging
        return self._recovery_success

    

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

    

    def setup(self) -> bool:
        self.log("Setting up actions...")

        for ac in self._action_clients:
            ac.setup()
            if ac.state != ActionClientState.READY:
                self.log(f"{ac.name} failed to setup! State: {str(ac.state)}")
                return False
        
        self.log("All actions setup successfully!")


        do_recover_with_buoy = Sequence("SQ Do recover with buoy", memory=True, children=[
            FuncToStatus("Set goal", self._set_goal_recover_with_buoy),
            self.act_recover_bouy,
            FuncToStatus("Check success", self._check_recovery_success)
        ])

        recover_with_buoy = self._post_pre_act(
            title = "Recover with buoy",
            post_condition = lambda: self._recovery_success,
            post_title = "AUV is hanging",
            pre_condition = lambda: self._recover_fail_count < float(self._goal['num_retries']) and self._is_buoy_position_live and self._is_auv_position_live,
            pre_title = "Can retry, AUV position is live",
            act = Fallback("FB Recover, buoy", memory=True, children=[
                do_recover_with_buoy,
                FuncToStatus("Count fail", lambda: self._count_recover_fail())
            ])
        )

        do_recover_without_buoy = Sequence("SQ Do recover without buoy", memory=True, children=[
            FuncToStatus("Set goal", self._set_goal_recover_without_buoy),
            self.act_recover_no_bouy,
            FuncToStatus("Check success", self._check_recovery_success)
        ])

        recover_without_buoy = self._post_pre_act(
            title = "Recover without buoy",
            post_condition = lambda: self._recovery_success,
            post_title = "AUV is hanging",
            pre_condition = lambda: self._recover_fail_count < float(self._goal['num_retries']) and self._is_auv_position_live and self._vulture_timeout_count >= len(self.VULTURE_RANGES),
            pre_title = "Can retry, AUV position is live and vulture t/o cnt exceeded",
            act = Fallback("FB Recover, no buoy", memory=True, children=[
                do_recover_without_buoy,
                FuncToStatus("Count fail", lambda: self._count_recover_fail())
            ])
        )

        vulture = self._post_pre_act(
            title = "Vulture",
            post_condition = lambda: self._is_auv_position_live and self._is_buoy_position_live,
            post_title = "Buoy and AUV position live",
            pre_condition = lambda: self._is_auv_position_live and self._vulture_timeout_count < len(self.VULTURE_RANGES),
            pre_title = "AUV position live and vulture timeout count not exceeded",
            act = Sequence("SQ Vulture", memory=True, children=[
                FuncToStatus("Set goal", self._set_goal_vulture),
                self.act_vulture,
                FuncToStatus("Count timeout", lambda: self._count_vulture_timeout())
            ])
        )

        do_search_local = Sequence("SQ Do local search", memory=True, children=[
            FuncToStatus("Set goal", self._set_goal_search_local),
            self.act_search_local
        ])

        search_local = self._post_pre_act(
            title = "Search local",
            post_condition = lambda: self._is_auv_position_live,
            post_title= "AUV position live",
            pre_condition = lambda: self._auv_position_estimate is not None and self._search_fail_count < float(self._goal['num_retries']),
            pre_title = "Have seen AUV at least once and retries not exceeded",
            act = Fallback("FB Search local", memory=True, children=[
                do_search_local,
                FuncToStatus("Count fail", lambda: self._count_search_fail())
            ])
        )

        do_search_global = Sequence("SQ Do global search", memory=True, children=[
            FuncToStatus("Set goal", self._set_goal_search_global),
            self.act_search_global
        ])

        search_global = self._post_pre_act(
            title = "Search global",
            post_condition = lambda: self._is_auv_position_live,
            post_title= "AUV position live",
            pre_condition = lambda: self._search_fail_count < float(self._goal['num_retries']),
            pre_title = "Havent seen AUV before and retries not exceeded",
            act = Fallback("FB Search global", memory=True, children=[
                do_search_global,
                FuncToStatus("Count fail", lambda: self._count_search_fail())
            ])
        )

        root = Fallback("FB Root", memory=False, children=[
             recover_with_buoy,
             recover_without_buoy,
             vulture,
             search_local,
             search_global
        ])
       
        self._bt = BehaviourTree(root)

        return True        

    
    def _give_feedback(self) -> str:
        return self._status_str


def main():
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("alars_bt_node")
    alars_bt = AlarsBT(node)
    setup_success = alars_bt.setup()

    if not setup_success:
        node.get_logger().error("Failed to setup alars_bt, shutting down.")
        rclpy.shutdown()
        return

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    rclpy.spin(node, executor=executor)
    rclpy.shutdown()


if __name__ == "__main__":
    main()