#!/usr/bin/python

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.time import Time, Duration

import traceback

from geometry_msgs.msg import  PointStamped, PoseStamped, TwistStamped
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PointStamped
from nav_msgs.msg import Odometry


from tf2_geometry_msgs import do_transform_pose_stamped
from tf2_ros import Buffer, TransformListener

from smarc_action_base.gentler_action_server import GentlerActionServer
from smarc_utilities.georef_utils import convert_latlon_to_utm
from dji_msgs.msg import Topics as DJITopics
from dji_msgs.msg import Links as DJILinks
from smarc_msgs.msg import Topics as SmarcTopics

from alars.speed_names import SpeedNames
from alars.alars_common import DroneState


class MoveToAction():
    def __init__(self,
                 node: Node):
        self._node : Node = node

        self._node.declare_parameter('robot_name', 'M350')
        self._robot_name : str = self._node.get_parameter('robot_name').get_parameter_value().string_value
        self.BASE_FLAT_FRAME : str = self._robot_name + '/' + DJILinks.BASE_FLAT
        
        self._drone_state = DroneState(node, self._robot_name)

        self._goal_in_map : PoseStamped|None = None
        self._goal_tolerance : None | float = None
        self._node.declare_parameter('default_tolerance', 0.3)
        self._default_goal_tolerance : float = self._node.get_parameter('default_tolerance').get_parameter_value().double_value

        self._node.declare_parameter("speeds", [1.0, 3.0, 10.0])
        speeds = self._node.get_parameter("speeds").get_parameter_value().double_array_value
        self.SPEED_VALUES : dict[SpeedNames, float] = {
            SpeedNames.SLOW: speeds[0],
            SpeedNames.STANDARD: speeds[1],
            SpeedNames.FAST: speeds[2]
        }
        self._goal_speed : float | None = None

        # if set true, move vertically first, then horizontally always
        self._node.declare_parameter("vertical_first", True)
        self._VERTICAL_FIRST_MODE : bool = self._node.get_parameter("vertical_first").get_parameter_value().bool_value

        self._setpoint_pub = self._node.create_publisher(
            msg_type = TwistStamped,
            topic = DJITopics.VELOCITY_SETPOINT_TOPIC,
            qos_profile= 10)
        
        self._distance_remaining : None|float = None
    

        self._as = GentlerActionServer(
            node,
            "move_to",
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency = 50
        )

    @property
    def now_stamp(self):
        return self._node.get_clock().now().to_msg()
    
    @property
    def now_time(self):
        return self.now_stamp.sec + self.now_stamp.nanosec * 1e-9
    
    def log(self, msg: str):
        self._node.get_logger().info(msg)

    
    def _on_goal_received(self, goal_request: dict) -> bool:
        """
        This action takes a GeoPoint (with an optional tolerance field)
        """
        try:
            # first transform the latlon goal into UTM
            gp : GeoPoint = GeoPoint()
            gp.latitude = goal_request['waypoint']['latitude']
            gp.longitude = goal_request['waypoint']['longitude']
            gp.altitude = goal_request['waypoint']['altitude']
            
            self._goal_in_map = self._drone_state.geopoint_to_pose_stamped_map(gp)
            if self._goal_in_map is None:
                self._node.get_logger().error("Failed to transform goal from latlon to map frame")
                return False
            self._goal_in_base_flat = self._drone_state.pose_stamped_in_base_flat(self._goal_in_map)
            if self._goal_in_base_flat is None:
                self._node.get_logger().error("Failed to transform goal from map frame to base_flat frame")
                return False

            self._goal_tolerance = float(goal_request['waypoint']['tolerance']) if 'tolerance' in goal_request['waypoint'] else self._default_goal_tolerance
            speed_str = goal_request['speed'] if 'speed' in goal_request else 'standard'
            # test if speed_str is a float or one of the SpeedNames
            try:
                speed_value = float(speed_str)
            except:
                try:
                    speed_value = self.SPEED_VALUES[SpeedNames[speed_str.upper()]]
                except:
                    self.log(f"Unknown speed name: '{speed_str}', defaulting to STANDARD")
                    speed_value = self.SPEED_VALUES[SpeedNames.STANDARD]

            self._goal_speed = speed_value

            pos = self._goal_in_map.pose.position
            self.log(
                f"Received goal in map: [{pos.x:.2f},{pos.y:.2f},{pos.z:.2f}], tolerance: {self._goal_tolerance}, speed: {self._goal_speed}"
            )
            pos_base_flat = self._goal_in_base_flat.pose.position
            self.log(
                f"Same goal in base_flat: [{pos_base_flat.x:.2f},{pos_base_flat.y:.2f},{pos_base_flat.z:.2f}]"
            )
            return True
        
        except:
            self._node.get_logger().error("Failed to parse goal request")
            traceback.print_exc()
            return False

    def _on_cancel_received(self) -> bool:
        self.log("Cancel requested, stopping...")
        self._goal_in_map = None
        return True

    def _prepare_loop(self) -> None:
        self._distance_remaining = None
        return

    def _loop_inner(self) -> bool|None:
        self._goal_in_base_flat = self._drone_state.pose_stamped_in_base_flat(self._goal_in_map)

        if self._goal_in_base_flat is None:
            self.log("No goal set, failing...")
            return False
        
        if self._goal_tolerance is None:
            self.log("No goal tolerance set, failing...")
            return False

        if self._goal_speed is None:
            self.log("No goal speed set, failing...")
            return False
        
        if self._drone_state.drone_in_map is None:
            self.log("No drone position available yet, waiting...")
            return None

        goal_error = np.array([
            self._goal_in_base_flat.pose.position.x,
            self._goal_in_base_flat.pose.position.y,
            self._goal_in_base_flat.pose.position.z
        ])
        vertical_error = abs(goal_error[2])
        
        self.log(f"Goal error: [{goal_error[0]:.2f}, {goal_error[1]:.2f}, {goal_error[2]:.2f}], vertical first: {self._VERTICAL_FIRST_MODE}")
       
        # if vertical first mode, check if we need to move vertically first
        if self._VERTICAL_FIRST_MODE:
            if vertical_error > self._goal_tolerance:
                # need to move vertically first
                goal_error[0] = 0.0
                goal_error[1] = 0.0

        goal_error_mag = np.linalg.norm(goal_error)
        self._distance_remaining = float(goal_error_mag)

        # maybe we reached already
        if self._distance_remaining <= self._goal_tolerance:
            self.log(f"Reached goal within tolerance {self._goal_tolerance}m")
            setpoint = TwistStamped()
            setpoint.header.stamp = self.now_stamp
            setpoint.header.frame_id = self.BASE_FLAT_FRAME
            setpoint.twist.linear.x = 0.0
            setpoint.twist.linear.y = 0.0
            setpoint.twist.linear.z = 0.0
            setpoint.twist.angular.x = 0.0
            setpoint.twist.angular.y = 0.0
            setpoint.twist.angular.z = 0.0
            self._setpoint_pub.publish(setpoint)
            return True
        
        # otherwise, set the velocity setpoint
        # normalize the goal error to get the direction, then multiply by the speed
        goal_direction = goal_error / goal_error_mag
        velocity_setpoint = goal_direction * self._goal_speed

        # publish the setpoint
        setpoint = TwistStamped()
        setpoint.header.stamp = self.now_stamp
        setpoint.header.frame_id = self.BASE_FLAT_FRAME
        setpoint.twist.linear.x = velocity_setpoint[0]
        setpoint.twist.linear.y = velocity_setpoint[1]
        setpoint.twist.linear.z = velocity_setpoint[2]
        setpoint.twist.angular.x = 0.0
        setpoint.twist.angular.y = 0.0
        setpoint.twist.angular.z = 0.0
        self._setpoint_pub.publish(setpoint)

        return None

    def _give_feedback(self) -> str:
        if self._distance_remaining is not None:
            return f"Distance remaining: {self._distance_remaining:.2f} (tolerance: {self._goal_tolerance:.2f}m)"
        else:
            return "No distance remaining info"
        

def main(args=None):
    rclpy.init(args=args)
    node = Node("alars_move_to_action_server")
    move_to_action = MoveToAction(node)
    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)
    node.destroy_node()
    rclpy.shutdown()