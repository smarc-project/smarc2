import numpy as np
from .geometry_utils import wrap, residual_z

class EKFCore:
    def __init__(
            self, 
            z_water=0.0,
            state_dim=5, 
            outlier_threshold=0.0, 
            logger=None
            ):
        
        self.z_water = z_water
        self.state_dim = state_dim
        self.outlier_threshold = outlier_threshold
        self.last_t = None
        self.initialized = False
        self.logger = logger
        self.X = np.zeros((self.state_dim, 1))
        self.P = np.eye(self.state_dim) * 10.0
        self.Q = np.eye(self.state_dim) * 1e-3
        self.nr_of_consecutive_outliers = 0
    
    def set_state(self, X0, P0, t0):

        # directly set the state and covariance, used for initialization or reset

        self.X = X0
        self.P = P0
        self.last_t = t0


    def update(self, z, h, H, R):

        # EKF update step.
        # performs gating based on mahalanobis distance.

        if h is None or H is None:
            return self.X, self.P
        innov = residual_z(z, h).reshape(z.shape[0], 1)
        S = H @ self.P @ H.T + R
        try:
            S_inv = np.linalg.inv(S)
        except np.linalg.LinAlgError:
            if self.logger:
                self.logger.info("Gating failed: S singular")
            return self.X, self.P
        d2 = float(innov.T @ S_inv @ innov)
        if d2 > self.outlier_threshold:
            self.nr_of_consecutive_outliers += 1
            if self.logger:
                self.logger.info(f"Outlier detected with mahalanobis distance squared: {d2:.3f}")
            return self.X, self.P
        K = self.P @ H.T @ S_inv
        self.X = self.X + K @ innov
        yaw_idx = 2 if self.state_dim == 5 else 3
        self.X[yaw_idx, 0] = wrap(self.X[yaw_idx, 0])
        I = np.eye(self.state_dim)
        #self.P = (I - K @ H) @ self.P # standard form, but can be numerically unstable
        IKH = I - K @ H
        self.P = IKH @ self.P @ IKH.T + K @ R @ K.T # joseph form for numerical stability
        #self.P = 0.5 * (self.P + self.P.T) + 1e-9 * np.eye(self.state_dim) # ensure symmetry and numerical stability
        self.nr_of_consecutive_outliers = 0
        return self.X, self.P
    
    def predict(self, x_pred, F, Q, t):
        self.X = x_pred
        self.P = F @ self.P @ F.T + Q
        self.last_t = t
        return self.X, self.P
    
