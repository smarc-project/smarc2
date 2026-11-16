"""Estimate pad velocity and predict XY motion during detection loss.

Velocity is estimated and filtered from pad poses in map. When enabled,
prediction uses saved XY velocity and holds Z, with its time limit measured
from the last real observation.
"""

from collections import deque
from copy import deepcopy

from nav_msgs.msg import Odometry
import numpy as np
from rclpy.time import Time

from .math_utils import numpy_to_vector3, rotation, vector3_to_numpy


class PadMotionHandler:
    """Estimate pad velocity from recent poses and predict position during detection loss."""
    
    VELOCITY_FILTER_TAU_S = 0.25
    MIN_VELOCITY_DT_S = 0.01
    MAX_VELOCITY_GAP_S = 1.5
    PREDICTION_START_AFTER_S = 0.4
    REACQUIRE_DWELL_S = 0.3
    HISTORY_WINDOW_S = 0.75
    HISTORY_MIN_SAMPLES = 4
    HISTORY_MIN_SPAN_S = 0.25
    VELOCITY_VARIANCE = 0.1
    PREDICTION_POSITION_VARIANCE_RATE = 0.003
    PREDICTION_VELOCITY_VARIANCE_RATE = 0.003

    def __init__(
            self, max_prediction_s=10.0, max_observation_age_s=1.5,
            allow_drone_velocity_fallback=False):
        self.max_prediction_s = max_prediction_s
        self.max_observation_age_s = max_observation_age_s
        self.allow_drone_velocity_fallback = allow_drone_velocity_fallback
        self.reset()

    def reset(self):
        """Clear one attempt, including real observations and prediction history."""
        self.velocity_ready = False
        self.prediction_active = False
        self.prediction_velocity_source = ''
        self.last_observation_stamp = None
        self._last_observation = None
        self._last_input_stamp = None
        self._last_input_received_at = None
        self._previous_position = self._previous_stamp = None
        self._filtered_velocity = np.zeros(3)
        self._position_history = deque()
        self._drone_velocity_history = deque()
        self._frozen_velocity = None
        self._reacquire_since = None

    def stop_prediction(self):
        """Leave terminal prediction while keeping recent visual history."""
        self.prediction_active = False
        self.prediction_velocity_source = ''
        self._frozen_velocity = None
        self._reacquire_since = None

    @property
    def last_observation(self):
        """Return real odometry separately from any current prediction."""
        return deepcopy(self._last_observation)

    def reject_observation(self):
        """Interrupt reacquisition without discarding the trusted prediction anchor."""
        self._reacquire_since = None

    def observation_age(self, now: Time):
        """Age of the last accepted real measurement, independent of forecasts."""
        if self.last_observation_stamp is None:
            return float('inf')
        return (now.nanoseconds - self.last_observation_stamp.nanoseconds) * 1e-9

    def update_gap(self, now: Time):
        """Time since receipt of a new valid pad pose, separate from source age."""
        if self._last_input_received_at is None:
            return float('inf')
        return (now - self._last_input_received_at).nanoseconds * 1e-9

    def observe(self, odometry: Odometry, now: Time, *, fresh=True):
        """Update pad history and velocity. If fresh=False, then rejects the observation.

        Return odometry when accepted, or None during rejection or reacquisition.
        """
        stamp = Time.from_msg(odometry.header.stamp)
        age = (now.nanoseconds - stamp.nanoseconds) * 1e-9
        if not fresh or stamp.nanoseconds == 0 or not 0 <= age <= self.max_observation_age_s:
            self.reject_observation()
            return None
        if self._last_input_stamp is not None and stamp <= self._last_input_stamp:
            return None
        if not odometry.header.frame_id or not odometry.child_frame_id:
            raise ValueError('Pad odometry needs header and child frames')
        if (self._last_observation is not None
                and odometry.header.frame_id != self._last_observation.header.frame_id):
            raise ValueError('Reset pad history before changing its map frame')
        position = vector3_to_numpy(odometry.pose.pose.position)
        orientation = rotation(odometry.pose.pose.orientation)
        covariance = np.asarray(odometry.pose.covariance).reshape(6, 6)
        if (not np.isfinite(np.concatenate((position, covariance.ravel()))).all()
                or np.any(np.diag(covariance) < 0)):
            raise ValueError('Invalid pad position or pose covariance')

        if self.prediction_active:
            if self.update_gap(now) >= self.PREDICTION_START_AFTER_S:
                self._reacquire_since = None
            if self._reacquire_since is None:
                self._reacquire_since = stamp
                self._previous_position = self._previous_stamp = None
                self._filtered_velocity = np.zeros(3)
                self.velocity_ready = False
                self._position_history.clear()

        self._estimate_velocity(position, stamp)
        t = stamp.nanoseconds * 1e-9
        self._position_history.append((t, position.copy()))
        self._trim_history(self._position_history, t)
        self._last_input_stamp = stamp
        self._last_input_received_at = now
        if self.prediction_active:
            dwell = (stamp - self._reacquire_since).nanoseconds * 1e-9
            if dwell < self.REACQUIRE_DWELL_S:
                return None
            self.stop_prediction()

        output = deepcopy(odometry)
        output.twist.twist.linear = numpy_to_vector3(orientation.T @ self._filtered_velocity)
        output.twist.covariance = np.diag([self.VELOCITY_VARIANCE] * 3 + [0.0] * 3).ravel().tolist()
        self._last_observation = deepcopy(output)
        self.last_observation_stamp = stamp
        return output

    # TODO: Integrate later with the FSM using the align flag
    def add_drone_odometry(self, odometry: Odometry):
        """Record an optional fallback, the caller must establish matching XY motion."""
        stamp = Time.from_msg(odometry.header.stamp)
        velocity = rotation(odometry.pose.pose.orientation) @ vector3_to_numpy(
            odometry.twist.twist.linear)
        if stamp.nanoseconds == 0 or not np.isfinite(velocity).all():
            return
        t = stamp.nanoseconds * 1e-9
        if self._drone_velocity_history and t <= self._drone_velocity_history[-1][0]:
            return
        self._drone_velocity_history.append((t, velocity))
        self._trim_history(self._drone_velocity_history, t)

    def predict(self, now: Time, *, enabled=False):
        """Predict XY, hold Z and grow uncertainty when enabled by the landing phase.

        Use observation_age() and prediction_active for validity; forecast timestamps
        are not new detections.
        """
        if not enabled:
            self.stop_prediction()
            return None
        age = self.observation_age(now)
        if age < 0 or age > self.max_prediction_s:
            self.stop_prediction()
            return None
        if self._last_observation is None:
            return None
        if not self.prediction_active:
            # Processing delay must not trigger dropout prediction.
            if self.update_gap(now) < self.PREDICTION_START_AFTER_S:
                return None
            if not self.velocity_ready:
                return None
            self._frozen_velocity = self._capture_dropout_velocity()
            self._frozen_velocity[2] = 0.0
            self.prediction_active = True

        output = deepcopy(self._last_observation)
        position = vector3_to_numpy(output.pose.pose.position) + self._frozen_velocity * age
        output.pose.pose.position.x = float(position[0])
        output.pose.pose.position.y = float(position[1])
        output.pose.pose.position.z = float(position[2])
        orientation = rotation(output.pose.pose.orientation)
        output.twist.twist.linear = numpy_to_vector3(orientation.T @ self._frozen_velocity)
        output.twist.twist.angular = numpy_to_vector3(np.zeros(3))
        pose_covariance = np.asarray(output.pose.covariance).reshape(6, 6).copy()
        twist_covariance = np.asarray(output.twist.covariance).reshape(6, 6).copy()
        pose_covariance[:3, :3] += np.eye(3) * self.PREDICTION_POSITION_VARIANCE_RATE * age
        twist_covariance[:3, :3] += np.eye(3) * self.PREDICTION_VELOCITY_VARIANCE_RATE * age
        output.pose.covariance = pose_covariance.ravel().tolist()
        output.twist.covariance = twist_covariance.ravel().tolist()
        output.header.stamp = now.to_msg()
        return output

    def _estimate_velocity(self, position, stamp):
        """Reuse filtered position differences without refreshing duplicate stamps."""
        if self._previous_stamp is None:
            self._previous_position, self._previous_stamp = position.copy(), stamp
            return
        dt = (stamp - self._previous_stamp).nanoseconds * 1e-9
        if dt < self.MIN_VELOCITY_DT_S:
            return
        if dt > self.MAX_VELOCITY_GAP_S:
            self._filtered_velocity = np.zeros(3)
            self.velocity_ready = False
        else:
            raw_velocity = (position - self._previous_position) / dt
            tau = self.VELOCITY_FILTER_TAU_S
            alpha = 1.0 if tau <= 0 else dt / (tau + dt)
            self._filtered_velocity += alpha * (raw_velocity - self._filtered_velocity)
            self.velocity_ready = True
        self._previous_position, self._previous_stamp = position.copy(), stamp

    def _trim_history(self, history, latest_time):
        while history and latest_time - history[0][0] > self.HISTORY_WINDOW_S:
            history.popleft()

    def _fit_velocity_from_history(self):
        """Reuse the original least-squares fit over a recent position window."""
        if len(self._position_history) < self.HISTORY_MIN_SAMPLES:
            return None
        times = np.array([t for t, _ in self._position_history])
        if times[-1] - times[0] < self.HISTORY_MIN_SPAN_S:
            return None
        positions = np.stack([p for _, p in self._position_history])
        times -= times.mean()
        denominator = float(times @ times)
        if denominator < 1e-9:
            return None
        return (times[:, None] * (positions - positions.mean(axis=0))).sum(axis=0) / denominator

    def _capture_dropout_velocity(self):
        """Use position regression, an opted-in drone snapshot, or filtered velocity."""
        velocity = self._fit_velocity_from_history()
        if velocity is not None:
            self.prediction_velocity_source = 'visual_regression'
            return velocity

        if self.allow_drone_velocity_fallback and self._drone_velocity_history:
            reference_t = self.last_observation_stamp.nanoseconds * 1e-9
            velocities = [v for t, v in self._drone_velocity_history
                          if reference_t - self.HISTORY_WINDOW_S <= t <= reference_t]
            if velocities:
                self.prediction_velocity_source = 'drone_odom_fallback'
                return np.median(velocities, axis=0)
        self.prediction_velocity_source = 'filtered_pad_velocity'
        return self._filtered_velocity.copy()
