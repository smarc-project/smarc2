#!/usr/bin/python

from rclpy.node import Node
from rclpy.time import Time, Duration

from geometry_msgs.msg import PointStamped, PoseStamped, TransformStamped
from geographic_msgs.msg import GeoPoint
from nav_msgs.msg import Odometry

from tf2_geometry_msgs import do_transform_pose_stamped
from tf2_ros import Buffer, TransformListener

from smarc_utilities.georef_utils import convert_latlon_to_utm, convert_utm_to_latlon

class FloatSam():
    def __init__(self,
                 node: Node,
                 robot_name: str,
                 use_sim: bool = True):
        
        self._node : Node = node
        self._floatsam_in_map : None | PoseStamped = None
        self.use_sim = use_sim

        if self.use_sim:
            self.GLOBAL_MAP_FRAME: str = 'unity_origin' 
            self.LOCAL_MAP_FRAME: str  = 'unity_origin' 
        else:
            self.GLOBAL_MAP_FRAME: str = 'map'               
            self.LOCAL_MAP_FRAME: str  = f"{robot_name}/map" 

        self._tf_buffer : Buffer = Buffer()
        self._tf_listener : TransformListener = TransformListener(self._tf_buffer, self._node, spin_thread=True)

        odom_topic = f"/{robot_name}/smarc/odom"
        self._node.create_subscription(Odometry, odom_topic, self._odom_cb, 10)
        self._node.get_logger().info(f"[FloatSam] Subscribed to odometry: {odom_topic}")
        
    def _odom_cb(self, msg_odom: Odometry):
        """Keep this specific robot's pose updated in its LOCAL map for standard behaviors."""
        floatsam_in_odom = PoseStamped()
        floatsam_in_odom.header = msg_odom.header
        floatsam_in_odom.pose = msg_odom.pose.pose
        
        try:
            # LIVE LOOKUP: Source -> Local Map
            odom_to_map_tf = self._tf_buffer.lookup_transform(
                self.LOCAL_MAP_FRAME, 
                msg_odom.header.frame_id, 
                Time() 
            )
            self._floatsam_in_map = do_transform_pose_stamped(floatsam_in_odom, odom_to_map_tf)
        except Exception as e:
            self._node.get_logger().warn(
                f"Waiting for TF: {msg_odom.header.frame_id} -> {self.LOCAL_MAP_FRAME}...", 
                throttle_duration_sec=2.0
            )

    @property
    def floatsam_in_map(self) -> PoseStamped|None:
        return self._floatsam_in_map    

    def convert_geopoint_to_map_pose_stamped(self, gp: GeoPoint) -> PoseStamped:
        in_utm : PointStamped = convert_latlon_to_utm(gp)
        in_utm_pose : PoseStamped = PoseStamped()
        in_utm_pose.header = in_utm.header
        in_utm_pose.pose.position = in_utm.point
        in_utm_pose.pose.position.z = gp.altitude  

        source_frame = in_utm.header.frame_id
        try:
            tf = self._tf_buffer.lookup_transform(
                target_frame=self.LOCAL_MAP_FRAME,
                source_frame=source_frame,
                time=Time(seconds=0),
                timeout=Duration(seconds=1)
            )
        except Exception as e:
            try:
                tf = self._tf_buffer.lookup_transform(
                    target_frame=self.LOCAL_MAP_FRAME,
                    source_frame='utm',
                    time=Time(seconds=0),
                    timeout=Duration(seconds=1)
                )
            except Exception as e2:
                err_msg = (
                    f"Failed to find a transform from any UTM frame to '{self.LOCAL_MAP_FRAME}'. "
                    f"Tried '{source_frame}' and 'utm'."
                )
                self._node.get_logger().error(err_msg)
                raise

        in_map = do_transform_pose_stamped(in_utm_pose, tf)
        in_map.pose.position.z = gp.altitude  
        return in_map

    def convert_map_point_to_geopoint(self, x: float, y: float, z: float = 0.0) -> GeoPoint:
        in_map = PoseStamped()
        in_map.header.frame_id = self.LOCAL_MAP_FRAME
        in_map.pose.position.x = float(x)
        in_map.pose.position.y = float(y)
        in_map.pose.position.z = float(z)

        if not hasattr(self, '_utm_frame_cache') or self._utm_frame_cache is None:
            candidates = ['utm_33_V', 'utm'] + [f'utm_{i}' for i in range(1, 61)]
            source_frame = None
            for candidate in candidates:
                try:
                    self._tf_buffer.lookup_transform(
                        target_frame=candidate,
                        source_frame=self.LOCAL_MAP_FRAME,
                        time=Time(seconds=0),
                        timeout=Duration(seconds=0)
                    )
                    source_frame = candidate
                    break  
                except Exception:
                    continue
            if source_frame is None:
                raise RuntimeError(f"Could not find a TF from '{self.LOCAL_MAP_FRAME}' to any valid UTM frame.")
            self._utm_frame_cache = source_frame

        try:
            tf_inv = self._tf_buffer.lookup_transform(
                target_frame=self._utm_frame_cache,
                source_frame=self.LOCAL_MAP_FRAME,
                time=Time(seconds=0),
                timeout=Duration(seconds=1)
            )
        except Exception as e:
            self._utm_frame_cache = None  
            raise RuntimeError(f"Failed to transform map to {self._utm_frame_cache}: {e}")

        in_utm = do_transform_pose_stamped(in_map, tf_inv)
        in_utm.header.frame_id = self._utm_frame_cache
        return convert_utm_to_latlon(in_utm)