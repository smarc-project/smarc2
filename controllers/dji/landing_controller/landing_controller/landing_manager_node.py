from enum import IntEnum
from pathlib import Path
from threading import RLock
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
from geometry_msgs.msg import TwistStamped
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.time import Time
from std_srvs.srv import Trigger
from tf2_ros import Buffer, TransformListener

from .landing_action_server import LandingActionServer
from .landing_command import LandingCommand
from .landing_control import LandingControl
from .math_utils import vector3_to_numpy
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

    LandingCommand handles controller updates and command selection, while this
    node manages landing transitions and ROS interfaces (LandingActionServer and services).
    """

    def __init__(self, **node_kwargs) -> None:
        super().__init__("landing_manager", **node_kwargs)
        # Default callbacks stay serialized; action callbacks share this lock.
        self._state_lock = RLock()

        self.declare_parameter("robot_name", "M350")
        self.declare_parameter("landing_manager.relative_state_topic", DJITopics.RELATIVE_STATE_TOPIC)
        self.declare_parameter("landing_manager.status_topic", DJITopics.STATUS_TOPIC)
        self.declare_parameter("landing_manager.start_service", DJITopics.LANDING_START_SERVICE)
        self.declare_parameter("landing_manager.abort_service", DJITopics.LANDING_ABORT_SERVICE)
        self.declare_parameter("landing_manager.reset_service", DJITopics.LANDING_RESET_SERVICE)
        self.declare_parameter("landing_manager.update_rate_hz", 20.0)
        self.declare_parameter("landing_manager.auto_start", False)
        self.declare_parameter("landing_manager.enable_descent", True)
        self.declare_parameter("landing_manager.action_name", "alars_land_on_pad")
        self.declare_parameter("landing_manager.default_timeout", 120.0)

        # Command output and watchdogs, previously owned by the velocity mux.
        self.declare_parameter("landing_manager.output_topic", DJITopics.VELOCITY_SETPOINT_TOPIC)
        self.declare_parameter("landing_manager.publish_rate_hz", 50.0)
        self.declare_parameter("landing_manager.controller_timeout_s", 0.15)
        self.declare_parameter("landing_manager.reference_timeout_s", 0.25)
        self.declare_parameter("landing_manager.zero_flush_cycles", 8)

        # Model and control tuning; the calculations remain in landing_control.py.
        self.declare_parameter("landing_lqr_controller.model_path", "")
        self.declare_parameter("landing_lqr_controller.model_kind", "auto")
        self.declare_parameter("landing_lqr_controller.model_sample_time_s", 0.0)
        self.declare_parameter("landing_lqr_controller.debug_topic", DJITopics.CONTROLLER_DEBUG_TOPIC)
        self.declare_parameter("landing_lqr_controller.tf_timeout_s", 0.04)
        self.declare_parameter("landing_lqr_controller.tf_fallback_to_latest", True)
        self.declare_parameter("landing_lqr_controller.max_state_age_s", 0.20)
        self.declare_parameter("landing_lqr_controller.max_reference_age_s", 0.20)
        self.declare_parameter("landing_lqr_controller.q_diagonal_xy", [12.0, 12.0, 4.0, 4.0])
        self.declare_parameter("landing_lqr_controller.r_diagonal_xy", [1.0, 1.0])
        self.declare_parameter("landing_lqr_controller.z_kp", 0.75)
        self.declare_parameter("landing_lqr_controller.z_kd", 0.30)
        self.declare_parameter("landing_lqr_controller.max_xy_speed_mps", 1.0)
        self.declare_parameter("landing_lqr_controller.max_xy_speed_final_mps", 0.35)
        self.declare_parameter("landing_lqr_controller.max_up_speed_mps", 0.45)
        self.declare_parameter("landing_lqr_controller.max_down_speed_mps", 0.25)
        self.declare_parameter("landing_lqr_controller.max_down_speed_final_mps", 0.10)
        self.declare_parameter("landing_lqr_controller.command_cutoff_hz", 0.8)
        self.declare_parameter("landing_lqr_controller.max_command_rate_mps2", [0.8, 0.8, 0.5])
        self.declare_parameter("landing_lqr_controller.start_filter_from_zero", True)

        self.declare_parameter("landing_manager.acquire_duration_s", 1.0)
        self.declare_parameter("landing_manager.minimum_align_height_m", 2.0)
        self.declare_parameter("landing_manager.capture_current_height_on_align", True)
        self.declare_parameter("landing_manager.align_xy_tolerance_m", 0.40)
        self.declare_parameter("landing_manager.align_speed_tolerance_mps", 0.25)
        self.declare_parameter("landing_manager.align_dwell_s", 1.5)

        self.declare_parameter("landing_manager.descent_rate_mps", 0.20)
        self.declare_parameter("landing_manager.descent_pause_xy_m", 0.55)
        self.declare_parameter("landing_manager.descent_pause_speed_mps", 0.35)
        self.declare_parameter("landing_manager.final_descent_height_m", 0.50)
        self.declare_parameter("landing_manager.final_descent_entry_margin_m", 0.20)
        self.declare_parameter("landing_manager.final_descent_rate_mps", 0.08)

        self.declare_parameter("landing_manager.touchdown_height_m", 0.08)
        self.declare_parameter("landing_manager.touchdown_detection_height_m", 0.12)
        self.declare_parameter("landing_manager.touchdown_xy_tolerance_m", 0.25)
        self.declare_parameter("landing_manager.touchdown_vertical_speed_mps", 0.15)
        self.declare_parameter("landing_manager.touchdown_dwell_s", 0.6)
        self.declare_parameter("landing_manager.touchdown_hold_s", 1.0)

        self.declare_parameter("landing_manager.estimate_loss_abort_s", 1.0)
        self.declare_parameter("landing_manager.abort_xy_error_m", 2.0)
        self.declare_parameter("landing_manager.abort_safe_height_m", 2.5)
        self.declare_parameter("landing_manager.abort_climb_speed_mps", 0.35)
        self.declare_parameter("landing_manager.abort_climb_duration_s", 4.0)
        self.declare_parameter("landing_manager.abort_hold_duration_s", 1.0)

        self.declare_parameter("landing_manager.turn_off_motors_on_landed", False)
        self.declare_parameter("landing_manager.turn_off_motors_service", PsdkTopics.PROPS_OFF_SRV)

        self._robot_name = str(self.get_parameter("robot_name").value)
        self.declare_parameter("landing_lqr_controller.controller_frame", f"{self._robot_name}/{DJILinks.BASE_FLAT}")
        self._controller_frame = str(self.get_parameter("landing_lqr_controller.controller_frame").value)

        model_path = str(self.get_parameter("landing_lqr_controller.model_path").value)
        if not model_path:
            model_path = str(
                Path(get_package_share_directory("dji_captain"))
                / "models/M350/discrete_model/discrete_models.yaml"
            )
        sample_time = float(self.get_parameter("landing_lqr_controller.model_sample_time_s").value)
        self._model: DiscreteVelocityModel = load_velocity_model(
            model_path,
            model_kind=str(self.get_parameter("landing_lqr_controller.model_kind").value),
            sample_time=sample_time if sample_time > 0.0 else None,
        )
        control = LandingControl(
            self._model,
            self.get_parameter("landing_lqr_controller.q_diagonal_xy").value,
            self.get_parameter("landing_lqr_controller.r_diagonal_xy").value,
        )
        self.get_logger().info(
            f"Loaded M350 model from {self._model.source}; "
            f"dt={self._model.dt:.4f}s, gains={self._model.dc_gain_vector}"
        )
        self.get_logger().info(f"Discrete XY LQR gain:\n{control.gain}")
        buffer = Buffer()
        self._listener = TransformListener(buffer, self)
        self._command = LandingCommand(control, self._controller_frame, buffer, self.get_logger())

        motor_service = str(self.get_parameter("landing_manager.turn_off_motors_service").value)
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

        self._latest_reference: Optional[LandingReference] = None

        self.create_subscription(
            LandingRelativeState,
            str(self.get_parameter("landing_manager.relative_state_topic").value),
            self._relative_state_callback,
            20,
        )

        self._status_publisher = self.create_publisher(
            LandingStatus,
            str(self.get_parameter("landing_manager.status_topic").value),
            20,
        )
        self._debug_publisher = self.create_publisher(
            LandingControllerDebug,
            str(self.get_parameter("landing_lqr_controller.debug_topic").value),
            20,
        )

        output_topic = str(self.get_parameter("landing_manager.output_topic").value)
        self._velocity_publisher = self.create_publisher(TwistStamped, output_topic, 20)
        self.get_logger().info(f"Landing velocity output: {output_topic} [TwistStamped]")

        self.create_service(
            Trigger, str(self.get_parameter("landing_manager.start_service").value), self._start_service
        )
        self.create_service(
            Trigger, str(self.get_parameter("landing_manager.abort_service").value), self._abort_service
        )
        self.create_service(
            Trigger, str(self.get_parameter("landing_manager.reset_service").value), self._reset_service
        )

        self._action_server = LandingActionServer(
            self,
            self._accept_landing_goal,
            self._start_landing,
            self._abort_landing,
            self._finish_landing,
            self._landing_feedback,
            state_lock=self._state_lock,
        )

        update_rate = float(self.get_parameter("landing_manager.update_rate_hz").value)
        if update_rate <= 0.0:
            raise ValueError("update_rate_hz must be positive")
        publish_rate = float(self.get_parameter("landing_manager.publish_rate_hz").value)
        if publish_rate <= 0.0:
            raise ValueError("publish_rate_hz must be positive")

        self.create_timer(1.0 / update_rate, self._update)
        self.create_timer(self._model.dt, self._control_loop)
        self.create_timer(1.0 / publish_rate, self._publish_command)

    def _relative_state_callback(self, message: LandingRelativeState) -> None:
        with self._state_lock:
            self._latest_state = message

    def _start_service(
        self,
        _request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        with self._state_lock:
            if self._action_server.pending or self._state not in {LandingState.IDLE, LandingState.LANDED}:
                response.success = False
                response.message = f"Landing already active in {self._state.name}"
                return response

            self._start_landing("landing requested")

            response.success = True
            response.message = "Started landing in ACQUIRE"
            return response

    def _abort_service(
        self,
        _request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        with self._state_lock:
            response.success = self._abort_landing("operator abort")
            response.message = ("Abort climb started" if response.success
                                else f"Cannot abort from {self._state.name}")
            return response

    def _reset_service(
        self,
        _request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        with self._state_lock:
            self._action_server.set_result(False)
            self._reset_states()
            self._transition(LandingState.IDLE, "reset")
            self._update_reference(self.get_clock().now())

            response.success = True
            response.message = "Landing manager reset"
            return response

    def _reset_states(self) -> None:
        """Clear this attempt without clearing perception or rearming auto-start."""
        now = self.get_clock().now()
        self._state_entered = self._last_update = now
        self._valid_since = self._condition_since = self._invalid_since = None
        self._height_reference = 0.0
        self._last_descent_allowed = False
        self._last_vertical_reference_velocity = 0.0
        self._latest_reference = None
        self._motor_off_requested = False
        self._command.reset()

    def _accept_landing_goal(self) -> bool:
        if self._state != LandingState.IDLE:
            return False
        self._auto_start_consumed = True
        return True

    def _start_landing(self, detail: str) -> None:
        self._reset_states()
        self._auto_start_consumed = True
        self._transition(LandingState.ACQUIRE, detail)
        self._update_reference(self.get_clock().now())

    def _abort_landing(self, detail: str) -> bool:
        if self._state in {LandingState.IDLE, LandingState.LANDED}:
            return False
        if self._state not in {LandingState.ABORT_CLIMB, LandingState.ABORT_HOLD}:
            self._transition(LandingState.ABORT_CLIMB, detail)
            self._update_reference(self.get_clock().now())
        return True

    def _finish_landing(self, detail: str) -> None:
        if self._state == LandingState.LANDED:
            self._reset_states()
            self._transition(LandingState.IDLE, detail)
            self._update_reference(self.get_clock().now())

    def _landing_feedback(self) -> str:
        xy_error, xy_speed, height, _ = self._metrics()
        return (
            f"{self._state.name} | xy={xy_error:.2f}m | h={height:.2f}m | "
            f"vxy={xy_speed:.2f}m/s | estimate={'valid' if self._estimate_valid() else 'invalid'}"
        )

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
            minimum = float(self.get_parameter("landing_manager.minimum_align_height_m").value)
            relative_height = self._relative_height()
            self._height_reference = (
                max(relative_height, minimum)
                if bool(self.get_parameter("landing_manager.capture_current_height_on_align").value)
                else minimum
            )

        elif new_state == LandingState.ACQUIRE and self._latest_state is not None:
            self._height_reference = max(
                self._relative_height(),
                float(self.get_parameter("landing_manager.minimum_align_height_m").value),
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
            or not bool(self.get_parameter("landing_manager.turn_off_motors_on_landed").value)
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
        with self._state_lock:
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

            timeout = float(self.get_parameter("landing_manager.estimate_loss_abort_s").value)
            if self._elapsed_since(now, self._invalid_since) >= timeout:
                self._transition(LandingState.ABORT_CLIMB, "landing estimate lost")
            return False

        self._invalid_since = None
        xy_error, _, _, _ = self._metrics()
        if xy_error > float(self.get_parameter("landing_manager.abort_xy_error_m").value):
            self._transition(
                LandingState.ABORT_CLIMB,
                "horizontal error exceeded abort limit",
            )
            return False
        return True

    def _update(self) -> None:
        with self._state_lock:
            now = self.get_clock().now()
            dt = max(0.0, min((now - self._last_update).nanoseconds * 1e-9, 0.2))
            self._last_update = now
            self._last_descent_allowed = False
            self._last_vertical_reference_velocity = 0.0

            if (
                bool(self.get_parameter("landing_manager.auto_start").value)
                and not self._auto_start_consumed
                and not self._action_server.pending
                and self._latest_state is not None
                and self._latest_state.valid
                and self._state == LandingState.IDLE
            ):
                self._reset_states()
                self._auto_start_consumed = True
                self._transition(LandingState.ACQUIRE, "auto-start")

            if (
                self._action_server.timed_out(now)
                and self._state not in {
                    LandingState.IDLE, LandingState.LANDED,
                    LandingState.ABORT_CLIMB, LandingState.ABORT_HOLD,
                }
            ):
                self._abort_landing("landing action timed out")

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
                if self._state_elapsed(now) >= float(self.get_parameter("landing_manager.touchdown_hold_s").value):
                    self._transition(LandingState.LANDED, "touchdown hold complete")

            elif self._state == LandingState.ABORT_CLIMB:
                safe_height = float(self.get_parameter("landing_manager.abort_safe_height_m").value)
                duration = float(self.get_parameter("landing_manager.abort_climb_duration_s").value)

                if (
                    (estimate_valid and relative_height >= safe_height)
                    or self._state_elapsed(now) >= duration
                ):
                    self._transition(LandingState.ABORT_HOLD, "abort climb complete")

            elif self._state == LandingState.ABORT_HOLD:
                if self._state_elapsed(now) >= float(self.get_parameter("landing_manager.abort_hold_duration_s").value):
                    self._reset_states()
                    self._transition(LandingState.IDLE, "abort complete")
                    self._action_server.set_result(False)

            elif self._state == LandingState.LANDED and not self._action_server.pending:
                self._finish_landing("landing complete")

            if self._state == LandingState.LANDED:
                self._action_server.set_result(True)

            self._update_reference(now)
            self._publish_status(now, xy_error, xy_speed, relative_height, vertical_speed)

    def _update_acquire(self, now: Time) -> None:
        if self._estimate_valid():
            if self._valid_since is None:
                self._valid_since = now

            if self._elapsed_since(now, self._valid_since) >= float(
                self.get_parameter("landing_manager.acquire_duration_s").value
            ):
                self._transition(LandingState.ALIGN, "estimate stable")
        else:
            self._valid_since = None

    def _update_align(self, now: Time) -> None:
        xy_error, xy_speed, _, _ = self._metrics()
        aligned = (
            xy_error <= float(self.get_parameter("landing_manager.align_xy_tolerance_m").value)
            and xy_speed <= float(self.get_parameter("landing_manager.align_speed_tolerance_mps").value)
        )

        if self._condition_dwell(
            aligned, now, float(self.get_parameter("landing_manager.align_dwell_s").value)
        ):
            if bool(self.get_parameter("landing_manager.enable_descent").value):
                self._transition(LandingState.DESCEND, "horizontal alignment stable")
            else:
                self._detail = "tracking-only: alignment stable"

    def _update_descend(self, dt: float) -> None:
        final_height = float(self.get_parameter("landing_manager.final_descent_height_m").value)
        self._last_descent_allowed = self._descent_is_allowed()
        if self._last_descent_allowed:
            rate = float(self.get_parameter("landing_manager.descent_rate_mps").value)
            self._lower_height_reference(dt, rate, final_height)

        entry_margin = float(self.get_parameter("landing_manager.final_descent_entry_margin_m").value)
        if (
            self._height_reference <= final_height + 1e-06
            and self._relative_height() <= final_height + entry_margin
        ):
            self._transition(LandingState.FINAL_DESCENT, "entered final descent region")

    def _update_final_descent(self, now: Time, dt: float) -> None:
        self._last_descent_allowed = self._descent_is_allowed()
        if self._last_descent_allowed:
            rate = float(self.get_parameter("landing_manager.final_descent_rate_mps").value)
            touchdown_height = float(self.get_parameter("landing_manager.touchdown_height_m").value)
            self._lower_height_reference(dt, rate, touchdown_height)

        xy_error, _, relative_height, vertical_speed = self._metrics()
        # Require low gear clearance, XY alignment and relative
        # vertical speed together for the configured dwell.
        touchdown_condition = (
            relative_height <= float(self.get_parameter("landing_manager.touchdown_detection_height_m").value)
            and xy_error <= float(self.get_parameter("landing_manager.touchdown_xy_tolerance_m").value)
            and abs(vertical_speed)
            <= float(self.get_parameter("landing_manager.touchdown_vertical_speed_mps").value)
        )

        if self._condition_dwell(
            touchdown_condition,
            now,
            float(self.get_parameter("landing_manager.touchdown_dwell_s").value),
        ):
            self._transition(LandingState.TOUCHDOWN, "touchdown conditions stable")

    def _estimate_valid(self) -> bool:
        return self._latest_state is not None and bool(self._latest_state.valid)

    def _descent_is_allowed(self) -> bool:
        xy_error, xy_speed, _, _ = self._metrics()
        return (
            xy_error <= float(self.get_parameter("landing_manager.descent_pause_xy_m").value)
            and xy_speed <= float(self.get_parameter("landing_manager.descent_pause_speed_mps").value)
        )

    def _lower_height_reference(self, dt: float, rate: float, floor: float) -> None:
        previous_height = self._height_reference
        self._height_reference = max(floor, self._height_reference - rate * dt)

        if self._height_reference < previous_height - 1e-09:
            self._last_vertical_reference_velocity = -rate

    def _update_reference(self, now: Time) -> None:
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
            message.override_velocity.z = float(self.get_parameter("landing_manager.abort_climb_speed_mps").value)

        elif self._state in {LandingState.ABORT_HOLD, LandingState.TOUCHDOWN}:
            message.control_enabled = True
            message.override_active = True

        elif self._state == LandingState.LANDED:
            message.control_enabled = False

        self._latest_reference = message

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

    def _control_loop(self) -> None:
        with self._state_lock:
            now = self.get_clock().now()
            parameters = {
                "tf_timeout_s": self.get_parameter("landing_lqr_controller.tf_timeout_s").value,
                "tf_fallback_to_latest": self.get_parameter("landing_lqr_controller.tf_fallback_to_latest").value,
                "max_state_age_s": self.get_parameter("landing_lqr_controller.max_state_age_s").value,
                "max_reference_age_s": self.get_parameter("landing_lqr_controller.max_reference_age_s").value,
                "start_filter_from_zero": self.get_parameter("landing_lqr_controller.start_filter_from_zero").value,
                "z_kp": self.get_parameter("landing_lqr_controller.z_kp").value,
                "z_kd": self.get_parameter("landing_lqr_controller.z_kd").value,
                "max_xy_speed_mps": self.get_parameter("landing_lqr_controller.max_xy_speed_mps").value,
                "max_xy_speed_final_mps": self.get_parameter("landing_lqr_controller.max_xy_speed_final_mps").value,
                "max_up_speed_mps": self.get_parameter("landing_lqr_controller.max_up_speed_mps").value,
                "max_down_speed_mps": self.get_parameter("landing_lqr_controller.max_down_speed_mps").value,
                "max_down_speed_final_mps": self.get_parameter("landing_lqr_controller.max_down_speed_final_mps").value,
                "command_cutoff_hz": self.get_parameter("landing_lqr_controller.command_cutoff_hz").value,
                "max_command_rate_mps2": self.get_parameter("landing_lqr_controller.max_command_rate_mps2").value,
            }
            debug = self._command.update_control(
                now, self._latest_state, self._latest_reference, parameters,
            )
            if debug is not None:
                self._debug_publisher.publish(debug)

    def _publish_command(self) -> None:
        with self._state_lock:
            output = self._command.select_output(
                self.get_clock().now(), self._latest_reference,
                controller_timeout_s=float(self.get_parameter("landing_manager.controller_timeout_s").value),
                reference_timeout_s=float(self.get_parameter("landing_manager.reference_timeout_s").value),
                zero_flush_cycles=int(self.get_parameter("landing_manager.zero_flush_cycles").value),
            )
            if output is not None:
                self._velocity_publisher.publish(output)

    # Override destroy_node to finish the action server
    def destroy_node(self):
        self._action_server.destroy()
        return super().destroy_node()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = LandingManagerNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node._action_server.set_result(False)
        executor.shutdown()
        node.destroy_node()
        # ROS may already have shut the context down while handling SIGINT.
        if rclpy.ok():
            rclpy.shutdown()
