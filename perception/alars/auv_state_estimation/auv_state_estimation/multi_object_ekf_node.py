import math
import yaml
import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.time import Time
from rclpy.duration import Duration
from rclpy.executors import MultiThreadedExecutor

from nav_msgs.msg import Odometry
from scipy.spatial.transform import Rotation as R
import tf2_ros

from dji_msgs.msg import Links, Topics, ObjectPoseWithCovarianceArray, ObjectEkfStatusArray

from dji_msgs.srv import ResetObjectEkf
from smarc_msgs.msg import Topics as SmarcTopics
from yolo_msgs.msg import DetectionArray
from visualization_msgs.msg import Marker, MarkerArray

from .object_ekf import ObjectEKF

class MultiObjectEKFNode(Node):
    def __init__(self, **node_kwargs):
        super().__init__("multi_object_ekf_node", **node_kwargs)

        # Input
        self.declare_parameter("topics.input_detections", Topics.YOLO_DETECTIONS)

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
        self.declare_parameter("pad_projection_debug", False)
        self.pad_projection_debug = bool(self.get_parameter("pad_projection_debug").value)
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

        self.input_detections_topic = self.get_parameter("topics.input_detections").get_parameter_value().string_value
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
        self.sub_detections = self.create_subscription(DetectionArray, self.input_detections_topic, self.detections_cb, 10)
        self.sub_odom = self.create_subscription(Odometry, self.odom_topic, self.odom_cb, 10)

        # Reset service
        self.reset_srv = self.create_service(ResetObjectEkf, self.reset_service_name, self.handle_reset)

        self.status_timer = self.create_timer(0.5, self.publish_status_array)

        self.get_logger().info(
            "Multi-object EKF node started. "
            f"classes={list(self.tracks.keys())}, "
            f"map_frame={self.map_frame}, "
            f"cam_frame={self.cam_frame}, "
            f"input_detections={self.input_detections_topic}, "
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

    @staticmethod
    def project_point_numpy(p_map, cam_pos_map, R_map_cam, K, D):
        """
        Project a 3D map-frame point into the image using
        the pinhole + plumb_bob distortion model.

        No OpenCV.
        """

        p_map = np.asarray(p_map, dtype=float).reshape(3)
        cam_pos_map = np.asarray(cam_pos_map, dtype=float).reshape(3)

        # map -> optical camera
        p_cam = R_map_cam.T @ (p_map - cam_pos_map)
        X, Y, Z = p_cam

        if Z <= 1e-6:
            return None

        # Normalized pinhole coordinates
        x = X / Z
        y = Y / Z

        # Brown-Conrady / ROS plumb_bob distortion
        # D = [k1, k2, p1, p2, k3]
        coeffs = np.zeros(5)
        D_flat = np.asarray(D, dtype=float).reshape(-1)
        coeffs[:min(5, len(D_flat))] = D_flat[:5]
        k1, k2, p1, p2, k3 = coeffs

        r2 = x * x + y * y
        r4 = r2 * r2
        r6 = r4 * r2
        radial = 1.0 + k1 * r2 + k2 * r4 + k3 * r6
        x_dist = x * radial + 2.0 * p1 * x * y + p2 * (r2 + 2.0 * x * x)
        y_dist = y * radial + p1 * (r2 + 2.0 * y * y) + 2.0 * p2 * x * y
        pixel_h = K @ np.array([x_dist, y_dist, 1.0])

        return pixel_h[:2]

    @staticmethod
    def min_area_rect_numpy(points):
        """
        NumPy-only minimum-area oriented rectangle for
        an ordered convex polygon.

        Returns:
            center_uv
            size_uv
            angle_rad
        """

        pts = np.asarray(points, dtype=float)

        if len(pts) < 2:
            return None

        best_area = np.inf
        best_center = None
        best_size = None
        best_angle = None
        n = len(pts)

        for i in range(n):
            p0 = pts[i]
            p1 = pts[(i + 1) % n]
            edge = p1 - p0

            if np.linalg.norm(edge) < 1e-9:
                continue

            theta = np.arctan2(edge[1], edge[0])
            c = np.cos(theta)
            s = np.sin(theta)

            # Rotate points so this edge aligns with x axis.
            R2 = np.array([[c, s], [-s, c]])
            pts_rot = (R2 @ pts.T).T
            pmin = pts_rot.min(axis=0)
            pmax = pts_rot.max(axis=0)
            size = pmax - pmin
            area = size[0] * size[1]

            if area < best_area:
                center_rot = 0.5 * (pmin + pmax)

                # Rotate back.
                center = R2.T @ center_rot
                best_area = area
                best_center = center
                best_size = size
                best_angle = theta

        if best_center is None:
            return None

        return (best_center, best_size, best_angle)

    def detections_cb(self, msg: DetectionArray):
        # Shared detection callback.
        # Each configured ObjectEKF selects the best detection for its class.
        stamp = msg.header.stamp

        if stamp.sec == 0 and stamp.nanosec == 0:
            stamp = self.get_clock().now().to_msg()

        transform = self.lookup_camera_transform(stamp)

        if transform is None:
            return

        cam_pos_map, R_map_cam = self.transform_to_pose(transform)
        self.current_R_map_cam = R_map_cam

        now = self.get_clock().now()
        measurement_time = Time.from_msg(stamp)
        detection_age_s = (now - measurement_time).nanoseconds * 1e-9
        self.get_logger().info(f"Detection age: {detection_age_s:.3f} s", throttle_duration_sec=2.0)

        for track in self.tracks.values():
            best_det = self.find_best_detection(track, msg.detections)

            if best_det is None:
                continue

            track.last_detection_score = float(best_det.score)

            track.z(
                det=best_det,
                stamp=stamp,
                cam_pos_map=cam_pos_map,
                R_map_cam=R_map_cam,
                lin_vel_map=self.lin_vel_map,
                ang_vel_map=self.ang_vel_map,
                now=now,
            )
            center_uv = np.array([
                float(best_det.bbox.center.position.x),
                float(best_det.bbox.center.position.y),
            ])
            if track.class_name == "land_pad" and self.pad_projection_debug:
                center_uv = np.array([
                    float(best_det.bbox.center.position.x),
                    float(best_det.bbox.center.position.y),
                ])

                ray = track.measurement_model.back_projection(center_uv, R_map_cam)

                direct_point = track.initializer.point_on_line_at_z(
                    cam_pos_map,
                    ray,
                    track.water_surface_height,
                )

                # Unity ground-truth landing-pad center, used only for diagnostics.
                gt_point = None
                gt_uv = None

                try:
                    gt_tf = self.tf_buffer.lookup_transform(
                        self.map_frame,
                        "Milou/landing_pad_link",
                        Time.from_msg(stamp),
                        timeout=Duration(seconds=0.05),
                    )

                    gt_t = gt_tf.transform.translation
                    gt_point = np.array([gt_t.x, gt_t.y, gt_t.z])
                    gt_uv = track.measurement_model.projection(gt_point, cam_pos_map, R_map_cam)

                    # Project the true deck rectangle into the image.
                    q_gt = gt_tf.transform.rotation
                    R_map_pad = R.from_quat([q_gt.x, q_gt.y, q_gt.z, q_gt.w]).as_matrix()
                    L = track.obb_length_m
                    W = track.obb_width_m

                    # Flat rectangle in landing-pad local coordinates.
                    corners_pad = np.array([
                        [+L / 2.0, +W / 2.0, 0.0],
                        [+L / 2.0, -W / 2.0, 0.0],
                        [-L / 2.0, -W / 2.0, 0.0],
                        [-L / 2.0, +W / 2.0, 0.0],
                    ])

                    # Transform pad corners into the configured map frame.
                    corners_map = (R_map_pad @ corners_pad.T).T + gt_point
                    corners_uv = []

                    for p_map in corners_map:
                        uv = self.project_point_numpy(
                            p_map=p_map,
                            cam_pos_map=cam_pos_map,
                            R_map_cam=R_map_cam,
                            K=track.measurement_model.K,
                            D=track.measurement_model.D,
                        )

                        if uv is not None:
                            corners_uv.append(uv)
                    if len(corners_uv) == 4:
                        corners_uv = np.asarray(corners_uv)
                        rect_result = self.min_area_rect_numpy(corners_uv)

                        if rect_result is not None:
                            (gt_obb_center, gt_obb_size, gt_obb_angle) = rect_result
                            du = center_uv[0] - gt_obb_center[0]
                            dv = center_uv[1] - gt_obb_center[1]
                            pixel_error = np.hypot(du, dv)

                            self.get_logger().info(
                                "LAND_PAD FLAT GT: "
                                f"det_uv=({center_uv[0]:.1f},{center_uv[1]:.1f}) "
                                f"gt_obb_uv=({gt_obb_center[0]:.1f},{gt_obb_center[1]:.1f}) "
                                f"det_size=({best_det.bbox.size.x:.1f},{best_det.bbox.size.y:.1f}) "
                                f"gt_size=({gt_obb_size[0]:.1f},{gt_obb_size[1]:.1f}) "
                                f"du={du:.1f}px "
                                f"dv={dv:.1f}px "
                                f"err={pixel_error:.1f}px",
                                throttle_duration_sec=0.5,
                            )

                except Exception as e:
                    self.get_logger().warn(f"Could not get landing-pad GT: {e}")

                if direct_point is not None:
                    msg_str = (
                        "LAND_PAD DEBUG: "
                        f"det_uv=({center_uv[0]:.1f},{center_uv[1]:.1f}) "
                        f"direct_xyz=({direct_point[0]:.3f},"
                        f"{direct_point[1]:.3f},"
                        f"{direct_point[2]:.3f})"
                    )

                    if gt_point is not None:
                        direct_error = np.linalg.norm(direct_point[:2] - gt_point[:2])

                        msg_str += (
                            f" gt_xyz=({gt_point[0]:.3f},"
                            f"{gt_point[1]:.3f},"
                            f"{gt_point[2]:.3f})"
                            f" xy_err={direct_error:.3f}m"
                        )

                    if gt_uv is not None:
                        du = center_uv[0] - gt_uv[0]
                        dv = center_uv[1] - gt_uv[1]
                        pixel_error = np.linalg.norm([du, dv])

                        msg_str += (
                            f" gt_uv=({gt_uv[0]:.1f},{gt_uv[1]:.1f})"
                            f" du={du:.1f}px"
                            f" dv={dv:.1f}px"
                            f" pixel_err={pixel_error:.1f}px"
                        )

                    self.get_logger().info(msg_str, throttle_duration_sec=0.5)

            ray = track.measurement_model.back_projection(center_uv, R_map_cam)

            direct_point = track.initializer.point_on_line_at_z(
                cam_pos_map,
                ray,
                track.water_surface_height,
            )

            if (
                track.class_name == "land_pad"
                and self.pad_projection_debug
                and direct_point is not None
            ):
                self.get_logger().info(
                    "LAND_PAD DIRECT: "
                    f"x={direct_point[0]:.3f}, "
                    f"y={direct_point[1]:.3f}, "
                    f"z={direct_point[2]:.3f}"
                )

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

            if float(det.bbox.size.x) <= 0.0 or float(det.bbox.size.y) <= 0.0:
                continue

            if score > best_score:
                best_score = score
                best_det = det

        return best_det

    def lookup_camera_transform(self, stamp):
        # Use the exact image acquisition time. Latest TF is diagnostic only.
        measurement_time = Time.from_msg(stamp)
        try:
            return self.tf_buffer.lookup_transform(
                self.map_frame, self.cam_frame, measurement_time, Duration(seconds=0.25)
            )
        except Exception as e:
            now = self.get_clock().now()
            requested_s = measurement_time.nanoseconds * 1e-9
            now_s = now.nanoseconds * 1e-9
            latest_s = float("nan")
            tf_lag_s = float("nan")

            try:
                latest_tf = self.tf_buffer.lookup_transform(
                    self.map_frame,
                    self.cam_frame,
                    Time(),
                    timeout=Duration(seconds=0.0),
                )

                latest_time = Time.from_msg(latest_tf.header.stamp)
                latest_s = latest_time.nanoseconds * 1e-9
                tf_lag_s = (measurement_time - latest_time).nanoseconds * 1e-9

            except Exception:
                pass

            detection_age_s = (now - measurement_time).nanoseconds * 1e-9

            self.get_logger().warn(
                "\n"
                "TF lookup failed:\n"
                f"  requested detection time = {requested_s:.6f}\n"
                f"  latest TF time           = {latest_s:.6f}\n"
                f"  ROS now                  = {now_s:.6f}\n"
                f"  requested - latest TF    = {tf_lag_s:.3f} s\n"
                f"  now - detection          = {detection_age_s:.3f} s\n"
                f"  error: {e}"
            )

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
            track_stamp = (
                Time(nanoseconds=track.state_stamp_ns).to_msg()
                if track.state_stamp_ns is not None else stamp
            )
            pose_msg = track.create_estimate_msg(track_stamp, self.map_frame)

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
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
