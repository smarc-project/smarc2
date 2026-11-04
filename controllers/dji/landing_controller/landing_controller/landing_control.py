"""Landing control calculations, independent of node callbacks and TF lookup."""

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.linalg import solve_discrete_are

from .math_utils import first_order_lowpass, slew_limit
from .model_loader import DiscreteVelocityModel


@dataclass(frozen=True)
class ControlParameters:
    """Runtime tuning and the speed limits selected for the current phase."""

    z_kp: float
    z_kd: float
    max_xy_speed_mps: float
    max_up_speed_mps: float
    max_down_speed_mps: float
    command_cutoff_hz: float
    max_command_rate_mps2: Sequence[float]


@dataclass
class ControlResult:
    """Command and intermediate values used by LandingControllerDebug."""

    lqr_state_xy: np.ndarray
    command_feedforward: np.ndarray
    command_feedback: np.ndarray
    command_raw: np.ndarray
    command_filtered: np.ndarray
    saturated: bool
    rate_limited: bool


class LandingControl:
    """Calculate XY LQR and vertical PD commands in the controller frame.

    Input positions and velocities must already share that frame, with relative
    state defined as drone minus pad. The model and LQR weights are fixed at
    construction; runtime tuning is supplied on each compute call.
    """

    def __init__(
        self,
        model: DiscreteVelocityModel,
        q_diagonal_xy: Sequence[float],
        r_diagonal_xy: Sequence[float],
    ) -> None:
        self._model = model
        a_xy, b_xy = model.xy_position_velocity_matrices()
        q_values = np.asarray(q_diagonal_xy, dtype=float)
        r_values = np.asarray(r_diagonal_xy, dtype=float)
        if q_values.shape != (4,) or r_values.shape != (2,):
            raise ValueError("q_diagonal_xy must have 4 values and r_diagonal_xy 2 values")
        q = np.diag(q_values)
        r = np.diag(r_values)
        p = solve_discrete_are(a_xy, b_xy, q, r)
        self._gain = np.linalg.solve(r + b_xy.T @ p @ b_xy, b_xy.T @ p @ a_xy)
        self._last_command = np.zeros(3, dtype=float)

    @property
    def gain(self) -> np.ndarray:
        return self._gain.copy()

    def reset(self) -> None:
        """Clear command history before restarting the filter from zero."""
        self._last_command[:] = 0.0

    def compute(
        self,
        relative_position: np.ndarray,
        relative_velocity: np.ndarray,
        pad_velocity: np.ndarray,
        height_above_pad: float,
        vertical_reference_velocity: float,
        parameters: ControlParameters,
    ) -> ControlResult:
        """Compute and filter a command using the identified model's sample time."""
        lqr_state = np.array(
            [
                relative_position[0],
                relative_position[1],
                relative_velocity[0],
                relative_velocity[1],
            ],
            dtype=float,
        )
        feedback_xy = -self._gain @ lqr_state

        # Follow pad motion and the requested clearance rate using model gains.
        gains = self._model.dc_gain_vector
        feedforward = np.zeros(3, dtype=float)
        feedforward[:2] = pad_velocity[:2] / gains[:2]
        desired_drone_vertical_velocity = pad_velocity[2] + vertical_reference_velocity
        feedforward[2] = desired_drone_vertical_velocity / gains[2]

        z_position_error = relative_position[2] - height_above_pad
        z_velocity_error = relative_velocity[2] - vertical_reference_velocity
        feedback = np.array(
            [
                feedback_xy[0],
                feedback_xy[1],
                -parameters.z_kp * z_position_error - parameters.z_kd * z_velocity_error,
            ],
            dtype=float,
        )
        raw_command = feedforward + feedback

        lower = np.array(
            [-parameters.max_xy_speed_mps, -parameters.max_xy_speed_mps,
             -parameters.max_down_speed_mps],
            dtype=float,
        )
        upper = np.array(
            [parameters.max_xy_speed_mps, parameters.max_xy_speed_mps,
             parameters.max_up_speed_mps],
            dtype=float,
        )
        saturated_command = np.clip(raw_command, lower, upper)
        saturated = not np.allclose(raw_command, saturated_command, rtol=0.0, atol=1e-12)

        # Order: speed limit, low-pass, slew, speed limit.
        filtered = first_order_lowpass(
            self._last_command,
            saturated_command,
            parameters.command_cutoff_hz,
            self._model.dt,
        )
        rate_values = np.asarray(parameters.max_command_rate_mps2, dtype=float)
        if rate_values.shape != (3,):
            raise ValueError("max_command_rate_mps2 must contain three values")
        filtered, rate_limited = slew_limit(
            self._last_command, filtered, rate_values, self._model.dt,
        )
        filtered = np.clip(filtered, lower, upper)
        self._last_command = filtered.copy()

        return ControlResult(
            lqr_state_xy=lqr_state,
            command_feedforward=feedforward,
            command_feedback=feedback,
            command_raw=raw_command,
            command_filtered=filtered,
            saturated=saturated,
            rate_limited=rate_limited,
        )
