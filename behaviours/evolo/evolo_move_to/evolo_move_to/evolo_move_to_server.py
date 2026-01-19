import rclpy

from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from smarc_action_base.gentler_action_server import GentlerActionServer
from geodesy import utm
from geographic_msgs.msg import GeoPoint
from tf2_geometry_msgs import do_transform_pose_stamped
from tf_transformations import euler_from_quaternion
from rclpy.time import Duration, Time
from nav_msgs.srv import SetMap
from nav_msgs.msg import OccupancyGrid
from nav_msgs.msg import MapMetaData
from nav_msgs.srv import GetPlan
from nav_msgs.msg import Path
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32, Empty
from std_msgs.msg import String
from evolo_msgs.msg import Topics as evoloTopics
from smarc_msgs.msg import Topics as smarcTopics
from smarc_control_msgs.msg import Topics as controlTopics
from tf2_ros import Buffer, TransformException, TransformListener
import numpy as np
import time
import math
import json

import tf_transformations

from enum import Enum

class EvoloMoveTo():


    def __init__(self,
                 node: Node,
                 action_name: str):
        self._node = node

        # Initialize the action server with the node and action name
        # Give it all the necessary callbacks
        self._as = GentlerActionServer(
            node,
            action_name,
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency=2
        )

        # Initialize any necessary state for your specific action
        # These have nothing to do with the action server itself

        # Tf listener
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(
            self._tf_buffer, self._node, spin_thread=True
        )
        
        # State variables. gets updated from topic callbacks
        self.robot_position = PoseStamped() #robot positon [geometry_msgs/msg/Pose]
        self.robot_position_time = None #robot position time to be compared with current time
        self.target_position = PoseStamped() #target positon [geometry_msgs/msg/Pose]
        self.distance_to_target = None

        #Target frame
        #self.frame_id = 'map_gt'
        self.frame_id = 'evolo/odom'

        #Settings etc
        self.target_tol = 10 #Waypoint tolerance
        self.timeout = 1800.0
        self.target_speed = "fly"
        
        #Time of action start to check for timeout
        self.action_started_time = None
        
        #Callback groups
        self.publisher_callback_group = ReentrantCallbackGroup()
        self.subscriber_callback_group = ReentrantCallbackGroup()

        # Publishers
        self.evolo_pub = self._node.create_publisher(Float32, controlTopics.CONTROL_YAW_TOPIC,10, callback_group=self.publisher_callback_group)
        # Subscribers
        self.robot_sub = self._node.create_subscription(Odometry, smarcTopics.ODOM_TOPIC, self.robot_odom_callback,10, callback_group=self.subscriber_callback_group)
        self._node.get_logger().info("Action server started")

    def _on_goal_received(self, goal_request: dict) -> bool:
        self._node.get_logger().info(f"Received goal request: {goal_request}")
        # Here you would typically validate the goal request
        # Return True to accept the goal, False to reject it
        #params = json.loads(goal_request['json-params'])

        speed = goal_request['speed']
        waypoint = goal_request['waypoint']

        self._node.get_logger().info(f"speed: {speed}, waypoint: {waypoint}")

        #if 'timeout' in params.keys() : self.timeout = min(3600, max(1, params['timeout']))
        self.timeout = 600
        #self._node.get_logger().info('timeout: ' + str(self.timeout))

        #TODO compute target position from lat lon
        lat = float(waypoint['latitude'])
        lon = float(waypoint['longitude'])
        self._node.get_logger().info(f"lat lon sent to function: {lat}, {lon}")
        self.target_position = self.latlon_to_local_frame([lat,lon])
        self.target_speed = speed
        return True
    
    def _on_cancel_received(self) -> bool:
        self._node.get_logger().info("Received cancel request")
        # Here you would typically handle the cancel request
        # Return True to accept the cancel, False to reject it
        #TODO send speed=stop
        return True
    
    def _prepare_loop(self) -> None:
        self._node.get_logger().info("Preparing loop for action execution")
        # Here you would typically set up any necessary state or resources
        # This is run once before the loop starts, after you accept the goal
        self.action_started_time = int(self._node.get_clock().now().nanoseconds * 1e-9)

    def _loop_inner(self) -> bool | None:
        # Here you would typically perform the main logic of the action
        # Return True to indicate success, False for failure, or None to continue
        # This is run after _prepare_loop call at "loop_frequency" Hz

        #Check for timeout
        time_now = int(self._node.get_clock().now().nanoseconds * 1e-9)
        runtime = (time_now - self.action_started_time)
        if(runtime > self.timeout):
            return False # Failure

        if(self.robot_position is None or (time_now - self.robot_position_time) > 10):
            self._node.get_logger().error("ERROR no robot position")
            return False

        #Calculate distance to our current loiter target and change target if we are close enough to switch to the next one
        self.distance_to_target = self.calculate_distance(self.robot_position, self.target_position)
        if(self.distance_to_target < self.target_tol):
            #TODO send speed = Stop
            return True

        targetYaw = Float32()
        dx = self.target_position.pose.position.x - self.robot_position.pose.position.x
        dy = self.target_position.pose.position.y - self.robot_position.pose.position.y
        targetYaw.data = math.atan2(dy,dx) # yaw in ENU

        self.evolo_pub.publish(targetYaw)
        
        return None
    
    def _give_feedback(self) -> str:
        time_now = int(self._node.get_clock().now().nanoseconds * 1e-9)
        runtime = time_now - self.action_started_time

        feedback = f"Action runtime: {runtime}. DTT: {self.distance_to_target}"
        self._node.get_logger().info(feedback)
        # Here you would typically generate feedback for the action
        # This is run after each _loop_inner call
        return feedback
   
    def calculate_distance(self, pose1:PoseStamped, pose2:PoseStamped) -> float:
        dx = pose1.pose.position.x - pose2.pose.position.x
        dy = pose1.pose.position.y - pose2.pose.position.y
        return math.sqrt(dx*dx + dy*dy)

    
    def latlon_to_local_frame(self, point_list: list) -> PoseStamped:

        geopoint = GeoPoint()
        geopoint.latitude = point_list[0]
        geopoint.longitude = point_list[1]
        geopoint.altitude = 0.0
        yaw = math.radians(point_list[2]) if len(point_list) > 2 else 0.0


        point: utm.UTMPoint = utm.fromMsg(geopoint)
        pose_stamp = PoseStamped()
        pose_stamp.pose.position = point.toPoint()
        zone, band = point.gridZone()
        pose_stamp.header.frame_id = f"utm_{zone}_{band}"

        self._node.get_logger().info(f"Utmpoint: {point}")

        #Add yaw
        quaternion_values = tf_transformations.quaternion_from_euler(0,0,yaw)
        pose_stamp.pose.orientation.x = quaternion_values[0]
        pose_stamp.pose.orientation.y = quaternion_values[1]
        pose_stamp.pose.orientation.z = quaternion_values[2]
        pose_stamp.pose.orientation.w = quaternion_values[3]

        t = self._tf_buffer.lookup_transform(
                target_frame=self.frame_id,
                source_frame=pose_stamp.header.frame_id,
                time=Time(seconds=0),
                timeout=Duration(seconds=1),
            )
        return do_transform_pose_stamped(pose_stamp, t)

    #Subscriber callback functions
    def robot_odom_callback(self,msg : Odometry):
        #self._node.get_logger().info("robot position updated.")
        self.robot_position = PoseStamped()
        self.robot_position.header = msg.header
        self.robot_position.pose = msg.pose.pose
        self.robot_position_time = int(self._node.get_clock().now().nanoseconds * 1e-9)
        #self._node.get_logger().info("" + str(msg.header.frame_id))

    def testcase(self):
        pass


def main():
    rclpy.init()
    node = Node("evolo_move_to_action_server")
    
    action_client = EvoloMoveTo(node, "move_to")
    
    #action_client.testcase()
    

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down evolo move to acation server")
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()
