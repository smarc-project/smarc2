import rclpy

from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from smarc_action_base.gentler_action_server import GentlerActionServer
from geodesy import utm
from geographic_msgs.msg import GeoPoint
from tf2_geometry_msgs import do_transform_pose_stamped

from transforms3d.euler import euler2quat

from rclpy.time import Duration, Time
from nav_msgs.srv import SetMap
from nav_msgs.msg import OccupancyGrid
from nav_msgs.msg import MapMetaData
from nav_msgs.srv import GetPlan
from nav_msgs.msg import Path
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose, Twist
from geometry_msgs.msg import PoseStamped, PointStamped
from std_msgs.msg import Float32, Empty
from std_msgs.msg import String
from evolo_msgs.msg import Topics as evoloTopics
from smarc_msgs.msg import Topics as smarcTopics
from smarc_control_msgs.msg import Topics as controlTopics
from tf2_ros import Buffer, TransformException, TransformListener
import math

import numpy as np
import time
import math
import json


from enum import Enum

def vec2_directed_angle(v1, v2):
    """
    # Author: Ozer Ozkahraman (ozkahramanozer@gmail.com)
    # Date: 2018-07-10

    returns the shortest angle from v1 to v2 in radians.
    v1 + angle = v2.

    positive value means ccw rotation from v1 to v2.
    negative value means cw.

    v1, v2 can be (N,2)
    """
    v1 = np.array(np.atleast_2d(v1))
    v2 = np.array(np.atleast_2d(v2))
    assert v1.shape == v2.shape

    x1s = v1[:,0]
    x2s = v2[:,0]
    y1s = v1[:,1]
    y2s = v2[:,1]

    dots = x1s*x2s + y1s*y2s
    dets = x1s*y2s - y1s*x2s

    angles = np.arctan2(dets,dots)

    N,_ = v1.shape
    if N == 1:
        return angles[0]
    else:
        return angles

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
        self._node.declare_parameter('target_radius', 10)
        self.target_tol = float(self._node.get_parameter('target_radius').value)

        self._node.declare_parameter('timeout', 1800)
        self.timeout = float(self._node.get_parameter('timeout').value)

        self._node.declare_parameter('p_gain', 0.5)
        self.pid_p_gain = float(self._node.get_parameter('p_gain').value)

        self._node.declare_parameter('i_gain', 0)
        self.pid_i_gain = float(self._node.get_parameter('i_gain').value)

        self._node.declare_parameter('d_gain', 0)
        self.pid_d_gain = float(self._node.get_parameter('d_gain').value)

        self.max_speed = 8.0        
        
        #Time of action start to check for timeout
        self.action_started_time = None
        
        #Callback groups
        self.publisher_callback_group = ReentrantCallbackGroup()
        self.subscriber_callback_group = ReentrantCallbackGroup()

        # Publishers
        self.evolo_pub = self._node.create_publisher(Odometry, evoloTopics.EVOLO_CONTROL_PLANNED, 10, callback_group=self.publisher_callback_group)
        self.target_pub = self._node.create_publisher(PointStamped, evoloTopics.EVOLO_CURRENT_WP, 10, callback_group=self.publisher_callback_group)
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

        try:
            speed = float(speed)
        except Exception as e:
            self._node.get_logger().info(f"Tried to parse speed as float. Did not work: {speed}, {e}")
            if(speed == "slow"): speed = 2.0
            elif(speed == "standard"): speed = 4.9
            elif(speed == "fast"): speed = 6
            else: speed = 0.0

        assert type(speed) == float

        self._node.get_logger().info(f"speed: {speed}, waypoint: {waypoint}")

        #if 'timeout' in params.keys() : self.timeout = min(3600, max(1, params['timeout']))
        #self.timeout = 600
        #self._node.get_logger().info('timeout: ' + str(self.timeout))

        #Compute target position from lat lon
        lat = float(waypoint['latitude'])
        lon = float(waypoint['longitude'])
        #self._node.get_logger().info(f"lat lon sent to function: {lat}, {lon}")
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

        #Calculate distance to our target and return true (success) if we are close to it
        self.distance_to_target = self.calculate_distance(self.robot_position, self.target_position)
        if(self.distance_to_target < self.target_tol):
            #TODO send speed = Stop
            return True

        dx = self.target_position.pose.position.x - self.robot_position.pose.position.x
        dy = self.target_position.pose.position.y - self.robot_position.pose.position.y
        targetYaw = math.atan2(dy,dx) # yaw in ENU
        target_quaternion = euler2quat(0,0,targetYaw, axes='sxyz')

        control_msg = Odometry()
        control_msg.header.stamp    = self._node.get_clock().now().to_msg()
        control_msg.header.frame_id = self.frame_id
        control_msg.child_frame_id = "evolo/base_link"
        control_msg.pose.pose.orientation.x = target_quaternion[1]
        control_msg.pose.pose.orientation.y = target_quaternion[2]
        control_msg.pose.pose.orientation.z = target_quaternion[3]
        control_msg.pose.pose.orientation.w = target_quaternion[0]
        control_msg.twist.twist.linear.x  = self.target_speed
        self.evolo_pub.publish(control_msg)

        #Publish current waypoint
        target_point = PointStamped()
        target_point.header = self.target_position.header
        target_point.point = self.target_position.pose.position 
        self.target_pub.publish(target_point)

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
        quaternion_values = euler2quat(0,0,yaw, axes='sxyz')
        pose_stamp.pose.orientation.x = quaternion_values[1]
        pose_stamp.pose.orientation.y = quaternion_values[2]
        pose_stamp.pose.orientation.z = quaternion_values[3]
        pose_stamp.pose.orientation.w = quaternion_values[0]

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
