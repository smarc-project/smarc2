import numpy as np
from .geometry_utils import wrap

class SurfaceModel:
    def __init__(self, sigma_a, sigma_yaw):
        self.name = "surface"

        self.sigma_a = sigma_a
        self.sigma_yaw = sigma_yaw
        self.state_dim = 5

        self.eps = [1e-3] * 5 # for numerical jacobian

        self.i_x = 0
        self.i_y = 1
        self.i_yaw = 2
        self.i_vx = 3
        self.i_vy = 4

    def predict(self, X, dt):
        F = np.eye(5)
        F[0, 3] = dt
        F[1, 4] = dt

        px, py, yaw, vx, vy = X.reshape(-1)
        X_pred = np.array([
            [px + vx * dt],
            [py + vy * dt],
            [wrap(yaw)],
            [vx],
            [vy]
        ])
        return X_pred, F

    def build_Q(self, dt):
        Q = np.zeros((5, 5))
        q_cv = np.array([
            [dt**4 / 4.0, dt**3 / 2.0],
            [dt**3 / 2.0, dt**2]
        ])
        Q[np.ix_([0, 3], [0, 3])] = q_cv * (self.sigma_a ** 2)
        Q[np.ix_([1, 4], [1, 4])] = q_cv * (self.sigma_a ** 2)
        Q[2, 2] = (dt * self.sigma_yaw) ** 2
        return Q
    
class DepthModel:
    # may work better than oscillator in very stochastic environments, but less stable in calm water.
    def __init__(self, sigma_a, sigma_z, sigma_yaw):
        self.name = "depth"

        self.sigma_a = sigma_a
        self.sigma_z = sigma_z
        self.sigma_yaw = sigma_yaw
        self.state_dim = 7

        self.eps = [1e-2] * 7 # for numerical jacobian
        self.eps[2] = 5e-2

        self.i_x = 0
        self.i_y = 1
        self.i_z = 2
        self.i_yaw = 3
        self.i_vx = 4
        self.i_vy = 5
        self.i_vz = 6

    def predict(self, X, dt):
        F = np.eye(7)
        F[0, 4], F[1, 5], F[2, 6] = dt, dt, dt
        px, py, z, yaw, vx, vy, vz = X.reshape(-1)

        k_z = 0.4
        d_z = 0.1

        F[6, 2] = -k_z * dt
        F[6, 6] = 1.0 - d_z * dt

        z_new = z + vz * dt
        vz_new = vz + (-k_z * z - d_z * vz) * dt

        X_pred = np.array([
            [px + vx * dt],
            [py + vy * dt],
            [z_new],
            [wrap(yaw)],
            [vx],
            [vy],
            [vz_new]
        ])
        return X_pred, F

    def build_Q(self, dt):
        Q = np.zeros((7, 7))
        q_cv = np.array([
            [dt**4 / 4.0, dt**3 / 2.0],
            [dt**3 / 2.0, dt**2]        
        ])
        Q[np.ix_([0, 4], [0, 4])] = q_cv * (self.sigma_a ** 2)
        Q[np.ix_([1, 5], [1, 5])] = q_cv * (self.sigma_a ** 2)
        Q[np.ix_([2, 6], [2, 6])] = q_cv * (self.sigma_z ** 2)
        Q[3, 3] = (dt * self.sigma_yaw) ** 2
        return Q
    
