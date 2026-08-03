import numpy as np
import control as ct


class LQR:
    """LQR state feedback for a drone carrying a hook on a rope.

    Model, 10 states / 3 inputs, all in base_flat_link:

        index  state          dynamics
          0    p_x            d(p_x) = v_x
          1    p_y            d(p_y) = v_y
          2    p_z            d(p_z) = v_z
          3    v_x            d(v_x) = -tau_x v_x + k_x u_x
          4    v_y            d(v_y) = -tau_y v_y + k_y u_y
          5    v_z            d(v_z) = -tau_z v_z + k_z u_z
          6    theta_x        d(theta_x) = omega_x
          7    omega_x        d(omega_x) = -(1/L)(-tau_x v_x + k_x u_x) - wn^2 theta_x - 2 xi wn omega_x
          8    theta_y        d(theta_y) = omega_y
          9    omega_y        d(omega_y) = -(1/L)(-tau_y v_y + k_y u_y) - wn^2 theta_y - 2 xi wn omega_y

        inputs u = [vx_cmd, vy_cmd, vz_cmd]  (velocity setpoints, base_flat_link)

    """

    IDX = {
        'p_x': 0, 'p_y': 1, 'p_z': 2,
        'v_x': 3, 'v_y': 4, 'v_z': 5,
        'theta_x': 6, 'omega_x': 7,
        'theta_y': 8, 'omega_y': 9,
    }
    N_STATES = 10
    N_INPUTS = 3

    G = 9.81

    def __init__(self,
                 L: float, xi: float,
                 k_x: float, tau_x: float,
                 k_y: float, tau_y: float,
                 k_z: float, tau_z: float,
                 v_max: float,
                 rho: float = 1.0,
                 p_max: float = 0.3,
                 pz_max: float = 0.3,
                 theta_max: float = 0.1):
        assert L > 0, 'Length must be positive'
        assert 0 < xi < 1, 'Damping must be in (0, 1)'
        assert v_max > 0, 'Vmax must be positive'
        assert rho > 0, 'rho must be positive'

        self._L = L
        self._xi = xi
        self._wn = np.sqrt(self.G / L)
        self._dwn = 2.0 * xi * self._wn

        self._A, self._B, self._C, self._D = self._build_state_space(
            L, k_x, tau_x, k_y, tau_y, k_z, tau_z
        )
        self._sys = ct.StateSpace(self._A, self._B, self._C, self._D)

        self._pMax        = p_max                        
        self._pzMax       = pz_max                       
        self._vMax        = v_max                        
        self._thetaMax    = theta_max                    
        self._thetaDotMax = self._thetaMax * self._wn    

        # z = [p_x, p_y, p_z, th_x, w_x, th_y, w_y, v_z]
        i = self.IDX
        self._M = np.zeros((8, self.N_STATES))
        self._M[0, i['p_x']]     = 1.0
        self._M[1, i['p_y']]     = 1.0
        self._M[2, i['p_z']]     = 1.0
        self._M[3, i['theta_x']] = 1.0
        self._M[4, i['omega_x']] = 1.0
        self._M[5, i['theta_y']] = 1.0
        self._M[6, i['omega_y']] = 1.0
        self._M[7, i['v_z']]     = 1.0

        self._Q1 = np.diag([1/self._pMax**2,
                            1/self._pMax**2,
                            1/self._pzMax**2,
                            1/self._thetaMax**2,
                            1/self._thetaDotMax**2,
                            1/self._thetaMax**2,
                            1/self._thetaDotMax**2,
                            1/self._vMax**2])

        self._Q = self._M.T @ self._Q1 @ self._M

        self._R = rho * np.diag([1/self._vMax**2]*3)

        self._assert_solvable()

        self._K, self._S, self._E = ct.lqr(self._sys, self._Q, self._R)

    def _build_state_space(self, L, k_x, tau_x, k_y, tau_y, k_z, tau_z):
        cx, cy = tau_x / L, tau_y / L
        dx, dy = k_x / L,   k_y / L
        wn2, dwn = self._wn**2, self._dwn

        A = np.array([
            [0, 0, 0,  1,      0,      0,      0,    0,    0,    0   ],
            [0, 0, 0,  0,      1,      0,      0,    0,    0,    0   ],
            [0, 0, 0,  0,      0,      1,      0,    0,    0,    0   ],
            [0, 0, 0, -tau_x,  0,      0,      0,    0,    0,    0   ],
            [0, 0, 0,  0,     -tau_y,  0,      0,    0,    0,    0   ],
            [0, 0, 0,  0,      0,     -tau_z,  0,    0,    0,    0   ],
            [0, 0, 0,  0,      0,      0,      0,    1,    0,    0   ],
            [0, 0, 0,  cx,     0,      0,     -wn2, -dwn,  0,    0   ],
            [0, 0, 0,  0,      0,      0,      0,    0,    0,    1   ],
            [0, 0, 0,  0,      cy,     0,      0,    0,   -wn2, -dwn ],
        ], dtype=float)

        B = np.array([
            [0,    0,    0  ],
            [0,    0,    0  ],
            [0,    0,    0  ],
            [k_x,  0,    0  ],
            [0,    k_y,  0  ],
            [0,    0,    k_z],
            [0,    0,    0  ],
            [-dx,  0,    0  ],
            [0,    0,    0  ],
            [0,   -dy,   0  ],
        ], dtype=float)

        C = np.zeros((14, self.N_STATES))
        for r, s in [(0,0),(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,8),(8,7),(9,9)]:
            C[r, s] = 1.0
        i = self.IDX
        C[10, i['theta_x']] = L
        C[11, i['theta_y']] = L
        C[12, i['omega_x']] = L
        C[13, i['omega_y']] = L

        D = np.zeros((14, self.N_INPUTS))
        return A, B, C, D

    def _assert_solvable(self):
        n = self.N_STATES
        ctrb_rank = np.linalg.matrix_rank(ct.ctrb(self._A, self._B))
        if ctrb_rank < n:
            unstable = [e for e in np.linalg.eigvals(self._A) if e.real > 1e-9]
            if unstable:
                raise ValueError(
                    f'Plant has uncontrollable UNSTABLE modes (ctrb rank {ctrb_rank}/{n}, '
                    f'unstable eigenvalues {unstable}) - LQR would not stabilise it'
                )

    @property
    def K(self):
        return self._K

    @property
    def A(self):
        return self._A

    @property
    def B(self):
        return self._B

    @property
    def C(self):
        return self._C

    @property
    def D(self):
        return self._D

    @property
    def closed_loop_eigenvalues(self):
        return self._E

    def controlAction(self, stateVector: np.ndarray, referenceVector: np.ndarray) -> np.ndarray:
        x = np.asarray(stateVector, float).reshape(-1)
        r = np.asarray(referenceVector, float).reshape(-1)
        if x.size != self.N_STATES or r.size != self.N_STATES:
            raise ValueError(
                f'state/reference must have {self.N_STATES} elements in IDX order, '
                f'got {x.size} and {r.size}'
            )
        return (-self._K @ (x - r))
