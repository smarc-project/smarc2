from enum import IntEnum
from pathlib import Path
from typing import Optional

from ament_index_python.packages import get_package_share_directory
import numpy as np
import rclpy
from dji_msgs.msg import (
    LandingControllerDebug,
    LandingReference,
    LandingRelativeState,
    LandingStatus,
    Links as DJILinks,
    PsdkTopics,
    Topics as DJITopics,
)
from geometry_msgs.msg import TwistStamped, Vector3Stamped
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from std_srvs.srv import Trigger
from tf2_ros import Buffer, TransformException, TransformListener

from .landing_control import ControlParameters, LandingControl
from .math_utils import numpy_to_vector3, transform_vector, vector3_to_numpy
from .model_loader import DiscreteVelocityModel, load_velocity_model


class LandingState(IntEnum):
    """Published state IDs; keep values stable for ROS consumers and recorded bags."""

    IDLE = 0
    # State 1 was APPROACH. The current start service enters ACQUIRE directly.
    ACQUIRE = 2
    ALIGN = 3
    DESCEND = 4
    FINAL_DESCENT = 5
    TOUCHDOWN = 6
    LANDED = 7
    ABORT_CLIMB = 8
    ABORT_HOLD = 9


TRACKING_STATES = {LandingState.ALIGN, LandingState.DESCEND, LandingState.FINAL_DESCENT}


