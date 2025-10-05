#!/usr/bin/python3

import json
import sys

import rclpy
from rclpy.node import Node
from rclpy.time import Time, Duration
from rclpy.executors import MultiThreadedExecutor
from tf2_ros import Buffer, TransformListener
from tf2_geometry_msgs import do_transform_pose_stamped


import py_trees as pt
from py_trees.composites import Selector as Fallback
from py_trees.composites import Sequence, Parallel
from py_trees.decorators import Inverter
from py_trees.common import Status, ParallelPolicy
from py_trees.behaviours import Running, Success, Failure
from py_trees.trees import BehaviourTree

from std_msgs.msg import String, Float32
from geographic_msgs.msg import GeoPoint
from nav_msgs.msg import Odometry
from geometry_msgs.msg import  PointStamped, PoseStamped, Point


from smarc_msgs.action import BaseAction
from smarc_action_base.bt_action_client_action import A_ActionClient, FuncToStatus
from smarc_action_base.gentler_action_server import GentlerActionServer
from smarc_action_base.smarc_action_base import ActionClientState

from smarc_utilities.georef_utils import convert_latlon_to_utm, convert_utm_to_latlon


from smarc_msgs.msg import Topics as SmarcTopics
from dji_msgs.msg import Topics as DJITopics
from dji_msgs.msg import Links as DJILinks



