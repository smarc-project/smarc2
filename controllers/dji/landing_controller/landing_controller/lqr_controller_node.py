from typing import Optional

import numpy as np
import rclpy
from dji_msgs.msg import (
    LandingControllerDebug,
    LandingReference,
    LandingRelativeState,
    Links as DJILinks,
    Topics as DJITopics,
)
from geometry_msgs.msg import TwistStamped
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from scipy.linalg import solve_discrete_are
from tf2_ros import Buffer, TransformException, TransformListener

from .math_utils import (
    clamp,
    first_order_lowpass,
    numpy_to_vector3,
    slew_limit,
    transform_vector,
    vector3_to_numpy,
)
from .model_loader import DiscreteVelocityModel, load_velocity_model


class LqrControllerNode(Node):
    def __init__(self, **node_kwargs) -> None:
        super().__init__("landing_lqr_controller", **node_kwargs)

        self.declare_parameter("robot_name", "M350")
        robot_name = str(self.get_parameter("robot_name").value)
        self.declare_parameter("model_path", "")
        self.declare_parameter("model_kind", "auto")
        self.declare_parameter("model_sample_time_s", 0.0)
        self.declare_parameter("relative_state_topic", DJITopics.RELATIVE_STATE_TOPIC)
        self.declare_parameter("reference_topic", DJITopics.REFERENCE_TOPIC)
        self.declare_parameter("controller_command_topic", DJITopics.CONTROLLER_CMD_TOPIC)
        self.declare_parameter("debug_topic", DJITopics.CONTROLLER_DEBUG_TOPIC)
        self.declare_parameter("controller_frame", f"{robot_name}/{DJILinks.BASE_FLAT}")
        self.declare_parameter("tf_timeout_s", 0.04)
        self.declare_parameter("tf_fallback_to_latest", True)
        self.declare_parameter("max_state_age_s", 0.20)
        self.declare_parameter("max_reference_age_s", 0.20)

        self.declare_parameter("q_diagonal_xy", [12.0, 12.0, 4.0, 4.0])
        self.declare_parameter("r_diagonal_xy", [1.0, 1.0])
        self.declare_parameter("z_kp", 0.75)
        self.declare_parameter("z_kd", 0.30)

        self.declare_parameter("max_xy_speed_mps", 1.0)
        self.declare_parameter("max_xy_speed_final_mps", 0.35)
        self.declare_parameter("max_up_speed_mps", 0.45)
        self.declare_parameter("max_down_speed_mps", 0.25)
        self.declare_parameter("max_down_speed_final_mps", 0.10)
        self.declare_parameter("command_cutoff_hz", 0.8)
        self.declare_parameter("max_command_rate_mps2", [0.8, 0.8, 0.5])
        self.declare_parameter("start_filter_from_zero", True)

        model_path = str(self.get_parameter("model_path").value)
        if not model_path:
            raise ValueError("model_path parameter is required")
        sample_time = float(self.get_parameter("model_sample_time_s").value)
        self._model: DiscreteVelocityModel = load_velocity_model(
            model_path,
            model_kind=str(self.get_parameter("model_kind").value),
            sample_time=sample_time if sample_time > 0.0 else None,
        )
        self.get_logger().info(
            f"Loaded M350 model from {self._model.source}; "
            f"dt={self._model.dt:.4f}s, gains={self._model.dc_gain_vector}"
        )

        a_xy, b_xy = self._model.xy_position_velocity_matrices()
        q_values = np.asarray(self.get_parameter("q_diagonal_xy").value, dtype=float)
        r_values = np.asarray(self.get_parameter("r_diagonal_xy").value, dtype=float)
        if q_values.shape != (4,) or r_values.shape != (2,):
            raise ValueError("q_diagonal_xy must have 4 values and r_diagonal_xy 2 values")
        q = np.diag(q_values)
        r = np.diag(r_values)
        p = solve_discrete_are(a_xy, b_xy, q, r)
        self._gain = np.linalg.solve(r + b_xy.T @ p @ b_xy, b_xy.T @ p @ a_xy)
        self.get_logger().info(f"Discrete XY LQR gain:\n{self._gain}")

        self._controller_frame = str(self.get_parameter("controller_frame").value)
        self._buffer = Buffer()
        self._listener = TransformListener(self._buffer, self)
        self._latest_state: Optional[LandingRelativeState] = None
        self._latest_reference: Optional[LandingReference] = None
        self._last_command = np.zeros(3, dtype=float)
        self._was_active = False

        self.create_subscription(
            LandingRelativeState,
            str(self.get_parameter("relative_state_topic").value),
            self._state_callback,
            20,
        )
        self.create_subscription(
            LandingReference,
            str(self.get_parameter("reference_topic").value),
            self._reference_callback,
            20,
        )
        self._command_publisher = self.create_publisher(
            TwistStamped,
            str(self.get_parameter("controller_command_topic").value),
            20,
        )
        self._debug_publisher = self.create_publisher(
            LandingControllerDebug,
            str(self.get_parameter("debug_topic").value),
            20,
        )
        self.create_timer(self._model.dt, self._control_loop)

    def _state_callback(self, message: LandingRelativeState) -> None:
        self._latest_state = message

    def _reference_callback(self, message: LandingReference) -> None:
        self._latest_reference = message

    def _lookup_transform(self, target: str, source: str, stamp: Time):
        if target == source:
            return None
        timeout = float(self.get_parameter("tf_timeout_s").value)
        try:
            return self._buffer.lookup_transform(
                target,
                source,
                stamp,
                timeout=Duration(seconds=timeout),
            )
        except TransformException:
            if not bool(self.get_parameter("tf_fallback_to_latest").value):
                raise
            return self._buffer.lookup_transform(
                target,
                source,
                Time(),
                timeout=Duration(seconds=timeout),
            )

    def _active_and_fresh(self, now: Time) -> tuple[bool, str]:
        if self._latest_state is None:
            return False, "no relative state"
        if self._latest_reference is None:
            return False, "no landing reference"
        if not self._latest_reference.control_enabled:
            return False, "control disabled"
        if self._latest_reference.override_active:
            return False, "manager override active"
        if not self._latest_state.valid:
            return False, f"invalid state: {self._latest_state.invalid_reason}"
        state_age = max(
            0.0,
            (now - Time.from_msg(self._latest_state.header.stamp)).nanoseconds * 1e-9,
        )
        reference_age = max(
            0.0,
            (now - Time.from_msg(self._latest_reference.header.stamp)).nanoseconds * 1e-9,
        )
        if state_age > float(self.get_parameter("max_state_age_s").value):
            return False, f"state stale ({state_age:.3f}s)"
        if reference_age > float(self.get_parameter("max_reference_age_s").value):
            return False, f"reference stale ({reference_age:.3f}s)"
        return True, "active"

    def _control_loop(self) -> None:
        now = self.get_clock().now()
        active, detail = self._active_and_fresh(now)
        if not active:
            if self._was_active:
                self.get_logger().info(f"LQR controller inactive: {detail}")
            self._was_active = False
            if bool(self.get_parameter("start_filter_from_zero").value):
                self._last_command[:] = 0.0
            return

        assert self._latest_state is not None
        assert self._latest_reference is not None
        state = self._latest_state
        reference = self._latest_reference
        source_frame = state.header.frame_id
        try:
            transform = self._lookup_transform(
                self._controller_frame,
                source_frame,
                Time(),
            )
        except TransformException as error:
            self.get_logger().warning(f"Controller TF unavailable: {error}")
            return

        relative_position = vector3_to_numpy(state.relative_position)
        relative_velocity = vector3_to_numpy(state.relative_velocity)
        pad_velocity = vector3_to_numpy(state.pad_velocity)
        if transform is not None:
            relative_position = transform_vector(relative_position, transform)
            relative_velocity = transform_vector(relative_velocity, transform)
            pad_velocity = transform_vector(pad_velocity, transform)

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

        gains = self._model.dc_gain_vector
        feedforward = np.zeros(3, dtype=float)
        feedforward[:2] = pad_velocity[:2] / gains[:2]
        desired_drone_vertical_velocity = (
            pad_velocity[2] + float(reference.vertical_reference_velocity)
        )
        feedforward[2] = desired_drone_vertical_velocity / gains[2]

        z_position_error = relative_position[2] - float(reference.height_above_pad)
        z_velocity_error = (
            relative_velocity[2] - float(reference.vertical_reference_velocity)
        )
        feedback = np.array(
            [
                feedback_xy[0],
                feedback_xy[1],
                -float(self.get_parameter("z_kp").value) * z_position_error
                - float(self.get_parameter("z_kd").value) * z_velocity_error,
            ],
            dtype=float,
        )
        raw_command = feedforward + feedback

        final_descent = reference.state_name == "FINAL_DESCENT"
        max_xy = float(
            self.get_parameter(
                "max_xy_speed_final_mps" if final_descent else "max_xy_speed_mps"
            ).value
        )
        max_down = float(
            self.get_parameter(
                "max_down_speed_final_mps" if final_descent else "max_down_speed_mps"
            ).value
        )
        lower = np.array([-max_xy, -max_xy, -max_down], dtype=float)
        upper = np.array(
            [
                max_xy,
                max_xy,
                float(self.get_parameter("max_up_speed_mps").value),
            ],
            dtype=float,
        )
        saturated_command = clamp(raw_command, lower, upper)
        saturated = not np.allclose(raw_command, saturated_command, rtol=0.0, atol=1e-12)

        filtered = first_order_lowpass(
            self._last_command,
            saturated_command,
            float(self.get_parameter("command_cutoff_hz").value),
            self._model.dt,
        )
        rate_values = np.asarray(
            self.get_parameter("max_command_rate_mps2").value,
            dtype=float,
        )
        if rate_values.shape != (3,):
            raise ValueError("max_command_rate_mps2 must contain three values")
        filtered, rate_limited = slew_limit(
            self._last_command,
            filtered,
            rate_values,
            self._model.dt,
        )
        filtered = clamp(filtered, lower, upper)
        self._last_command = filtered
        self._was_active = True

        command_message = TwistStamped()
        command_message.header.stamp = now.to_msg()
        command_message.header.frame_id = self._controller_frame
        command_message.twist.linear = numpy_to_vector3(filtered)
        command_message.twist.angular.z = 0.0
        self._command_publisher.publish(command_message)

        debug = LandingControllerDebug()
        debug.header = command_message.header
        debug.lqr_state_xy = [float(value) for value in lqr_state]
        debug.pad_velocity_controller_frame = numpy_to_vector3(pad_velocity)
        debug.command_feedforward = numpy_to_vector3(feedforward)
        debug.command_feedback = numpy_to_vector3(feedback)
        debug.command_raw = numpy_to_vector3(raw_command)
        debug.command_filtered = numpy_to_vector3(filtered)
        debug.saturated = saturated
        debug.rate_limited = rate_limited
        debug.detail = detail
        self._debug_publisher.publish(debug)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = LqrControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        # ROS may already have shut the context down while handling SIGINT.
        if rclpy.ok():
            rclpy.shutdown()
