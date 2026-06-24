#! /usr/bin/env python3

import math
import rclpy
import time
import numpy as np
from rclpy.node import Node
from rclpy.time import Duration, Time
from std_msgs.msg import String, Float32
from geometry_msgs.msg import TwistStamped
from rosgraph_msgs.msg import Clock
from rclpy.executors import MultiThreadedExecutor
from nav_msgs.msg import Odometry, OccupancyGrid
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import PoseStamped, PointStamped
from tf_transformations import euler_from_quaternion
from tf2_ros import Buffer, TransformException, TransformListener
from tf2_geometry_msgs import do_transform_pose_stamped

from evolo_msgs.msg import Topics as EvoloTopics
from smarc_msgs.msg import Topics as smarcTopics
from smarc_control_msgs.msg import Topics as ControlTopics
import json


class ghost_obstacles(Node):
    """Sends virtual obstacles on collision course with Evolo."""
    def __init__(self):
        super().__init__("ghost_obstacles")
        self.logger = self.get_logger()
        self.logger.info("Ghost obstacles initiated!")

        self.declare_node_parameters()

        self.update_rate = float(self.get_parameter("update_rate").value)
        self.logger.info(f"update rate: {self.update_rate}")
        self.robot_name = self.get_parameter("robot_name").value

        # Keep track of Evolo using TF2
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(
            self.tf_buffer, self, spin_thread=True
        )

        # Keep track of time
        self.current_time = None
        self.clock_sub = self.create_subscription(Clock, "/clock", self.clock_cb, 10)

        # Relay control to Unity
        unity_sim = True
        self.p_value = 0.5
        if unity_sim:
            self.control_sub = self.create_subscription(Float32, f"{EvoloTopics.EVOLO_STEERING_SETPOINT}", self.ctrl_cb, 1)
            self.control_pub = self.create_publisher(TwistStamped, "/evolo/ctrl/twist_setpoint", 10)

        # Outputs
        self.obstacle_topic = self.get_parameter("obstacle_topic").value
        self.obstacle_pub = self.create_publisher(Odometry,
                                                f"{self.obstacle_topic}", 10)
        self.logger.info(f"Sending obstacle messages to /{self.robot_name}/{self.obstacle_topic}")

        # Calculate start and end point of the obstacles path in Evolo frame
        self.radius = float(self.get_parameter("obstacle_radius").value) # [m]
        evolo_speed = 4.5 # [m/s]
        time_to_collision = float(self.get_parameter("time_to_collision").value) # [s]
        self.obstacle_angle = float(self.get_parameter("obstacle_angle").value) # [rad]
        self.obstacle_speed = float(self.get_parameter("obstacle_speed").value) # [m/s]
        self.t = 0 # [s]
        self.t_tot = time_to_collision * 2
        self.logger.info(f"Radius: {self.radius}, time to collision: {time_to_collision}, angle: {self.obstacle_angle}, speed: {self.obstacle_speed}")

        evolo_dist_to_col = evolo_speed * time_to_collision
        obst_dist_to_col = self.obstacle_speed * time_to_collision

        x_obst_start = evolo_dist_to_col + obst_dist_to_col * np.cos(self.obstacle_angle)
        y_obst_start = obst_dist_to_col * np.sin(self.obstacle_angle)
        x_obst_goal = evolo_dist_to_col - obst_dist_to_col * np.cos(self.obstacle_angle)
        y_obst_goal = -obst_dist_to_col * np.sin(self.obstacle_angle)

        self.x_vel = -self.obstacle_speed * np.cos(self.obstacle_angle)
        self.y_vel = -self.obstacle_speed * np.sin(self.obstacle_angle)

        # Transform them to odom frame
        self.start_point = PointStamped()
        self.start_point.header.frame_id = 'base_footprint'

        self.start_point.point.x = x_obst_start
        self.start_point.point.y = y_obst_start
        self.start_point.point.z = 0.0

        self.goal_point = PointStamped()
        self.goal_point.header.frame_id = 'base_footprint'

        self.goal_point.point.x = x_obst_goal
        self.goal_point.point.y = y_obst_goal
        self.goal_point.point.z = 0.0

        no_TF_start = True
        no_TF_goal = True

        self.target_frame = "evolo/odom"
        while no_TF_goal or no_TF_start:
            try:
                self.start_point.header.stamp = self.current_time
                self.start_point = self.tf_buffer.transform(
                    self.start_point,
                    self.target_frame,
                    timeout=rclpy.duration.Duration(seconds=1.0)
                )

                self.get_logger().info(
                    f"Transformed start point: {self.start_point.point}"
                )
                no_TF_start = False

            except Exception as e:
                self.get_logger().error(f"Start transform failed: {e}")

            try:
                self.goal_point.header.stamp = self.current_time
                self.goal_point = self.tf_buffer.transform(
                    self.goal_point,
                    self.target_frame,
                    timeout=rclpy.duration.Duration(seconds=1.0)
                )

                self.get_logger().info(
                    f"Transformed goal point: {self.goal_point.point}"
                )
                no_TF_goal = False

            except Exception as e:
                self.get_logger().error(f"Goal transform failed: {e}")
            time.sleep(5.0)

    def clock_cb(self, msg):
        self.current_time = msg.clock

    def declare_node_parameters(self):
        self.declare_parameter("update_rate", 1)
        self.declare_parameter("robot_name", "")
        self.declare_parameter("obstacle_topic", "")
        self.declare_parameter("obstacle_radius", 1.0)
        self.declare_parameter("time_to_collision", 1.0)
        self.declare_parameter("obstacle_angle", 1.0)
        self.declare_parameter("obstacle_speed", 1.0)

    def update(self):
        """Calculate the updated position of the obstacle in odom frame, then send it"""
        self.t += 1.0
        t_frac = self.t / self.t_tot

        obstacle_msg = Odometry()
        obstacle_msg.header.frame_id = self.target_frame
        obstacle_msg.header.stamp = self.current_time
        obstacle_msg.header.stamp.sec -= 1

        obstacle_msg.pose.covariance[0] = self.radius
        obstacle_msg.pose.covariance[7] = self.radius
        obstacle_msg.pose.covariance[14] = self.radius

        obstacle_msg.pose.pose.position.x = self.start_point.point.x * (1 - t_frac) + self.goal_point.point.x * t_frac
        obstacle_msg.pose.pose.position.y = self.start_point.point.y * (1 - t_frac) + self.goal_point.point.y * t_frac

        obstacle_msg.twist.twist.linear.x = self.x_vel
        obstacle_msg.twist.twist.linear.y = self.y_vel

        self.obstacle_pub.publish(obstacle_msg)
        self.logger.info(f"Updating obstacle position to x: {obstacle_msg.pose.pose.position.x}, y: {obstacle_msg.pose.pose.position.y}")

    def ctrl_cb(self, msg):
        """Relays control to unity simulator"""
        w = msg.data * self.p_value
        # self.logger.info(f"Target heading diff: {msg.data}")

        new_msg = TwistStamped()
        new_msg.header.frame_id = self.target_frame
        new_msg.header.stamp = self.get_clock().now().to_msg()

        new_msg.twist.linear.x = 4.5
        new_msg.twist.angular.z = w
        # self.logger.info(f"Belayed message v: {4.5}, w: {w}")
        self.control_pub.publish(new_msg)



def main(args=None, namespace=None):
    rclpy.init(args=args)
    ghost_node = ghost_obstacles()

    ghost_node.create_timer(1.0/ghost_node.update_rate, ghost_node.update)
    executor = MultiThreadedExecutor()
    executor.add_node(ghost_node)
    executor.spin()
