#!/usr/bin/python3

import json
import sys
from typing import Callable

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor


import py_trees as pt
from py_trees.composites import Selector as Fallback
from py_trees.composites import Sequence, Parallel
from py_trees.decorators import Inverter
from py_trees.common import Status, ParallelPolicy
from py_trees.trees import BehaviourTree

from std_msgs.msg import String, Float32, Int32
from geographic_msgs.msg import GeoPointStamped, GeoPoint
from geometry_msgs.msg import  PointStamped, PoseWithCovarianceStamped


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

            self.act_search =  A_ActionClient(node, 'alars_search',     'search')
            self.act_vulture = A_ActionClient(node, 'alars_follow_auv', 'vulture')
            self.act_recover = A_ActionClient(node, 'alars_recover',    'recover')
            self.act_deliver = A_ActionClient(node, 'move_to',          'deliver')

            self._node.declare_parameter('robot_name', 'M350')
            self._robot_name : str = self._node.get_parameter('robot_name').get_parameter_value().string_value
            self._drone_state = DroneState(node, self._robot_name)

            
            self._action_clients = [
                self.act_search,
                self.act_vulture,
                self.act_recover,
                self.act_deliver
            ]

            
            self._node.create_subscription(Float32,
                                           DJITopics.LOAD_CELL_WEIGHT_TOPIC,
                                           self._load_cell_weight_cb,
                                           10)
            
            self._node.create_subscription(Int32,
                                           DJITopics.LOAD_CELL_RAW_TOPIC,
                                           self._load_cell_raw_cb,
                                           10)


            self._node.declare_parameter('loaded_weight_kg', 1.2)
            self.LOADED_WEIGHT_KG : float = self._node.get_parameter('loaded_weight_kg').get_parameter_value().double_value
            self._load_cell_weight : float|None = None
            self._node.declare_parameter('loaded_loadcell_raw', 300000)
            self.LOADED_LOADCELL_RAW : int = self._node.get_parameter('loaded_loadcell_raw').get_parameter_value().integer_value
            self._load_cell_raw : int|None = None

            self._drone_geopoint : GeoPoint|None = None
            self._node.create_subscription(GeoPoint,
                                           SmarcTopics.POS_LATLON_TOPIC,
                                           self._pos_latlon_cb,
                                           10)

            self._reset_states()


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
                "delivery_position":
                {
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


    def _reset_states(self) -> None:
        self.delivered : bool = False
        self.captured_auv : bool = False
        self.found_once : bool = False
        self.retry_count : int = 0
        for ac in self._action_clients:
            ac.terminate(Status.INVALID)
        self.log("States reset")



    def log(self, msg: str):
        self._node.get_logger().info(msg)


    def _load_cell_weight_cb(self, msg: Float32): self._load_cell_weight = msg.data
    def _load_cell_raw_cb(self, msg: Int32): self._load_cell_raw = msg.data
    def _pos_latlon_cb(self, msg: GeoPoint): self._drone_geopoint = msg


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
        str += f"\n Fails: {self.retry_count}/{self._goal['num_retries']}"
        str += f"\n Found Once: {self.found_once}"

        if self._load_cell_weight is not None:
            str += f"\n Captured(kg): {self.captured_auv}({self._load_cell_weight:.2f})"
        elif self._load_cell_raw is not None:
            str += f"\n Captured(raw): {self.captured_auv}({self._load_cell_raw:.2f})"
        else:
            str += f"\n Captured AUV: {self.captured_auv} (none)"
        return str


    def _loop_inner(self) -> bool|None:
        if self._bt is None:
            self.log("Behaviour tree not set up, failing?!")
            return False
        

        # Update states
        # captured is latched, once we have it, we keep it
        # we use calibrated load cell if available, otherwise raw
        if self._load_cell_weight is not None:
            self.captured_auv = self.captured_auv or self._load_cell_weight >= self.LOADED_WEIGHT_KG
        elif self._load_cell_raw is not None:
            self.captured_auv = self.captured_auv or self._load_cell_raw >= self.LOADED_LOADCELL_RAW
        else:
            self.captured_auv = self.captured_auv or False

                    
        self._bt.tick()

        str = pt.display.ascii_tree(self._bt.root, show_status=True)
        str += self._status_str
        if str != self._prev_str:
            self.log("\n" + str)
            self._prev_str = str


        status = self._bt.root.status
        if self.delivered:
            self.log("We have ALARS'd")
            return True
        
        if status == Status.FAILURE:
            self.log("We have failed ALARS")
            return False

        return None
    
    def _set_goal_deliver(self) -> bool:
        try:
            g = { "waypoint": {
                    "latitude": self._goal["delivery_position"]["latitude"],
                    "longitude": self._goal["delivery_position"]["longitude"],
                    "altitude": self._goal["delivery_position"]["altitude"],
                    "tolerance": self._goal["delivery_position"]["tolerance"]
                    }   
                }
            self.act_deliver.set_goal(json.dumps(g))
            self.log("Set move_to delivery goal.")
            return True
        except:
            self.log("Failed to set move_to delivery goal.")
            return False


    
    def _set_goal_recover(self) -> bool:
        try:
            g = {
                "forward_distance": self._goal["forward_distance"],
                "forward_altitude": self._goal["forward_altitude"],
                "dipping_altitude": self._goal["dipping_altitude"],
                "raising_altitude": self._goal["raising_altitude"],
            }
            self.act_recover.set_goal(json.dumps(g))
            return True
        except:
            self.log("Failed to set recover goal.")
            return False



    

    def _set_goal_search(self) -> bool:
        if self.found_once:
            if self._drone_geopoint is None:
                self.log("Drone geopoint not known, cannot set search locally.")
                return False
            lat,lon = self._drone_geopoint.latitude, self._drone_geopoint.longitude
        else:
            lat = self._goal["search_position"]["latitude"]
            lon = self._goal["search_position"]["longitude"]
            self.found_once = True

        try:
            g = {"search_position": {
                "latitude": lat,
                "longitude": lon,
                "altitude": self._goal["search_position"]["altitude"],
                "tolerance": self._goal["search_position"]["tolerance"]
            }}
            self.act_search.set_goal(json.dumps(g))
            self.log("Set search goal.")
            return True
        except:
            self.log("Failed to set search goal.")
            return False
        

    def _set_delivered(self) -> bool:
        self.delivered = True
        return True
    



    def _add_failable_action(self,
                             parent: pt.composites.Composite,
                             action_client: A_ActionClient,
                             count_action_failure: bool = False,
                             post_condition: Callable[[], bool] | None = None,
                             count_condition_failure: bool = False) -> None:
        
        def _count_failure() -> bool:
            self.retry_count += 1
            self.log(f"Action failed, failure count: {self.retry_count}")
            return True
        
        if count_action_failure:
            attempt_action = Fallback(f"FB {action_client.name} attempt", memory=False)
            attempt_action.add_child(action_client)
            failure_counter = FuncToStatus(f"Count {action_client.name} failure", _count_failure)
            attempt_action.add_child(failure_counter)
        else:
            attempt_action = action_client

        if post_condition is not None:
            post_check = Sequence(f"SQ {action_client.name} post-condition", memory=False)
            post_check.add_child(attempt_action)

            if count_condition_failure:
                attempt_check = Fallback(f"FB {action_client.name} post-condition?", memory=False)
                attempt_check.add_child(FuncToStatus(f"Check {action_client.name} post-condition", post_condition))
                failure_counter2 = FuncToStatus(f"Count {action_client.name} post-condition failure", _count_failure)
                attempt_check.add_child(failure_counter2)
            else:
                attempt_check = FuncToStatus(f"Check {action_client.name} post-condition", post_condition)

            post_check.add_child(attempt_check)
            parent.add_child(post_check)
        else:            
            parent.add_child(attempt_action)


    

    def setup(self) -> bool:
        self.log("Setting up actions...")

        for ac in self._action_clients:
            ac.setup()
            if ac.state != ActionClientState.READY:
                self.log(f"{ac.name} failed to setup! State: {str(ac.state)}")
                return False
        
        self.log("All actions setup successfully!")

        root = Sequence("SQ Pre-mission checks", memory=False)
        self._bt = BehaviourTree(root)

        # check all the requirements to even _run_ a mission
        root.add_child(FuncToStatus("Retries remaining?", lambda: self.retry_count < int(self._goal["num_retries"])))
        
        mission = Fallback("FB ALARS Mission", memory=False)

        # First priority, are we done?
        done = Parallel("PR Done?", policy=ParallelPolicy.SuccessOnAll(synchronise=False))
        done.add_child(FuncToStatus("Got AUV?", lambda: self.captured_auv))
        done.add_child(FuncToStatus("Delivery done?", lambda: self.delivered))
        mission.add_child(done)

        # Go home if we have the AUV
        go_deliver = Sequence("SQ Deliver the AUV", memory=False)
        go_deliver.add_child(FuncToStatus("Got AUV?", lambda: self.captured_auv))
        deliver = Sequence("SQ Deliver", memory=True)
        deliver.add_child(FuncToStatus("Set goal: Move to delivery point", self._set_goal_deliver))
        deliver.add_child(self.act_deliver)
        deliver.add_child(FuncToStatus("Set delivery complete", self._set_delivered))

        go_deliver.add_child(deliver)
        mission.add_child(go_deliver)

        # Okay, we dont have the AUV yet, can we recover it?
        # We let the recover action handle the logic of whether we can actually recover or not
        # if it fails, we try to vulture until it can work
        # it works if both auv and buoy are known from camera processing
        recover = Sequence("SQ Recover AUV", memory=False)
        recover.add_child(FuncToStatus("Set goal: Recover", self._set_goal_recover))
        self._add_failable_action(recover,
                                  self.act_recover, 
                                  count_action_failure=False,
                                  post_condition=lambda: self.captured_auv,
                                  count_condition_failure=True)
        mission.add_child(recover)

        # Cant recover, can we vulture it?
        # This requires just the AUV to be known
        mission.add_child(self.act_vulture)

        # Cant vulture either, so we have to search for it.
        search = Sequence("SQ Search AUV", memory=True)
        search.add_child(FuncToStatus("Set search goal", self._set_goal_search))
        self._add_failable_action(search,
                                  self.act_search,
                                  count_action_failure=True,
                                  post_condition=None,
                                  count_condition_failure=False)
        mission.add_child(search)
        root.add_child(mission)

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