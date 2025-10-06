#!/usr/bin/python3

import json
import sys

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor


import py_trees as pt
from py_trees.composites import Selector as Fallback
from py_trees.composites import Sequence, Parallel
from py_trees.decorators import Inverter
from py_trees.common import Status, ParallelPolicy
from py_trees.trees import BehaviourTree

from std_msgs.msg import String, Float32
from geographic_msgs.msg import GeoPoint
from nav_msgs.msg import Odometry
from geometry_msgs.msg import  PointStamped


from smarc_action_base.bt_action_client_action import A_ActionClient, FuncToStatus
from smarc_action_base.gentler_action_server import GentlerActionServer
from smarc_action_base.smarc_action_base import ActionClientState

from smarc_msgs.msg import Topics as SmarcTopics
from dji_msgs.msg import Topics as DJITopics



class AlarsBT():
    def __init__(self,
                 node: Node):
            
            self._node : Node = node

            self.raise_to_delivery_action = A_ActionClient(node, action_client_name='move_to', bt_action_name='raise_to_delivery')
            self.move_to_delivery_action = A_ActionClient(node, action_client_name='move_to', bt_action_name='move_to_delivery')
            self.lower_to_localize_action = A_ActionClient(node, action_client_name='move_to', bt_action_name='lower_to_localize')
            self.search_action = A_ActionClient(node, 'alars_search')
            self.localize_auv_action = A_ActionClient(node, action_client_name='alars_localize', bt_action_name='localize_auv')
            self.localize_buoy_action = A_ActionClient(node, action_client_name='alars_localize', bt_action_name='localize_buoy')
            self.recover_action = A_ActionClient(node, 'alars_recover')

            self._node.create_subscription(GeoPoint,
                                           SmarcTopics.POS_LATLON_TOPIC,
                                           self._pos_latlon_cb,
                                           10)
            
            self._node.create_subscription(Odometry,
                                           SmarcTopics.ODOM_TOPIC,
                                           self._odom_cb,
                                           10)
            
            self._node.create_subscription(String,
                                           DJITopics.LABELED_UTM_TOPIC,
                                           self._labeled_utm_cb,
                                           10)
            
            self._node.create_subscription(Float32,
                                           DJITopics.LOAD_CELL_WEIGHT_TOPIC,
                                           self._load_cell_weight_cb,
                                           10)
            
            self._node.create_subscription(PointStamped,
                                           DJITopics.ESTIMATED_AUV_TOPIC,
                                           self._auv_detection_cb,
                                           10)

                                                           
            self._drone_geopoint : GeoPoint | None = None


            self._node.declare_parameter('max_detection_age', 5.0)
            self.MAX_DETECTION_AGE : float = self._node.get_parameter('max_detection_age').get_parameter_value().double_value
            self._auv_detection_camera : PointStamped | None = None
            self.auv_in_view : bool = False


            self._node.declare_parameter('loaded_weight_kg', 2.0)
            self.LOADED_WEIGHT_KG : float = self._node.get_parameter('loaded_weight_kg').get_parameter_value().double_value
            self._load_cell_weight : float|None = None
            self.captured_auv : bool = False


            self._auv_geopoint : GeoPoint | None = None
            self._buoy_geopoint : GeoPoint | None = None
            self.both_geopoints_known : bool = False
            
            self.first_search_done : bool = False
            self.delivered : bool = False


            self._bt : BehaviourTree|None = None
            self._prev_str : str = ""

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
                "recover_min_height_above_water": None,
                "recover_swoop_vertical": None,
                "recover_swoop_horizontal": None,
                "recover_straight_before_rope": None,
                "recover_straight_distance": None,
                "recover_raise_horizontal": None,
                "recover_raise_vertical": None,
            }
                

    def log(self, msg: str):
        self._node.get_logger().info(msg)


    def _msg_is_older_than(self, msg, age_s: float) -> bool:
        now_stamp = self._node.get_clock().now().to_msg()
        return (now_stamp.sec - msg.header.stamp.sec) + (now_stamp.nanosec - msg.header.stamp.nanosec) * 1e-9 > age_s


    def _pos_latlon_cb(self, msg: GeoPoint):
        self._drone_geopoint = msg

    def _labeled_utm_cb(self, msg: String):
        self.UTM_FRAME = msg.data

    def _odom_cb(self, msg: Odometry):
        self._drone_in_odom = msg.pose.pose.position


    def _auv_detection_cb(self, msg: PointStamped):
        self._auv_detection_camera = msg


    def _load_cell_weight_cb(self, msg: Float32):
        self._load_cell_weight = msg.data


    def _on_goal_received(self, goal_request: dict) -> bool:
        self.log(f"Received new goal request: {goal_request}")

        # make sure all required fields are present
        try:
            if not (goal_request.keys() >= self._goal.keys()):
                self.log("Goal request missing required fields, rejecting.")
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
    
    def _reset_states(self):
        self.delivered = False
        self.captured_auv = False
        self.auv_in_view = False
        self.both_geopoints_known = False
        self.first_search_done = False
        self.search_action.set_goal(None)
        self.raise_to_delivery_action.set_goal(None)
        self.move_to_delivery_action.set_goal(None)
        self.lower_to_localize_action.set_goal(None)
        self.localize_auv_action.set_goal(None)
        self.localize_buoy_action.set_goal(None)
        self.recover_action.set_goal(None)
        self.log("States reset")


    def _prepare_loop(self) -> None:
        self._reset_states()
    

    def _loop_inner(self) -> bool|None:
        if self._bt is None:
            self.log("Behaviour tree not set up, failing?!")
            return False
        
        if self._drone_geopoint is None:
            self.log("Haven't received drone geopoint, failing...")
            return False
        
        # Update states
        # captured is latched, once we have it, we keep it
        self.captured_auv = self.captured_auv or self._load_cell_weight is not None and self._load_cell_weight >= self.LOADED_WEIGHT_KG
        self.auv_in_view = self._auv_detection_camera is not None and not self._msg_is_older_than(self._auv_detection_camera, self.MAX_DETECTION_AGE)
        self.both_geopoints_known = self._auv_geopoint is not None and self._buoy_geopoint is not None
        
        self._bt.tick()

        str = pt.display.ascii_tree(self._bt.root, show_status=True)
        str += "\n\nStates:"
        str += f"\n Delivered: {self.delivered}"
        str += f"\n Captured AUV (load cell): {self.captured_auv}({self._load_cell_weight})"
        str += f"\n AUV in view: {self.auv_in_view}"
        str += f"\n Both geopoints known: {self.both_geopoints_known}"
        str += f"\n First search done: {self.first_search_done}"
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
    
    def _set_move_to_goal_delivery(self) -> bool:
        try:
            g = { "waypoint": {
                    "latitude": self._goal["delivery_position"]["latitude"],
                    "longitude": self._goal["delivery_position"]["longitude"],
                    "altitude": float(self._goal["delivery_position"]["altitude"]),
                    "tolerance": float(self._goal["delivery_position"]["tolerance"])
                    }   
                }
            self.move_to_delivery_action.set_goal(json.dumps(g))
            return True
        except:
            self.log("Failed to set move_to delivery goal.")
            return False
        

    def _set_move_to_goal_delivery_altitude(self) -> bool:
        if self._drone_geopoint is None:
            self.log("Drone geopoint not known, cannot set move_to RTH altitude goal.")
            return False
        try:
            g = {"waypoint":{
                    "latitude": self._drone_geopoint.latitude,
                    "longitude": self._drone_geopoint.longitude,
                    "altitude": float(self._goal["delivery_position"]["altitude"]),
                    "tolerance": float(self._goal["delivery_position"]["tolerance"])
                }}
            self.raise_to_delivery_action.set_goal(json.dumps(g))
            return True
        except:
            self.log("Failed to set move_to RTH altitude goal.")
            return False
        
    def _set_goal_lower_to_localize(self) -> bool:
        if self._drone_geopoint is None:
            self.log("Drone geopoint not known, cannot set lower to localize goal.")
            return False
        try:
            g = {"waypoint":{
                    "latitude": self._drone_geopoint.latitude,
                    "longitude": self._drone_geopoint.longitude,
                    "altitude": float(self._goal["search_position"]["altitude"]),
                    "tolerance": 1.0
                }}
            self.lower_to_localize_action.set_goal(json.dumps(g))
            return True
        except:
            self.log("Failed to set lower to localize goal.")
            return False
    
    def _set_recover_goal(self) -> bool:
        if self._auv_geopoint is None or self._buoy_geopoint is None:
            self.log("AUV or buoy geopoint not known, cannot set recover goal.")
            return False
        try:
            g = {
                "object_position": {
                    "latitude": self._auv_geopoint.latitude,
                    "longitude": self._auv_geopoint.longitude,
                    "altitude": 0.0
                },
                "buoy_position": {
                    "latitude": self._buoy_geopoint.latitude,
                    "longitude": self._buoy_geopoint.longitude,
                    "altitude": 0.0
                },
                "min_height_above_water": self._goal["recover_min_height_above_water"],
                "swoop_vertical": self._goal["recover_swoop_vertical"],
                "swoop_horizontal": self._goal["recover_swoop_horizontal"],
                "straight_before_rope": self._goal["recover_straight_before_rope"],
                "straight_distance": self._goal["recover_straight_distance"],
                "raise_horizontal": self._goal["recover_raise_horizontal"],
                "raise_vertical": self._goal["recover_raise_vertical"]
            }
            self.recover_action.set_goal(json.dumps(g))
            return True
        except:
            self.log("Failed to set recover goal.")
            return False

    
    def _set_goal_localize_auv(self) -> bool:
        g = {"localize_auv": True, "localize_buoy": False}
        self.localize_auv_action.set_goal(json.dumps(g))
        return True
    
    def _set_goal_localize_buoy(self) -> bool:
        g = {"localize_auv": False, "localize_buoy": True}
        self.localize_buoy_action.set_goal(json.dumps(g))
        return True
    
    def _unset_auv_buoy_positions(self) -> bool:
        self._auv_geopoint = None
        self._buoy_geopoint = None
        return True

    def _set_auv_position_from_drone(self) -> bool:
        if self._drone_geopoint is None:
            self.log("Drone geopoint not known, cannot set AUV position.")
            return False
        self._auv_geopoint = GeoPoint()
        self._auv_geopoint.latitude = self._drone_geopoint.latitude
        self._auv_geopoint.longitude = self._drone_geopoint.longitude
        self._auv_geopoint.altitude = 0.0
        return True
    
    def _set_buoy_position(self) -> bool:
        if self._drone_geopoint is None:
            self.log("Drone geopoint not known, cannot set buoy position.")
            return False
        self._buoy_geopoint = GeoPoint()
        self._buoy_geopoint.latitude = self._drone_geopoint.latitude
        self._buoy_geopoint.longitude = self._drone_geopoint.longitude
        self._buoy_geopoint.altitude = 0.0
        return True
    
    def _set_goal_search_first(self) -> bool:
        self.log("Setting first search goal from given goal position.")
        try:
            g = {"search_position": {
                "latitude": self._goal["search_position"]["latitude"],
                "longitude": self._goal["search_position"]["longitude"],
                "altitude": self._goal["search_position"]["altitude"],
                "tolerance": self._goal["search_position"]["tolerance"]
            }}
            self.search_action.set_goal(json.dumps(g))
            return True
        except:
            self.log("Failed to set search goal.")
            return False
        
    def _set_goal_search_local(self) -> bool:
        self.log("Setting local search goal from current drone position.")
        if self._drone_geopoint is None:
            self.log("Drone geopoint not known, cannot set local search goal.")
            return False
        try:
            g = {"search_position": {
                    "latitude": self._drone_geopoint.latitude,
                    "longitude": self._drone_geopoint.longitude,
                    "altitude": self._goal["search_position"]["altitude"],
                    "tolerance": self._goal["search_position"]["tolerance"]
                }}
            self.search_action.set_goal(json.dumps(g))
            return True
        except:
            self.log("Failed to set local search goal.")
            return False
        

    def _set_delivered(self) -> bool:
        self.delivered = True
        return True


    def setup(self) -> bool:
        self.log("Setting up actions...")

        self.move_to_delivery_action.setup()
        if self.move_to_delivery_action.state != ActionClientState.READY:
            self.log("move_to_action failed to setup! State: " + str(self.move_to_delivery_action.state))
            return False
        
        self.raise_to_delivery_action.setup()
        if self.raise_to_delivery_action.state != ActionClientState.READY:
            self.log("raise_to_delivery_action failed to setup! State: " + str(self.raise_to_delivery_action.state))
            return False

        self.lower_to_localize_action.setup()
        if self.lower_to_localize_action.state != ActionClientState.READY:
            self.log("lower_to_localize_action failed to setup! State: " + str(self.lower_to_localize_action.state))
            return False

        self.search_action.setup()
        if self.search_action.state != ActionClientState.READY:
            self.log("search_action failed to setup! State: " + str(self.search_action.state))
            return False
        
        self.localize_auv_action.setup()
        if self.localize_auv_action.state != ActionClientState.READY:
            self.log("localize_auv_action failed to setup! State: " + str(self.localize_auv_action.state))
            return False
        
        self.localize_buoy_action.setup()
        if self.localize_buoy_action.state != ActionClientState.READY:
            self.log("localize_buoy_action failed to setup! State: " + str(self.localize_buoy_action.state))
            return False
        
        self.recover_action.setup()
        if self.recover_action.state != ActionClientState.READY:
            self.log("recover_action failed to setup! State: " + str(self.recover_action.state))
            return False
        
        self.log("All actions setup successfully!")

        root = Fallback("FB ALARS Root", memory=False)
        self._bt = BehaviourTree(root)

        # First priority, are we done?
        done = Parallel("PR Done?", policy=ParallelPolicy.SuccessOnAll(synchronise=False))
        done.add_child(FuncToStatus("Got AUV?", lambda: self.captured_auv))
        done.add_child(FuncToStatus("Delivery done?", lambda: self.delivered))
        root.add_child(done)

        # Go home if we have the AUV
        go_deliver = Sequence("SQ Deliver the AUV", memory=False)
        go_deliver.add_child(FuncToStatus("Got AUV?", lambda: self.captured_auv))

        deliver = Sequence("SQ Deliver", memory=True)
        deliver.add_child(FuncToStatus("Set goal: Delivery altitude", self._set_move_to_goal_delivery_altitude))
        deliver.add_child(self.raise_to_delivery_action)
        deliver.add_child(FuncToStatus("Set goal: Move to delivery", self._set_move_to_goal_delivery))
        deliver.add_child(self.move_to_delivery_action)
        deliver.add_child(FuncToStatus("Set delivery complete", self._set_delivered))

        go_deliver.add_child(deliver)
        root.add_child(go_deliver)

        # Okay, we dont have the AUV yet, if we know where it is, we can try to recover it
        recover = Sequence("SQ Recover AUV", memory=True)
        recover.add_child(FuncToStatus("Both geopoints known?", lambda: self.both_geopoints_known))
        recover.add_child(FuncToStatus("Set goal: Recover", self._set_recover_goal))
        recover.add_child(self.recover_action)
        recover.add_child(FuncToStatus("Forget geopoints", self._unset_auv_buoy_positions))
        root.add_child(recover)

        # So we dont exactly know where the auv and buoy are, but do we at least see the AUV so we can localize it?
        localize = Sequence("SQ Localize AUV", memory=True)
        localize.add_child(FuncToStatus("AUV in view?", lambda: self.auv_in_view))
        localize.add_child(FuncToStatus("Set goal: Lower to localize", self._set_goal_lower_to_localize))
        localize.add_child(self.lower_to_localize_action)
        localize.add_child(FuncToStatus("Set goal: Localize auv", self._set_goal_localize_auv))
        localize.add_child(self.localize_auv_action)
        localize.add_child(FuncToStatus("Set AUV Position", self._set_auv_position_from_drone))
        localize.add_child(FuncToStatus("Set goal: Localize buoy", self._set_goal_localize_buoy))
        localize.add_child(self.localize_buoy_action)
        localize.add_child(FuncToStatus("Set Buoy Position", self._set_buoy_position))
        root.add_child(localize)

        # We dont even see the thing... so we gotta search it
        # if this is the first time searching, we use the given search position
        # in the goal, otherwise we search from where we are
        # TODO limit number of search attempts as a goal param
        search = Sequence("SQ Search AUV", memory=True)
        search_goal = Fallback("FB Set Search Goal", memory=True)
        local_search = Sequence("SQ First Search", memory=True)
        local_search.add_child(FuncToStatus("First search done?", lambda: self.first_search_done))
        local_search.add_child(FuncToStatus("Set goal: Search AUV (local)", self._set_goal_search_local))
        search_goal.add_child(local_search)
        search_goal.add_child(FuncToStatus("Set goal: Search AUV (first)", self._set_goal_search_first))
        search.add_child(search_goal)
        search.add_child(self.search_action)
        root.add_child(search)

        return True        

    
    def _give_feedback(self) -> str:
        return "No feedback implemented yet."


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