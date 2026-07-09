import math
import yaml
import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.time import Time
from rclpy.duration import Duration

from geometry_msgs.msg import PolygonStamped
from nav_msgs.msg import Odometry
from scipy.spatial.transform import Rotation as R
import tf2_ros

from dji_msgs.msg import Links, Topics, ObjectPoseWithCovarianceArray, ObjectEkfStatusArray

from dji_msgs.srv import ResetObjectEkf
from smarc_msgs.msg import Topics as SmarcTopics
from yolo_msgs.msg import DetectionWithCornersArray
from visualization_msgs.msg import Marker, MarkerArray

from .object_ekf import ObjectEKF

class MultiObjectEKFNode(Node):
    def __init__(self):
        super().__init__("multi_object_ekf_node")

        # Input
        self.declare_parameter("topics.input_detections_corners", "yolo/detections_with_corners")

        # Outputs for all estimated objects.
        self.declare_parameter("topics.output_poses_array", Topics.PROJECTED_OBJECT_POSES_ARRAY_TOPIC)
        self.declare_parameter("topics.status_array", Topics.OBJECT_EKF_STATUS_ARRAY_TOPIC)

        # Visualization
        self.declare_parameter("visualization_enable", True)
        self.declare_parameter("topics.markers", Topics.OBJECT_EKF_MARKERS_TOPIC)

        # Multi-object reset service.
        self.declare_parameter("services.reset", Topics.OBJECT_EKF_RESET_SERVICE)

        self.declare_parameter("robot_name", "M350")
        self.declare_parameter("frames.map", Links.MAP)
        self.declare_parameter("frames.camera", Links.GIMBAL_OPTICAL_FRAME)

        # Camera and EKF config files
        self.declare_parameter("base_params_file", "")
        self.declare_parameter("object_config_file", "")
        self.declare_parameter("camera_info", "")

        # Odom topic
        self.declare_parameter("topics.odom", SmarcTopics.ODOM_TOPIC)

        self.robot_name = self.get_parameter("robot_name").get_parameter_value().string_value.strip("/")

        map_frame = self.get_parameter("frames.map").get_parameter_value().string_value
        camera_frame = self.get_parameter("frames.camera").get_parameter_value().string_value

        self.map_frame = self.resolve_frame(map_frame)
        self.cam_frame = self.resolve_frame(camera_frame)

        base_params_file = self.get_parameter("base_params_file").get_parameter_value().string_value
        object_config_file = self.get_parameter("object_config_file").get_parameter_value().string_value
        camera_info_file = self.get_parameter("camera_info").get_parameter_value().string_value

        if base_params_file == "":
            raise RuntimeError("base_params_file must be set")

        if object_config_file == "":
            raise RuntimeError("object_config_file must be set")

        if camera_info_file == "":
            raise RuntimeError("camera_info parameter must be set")

        base_params = ObjectEKF.flatten_params(self.load_ros_params_yaml(base_params_file))
        object_config = self.load_ros_params_yaml(object_config_file)
        camera_info = self.load_camera_info(camera_info_file)

        self.input_detections_corners_topic = self.get_parameter("topics.input_detections_corners").get_parameter_value().string_value
        self.output_poses_array_topic = self.get_parameter("topics.output_poses_array").get_parameter_value().string_value
        self.status_array_topic = self.get_parameter("topics.status_array").get_parameter_value().string_value
        self.visualization_enable = self.get_parameter("visualization_enable").get_parameter_value().bool_value
        self.markers_topic = self.get_parameter("topics.markers").get_parameter_value().string_value
        self.reset_service_name = self.get_parameter("services.reset").get_parameter_value().string_value
        self.odom_topic = self.get_parameter("topics.odom").get_parameter_value().string_value
        
        self.tracks = {}

        classes = object_config.get("classes", object_config.get("objects", {}))

        # Create one EKF instance per configured class.
        # The ObjectEKF class contains the original single-object EKF logic.
        for class_name, cfg in classes.items():
            if not cfg.get("enabled", True):
                continue

            self.tracks[class_name] = ObjectEKF(
                class_name=class_name,
                cfg=cfg,
                base_params=base_params,
                camera_info=camera_info,
                logger=self.get_logger(),
            )

        if len(self.tracks) == 0:
            raise RuntimeError("No enabled objects found in object_config_file")

        # tf
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.current_R_map_cam = None
        self.lin_vel_map = np.zeros(3)
        self.ang_vel_map = np.zeros(3)

        # Publishers
        self.pub_poses = self.create_publisher(ObjectPoseWithCovarianceArray, self.output_poses_array_topic, 10)
        self.pub_status = self.create_publisher(ObjectEkfStatusArray, self.status_array_topic, 10)
        
        self.pub_markers = None
        if self.visualization_enable:
            self.pub_markers = self.create_publisher(MarkerArray, self.markers_topic, 10)

        # Subscribers
        self.sub_detections = self.create_subscription(DetectionWithCornersArray, self.input_detections_corners_topic, self.detections_cb, 10)
        self.sub_odom = self.create_subscription(Odometry, self.odom_topic, self.odom_cb, 10)

        # Reset service
        self.reset_srv = self.create_service(ResetObjectEkf, self.reset_service_name, self.handle_reset)

        self.status_timer = self.create_timer(0.5, self.publish_status_array)

        self.get_logger().info(
            "Multi-object EKF node started. "
            f"classes={list(self.tracks.keys())}, "
            f"map_frame={self.map_frame}, "
            f"cam_frame={self.cam_frame}, "
            f"input_detections_corners={self.input_detections_corners_topic}, "
            f"output_poses_array={self.output_poses_array_topic}, "
            f"status_array={self.status_array_topic}, "
            f"Markers visualization={self.visualization_enable}, "
            f"reset_service={self.reset_service_name}"
        )

    @staticmethod
    def load_ros_params_yaml(path):
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}

        if "/**" in data:
            return data["/**"].get("ros__parameters", {})

        return data

    @staticmethod
    def load_camera_info(path):
        with open(path, "r") as f:
            calib = yaml.safe_load(f) or {}

        return {
            "width": int(calib["image_width"]),
            "height": int(calib["image_height"]),
            "K": np.array(calib["camera_matrix"]["data"]).reshape(3, 3),
            "D": np.array(calib["distortion_coefficients"]["data"]),
        }

    def detections_cb(self, msg: DetectionWithCornersArray):
        # Shared detection callback.
        # Each configured ObjectEKF selects the best detection for its class.
        transform = self.lookup_camera_transform()

        if transform is None:
            return

        cam_pos_map, R_map_cam = self.transform_to_pose(transform)
        self.current_R_map_cam = R_map_cam

        now = self.get_clock().now()

        for track in self.tracks.values():
            best_det = self.find_best_detection(track, msg.detections)

            if best_det is None:
                continue

            poly_msg = PolygonStamped()
            poly_msg.header = msg.header
            poly_msg.header.frame_id = self.cam_frame
            poly_msg.polygon = best_det.bbox.normalized_corners

            track.last_detection_score = float(best_det.score)

            track.z(
                msg=poly_msg,
                cam_pos_map=cam_pos_map,
                R_map_cam=R_map_cam,
                lin_vel_map=self.lin_vel_map,
                ang_vel_map=self.ang_vel_map,
                now=now,
            )

        stamp = msg.header.stamp

        if stamp.sec == 0 and stamp.nanosec == 0:
            stamp = self.get_clock().now().to_msg()

        self.publish_pose_array(stamp)

    def find_best_detection(self, track, detections):
        best_det = None
        best_score = -1.0

        for det in detections:
            if not track.matches_detection(det):
                continue

            score = float(det.score)

            if score < track.confidence_threshold:
                continue

            if len(det.bbox.normalized_corners.points) < 4:
                continue

            if score > best_score:
                best_score = score
                best_det = det

        return best_det

    def lookup_camera_transform(self):
        # Use latest available TF instead of exact measurement time.
        # This avoids lookup-in-the-future problems when images arrive faster than TF.
        check_time = Time(seconds=0)
        check_duration = Duration(seconds=1)
        try:
            return self.tf_buffer.lookup_transform(self.map_frame, self.cam_frame, check_time, check_duration)
        except Exception as e:
            self.get_logger().warn(
                f"Cant transform from {self.cam_frame} to {self.map_frame}, dropping msg."
            )
            self.get_logger().warn(f"Transform error: {e}")
            return None

    @staticmethod
    def transform_to_pose(transform):
        t = transform.transform.translation
        q = transform.transform.rotation

        cam_pos_map = np.array([t.x, t.y, t.z])  # Actually the optical frame
        R_map_cam = R.from_quat([q.x, q.y, q.z, q.w]).as_matrix()

        return cam_pos_map, R_map_cam

    def odom_cb(self, msg: Odometry):
        if self.current_R_map_cam is None:
            return
        self.lin_vel_map = self.current_R_map_cam @ np.array([-msg.twist.twist.linear.x, msg.twist.twist.linear.y, msg.twist.twist.linear.z])
        self.ang_vel_map = self.current_R_map_cam @ np.array([-msg.twist.twist.angular.x, msg.twist.twist.angular.y, msg.twist.twist.angular.z])

    def publish_pose_array(self, stamp):
        out = ObjectPoseWithCovarianceArray()
        out.header.stamp = stamp
        out.header.frame_id = self.map_frame

        marker_array = MarkerArray()

        if self.visualization_enable:
            # Clear old markers every update.
            clear_marker = Marker()
            clear_marker.action = Marker.DELETEALL
            marker_array.markers.append(clear_marker)

        marker_id = 0

        for track in self.tracks.values():
            pose_msg = track.create_estimate_msg(stamp, self.map_frame)

            if pose_msg is None:
                continue

            out.objects.append(pose_msg)

            if self.visualization_enable:
                markers = self.make_object_markers(
                    pose_msg=pose_msg,
                    marker_id_start=marker_id,
                )

                marker_array.markers.extend(markers)
                marker_id += 10

        self.pub_poses.publish(out)

        if self.visualization_enable and self.pub_markers is not None:
            self.pub_markers.publish(marker_array)

    def publish_status_array(self):
        now = self.get_clock().now()

        out = ObjectEkfStatusArray()
        out.header.stamp = now.to_msg()
        out.header.frame_id = self.map_frame

        for track in self.tracks.values():
            out.statuses.append(track.create_status_msg(now, self.map_frame))

        self.pub_status.publish(out)

    def make_object_markers(self, pose_msg, marker_id_start):
        markers = []

        stamp = pose_msg.header.stamp
        frame_id = pose_msg.header.frame_id

        x = pose_msg.pose.pose.position.x
        y = pose_msg.pose.pose.position.y
        z = pose_msg.pose.pose.position.z

        # Main object marker
        sphere = Marker()
        sphere.header.stamp = stamp
        sphere.header.frame_id = frame_id
        sphere.ns = pose_msg.class_name
        sphere.id = marker_id_start
        sphere.type = Marker.SPHERE
        sphere.action = Marker.ADD
        sphere.pose = pose_msg.pose.pose
        sphere.scale.x = 0.35
        sphere.scale.y = 0.35
        sphere.scale.z = 0.35
        sphere.color.r = 0.0
        sphere.color.g = 1.0
        sphere.color.b = 0.0
        sphere.color.a = 1.0
        markers.append(sphere)

        # Text label
        text = Marker()
        text.header.stamp = stamp
        text.header.frame_id = frame_id
        text.ns = pose_msg.class_name
        text.id = marker_id_start + 1
        text.type = Marker.TEXT_VIEW_FACING
        text.action = Marker.ADD
        text.pose.position.x = x
        text.pose.position.y = y
        text.pose.position.z = z + 0.6
        text.scale.z = 0.35
        text.color.r = 1.0
        text.color.g = 1.0
        text.color.b = 1.0
        text.color.a = 1.0
        text.text = f"{pose_msg.class_name}"
        markers.append(text)

        # 2D covariance ellipse in XY
        try:
            cov = np.array(pose_msg.pose.covariance, dtype=float)
            if cov.size != 36:
                raise ValueError("covariance size is not 36")

            cov = cov.reshape(6, 6)
            cov_xy = np.nan_to_num(cov[:2, :2], nan=1e-6, posinf=1e-6, neginf=1e-6)
            cov_xy = 0.5 * (cov_xy + cov_xy.T)

            eigvals, eigvecs = np.linalg.eigh(cov_xy)
            eigvals = np.clip(eigvals, 1e-6, None)

            order = np.argsort(eigvals)[::-1]
            eigvals = eigvals[order]
            eigvecs = eigvecs[:, order]

            major = 2.0 * math.sqrt(max(eigvals[0], 1e-6)) * 1.2
            minor = 2.0 * math.sqrt(max(eigvals[1], 1e-6)) * 1.2

            yaw = math.atan2(eigvecs[1, 0], eigvecs[0, 0])
            q = R.from_euler("z", yaw).as_quat()

            ellipse = Marker()
            ellipse.header.stamp = stamp
            ellipse.header.frame_id = frame_id
            ellipse.ns = pose_msg.class_name
            ellipse.id = marker_id_start + 2
            ellipse.type = Marker.CYLINDER
            ellipse.action = Marker.ADD

            ellipse.pose.position.x = x
            ellipse.pose.position.y = y
            ellipse.pose.position.z = z + 0.02
            ellipse.pose.orientation.x = q[0]
            ellipse.pose.orientation.y = q[1]
            ellipse.pose.orientation.z = q[2]
            ellipse.pose.orientation.w = q[3]

            ellipse.scale.x = major
            ellipse.scale.y = minor
            ellipse.scale.z = 0.03

            ellipse.color.r = 1.0
            ellipse.color.g = 1.0
            ellipse.color.b = 0.0
            ellipse.color.a = 0.35

            markers.append(ellipse)

        except Exception as e:
            self.get_logger().warn(f"Could not create covariance marker: {e}")

        # Visualize the pose orientation as an arrow
        arrow = Marker()
        arrow.header.stamp = stamp
        arrow.header.frame_id = frame_id
        arrow.ns = pose_msg.class_name
        arrow.id = marker_id_start + 3
        arrow.type = Marker.ARROW
        arrow.action = Marker.ADD
        arrow.pose.position.x = x
        arrow.pose.position.y = y
        arrow.pose.position.z = z
        arrow.pose.orientation = pose_msg.pose.pose.orientation
        arrow.scale.x = 0.6
        arrow.scale.y = 0.08
        arrow.scale.z = 0.08
        arrow.color.r = 0.0
        arrow.color.g = 0.0
        arrow.color.b = 1.0
        arrow.color.a = 0.9
        markers.append(arrow)

        return markers

    def handle_reset(self, request, response):
        target = request.class_name.strip()

        if target == "":
            response.success = False
            response.message = (
                "class_name must not be empty. "
                "Use class_name='all' to reset all EKFs."
            )
            return response

        if target == "all":
            for track in self.tracks.values():
                track.reset_filter()

            response.success = True
            response.message = "Reset all object EKFs"
            return response

        if target not in self.tracks:
            response.success = False
            response.message = (
                f"Unknown class_name: {target}. "
                f"Available classes: {list(self.tracks.keys())}"
            )
            return response

        self.tracks[target].reset_filter()

        response.success = True
        response.message = f"Reset EKF for class_name={target}"
        return response

    def resolve_frame(self, frame):
        frame = str(frame).strip("/")

        if self.robot_name == "":
            return frame

        if frame.startswith(f"{self.robot_name}/"):
            return frame

        return f"{self.robot_name}/{frame}"


def main(args=None):
    rclpy.init(args=args)
    node = MultiObjectEKFNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()