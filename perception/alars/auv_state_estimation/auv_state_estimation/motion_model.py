import numpy as np
from .geometry_utils import wrap

class SurfaceModel5D:
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
    
class DepthModel7D:
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
    
class PitchModel9D:
    # motion model that includes pitch dynamics
    # but since pitch is weakly observable, it doesn't work that well.
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

class DepthModel9D:
    # motion model that includes simple state of water
    # water is modeled as a oscillator that the auv tries to follow, with some lag and damping.
    def __init__(self, sigma_a, sigma_z, sigma_yaw,
                 omega=2.0, zeta=0.1, k_follow=0.6, d_follow=0.2, c_eta=0.8):
        self.name = "depth9d"
        self.sigma_a = sigma_a
        self.sigma_z = sigma_z
        self.sigma_yaw = sigma_yaw

        self.eps = [1e-2] * 9 # for numerical jacobian
        self.eps[2] = 5e-2

        self.omega = omega # natural frequency of the water oscillator, may want to make this adaptive in the future.
        self.zeta = zeta # damping of oscillator

        # how the auv follows water surface, allows for more freedom in the motion
        self.k_follow = k_follow # how strongly the auv tries to follow the water surface
        self.d_follow = d_follow # how much the auv damps its z velocity
        self.c_eta = c_eta # how much the water state affects the target depth

        self.i_x = 0
        self.i_y = 1
        self.i_z = 2
        self.i_yaw = 3
        self.i_vx = 4
        self.i_vy = 5
        self.i_vz = 6
        self.i_eta = 7
        self.i_eta_dot = 8
        self.state_dim = 9

    def predict(self, X, dt):

        px, py, z, yaw, vx, vy, vz, eta, eta_dot = X.reshape(-1)

        px_new = px + vx * dt
        py_new = py + vy * dt

        z_target = self.c_eta * eta
        az = -self.k_follow * (z - z_target) - self.d_follow * vz
        z_new = z + vz * dt
        vz_new = vz + az * dt

        eta_new = eta + eta_dot * dt
        eta_ddot = -2.0 * self.zeta * self.omega * eta_dot - (self.omega ** 2) * eta
        eta_dot_new = eta_dot + eta_ddot * dt

        X_pred = np.array([
            [px_new],
            [py_new],
            [z_new],
            [wrap(yaw)],
            [vx],
            [vy],
            [vz_new],
            [eta_new],
            [eta_dot_new]
        ])

        F = np.eye(9)
        F[self.i_x, self.i_vx] = dt
        F[self.i_y, self.i_vy] = dt
        F[self.i_z, self.i_vz] = dt
        F[self.i_eta, self.i_eta_dot] = dt
        F[self.i_vz, self.i_z] = -self.k_follow * dt
        F[self.i_vz, self.i_vz] = 1.0 - self.d_follow * dt
        F[self.i_vz, self.i_eta] = self.k_follow * self.c_eta * dt
        F[self.i_eta_dot, self.i_eta] = -(self.omega ** 2) * dt
        F[self.i_eta_dot, self.i_eta_dot] = 1.0 - 2.0 * self.zeta * self.omega * dt

        return X_pred, F

    def build_Q(self, dt):
        Q = np.zeros((9, 9))
        q_cv = np.array([
            [dt**4 / 4.0, dt**3 / 2.0],
            [dt**3 / 2.0, dt**2]        
        ])
        Q[np.ix_([self.i_x, self.i_vx], [self.i_x, self.i_vx])] = q_cv * (self.sigma_a ** 2)
        Q[np.ix_([self.i_y, self.i_vy], [self.i_y, self.i_vy])] = q_cv * (self.sigma_a ** 2)
        Q[np.ix_([self.i_z, self.i_vz], [self.i_z, self.i_vz])] = q_cv * (self.sigma_z ** 2)
        Q[np.ix_([self.i_eta, self.i_eta_dot], [self.i_eta, self.i_eta_dot])] = q_cv * (1.0 ** 2) # TODO: put noise on eta in ekf_params
        Q[self.i_yaw, self.i_yaw] = (dt * self.sigma_yaw) ** 2
        return Q
    
class DepthModel7DWave:
    # modelling the wave as external disturbance, needs seperate estimator for wave state
    def __init__(self, sigma_a, sigma_z, sigma_yaw,
                 k_follow=1.0, d_follow=0.1):
        self.name = "wave"

        self.sigma_a = sigma_a
        self.sigma_z = sigma_z
        self.sigma_yaw = sigma_yaw

        self.k_follow = k_follow
        self.d_follow = d_follow

        self.eps = [1e-2] * 7 # for numerical jacobian
        self.eps[2] = 5e-2
        self.state_dim = 7

        self.i_x = 0
        self.i_y = 1
        self.i_z = 2
        self.i_yaw = 3
        self.i_vx = 4
        self.i_vy = 5
        self.i_vz = 6

    def predict(self, X, dt, eta=0.0, eta_dot=0.0):
        F = np.eye(7)
        F[0, 4] = dt
        F[1, 5] = dt
        F[2, 6] = dt

        px, py, z, yaw, vx, vy, vz = X.reshape(-1)

        az = -self.k_follow * (z - eta) - self.d_follow * (vz - eta_dot)

        z_new = z + vz * dt
        vz_new = vz + az * dt

        F[6, 2] = -self.k_follow * dt
        F[6, 6] = 1.0 - self.d_follow * dt

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


class OscillatorModel:
    # auv as oscillator
    def __init__(self, sigma_a, sigma_z, sigma_yaw,
                 omega=1.0, zeta=0.1):
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
        Q[np.ix_([self.i_z, self.i_vz], [self.i_z, self.i_vz])] = 0.2 * (self.sigma_z ** 2)
        Q[self.i_yaw, self.i_yaw] = (dt * self.sigma_yaw) ** 2
        return Q