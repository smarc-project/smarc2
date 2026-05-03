import numpy as np
from .geometry_utils import wrap

class Initializer: 
    def __init__(self, 
                 z_water, 
                 state_dim, 
                 init_z_needed, 
                 init_pos_max_spread, 
                 init_yaw_max_spread, 
                 alpha_line_pixels, 
                 R_len, 
                 R_wid, 
                 R_alpha, 
                 motion_model_type,
                 logger=None):
        self.z_water = z_water
        self.state_dim = state_dim
        self.init_z_needed = init_z_needed
        self.init_pos_max_spread = init_pos_max_spread
        self.init_yaw_max_spread = init_yaw_max_spread
        self.alpha_line_pixels = alpha_line_pixels
        self.R_len = R_len
        self.R_wid = R_wid
        self.R_alpha = R_alpha
        self.motion_model_type = motion_model_type
        self.logger = logger
        self.init_buffer = []

    def log_info(self, msg):
        if self.logger is not None:
            self.logger.info(msg)

    def point_on_line_at_z(self, p0, d, z):
        # Compute the parameter t for the line p(t) = p0 + t * d to intersect the plane z = constant
        if abs(d[2]) < 1e-9:
            self.log_info("Line is parallel to plane, cannot find intersection")
            return None
        t = (z - p0[2]) / d[2]
        if t < 0.0:
            self.log_info("Intersection point is behind the camera, invalid for initialization")
            return None
        return p0 + t * d

    def build_initial_state(self, center_map, z, yaw):
        # we initialize at the water surface, for all motion models.
        # could be extended to initialize at different depths if needed.
        # high initial uncertainty in z works quite well, but if auv is underwater better initialization may be required.
        if self.state_dim == 5:
            return np.array([[center_map[0]], [center_map[1]], [yaw], [0.0], [0.0]])
        if self.state_dim == 7:
            return np.array([[center_map[0]], [center_map[1]], [z], [yaw], [0.0], [0.0], [0.0]])

        x_c = np.zeros((self.state_dim, 1))
        x_c[0, 0] = center_map[0]
        x_c[1, 0] = center_map[1]
        x_c[2, 0] = z
        x_c[3, 0] = yaw
        return x_c
    
    def compute_axis_rays(self, center_uv, alpha_img, measurement_model, cam_rot):
        # Compute rays for the center, front, and back points along the estimated axis
        # use both front and back rays to get a better yaw estimate, 
        # less sensitive to noise in the center ray and potential bias in the alpha estimation
        # may be overkill
        d_img = np.array([np.cos(alpha_img), np.sin(alpha_img)])
        uv_front = center_uv + self.alpha_line_pixels * d_img
        uv_back = center_uv - self.alpha_line_pixels * d_img

        ray_center = measurement_model.back_projection(center_uv, cam_rot)
        ray_front = measurement_model.back_projection(uv_front, cam_rot)
        ray_back = measurement_model.back_projection(uv_back, cam_rot)

        if ray_center is None or ray_front is None or ray_back is None:
            return None
        return ray_center, ray_front, ray_back
    
    def estimate_yaw_on_plane(self, cam_pos, ray_front, ray_back, z_plane):
        # Estimate the yaw of the AUV on the plane z = z_plane using the front and back rays
        pf = self.point_on_line_at_z(cam_pos, ray_front, z_plane)
        pb = self.point_on_line_at_z(cam_pos, ray_back, z_plane)
        if pf is None or pb is None:
            return None

        vec = pf[:2] - pb[:2]
        if np.linalg.norm(vec) < 1e-9:
            self.log_info("Front and back rays are nearly parallel, cannot reliably estimate yaw (initializer)")
            return None

        return wrap(np.arctan2(vec[1], vec[0]))

    def infer_initial_state_from_measurement(self, center_uv, alpha_img, measurement_model, cam_pos, cam_rot):
        # Infer an initial state estimate from a single measurement of the center pixel and alpha angle
        rays = self.compute_axis_rays(center_uv, alpha_img, measurement_model, cam_rot)
        if rays is None:
            return None
        ray, dir_f, dir_b = rays

        center_map = self.point_on_line_at_z(cam_pos, ray, self.z_water)
        if center_map is None:
            return None
        yaw_c = self.estimate_yaw_on_plane(cam_pos, dir_f, dir_b, self.z_water)
        if yaw_c is None:
            return None
        return self.build_initial_state(center_map, self.z_water, yaw_c)

    def try_initialize(self, stamp, center_uv, alpha_img, measurement_model, cam_pos, cam_rot):
        # Try to initialize the state estimator using the current measurement. We require multiple consistent measurements to ensure a good initial estimate.
        # initializes as stationary at water surface with high uncertainty in z.
        x_init = self.infer_initial_state_from_measurement(center_uv, alpha_img, measurement_model, cam_pos, cam_rot)
        if x_init is None:
            return None
        self.init_buffer.append(x_init.reshape(-1))
        if len(self.init_buffer) < self.init_z_needed:
            return None
        Z = np.stack(self.init_buffer, axis=0)

        pos = np.asarray(Z[:, :2], dtype=np.float64)

        yaw_idx = 2 if self.state_dim == 5 else 3 # depends on how state vector is defined in different motion models
        yaws = np.asarray(Z[:, yaw_idx], dtype=np.float64)

        try:
            diff = pos - pos.mean(axis=0)
            norm = np.linalg.norm(diff, axis=1)
            maxx = norm.max()
            pos_spread_xy = maxx # max distance from mean position in xy plane, may be too strict
            # pos_spread_xy = np.linalg.norm(pos - pos.mean(axis=0), axis=1).max() # max distance from mean position in xy plane, may be too strict
        except Exception as e:
            self.log_info(f"Error occurred while calculating position spread: {e}")
            self.log_info(f"pos: {pos}, diff: {diff}")
            raise

        c2 = np.mean(np.cos(2.0 * yaws))
        s2 = np.mean(np.sin(2.0 * yaws))
        yaw_mean = wrap(0.5 * np.arctan2(s2, c2))
        yaws_diff = np.array([min(abs(wrap(y - yaw_mean)), abs(wrap((y + np.pi) - yaw_mean))) for y in yaws])
        yaw_spread = np.max(np.abs(yaws_diff))

        if (pos_spread_xy > self.init_pos_max_spread or
            yaw_spread > self.init_yaw_max_spread):
            self.init_buffer.pop(0)
            self.log_info("Initial measurements too spread out, discarding oldest and waiting for more")
            return None
        
        pos_mean = np.mean(pos, axis=0)
        P0 = np.eye(self.state_dim) * 2.0
        P0[0, 0] = max(0.25, np.var(pos[:, 0]) + 0.1)
        P0[1, 1] = max(0.25, np.var(pos[:, 1]) + 0.1)
        if self.motion_model_type == "surface":
            X0 = np.array([[pos_mean[0]], [pos_mean[1]], [yaw_mean], [0.0], [0.0]])
            P0[2, 2] = 0.5
            P0[3, 3] = 1.0
            P0[4, 4] = 1.0
        elif self.motion_model_type == "depth" or self.motion_model_type == "wave" or self.motion_model_type == "oscillator":
            X0 = np.array([[pos_mean[0]], [pos_mean[1]], [0], [yaw_mean], [0.0], [0.0], [0.0]])
            P0[2, 2] = 1.0
            P0[3, 3] = 0.5
            P0[4, 4] = 1.0
            P0[5, 5] = 1.0
            P0[6, 6] = 1.0
        elif self.motion_model_type == "pitch":
            X0 = np.array([[pos_mean[0]], [pos_mean[1]], [0], [yaw_mean], [0.0], [0.0], [0.0], [0.0], [0.0]])
            P0[2, 2] = 1.0
            P0[3, 3] = 0.5
            P0[4, 4] = 0.5
            P0[5, 5] = 1.0
            P0[6, 6] = 1.0
            P0[7, 7] = 1.0
            P0[8, 8] = 1.0
        elif self.motion_model_type == "double_oscillator":
            X0 = np.array([
                [pos_mean[0]],
                [pos_mean[1]],
                [0.0],       # z_slow
                [yaw_mean],
                [0.0],
                [0.0],
                [0.0],       # vz_slow
                [0.0],       # z_fast
                [0.0],       # vz_fast
            ])
            P0[2, 2] = 1.0
            P0[3, 3] = 0.5
            P0[4, 4] = 1.0
            P0[5, 5] = 1.0
            P0[6, 6] = 1.0
            P0[7, 7] = 0.3   
            P0[8, 8] = 1.0
        t0 = stamp.sec + stamp.nanosec * 1e-9
        self.log_info(f"Initialization successful, initial state: {X0.flatten()}")
        self.init_buffer.clear()
        return X0, P0, t0
    