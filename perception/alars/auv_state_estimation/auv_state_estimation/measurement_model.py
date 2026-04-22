import numpy as np
import cv2
from scipy.spatial.transform import Rotation as R
from .geometry_utils import wrap, residual_z

class MeasurementModel: 
    def __init__(
            self, 
            width,
            height,
            meas_dim, 
            state_dim, 
            eps,
            eps_pose_pos,
            eps_pose_ang,
            K, 
            D, 
            z_water, 
            n_air, 
            n_water, 
            obb_length_m, 
            obb_width_m, 
            motion_model, #TODO weird usage of this :)
            logger=None
                 ):
        
        self.width = width
        self.height = height
        self.meas_dim = meas_dim
        self.state_dim = state_dim
        self.eps = eps
        self.eps_pose_pos = eps_pose_pos
        self.eps_pose_ang = eps_pose_ang
        self.width = width
        self.height = height
        self.K = K
        self.D = D
        self.z_water = z_water
        self.n_air = n_air
        self.n_water = n_water
        self.obb_length_m = obb_length_m
        self.obb_width_m = obb_width_m
        self.motion_model = motion_model
        self.logger = logger

    def get_logger(self, msg):
        if self.logger is not None:
            self.logger.info(msg)

    def norm_to_pixels(self, pts_norm):

        # convert normalized coordinates [-1, 1] to pixel coordinates [0, width] and [0, height]

        u = (pts_norm[:, 0] + 1.0) * 0.5 * self.width
        v = (pts_norm[:, 1] + 1.0) * 0.5 * self.height
        #self.get_logger(f"Converted normalized points to pixels: {list(zip(u, v))}")
        return np.stack([u, v], axis=1)
    
    def get_obb_features(self, pts):

        # compute oriented bounding box features (center, angle, length, width) from pixel coordinates
        # this avoids issue with matching obb corners

        center = pts.mean(axis=0)
        centered = pts - center
        cov = np.cov(centered.T)
        eigvals, eigvecs = np.linalg.eigh(cov)
        major = eigvecs[:, np.argmax(eigvals)]
        minor = eigvecs[:, np.argmin(eigvals)]
        alpha = wrap(np.arctan2(major[1], major[0]))
        proj_major = centered @ major
        proj_minor = centered @ minor
        len_px = np.max(proj_major) - np.min(proj_major)
        wid_px = np.max(proj_minor) - np.min(proj_minor)
        #self.get_logger(f"OBB features - Center: {center}, Alpha: {alpha}, Length: {len_px}, Width: {wid_px}")
        return center, alpha, len_px, wid_px

    def extract_features(self, pts_norm):

        # extract measurement features from normalized points: convert to pixels, then compute OBB features

        pts_uv = self.norm_to_pixels(pts_norm)
        center_uv, alpha_img, len_px, wid_px = self.get_obb_features(pts_uv)
        return center_uv, alpha_img, len_px, wid_px, pts_uv
    
    def projection(self, x, cam_pos, cam_rot):

        # project a 3D point in the map frame to pixel coordinates 
        # given the camera pose (position and rotation) in the map frame

        R_wc = cam_rot.T
        t_wc = -R_wc @ cam_pos
        rvec, _ = cv2.Rodrigues(R_wc)
        tvec = t_wc.reshape(3, 1)
        obj_pt = np.asarray(x).reshape(1, 1, 3)
        img_pts, _ = cv2.projectPoints(obj_pt, rvec, tvec, self.K, self.D)
        uv = img_pts.reshape(2)
        return uv
    
    def back_projection(self, uv, cam_rot):

        # given pixel coordinates and camera rotation, compute the corresponding ray in the map frame

        pts_uv = np.asarray(uv).reshape(-1, 1, 2)
        und = cv2.undistortPoints(pts_uv, self.K, self.D)
        x = und[:, 0, 0]
        y = und[:, 0, 1]
        ray_cam = np.array([x[0], y[0], 1.0])
        ray_map = cam_rot @ ray_cam
        ray = ray_map / np.linalg.norm(ray_map)
        return ray
    
    def numerical_H(self, x, cam_pos_map, R_map_cam):
        
        #Compute numerical measurement jacobian H = dz/dx by finite differences.
        
        H = np.zeros((self.meas_dim, self.state_dim))
        mm = self.motion_model

        yaw_idx = getattr(mm, "i_yaw", None)

        for i in range(self.state_dim):
            eps = self.eps[i]

            x_plus_eps = x.copy()
            x_minus_eps = x.copy()
            x_plus_eps[i, 0] += eps
            x_minus_eps[i, 0] -= eps

            if yaw_idx is not None and i == yaw_idx: # wrap yaw angle perturbations 
                x_plus_eps[i, 0] = wrap(x_plus_eps[i, 0])
                x_minus_eps[i, 0] = wrap(x_minus_eps[i, 0])

            z_plus_eps = self.hx(x_plus_eps, cam_pos_map, R_map_cam)
            z_minus_eps = self.hx(x_minus_eps, cam_pos_map, R_map_cam)

            if z_plus_eps is None or z_minus_eps is None:
                return None

            dz = residual_z(z_plus_eps, z_minus_eps) / (2.0 * eps)
            H[:, i] = dz.reshape(-1)

        return H
    
    def cam_pose_perturbation(self, cam_pos, cam_rot, delta):

        # apply a small perturbation to the camera pose (position and rotation) and return the perturbed pose
        # helper function for numerical Jacobian with respect to camera pose

        dpos = delta[:3]
        drot = delta[3:]
        cam_pos_pert = cam_pos + dpos
        R_delta = R.from_rotvec(drot).as_matrix()
        R_map_cam_pert = R_delta @ cam_rot
        return cam_pos_pert, R_map_cam_pert
    
    def numerical_J_pose(self, x_ref, cam_pos_map, R_map_cam):

        # compute numerical measurement Jacobian with respect to camera pose J = dz/dp by finite differences
        # this captures how camera pose uncertainty affects the measurement prediction

        J = np.zeros((self.meas_dim, 6))
        for i in range(6):
            eps = self.eps_pose_ang if i >= 3 else self.eps_pose_pos
            delta_plus = np.zeros(6)
            delta_minus = np.zeros(6)
            delta_plus[i] = eps
            delta_minus[i] = -eps
            cam_pos_p, R_map_cam_p = self.cam_pose_perturbation(cam_pos_map, R_map_cam, delta_plus)
            cam_pos_m, R_map_cam_m = self.cam_pose_perturbation(cam_pos_map, R_map_cam, delta_minus)
            z_plus = self.hx(x_ref, cam_pos_p, R_map_cam_p)
            z_minus = self.hx(x_ref, cam_pos_m, R_map_cam_m)
            if z_plus is None or z_minus is None:
                return None
            dz = residual_z(z_plus, z_minus) / (2.0 * eps)
            J[:, i] = dz.reshape(-1)
        return J
    
    def hx(self, x, cam_pos_map, R_map_cam):

        # given a state x, compute the expected measurement by projecting the corresponding 3D point to pixel coordinates
        # this is the nonlinear measurement function h(x) used in the EKF update

        state = np.asarray(x).reshape(-1)
        if self.motion_model.name == "surface":
            px, py, yaw = state[:3]
            pz = self.z_water
            pitch = 0.0
        elif self.motion_model.name == "depth" or self.motion_model.name == "depth9d" or self.motion_model.name == "wave" or self.motion_model.name == "oscillator":
            px, py, pz, yaw = state[:4]
            pitch = 0.0
        else:
            px, py, pz, yaw, pitch = state[:5]
        center = np.array([px, py, pz])
        pts_map = self.sample_capsule_points(center=center, yaw=yaw, pitch=pitch, length_m=self.obb_length_m, 
                                             radius_m=0.5 * self.obb_width_m, n_len=5, n_ang=16)
        pts_img = []
        for p in pts_map:
            uv = self.projection(p, cam_pos_map, R_map_cam)
            if uv is None:
                continue
            u, v = uv[0], uv[1]
            if 0.0 <= u <= self.width and 0.0 <= v <= self.height:
                pts_img.append([u, v])
        if len(pts_img) < 5:
            return None
        pts_img = np.asarray(pts_img, dtype=np.float32)
        rect = cv2.minAreaRect(pts_img)
        box = cv2.boxPoints(rect)
        expected_meas = self.get_obb_features(box)
        z_center_img, z_alpha_img, z_len_px, z_wid_px = expected_meas
        return np.array([[z_center_img[0]], [z_center_img[1]], [z_alpha_img], [z_len_px], [z_wid_px]])

    def orthonormal_basis(self, axis):

        # given a 3D axis, compute an orthonormal basis (axis, n1, n2) where n1 and n2 are perpendicular to the axis and to each other
        # this is used for sampling points on the capsule surface in the measurement function

        axis = np.asarray(axis)
        axis /= np.linalg.norm(axis)
        helper = np.array([0.0, 0.0, 1.0])
        if abs(np.dot(axis, helper)) > 0.95:
            helper = np.array([1.0, 0.0, 0.0])
        n1 = np.cross(axis, helper)
        n1 /= np.linalg.norm(n1)
        n2 = np.cross(axis, n1)
        n2 /= np.linalg.norm(n2)
        return axis, n1, n2
    
    def sample_capsule_points(self, center, yaw, pitch, length_m, radius_m, n_len=5, n_ang=24):

        # sample points on the surface of a capsule defined by its center, orientation (yaw, pitch), length, and radius
        # this is used to generate the 3D points corresponding to the AUV shape for projection in the measurement function

        c = np.asarray(center)
        axis = np.array([np.cos(yaw) * np.cos(pitch), np.sin(yaw) * np.cos(pitch), np.sin(pitch)])
        axis, n1, n2 = self.orthonormal_basis(axis)
        half_l = 0.5 * length_m
        pts = []
        s_vals = np.linspace(-half_l, half_l, n_len)
        phi_vals = np.linspace(0.0, 2.0 * np.pi, n_ang, endpoint=False)
        for s in s_vals:
            axis_pt = c + s * axis
            for phi in phi_vals:
                radial = np.cos(phi) * n1 + np.sin(phi) * n2
                p = axis_pt + radius_m * radial
                pts.append(p)
        return np.asarray(pts)
