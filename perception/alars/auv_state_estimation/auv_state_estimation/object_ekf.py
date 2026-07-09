import numpy as np

from rclpy.time import Time
from scipy.stats import chi2
from scipy.spatial.transform import Rotation as R

from dji_msgs.msg import ObjectPoseWithCovariance, ObjectEkfStatus

from .ekf_core import EKFCore
from .measurement_model import MeasurementModel
from .noise_models import NoiseModels
from .initializer import Initializer
from .visualization import create_pose_msg
from .geometry_utils import residual_z, wrap
from .motion_model import DepthModel, DoubleOscillatorModel, OscillatorModel, PitchModel, SurfaceModel

class ObjectEKF:
    """
    Single-object EKF logic.
    """

    def __init__(self, class_name, cfg, base_params, camera_info, logger):
        self.class_name = class_name
        self.logger = logger

        if self.class_name == "":
            raise ValueError("class_name must not be empty")

        self.get_params(cfg, base_params, camera_info)

        self.log_info(f"Object/class name: {self.class_name}")
        self.log_info(f"Motion model type: {self.motion_model_type}")

        self.motion_model = self.get_motion_model(self.motion_model_type)
        self.eps = self.motion_model.eps

        self.state_dim = self.motion_model.state_dim
        self.meas_dim = 3 if self.state_dim == 5 else 5
        self.outlier_threshold = chi2.ppf(self.gating_prob, df=self.meas_dim)

        # In case of AUV estimation, we can optionally use a head topic.
        # For generic multi-object estimation this is disabled for now.
        self.enable_head_disambiguation = False
        self.flip_buffer = [-1]

        self.current_cam_pos_map = None
        self.current_R_map_cam = None
        self.lin_vel_map = np.zeros(3)
        self.ang_vel_map = np.zeros(3)

        self.last_processed_measurement_time = None
        self.last_innovation_norm = -1.0
        self.nr_of_consecutive_invalid_measurements = 0

        self.initialize_components()

        self.log_info(
            f"Created EKF for class={self.class_name}, "
            f"model={self.motion_model_type}, "
            f"size={self.obb_length_m}x{self.obb_width_m}"
        )

    @staticmethod
    def flatten_params(params, prefix=""):
        flat = {}

        for key, value in params.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                flat.update(ObjectEKF.flatten_params(value, full_key))
            else:
                flat[full_key] = value

        return flat

    def log_info(self, msg):
        if self.logger_info_enable:
            self.logger.info(msg)

    def matches_detection(self, det):
        return str(det.class_name) == self.class_name

    def pol_to_array(self, msg):
        # polygon -> array of normalized image coordinates
        return np.array([(p.x, p.y) for p in msg.polygon.points])

    def z(self, msg, cam_pos_map, R_map_cam, lin_vel_map, ang_vel_map, now):
        # main callback for processing incoming measurements, performing EKF prediction and update, and preparing the estimated pose.
        stamp = msg.header.stamp
        t: float = stamp.sec + stamp.nanosec * 1e-9

        self.current_cam_pos_map = cam_pos_map
        self.current_R_map_cam = R_map_cam
        self.lin_vel_map = lin_vel_map
        self.ang_vel_map = ang_vel_map

        if Time.from_msg(stamp).seconds_nanoseconds() == (0, 0):
            self.log_info(f"{self.class_name}: Received message with zero timestamp, skipping.")
            return

        if self.last_processed_measurement_time is not None:
            state_age = (now - self.last_processed_measurement_time).nanoseconds * 1e-9
            if state_age > self.stale_state_age:
                self.log_info(f"{self.class_name}: Exceeding stale state age {state_age:.2f}s, Resetting filter.")
                self.reset_filter()
                return
        else:
            self.log_info(f"{self.class_name}: First measurement received.")

        z_center_img, z_alpha_img, z_len_px, z_wid_px, _ = self.measurement_model.extract_features(self.pol_to_array(msg))

        if not self.ekf.initialized:
            init_result = self.initializer.try_initialize(stamp, z_center_img, z_alpha_img, self.measurement_model, self.current_cam_pos_map, self.current_R_map_cam)
            if init_result is None:
                return

            X0, P0, t0 = init_result
            self.ekf.set_state(X0, P0, t0)
            self.ekf.initialized = True
            self.last_processed_measurement_time = now
            self.log_info(f"{self.class_name}: Initialization complete")
            return

        if self.state_dim == 5:
            z = np.array([[z_center_img[0]], [z_center_img[1]], [z_alpha_img]])
        else:
            z = np.array([[z_center_img[0]], [z_center_img[1]], [z_alpha_img], [z_len_px], [z_wid_px]])

        if self.ekf.last_t is None:
            self.log_info(f"{self.class_name}: EKF not initialized with time, skipping measurement")
            return

        dt: float = t - self.ekf.last_t

        if dt < 0:  # due to mismatch between stamp and arrival time, we may receive measurements from the past.
            self.log_info(f"{self.class_name}: Measurement from the past received (dt={dt:.3f}s), skipping")
            return

        X = self.predict_to_measurement_time(dt)

        h = self.measurement_model.hx(X, cam_pos_map=self.current_cam_pos_map, R_map_cam=self.current_R_map_cam)
        if h is None:
            self.nr_of_consecutive_invalid_measurements += 1
            self.log_info(f"{self.class_name}: Measurement function returned None, skipping update")
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

        self.last_processed_measurement_time = now
        self.log_info(f"{self.class_name}: update {status}, state={X.flatten()[:3]}")

    def predict_to_measurement_time(self, dt_total):
        # performs multiple prediction steps between measurements.
        # this improves predictions during longer time gaps.

        dt_max = 0.01
        n_steps = max(1, int(np.ceil(dt_total / dt_max)))
        dt_step = dt_total / n_steps

        for _ in range(n_steps):
            X, F = self.motion_model.predict(self.ekf.X, dt_step)
            Q = self.motion_model.build_Q(dt_step)
            self.ekf.predict(X, F, Q, self.ekf.last_t + dt_step)
        return X # type: ignore

    def create_estimate_msg(self, stamp, map_frame):
        # creates the current state estimate as an ObjectPoseWithCovariance message.
        yaw_idx = 2 if self.state_dim == 5 else 3

        if not self.ekf.initialized:
            return None

        yaw_out = self.ekf.X[yaw_idx, 0]

        if self.enable_head_disambiguation:
            flip_decision = np.sum(self.flip_buffer)

            if flip_decision > 0:
                yaw_out += np.pi

        yaw_out = wrap(yaw_out)

        if self.state_dim == 5:
            q = R.from_euler("z", yaw_out).as_quat()
        elif self.motion_model_type == "pitch":
            q = R.from_euler("xyz", [0, self.ekf.X[4, 0], yaw_out]).as_quat()
        else:
            q = R.from_euler("z", yaw_out).as_quat()

        if Time.from_msg(stamp).seconds_nanoseconds() == (0, 0):
            self.log_info(">> Almost created estimate without a stamp!")
            return None

        pose_stamped = create_pose_msg(stamp, self.motion_model_type, q, map_frame, self.ekf.X, self.ekf.P, self.water_surface_height)

        out = ObjectPoseWithCovariance()
        out.header = pose_stamped.header
        out.class_name = self.class_name
        out.pose = pose_stamped.pose

        return out

    def create_status_msg(self, now, map_frame):
        # creates information regarding the status of the filter.
        # nr of consecutive outliers is probably a good indication of the status.
        now_sec = now.nanoseconds * 1e-9

        if self.ekf.initialized:
            time_since_last_update = now_sec - self.ekf.time_last_update

            if time_since_last_update > self.stale_state_age:
                self.log_info(
                    f"{self.class_name}: time since last update is "
                    f"{time_since_last_update:.3f}s, exceeding stale state age "
                    f"{self.stale_state_age}s. Resetting filter."
                )
                self.reset_filter()
        else:
            time_since_last_update = 0.0

        msg = ObjectEkfStatus()
        msg.header.stamp = now.to_msg()
        msg.header.frame_id = map_frame

        msg.class_name = self.class_name

        msg.initialized = bool(self.ekf.initialized)

        if self.last_processed_measurement_time is None:
            msg.time_since_last_processed_measurement = 0.0
        else:
            msg.time_since_last_processed_measurement = float((now - self.last_processed_measurement_time).nanoseconds * 1e-9)

        msg.time_since_last_update = float(time_since_last_update)
        msg.consecutive_outliers = int(self.ekf.nr_of_consecutive_outliers)
        msg.consecutive_invalid_measurements = int(self.nr_of_consecutive_invalid_measurements)
        msg.covariance_trace = float(np.trace(self.ekf.P) if self.ekf.P is not None else -1.0)
        msg.innovation_norm = float(self.last_innovation_norm)

        return msg

    def reset_filter(self):
        self.ekf = EKFCore(
            self.water_surface_height,
            state_dim=self.state_dim,
            outlier_threshold=self.outlier_threshold,
            logger=self.logger,
        )

        self.flip_buffer = [-1]
        self.current_cam_pos_map = None
        self.current_R_map_cam = None
        self.lin_vel_map = np.zeros(3)
        self.ang_vel_map = np.zeros(3)
        self.last_processed_measurement_time = None
        self.nr_of_consecutive_invalid_measurements = 0
        self.last_innovation_norm = -1.0

        self.logger.info(f"{self.class_name}: EKF internal state reset.")

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
            logger=self.logger,
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
            logger=self.logger,
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
            outlier_threshold=self.outlier_threshold,
            logger=self.logger,
        )

    def get_params(self, cfg, base_params, camera_info):
        PARAMS = [
            ("object_name", "object"),

            ("detection.class_name", ""),
            ("detection.confidence_threshold", 0.5),

            ("environment.water_surface_height", 0.0),

            # Dimensions of the object model used by the measurement model.
            ("obb.length_m", 1.3),
            ("obb.width_m", 0.16),

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
            ("stale_state_age", 3.0),
        ]

        params = dict(PARAMS)

        # Base params are loaded from the common EKF yaml file.
        params.update(base_params)

        # Per-class params override the base params.
        params.update(self.flatten_params(cfg.get("parameters", {})))

        # Per-class top-level config values.
        params["object_name"] = self.class_name
        params["detection.class_name"] = self.class_name
        params["detection.confidence_threshold"] = cfg.get(
            "confidence_threshold",
            params["detection.confidence_threshold"],
        )
        params["obb.length_m"] = cfg.get("length_m", params["obb.length_m"])
        params["obb.width_m"] = cfg.get("width_m", params["obb.width_m"])
        params["motion.model_type"] = cfg.get(
            "motion_model_type",
            params["motion.model_type"],
        )

        params["stale_state_age"] = cfg.get("stale_state_age", params["stale_state_age"])

        env = cfg.get("environment", {})
        params["environment.water_surface_height"] = env.get(
            "water_surface_height",
            params["environment.water_surface_height"],
        )

        self.params = params

        self.object_name: str = str(params["object_name"])
        self.detection_class_name: str = str(params["detection.class_name"])
        self.confidence_threshold: float = float(params["detection.confidence_threshold"])

        self.water_surface_height: float = float(params["environment.water_surface_height"])

        self.obb_length_m: float = float(params["obb.length_m"])
        self.obb_width_m: float = float(params["obb.width_m"])
        self.alpha_line_pixels: int = int(params["alpha_line_pixels"])

        self.sigma_a_xy: float = float(params["motion.sigma_a_xy"])
        self.sigma_yaw: float = np.deg2rad(float(params["motion.sigma_yaw"]))

        self.motion_model_type: str = str(params["motion.model_type"])

        self.depth_sigma_z_process: float = float(params["depth.sigma_z_process"])
        self.depth_k_z: float = float(params["depth.k_z"])
        self.depth_d_z: float = float(params["depth.d_z"])

        self.sigma_pitch_process: float = float(params["pitch.sigma_pitch_process"])

        self.oscillator_sigma_z_process: float = float(params["oscillator.sigma_z_process"])
        self.oscillator_omega: float = float(params["oscillator.omega"])
        self.oscillator_zeta: float = float(params["oscillator.zeta"])

        self.double_oscillator_sigma_z_slow: float = float(params["double_oscillator.sigma_z_slow"])
        self.double_oscillator_sigma_z_fast: float = float(params["double_oscillator.sigma_z_fast"])
        self.double_oscillator_omega_slow: float = float(params["double_oscillator.omega_slow"])
        self.double_oscillator_zeta_slow: float = float(params["double_oscillator.zeta_slow"])
        self.double_oscillator_omega_fast: float = float(params["double_oscillator.omega_fast"])
        self.double_oscillator_zeta_fast: float = float(params["double_oscillator.zeta_fast"])

        self.R_u: float = float(params["measurement_noise.R_u"])
        self.R_v: float = float(params["measurement_noise.R_v"])
        self.R_alpha: float = np.deg2rad(float(params["measurement_noise.R_alpha_deg"]))
        self.R_len: float = float(params["measurement_noise.R_len"])
        self.R_wid: float = float(params["measurement_noise.R_wid"])

        self.R_pose_x: float = float(params["camera_pose_noise.R_pose_x"])
        self.R_pose_y: float = float(params["camera_pose_noise.R_pose_y"])
        self.R_pose_z: float = float(params["camera_pose_noise.R_pose_z"])
        self.R_pose_r: float = np.deg2rad(float(params["camera_pose_noise.R_pose_r"]))
        self.R_pose_p: float = np.deg2rad(float(params["camera_pose_noise.R_pose_p"]))
        self.R_pose_yaw: float = np.deg2rad(float(params["camera_pose_noise.R_pose_yaw"]))

        self.R_dyn_center_gain_u: float = float(params["measurement_noise.center_gain_u"])
        self.R_dyn_center_gain_v: float = float(params["measurement_noise.center_gain_v"])
        self.R_dyn_center_gain_alpha: float = np.deg2rad(float(params["measurement_noise.center_gain_alpha_deg"]))
        self.R_dyn_center_gain_len: float = float(params["measurement_noise.center_gain_len"])
        self.R_dyn_center_gain_wid: float = float(params["measurement_noise.center_gain_wid"])

        self.R_dyn_speed_gain_u: float = float(params["measurement_noise.speed_gain_u"])
        self.R_dyn_speed_gain_v: float = float(params["measurement_noise.speed_gain_v"])
        self.R_dyn_speed_gain_alpha: float = np.deg2rad(float(params["measurement_noise.speed_gain_alpha_deg"]))
        self.R_dyn_speed_gain_len: float = float(params["measurement_noise.speed_gain_len"])
        self.R_dyn_speed_gain_wid: float = float(params["measurement_noise.speed_gain_wid"])

        self.R_dyn_dt: float = float(params["measurement_noise.R_dyn_dt"])

        self.init_z_needed: int = int(params["initialization.min_valid_meas_needed"])
        self.init_pos_max_spread: float = float(params["initialization.max_pos_spread"])
        self.init_yaw_max_spread: float = np.deg2rad(float(params["initialization.max_yaw_spread"]))

        self.gating_prob: float = float(params["gating.prob"])

        self.eps_state_pos: float = float(params["jacobian.eps_state_pos"])
        self.eps_state_yaw: float = float(params["jacobian.eps_state_yaw"])
        self.eps_state_vel: float = float(params["jacobian.eps_state_vel"])
        self.eps_pose_pos: float = float(params["jacobian.eps_pose_pos"])
        self.eps_pose_ang: float = float(params["jacobian.eps_pose_ang"])

        self.logger_info_enable: bool = bool(params["logger_info.enable"])

        # how long do we hold on to the state after last measurement before considering it stale and reinitializing?
        self.stale_state_age: float = float(params["stale_state_age"])

        self.width = camera_info["width"]
        self.height = camera_info["height"]
        self.K = camera_info["K"]
        self.D = camera_info["D"]