class PitchModel:
    # motion model that includes pitch dynamics
    # but since pitch is weakly observable, it doesn't work that well.
    # looking at target from an angle can help with observability, but only marginally.
    # obb ratio is a cue, but is noisy and only gives +- angle.
    def __init__(self, sigma_a, sigma_z, sigma_yaw, sigma_pitch):
        self.name = "pitch"
        self.sigma_a = sigma_a
        self.sigma_z = sigma_z
        self.sigma_yaw = sigma_yaw
        self.sigma_pitch = sigma_pitch
        self.state_dim = 9

        self.eps = [1e-2] * 9 # for numerical jacobian
        self.eps[2] = 5e-2
        self.eps[3] = 5e-2

        self.i_x = 0
        self.i_y = 1
        self.i_z = 2
        self.i_yaw = 3
        self.i_pitch = 4
        self.i_vx = 5
        self.i_vy = 6
        self.i_vz = 7
        self.i_pitch_rate = 8

    def predict(self, X, dt):
        F = np.eye(9)
        F[0, 5] = dt
        F[1, 6] = dt
        F[2, 7] = dt
        F[4, 8] = dt

        px, py, pz, yaw, pitch, vx, vy, vz, pitch_rate = X.reshape(-1)

        k_pitch = 0.5
        d_pitch = 0.1

        F[8, 4] = -k_pitch * dt
        F[8, 8] = 1.0 - d_pitch * dt

        pitch_new = pitch + pitch_rate * dt
        pitch_rate_new = pitch_rate + (-k_pitch * pitch - d_pitch * pitch_rate) * dt

        X_pred = np.array([[px + vx * dt],[py + vy * dt],[pz + vz * dt],[wrap(yaw)],[pitch_new],[vx],[vy],[vz],[pitch_rate_new]])
        return X_pred, F

    def build_Q(self, dt):
        Q = np.zeros((9, 9))
        q_cv = np.array([
            [dt**4 / 4.0, dt**3 / 2.0],
            [dt**3 / 2.0, dt**2]        
        ])
        Q[np.ix_([0, 5], [0, 5])] = q_cv * (self.sigma_a ** 2)
        Q[np.ix_([1, 6], [1, 6])] = q_cv * (self.sigma_a ** 2)
        Q[np.ix_([2, 7], [2, 7])] = q_cv * (self.sigma_z ** 2)

        Q[np.ix_([4, 8], [4, 8])] = q_cv * (self.sigma_pitch ** 2)

        Q[3, 3] = (dt * self.sigma_yaw) ** 2
        return Q

class OscillatorModel:
    # auv as oscillator
    def __init__(self, sigma_a, sigma_z, sigma_yaw,
                 omega=2.0, zeta=0.01):
        self.name = "oscillator"
        self.sigma_a = sigma_a
        self.sigma_z = sigma_z
        self.sigma_yaw = sigma_yaw

        self.eps = [1e-2] * 7 # for numerical jacobian
        self.eps[2] = 5e-2

        self.omega = omega 
        self.zeta = zeta 

        self.i_x = 0
        self.i_y = 1
        self.i_z = 2
        self.i_yaw = 3
        self.i_vx = 4
        self.i_vy = 5
        self.i_vz = 6
        self.state_dim = 7

    def predict(self, X, dt):

        px, py, z, yaw, vx, vy, vz = X.reshape(-1)

        px_new = px + vx * dt
        py_new = py + vy * dt

        z_new = z + vz * dt
        az = -2.0 * self.zeta * self.omega * vz - (self.omega ** 2) * z
        vz_new = vz + az * dt

        X_pred = np.array([
            [px_new],
            [py_new],
            [z_new],
            [wrap(yaw)],
            [vx],
            [vy],
            [vz_new],
        ])

        F = np.eye(7)
        F[self.i_x, self.i_vx] = dt
        F[self.i_y, self.i_vy] = dt
        F[self.i_z, self.i_vz] = dt
        F[self.i_vz, self.i_z] = -(self.omega ** 2) * dt
        F[self.i_vz, self.i_vz] = 1.0 - 2.0 * self.zeta * self.omega * dt

        return X_pred, F

    def build_Q(self, dt):
        Q = np.zeros((7, 7))
        q_cv = np.array([
            [dt**4 / 4.0, dt**3 / 2.0],
            [dt**3 / 2.0, dt**2]        
        ])
        Q[np.ix_([self.i_x, self.i_vx], [self.i_x, self.i_vx])] = q_cv * (self.sigma_a ** 2)
        Q[np.ix_([self.i_y, self.i_vy], [self.i_y, self.i_vy])] = q_cv * (self.sigma_a ** 2)
        Q[np.ix_([self.i_z, self.i_vz], [self.i_z, self.i_vz])] = q_cv * (self.sigma_z ** 2)
        Q[self.i_yaw, self.i_yaw] = (dt * self.sigma_yaw) ** 2
        return Q
    
