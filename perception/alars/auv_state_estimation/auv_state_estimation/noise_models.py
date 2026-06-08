import numpy as np

class NoiseModels:
    def __init__(
            self, 
            width, 
            height, 
            R_u, 
            R_v, 
            R_alpha, 
            R_len, 
            R_wid, 
            R_pose_x, 
            R_pose_y, 
            R_pose_z, 
            R_pose_r, 
            R_pose_p, 
            R_pose_yaw,
            R_dyn_center_gain_u, 
            R_dyn_center_gain_v, 
            R_dyn_center_gain_alpha, 
            R_dyn_center_gain_len, 
            R_dyn_center_gain_wid,
            R_dyn_speed_gain_u, 
            R_dyn_speed_gain_v, 
            R_dyn_speed_gain_alpha, 
            R_dyn_speed_gain_len, 
            R_dyn_speed_gain_wid,
            R_dyn_dt, 
            meas_dim, 
            logger=None
            ):
        
        self.width = width
        self.height = height
        self.R_u = R_u
        self.R_v = R_v
        self.R_alpha = R_alpha
        self.R_len = R_len
        self.R_wid = R_wid
        self.R_pose_x = R_pose_x
        self.R_pose_y = R_pose_y
        self.R_pose_z = R_pose_z
        self.R_pose_r = R_pose_r
        self.R_pose_p = R_pose_p
        self.R_pose_yaw = R_pose_yaw
        self.R_dyn_center_gain_u = R_dyn_center_gain_u
        self.R_dyn_center_gain_v = R_dyn_center_gain_v
        self.R_dyn_center_gain_alpha = R_dyn_center_gain_alpha
        self.R_dyn_center_gain_len = R_dyn_center_gain_len
        self.R_dyn_center_gain_wid = R_dyn_center_gain_wid
        self.R_dyn_speed_gain_u = R_dyn_speed_gain_u
        self.R_dyn_speed_gain_v = R_dyn_speed_gain_v
        self.R_dyn_speed_gain_alpha = R_dyn_speed_gain_alpha
        self.R_dyn_speed_gain_len = R_dyn_speed_gain_len
        self.R_dyn_speed_gain_wid = R_dyn_speed_gain_wid
        self.R_dyn_dt = R_dyn_dt
        self.meas_dim = meas_dim
        self.logger = logger
    
    def build_image_measurement_covariance(self, center_uv, lin_vel_map):
        # Compute measurement covariance R for image-based measurements, dynamically adjusting based on position and speed.
        img_center = np.array([0.5 * self.width, 0.5 * self.height])
        diag_half = 0.5 * np.hypot(self.width, self.height)
        center_dist = np.linalg.norm(center_uv - img_center)
        center_dist_norm = center_dist / max(diag_half, 1e-6)
        speed = np.linalg.norm(lin_vel_map)
        sigma_u = self.R_u + self.R_dyn_center_gain_u * center_dist_norm + self.R_dyn_speed_gain_u * speed
        sigma_v = self.R_v + self.R_dyn_center_gain_v * center_dist_norm + self.R_dyn_speed_gain_v * speed
        sigma_alpha = self.R_alpha + self.R_dyn_center_gain_alpha * center_dist_norm + self.R_dyn_speed_gain_alpha * speed
        if self.meas_dim == 3:
            return np.diag([sigma_u ** 2, sigma_v ** 2, sigma_alpha ** 2])
        sigma_len = self.R_len + self.R_dyn_center_gain_len * center_dist_norm + self.R_dyn_speed_gain_len * speed
        sigma_wid = self.R_wid + self.R_dyn_center_gain_wid * center_dist_norm + self.R_dyn_speed_gain_wid * speed
        return np.diag([sigma_u ** 2, sigma_v ** 2, sigma_alpha ** 2, sigma_len ** 2, sigma_wid ** 2])

    def build_pose_covariance(self, lin_vel_map, ang_vel_map):
        # Compute pose covariance Sigma for the drone, dynamically adjusting based on linear and angular velocities.
        vel_map = np.array(lin_vel_map)
        yaw_rate = ang_vel_map[2]
        sigma_constant = np.diag([self.R_pose_x**2, self.R_pose_y**2, self.R_pose_z**2, self.R_pose_r**2, self.R_pose_p**2, self.R_pose_yaw**2])
        sigma_dyn = np.zeros((6, 6))
        v_xy = vel_map[:2]
        speed_xy = np.linalg.norm(v_xy)

        # increses noise in direction of motion, and perpendicular to motion, based on speed.
        # also increases noise in z based on vertical speed, and in yaw based on yaw rate.

        if speed_xy > 1e-6:
            speed_dir = v_xy / speed_xy
            speed_perp = np.array([-speed_dir[1], speed_dir[0]])
            sigma_par = self.R_dyn_dt * speed_xy
            sigma_perp = 0.3 * sigma_par 
            Sigma_xy = sigma_par**2 * np.outer(speed_dir, speed_dir) + sigma_perp**2 * np.outer(speed_perp, speed_perp)
            sigma_dyn[0:2, 0:2] = Sigma_xy
        sigma_dyn[2, 2] = (self.R_dyn_dt * abs(vel_map[2])) ** 2
        sigma_dyn[5, 5] = (self.R_dyn_dt * abs(yaw_rate)) ** 2
        return sigma_constant + sigma_dyn
    
    def project_pose_covariance_to_measurement(self, J_pose, lin_vel_map, ang_vel_map):
        # Project pose covariance Sigma_pose to measurement space using Jacobian J_pose.
        Sigma_pose = self.build_pose_covariance(lin_vel_map, ang_vel_map)
        if J_pose is None:
            if self.meas_dim == 3:
                return np.diag([self.R_u**2, self.R_v**2, self.R_alpha**2])
            return np.diag([self.R_u**2, self.R_v**2, self.R_alpha**2, self.R_len**2, self.R_wid**2])
        R_pose = J_pose @ Sigma_pose @ J_pose.T
        R_pose = 0.5 * (R_pose + R_pose.T)
        R_pose += 1e-9 * np.eye(self.meas_dim)
        return R_pose
