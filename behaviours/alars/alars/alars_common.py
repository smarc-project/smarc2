#!/usr/bin/python

import numpy as np

from rclpy.node import Node
from rclpy.time import Time
from rclpy.duration import Duration

from std_msgs.msg import String
from geometry_msgs.msg import  PointStamped, PoseStamped
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PointStamped
from nav_msgs.msg import Odometry

from tf2_geometry_msgs import PoseWithCovarianceStamped, do_transform_pose_stamped
from tf2_ros import Buffer, TransformListener

from smarc_utilities.georef_utils import convert_latlon_to_utm, convert_utm_to_latlon
from dji_msgs.msg import Topics as DJITopics
from dji_msgs.msg import Links as DJILinks
from smarc_msgs.msg import Topics as SmarcTopics



class DroneState():
    def __init__(self,
                 node: Node,
                 robot_name: str):
        
        self._node : Node = node
        self._robot_name : str = robot_name
        self.MAP_FRAME : str = robot_name + '/' + DJILinks.MAP
        self.ODOM_FRAME : str = robot_name + '/' + DJILinks.ODOM
        self._utm_frame : str|None = None
        self._drone_in_map : None | PoseStamped = None

        def _pose_in_map_cb(msg: PoseStamped):
            if msg.header.frame_id != self.MAP_FRAME:
                self._loginfo(f"Received pose in map topic, but frame_id is {msg.header.frame_id} instead of expected {self.MAP_FRAME}. Ignoring.")
                return
            self._drone_in_map = msg

        self._node.create_subscription(PoseStamped,
                                       DJITopics.BASE_LINK_IN_MAP_TOPIC,
                                       _pose_in_map_cb,
                                       10)

        def _utm_frame_cb(msg: String):
            self._utm_frame = msg.data

        self._node.create_subscription(String,
                                       DJITopics.LABELED_UTM_TOPIC,
                                       _utm_frame_cb,
                                       10)
        
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self._node, spin_thread=False)
            

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
    
    
    def msg_is_older_than(self, msg, age_s: float, debug_str:str="") -> bool:
        if msg is None: return True
        if msg.header is None: return True
        if msg.header.stamp is None: return True

        # did someone forget to set the timestamp at all??
        if msg.header.stamp.sec == 0 and msg.header.stamp.nanosec == 0:
            self._loginfo(f"Message has zero timestamp, treating as stale. {debug_str}")
            return True
        
        age = self.now_float - (msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9)

        # did someone forget sim time flag?
        if age > 100000.0 or age < 0.0:
            self._loginfo(f"Message age is abnormal, treating as stale. {debug_str}")
            self._loginfo(f"Message timestamp: {msg.header.stamp.sec}.{msg.header.stamp.nanosec}, now: {self.now_float}, age: {age}")

        if age > age_s:
            if debug_str != "":
                self._loginfo(f"Message is stale (age {age:.2f} > {age_s:.2f}). {debug_str}")
            return True
        
        return False

    def geopoint_to_pose_stamped_map(self, gp: GeoPoint) -> PoseStamped|None:
        in_utm : PointStamped = convert_latlon_to_utm(gp)
        in_utm_pose : PoseStamped = PoseStamped()
        in_utm_pose.header = in_utm.header
        in_utm_pose.pose.position = in_utm.point
        in_utm_pose.pose.position.z = gp.altitude  # keep the altitude from the GeoPoint as is

        if not self._tf_buffer.can_transform(self.MAP_FRAME, in_utm_pose.header.frame_id, Time(seconds=0)):
            self._loginfo(f"Cannot transform pose in frame <{in_utm_pose.header.frame_id}> to <{self.MAP_FRAME}> frame.")
            return None

        tf = self._tf_buffer.lookup_transform(
            target_frame = self.MAP_FRAME,
            source_frame = in_utm.header.frame_id,
            time = Time(seconds=0),
            timeout = Duration(seconds=1)
        )
        in_map = do_transform_pose_stamped(in_utm_pose, tf)
        in_map.pose.position.z = gp.altitude  # ensure altitude is preserved
        return in_map
    

    def pose_to_geopoint(self, pose: PoseStamped | PoseWithCovarianceStamped) -> GeoPoint|None:
        if self._utm_frame is None:
            self._loginfo("UTM frame not set yet, cannot convert pose to geopoint.")
            return None

        if not self._tf_buffer.can_transform(self._utm_frame, pose.header.frame_id, Time(seconds=0)):
            self._loginfo(f"Cannot transform pose in frame <{pose.header.frame_id}> to <{self._utm_frame}> frame.")
            return None

        tf = self._tf_buffer.lookup_transform(
            target_frame = self._utm_frame,
            source_frame = pose.header.frame_id,
            time = Time(seconds=0),
            timeout = Duration(seconds=1)
        )
        if isinstance(pose, PoseWithCovarianceStamped):
            ps = PoseStamped()
            ps.header = pose.header
            ps.pose = pose.pose.pose
        else:
            ps = pose

        in_utm = do_transform_pose_stamped(ps, tf)
        return convert_utm_to_latlon(in_utm)
        

    def pose_stamped_in_map(self, pose: PoseStamped) -> PoseStamped|None:
        if pose.header.frame_id == self.MAP_FRAME:
            return pose
        else:
            if not self._tf_buffer.can_transform(self.MAP_FRAME, pose.header.frame_id, Time(seconds=0)):
                self._loginfo(f"Cannot transform pose in frame <{pose.header.frame_id}> to <{self.MAP_FRAME}> frame.")
                return None
            
            tf = self._tf_buffer.lookup_transform(
                target_frame = self.MAP_FRAME,
                source_frame = pose.header.frame_id,
                time = Time(seconds=0),
                timeout = Duration(seconds=1)
            )
            in_map = do_transform_pose_stamped(pose, tf)
            return in_map
        
