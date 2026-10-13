import copy
from collections import deque
from typing import Optional

import numpy as np
import rclpy
from dji_msgs.msg import (
    LandingStatus,
    ObjectEkfStatus,
    ObjectEkfStatusArray,
    ObjectPoseWithCovariance,
    ObjectPoseWithCovarianceArray,
    Topics as DJITopics,
)
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from smarc_msgs.msg import Topics as SmarcTopics

from .math_utils import point_to_numpy


class ObjectArrayToOdometryNode(Node):
    """Select one class from the ALARS multi-object EKF and publish Odometry.

    The EKF output contains pose and covariance but no twist, so velocity is
    estimated from successive poses.

    In FINAL_DESCENT, velocity is captured from recent history at visual
    dropout. The last observed pose is propagated with this frozen XY velocity
    while uncertainty grows. Sustained fresh EKF updates end prediction.
    """

    def __init__(self, **node_kwargs) -> None:
        super().__init__("object_array_to_odometry", **node_kwargs)

        # Input/output.
        self.declare_parameter("pose_array_topic", DJITopics.PROJECTED_OBJECT_POSES_ARRAY_TOPIC)
        self.declare_parameter("status_array_topic", DJITopics.OBJECT_EKF_STATUS_ARRAY_TOPIC)
        self.declare_parameter("landing_status_topic", DJITopics.STATUS_TOPIC)
        self.declare_parameter("output_topic", DJITopics.PAD_ODOM_TOPIC)
        self.declare_parameter("class_name", "landing_pad")
        self.declare_parameter("child_frame_id", "landing_pad")

        # EKF validity.
        self.declare_parameter("require_status", True)
        self.declare_parameter("max_status_message_age_s", 1.0)
        self.declare_parameter("max_time_since_update_s", 0.35)
        self.declare_parameter("max_time_since_measurement_s", 0.50)
        self.declare_parameter("max_covariance_trace", -1.0)
        self.declare_parameter("max_consecutive_outliers", 5)
        self.declare_parameter("max_consecutive_invalid_measurements", 5)

        # Normal velocity estimator.
        self.declare_parameter("velocity_filter_tau_s", 0.25)
        self.declare_parameter("min_dt_s", 0.01)
        self.declare_parameter("max_dt_s", 0.50)
        self.declare_parameter("velocity_variance", 0.10)

        # Timestamp handling.
        self.declare_parameter("replace_zero_stamp_with_now", True)
        self.declare_parameter("use_array_header_if_object_header_empty", True)

        # Dropout prediction.
        self.declare_parameter("enable_dropout_prediction", False)
        self.declare_parameter("prediction_only_in_final_descent", True)
        self.declare_parameter("prediction_start_after_s", 0.30)
        self.declare_parameter("max_prediction_s", 12.0)
        self.declare_parameter("prediction_publish_rate_hz", 20.0)
        self.declare_parameter("prediction_position_variance_rate", 0.01)
        self.declare_parameter("prediction_velocity_variance_rate", 0.01)

        # Velocity regression used for prediction.
        self.declare_parameter("prediction_velocity_window_s", 1.5)
        self.declare_parameter("prediction_velocity_min_samples", 4)
        self.declare_parameter("prediction_velocity_hold_s", 5.0)
        self.declare_parameter("prediction_velocity_min_xy_speed_mps", 0.03)

        # Terminal velocity snapshot.
        self.declare_parameter("terminal_velocity_history_s", 6.0)
        self.declare_parameter("terminal_velocity_min_samples", 8)

        self.declare_parameter("drone_odom_topic", SmarcTopics.ODOM_TOPIC)
        self.declare_parameter("terminal_drone_velocity_history_s", 2.0)

        self.declare_parameter("dropout_velocity_capture_window_s", 0.75)

        self.declare_parameter("fresh_ekf_update_max_age_s", 0.10)
        self.declare_parameter("reacquire_dwell_s", 0.30)
        self.declare_parameter("terminal_velocity_min_span_s", 0.25)

        self.declare_parameter("terminal_velocity_collapse_ratio", 0.55)
        self.declare_parameter("terminal_velocity_memory_s", 2.0)
        self.declare_parameter("terminal_velocity_direction_min_speed_mps", 0.15)

        self._reacquire_since: Optional[Time] = None

        self._last_good_terminal_velocity: Optional[np.ndarray] = None
        self._last_good_terminal_velocity_stamp: Optional[Time] = None

        self._latest_status: Optional[ObjectEkfStatus] = None
        self._status_received_at: Optional[Time] = None

        self._previous_position: Optional[np.ndarray] = None
        self._previous_stamp: Optional[Time] = None
        self._filtered_velocity = np.zeros(3, dtype=float)
        self._raw_pad_velocity_history = deque()
        self._latest_raw_pad_velocity = np.zeros(3, dtype=float)
        self._latest_raw_pad_velocity_stamp: Optional[Time] = None

        self._last_valid_odom: Optional[Odometry] = None
        self._last_valid_received_at: Optional[Time] = None
        self._last_reliable_pad_velocity = np.zeros(3, dtype=float)
        self._last_reliable_pad_velocity_stamp: Optional[Time] = None

        self._prediction_position_history = deque()
        self._prediction_velocity = np.zeros(3, dtype=float)

        self._last_reliable_prediction_velocity = np.zeros(3, dtype=float)
        self._last_reliable_prediction_velocity_stamp: Optional[Time] = None

        self._drone_velocity_history = deque()
        self._landing_state_name = ""
        self._terminal_prediction_velocity: Optional[np.ndarray] = None
        self._terminal_prediction_velocity_source = ""
        self._prediction_active = False

        self._publisher = self.create_publisher(
            Odometry,
            str(self.get_parameter("output_topic").value),
            20,
        )

        self.create_subscription(
            ObjectPoseWithCovarianceArray,
            str(self.get_parameter("pose_array_topic").value),
            self._pose_array_callback,
            qos_profile_sensor_data,
        )

        self.create_subscription(
            ObjectEkfStatusArray,
            str(self.get_parameter("status_array_topic").value),
            self._status_array_callback,
            qos_profile_sensor_data,
        )

        self.create_subscription(
            LandingStatus,
            str(self.get_parameter("landing_status_topic").value),
            self._landing_status_callback,
            20,
        )

        self.create_subscription(
            Odometry,
            str(self.get_parameter("drone_odom_topic").value),
            self._drone_odom_callback,
            20,
        )

        prediction_rate = float(self.get_parameter("prediction_publish_rate_hz").value)
        if prediction_rate <= 0.0:
            raise ValueError("prediction_publish_rate_hz must be positive")

        self._prediction_timer = self.create_timer(
            1.0 / prediction_rate,
            self._prediction_timer_callback,
        )

        self.get_logger().info(
            "Selecting class '%s' from %s"
            % (
                str(self.get_parameter("class_name").value),
                str(self.get_parameter("pose_array_topic").value),
            )
        )

    def _select_by_class(self, values):
        target = str(self.get_parameter("class_name").value)

        if not target and values:
            return values[0]

        for value in values:
            if str(value.class_name) == target:
                return value

        return None

    def _guard_terminal_velocity(self, velocity: np.ndarray, source: str) -> np.ndarray:
        """Reject sudden speed collapses using the recent terminal velocity."""
        now = self.get_clock().now()
        speed = float(np.linalg.norm(velocity[:2]))
        min_speed = float(self.get_parameter("prediction_velocity_min_xy_speed_mps").value)

        if (
            self._last_good_terminal_velocity is not None
            and self._last_good_terminal_velocity_stamp is not None
        ):
            age = (now - self._last_good_terminal_velocity_stamp).nanoseconds * 1e-9
            memory_s = float(self.get_parameter("terminal_velocity_memory_s").value)
            baseline_speed = float(np.linalg.norm(self._last_good_terminal_velocity[:2]))
            collapse_ratio = float(self.get_parameter("terminal_velocity_collapse_ratio").value)

            if (
                0.0 <= age <= memory_s
                and baseline_speed >= min_speed
                and speed < collapse_ratio * baseline_speed
            ):
                direction_min_speed = float(
                    self.get_parameter("terminal_velocity_direction_min_speed_mps").value,
                )

                if speed >= direction_min_speed:
                    corrected = velocity.copy()
                    corrected[:2] *= baseline_speed / speed
                    self._terminal_prediction_velocity_source = f"{source}_speed_guard"
                    self.get_logger().warn(
                        f"Terminal velocity collapse rejected: {speed:.3f} -> "
                        f"using {baseline_speed:.3f} m/s magnitude.",
                    )
                    return corrected

                self._terminal_prediction_velocity_source = "held_terminal_velocity"
                self.get_logger().warn(
                    f"Terminal velocity collapse rejected: {speed:.3f} -> holding previous "
                    f"v=[{self._last_good_terminal_velocity[0]:.3f}, "
                    f"{self._last_good_terminal_velocity[1]:.3f}] m/s.",
                )
                return self._last_good_terminal_velocity.copy()

        self._last_good_terminal_velocity = velocity.copy()
        self._last_good_terminal_velocity_stamp = now
        self._terminal_prediction_velocity_source = source
        return velocity

    def _drone_odom_callback(self, message: Odometry) -> None:
        now = self.get_clock().now()
        t = now.nanoseconds * 1e-9

        velocity = np.array(
            [
                message.twist.twist.linear.x,
                message.twist.twist.linear.y,
                message.twist.twist.linear.z,
            ],
            dtype=float,
        )

        self._drone_velocity_history.append((t, velocity))

        history_s = float(self.get_parameter("terminal_drone_velocity_history_s").value)
        while self._drone_velocity_history and t - self._drone_velocity_history[0][0] > history_s:
            self._drone_velocity_history.popleft()

    def _status_array_callback(self, message: ObjectEkfStatusArray) -> None:
        status = self._select_by_class(message.statuses)

        if status is None:
            return

        self._latest_status = status
        self._status_received_at = self.get_clock().now()

    def _landing_status_callback(self, message: LandingStatus) -> None:
        new_state = str(message.state_name)
        old_state = self._landing_state_name

        if new_state == "FINAL_DESCENT" and old_state != "FINAL_DESCENT":
            self._prediction_active = False
            self._terminal_prediction_velocity = None
            self._terminal_prediction_velocity_source = ""
            self._last_good_terminal_velocity = None
            self._last_good_terminal_velocity_stamp = None
            self._reacquire_since = None
            self.get_logger().info(
                "FINAL_DESCENT entered; terminal velocity will be captured at visual dropout.",
            )

        elif old_state == "FINAL_DESCENT" and new_state != "FINAL_DESCENT":
            if self._prediction_active:
                self.get_logger().info(
                    f"Leaving FINAL_DESCENT for {new_state}; stopping dropout prediction.",
                )
            self._prediction_active = False
            self._terminal_prediction_velocity = None
            self._terminal_prediction_velocity_source = ""
            self._last_good_terminal_velocity = None
            self._last_good_terminal_velocity_stamp = None
            self._reacquire_since = None

        self._landing_state_name = new_state

    def _capture_dropout_velocity(self) -> Optional[np.ndarray]:
        """Prefer recent visual pad motion; use drone odometry as a fallback."""
        history_s = float(self.get_parameter("terminal_velocity_history_s").value)
        min_samples = int(self.get_parameter("terminal_velocity_min_samples").value)
        min_span_s = float(self.get_parameter("terminal_velocity_min_span_s").value)
        min_xy_speed = float(self.get_parameter("prediction_velocity_min_xy_speed_mps").value)
        hold_s = float(self.get_parameter("prediction_velocity_hold_s").value)
        now = self.get_clock().now()

        visual_velocity = self._fit_velocity_from_history(history_s, min_samples, min_span_s)
        if visual_velocity is not None and np.linalg.norm(visual_velocity[:2]) >= min_xy_speed:
            return self._guard_terminal_velocity(visual_velocity, "visual_regression")

        if self._raw_pad_velocity_history:
            raw_velocity = np.median(
                np.stack([velocity for (_, velocity) in self._raw_pad_velocity_history]),
                axis=0,
            )
            if np.linalg.norm(raw_velocity[:2]) >= min_xy_speed:
                return self._guard_terminal_velocity(raw_velocity, "raw_pad_velocity_median")

        if self._last_reliable_prediction_velocity_stamp is not None:
            reliable_age = (now - self._last_reliable_prediction_velocity_stamp).nanoseconds * 1e-9
            if (
                0.0 <= reliable_age <= hold_s
                and np.linalg.norm(self._last_reliable_prediction_velocity[:2]) >= min_xy_speed
            ):
                return self._guard_terminal_velocity(
                    self._last_reliable_prediction_velocity.copy(),
                    f"held_visual_regression_{reliable_age:.2f}s",
                )

        if self._last_reliable_pad_velocity_stamp is not None:
            reliable_age = (now - self._last_reliable_pad_velocity_stamp).nanoseconds * 1e-9
            if (
                0.0 <= reliable_age <= hold_s
                and np.linalg.norm(self._last_reliable_pad_velocity[:2]) >= min_xy_speed
            ):
                return self._guard_terminal_velocity(
                    self._last_reliable_pad_velocity.copy(),
                    f"held_pad_odom_{reliable_age:.2f}s",
                )

        if self._latest_raw_pad_velocity_stamp is not None:
            raw_age = (now - self._latest_raw_pad_velocity_stamp).nanoseconds * 1e-9
            if (
                0.0 <= raw_age <= hold_s
                and np.linalg.norm(self._latest_raw_pad_velocity[:2]) >= min_xy_speed
            ):
                return self._guard_terminal_velocity(
                    self._latest_raw_pad_velocity.copy(),
                    f"latest_raw_pad_velocity_{raw_age:.2f}s",
                )

        if not self._drone_velocity_history:
            return None

        window_s = float(self.get_parameter("dropout_velocity_capture_window_s").value)
        reference_t = (
            self._last_valid_received_at.nanoseconds * 1e-09
            if self._last_valid_received_at is not None
            else now.nanoseconds * 1e-09
        )
        velocities = [
            velocity
            for (t, velocity) in self._drone_velocity_history
            if reference_t - window_s <= t <= reference_t
        ]

        if not velocities:
            return None

        velocity = np.median(np.stack(velocities), axis=0)
        velocity[2] = 0.0
        return self._guard_terminal_velocity(velocity, "drone_odom_fallback")

    def _status_is_valid(self) -> tuple[bool, str]:
        if not bool(self.get_parameter("require_status").value):
            return True, ""

        if self._latest_status is None or self._status_received_at is None:
            return False, "no EKF status"

        now = self.get_clock().now()
        message_age = (now - self._status_received_at).nanoseconds * 1e-9

        if message_age > float(self.get_parameter("max_status_message_age_s").value):
            return False, f"status stale ({message_age:.2f}s)"

        status = self._latest_status

        if not bool(status.initialized):
            return False, "EKF not initialized"

        if float(status.time_since_last_update) > float(
            self.get_parameter("max_time_since_update_s").value
        ):
            return False, "EKF update stale"

        if float(status.time_since_last_processed_measurement) > float(
            self.get_parameter("max_time_since_measurement_s").value
        ):
            return False, "measurement stale"

        max_covariance = float(self.get_parameter("max_covariance_trace").value)

        if max_covariance >= 0.0 and float(status.covariance_trace) > max_covariance:
            return False, "EKF covariance too high"

        if int(status.consecutive_outliers) > int(
            self.get_parameter("max_consecutive_outliers").value
        ):
            return False, "too many EKF outliers"

        if int(status.consecutive_invalid_measurements) > int(
            self.get_parameter("max_consecutive_invalid_measurements").value
        ):
            return False, "too many invalid measurements"

        return True, ""

    def _message_stamp(
        self,
        object_message: ObjectPoseWithCovariance,
        array_message: ObjectPoseWithCovarianceArray,
    ) -> Time:
        stamp = Time.from_msg(object_message.header.stamp)

        if (
            stamp.nanoseconds == 0
            and bool(self.get_parameter("use_array_header_if_object_header_empty").value)
        ):
            stamp = Time.from_msg(array_message.header.stamp)

        if stamp.nanoseconds == 0 and bool(self.get_parameter("replace_zero_stamp_with_now").value):
            stamp = self.get_clock().now()

        return stamp

    def _estimate_velocity(self, position: np.ndarray, stamp: Time) -> np.ndarray:
        if self._previous_position is None or self._previous_stamp is None:
            self._previous_position = position.copy()
            self._previous_stamp = stamp
            return self._filtered_velocity.copy()

        dt = (stamp - self._previous_stamp).nanoseconds * 1e-9

        min_dt = float(self.get_parameter("min_dt_s").value)
        max_dt = float(self.get_parameter("max_dt_s").value)

        if dt <= 0.0 or dt < min_dt:
            return self._filtered_velocity.copy()

        if dt > max_dt:
            self._previous_position = position.copy()
            self._previous_stamp = stamp
            self._filtered_velocity[:] = 0.0
            return self._filtered_velocity.copy()

        raw_velocity = (position - self._previous_position) / dt
        self._latest_raw_pad_velocity = raw_velocity.copy()
        self._latest_raw_pad_velocity_stamp = stamp
        raw_time = stamp.nanoseconds * 1e-9
        self._raw_pad_velocity_history.append((raw_time, raw_velocity.copy()))

        raw_history_s = float(self.get_parameter("dropout_velocity_capture_window_s").value)
        while (
            self._raw_pad_velocity_history
            and raw_time - self._raw_pad_velocity_history[0][0] > raw_history_s
        ):
            self._raw_pad_velocity_history.popleft()

        tau = float(self.get_parameter("velocity_filter_tau_s").value)
        alpha = 1.0 if tau <= 0.0 else dt / (tau + dt)

        self._filtered_velocity += (
            alpha * (raw_velocity - self._filtered_velocity)
        )

        self._previous_position = position.copy()
        self._previous_stamp = stamp

        return self._filtered_velocity.copy()

    def _has_fresh_ekf_update(self) -> bool:
        if self._latest_status is None:
            return False
        max_age = float(self.get_parameter("fresh_ekf_update_max_age_s").value)
        return float(self._latest_status.time_since_last_update) <= max_age

    def _pose_array_callback(self, message: ObjectPoseWithCovarianceArray) -> None:
        object_message = self._select_by_class(message.objects)
        if object_message is None:
            return

        valid, reason = self._status_is_valid()
        if not valid:
            self.get_logger().debug(f"Not publishing pad odometry: {reason}")
            return

        now = self.get_clock().now()

        # During FINAL_DESCENT, only accept genuinely fresh EKF updates.
        if self._landing_state_name == "FINAL_DESCENT":
            if not self._has_fresh_ekf_update():
                self._reacquire_since = None
                return

            # While predicting, do not immediately trust a single fresh EKF sample.
            # Require sustained fresh updates before allowing them back into the
            # pad velocity estimator/history.
            if self._prediction_active:
                if self._reacquire_since is None:
                    self._reacquire_since = now
                    return

                reacquire_elapsed = (now - self._reacquire_since).nanoseconds * 1e-9
                reacquire_dwell = float(self.get_parameter("reacquire_dwell_s").value)

                if reacquire_elapsed < reacquire_dwell:
                    return

                self.get_logger().info(
                    f"Landing-pad detection stably reacquired after {reacquire_elapsed:.2f}s; "
                    "stopping dropout prediction.",
                )
                self._prediction_active = False
                self._terminal_prediction_velocity = None
                self._terminal_prediction_velocity_source = ""
                self._reacquire_since = None
            else:
                self._reacquire_since = None

        stamp = self._message_stamp(object_message, message)
        position = point_to_numpy(object_message.pose.pose.position)

        velocity = self._estimate_velocity(position, stamp)
        self._update_prediction_velocity(position, stamp)

        output = Odometry()
        output.header = object_message.header

        if not output.header.frame_id:
            output.header.frame_id = message.header.frame_id

        output.header.stamp = stamp.to_msg()
        output.child_frame_id = str(self.get_parameter("child_frame_id").value)
        output.pose = object_message.pose

        output.twist.twist.linear.x = float(velocity[0])
        output.twist.twist.linear.y = float(velocity[1])
        output.twist.twist.linear.z = float(velocity[2])

        velocity_variance = float(self.get_parameter("velocity_variance").value)
        output.twist.covariance[0] = velocity_variance
        output.twist.covariance[7] = velocity_variance
        output.twist.covariance[14] = velocity_variance

        min_xy_speed = float(self.get_parameter("prediction_velocity_min_xy_speed_mps").value)
        if np.linalg.norm(velocity[:2]) >= min_xy_speed:
            self._last_reliable_pad_velocity = velocity.copy()
            self._last_reliable_pad_velocity_stamp = stamp

        pose_trace = output.pose.covariance[0] + output.pose.covariance[7] + output.pose.covariance[14]

        if abs(pose_trace) < 1e-12 and self._latest_status is not None:
            diagonal = max(0.0, float(self._latest_status.covariance_trace)) / 3.0
            output.pose.covariance[0] = diagonal
            output.pose.covariance[7] = diagonal
            output.pose.covariance[14] = diagonal

        self._last_valid_odom = copy.deepcopy(output)
        self._last_valid_received_at = now

        self._publisher.publish(output)

    def _update_prediction_velocity(self, position: np.ndarray, stamp: Time) -> None:
        t = stamp.nanoseconds * 1e-9

        if self._prediction_position_history:
            last_t = self._prediction_position_history[-1][0]
            min_dt = float(self.get_parameter("min_dt_s").value)

            if t <= last_t or t - last_t < min_dt:
                return

        self._prediction_position_history.append((t, position.copy()))

        prediction_window = float(self.get_parameter("prediction_velocity_window_s").value)

        terminal_window = float(self.get_parameter("terminal_velocity_history_s").value)

        history_to_keep = max(prediction_window, terminal_window)

        while (
            self._prediction_position_history
            and t - self._prediction_position_history[0][0]
            > history_to_keep
        ):
            self._prediction_position_history.popleft()

        min_samples = int(self.get_parameter("prediction_velocity_min_samples").value)

        candidate_velocity = self._fit_velocity_from_history(prediction_window, min_samples)

        if candidate_velocity is None:
            return

        self._prediction_velocity = candidate_velocity

        min_xy_speed = float(self.get_parameter("prediction_velocity_min_xy_speed_mps").value)

        if np.linalg.norm(candidate_velocity[:2]) >= min_xy_speed:
            self._last_reliable_prediction_velocity = candidate_velocity.copy()
            self._last_reliable_prediction_velocity_stamp = stamp

    def _fit_velocity_from_history(
        self,
        window_s: float,
        min_samples: int,
        min_span_s: float = 0.5,
    ) -> Optional[np.ndarray]:
        if not self._prediction_position_history:
            return None

        newest_t = self._prediction_position_history[-1][0]

        samples = [
            (t, position)
            for t, position in self._prediction_position_history
            if newest_t - t <= window_s
        ]

        if len(samples) < min_samples:
            return None

        times = np.array([sample[0] for sample in samples], dtype=float)

        positions = np.array([sample[1] for sample in samples], dtype=float)

        time_span = times[-1] - times[0]

        if time_span < min_span_s:
            return None

        times -= np.mean(times)

        denominator = float(np.dot(times, times))

        if denominator < 1e-09:
            return None

        centered_positions = positions - np.mean(positions, axis=0)

        velocity = (times[:, None] * centered_positions).sum(axis=0) / denominator

        return velocity

    def _prediction_timer_callback(self) -> None:
        if not bool(self.get_parameter("enable_dropout_prediction").value):
            return

        prediction_only_final = bool(self.get_parameter("prediction_only_in_final_descent").value)

        if prediction_only_final and self._landing_state_name != "FINAL_DESCENT":
            return

        if self._last_valid_odom is None or self._last_valid_received_at is None:
            return

        now = self.get_clock().now()
        dropout_age = (now - self._last_valid_received_at).nanoseconds * 1e-9

        start_after = float(self.get_parameter("prediction_start_after_s").value)
        max_prediction = float(self.get_parameter("max_prediction_s").value)

        if dropout_age < start_after:
            return

        if dropout_age > max_prediction:
            if self._prediction_active:
                self.get_logger().warn(
                    f"Landing-pad prediction timeout after {dropout_age:.2f}s; stopping predicted odometry.",
                )

            self._prediction_active = False
            self._terminal_prediction_velocity = None
            self._terminal_prediction_velocity_source = ""
            self._reacquire_since = None
            return

        source = self._last_valid_odom
        source_stamp = Time.from_msg(source.header.stamp)
        dt = (now - source_stamp).nanoseconds * 1e-9

        if dt < 0.0:
            return

        # Capture recent pad motion when dropout prediction begins. The capture
        # helper uses drone motion only if the visual histories are unusable.
        if (
            self._landing_state_name == "FINAL_DESCENT"
            and self._terminal_prediction_velocity is None
        ):
            captured_velocity = self._capture_dropout_velocity()

            if captured_velocity is not None:
                self._terminal_prediction_velocity = captured_velocity.copy()
                self.get_logger().warn(
                    f"Visual dropout: frozen terminal velocity "
                    f"v=[{captured_velocity[0]:.3f}, {captured_velocity[1]:.3f}, "
                    f"{captured_velocity[2]:.3f}] m/s, "
                    f"source={self._terminal_prediction_velocity_source}."
                )

        output = copy.deepcopy(source)

        # In FINAL_DESCENT, prefer the velocity captured at actual vision loss.
        if (
            self._landing_state_name == "FINAL_DESCENT"
            and self._terminal_prediction_velocity is not None
        ):
            prediction_velocity = self._terminal_prediction_velocity.copy()
            velocity_source = "dropout_snapshot"

        else:
            # Fallback to the visual-motion regression if no terminal snapshot
            # could be captured.
            prediction_velocity = self._prediction_velocity.copy()
            velocity_source = "current"

            min_xy_speed = float(self.get_parameter("prediction_velocity_min_xy_speed_mps").value)
            hold_s = float(self.get_parameter("prediction_velocity_hold_s").value)

            if (
                np.linalg.norm(prediction_velocity[:2]) < min_xy_speed
                and self._last_reliable_prediction_velocity_stamp is not None
            ):
                reliable_age = (
                    now - self._last_reliable_prediction_velocity_stamp
                ).nanoseconds * 1e-9

                if 0.0 <= reliable_age <= hold_s:
                    prediction_velocity[:2] = self._last_reliable_prediction_velocity[:2]
                    velocity_source = f"held ({reliable_age:.2f}s old)"

        # Do not extrapolate vertical pad motion during the blind terminal phase.
        prediction_velocity[2] = 0.0

        vx = float(prediction_velocity[0])
        vy = float(prediction_velocity[1])
        vz = float(prediction_velocity[2])

        # Propagate from the last real pad measurement, never recursively from
        # previous predictions.
        output.pose.pose.position.x += vx * dt
        output.pose.pose.position.y += vy * dt
        output.pose.pose.position.z += vz * dt

        # Keep predicted pad velocity consistent with predicted pad position.
        output.twist.twist.linear.x = vx
        output.twist.twist.linear.y = vy
        output.twist.twist.linear.z = vz

        output.header.stamp = now.to_msg()

        # Grow uncertainty as the blind interval increases.
        pose_var_rate = float(self.get_parameter("prediction_position_variance_rate").value)
        vel_var_rate = float(self.get_parameter("prediction_velocity_variance_rate").value)

        output.pose.covariance[0] += pose_var_rate * dropout_age
        output.pose.covariance[7] += pose_var_rate * dropout_age
        output.pose.covariance[14] += pose_var_rate * dropout_age

        output.twist.covariance[0] += vel_var_rate * dropout_age
        output.twist.covariance[7] += vel_var_rate * dropout_age
        output.twist.covariance[14] += vel_var_rate * dropout_age

        if not self._prediction_active:
            self._reacquire_since = None
            self.get_logger().warn(
                "Landing-pad detection lost; starting constant-velocity prediction "
                f"(dropout age {dropout_age:.2f}s, v=[{vx:.3f}, {vy:.3f}, {vz:.3f}] m/s, "
                f"source={velocity_source})."
            )
            self._prediction_active = True

        self._publisher.publish(output)

def main(args=None) -> None:
    rclpy.init(args=args)

    node = ObjectArrayToOdometryNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        # ROS may already have shut the context down while handling SIGINT.
        if rclpy.ok():
            rclpy.shutdown()
