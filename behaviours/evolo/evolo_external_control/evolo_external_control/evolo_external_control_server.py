import rclpy

from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from smarc_action_base.gentler_action_server import GentlerActionServer
from transforms3d.euler import euler2quat
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32
from evolo_msgs.msg import Topics as evoloTopics
from smarc_msgs.msg import Topics as smarcTopics
import math

import math
import json

from enum import Enum

class EvoloExternalControl():


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

        # State variables. gets updated from topic callbacks
        self.robot_position = PoseStamped() #robot positon [geometry_msgs/msg/Pose]
        self.robot_position_time = None #robot position time to be compared with current time
        
        self.target_yaw = Float32() #target positon [geometry_msgs/msg/Pose]
        self.target_yaw_time = None

        self.target_speed = Float32()
        self.target_speed_time = None
        
        #Target frame
        self.frame_id = 'evolo/base_link'

        #Settings etc
        self.timeout = 1800.0

        self.max_speed = 8.0
        
        #Time of action start to check for timeout
        self.action_started_time = None
        
        #Callback groups
        self.publisher_callback_group = ReentrantCallbackGroup()
        self.subscriber_callback_group = ReentrantCallbackGroup()

        # Publishers
        self.evolo_pub = self._node.create_publisher(Odometry, evoloTopics.EVOLO_CONTROL_PLANNED, 10, callback_group=self.publisher_callback_group)
        # Subscribers
        self.robot_sub = self._node.create_subscription(Odometry, smarcTopics.ODOM_TOPIC, self.robot_odom_callback,10, callback_group=self.subscriber_callback_group)

        self.target_yaw_sub = self._node.create_subscription(Float32, evoloTopics.EVOLO_EXTERNAL_CONTROL_YAW_SETPOINT, self.robot_target_yaw_callback,10, callback_group=self.subscriber_callback_group)
        self.target_speed_sub = self._node.create_subscription(Float32, evoloTopics.EVOLO_EXTERNAL_CONTROL_SPEED_SETPOINT, self.robot_target_speed_callback,10, callback_group=self.subscriber_callback_group)

        self._node.get_logger().info("Action server started")

    def _on_goal_received(self, goal_request: dict) -> bool:
        self._node.get_logger().info(f"Received goal request: {goal_request}")
        # Here you would typically validate the goal request
        # Return True to accept the goal, False to reject it
        params = json.loads(goal_request['json-params'])

        self._node.get_logger().info(f"params: {params}")
        if 'timeout' in params.keys() : self.timeout = min(3600, max(1, params['timeout']))
        self._node.get_logger().info('timeout: ' + str(self.timeout))


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
            return True # Done

        if(self.robot_position is None or (time_now - self.robot_position_time) > 10):
            self._node.get_logger().error("ERROR no robot position")
            return False
        

        allow_control = True
        
        if(self.target_yaw_time is None or (time_now - self.target_yaw_time) > 2):
            allow_control = False

        if(self.target_speed_time is None):
            allow_control = False
        
        # Publication
        if(allow_control):
            targetYaw = self.target_yaw
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
            
        else:
            self._node.get_logger().error("ERROR external control timeout")
            pass
        
        return None
    
    def _give_feedback(self) -> str:
        time_now = int(self._node.get_clock().now().nanoseconds * 1e-9)
        runtime = time_now - self.action_started_time

        feedback = f"Action runtime: {runtime}."
        self._node.get_logger().info(feedback)
        # Here you would typically generate feedback for the action
        # This is run after each _loop_inner call
        return feedback


    #Subscriber callback functions
    def robot_odom_callback(self,msg : Odometry):
        #self._node.get_logger().info("robot position updated.")
        self.robot_position = PoseStamped()
        self.robot_position.header = msg.header
        self.robot_position.pose = msg.pose.pose
        self.robot_position_time = int(self._node.get_clock().now().nanoseconds * 1e-9)
        #self._node.get_logger().info("" + str(msg.header.frame_id))
    
    def robot_target_yaw_callback(self, msg : Float32):
        self._node.get_logger().info(f"target yaw updated: {msg.data}")
        self.target_yaw = msg.data
        while(self.target_yaw < 0): self.target_yaw += 2* math.pi
        while(self.target_yaw > 0): self.target_yaw -= 2* math.pi
        self.target_yaw_time = int(self._node.get_clock().now().nanoseconds * 1e-9)

    def robot_target_speed_callback(self, msg : Float32):
        self._node.get_logger().info(f"target speed updated: {msg.data}")
        self.target_speed = msg.data
        self.target_speed = max(0.0, min(10.0, self.target_speed))
        self.target_speed_time = int(self._node.get_clock().now().nanoseconds * 1e-9)

def main():
    rclpy.init()
    node = Node("evolo_external_control_action_server")
    
    action_server = EvoloExternalControl(node, "external_control")   

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down evolo external_control acation server")
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()
