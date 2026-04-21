from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2
import yaml
import numpy as np
from collections import deque
import rclpy
from rclpy.time import Time
from rclpy.node import Node
from geometry_msgs.msg import PointStamped, PolygonStamped, TransformStamped, PoseWithCovarianceStamped, Vector3Stamped
from std_msgs.msg import Float32MultiArray
from scipy.stats import chi2
import tf2_ros
from scipy.spatial.transform import Rotation as R

from .ekf_params import PARAMS

from .ekf_core import EKFCore
from .measurement_model import MeasurementModel
from .noise_models import NoiseModels
from .initializer import Initializer
from .visualization import create_pose_msg, create_transform_msg
from .geometry_utils import residual_z, wrap
from .motion_model import DepthModel9D, SurfaceModel5D, DepthModel7D, PitchModel9D

from std_srvs.srv import Trigger

class EKFNode(Node):
    def __init__(self):
        super().__init__("ekf_node")

        self.declare_parameters(namespace="", parameters=PARAMS)

        self.logger_info_enable = self.get_parameter("logger_info.enable").value
        
        self.get_params()

        self.motion_model = self.get_motion_model(self.motion_model_type)
        self.eps = self.motion_model.eps

        self.state_dim = self.motion_model.state_dim
        self.meas_dim = 3 if self.state_dim == 5 else 5
        self.outlier_threshold = chi2.ppf(self.gating_prob, df=self.meas_dim)

        # tf
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        # publishers and subscribers
        self.pub = self.create_publisher(PoseWithCovarianceStamped, self.topic_estimated_pose, 10)
        self.pub_status = self.create_publisher(Float32MultiArray, self.topic_ekf_status, 10) 

        self.sub_pose = self.create_subscription(PolygonStamped, self.topic_in_poly, self.poly_cb, 10)
        self.sub_lin_vel = self.create_subscription(Vector3Stamped, self.topic_linear_velocity, self.lin_vel_cb, 10)
        self.sub_ang_rate = self.create_subscription(Vector3Stamped, self.topic_angular_velocity, self.ang_rate_cb, 10)
        self.sub_head = self.create_subscription(PolygonStamped, self.topic_input_auv_head, self.head_cb, 10)

        self.reset_srv = self.create_service(Trigger, "alars_auv_ekf/reset", self.handle_reset_service)

        self.current_transform = None
        self.current_cam_pos_map = None
        self.current_R_map_cam = None
        self.flip_buffer = [-1]
        self.lin_vel_map = np.zeros(3)
        self.ang_vel_map = np.zeros(3)

        self.last_innovation_norm = -1.0

        self.initialize_components()

        self.get_logger().info(f"EKF node started. map_frame={self.map_frame}, cam_frame={self.cam_frame}, estimated_auv_frame={self.output_frame}")

        self.q = deque()
        self.timer = self.create_timer(0.01, self.process_q)
        self.status_timer = self.create_timer(0.5, self.publish_status)

    def log_info(self, msg):
        if self.logger_info_enable:
            self.get_logger().info(msg)

    def poly_cb(self, msg):
        arrival = self.get_clock().now()
        self.q.append((msg, arrival))

    def process_q(self):
        while self.q:
            msg, arrival = self.q[0]
            now = self.get_clock().now()
            stamp = Time.from_msg(msg.header.stamp)
            if self.tf_buffer.can_transform(self.map_frame, self.cam_frame, stamp):
                transform = self.tf_buffer.lookup_transform(self.map_frame, self.cam_frame, stamp)
                self.current_transform = transform
                t = transform.transform.translation
                q = transform.transform.rotation
                self.current_cam_pos_map = np.array([t.x, t.y, t.z]) # Actually the optical frame
                self.current_R_map_cam = R.from_quat([q.x, q.y, q.z, q.w]).as_matrix()
                self.current_R_map_cam = self.current_R_map_cam 
                self.q.popleft()
                self.z(msg, transform)
                continue

            wait_time = (now - arrival).nanoseconds * 1e-9
            if wait_time > 0.3:
                self.log_info(f"Dropping msg after waiting {wait_time:.3f}s for TF")
                self.q.popleft()
                continue

            break

    def pol_to_array(self, msg: PolygonStamped):
        # polygon -> array of normalized image coordinates
        return np.array([(p.x, p.y) for p in msg.polygon.points])

    def head_cb(self, msg: PolygonStamped):
        # simple voting-based logic to determine the direction of the auv's head.
        if (not self.ekf.initialized) or (self.current_cam_pos_map is None):
            return
        pts = self.pol_to_array(msg)
        uv_img = self.measurement_model.norm_to_pixels(self.pol_to_array(msg))
        ray = self.measurement_model.back_projection(uv_img[0], self.current_R_map_cam)
        if ray is None:
            return
        head = self.initializer.point_on_line_at_z(self.current_cam_pos_map, ray, self.z_water)
        yaw_axis_est = self.ekf.X[2, 0] if self.state_dim == 5 else self.ekf.X[3, 0]
        if head is None:
            return
        est_xy = np.array([self.ekf.X[0, 0], self.ekf.X[1, 0]])
        head_vec = head[:2] - est_xy
        yaw_head = np.arctan2(head_vec[1], head_vec[0])
        d0 = abs(wrap(yaw_head - yaw_axis_est))
        d1 = abs(wrap(yaw_head - (yaw_axis_est + np.pi)))
        vote = -1 if d0 <= d1 else +1
        self.flip_buffer.append(vote)
        if len(self.flip_buffer) > 10:
            self.flip_buffer.pop(0)

    def lin_vel_cb(self, msg: Vector3Stamped):
        # transforms and stores the linear velocity of the drone for use in dynamic measurement noise.
        # may be adjusted / removed in the future depending on how useful it proves to be and how noisy the measurements are.
        if self.current_R_map_cam is None:
            return
        self.lin_vel_map = self.current_R_map_cam @ np.array([-msg.vector.x, msg.vector.y, msg.vector.z])

    def ang_rate_cb(self, msg: Vector3Stamped):
        # same as for lin_vel_cb but for angular velocity.
        if self.current_R_map_cam is None:
            return
        self.ang_vel_map = self.current_R_map_cam @ np.array([-msg.vector.x, msg.vector.y, msg.vector.z])

    def predict_to_measurement_time(self, dt_total):
        # perfoems multiple prediction steps between measurements.
        # this should imporve predictions duering longer time gaps.

        dt_max = 0.1
        n_steps = max(1, int(np.ceil(dt_total / dt_max)))
        dt_step = dt_total / n_steps
        for _ in range(n_steps):
            X, F = self.motion_model.predict(self.ekf.X, dt_step)
            Q = self.motion_model.build_Q(dt_step)
            self.ekf.predict(X, F, Q, self.ekf.last_t + dt_step)
        return X
    

    def z(self, msg: PolygonStamped, transform: TransformStamped):
        # main callback for processing incoming measurements, performing EKF prediction and update, and publishing the estimated pose.
        stamp = msg.header.stamp
        t = stamp.sec + stamp.nanosec * 1e-9
        self.current_transform = transform
        
        z_center_img, z_alpha_img, z_len_px, z_wid_px, _ = self.measurement_model.extract_features(self.pol_to_array(msg))
        self.log_info(f"Received measurement: center={z_center_img}")
        if not self.ekf.initialized:
            init_result = self.initializer.try_initialize(stamp, z_center_img, z_alpha_img, self.measurement_model, self.current_cam_pos_map, self.current_R_map_cam)
            if init_result is None:
                return
            X0, P0, t0 = init_result
            self.ekf.set_state(X0, P0, t0)
            self.ekf.initialized = True
            self.log_info("Initialization complete")
            return
        if self.state_dim == 5:
            z = np.array([[z_center_img[0]], [z_center_img[1]], [z_alpha_img]])
        else:
            z = np.array([[z_center_img[0]], [z_center_img[1]], [z_alpha_img], [z_len_px], [z_wid_px]])
        dt = t - self.ekf.last_t

        X = self.predict_to_measurement_time(dt)

        h = self.measurement_model.hx(X, cam_pos_map=self.current_cam_pos_map, R_map_cam=self.current_R_map_cam)

        H = self.measurement_model.numerical_H(X, cam_pos_map=self.current_cam_pos_map, R_map_cam=self.current_R_map_cam)
        J_pose = self.measurement_model.numerical_J_pose(X, cam_pos_map=self.current_cam_pos_map, R_map_cam=self.current_R_map_cam)
        R_meas = self.noise_models.build_image_measurement_covariance(z_center_img, self.lin_vel_map) + self.noise_models.project_pose_covariance_to_measurement(J_pose, self.lin_vel_map, self.ang_vel_map)

        innov = residual_z(z, h).reshape(z.shape[0], 1)
        self.last_innovation_norm = np.linalg.norm(innov)  

        X, P = self.ekf.update(z, h, H, R_meas)
        self.log_info(f"Post-update state: {X.flatten()[:3]}")
        self.publish_estimate(stamp)
    
    def publish_estimate(self, stamp):
        # publishes the current state estimate as a PoseWithCovarianceStamped message and also broadcasts a TF.
        flip_decision = np.sum(self.flip_buffer)
        yaw_idx = 2 if self.state_dim == 5 else 3
        yaw_out = self.ekf.X[yaw_idx, 0] + (np.pi if (flip_decision > 0) else 0.0)
        yaw_out = wrap(yaw_out)
        if self.state_dim == 5:
            q = R.from_euler("z", yaw_out).as_quat()
        elif self.state_dim == 9:
            q = R.from_euler("xyz", [0, self.ekf.X[4, 0], yaw_out]).as_quat()
        else:
            q = R.from_euler("z", yaw_out).as_quat()
        self.pub.publish(create_pose_msg(stamp, q, self.map_frame, self.ekf.X, self.ekf.P, self.z_water))
        self.tf_broadcaster.sendTransform(create_transform_msg(stamp, q, self.map_frame, self.output_frame, self.ekf.X, self.z_water))

    def publish_status(self):
        # publishes information regarding the status of the filter.
        # nr of consecutive outliers is probably a good indication of the status.
        # may want to exanp thi.
        msg = Float32MultiArray()
        now = self.get_clock().now().nanoseconds * 1e-9
        if self.ekf.last_t is None:
            time_since_last_meas = 0.0
        else:
            time_since_last_meas = now - self.ekf.last_t

        cov_trace = np.trace(self.ekf.P) if self.ekf.P is not None else -1.0
        if not self.ekf.initialized:
            initialized = 0.0
        else:
            initialized = 1.0
        innovation_norm = getattr(self, "last_innovation_norm", -1.0)
        msg.data = [
            initialized,    # 0 = not initialized, 1 = initialized
            time_since_last_meas,
            cov_trace,
            innovation_norm,
            float(self.ekf.nr_of_consecutive_outliers)]

        self.pub_status.publish(msg)

    def handle_reset_service(self, request, response):
        self.reset_filter()
        response.success = True
        response.message = "EKF reset successfully."
        return response
    
    def reset_filter(self):
        self.ekf = EKFCore(
            self.z_water,
            state_dim=self.state_dim,
            outlier_threshold=self.outlier_threshold,
            #logger=self.get_logger(),
        )

        self.flip_buffer = [-1]
        self.current_transform = None
        self.current_cam_pos_map = None
        self.current_R_map_cam = None
        self.lin_vel_map = np.zeros(3)
        self.ang_vel_map = np.zeros(3)
        self.q.clear()
        self.get_logger().info("EKF internal state reset.")

    def get_motion_model(self, model_type):
        if model_type == "surface":
            return SurfaceModel5D(
                sigma_a=self.sigma_a,
                sigma_yaw=self.sigma_yaw,
            )
        elif model_type == "depth":
            return DepthModel7D(
                sigma_a=self.sigma_a,
                sigma_z=self.sigma_z,
                sigma_yaw=self.sigma_yaw,
            )
        elif model_type == "pitch":
            return PitchModel9D(
                sigma_a=self.sigma_a,
                sigma_z=self.sigma_z,
                sigma_yaw=self.sigma_yaw,
                sigma_pitch=self.sigma_pitch,
            )
        elif model_type == "depth9d":
            return DepthModel9D(
                sigma_a=self.sigma_a,
                sigma_z=self.sigma_z,
                sigma_yaw=self.sigma_yaw,
            )
        else:
            raise ValueError(f"Unknown motion model type: {model_type}")
        
    def initialize_components(self):
        self.initializer = Initializer(
            z_water=self.z_water,
            state_dim=self.state_dim,
            init_z_needed=self.init_z_needed,
            init_pos_max_spread=self.init_pos_max_spread,
            init_yaw_max_spread=self.init_yaw_max_spread,
            init_z_max_spread=self.init_z_max_spread,
            init_max_depth=self.init_max_depth,
            init_depth_steps=self.init_depth_steps,
            alpha_line_pixels=self.alpha_line_pixels,
            R_len=self.R_len,
            R_wid=self.R_wid,
            R_alpha=self.R_alpha,
            motion_model=self.motion_model_type,
            logger=self.get_logger(),
        )
        self.measurement_model = MeasurementModel(
            meas_dim=self.meas_dim,
            state_dim=self.state_dim,
            eps=self.eps,
            eps_pose_pos=self.eps_pose_pos,
            eps_pose_ang=self.eps_pose_ang,
            width=self.width,
            height=self.height,
            K=self.K,
            D=self.D,
            z_water=self.z_water,
            n_air=self.n_air,
            n_water=self.n_water,
            obb_length_m=self.obb_length_m,
            obb_width_m=self.obb_width_m,
            motion_model=self.motion_model,
            #logger=self.get_logger(),
        )

        self.noise_models = NoiseModels(
            width=self.width,
            height=self.height,
            R_u=self.R_u,
            R_v=self.R_v,
            R_alpha=self.R_alpha,   
            R_len=self.R_len,
            R_wid=self.R_wid,
            R_pose_x=self.R_pose_x,
            R_pose_y=self.R_pose_y,
            R_pose_z=self.R_pose_z,
            R_pose_r=self.R_pose_r,
            R_pose_p=self.R_pose_p,
            R_pose_yaw=self.R_pose_yaw,
            R_dyn_center_gain_u=self.R_dyn_center_gain_u,
            R_dyn_center_gain_v=self.R_dyn_center_gain_v,
            R_dyn_center_gain_alpha=self.R_dyn_center_gain_alpha,
            R_dyn_center_gain_len=self.R_dyn_center_gain_len,
            R_dyn_center_gain_wid=self.R_dyn_center_gain_wid,
            R_dyn_speed_gain_u=self.R_dyn_speed_gain_u,
            R_dyn_speed_gain_v=self.R_dyn_speed_gain_v,
            R_dyn_speed_gain_alpha=self.R_dyn_speed_gain_alpha,
            R_dyn_speed_gain_len=self.R_dyn_speed_gain_len,
            R_dyn_speed_gain_wid=self.R_dyn_speed_gain_wid,
            R_dyn_dt=self.R_dyn_dt,
            meas_dim=self.meas_dim,
        )
        self.ekf = EKFCore(
            self.z_water,
            state_dim=self.state_dim,
            outlier_threshold=self.outlier_threshold,
            logger=self.get_logger(),   
        )

    def get_params(self):
        self.z_water = self.get_parameter("z_water").value
        self.n_air = self.get_parameter("n_air").value
        self.n_water = self.get_parameter("n_water").value

        self.obb_length_m = self.get_parameter("obb.length_m").value
        self.obb_width_m = self.get_parameter("obb.width_m").value
        self.alpha_line_pixels = self.get_parameter("alpha_line_pixels").value

        self.sigma_a = self.get_parameter("sigma_a").value
        self.sigma_z = self.get_parameter("sigma_z_process").value
        self.sigma_yaw = np.deg2rad(self.get_parameter("sigma_yaw_process").value)
        self.sigma_pitch = np.deg2rad(self.get_parameter("sigma_pitch_acc_deg").value)
        self.R_u = self.get_parameter("R_u").value
        self.R_v = self.get_parameter("R_v").value
        self.R_alpha = np.deg2rad(float(self.get_parameter("R_alpha_deg").value))
        self.R_len = self.get_parameter("R_len").value
        self.R_wid = self.get_parameter("R_wid").value

        self.R_pose_x = self.get_parameter("R_pose_x").value
        self.R_pose_y = self.get_parameter("R_pose_y").value
        self.R_pose_z = self.get_parameter("R_pose_z").value
        self.R_pose_r = np.deg2rad(self.get_parameter("R_pose_r").value)
        self.R_pose_p = np.deg2rad(self.get_parameter("R_pose_p").value)
        self.R_pose_yaw = np.deg2rad(self.get_parameter("R_pose_yaw").value)

        self.R_dyn_center_gain_u = self.get_parameter("R_dyn.center_gain_u").value
        self.R_dyn_center_gain_v = self.get_parameter("R_dyn.center_gain_v").value
        self.R_dyn_center_gain_alpha = np.deg2rad(self.get_parameter("R_dyn.center_gain_alpha_deg").value)
        self.R_dyn_center_gain_len = self.get_parameter("R_dyn.center_gain_len").value
        self.R_dyn_center_gain_wid = self.get_parameter("R_dyn.center_gain_wid").value

        self.R_dyn_speed_gain_u = self.get_parameter("R_dyn.speed_gain_u").value
        self.R_dyn_speed_gain_v = self.get_parameter("R_dyn.speed_gain_v").value
        self.R_dyn_speed_gain_alpha = np.deg2rad(self.get_parameter("R_dyn.speed_gain_alpha_deg").value)
        self.R_dyn_speed_gain_len = self.get_parameter("R_dyn.speed_gain_len").value
        self.R_dyn_speed_gain_wid = self.get_parameter("R_dyn.speed_gain_wid").value

        self.R_dyn_dt = self.get_parameter("R_dyn_dt").value

        self.init_z_needed = self.get_parameter("init_z_needed").value
        self.init_pos_max_spread = self.get_parameter("init_pos_max_spread").value
        self.init_yaw_max_spread = self.get_parameter("init_yaw_max_spread").value
        self.init_z_max_spread = self.get_parameter("init_z_max_spread").value
        self.init_min_depth = self.get_parameter("init_min_depth").value
        self.init_max_depth = self.get_parameter("init_max_depth").value
        self.init_depth_steps = self.get_parameter("init_depth_steps").value

        self.gating_prob = self.get_parameter("gating.prob").value

        self.eps_state_pos = self.get_parameter("jacobian.eps_state_pos").value
        self.eps_state_yaw = self.get_parameter("jacobian.eps_state_yaw").value
        self.eps_state_vel = self.get_parameter("jacobian.eps_state_vel").value
        self.eps_pose_pos = self.get_parameter("jacobian.eps_pose_pos").value
        self.eps_pose_ang = self.get_parameter("jacobian.eps_pose_ang").value

        self.topic_in_poly = self.get_parameter("topics.input_polygon").value
        self.topic_input_auv_head = self.get_parameter("topics.input_auv_head").value
        self.topic_estimated_pose = self.get_parameter("topics.output_topic").value
        self.topic_linear_velocity = self.get_parameter("topics.linear_velocity").value
        self.topic_angular_velocity = self.get_parameter("topics.angular_velocity").value
        self.topic_ekf_status = self.get_parameter("topics.ekf_status").value

        namespace = self.get_namespace().strip("/")
        map_frame = self.get_parameter("frames.map").value
        output_frame = self.get_parameter("frames.output_link").value
        camera_frame = self.get_parameter("frames.camera").value

        self.map_frame = f"{namespace}/{map_frame}"
        self.output_frame = f"{namespace}/{output_frame}"
        self.cam_frame = f"{namespace}/{camera_frame}"

        self.width = None
        self.height = None
        self.K = None
        self.D = None

        cam_info_path = self.get_parameter("camera_info").value
        if cam_info_path:
            with open(cam_info_path, "r") as f:
                calib = yaml.safe_load(f.read())
            self.width = calib["image_width"]
            self.height = calib["image_height"]
            self.K = np.array(calib["camera_matrix"]["data"]).reshape(3, 3)
            self.D = np.array(calib["distortion_coefficients"]["data"])
            self.get_logger().info(f"Loaded CameraInfo from yaml: {self.width}x{self.height}")
        else:
            raise RuntimeError("camera_info parameter must be set")
        
        self.motion_model_type = self.get_parameter("motion_model").value


def main():
    rclpy.init()
    node = EKFNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
