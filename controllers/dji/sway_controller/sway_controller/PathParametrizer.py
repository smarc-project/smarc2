import numpy as np
import sympy as sp


class PathParametrizer:
    def __init__(self,
                 startingDronePosition: np.ndarray,
                 targetPosition: np.ndarray,
                 maxSpeed: float,
                 maxAcceleration: float, 
                 extraTime: float = 0):

        displacement = np.asarray(targetPosition, float) - np.asarray(startingDronePosition, float)
        self._p0 = np.asarray(startingDronePosition, float)
        self._totalDistance = np.linalg.norm(displacement)

        if self._totalDistance < 1e-9:
            self._missionTime = 0.0
            self._dir = np.zeros_like(displacement)
            self._s_fn = lambda t: 0.0
            self._v_fn = lambda t: 0.0
            return

        self._dir = displacement / self._totalDistance

        self._missionTime = max(
            1.875 * self._totalDistance / maxSpeed,
            np.sqrt(5.7735 * self._totalDistance / maxAcceleration),
        ) + self._totalDistance

        t = sp.Symbol('t')
        tau = t / self._missionTime                                
        s = self._totalDistance * (10 * tau**3 - 15 * tau**4 + 6 * tau**5)
        v = sp.diff(s, t)
        a = sp.diff(v, t)

        self._s_fn = sp.lambdify(t, s, 'numpy')
        self._v_fn = sp.lambdify(t, v, 'numpy')
        self._a_fn = sp.lambdify(t, a, 'numpy')                     

    def sample(self, t: float):
        
        tc = min(max(t, 0.0), self._missionTime)          
        s = float(self._s_fn(tc))
        v = float(self._v_fn(tc)) if 0.0 <= t <= self._missionTime else 0.0
        
        p_ref = self._p0 + s * self._dir
        v_ref = v * self._dir
        return p_ref, v_ref