class DoubleOscillatorModel:
    # AUV z motion as superposition of slow oscillation + faster oscillation
    def __init__(
        self,
        sigma_a=0.01,
        sigma_z_slow=1.0,
        sigma_z_fast=3.0,
        sigma_yaw=0.1,
        omega_slow=1.0,
        zeta_slow=0.01,
        omega_fast=2.0,
        zeta_fast=0.01,
    ):
        self.name = "double_oscillator"

        self.sigma_a = sigma_a
        self.sigma_z_slow = sigma_z_slow
        self.sigma_z_fast = sigma_z_fast
        self.sigma_yaw = sigma_yaw

        self.omega_slow = omega_slow
        self.zeta_slow = zeta_slow
        self.omega_fast = omega_fast
        self.zeta_fast = zeta_fast

        self.state_dim = 9

        self.i_x = 0
        self.i_y = 1
        self.i_z_slow = 2
        self.i_yaw = 3
        self.i_vx = 4
        self.i_vy = 5
        self.i_vz_slow = 6
        self.i_z_fast = 7
        self.i_vz_fast = 8

        self.eps = [1e-2] * self.state_dim
        self.eps[self.i_z_slow] = 5e-2
        self.eps[self.i_z_fast] = 5e-2

    def predict(self, X, dt):
        px, py, z_s, yaw, vx, vy, vz_s, z_f, vz_f = X.reshape(-1)

        px_new = px + vx * dt
        py_new = py + vy * dt

        # slow oscillator
        az_s = -2.0 * self.zeta_slow * self.omega_slow * vz_s - (self.omega_slow ** 2) * z_s
        z_s_new = z_s + vz_s * dt
        vz_s_new = vz_s + az_s * dt

        # Fast oscillator
        az_f = -2.0 * self.zeta_fast * self.omega_fast * vz_f - (self.omega_fast ** 2) * z_f
        z_f_new = z_f + vz_f * dt
        vz_f_new = vz_f + az_f * dt

        X_pred = np.array([
            [px_new],
            [py_new],
            [z_s_new],
            [wrap(yaw)],
            [vx],
            [vy],
            [vz_s_new],
            [z_f_new],
            [vz_f_new],
        ])

        F = np.eye(self.state_dim)

        F[self.i_x, self.i_vx] = dt
        F[self.i_y, self.i_vy] = dt

        F[self.i_z_slow, self.i_vz_slow] = dt
        F[self.i_vz_slow, self.i_z_slow] = -(self.omega_slow ** 2) * dt
        F[self.i_vz_slow, self.i_vz_slow] = 1.0 - 2.0 * self.zeta_slow * self.omega_slow * dt

        F[self.i_z_fast, self.i_vz_fast] = dt
        F[self.i_vz_fast, self.i_z_fast] = -(self.omega_fast ** 2) * dt
        F[self.i_vz_fast, self.i_vz_fast] = 1.0 - 2.0 * self.zeta_fast * self.omega_fast * dt

        return X_pred, F

    def build_Q(self, dt):
        Q = np.zeros((self.state_dim, self.state_dim))

        q_cv = np.array([
            [dt**4 / 4.0, dt**3 / 2.0],
            [dt**3 / 2.0, dt**2],
        ])

        Q[np.ix_([self.i_x, self.i_vx], [self.i_x, self.i_vx])] = q_cv * (self.sigma_a ** 2)
        Q[np.ix_([self.i_y, self.i_vy], [self.i_y, self.i_vy])] = q_cv * (self.sigma_a ** 2)

        Q[np.ix_([self.i_z_slow, self.i_vz_slow], [self.i_z_slow, self.i_vz_slow])] = q_cv * (self.sigma_z_slow ** 2)

        Q[np.ix_([self.i_z_fast, self.i_vz_fast], [self.i_z_fast, self.i_vz_fast])] = q_cv * (self.sigma_z_fast ** 2)

        Q[self.i_yaw, self.i_yaw] = (dt * self.sigma_yaw) ** 2

        return Q