class LandingManagerNode(Node):
    """Manage landing phases, XY LQR/Z PD control and final velocity output.

    The FSM, model-based control and command output have separate timers.
    References and commands are shared directly; ROS publications expose them
    for monitoring. Abort and touchdown overrides take priority over control.
    """

    def __init__(self, **node_kwargs) -> None:
        super().__init__("landing_manager", **node_kwargs)

        self.declare_parameter("robot_name", "M350")
        self.declare_parameter("relative_state_topic", DJITopics.RELATIVE_STATE_TOPIC)
        self.declare_parameter("reference_topic", DJITopics.REFERENCE_TOPIC)
        self.declare_parameter("status_topic", DJITopics.STATUS_TOPIC)
        self.declare_parameter("start_service", DJITopics.LANDING_START_SERVICE)
        self.declare_parameter("abort_service", DJITopics.LANDING_ABORT_SERVICE)
        self.declare_parameter("reset_service", DJITopics.LANDING_RESET_SERVICE)
        self.declare_parameter("update_rate_hz", 20.0)
        self.declare_parameter("auto_start", False)
        self.declare_parameter("enable_descent", True)

        # Command output and watchdogs, previously owned by the velocity mux.
        self.declare_parameter("controller_command_topic", DJITopics.CONTROLLER_CMD_TOPIC)
        self.declare_parameter("output_topic", DJITopics.VELOCITY_SETPOINT_TOPIC)
        self.declare_parameter("mirror_vector_topic", "")
        self.declare_parameter("publish_rate_hz", 50.0)
        self.declare_parameter("controller_timeout_s", 0.15)
        self.declare_parameter("reference_timeout_s", 0.25)
        self.declare_parameter("zero_flush_cycles", 8)

        # Model and control tuning; the calculations remain in landing_control.py.
        self.declare_parameter("model_path", "")
        self.declare_parameter("model_kind", "auto")
        self.declare_parameter("model_sample_time_s", 0.0)
        self.declare_parameter("debug_topic", DJITopics.CONTROLLER_DEBUG_TOPIC)
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

        self.declare_parameter("acquire_duration_s", 1.0)
        self.declare_parameter("minimum_align_height_m", 2.0)
        self.declare_parameter("capture_current_height_on_align", True)
        self.declare_parameter("align_xy_tolerance_m", 0.40)
        self.declare_parameter("align_speed_tolerance_mps", 0.25)
        self.declare_parameter("align_dwell_s", 1.5)

        self.declare_parameter("descent_rate_mps", 0.20)
        self.declare_parameter("descent_pause_xy_m", 0.55)
        self.declare_parameter("descent_pause_speed_mps", 0.35)
        self.declare_parameter("final_descent_height_m", 0.50)
        self.declare_parameter("final_descent_entry_margin_m", 0.20)
        self.declare_parameter("final_descent_rate_mps", 0.08)

        self.declare_parameter("touchdown_height_m", 0.08)
        self.declare_parameter("touchdown_detection_height_m", 0.12)
        self.declare_parameter("touchdown_xy_tolerance_m", 0.25)
        self.declare_parameter("touchdown_vertical_speed_mps", 0.15)
        self.declare_parameter("touchdown_dwell_s", 0.6)
        self.declare_parameter("touchdown_hold_s", 1.0)

        self.declare_parameter("estimate_loss_abort_s", 1.0)
        self.declare_parameter("abort_xy_error_m", 2.0)
        self.declare_parameter("abort_safe_height_m", 2.5)
        self.declare_parameter("abort_climb_speed_mps", 0.35)
        self.declare_parameter("abort_climb_duration_s", 4.0)
        self.declare_parameter("abort_hold_duration_s", 1.0)

        self.declare_parameter("turn_off_motors_on_landed", False)
        self.declare_parameter("turn_off_motors_service", PsdkTopics.PROPS_OFF_SRV)

        self._robot_name = str(self.get_parameter("robot_name").value)
        self.declare_parameter("controller_frame", f"{self._robot_name}/{DJILinks.BASE_FLAT}")
        self._controller_frame = str(self.get_parameter("controller_frame").value)

        model_path = str(self.get_parameter("model_path").value)
        if not model_path:
            model_path = str(
                Path(get_package_share_directory("dji_captain"))
                / "models/M350/discrete_model/discrete_models.yaml"
            )
        sample_time = float(self.get_parameter("model_sample_time_s").value)
        self._model: DiscreteVelocityModel = load_velocity_model(
            model_path,
            model_kind=str(self.get_parameter("model_kind").value),
            sample_time=sample_time if sample_time > 0.0 else None,
        )
        self._control = LandingControl(
            self._model,
            self.get_parameter("q_diagonal_xy").value,
            self.get_parameter("r_diagonal_xy").value,
        )
        self.get_logger().info(
            f"Loaded M350 model from {self._model.source}; "
            f"dt={self._model.dt:.4f}s, gains={self._model.dc_gain_vector}"
        )
        self.get_logger().info(f"Discrete XY LQR gain:\n{self._control.gain}")
        self._buffer = Buffer()
        self._listener = TransformListener(self._buffer, self)
        self._was_active = False

        motor_service = str(self.get_parameter("turn_off_motors_service").value)
        self._turn_off_motors_client = self.create_client(Trigger, motor_service)
        self._motor_off_requested = False

        self._state = LandingState.IDLE
        self._state_entered = self.get_clock().now()
        self._latest_state: Optional[LandingRelativeState] = None
        self._height_reference = 0.0
        self._last_update = self.get_clock().now()
        self._valid_since: Optional[Time] = None
        self._condition_since: Optional[Time] = None
        self._invalid_since: Optional[Time] = None
        self._auto_start_consumed = False
        self._detail = "idle"
        self._last_descent_allowed = False
        self._last_vertical_reference_velocity = 0.0

        self._latest_command: Optional[TwistStamped] = None
        self._latest_reference: Optional[LandingReference] = None
        self._was_enabled = False
        self._flush_remaining = 0

        self.create_subscription(
            LandingRelativeState,
            str(self.get_parameter("relative_state_topic").value),
            self._relative_state_callback,
            20,
        )

        self._reference_publisher = self.create_publisher(
            LandingReference,
            str(self.get_parameter("reference_topic").value),
            20,
        )
        self._status_publisher = self.create_publisher(
            LandingStatus,
            str(self.get_parameter("status_topic").value),
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

        output_topic = str(self.get_parameter("output_topic").value)
        self._velocity_publisher = self.create_publisher(TwistStamped, output_topic, 20)
        self.get_logger().info(f"Landing velocity output: {output_topic} [TwistStamped]")

        mirror_topic = str(self.get_parameter("mirror_vector_topic").value)
        self._mirror_publisher = None
        if mirror_topic:
            self._mirror_publisher = self.create_publisher(Vector3Stamped, mirror_topic, 20)
            self.get_logger().info(
                "Mirroring final landing velocity command as "
                f"Vector3Stamped on {mirror_topic}"
            )

        self.create_service(
            Trigger, str(self.get_parameter("start_service").value), self._start_service
        )
        self.create_service(
            Trigger, str(self.get_parameter("abort_service").value), self._abort_service
        )
        self.create_service(
            Trigger, str(self.get_parameter("reset_service").value), self._reset_service
        )

        update_rate = float(self.get_parameter("update_rate_hz").value)
        if update_rate <= 0.0:
            raise ValueError("update_rate_hz must be positive")
        publish_rate = float(self.get_parameter("publish_rate_hz").value)
        if publish_rate <= 0.0:
            raise ValueError("publish_rate_hz must be positive")

        self.create_timer(1.0 / update_rate, self._update)
        self.create_timer(self._model.dt, self._control_loop)
        self.create_timer(1.0 / publish_rate, self._publish_command)

    def _relative_state_callback(self, message: LandingRelativeState) -> None:
        self._latest_state = message

    def _start_service(
        self,
        _request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        if self._state not in {LandingState.IDLE, LandingState.LANDED}:
            response.success = False
            response.message = f"Landing already active in {self._state.name}"
            return response

        self._motor_off_requested = False
        self._transition(LandingState.ACQUIRE, "landing requested")

        response.success = True
        response.message = "Started landing in ACQUIRE"
        return response

    def _abort_service(
        self,
        _request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        if self._state in {LandingState.IDLE, LandingState.LANDED}:
            response.success = False
            response.message = f"Cannot abort from {self._state.name}"
            return response

        self._transition(LandingState.ABORT_CLIMB, "operator abort")
        response.success = True
        response.message = "Abort climb started"
        return response

    def _reset_service(
        self,
        _request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        self._motor_off_requested = False
        self._transition(LandingState.IDLE, "reset")

        response.success = True
        response.message = "Landing manager reset"
        return response

    def _transition(self, new_state: LandingState, detail: str) -> None:
        if new_state == self._state:
            return

        old_state = self._state
        self._state = new_state
        self._state_entered = self.get_clock().now()
        self._valid_since = None
        self._condition_since = None
        self._invalid_since = None
        self._detail = detail
        self.get_logger().info(f"Landing state {old_state.name} -> {new_state.name}: {detail}")

        if new_state == LandingState.ALIGN:
            minimum = float(self.get_parameter("minimum_align_height_m").value)
            relative_height = self._relative_height()
            self._height_reference = (
                max(relative_height, minimum)
                if bool(self.get_parameter("capture_current_height_on_align").value)
                else minimum
            )

        elif new_state == LandingState.ACQUIRE and self._latest_state is not None:
            self._height_reference = max(
                self._relative_height(),
                float(self.get_parameter("minimum_align_height_m").value),
            )

        elif new_state == LandingState.LANDED:
            self._request_motor_off()

    def _relative_height(self) -> float:
        return (
            float("nan")
            if self._latest_state is None
            else float(self._latest_state.relative_position.z)
        )

    def _metrics(self) -> tuple[float, float, float, float]:
        if self._latest_state is None:
            return float("inf"), float("inf"), float("nan"), float("inf")

        position = vector3_to_numpy(self._latest_state.relative_position)
        velocity = vector3_to_numpy(self._latest_state.relative_velocity)
        return (
            float(np.linalg.norm(position[:2])),
            float(np.linalg.norm(velocity[:2])),
            float(position[2]),
            float(velocity[2]),
        )

    def _request_motor_off(self) -> None:
        if (
            self._motor_off_requested
            or not bool(self.get_parameter("turn_off_motors_on_landed").value)
        ):
            return
        if self._state != LandingState.LANDED:
            return

        if not self._turn_off_motors_client.service_is_ready():
            self.get_logger().warn("Turn-off-motors service is not available.")
            return

        self._motor_off_requested = True
        self.get_logger().info("Landing confirmed; requesting motor shutdown.")
        future = self._turn_off_motors_client.call_async(Trigger.Request())
        future.add_done_callback(self._motor_off_response)

    def _motor_off_response(self, future) -> None:
        try:
            response = future.result()
        except Exception as exc:
            self.get_logger().error(f"Turn-off-motors service failed: {exc}")
            self._motor_off_requested = False
            return

        if response.success:
            self.get_logger().info(f"Motors turned off after landing: {response.message}")
        else:
            self.get_logger().error(f"Failed to turn off motors: {response.message}")
            self._motor_off_requested = False

    def _state_elapsed(self, now: Time) -> float:
        return max(0.0, (now - self._state_entered).nanoseconds * 1e-9)

    @staticmethod
    def _elapsed_since(now: Time, start: Optional[Time]) -> float:
        return 0.0 if start is None else max(0.0, (now - start).nanoseconds * 1e-9)

    def _condition_dwell(self, condition: bool, now: Time, dwell_s: float) -> bool:
        if not condition:
            self._condition_since = None
            return False

        if self._condition_since is None:
            self._condition_since = now

        return self._elapsed_since(now, self._condition_since) >= dwell_s

    def _tracking_state_usable(self, now: Time) -> bool:
        """Pause tracking on estimate loss and abort when a limit is reached."""
        if not self._estimate_valid():
            if self._invalid_since is None:
                self._invalid_since = now

            timeout = float(self.get_parameter("estimate_loss_abort_s").value)
            if self._elapsed_since(now, self._invalid_since) >= timeout:
                self._transition(LandingState.ABORT_CLIMB, "landing estimate lost")
            return False

        self._invalid_since = None
        xy_error, _, _, _ = self._metrics()
        if xy_error > float(self.get_parameter("abort_xy_error_m").value):
            self._transition(
                LandingState.ABORT_CLIMB,
                "horizontal error exceeded abort limit",
            )
            return False
        return True

    def _update(self) -> None:
        now = self.get_clock().now()
        dt = max(0.0, min((now - self._last_update).nanoseconds * 1e-9, 0.2))
        self._last_update = now
        self._last_descent_allowed = False
        self._last_vertical_reference_velocity = 0.0

        if (
            bool(self.get_parameter("auto_start").value)
            and not self._auto_start_consumed
            and self._latest_state is not None
            and self._latest_state.valid
            and self._state == LandingState.IDLE
        ):
            self._auto_start_consumed = True
            self._transition(LandingState.ACQUIRE, "auto-start")

        xy_error, xy_speed, relative_height, vertical_speed = self._metrics()
        estimate_valid = self._latest_state is not None and bool(self._latest_state.valid)

        if self._state == LandingState.ACQUIRE:
            self._update_acquire(now)

        elif self._state == LandingState.ALIGN:
            if self._tracking_state_usable(now):
                self._update_align(now)

        elif self._state == LandingState.DESCEND:
            if self._tracking_state_usable(now):
                self._update_descend(dt)

        elif self._state == LandingState.FINAL_DESCENT:
            if self._tracking_state_usable(now):
                self._update_final_descent(now, dt)

        elif self._state == LandingState.TOUCHDOWN:
            if self._state_elapsed(now) >= float(self.get_parameter("touchdown_hold_s").value):
                self._transition(LandingState.LANDED, "touchdown hold complete")

        elif self._state == LandingState.ABORT_CLIMB:
            safe_height = float(self.get_parameter("abort_safe_height_m").value)
            duration = float(self.get_parameter("abort_climb_duration_s").value)

            if (
                (estimate_valid and relative_height >= safe_height)
                or self._state_elapsed(now) >= duration
            ):
                self._transition(LandingState.ABORT_HOLD, "abort climb complete")

        elif self._state == LandingState.ABORT_HOLD:
            if self._state_elapsed(now) >= float(self.get_parameter("abort_hold_duration_s").value):
                self._transition(LandingState.IDLE, "abort complete")

        self._publish_reference(now)
        self._publish_status(now, xy_error, xy_speed, relative_height, vertical_speed)

    def _update_acquire(self, now: Time) -> None:
        if self._estimate_valid():
            if self._valid_since is None:
                self._valid_since = now

            if self._elapsed_since(now, self._valid_since) >= float(
                self.get_parameter("acquire_duration_s").value
            ):
                self._transition(LandingState.ALIGN, "estimate stable")
        else:
            self._valid_since = None

    def _update_align(self, now: Time) -> None:
        xy_error, xy_speed, _, _ = self._metrics()
        aligned = (
            xy_error <= float(self.get_parameter("align_xy_tolerance_m").value)
            and xy_speed <= float(self.get_parameter("align_speed_tolerance_mps").value)
        )

        if self._condition_dwell(
            aligned, now, float(self.get_parameter("align_dwell_s").value)
        ):
            if bool(self.get_parameter("enable_descent").value):
                self._transition(LandingState.DESCEND, "horizontal alignment stable")
            else:
                self._detail = "tracking-only: alignment stable"

    def _update_descend(self, dt: float) -> None:
        final_height = float(self.get_parameter("final_descent_height_m").value)
        self._last_descent_allowed = self._descent_is_allowed()
        if self._last_descent_allowed:
            rate = float(self.get_parameter("descent_rate_mps").value)
            self._lower_height_reference(dt, rate, final_height)

        entry_margin = float(self.get_parameter("final_descent_entry_margin_m").value)
        if (
            self._height_reference <= final_height + 1e-06
            and self._relative_height() <= final_height + entry_margin
        ):
            self._transition(LandingState.FINAL_DESCENT, "entered final descent region")

    def _update_final_descent(self, now: Time, dt: float) -> None:
        self._last_descent_allowed = self._descent_is_allowed()
        if self._last_descent_allowed:
            rate = float(self.get_parameter("final_descent_rate_mps").value)
            touchdown_height = float(self.get_parameter("touchdown_height_m").value)
            self._lower_height_reference(dt, rate, touchdown_height)

        xy_error, _, relative_height, vertical_speed = self._metrics()
        # Require low gear clearance, XY alignment and relative
        # vertical speed together for the configured dwell.
        touchdown_condition = (
            relative_height <= float(self.get_parameter("touchdown_detection_height_m").value)
            and xy_error <= float(self.get_parameter("touchdown_xy_tolerance_m").value)
            and abs(vertical_speed)
            <= float(self.get_parameter("touchdown_vertical_speed_mps").value)
        )

        if self._condition_dwell(
            touchdown_condition,
            now,
            float(self.get_parameter("touchdown_dwell_s").value),
        ):
            self._transition(LandingState.TOUCHDOWN, "touchdown conditions stable")

    def _estimate_valid(self) -> bool:
        return self._latest_state is not None and bool(self._latest_state.valid)

    def _descent_is_allowed(self) -> bool:
        xy_error, xy_speed, _, _ = self._metrics()
        return (
            xy_error <= float(self.get_parameter("descent_pause_xy_m").value)
            and xy_speed <= float(self.get_parameter("descent_pause_speed_mps").value)
        )

    def _lower_height_reference(self, dt: float, rate: float, floor: float) -> None:
        previous_height = self._height_reference
        self._height_reference = max(floor, self._height_reference - rate * dt)

        if self._height_reference < previous_height - 1e-09:
            self._last_vertical_reference_velocity = -rate

    def _publish_reference(self, now: Time) -> None:
        message = LandingReference()
        message.header.stamp = now.to_msg()
        message.header.frame_id = (
            self._latest_state.header.frame_id
            if self._latest_state is not None
            else f"{self._robot_name}/{DJILinks.MAP}"
        )
        message.state = int(self._state)
        message.state_name = self._state.name
        message.height_above_pad = float(self._height_reference)
        message.vertical_reference_velocity = float(self._last_vertical_reference_velocity)

        estimate_valid = self._latest_state is not None and bool(self._latest_state.valid)
        message.control_enabled = self._state in TRACKING_STATES and estimate_valid
        message.descent_allowed = bool(self._last_descent_allowed)
        message.override_active = False
        message.controller_frame = self._controller_frame

        if self._state == LandingState.ABORT_CLIMB:
            message.control_enabled = True
            message.override_active = True
            message.override_velocity.z = float(self.get_parameter("abort_climb_speed_mps").value)

        elif self._state in {LandingState.ABORT_HOLD, LandingState.TOUCHDOWN}:
            message.control_enabled = True
            message.override_active = True

        elif self._state == LandingState.LANDED:
            message.control_enabled = False

        self._latest_reference = message
        self._reference_publisher.publish(message)

    def _publish_status(
        self,
        now: Time,
        xy_error: float,
        xy_speed: float,
        relative_height: float,
        vertical_speed: float,
    ) -> None:
        message = LandingStatus()
        message.header.stamp = now.to_msg()
        message.header.frame_id = (
            self._latest_state.header.frame_id
            if self._latest_state is not None
            else f"{self._robot_name}/{DJILinks.MAP}"
        )
        message.state = int(self._state)
        message.state_name = self._state.name
        message.detail = self._detail
        message.active = self._state not in {LandingState.IDLE, LandingState.LANDED}
        message.estimate_valid = self._latest_state is not None and bool(self._latest_state.valid)
        message.control_enabled = self._state in TRACKING_STATES and message.estimate_valid
        message.descent_allowed = self._last_descent_allowed
        message.horizontal_error = float(xy_error)
        message.horizontal_relative_speed = float(xy_speed)
        message.relative_height = float(relative_height)
        message.vertical_relative_speed = float(vertical_speed)
        message.height_reference = float(self._height_reference)
        message.state_elapsed = self._state_elapsed(now)
        self._status_publisher.publish(message)

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
                self._control.reset()
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

        final_descent = reference.state_name == "FINAL_DESCENT"
        parameters = ControlParameters(
            z_kp=float(self.get_parameter("z_kp").value),
            z_kd=float(self.get_parameter("z_kd").value),
            max_xy_speed_mps=float(self.get_parameter(
                "max_xy_speed_final_mps" if final_descent else "max_xy_speed_mps"
            ).value),
            max_up_speed_mps=float(self.get_parameter("max_up_speed_mps").value),
            max_down_speed_mps=float(self.get_parameter(
                "max_down_speed_final_mps" if final_descent else "max_down_speed_mps"
            ).value),
            command_cutoff_hz=float(self.get_parameter("command_cutoff_hz").value),
            max_command_rate_mps2=self.get_parameter("max_command_rate_mps2").value,
        )
        result = self._control.compute(
            relative_position,
            relative_velocity,
            pad_velocity,
            height_above_pad=float(reference.height_above_pad),
            vertical_reference_velocity=float(reference.vertical_reference_velocity),
            parameters=parameters,
        )
        self._was_active = True

        command_message = TwistStamped()
        command_message.header.stamp = now.to_msg()
        command_message.header.frame_id = self._controller_frame
        command_message.twist.linear = numpy_to_vector3(result.command_filtered)
        command_message.twist.angular.z = 0.0
        self._latest_command = command_message
        self._command_publisher.publish(command_message)

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
        self._debug_publisher.publish(debug)

    @staticmethod
    def _age(now: Time, stamp) -> float:
        return max(0.0, (now - Time.from_msg(stamp)).nanoseconds * 1e-09)

    def _zero_message(self, now: Time, frame_id: Optional[str] = None) -> TwistStamped:
        message = TwistStamped()
        message.header.stamp = now.to_msg()
        message.header.frame_id = frame_id if frame_id else self._controller_frame
        return message

    def _publish_output(self, message: TwistStamped) -> None:
        self._velocity_publisher.publish(message)
        if self._mirror_publisher is None:
            return

        mirror = Vector3Stamped()
        mirror.header = message.header
        mirror.vector = message.twist.linear
        self._mirror_publisher.publish(mirror)

    def _publish_command(self) -> None:
        """Select the FSM override or a fresh controller command at the output rate."""
        now = self.get_clock().now()

        if self._latest_reference is None:
            self.get_logger().info(
                "Landing output inactive: no landing reference",
                throttle_duration_sec=2.0,
            )
            self._handle_disabled(now)
            return

        reference_age = self._age(now, self._latest_reference.header.stamp)
        reference_timeout = float(self.get_parameter("reference_timeout_s").value)
        if reference_age > reference_timeout:
            self.get_logger().warning(
                "Landing output inactive: landing reference stale "
                f"({reference_age:.3f}s > {reference_timeout:.3f}s)",
                throttle_duration_sec=2.0,
            )
            self._handle_disabled(now)
            return

        if not self._latest_reference.control_enabled:
            self.get_logger().info(
                "Landing output inactive: control disabled by landing manager",
                throttle_duration_sec=2.0,
            )
            self._handle_disabled(now)
            return

        if self._latest_reference.override_active:
            output = self._zero_message(now)
            output.twist.linear.x = float(self._latest_reference.override_velocity.x)
            output.twist.linear.y = float(self._latest_reference.override_velocity.y)
            output.twist.linear.z = float(self._latest_reference.override_velocity.z)
            self._publish_output(output)
            self._was_enabled = True
            self._flush_remaining = int(self.get_parameter("zero_flush_cycles").value)
            return

        if self._latest_command is None:
            self.get_logger().warning(
                "Landing output enabled but no controller command has been received",
                throttle_duration_sec=2.0,
            )
            self._publish_output(self._zero_message(now))
            return

        controller_age = self._age(now, self._latest_command.header.stamp)
        controller_timeout = float(self.get_parameter("controller_timeout_s").value)
        if controller_age > controller_timeout:
            self.get_logger().warning(
                "Landing output enabled but controller command stale "
                f"({controller_age:.3f}s > {controller_timeout:.3f}s)",
                throttle_duration_sec=2.0,
            )
            self._publish_output(self._zero_message(now))
            self._was_enabled = True
            self._flush_remaining = int(self.get_parameter("zero_flush_cycles").value)
            return

        output = self._zero_message(now, self._latest_command.header.frame_id)
        output.twist.linear.x = float(self._latest_command.twist.linear.x)
        output.twist.linear.y = float(self._latest_command.twist.linear.y)
        output.twist.linear.z = float(self._latest_command.twist.linear.z)
        output.twist.angular.x = float(self._latest_command.twist.angular.x)
        output.twist.angular.y = float(self._latest_command.twist.angular.y)
        output.twist.angular.z = float(self._latest_command.twist.angular.z)
        self._publish_output(output)
        self._was_enabled = True
        self._flush_remaining = int(self.get_parameter("zero_flush_cycles").value)

    def _handle_disabled(self, now: Time) -> None:
        if self._was_enabled:
            self._was_enabled = False
            self._flush_remaining = int(self.get_parameter("zero_flush_cycles").value)
        if self._flush_remaining <= 0:
            return

        self._publish_output(self._zero_message(now))
        self._flush_remaining -= 1


def main(args=None) -> None:
    rclpy.init(args=args)
    node = LandingManagerNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        # ROS may already have shut the context down while handling SIGINT.
        if rclpy.ok():
            rclpy.shutdown()
