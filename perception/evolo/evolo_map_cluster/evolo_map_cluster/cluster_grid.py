#! /usr/bin/env python3

import math
import rclpy
import numpy as np
from rclpy.node import Node
from std_msgs.msg import String, Float32
from geometry_msgs.msg import TwistStamped
from rclpy.executors import MultiThreadedExecutor
from nav_msgs.msg import Odometry, OccupancyGrid
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import PoseStamped
from tf_transformations import euler_from_quaternion

from smarc_msgs.msg import Topics as smarcTopics
from smarc_control_msgs.msg import Topics as ControlTopics
import json


class cluster_grid(Node):
    """Cluster occupied areas from a occupancy grid, to provide easy input for the CBF."""
    def __init__(self):
        super().__init__("cluster_grid")
        self.logger = self.get_logger()
        self.logger.info("Occupancy map clustering initiated!")

        self.declare_node_parameters()

        self.update_rate = float(self.get_parameter("update_rate").value)
        self.logger.info(f"update rate: {self.update_rate}")
        self.robot_name = self.get_parameter("robot_name").value

        # Occupancy grid
        self.occ_limit = 30 # Limit for a single square
        self.cluster_limit = 80 # Limit for a cluster
        self.obstacle_closeness_limit = 3
        self.reduce_search = 20
        self.max_cluster_size = 100
        self.grid_size = 200

        self.grid = np.zeros((self.grid_size, self.grid_size))
        self.cluster_num = 1
        self.cluster_list = [[]]
        self.grid_topic = self.get_parameter("grid_topic").value
        self.grid_sub = self.create_subscription(OccupancyGrid, 
                                 f"/{self.grid_topic}", self.grid_cb, 1)
        self.logger.info(f"Reciving occupancy grid messages from /{self.grid_topic}")

        # Outputs
        self.obstacle_topic = self.get_parameter("obstacle_topic").value
        self.obstacle_pub = self.create_publisher(Odometry,
                                                f"{self.obstacle_topic}", 10)
        self.logger.info(f"Sending obstacle messages to /{self.robot_name}/{self.obstacle_topic}")

        # Nicer obstacle publisher for rviz
        self.rviz_obs_array = MarkerArray()
        self.rviz_obs_pub = self.create_publisher(MarkerArray, "rvizObstacles", 1)

    def declare_node_parameters(self):
        self.declare_parameter("update_rate", 1)
        self.declare_parameter("robot_name", "")
        self.declare_parameter("grid_topic", "")
        self.declare_parameter("obstacle_topic", "")

    def update(self):
        pass

    def grid_cb(self, msg):
        """Callback when reciving an updated occupancy grid."""
        data = msg.data
        self.header = msg.header
        self.grid = np.zeros((self.grid_size, self.grid_size))
        self.cluster_num = 1
        self.cluster_list = [[]]
        
        for y in range(self.reduce_search, self.grid_size - self.reduce_search):
            for x in range(self.reduce_search, self.grid_size - self.reduce_search):
                self.cluster_list[-1] = []
                if self.expand_cluster(x, y, data):
                    self.cluster_num += 1
                    self.cluster_list.append([])

        self.send_cluster_info()
        self.logger.info(f"Found {self.cluster_num-1} clusters.")

    def expand_cluster(self, first_x, first_y, data):
        """List based expansion of the cluster"""
        potential_cells = [[first_x, first_y]]
        cluster_certainty = 0

        for i in range(self.max_cluster_size):
            if i >= len(potential_cells):
                break
            x, y = potential_cells[i]
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                # Check if clamied by other cluster and above occupied limit
                if self.grid[x, y] == 0 and data[y * self.grid_size + x] > self.occ_limit:
                    cluster_certainty += data[y * self.grid_size + x]
                    self.cluster_list[-1].append((x, y))
                    self.grid[x, y] = self.cluster_num
                    
                    potential_cells.append([x + 1, y    ])
                    potential_cells.append([x    , y + 1])
                    potential_cells.append([x - 1, y    ])
                    potential_cells.append([x,     y - 1])

        if cluster_certainty >= self.cluster_limit:
            return True
        return False
   
        
    def send_cluster_info(self):
        """Sends the clusters as a point and a circle"""
        # If no obstacle is found, set a zero-sized obstacle at 4711 (Cologne)
        if self.cluster_num - 1 < 1:
            msg = Odometry()
            msg.header = self.header
            self.logger.info(f"Found no obstacle at time {msg.header.stamp}")
            msg.pose.pose.position.x = 4711.0
            msg.pose.pose.position.y = 4711.0
            msg.pose.covariance[0] = 0.0
            msg.pose.covariance[7] = 0.0
            msg.pose.covariance[14] = 0.0
            self.obstacle_pub.publish(msg)
            return

        # Calculate the size of each cluster, and construct an over-approximating circle around it
        self.rviz_obs_array = MarkerArray()
        for i in range(self.cluster_num-1):
            max_x = 0
            min_x = self.grid_size
            max_y = 0
            min_y = self.grid_size
            for x, y in self.cluster_list[i]:
                if x > max_x:
                    max_x = x
                if x < min_x:
                    min_x = x
                if y > max_y:
                    max_y = y
                if y < min_y:
                    min_y = y
            
            center_x = 0.5 * (max_x + 1 + min_x)
            center_y = 0.5 * (max_y + 1 + min_y)
            add_r = 0.5 * np.sqrt(2)
            max_r = add_r # Default for a single square

            # Calculate coorinates in agent's frame
            obs_x = center_x - 0.5 * self.grid_size
            obs_y = center_y - 0.5 * self.grid_size

            # Calculate radial distance to obstacle
            obs_r = np.sqrt(obs_x**2 + obs_y**2)

            if obs_x > 0 and obs_r > self.obstacle_closeness_limit:
                for x, y in self.cluster_list[i]:
                    r = np.sqrt((x - center_x)**2 + (y - center_y)**2) + add_r
                    if r > max_r:
                        max_r = r

                msg = Odometry()
                msg.header = self.header
                msg.pose.pose.position.x = obs_x
                msg.pose.pose.position.y = obs_y
                msg.pose.covariance[0] = max_r
                msg.pose.covariance[7] = max_r
                msg.pose.covariance[14] = max_r
                self.logger.info(f"Obstacle at x: {msg.pose.pose.position.x}, y: {msg.pose.pose.position.y}, r: {max_r}")
                self.obstacle_pub.publish(msg)

                # Same but for rviz
                obs_msg = Marker()
                obs_msg.header = self.header

                obs_msg.ns = "obstacles"
                obs_msg.id = i
                obs_msg.type = Marker.SPHERE
                obs_msg.action = Marker.ADD

                obs_msg.pose.position.x = obs_x
                obs_msg.pose.position.y = obs_y
                obs_msg.pose.position.z = 0.0
                
                obs_msg.scale.x = max_r * 2.0  # Diameter
                obs_msg.scale.y = max_r * 2.0
                obs_msg.scale.z = max_r * 2.0

                obs_msg.color.r = 0.0
                obs_msg.color.g = 0.0
                obs_msg.color.b = 1.0
                obs_msg.color.a = 1.0

                obs_msg.lifetime.sec = 3
                obs_msg.lifetime.nanosec = 0

                self.rviz_obs_array.markers.append(obs_msg)
        self.rviz_obs_pub.publish(self.rviz_obs_array)


def main(args=None, namespace=None):
    rclpy.init(args=args)
    cluster_node = cluster_grid()

    cluster_node.create_timer(1.0/cluster_node.update_rate, cluster_node.update)
    executor = MultiThreadedExecutor()
    executor.add_node(cluster_node)
    executor.spin()
