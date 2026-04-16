#!/usr/bin/python

import numpy as np
import rclpy
import json
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.time import Time, Duration

import traceback

from floatsam_controllers.floatsam_common import FloatSam

from smarc_msgs.msg import FloatStamped
from floatsam_msgs.msg import Topics as FloatsamTopics
from geometry_msgs.msg import  PointStamped, PoseStamped
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PointStamped
from nav_msgs.msg import Odometry
from tf_transformations import euler_from_quaternion
from std_msgs.msg import String


from tf2_geometry_msgs import do_transform_pose_stamped
from tf2_ros import Buffer, TransformListener

from smarc_action_base.gentler_action_server import GentlerActionServer
import time

class MoveToPathActionFloatSam():
    def __init__(self,
                 node: Node):
        self._node : Node = node
        
        self._robot_name : str = self._node.get_parameter('robot_name').value

        self.declare_node_parameters()

        self.yaw_p_gain = str(self._node.get_parameter('yaw_p_gain').value)
        self.yaw_i_gain = str(self._node.get_parameter('yaw_i_gain').value)
        self.yaw_d_gain = str(self._node.get_parameter('yaw_d_gain').value)
        self.yaw_threshold = str(self._node.get_parameter('yaw_threshold').value)

        self.yawrate_p_gain = str(self._node.get_parameter('yawrate_p_gain').value)
        self.yawrate_i_gain = str(self._node.get_parameter('yawrate_i_gain').value)
        self.yawrate_d_gain = str(self._node.get_parameter('yawrate_d_gain').value)

        self.velocity_p_gain = str(self._node.get_parameter('velocity_p_gain').value)
        self.velocity_i_gain = str(self._node.get_parameter('velocity_i_gain').value)
        self.velocity_d_gain = str(self._node.get_parameter('velocity_d_gain').value)
        
        self._node.declare_parameter('use_sim', True)
        self._use_sim = self._node.get_parameter('use_sim').get_parameter_value().bool_value

        self.MAP_FRAME : str = self._robot_name + '/map'
        self._floatsam = FloatSam(node, self._robot_name, use_sim=self._use_sim)
        
        self._node.get_logger().info(f"FloatSam move_to server initialized for robot: {self._robot_name}")

        self._default_goal_tolerance = 1  
        self._default_speed_threshold = 5  
        self._decelerating : bool = False
        self._desired_speed : float = 0.0

        
        self._speed_override : float | None = None
        self._node.create_subscription(
            FloatStamped,
            FloatsamTopics.SPEED_OVERRIDE,
            self._speed_override_cb,
            10
        )

        self._yaw_reference_publisher = self._node.create_publisher(FloatStamped, FloatsamTopics.YAW_SETPOINT, 10)

        self._speed_reference_publisher = self._node.create_publisher(FloatStamped, FloatsamTopics.VELOCITY_SETPOINT, 10)

        self._as = GentlerActionServer(
            node,
            "move_path",
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency=10
        )

        self._captain_parameters_publisher = self._node.create_publisher(
            String, 
            'captain_parameters',
            10
        )

        self._initial_pos_deadline = int(self._node.get_clock().now().nanoseconds * 1e-9) + 5
        self._initial_pos_timer = self._node.create_timer(0.5, self._check_initial_position)

        self.index=0

    def _speed_override_cb(self, msg: FloatStamped) -> None:
        """Store the real-time speed published by behaviours.py.
        This overrides the speed that was sent in the action goal."""
        self._speed_override = float(msg.data)

    @property
    def effective_goal_speed(self) -> float:
        """The speed to use for this tick.
        Priority: real-time override topic > goal speed value > 2.0 m/s default.
        When the goal speed was set to 'override', only the topic value is used."""
        if self._speed_override is not None:
            return self._speed_override
        if self._goal_speed is not None:
            return self._goal_speed
        self._node.get_logger().warn("Speed override requested but no topic value received yet, holding 0.0")
        return 0.0

    @property
    def now_stamp(self):
        return self._node.get_clock().now().to_msg()
    
    @property
    def now_time(self):
        return self.now_stamp.sec + self.now_stamp.nanosec * 1e-9
    
    def log(self, msg: str):
        self._node.get_logger().info(msg)

    def _check_initial_position(self):
        """Timer callback: print the first floatsam position received from odom_gt (or timeout)."""
        if self._floatsam.floatsam_in_map is not None:
            p = self._floatsam.floatsam_in_map.pose.position
            self._node.get_logger().info(f"Floatsam position from odom_gt: [{p.x:.2f}, {p.y:.2f}, {p.z:.2f}]")
            try:
                self._initial_pos_timer.cancel()
            except Exception:
                pass
        else:
            now = int(self._node.get_clock().now().nanoseconds * 1e-9)
            if now > self._initial_pos_deadline:
                self._node.get_logger().warning("Timed out waiting for floatsam position from odom_gt")
                try:
                    self._initial_pos_timer.cancel()
                except Exception:
                    pass

    def _on_goal_received(self, goal_request: dict) -> bool:
        
        self._node.get_logger().info(f"Goal request received: {goal_request} piselli")

        try:
            try:
                self._goal_speed = goal_request.get('speed', 2.0)
                if self._goal_speed == "standard":
                    self._goal_speed = 2.0
                elif self._goal_speed == "slow":
                    self._goal_speed = 1.0
                elif self._goal_speed == "fast":
                    self._goal_speed = 5.0
                elif self._goal_speed == "override":
                    self._goal_speed = None
                    self._node.get_logger().info("Speed mode: override (using real-time topic value)")
                else:
                    self._goal_speed = float(self._goal_speed)
            except:
                self._node.get_logger().info(f"no valid speed, default to 2.0")
                self._goal_speed = 2.0

            self._goal_in_map=[]
            self._goal_tolerance=[]
            self.index = 0 

            waypoints = goal_request['waypoints']
            if not isinstance(waypoints, list):
                waypoints = [waypoints]

            self._constant_speed = bool(goal_request.get('constant_speed', False))
            self._node.get_logger().info(f"Constant speed mode: {self._constant_speed}")

            for i in range(len(waypoints)):
                self._node.get_logger().info(f"waypoint {i}: {waypoints[i]}")

                gp : GeoPoint = GeoPoint()
                gp.latitude = float(waypoints[i]['latitude'])
                gp.longitude = float(waypoints[i]['longitude'])

                pose_converted = self._floatsam.convert_geopoint_to_map_pose_stamped(gp)
                self._goal_in_map.append(pose_converted)

                tol = float(waypoints[i].get('tolerance', self._default_goal_tolerance))
                self._goal_tolerance.append(tol)

                pos = pose_converted.pose.position
                self._node.get_logger().info(f"Received goal in map: [{pos.x:.2f},{pos.y:.2f},{pos.z:.2f}], tolerance: {tol}, speed: {self._goal_speed}")

            return True
        
        except:
            self._node.get_logger().error("Failed to parse goal request")
            traceback.print_exc()
            return False


    def _on_cancel_received(self) -> bool:
        self._node.get_logger().info("Cancel requested, stopping...")
        self._goal_in_map = None
        return True

    def _prepare_loop(self) -> None:
        self._distance_remaining = None
        self._desired_speed = 0.0
        self._decelerating = False
        self.index = 0
        return

    def _loop_inner(self) -> bool|None:
        if self._goal_in_map is None or not self._goal_in_map:
            self._node.get_logger().info("No goal set, failing...")
            return False

        if self._floatsam.floatsam_in_map is None:
            self._node.get_logger().info("No floatsam position available yet, waiting...")
            return None
        
        if self.index >= len(self._goal_in_map):
            self._node.get_logger().info("All waypoints reached! SUCCESS.")
            return True 

        i = self.index

        goal_position = np.array([self._goal_in_map[i].pose.position.x,
                                  self._goal_in_map[i].pose.position.y])
        
        self_position = np.array([self._floatsam.floatsam_in_map.pose.position.x,
                                  self._floatsam.floatsam_in_map.pose.position.y])

        goal_error = goal_position - self_position
        goal_error_mag = np.linalg.norm(goal_error)
        self._distance_remaining = float(goal_error_mag)

        if self._distance_remaining <= self._goal_tolerance[i]:
            self._node.get_logger().info(f"Reached waypoint {i} within tolerance {self._goal_tolerance[i]}m")
            self.index += 1 
            return None 

        is_last_waypoint = (i == len(self._goal_in_map) - 1)

        if (self._distance_remaining <= self._default_speed_threshold) and is_last_waypoint and not self._constant_speed:
            self._desired_speed = (self._distance_remaining / self._default_speed_threshold) * self.effective_goal_speed
            self._decelerating = True
        else:
            self._desired_speed = self.effective_goal_speed
            self._decelerating = False
            
        error_heading = float(np.arctan2(goal_error[1], goal_error[0]))
        
        speed = float(self._desired_speed)
        
        yaw_msg = FloatStamped()
        speed_msg = FloatStamped()
        now = self._node.get_clock().now().to_msg()
        yaw_msg.header.stamp = now
        yaw_msg.data = error_heading
        speed_msg.header.stamp = now
        speed_msg.data = speed
        self._yaw_reference_publisher.publish(yaw_msg)
        self._speed_reference_publisher.publish(speed_msg)
        self._publish_captain_parametrs()

        return None

    def _give_feedback(self) -> str:
        if self._distance_remaining is not None and self._goal_in_map:
            safe_index = min(self.index, len(self._goal_in_map) - 1)
            feedback = {
                "wp_index": safe_index + 1,
                "wp_total": len(self._goal_in_map),
                "distance_remaining": round(self._distance_remaining, 3),
                "tolerance": round(self._goal_tolerance[safe_index], 3),
                "desired_speed": round(self._desired_speed, 3),
                "decelerating": self._decelerating,
            }
        else:
            feedback = {
                "decelerating": False,
                "desired_speed": 0.0,
            }
        return json.dumps(feedback)
        
    def declare_node_parameters(self) -> None:
        self._node.declare_parameter("_tolerance", 5.0)
        self._node.declare_parameter("reposition_tolerance", 0.5)
        self._node.declare_parameter("move_to_speed", 'fast')

        self._node.declare_parameter("yaw_p_gain", 0.3)
        self._node.declare_parameter("yaw_i_gain", 0.0)
        self._node.declare_parameter("yaw_d_gain", 0.1)
        self._node.declare_parameter("yaw_threshold", 0.5)

        self._node.declare_parameter("yawrate_p_gain", 300.0)
        self._node.declare_parameter("yawrate_i_gain", 0.0)
        self._node.declare_parameter("yawrate_d_gain", 30.0)

        self._node.declare_parameter("velocity_p_gain", 500.0)
        self._node.declare_parameter("velocity_i_gain", 10.0)
        self._node.declare_parameter("velocity_d_gain", 0.0)
        
    def _publish_captain_parametrs(self):
        """It publish the message containing the parameters for captain node"""
        parameters = {
            "yaw_p_gain" : self.yaw_p_gain,
            "yaw_i_gain" : self.yaw_i_gain,
            "yaw_d_gain" : self.yaw_d_gain,
            "yaw_threshold" : self.yaw_threshold,
            "yawrate_p_gain" : self.yawrate_p_gain,
            "yawrate_i_gain" : self.yawrate_i_gain,
            "yawrate_d_gain" : self.yaw_d_gain,
            "velocity_p_gain" : self.velocity_p_gain, 
            "velocity_i_gain" : self.velocity_i_gain, 
            "velocity_d_gain" : self.velocity_d_gain
        }
        msg = String()
        msg.data = json.dumps(parameters)
        self._captain_parameters_publisher.publish(msg)
        

def main(args=None):
    rclpy.init(args=args)

    node = Node("floatsam_move_to_path_action_server")
    node.declare_parameter('robot_name', 'floatsam_usv')

    move_to_path_action = MoveToPathActionFloatSam(node)
    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)
    node.destroy_node()
    rclpy.shutdown()
