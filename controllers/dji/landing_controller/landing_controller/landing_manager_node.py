from enum import IntEnum
from typing import Optional

import numpy as np
import rclpy
from dji_msgs.msg import (
    LandingReference,
    LandingRelativeState,
    LandingStatus,
    Links as DJILinks,
    PsdkTopics,
    Topics as DJITopics,
)
from rclpy.node import Node
from rclpy.time import Time
from std_srvs.srv import Trigger

from .math_utils import vector3_to_numpy


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
    """Manage landing phases and publish height references and abort overrides."""

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

        self.create_timer(1.0 / update_rate, self._update)

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

    def _handle_estimate_validity(self, now: Time) -> bool:
        valid = self._latest_state is not None and bool(self._latest_state.valid)

        if valid:
            self._invalid_since = None
            return True

        if self._invalid_since is None:
            self._invalid_since = now

        timeout = float(self.get_parameter("estimate_loss_abort_s").value)
        if self._elapsed_since(now, self._invalid_since) >= timeout:
            self._transition(LandingState.ABORT_CLIMB, "landing estimate lost")

        return False

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
            if estimate_valid:
                if self._valid_since is None:
                    self._valid_since = now

                if self._elapsed_since(now, self._valid_since) >= float(
                    self.get_parameter("acquire_duration_s").value
                ):
                    self._transition(LandingState.ALIGN, "estimate stable")
            else:
                self._valid_since = None

        elif self._state == LandingState.ALIGN:
            if self._handle_estimate_validity(now):
                if xy_error > float(self.get_parameter("abort_xy_error_m").value):
                    self._transition(
                        LandingState.ABORT_CLIMB,
                        "horizontal error exceeded abort limit",
                    )
                else:
                    aligned = (
                        xy_error <= float(self.get_parameter("align_xy_tolerance_m").value)
                        and xy_speed <= float(self.get_parameter("align_speed_tolerance_mps").value)
                    )

                    if self._condition_dwell(aligned, now, float(self.get_parameter("align_dwell_s").value)):
                        if bool(self.get_parameter("enable_descent").value):
                            self._transition(LandingState.DESCEND, "horizontal alignment stable")
                        else:
                            self._detail = "tracking-only: alignment stable"

        elif self._state == LandingState.DESCEND:
            if self._handle_estimate_validity(now):
                if xy_error > float(self.get_parameter("abort_xy_error_m").value):
                    self._transition(
                        LandingState.ABORT_CLIMB,
                        "horizontal error exceeded abort limit",
                    )
                else:
                    allowed = (
                        xy_error <= float(self.get_parameter("descent_pause_xy_m").value)
                        and xy_speed <= float(self.get_parameter("descent_pause_speed_mps").value)
                    )
                    self._last_descent_allowed = allowed

                    if allowed:
                        rate = float(self.get_parameter("descent_rate_mps").value)
                        final_height = float(self.get_parameter("final_descent_height_m").value)
                        previous_height = self._height_reference
                        self._height_reference = max(
                            final_height,
                            self._height_reference - rate * dt,
                        )

                        if self._height_reference < previous_height - 1e-09:
                            self._last_vertical_reference_velocity = -rate

                    final_height = float(self.get_parameter("final_descent_height_m").value)
                    entry_margin = float(self.get_parameter("final_descent_entry_margin_m").value)

                    if (
                        self._height_reference <= final_height + 1e-06
                        and relative_height <= final_height + entry_margin
                    ):
                        self._transition(LandingState.FINAL_DESCENT, "entered final descent region")

        elif self._state == LandingState.FINAL_DESCENT:
            if self._handle_estimate_validity(now):
                if xy_error > float(self.get_parameter("abort_xy_error_m").value):
                    self._transition(
                        LandingState.ABORT_CLIMB,
                        "horizontal error exceeded abort limit",
                    )
                else:
                    allowed = (
                        xy_error <= float(self.get_parameter("descent_pause_xy_m").value)
                        and xy_speed <= float(self.get_parameter("descent_pause_speed_mps").value)
                    )
                    self._last_descent_allowed = allowed

                    if allowed:
                        rate = float(self.get_parameter("final_descent_rate_mps").value)
                        touchdown_height = float(self.get_parameter("touchdown_height_m").value)
                        previous_height = self._height_reference
                        self._height_reference = max(
                            touchdown_height,
                            self._height_reference - rate * dt,
                        )

                        if self._height_reference < previous_height - 1e-09:
                            self._last_vertical_reference_velocity = -rate

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
