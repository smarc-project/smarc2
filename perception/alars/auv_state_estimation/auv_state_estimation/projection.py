import rclpy
from rclpy.time import Time, Duration
import numpy as np
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo
import tf2_ros
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
from scipy.spatial.transform import Rotation as R
from geometry_msgs.msg import PolygonStamped, Point32

from dji_msgs.msg import Links, Topics


class ProjectionNode(Node):
    def __init__(self, name = 'projection_node'):
        super().__init__(name)
        
        self.declare_parameters(
            namespace="",
            parameters=[
                ("z_water", 0.0),
                ("topics.camera_info", Topics.GIMBAL_CAMERA_INFO_TOPIC),
                ("topics.input_polygon", Topics.ESTIMATED_AUV_OBB_TOPIC),
                ("topics.output_projected_polygon", Topics.PROJECTED_AUV_OBB_TOPIC),
                ("topics.rviz.camera_rays", "rviz/projection_rays"),
                ("frames.map", Links.MAP),                      
                ("frames.camera", Links.GIMBAL_OPTICAL_FRAME), 
                ])

        self.marker_ns = self.get_name() # ns fro rviz ray markers

        # Parameters
        self.z_water = float(self.get_parameter("z_water").value)  # water plane height in map frame
        # Topics
        self.topic_camera_info = self.get_parameter("topics.camera_info").value
        self.topic_rays = self.get_parameter("topics.rviz.camera_rays").value
        self.topic_in_poly  = self.get_parameter("topics.input_polygon").value
        self.topic_out_poly = self.get_parameter("topics.output_projected_polygon").value

        # Frames
        map_frame = self.get_parameter("frames.map").value
        cam_frame = self.get_parameter("frames.camera").value

        namespace = self.get_namespace().strip("/")
        self.map_frame = f'{namespace}/{map_frame}' 
        self.cam_frame = f'{namespace}/{cam_frame}' 

        # Cam parameters
        self.cam_info = False
        self.K_inv = None
        self.width = None
        self.height = None
        
        # tf
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        # Publishers
        self.ray_pub  = self.create_publisher(Marker, self.topic_rays, 10)
        self.pub_poly  = self.create_publisher(PolygonStamped, self.topic_out_poly, 10)

        # Subscribers
        self.sub_cam = self.create_subscription(CameraInfo, self.topic_camera_info, self.cam_info_cb, 10)
        self.sub_poly = self.create_subscription(PolygonStamped, self.topic_in_poly, self.project, 10)

    def cam_info_cb(self, msg: CameraInfo):

        # Callback for cam info, only needed once.
        if self.cam_info:  # cam info already received
            return
        self.width = msg.width
        self.height = msg.height
        K = np.array(msg.k).reshape((3, 3))  # cam intrinsic matrix
        try:
            self.K_inv = np.linalg.inv(K)
        except np.linalg.LinAlgError:
            self.get_logger().error(f"Camera intrinsic matrix is singular, cannot invert...\nK was: {K}\nCheck CameraInfo message on topic {self.topic_camera_info}")
            return
        self.cam_info = True
        self.get_logger().info(f"CameraInfo received: {self.width}x{self.height}, K={K}")
    
    def project(self, msg: PolygonStamped):
        # Projects head and obb points from image to 3d points on water plane
        if not self.cam_info:
            self.get_logger().warning("No CameraInfo received yet")
            return
        
        # use zero time to get the lastest available instead of the exact stamp of the image
        # image might be coming faster than TF updates for reasons, and using stamp of image
        # to get TF causes "lookup in the future" errors.
        try:
            transform = self.tf_buffer.lookup_transform(self.map_frame, self.cam_frame, Time(seconds=0), timeout=Duration(seconds=1))
        except Exception as e:
            self.get_logger().info(f"TF lookup failed ({self.cam_frame} -> {self.map_frame}): {e}")
            return
        
        t = transform.transform.translation
        cam_pos_map = np.array([t.x, t.y, t.z])  # camera position in map frame

        q = transform.transform.rotation
        rot = R.from_quat([q.x, q.y, q.z, q.w]).as_matrix()

        # pixelcoords from normalized image coords
        points_im = np.array([(p.x, p.y) for p in msg.polygon.points])
        u = (points_im[:, 0] + 1.0) * 0.5 * self.width
        v = (points_im[:, 1] + 1.0) * 0.5 * self.height

        ray_im = self.K_inv @ np.vstack((u, v, np.ones_like(u))) # projection from pixel to 3D ray in image frame (pc = K_inv @ xs)
        ray_map = rot @ ray_im # rotate ray to map frame
        
        dz = ray_map[2, :]
        if np.any(dz > -1e-2):  # if the z component of the norm ray is positive or close to zero, it means the ray is parallel to or pointing away from the water plane
            self.get_logger().info(f"Projection doesn't intersect with water surface")
            return
        
        t_intersect = (self.z_water - cam_pos_map[2]) / dz # translation along ray to intersect with water
        intersection_points_map = cam_pos_map[:, None] + ray_map * t_intersect  # intersection points in map frame
        intersection_points_cam = ray_im * t_intersect  # intersection points in cam frame
        
        now: Time = self.get_clock().now()
        self.publish_poly(now, intersection_points_map.T)
        self.publish_ray_marker(now, np.mean(intersection_points_cam, axis=1))

    def publish_ray_marker(self, stamp:Time, intersection_point):
        # publish projected line (ray) for rviz
        marker = Marker()
        marker.header.frame_id = self.cam_frame
        marker.header.stamp = stamp.to_msg()
        marker.ns = self.marker_ns
        marker.id = 0
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD
        marker.scale.x = 0.02  
        marker.color.a = 1.0
        marker.color.r = 1.0  
        p0 = Point(x=0.0, y=0.0, z=0.0)
        p1 = Point(x=intersection_point[0], y=intersection_point[1], z=intersection_point[2])
        marker.points.append(p0)
        marker.points.append(p1)
        self.ray_pub.publish(marker)
    
    def publish_poly(self, stamp:Time, points): 
        # Publish head pose and obb corners (may be used for filter)
        obb_marker = PolygonStamped()
        obb_marker.header.frame_id = self.map_frame
        obb_marker.header.stamp = stamp.to_msg()
        for px, py, pz in points:
            point32 = Point32()
            point32.x = px
            point32.y = py
            point32.z = pz
            obb_marker.polygon.points.append(point32)
        self.pub_poly.publish(obb_marker)


def main():
    rclpy.init()
    node = ProjectionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
