import numpy as np
from collections.abc import Callable   
from .PathParametrizer import PathParametrizer

class ZVD:
    def __init__(self, L: float, xi: float):
        assert L > 0, 'Length must be positive'
        assert 0 < xi < 1, 'Damping must be in (0, 1)'
        self._wn = np.sqrt(9.81 / L)
        self._K  = np.exp((-xi * np.pi) / np.sqrt(1 - xi**2))
        self._dt = np.pi / (self._wn * np.sqrt(1 - xi**2))   

    def computeZVDMatrix(self) -> tuple[np.ndarray, np.ndarray]:
        timeRow = np.array([0.0, self._dt, 2*self._dt])
        den = 1.0 / (self._K**2 + 2*self._K + 1)
        amplitudeRow = np.array([den, 2*self._K*den, (self._K**2)*den])
        assert abs(amplitudeRow.sum() - 1.0) < 1e-12, 'The pulses do not sum to 1'
        return amplitudeRow, timeRow

    def shapeReferences(self, A, T, path:PathParametrizer, t: float):
        p = np.zeros(2)
        v = np.zeros(2)
        for Ai, Ti in zip(A, T):
            pi, vi = path.sample(t - Ti)    
            p += Ai * pi
            v += Ai * vi
        return p, v

    def sampleReferences(self, path:PathParametrizer, ts: float):
        A, T = self.computeZVDMatrix()
        tg = np.arange(0.0, path._missionTime + T[-1] + ts, ts)
        P = np.zeros((len(tg), 2))
        V = np.zeros((len(tg), 2))
        for k, t in enumerate(tg):
            P[k], V[k] = self.shapeReferences(A, T, path, t)
        return tg, P, V