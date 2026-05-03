from dji_msgs.msg import Links, Topics
from smarc_msgs.msg import Topics as SmarcTopics

import yaml
import numpy as np
from collections import deque
import rclpy
from rclpy.time import Time
from rclpy.node import Node
from geometry_msgs.msg import PolygonStamped, TransformStamped, PoseWithCovarianceStamped, Vector3Stamped
from std_msgs.msg import Float32MultiArray
from nav_msgs.msg import Odometry
from scipy.stats import chi2
import tf2_ros
from scipy.spatial.transform import Rotation as R

from .ekf_core import EKFCore
from .measurement_model import MeasurementModel
from .noise_models import NoiseModels
from .initializer import Initializer
from .visualization import create_pose_msg, create_transform_msg
from .geometry_utils import residual_z, wrap
from .motion_model import DepthModel, DoubleOscillatorModel, OscillatorModel, PitchModel, SurfaceModel, PitchModel

from std_srvs.srv import Trigger

class EKFNode(Node):
    def __init__(self):
        super().__init__("ekf_node")
        self.get_params()

        self.logger_info_enable : bool = self.get_parameter("logger_info.enable").get_parameter_value().bool_value

        self.log_info(f"Motion model type: {self.motion_model_type}")

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
        self.sub_odom = self.create_subscription(Odometry, self.topic_odom, self.odom_cb, 10)
        self.sub_head = self.create_subscription(PolygonStamped, self.topic_input_auv_head, self.head_cb, 10)

        self.reset_srv = self.create_service(Trigger, "alars_auv_ekf/reset", self.handle_reset_service)

        self.current_transform = None
        self.current_cam_pos_map = None
        self.current_R_map_cam = None
        self.flip_buffer = [-1]
        self.lin_vel_map = np.zeros(3)
        self.ang_vel_map = np.zeros(3)

        self.last_innovation_norm = -1.0
        self.nr_of_consecutive_invalid_measurements = 0

        self.initialize_components()

        self.get_logger().info(f"EKF node started. map_frame={self.map_frame}, cam_frame={self.cam_frame}, estimated_auv_frame={self.output_frame}")

        self.q : deque[tuple[PolygonStamped | None, Time | None]] = deque()
        self.timer = self.create_timer(0.01, self.process_q)
        self.status_timer = self.create_timer(0.5, self.publish_status)
        self.check_time_since_last_meas_timer = self.create_timer(0.01, self.check_time_since_last_measurement)

    def log_info(self, msg):
        if self.logger_info_enable:
            self.get_logger().info(msg)

    def poly_cb(self, msg : PolygonStamped):
        arrival = self.get_clock().now()
        self.q.append((msg, arrival))

    def process_q(self):
        while self.q:
            msg, arrival = self.q[0]
            
            if msg is None or arrival is None: 
                self.log_info("Received None message or timestamp in queue, skipping.")
                self.q.popleft()
                continue

            now : Time = self.get_clock().now()
            if self.last_processed_measurement_time is not None:
                state_age = (now - self.last_processed_measurement_time).nanoseconds * 1e-9
                if state_age > self.stale_state_age:
                    self.log_info(f"STALE STATE (age {state_age:.2f}s), RESETTING FILTER.")
                    self.reset_filter()
                    return
            else:
                self.log_info("First measurement received.")

            stamp : Time = Time.from_msg(msg.header.stamp)
            if stamp.seconds_nanoseconds() == (0, 0):
                self.log_info("Received message with zero timestamp, skipping.")
                self.q.popleft()
                continue


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
                self.last_processed_measurement_time = arrival
                continue
            else:
                self.log_info(f"Cant transform from {self.cam_frame} to {self.map_frame} at msg time, dropping msg.")
                self.q.popleft()

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
        head = self.initializer.point_on_line_at_z(self.current_cam_pos_map, ray, self.water_surface_height)
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

    def odom_cb(self, msg: Odometry):
        if self.current_R_map_cam is None:
            return
        self.lin_vel_map = self.current_R_map_cam @ np.array([-msg.twist.twist.linear.x, msg.twist.twist.linear.y, msg.twist.twist.linear.z])
        self.ang_vel_map = self.current_R_map_cam @ np.array([-msg.twist.twist.angular.x, msg.twist.twist.angular.y, msg.twist.twist.angular.z])

    def predict_to_measurement_time(self, dt_total):
        # perfoems multiple prediction steps between measurements.
        # this should imporve predictions duering longer time gaps.

        dt_max = 0.01
        n_steps = max(1, int(np.ceil(dt_total / dt_max)))
        dt_step = dt_total / n_steps
        for _ in range(n_steps):
            X, F = self.motion_model.predict(self.ekf.X, dt_step)
            Q = self.motion_model.build_Q(dt_step)
            self.ekf.predict(X, F, Q, self.ekf.last_t + dt_step)
        return X # type: ignore
    

    def z(self, msg: PolygonStamped, transform: TransformStamped):
            
        # main callback for processing incoming measurements, performing EKF prediction and update, and publishing the estimated pose.
        stamp = msg.header.stamp
        t : float = stamp.sec + stamp.nanosec * 1e-9
        self.current_transform = transform
        
        z_center_img, z_alpha_img, z_len_px, z_wid_px, _ = self.measurement_model.extract_features(self.pol_to_array(msg))
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


        if self.ekf.last_t is None:
            self.log_info("EKF not initialized with time, skipping measurement")
            return

        dt : float = t - self.ekf.last_t

        if dt < 0: # due to mismatch between stamp and arrival time, we may receive measurements from the past.
            self.log_info(f"Measurement from the past received (dt={dt:.3f}s), skipping")
            return


        X = self.predict_to_measurement_time(dt)

        h = self.measurement_model.hx(X, cam_pos_map=self.current_cam_pos_map, R_map_cam=self.current_R_map_cam)
        if h is None:
            self.nr_of_consecutive_invalid_measurements += 1
            self.log_info("Measurement function returned None, skipping update")
            return

        H = self.measurement_model.numerical_H(X, cam_pos_map=self.current_cam_pos_map, R_map_cam=self.current_R_map_cam)
        J_pose = self.measurement_model.numerical_J_pose(X, cam_pos_map=self.current_cam_pos_map, R_map_cam=self.current_R_map_cam)
        R_meas = self.noise_models.build_image_measurement_covariance(z_center_img, self.lin_vel_map) + self.noise_models.project_pose_covariance_to_measurement(J_pose, self.lin_vel_map, self.ang_vel_map)

        innov = residual_z(z, h).reshape(z.shape[0], 1)
        self.last_innovation_norm = np.linalg.norm(innov)  

        X, P, status = self.ekf.update(z, h, H, R_meas)
        if status == "outlier" or status == "invalid":
            self.nr_of_consecutive_invalid_measurements += 1
        elif status == "updated":
            self.nr_of_consecutive_invalid_measurements = 0
        self.log_info(f"Update successful. Post-update state: {X.flatten()[:3]}")
        self.publish_estimate(stamp)
    
    def publish_estimate(self, stamp):
        # publishes the current state estimate as a PoseWithCovarianceStamped message and also broadcasts a TF.
        flip_decision = np.sum(self.flip_buffer)
        yaw_idx = 2 if self.state_dim == 5 else 3
        yaw_out = self.ekf.X[yaw_idx, 0] + (np.pi if (flip_decision > 0) else 0.0)
        yaw_out = wrap(yaw_out)
        if self.state_dim == 5:
            q = R.from_euler("z", yaw_out).as_quat()
        elif self.motion_model_type == "pitch":
            q = R.from_euler("xyz", [0, self.ekf.X[4, 0], yaw_out]).as_quat()
        else:
            q = R.from_euler("z", yaw_out).as_quat()


        if Time.from_msg(stamp).seconds_nanoseconds() == (0, 0):
            self.log_info(">> Almost pubbed without a stamp!")
            return

        self.pub.publish(create_pose_msg(stamp, self.motion_model_type, q, self.map_frame, self.ekf.X, self.ekf.P, self.water_surface_height))
        self.tf_broadcaster.sendTransform(create_transform_msg(stamp, self.motion_model_type, q, self.map_frame, self.output_frame, self.ekf.X, self.water_surface_height))

    def check_time_since_last_measurement(self, max_time_without_meas=0.5):
        # checks the time since the last measurement and resets the filter if it exceeds a threshold.
        if self.ekf.last_t is None and not self.ekf.initialized:
            return
        now = self.get_clock().now().nanoseconds * 1e-9
        time_since_last_meas = now - self.ekf.last_t
        if time_since_last_meas > max_time_without_meas:
            self.log_info(f"Time since last measurement is {time_since_last_meas:.3f}s, exceeding max time without measurement {max_time_without_meas}s. Predicting to current time.")
            self.predict_to_measurement_time(time_since_last_meas)
            self.publish_estimate(self.get_clock().now().to_msg())

    def publish_status(self):
        # publishes information regarding the status of the filter.
        # nr of consecutive outliers is probably a good indication of the status.
        # may want to exanp thi.
        msg = Float32MultiArray()
        now = self.get_clock().now().nanoseconds * 1e-9
        if self.last_processed_measurement_time is None:
            time_since_last_processed_meas = 0.0
        else:
            time_since_last_processed_meas = now - self.last_processed_measurement_time.nanoseconds * 1e-9

        time_since_last_update = now - self.ekf.time_last_update
        if self.ekf.initialized and time_since_last_update > self.stale_state_age:
            self.log_info(f"Time since last update is {time_since_last_update:.3f}s, exceeding stale state age {self.stale_state_age}s. Resetting filter.")
            self.reset_filter()

        cov_trace = np.trace(self.ekf.P) if self.ekf.P is not None else -1.0
        if not self.ekf.initialized:
            initialized = 0.0
        else:
            initialized = 1.0
        innovation_norm = getattr(self, "last_innovation_norm", -1.0)
        msg.data = [
            initialized,    # 0 = not initialized, 1 = initialized
            time_since_last_processed_meas,
            time_since_last_update,
            float(self.ekf.nr_of_consecutive_outliers),
            float(self.nr_of_consecutive_invalid_measurements),
            cov_trace,
            innovation_norm,
            ]

        self.pub_status.publish(msg)

    def handle_reset_service(self, request, response):
        self.reset_filter()
        response.success = True
        response.message = "EKF reset successfully."
        return response
    
    def reset_filter(self):
        self.ekf = EKFCore(
            self.water_surface_height,
            state_dim=self.state_dim,
            outlier_threshold=self.outlier_threshold, # type: ignore
            #logger=self.get_logger(),
        )

        self.flip_buffer = [-1]
        self.current_transform = None
        self.current_cam_pos_map = None
        self.current_R_map_cam = None
        self.lin_vel_map = np.zeros(3)
        self.ang_vel_map = np.zeros(3)
        self.q.clear()
        self.last_processed_measurement_time = None
        self.get_logger().info("EKF internal state reset.")

    def get_motion_model(self, model_type):
        if model_type == "surface":
            return SurfaceModel(
                sigma_a=self.sigma_a_xy,
                sigma_yaw=self.sigma_yaw,
            )
        elif model_type == "depth":
            return DepthModel(
                sigma_a=self.sigma_a_xy,
                sigma_z=self.depth_sigma_z_process,
                sigma_yaw=self.sigma_yaw,
            )
        elif model_type == "pitch":
            return PitchModel(
                sigma_a=self.sigma_a_xy,
                sigma_z=self.depth_sigma_z_process,
                sigma_yaw=self.sigma_yaw,
                sigma_pitch=self.sigma_pitch_process,
            )
        elif model_type == "oscillator":
            return OscillatorModel(
                sigma_a=self.sigma_a_xy,
                sigma_z=self.oscillator_sigma_z_process,
                sigma_yaw=self.sigma_yaw,
                omega=self.oscillator_omega,
                zeta=self.oscillator_zeta,
            )
        elif model_type == "double_oscillator":
            return DoubleOscillatorModel(
                sigma_a=self.sigma_a_xy,
                sigma_z_slow=self.double_oscillator_sigma_z_slow,
                sigma_z_fast=self.double_oscillator_sigma_z_fast,
                sigma_yaw=self.sigma_yaw,
                omega_slow=self.double_oscillator_omega_slow,
                zeta_slow=self.double_oscillator_zeta_slow,
                omega_fast=self.double_oscillator_omega_fast,
                zeta_fast=self.double_oscillator_zeta_fast,
            )
        else:
            raise ValueError(f"Unknown motion model type: {model_type}")
        
    def initialize_components(self):
        self.initializer = Initializer(
            z_water=self.water_surface_height,
            state_dim=self.state_dim,
            init_z_needed=self.init_z_needed,
            init_pos_max_spread=self.init_pos_max_spread,
            init_yaw_max_spread=self.init_yaw_max_spread,
            alpha_line_pixels=self.alpha_line_pixels,
            R_len=self.R_len,
            R_wid=self.R_wid,
            R_alpha=self.R_alpha,
            motion_model_type=self.motion_model_type,
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
            z_water=self.water_surface_height,
            obb_length_m=self.obb_length_m,
            obb_width_m=self.obb_width_m,
            motion_model_type=self.motion_model_type,
            logger=self.get_logger(),
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
            self.water_surface_height,
            state_dim=self.state_dim,
            outlier_threshold=self.outlier_threshold, # type: ignore
            logger=self.get_logger(),   
        )

    def get_params(self):
        PARAMS = [
            ("topics.input_polygon", Topics.ESTIMATED_AUV_OBB_TOPIC),
            ("topics.input_auv_head", Topics.ESTIMATED_AUV_HEAD_TOPIC),
            ("topics.output_topic", "rviz/estimated_pose"),
            ("topics.odom", SmarcTopics.ODOM_TOPIC),
            ("topics.ekf_status", "alars_auv_ekf/status"),

            ("robot_name", "M350"),
            ("frames.map", Links.MAP),
            ("frames.output_link", Links.ESTIMATED_AUV),
            ("frames.camera", Links.GIMBAL_OPTICAL_FRAME),

            ("camera_info", ""),

            ("environment.water_surface_height", 0.0),

            # note that these are dimensions of the AUV in the measurement model (OBB), not necessarily the true dimensions of the AUV.
            ("obb.length_m", 1.3), # auv length in meters, may need to be adjusted
            ("obb.width_m", 0.16), # auv width in meters, may need to be adjusted

            ("alpha_line_pixels", 40), # pixels along the alpha direction to compute the front and back rays for yaw estimation in initialization

            ("motion.sigma_a_xy", 0.01), # m/s^2, could split up into x, y
            ("motion.sigma_yaw", 3.0), # deg/s
            ("motion.model_type", "double_oscillator"),

            ("depth.sigma_z_process", 1.0), 
            ("depth.k_z", 0.4),
            ("depth.d_z", 0.1),

            ("pitch.sigma_pitch_process", 15.0), 

            ("oscillator.sigma_z_process", 5.0),
            ("oscillator.omega", 2.0),
            ("oscillator.zeta", 0.01),

            ("double_oscillator.sigma_z_slow", 1.0),
            ("double_oscillator.sigma_z_fast", 3.0),
            ("double_oscillator.omega_slow", 1.0),
            ("double_oscillator.zeta_slow", 0.01),
            ("double_oscillator.omega_fast", 2.0),
            ("double_oscillator.zeta_fast", 0.01),

            # measurement noise stddev (pixels)
            ("measurement_noise.R_u", 10.0), 
            ("measurement_noise.R_v", 10.0),
            ("measurement_noise.R_alpha_deg", 5.0),
            ("measurement_noise.R_len", 200.0),
            ("measurement_noise.R_wid", 40.0),

            # dynamic measurement noise stddev (pixels)
            # increases with distance from image center
            ("measurement_noise.center_gain_u", 50.0), 
            ("measurement_noise.center_gain_v", 50.0),
            ("measurement_noise.center_gain_alpha_deg", 10.0),
            ("measurement_noise.center_gain_len", 10.0),
            ("measurement_noise.center_gain_wid", 10.0),

            # increases with drone speed
            ("measurement_noise.speed_gain_u", 50.0),
            ("measurement_noise.speed_gain_v", 50.0),
            ("measurement_noise.speed_gain_alpha_deg", 10.0),
            ("measurement_noise.speed_gain_len", 60.0),
            ("measurement_noise.speed_gain_wid", 30.0),

            ("measurement_noise.R_dyn_dt", 0.5),

            # drone pose noise
            ("camera_pose_noise.R_pose_x", 0.03),
            ("camera_pose_noise.R_pose_y", 0.03),
            ("camera_pose_noise.R_pose_z", 0.03),
            ("camera_pose_noise.R_pose_r", 1.0),
            ("camera_pose_noise.R_pose_p", 1.0),
            ("camera_pose_noise.R_pose_yaw", 3.0),

            # dynamic measurement noise update rate (s)

            ("initialization.min_valid_meas_needed", 5),
            ("initialization.max_pos_spread", 2.0),
            ("initialization.max_yaw_spread", 0.7),

            ("gating.prob", 0.99),

            # jacobian epsilons for numerical differentiation
            ("jacobian.eps_state_pos", 1e-3),
            ("jacobian.eps_state_yaw", 1e-3),
            ("jacobian.eps_state_vel", 1e-3),
            ("jacobian.eps_pose_pos", 1e-3),
            ("jacobian.eps_pose_ang", 1e-3),

            ("logger_info.enable", True),

            # if the state is older than this many seconds when a new measurement arrives, reset the filter.
            ("stale_state_age", 3.0)
            ]
        
        self.declare_parameters(namespace="", parameters=PARAMS)

        self.water_surface_height :float = self.get_parameter("environment.water_surface_height").get_parameter_value().double_value

        self.obb_length_m :float = self.get_parameter("obb.length_m").get_parameter_value().double_value
        self.obb_width_m :float = self.get_parameter("obb.width_m").get_parameter_value().double_value
        self.alpha_line_pixels :int = self.get_parameter("alpha_line_pixels").get_parameter_value().integer_value

        self.sigma_a_xy :float = self.get_parameter("motion.sigma_a_xy").get_parameter_value().double_value
        self.sigma_yaw :float = np.deg2rad(self.get_parameter("motion.sigma_yaw").get_parameter_value().double_value)

        self.motion_model_type : str = self.get_parameter("motion.model_type").get_parameter_value().string_value

        self.depth_sigma_z_process : float = self.get_parameter("depth.sigma_z_process").get_parameter_value().double_value
        self.depth_k_z : float = self.get_parameter("depth.k_z").get_parameter_value().double_value
        self.depth_d_z : float = self.get_parameter("depth.d_z").get_parameter_value().double_value

        self.sigma_pitch_process : float = self.get_parameter("pitch.sigma_pitch_process").get_parameter_value().double_value

        self.oscillator_sigma_z_process : float = self.get_parameter("oscillator.sigma_z_process").get_parameter_value().double_value
        self.oscillator_omega : float = self.get_parameter("oscillator.omega").get_parameter_value().double_value
        self.oscillator_zeta : float = self.get_parameter("oscillator.zeta").get_parameter_value().double_value

        self.double_oscillator_sigma_z_slow : float = self.get_parameter("double_oscillator.sigma_z_slow").get_parameter_value().double_value
        self.double_oscillator_sigma_z_fast : float = self.get_parameter("double_oscillator.sigma_z_fast").get_parameter_value().double_value
        self.double_oscillator_omega_slow : float = self.get_parameter("double_oscillator.omega_slow").get_parameter_value().double_value
        self.double_oscillator_zeta_slow : float = self.get_parameter("double_oscillator.zeta_slow").get_parameter_value().double_value
        self.double_oscillator_omega_fast : float = self.get_parameter("double_oscillator.omega_fast").get_parameter_value().double_value
        self.double_oscillator_zeta_fast : float = self.get_parameter("double_oscillator.zeta_fast").get_parameter_value().double_value

        self.R_u :float = self.get_parameter("measurement_noise.R_u").get_parameter_value().double_value
        self.R_v :float = self.get_parameter("measurement_noise.R_v").get_parameter_value().double_value
        self.R_alpha :float = np.deg2rad(float(self.get_parameter("measurement_noise.R_alpha_deg").get_parameter_value().double_value))
        self.R_len :float = self.get_parameter("measurement_noise.R_len").get_parameter_value().double_value
        self.R_wid :float = self.get_parameter("measurement_noise.R_wid").get_parameter_value().double_value

        self.R_pose_x :float = self.get_parameter("camera_pose_noise.R_pose_x").get_parameter_value().double_value
        self.R_pose_y :float = self.get_parameter("camera_pose_noise.R_pose_y").get_parameter_value().double_value
        self.R_pose_z :float = self.get_parameter("camera_pose_noise.R_pose_z").get_parameter_value().double_value
        self.R_pose_r :float = np.deg2rad(self.get_parameter("camera_pose_noise.R_pose_r").get_parameter_value().double_value)
        self.R_pose_p :float = np.deg2rad(self.get_parameter("camera_pose_noise.R_pose_p").get_parameter_value().double_value)
        self.R_pose_yaw :float = np.deg2rad(self.get_parameter("camera_pose_noise.R_pose_yaw").get_parameter_value().double_value)

        self.R_dyn_center_gain_u :float = self.get_parameter("measurement_noise.center_gain_u").get_parameter_value().double_value
        self.R_dyn_center_gain_v :float = self.get_parameter("measurement_noise.center_gain_v").get_parameter_value().double_value
        self.R_dyn_center_gain_alpha :float = np.deg2rad(self.get_parameter("measurement_noise.center_gain_alpha_deg").get_parameter_value().double_value)
        self.R_dyn_center_gain_len :float = self.get_parameter("measurement_noise.center_gain_len").get_parameter_value().double_value
        self.R_dyn_center_gain_wid :float = self.get_parameter("measurement_noise.center_gain_wid").get_parameter_value().double_value

        self.R_dyn_speed_gain_u :float = self.get_parameter("measurement_noise.speed_gain_u").get_parameter_value().double_value
        self.R_dyn_speed_gain_v :float = self.get_parameter("measurement_noise.speed_gain_v").get_parameter_value().double_value
        self.R_dyn_speed_gain_alpha :float = np.deg2rad(self.get_parameter("measurement_noise.speed_gain_alpha_deg").get_parameter_value().double_value)
        self.R_dyn_speed_gain_len :float = self.get_parameter("measurement_noise.speed_gain_len").get_parameter_value().double_value
        self.R_dyn_speed_gain_wid :float = self.get_parameter("measurement_noise.speed_gain_wid").get_parameter_value().double_value

        self.R_dyn_dt :float = self.get_parameter("measurement_noise.R_dyn_dt").get_parameter_value().double_value

        self.init_z_needed : int = self.get_parameter("initialization.min_valid_meas_needed").get_parameter_value().integer_value
        self.init_pos_max_spread :float = self.get_parameter("initialization.max_pos_spread").get_parameter_value().double_value
        self.init_yaw_max_spread :float = np.deg2rad(self.get_parameter("initialization.max_yaw_spread").get_parameter_value().double_value)

        self.gating_prob :float = self.get_parameter("gating.prob").get_parameter_value().double_value

        self.eps_state_pos :float = self.get_parameter("jacobian.eps_state_pos").get_parameter_value().double_value
        self.eps_state_yaw :float = self.get_parameter("jacobian.eps_state_yaw").get_parameter_value().double_value
        self.eps_state_vel :float = self.get_parameter("jacobian.eps_state_vel").get_parameter_value().double_value
        self.eps_pose_pos :float = self.get_parameter("jacobian.eps_pose_pos").get_parameter_value().double_value
        self.eps_pose_ang :float = self.get_parameter("jacobian.eps_pose_ang").get_parameter_value().double_value

        self.topic_in_poly : str = self.get_parameter("topics.input_polygon").get_parameter_value().string_value
        self.topic_input_auv_head : str = self.get_parameter("topics.input_auv_head").get_parameter_value().string_value
        self.topic_estimated_pose : str = self.get_parameter("topics.output_topic").get_parameter_value().string_value
        self.topic_odom : str = self.get_parameter("topics.odom").get_parameter_value().string_value
        self.topic_ekf_status : str = self.get_parameter("topics.ekf_status").get_parameter_value().string_value

        # how long do we hold on to the state after last measurement before considering it stale and reinitializing?
        self.stale_state_age : float = self.get_parameter("stale_state_age").get_parameter_value().double_value
        self.last_processed_measurement_time : Time | None = None


        robot_name : str = self.get_parameter("robot_name").get_parameter_value().string_value
        map_frame : str = self.get_parameter("frames.map").get_parameter_value().string_value
        output_frame : str = self.get_parameter("frames.output_link").get_parameter_value().string_value
        camera_frame : str = self.get_parameter("frames.camera").get_parameter_value().string_value

        self.map_frame = f"{robot_name}/{map_frame}"
        self.output_frame = f"{robot_name}/{output_frame}"
        self.cam_frame = f"{robot_name}/{camera_frame}"

        self.width = None
        self.height = None
        self.K = None
        self.D = None

        cam_info_path : str = self.get_parameter("camera_info").get_parameter_value().string_value
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
        

def main():
    rclpy.init()
    node = EKFNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()