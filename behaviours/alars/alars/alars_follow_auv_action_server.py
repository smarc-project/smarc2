#!/usr/bin/python

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.time import Time, Duration

import traceback

from geometry_msgs.msg import  PointStamped, PoseStamped, PoseWithCovarianceStamped
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PointStamped

from smarc_action_base.gentler_action_server import GentlerActionServer
from dji_msgs.msg import Topics as DJITopics
from dji_msgs.msg import Links as DJILinks

from alars.alars_common import DroneState, do_transform_pose_stamped

class FollowAUVAction():
    def __init__(self,
                 node: Node):
        self._node : Node = node

        self._node.declare_parameter('robot_name', 'M350')
        self._robot_name : str = self._node.get_parameter('robot_name').get_parameter_value().string_value

        self._drone_state = DroneState(node, self._robot_name)

        self._node.declare_parameter('detection_freshness_threshold', 2.0)
        self.DETECTION_FRESHNESS_THRESHOLD : float = self._node.get_parameter('detection_freshness_threshold').get_parameter_value().double_value

        self._reset()

        self._auv_projection : PoseStamped = PoseStamped()
        self._auv_projection.header.frame_id = self._drone_state.MAP_FRAME
        
        self._setpoint_pub = self._node.create_publisher(
            msg_type = PoseStamped,
            topic = DJITopics.MOVE_TO_SETPOINT_TOPIC,
            qos_profile= 10)
        
        
        self._node.create_subscription(PoseWithCovarianceStamped,
                                       DJITopics.PROJECTED_AUV_POSE_WITH_COV_TOPIC,
                                       self._auv_projection_cb,
                                       10)
        

        self._loop_frequency = 10.0
        self._as = GentlerActionServer(
            node,
            "alars_follow_auv",
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency = self._loop_frequency
        )


    def _reset(self):
        self._current_setpoint : PoseStamped | None = None
        self._follow_altitude : float | None = None
        self._timeout : float | None = None
        self._follow_start_time : float | None = None
        self._vulture_radius : float = 0.0
        self._vulture_speed_deg : float = 10.0 
        self._vulture_pos_rad : float = np.random.uniform(0, 2*np.pi)


    def _loginfo(self, msg: str):
        self._node.get_logger().info(msg)


    def _auv_projection_cb(self, msg: PoseWithCovarianceStamped):        
        if msg.header.stamp is None:
            self._loginfo("Received AUV projection message with no timestamp, ignoring.")
            return
        
        if msg.header.stamp.sec == 0 and msg.header.stamp.nanosec == 0:
            self._loginfo("Received AUV projection message with zero timestamp, ignoring.")
            return
        
        if msg.header.frame_id == self._auv_projection.header.frame_id:
            self._auv_projection.pose = msg.pose.pose
        else:
            self._loginfo(f"Received AUV projection in frame {msg.header.frame_id}, expected {self._auv_projection.header.frame_id}. Transforming...")
            try:
                tf = self._drone_state._tf_buffer.lookup_transform(
                    target_frame = self._auv_projection.header.frame_id,
                    source_frame = msg.header.frame_id,
                    time = Time(seconds=0),
                    timeout = Duration(seconds=1)
                )
                self._auv_projection = do_transform_pose_stamped(PoseStamped(header=msg.header, pose=msg.pose.pose), tf)
            except Exception as e:
                self._loginfo(f"Error transforming AUV projection to map frame: {e}")
            
        self._auv_projection.header.stamp= msg.header.stamp
    



    def _on_goal_received(self, goal_request: dict) -> bool:
        """
        Here you would typically validate the goal request
        Return True to accept the goal, False to reject it
        """ 
        self._reset()
        self._loginfo(f"Received goal request: {goal_request}")

        try:
            self._follow_altitude = float(goal_request['follow_altitude'])
            self._vulture_radius = float(goal_request['vulture_radius'])
            self._vulture_speed_deg = float(goal_request['vulture_speed_deg'])
            self._timeout = float(goal_request['timeout'])
        except:
            self._loginfo('Action goal could not be parsed?') 
            return False
        
        

        self._loginfo(f"Accepted goal request to follow AUV at {self._follow_altitude}m")
        return True
    

    def _on_cancel_received(self) -> bool:
        self._loginfo("Cancelled.")
        self._reset()
        return True


    def _prepare_loop(self) -> None:
        self._follow_start_time = self._drone_state.now_float
        return
    

    def _loop_inner(self) -> bool|None:
        """
        Return True to indicate success, False for failure, or None to continue
        """
        if self._drone_state.drone_in_map is None:
            self._loginfo("No drone position received yet, cannot perform follow...")
            return False
        
        if self._drone_state.msg_is_older_than(self._auv_projection, self.DETECTION_FRESHNESS_THRESHOLD, "auv projection loop check"):
            self._loginfo("AUV projection is stale, finishing action successfully.")
            return True
        
        if self._follow_start_time is None or self._timeout is None:
            self._loginfo("Started following or timeout not set, this is a bug!")
            return False
            
        if self._timeout > 0:
            if self._drone_state.now_float - self._follow_start_time > self._timeout:
                self._loginfo("Follow AUV action timed out, finishing with success.")
                return True

        target_pos = np.array([self._auv_projection.pose.position.x, self._auv_projection.pose.position.y])
        if self._vulture_radius > 0.0 and self._vulture_speed_deg != 0.0:
            dt = 1.0 / self._loop_frequency
            rad_diff = np.radians(self._vulture_speed_deg) * dt
            self._vulture_pos_rad += rad_diff
            self._vulture_pos_rad %= (2 * np.pi)
            position_on_circle = np.array([np.cos(self._vulture_pos_rad), np.sin(self._vulture_pos_rad)]) * self._vulture_radius
            target_pos += position_on_circle
            self._loginfo(f"Vulturing: {np.rad2deg(self._vulture_pos_rad)} deg at radius {self._vulture_radius}m")
    
        # publish setpoint
        # we create the auv_projection in map frame in the callback, so we can directly use it here without needing to transform it
        setpoint_msg = PoseStamped()
        setpoint_msg.header.frame_id = self._auv_projection.header.frame_id
        setpoint_msg.header.stamp = self._node.get_clock().now().to_msg()
        setpoint_msg.pose.position.x = target_pos[0]
        setpoint_msg.pose.position.y = target_pos[1]
        setpoint_msg.pose.position.z = self._follow_altitude
        setpoint_msg.pose.orientation.w = 1.0
        self._setpoint_pub.publish(setpoint_msg)
        self._current_setpoint = setpoint_msg
        self._loginfo(f"New setpoint: {setpoint_msg.pose.position}")
        return None 



    def _give_feedback(self) -> str:
        if self._timeout is not None and self._timeout > 0 and self._follow_start_time is not None:
            time_remaining = max(0.0, self._timeout - (self._drone_state.now_float - self._follow_start_time))
            return f"Following AUV at {self._follow_altitude}m, time remaining: {time_remaining:.1f}s"
        else:
            return f"Following AUV at {self._follow_altitude}m until you stop it."


def main(args=None):
    rclpy.init(args=args)

    node = Node("alars_follow_auv_action_server")

    follow_auv_action = FollowAUVAction(node)

    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)

    node.destroy_node()
    rclpy.shutdown()