"""Turn landing references into controller and override velocity commands."""

from typing import Any, Mapping, Optional

from dji_msgs.msg import LandingControllerDebug, LandingReference, LandingRelativeState
from geometry_msgs.msg import TwistStamped
from rclpy.duration import Duration
from rclpy.impl.rcutils_logger import RcutilsLogger
from rclpy.time import Time
from tf2_ros import Buffer, TransformException

from .landing_control import ControlParameters, LandingControl
from .math_utils import numpy_to_vector3, transform_vector, vector3_to_numpy


class LandingCommand:
    """Run control and select output without creating ROS interfaces or timers.

    The manager supplies its current state, reference and parameter values.
    Control updates and output selection remain separate so each can run at
    its existing rate. The controller cache and watchdog history live here.
    """

    def __init__(
        self, control: LandingControl, controller_frame: str,
        buffer: Buffer, logger: RcutilsLogger,
    ) -> None:
        self._control = control
        self._controller_frame = controller_frame
        self._buffer = buffer
        self._logger = logger
        self._latest_command: Optional[TwistStamped] = None
        self._was_active = False
        self._was_enabled = False
        self._flush_remaining = 0

    def reset(self) -> None:
        """Clear controller history while preserving any remaining zero flush."""
        self._control.reset()
        self._latest_command = None
        self._was_active = False

    def update_control(
        self, now: Time, state: Optional[LandingRelativeState],
        reference: Optional[LandingReference], parameters: Mapping[str, Any],
    ) -> Optional[LandingControllerDebug]:
        """Cache a new controller command and return its debug message, if active."""
        active, detail = self._active_and_fresh(now, state, reference, parameters)
        if not active:
            if self._was_active:
                self._logger.info(f"LQR controller inactive: {detail}")
            self._was_active = False
            if bool(parameters["start_filter_from_zero"]):
                self._control.reset()
            return None

        assert state is not None
        assert reference is not None
        try:
            transform = self._lookup_transform(
                self._controller_frame, state.header.frame_id, Time(),
                float(parameters["tf_timeout_s"]),
                bool(parameters["tf_fallback_to_latest"]),
            )
        except TransformException as error:
            self._logger.warning(f"Controller TF unavailable: {error}")
            return None

        relative_position = vector3_to_numpy(state.relative_position)
        relative_velocity = vector3_to_numpy(state.relative_velocity)
        pad_velocity = vector3_to_numpy(state.pad_velocity)
        if transform is not None:
            relative_position = transform_vector(relative_position, transform)
            relative_velocity = transform_vector(relative_velocity, transform)
            pad_velocity = transform_vector(pad_velocity, transform)

        final_descent = reference.state_name == "FINAL_DESCENT"
        tuning = ControlParameters(
            z_kp=float(parameters["z_kp"]),
            z_kd=float(parameters["z_kd"]),
            max_xy_speed_mps=float(parameters[
                "max_xy_speed_final_mps" if final_descent else "max_xy_speed_mps"
            ]),
            max_up_speed_mps=float(parameters["max_up_speed_mps"]),
            max_down_speed_mps=float(parameters[
                "max_down_speed_final_mps" if final_descent else "max_down_speed_mps"
            ]),
            command_cutoff_hz=float(parameters["command_cutoff_hz"]),
            max_command_rate_mps2=parameters["max_command_rate_mps2"],
        )
        result = self._control.compute(
            relative_position,
            relative_velocity,
            pad_velocity,
            height_above_pad=float(reference.height_above_pad),
            vertical_reference_velocity=float(reference.vertical_reference_velocity),
            parameters=tuning,
        )
        self._was_active = True

        command_message = self._zero_message(now)
        command_message.twist.linear = numpy_to_vector3(result.command_filtered)
        command_message.twist.angular.z = 0.0
        self._latest_command = command_message

        debug = LandingControllerDebug()
        debug.header = command_message.header
        debug.lqr_state_xy = [float(value) for value in result.lqr_state_xy]
        debug.pad_velocity_controller_frame = numpy_to_vector3(pad_velocity)
        debug.command_feedforward = numpy_to_vector3(result.command_feedforward)
        debug.command_feedback = numpy_to_vector3(result.command_feedback)
        debug.command_raw = numpy_to_vector3(result.command_raw)
        debug.command_filtered = numpy_to_vector3(result.command_filtered)
        debug.saturated = result.saturated
        debug.rate_limited = result.rate_limited
        debug.detail = detail
        return debug

    def select_output(
        self, now: Time, reference: Optional[LandingReference], *,
        controller_timeout_s: float, reference_timeout_s: float, zero_flush_cycles: int,
    ) -> Optional[TwistStamped]:
        """Choose an override, fresh controller command or zero; None means no output."""
        if reference is None:
            self._logger.info(
                "Landing output inactive: no landing reference",
                throttle_duration_sec=2.0,
            )
            return self._handle_disabled(now, zero_flush_cycles)

        reference_age = self._age(now, reference.header.stamp)
        if reference_age > reference_timeout_s:
            self._logger.warning(
                "Landing output inactive: landing reference stale "
                f"({reference_age:.3f}s > {reference_timeout_s:.3f}s)",
                throttle_duration_sec=2.0,
            )
            return self._handle_disabled(now, zero_flush_cycles)

        if not reference.control_enabled:
            self._logger.info(
                "Landing output inactive: control disabled by landing manager",
                throttle_duration_sec=2.0,
            )
            return self._handle_disabled(now, zero_flush_cycles)

        if reference.override_active:
            output = self._zero_message(now)
            output.twist.linear.x = float(reference.override_velocity.x)
            output.twist.linear.y = float(reference.override_velocity.y)
            output.twist.linear.z = float(reference.override_velocity.z)
            self._was_enabled = True
            self._flush_remaining = zero_flush_cycles
            return output

        if self._latest_command is None:
            self._logger.warning(
                "Landing output enabled but no controller command has been received",
                throttle_duration_sec=2.0,
            )
            return self._zero_message(now)

        controller_age = self._age(now, self._latest_command.header.stamp)
        if controller_age > controller_timeout_s:
            self._logger.warning(
                "Landing output enabled but controller command stale "
                f"({controller_age:.3f}s > {controller_timeout_s:.3f}s)",
                throttle_duration_sec=2.0,
            )
            self._was_enabled = True
            self._flush_remaining = zero_flush_cycles
            return self._zero_message(now)

        output = self._zero_message(now, self._latest_command.header.frame_id)
        output.twist.linear.x = float(self._latest_command.twist.linear.x)
        output.twist.linear.y = float(self._latest_command.twist.linear.y)
        output.twist.linear.z = float(self._latest_command.twist.linear.z)
        output.twist.angular.x = float(self._latest_command.twist.angular.x)
        output.twist.angular.y = float(self._latest_command.twist.angular.y)
        output.twist.angular.z = float(self._latest_command.twist.angular.z)
        self._was_enabled = True
        self._flush_remaining = zero_flush_cycles
        return output

    def _lookup_transform(
        self, target: str, source: str, stamp: Time,
        timeout_s: float, fallback_to_latest: bool,
    ):
        if target == source:
            return None
        try:
            return self._buffer.lookup_transform(
                target,
                source,
                stamp,
                timeout=Duration(seconds=timeout_s),
            )
        except TransformException:
            if not fallback_to_latest:
                raise
            return self._buffer.lookup_transform(
                target,
                source,
                Time(),
                timeout=Duration(seconds=timeout_s),
            )

    @staticmethod
    def _active_and_fresh(
        now: Time, state: Optional[LandingRelativeState],
        reference: Optional[LandingReference], parameters: Mapping[str, Any],
    ) -> tuple[bool, str]:
        if state is None:
            return False, "no relative state"
        if reference is None:
            return False, "no landing reference"
        if not reference.control_enabled:
            return False, "control disabled"
        if reference.override_active:
            return False, "manager override active"
        if not state.valid:
            return False, f"invalid state: {state.invalid_reason}"
        state_age = LandingCommand._age(now, state.header.stamp)
        reference_age = LandingCommand._age(now, reference.header.stamp)
        if state_age > float(parameters["max_state_age_s"]):
            return False, f"state stale ({state_age:.3f}s)"
        if reference_age > float(parameters["max_reference_age_s"]):
            return False, f"reference stale ({reference_age:.3f}s)"
        return True, "active"

    @staticmethod
    def _age(now: Time, stamp) -> float:
        return max(0.0, (now - Time.from_msg(stamp)).nanoseconds * 1e-09)

    def _zero_message(self, now: Time, frame_id: Optional[str] = None) -> TwistStamped:
        message = TwistStamped()
        message.header.stamp = now.to_msg()
        message.header.frame_id = frame_id if frame_id else self._controller_frame
        return message

    def _handle_disabled(self, now: Time, zero_flush_cycles: int) -> Optional[TwistStamped]:
        if self._was_enabled:
            self._was_enabled = False
            self._flush_remaining = zero_flush_cycles
        if self._flush_remaining <= 0:
            return None

        self._flush_remaining -= 1
        return self._zero_message(now)
