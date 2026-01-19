#!/usr/bin/python

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.time import Time, Duration

import traceback

from geometry_msgs.msg import  PointStamped, PoseStamped
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PointStamped
from std_msgs.msg import Float32
from nav_msgs.msg import Odometry
from tf2_geometry_msgs import do_transform_pose_stamped
from tf2_ros import Buffer, TransformListener

from smarc_action_base.gentler_action_server import GentlerActionServer
from smarc_utilities.georef_utils import convert_latlon_to_utm
from dji_msgs.msg import Topics as DJITopics
from dji_msgs.msg import Links as DJILinks
from smarc_msgs.msg import Topics as SmarcTopics

from alars.alars_common import DroneState

class SearchAction():
    def __init__(self,
                 node: Node):
        self._node : Node = node

        self._node.declare_parameter('robot_name', 'M350')
        self._robot_name : str = self._node.get_parameter('robot_name').get_parameter_value().string_value
        self.MAP_FRAME : str = self._robot_name + '/' + DJILinks.MAP

        self._drone_state = DroneState(node, self._robot_name)

        self._node.declare_parameter('setpoint_threshold', 2.0)
        self.SETPOINT_THRESHOLD : float = self._node.get_parameter('setpoint_threshold').get_parameter_value().double_value

        self._node.declare_parameter('spiral_arm_distance', 5.0)
        self.SPIRAL_ARM_DISTANCE : float = self._node.get_parameter('spiral_arm_distance').get_parameter_value().double_value
        
        self._node.declare_parameter('min_setpoint_distance_to_drone', 2.0)
        self.MIN_SETPOINT_DISTANCE_TO_DRONE : float = self._node.get_parameter('min_setpoint_distance_to_drone').get_parameter_value().double_value

        self._node.declare_parameter('detection_freshness_threshold', 2.0)
        self.DETECTION_FRESHNESS_THRESHOLD : float = self._node.get_parameter('detection_freshness_threshold').get_parameter_value().double_value

        self._reset()
        
        self._setpoint_pub = self._node.create_publisher(
            msg_type = PoseStamped,
            topic = DJITopics.MOVE_TO_SETPOINT_TOPIC,
            qos_profile= 10)
        
        
        self._node.create_subscription(PointStamped, 
                                       DJITopics.ESTIMATED_AUV_TOPIC,
                                       self._auv_detection_cb,
                                       10)
        
        self._node.create_subscription(PointStamped,
                                       DJITopics.ESTIMATED_BUOY_TOPIC,
                                       self._buoy_detection_cb,
                                       10)

      
        self._as = GentlerActionServer(
            node,
            "alars_search",
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency = 10
        )
            
    def _reset(self):
        self._auv_detection : PointStamped = PointStamped()
        self._buoy_detection : PointStamped = PointStamped()
        self._spiral_progress : float = 0.0
        self._search_center_map : PoseStamped = PoseStamped()
        self._search_radius : float = 0.0
        self._radius_progress : float = -1.0
        self._current_setpoint : PoseStamped | None = None

    @property
    def _now_float(self) -> float:
        now_stamp = self._node.get_clock().now().to_msg()
        return now_stamp.sec + now_stamp.nanosec * 1e-9
    
    def _msg_is_older_than(self, msg, age_s: float) -> bool:
        if msg is None: return True
        if msg.header is None: return True
        if msg.header.stamp is None: return True
        if msg.header.stamp.sec == 0 and msg.header.stamp.nanosec == 0:
            return True
        return self._now_float - (msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9) > age_s

    def _loginfo(self, msg: str):
        self._node.get_logger().info(f"[SearchAction] {msg}")

    def _auv_detection_cb(self, msg: PointStamped):
        self._auv_detection = msg

    def _buoy_detection_cb(self, msg: PointStamped):
        self._buoy_detection = msg


    def _on_goal_received(self, goal_request: dict) -> bool:
        """
        Here you would typically validate the goal request
        Return True to accept the goal, False to reject it
        """ 
        self._reset()
        self._loginfo(f"Received goal request: {goal_request}")
        search_center_gp = GeoPoint()

        try:
            p = goal_request['search_position']
            search_center_gp.latitude = p['latitude']
            search_center_gp.longitude = p['longitude']
            search_center_gp.altitude = float(p['altitude'])
            self._search_radius = float(p['tolerance'])
            if self._search_radius <= 0:
                self._loginfo('Action goal had invalid radius(tolerance) value!')
                return False
            if search_center_gp.altitude <= 0:
                self._loginfo('Action goal had negative altitude value!')
                return False

        except:
            self._loginfo('Action goal could not be parsed?') 
            return False
        
        try:
            self._search_center_map = self._drone_state.convert_geopoint_to_map_pose_stamped(search_center_gp)
            
        except:
            self._loginfo('Could not transform search center into MAP frame!')
            traceback.print_exc()
            return False

        self._loginfo(f"Accepted goal request with search position: {self._search_center_map} and radius: {self._search_radius} m")
        return True
    

    def _on_cancel_received(self) -> bool:
        self._loginfo("Cancelled.")
        self._reset()
        return True


    def _prepare_loop(self) -> None:
        return
    

    def _loop_inner(self) -> bool|None:
        """
        Return True to indicate success, False for failure, or None to continue
        """
        # Sample the spiral until the point is X meters away from drone position
        def spiral(b: float, theta: float, a:float = 0.0) -> np.ndarray:
            r = a + b * theta
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            return np.array([x,y])
        
        if self._drone_state.drone_in_map is None:
            self._loginfo("No drone position received yet, cannot perform search...")
            return False
        
        # if both the auv and buoy are detected, we are done too
        auv_fresh = not self._msg_is_older_than(self._auv_detection, self.DETECTION_FRESHNESS_THRESHOLD)
        buoy_fresh = not self._msg_is_older_than(self._buoy_detection, self.DETECTION_FRESHNESS_THRESHOLD)
        if auv_fresh and buoy_fresh:
            self._loginfo("Both AUV and Buoy detected, finishing search action successfully.")
            return True
        

        # if there is a current setpoint, check if we are close enough to it
        if self._current_setpoint is not None:
            drone_pos = np.array([self._drone_state.drone_in_map.pose.position.x, self._drone_state.drone_in_map.pose.position.y])
            setpoint_pos = np.array([self._current_setpoint.pose.position.x, self._current_setpoint.pose.position.y])
            distance_to_setpoint = np.linalg.norm(drone_pos - setpoint_pos)
            if distance_to_setpoint < self.SETPOINT_THRESHOLD:
                self._loginfo(f"Reached current setpoint within {self.SETPOINT_THRESHOLD}m (distance: {distance_to_setpoint:.2f}m), computing next spiral point.")
                self._current_setpoint = None
            else:
                self._loginfo(f"Distance to active setpoint: {distance_to_setpoint:.2f}m.")
                if self._current_setpoint is None: return None
                if self._current_setpoint.header is None: return None
                self._current_setpoint.header.stamp = self._node.get_clock().now().to_msg()
                self._setpoint_pub.publish(self._current_setpoint)
                return None

        # either reached, or the first point
        # compute next spiral point
        drone_pos = np.array([self._drone_state.drone_in_map.pose.position.x, self._drone_state.drone_in_map.pose.position.y])
        search_center = np.array([self._search_center_map.pose.position.x, self._search_center_map.pose.position.y])
        

        # if the drone is far, at 0 progress, we'll break from the loop
        # if the drone is in-progress, this will advance the spiral until a far enough point is found
        # and if during advancement, we run out of spiral (exceeding search radius), we finish the action
        distance_to_drone = -1
        while distance_to_drone < self.MIN_SETPOINT_DISTANCE_TO_DRONE:
            dP = spiral(self.SPIRAL_ARM_DISTANCE, self._spiral_progress)
            self._radius_progress = np.linalg.norm(dP)
            self._loginfo(f"Spiral progress: {self._radius_progress:.2f}m / {self._search_radius:.2f}m, distance to drone: {distance_to_drone:.2f}m")
            if self._radius_progress > self._search_radius:
                self._loginfo("Completed search spiral, finishing action successfully.")
                return True
            spiral_point = search_center + dP
            distance_to_drone = np.linalg.norm(spiral_point - drone_pos)
            self._spiral_progress += 0.5

        # publish setpoint
        setpoint_msg = PoseStamped()
        setpoint_msg.header.frame_id = self.MAP_FRAME
        setpoint_msg.header.stamp = self._node.get_clock().now().to_msg()
        setpoint_msg.pose.position.x = float(spiral_point[0])
        setpoint_msg.pose.position.y = float(spiral_point[1])
        setpoint_msg.pose.position.z = self._search_center_map.pose.position.z
        setpoint_msg.pose.orientation.w = 1.0  # neutral orientation
        self._setpoint_pub.publish(setpoint_msg)
        self._current_setpoint = setpoint_msg
        self._loginfo(f"New setpoint: {setpoint_msg.pose.position}")
        return None 



    def _give_feedback(self) -> str:
        return f"Radius progress: {self._radius_progress:.2f}/{self._search_radius:.2f}m"


def main(args=None):
    rclpy.init(args=args)

    node = Node("alars_search_action_server")

    search_action = SearchAction(node)

    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)

    node.destroy_node()
    rclpy.shutdown()