class AlarsBT():
    def __init__(self,
                 node: Node):
            
            self._node : Node = node

            self._node.declare_parameter('robot_name', 'M350')
            self._robot_name : str = self._node.get_parameter('robot_name').get_parameter_value().string_value
            self.UTM_FRAME : str|None = None
            self.ODOM_FRAME : str = f"{self._robot_name}/{DJILinks.ODOM}"

            self._node.declare_parameter("RTH_altitude", 20.0)
            self.RTH_ALTITUDE : float = self._node.get_parameter("RTH_altitude").get_parameter_value().double_value

            self.raise_to_RTH_action = A_ActionClient(node, action_client_name='move_to', bt_action_name='raise_to_RTH')
            self.move_to_home_action = A_ActionClient(node, action_client_name='move_to', bt_action_name='move_to_home')
            self.search_action = A_ActionClient(node, 'alars_search')
            self.localize_action = A_ActionClient(node, 'alars_localize')
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


            self._tf_buffer = Buffer()
            self._tf_listener = TransformListener(self._tf_buffer, self._node, spin_thread=True)
                                                           

            self._home_geopoint : GeoPoint | None = None
            self._drone_geopoint : GeoPoint | None = None
            

            self._drone_in_odom : Point | None = None
            self._node.declare_parameter("home_radius", 1.0)
            self.HOME_RADIUS : float = self._node.get_parameter("home_radius").get_parameter_value().double_value
            self.drone_at_home : bool = False


            self._node.declare_parameter('max_detection_age', 5.0)
            self.MAX_DETECTION_AGE : float = self._node.get_parameter('max_detection_age').get_parameter_value().double_value
            self._auv_detection_camera : PointStamped | None = None
            self._auv_in_view : bool = False


            self._node.declare_parameter('loaded_weight_kg', 2.0)
            self.LOADED_WEIGHT_KG : float = self._node.get_parameter('loaded_weight_kg').get_parameter_value().double_value
            self._load_cell_weight : float|None = None
            self.captured_auv : bool = False


            self._auv_geopoint : GeoPoint | None = None
            self._buoy_geopoint : GeoPoint | None = None
            self.both_geopoints_known : bool = False


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
        try:
            self.search_action.set_goal(json.dumps(goal_request))
        except:
            self.log("Failed to parse goal request into json string.")
            return False
        
        if self._home_geopoint is None:
            if self.UTM_FRAME is None:
                self.log("UTM frame not known yet, cannot determine home geopoint.")
                return False
            odom_utm_tf = self._tf_buffer.lookup_transform(self.UTM_FRAME, self.ODOM_FRAME, Time(seconds=0), timeout=Duration(seconds=1))
            odom_origin = PoseStamped()
            odom_origin.header.frame_id = self.ODOM_FRAME
            odom_origin.header.stamp = Time(seconds=0).to_msg()
            odom_origin_in_utm = do_transform_pose_stamped(odom_origin, odom_utm_tf)
            self._home_geopoint = convert_utm_to_latlon(odom_origin_in_utm)

        return True


    def _on_cancel_received(self) -> bool:
        self.log("Received goal cancel request.")
        self.search_action.set_goal(None)
        return True
    

    def _prepare_loop(self) -> None:
        pass
    

    def _loop_inner(self) -> bool|None:
        if self._bt is None:
            self.log("Behaviour tree not set up yet!")
            return False
        
        if self._drone_geopoint is None:
            self.log("Haven't received drone geopoint yet!")
            return False
        
        if not self.search_action.got_goal:
            self.log("No valid search goal set, cannot proceed.")
            return False
        
        # Update states
        self.drone_at_home = self._drone_in_odom is not None and (self._drone_in_odom.x**2 + self._drone_in_odom.y**2 + self._drone_in_odom.z**2) < self.HOME_RADIUS**2
        self.captured_auv = self._load_cell_weight is not None and self._load_cell_weight >= self.LOADED_WEIGHT_KG
        
        self._auv_in_view = self._auv_detection_camera is not None and not self._msg_is_older_than(self._auv_detection_camera, self.MAX_DETECTION_AGE)
        self.both_geopoints_known = self._auv_geopoint is not None and self._buoy_geopoint is not None
        

        self._bt.tick()

        str = pt.display.ascii_tree(self._bt.root, show_status=True)
        str += "\n\nStates:"
        str += f"\n Drone at home: {self.drone_at_home}"
        str += f"\n Captured AUV (load cell): {self.captured_auv}({self._load_cell_weight})"

        str += "\n\n Known Places:"
        str += f"\n Home geopoint: {self._home_geopoint}"
        str += f"\n Drone geopoint: {self._drone_geopoint}"

        if str != self._prev_str:
            self.log("\n" + str)
            self._prev_str = str

        status = self._bt.root.status
        if status == Status.SUCCESS:
            self.log("We have ALARS'd")
            return True
        
        if status == Status.FAILURE:
            self.log("We have failed ALARS")
            return False

        return None
    
    def _set_move_to_goal_home(self) -> bool:
        if self._home_geopoint is None:
            self.log("Home geopoint not known, cannot set move_to home goal.")
            return False
        try:
            g = {"waypoint":{
                    "latitude": self._home_geopoint.latitude,
                    "longitude": self._home_geopoint.longitude,
                    "altitude": self.RTH_ALTITUDE
                    }
                 }
            self.move_to_home_action.set_goal(json.dumps(g))
            return True
        except:
            self.log("Failed to set move_to home goal.")
            return False
        

    def _set_move_to_goal_RTH_altitude(self) -> bool:
        if self._drone_geopoint is None:
            self.log("Drone geopoint not known, cannot set move_to RTH altitude goal.")
            return False
        try:
            g = {"waypoint":{
                    "latitude": self._drone_geopoint.latitude,
                    "longitude": self._drone_geopoint.longitude,
                    "altitude": self.RTH_ALTITUDE
                    }
                 }
            self.raise_to_RTH_action.set_goal(json.dumps(g))
            return True
        except:
            self.log("Failed to set move_to RTH altitude goal.")
            return False

    
       
    def setup(self) -> bool:
        self.log("Setting up actions...")

        self.move_to_home_action.setup()
        if self.move_to_home_action.state != ActionClientState.READY:
            self.log("move_to_action failed to setup! State: " + str(self.move_to_home_action.state))
            return False
        
        self.raise_to_RTH_action.setup()
        if self.raise_to_RTH_action.state != ActionClientState.READY:
            self.log("raise_to_RTH_action failed to setup! State: " + str(self.raise_to_RTH_action.state))
            return False
        
        self.search_action.setup()
        if self.search_action.state != ActionClientState.READY:
            self.log("search_action failed to setup! State: " + str(self.search_action.state))
            return False
        
        self.localize_action.setup()
        if self.localize_action.state != ActionClientState.READY:
            self.log("localize_action failed to setup! State: " + str(self.localize_action.state))
            return False
        
        self.recover_action.setup()
        if self.recover_action.state != ActionClientState.READY:
            self.log("recover_action failed to setup! State: " + str(self.recover_action.state))
            return False
        
        self.log("All actions setup successfully!")

        root = Fallback("FB ALARS Root", memory=False)
        self._bt = BehaviourTree(root)

        # First priority, are we done?
        done = Parallel("Done?", policy=ParallelPolicy.SuccessOnAll(synchronise=False))
        done.add_child(FuncToStatus("Got AUV?", lambda: self.captured_auv))
        done.add_child(FuncToStatus("Drone at home?", lambda: self.drone_at_home))
        root.add_child(done)

        # Go home if we have the AUV
        go_home = Sequence("Go Home with AUV", memory=False)
        go_home.add_child(FuncToStatus("Got AUV?", lambda: self.captured_auv))

        move_home = Sequence("Move Home", memory=True)
        move_home.add_child(FuncToStatus("Set goal: RTH Alt", self._set_move_to_goal_RTH_altitude))
        move_home.add_child(self.raise_to_RTH_action)
        move_home.add_child(FuncToStatus("Set goal: move to home", self._set_move_to_goal_home))
        move_home.add_child(self.move_to_home_action)

        go_home.add_child(move_home)
        root.add_child(go_home)


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