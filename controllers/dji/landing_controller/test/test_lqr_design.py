from pathlib import Path

import numpy as np
from scipy.linalg import solve_discrete_are

from landing_controller.model_loader import load_velocity_model


CONFIG = Path(__file__).resolve().parents[1] / "config"


def test_xy_lqr_closed_loop_is_stable() -> None:
    model = load_velocity_model(CONFIG / "m350_discrete.yaml")
    a, b = model.xy_position_velocity_matrices()
    q = np.diag([12.0, 12.0, 4.0, 4.0])
    r = np.diag([1.0, 1.0])
    p = solve_discrete_are(a, b, q, r)
    gain = np.linalg.solve(r + b.T @ p @ b, b.T @ p @ a)
    eigenvalues = np.linalg.eigvals(a - b @ gain)
    assert np.max(np.abs(eigenvalues)) < 1.0
