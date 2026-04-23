#!/usr/bin/python

import numpy as np

from rclpy.node import Node
from rclpy.time import Time, Duration

from geometry_msgs.msg import  PointStamped, PoseStamped
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PointStamped
from nav_msgs.msg import Odometry

from tf2_geometry_msgs import do_transform_pose_stamped
from tf2_ros import Buffer, TransformListener

from smarc_utilities.georef_utils import convert_latlon_to_utm
from dji_msgs.msg import Topics as DJITopics
from dji_msgs.msg import Links as DJILinks
from smarc_msgs.msg import Topics as SmarcTopics



class DroneState():
    def __init__(self,
                 node: Node,
                 robot_name: str):
        
        self._node : Node = node
        self.MAP_FRAME : str = robot_name + '/' + DJILinks.MAP
        self.ODOM_FRAME : str = robot_name + '/' + DJILinks.ODOM
        self._drone_in_map : None | PoseStamped = None

        self._tf_buffer : Buffer = Buffer()
        self._tf_listener : TransformListener = TransformListener(self._tf_buffer, self._node, spin_thread=True)

        found = False
        while not found:
            try:
                self._odom_to_map_tf = self._tf_buffer.lookup_transform(self.MAP_FRAME, self.ODOM_FRAME, Time(), Duration(seconds=1))
                found = True
            except Exception as e:
                self._node.get_logger().info(f"Waiting for transform from {self.ODOM_FRAME} to {self.MAP_FRAME}...")
        
        self._node.create_subscription(Odometry,
                                       SmarcTopics.ODOM_TOPIC,
                                       self._odom_cb,
                                       10)
        
    def _odom_cb(self, drone_in_odom: Odometry):
        drone_in_odom_ps : PoseStamped = PoseStamped()
        drone_in_odom_ps.header = drone_in_odom.header
        drone_in_odom_ps.pose = drone_in_odom.pose.pose
        try:
            self._drone_in_map = do_transform_pose_stamped(drone_in_odom_ps, self._odom_to_map_tf)
        except Exception as e:
            self._node.get_logger().error(f"Error transforming drone pose from odom to map: {e}")

    @property
    def drone_in_map(self) -> PoseStamped|None:
        return self._drone_in_map
    
    @property
    def drone_in_map_numpy(self) -> np.ndarray|None:
        if self._drone_in_map is not None:
            return np.array([self._drone_in_map.pose.position.x, self._drone_in_map.pose.position.y, self._drone_in_map.pose.position.z])
        else:
            return None

    @property
    def altitude(self) -> float|None:
        if self._drone_in_map is not None:
            return self._drone_in_map.pose.position.z
        else:
            return None
    
    @property
    def now_float(self) -> float:
        now_stamp = self._node.get_clock().now().to_msg()
        return now_stamp.sec + now_stamp.nanosec * 1e-9
    
    def _loginfo(self, msg: str):
        self._node.get_logger().info(msg)
    
    
    def msg_is_older_than(self, msg, age_s: float) -> bool:
        if msg is None: return True
        if msg.header is None: return True
        if msg.header.stamp is None: return True

        # did someone forget to set the timestamp at all??
        if msg.header.stamp.sec == 0 and msg.header.stamp.nanosec == 0:
            self._loginfo("Message has zero timestamp, treating as stale.")
            self._loginfo(f"Message timestamp: {msg.header.stamp.sec}.{msg.header.stamp.nanosec}, now: {self.now_float}")
            return True
        
        age = self.now_float - (msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9)

        # did someone forget sim time flag?
        if age > 100000.0 or age < 0.0:
            self._loginfo(f"Message age is abnormal, treating as stale.")
            self._loginfo(f"Message timestamp: {msg.header.stamp.sec}.{msg.header.stamp.nanosec}, now: {self.now_float}, age: {age}")

        if age > age_s:
            self._loginfo(f"Message is stale (age {age:.2f} > {age_s:.2f}).")
            return True
        
        return False

    def convert_geopoint_to_map_pose_stamped(self, gp: GeoPoint) -> PoseStamped:
        in_utm : PointStamped = convert_latlon_to_utm(gp)
        in_utm_pose : PoseStamped = PoseStamped()
        in_utm_pose.header = in_utm.header
        in_utm_pose.pose.position = in_utm.point
        in_utm_pose.pose.position.z = gp.altitude  # keep the altitude from the GeoPoint as is

        tf = self._tf_buffer.lookup_transform(
            target_frame = self.MAP_FRAME,
            source_frame = in_utm.header.frame_id,
            time = Time(seconds=0),
            timeout = Duration(seconds=1)
        )
        in_map = do_transform_pose_stamped(in_utm_pose, tf)
        in_map.pose.position.z = gp.altitude  # ensure altitude is preserved
        return in_map
    
    def pose_stamped_in_map(self, pose: PoseStamped) -> PoseStamped:
        if pose.header.frame_id == self.MAP_FRAME:
            return pose
        else:
            tf = self._tf_buffer.lookup_transform(
                target_frame = self.MAP_FRAME,
                source_frame = pose.header.frame_id,
                time = Time(seconds=0),
                timeout = Duration(seconds=1)
            )
            in_map = do_transform_pose_stamped(pose, tf)
            return in_map