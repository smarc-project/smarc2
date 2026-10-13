#!/usr/bin/python3

import math
from threading import Lock

import rclpy

from dji_msgs.msg import LandingStatus, Topics as DJITopics
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from smarc_action_base.gentler_action_server import GentlerActionServer
from std_srvs.srv import Trigger


class LandAction:
    """Expose the landing manager through the SMARC BaseAction interface.

    The JSON goal accepts an optional positive ``timeout`` in seconds. Flight
    control and touchdown detection remain in the landing controller stack.
    """

    def __init__(self, node: Node):
        self._node = node

        node.declare_parameter("landing_status_topic", DJITopics.STATUS_TOPIC)
        node.declare_parameter("landing_start_service", DJITopics.LANDING_START_SERVICE)
        node.declare_parameter("landing_abort_service", DJITopics.LANDING_ABORT_SERVICE)
        node.declare_parameter("default_timeout", 120.0)
        node.declare_parameter("max_status_age", 1.0)
        node.declare_parameter("start_timeout_s", 5.0)
        node.declare_parameter("abort_timeout_s", 10.0)

        self._status_topic = str(node.get_parameter("landing_status_topic").value)
        self._start_service = str(node.get_parameter("landing_start_service").value)
        self._abort_service = str(node.get_parameter("landing_abort_service").value)
        self._default_timeout = float(node.get_parameter("default_timeout").value)
        self._max_status_age = float(node.get_parameter("max_status_age").value)
        self._start_timeout = float(node.get_parameter("start_timeout_s").value)
        self._abort_timeout = float(node.get_parameter("abort_timeout_s").value)
        for name, value in (
            ("default_timeout", self._default_timeout),
            ("max_status_age", self._max_status_age),
            ("start_timeout_s", self._start_timeout),
            ("abort_timeout_s", self._abort_timeout),
        ):
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")

        self._status = None
        self._status_received_at = None
        self._start_future = None
        self._started = False
        self._seen_active = False
        self._abort_future = None
        self._abort_started_at = None
        self._cancel_requested = False
        # Cancel and execution callbacks can run on different executor threads.
        self._command_lock = Lock()
        self._goal_started_at = None
        self._timeout = self._default_timeout

        node.create_subscription(LandingStatus, self._status_topic, self._status_callback, 20)
        self._start_client = node.create_client(Trigger, self._start_service)
        self._abort_client = node.create_client(Trigger, self._abort_service)

        self._as = GentlerActionServer(
            node,
            "alars_land_on_pad",
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency=10,
        )

    @property
    def now_time(self) -> float:
        return self._node.get_clock().now().nanoseconds * 1e-9

    def log(self, message: str):
        self._node.get_logger().info(message)

    def _status_callback(self, msg: LandingStatus):
        self._status = msg
        self._status_received_at = self.now_time
        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        if (
            self._goal_started_at is not None
            and stamp >= self._goal_started_at
            and msg.state_name in {
                "ACQUIRE", "ALIGN", "DESCEND", "FINAL_DESCENT", "TOUCHDOWN",
                "ABORT_CLIMB", "ABORT_HOLD",
            }
            and msg.active
            and self._status_is_fresh()
        ):
            self._seen_active = True

    def _status_is_fresh(self) -> bool:
        if self._status is None or self._status_received_at is None:
            return False
        now = self.now_time
        stamp = self._status.header.stamp
        message_time = stamp.sec + stamp.nanosec * 1e-9
        return (
            0.0 <= now - self._status_received_at <= self._max_status_age
            and abs(now - message_time) <= self._max_status_age
        )

    def _on_goal_received(self, goal_request: dict) -> bool:
        if not isinstance(goal_request, dict):
            self.log("Rejecting landing goal: expected a JSON object.")
            return False
        try:
            timeout = float(goal_request.get("timeout", self._default_timeout))
        except (TypeError, ValueError):
            self.log(f"Invalid landing goal: {goal_request}")
            return False

        if not math.isfinite(timeout) or timeout <= 0.0:
            self.log("Rejecting landing goal: timeout must be finite and positive.")
            return False

        if not self._start_client.service_is_ready():
            self.log(f"Rejecting landing goal: {self._start_service} unavailable.")
            return False
        if not self._abort_client.service_is_ready():
            self.log(f"Rejecting landing goal: {self._abort_service} unavailable.")
            return False

        if self._status is None or not self._status_is_fresh():
            topic = self._node.resolve_topic_name(self._status_topic)
            if self._status is None or self._status_received_at is None:
                reason = "no messages received"
            else:
                now = self.now_time
                stamp = self._status.header.stamp
                message_time = stamp.sec + stamp.nanosec * 1e-9
                reason = (
                    f"receipt_age={now - self._status_received_at:.3f}s, "
                    f"header_age={now - message_time:.3f}s, "
                    f"limit={self._max_status_age:.3f}s"
                )
            use_sim_time = bool(self._node.get_parameter("use_sim_time").value)
            self.log(
                f"Rejecting landing goal: no fresh {topic} "
                f"({reason}, use_sim_time={use_sim_time})."
            )
            return False

        if self._status.active or self._status.state_name not in {"IDLE", "LANDED"}:
            self.log(f"Rejecting landing goal: already active in {self._status.state_name}.")
            return False

        self._timeout = timeout
        self._start_future = None
        self._started = False
        self._seen_active = False
        self._abort_future = None
        self._abort_started_at = None
        self._goal_started_at = None
        self._cancel_requested = False
        self.log(f"Accepted landing goal, timeout={self._timeout:.1f}s.")
        return True

    def _on_cancel_received(self) -> bool:
        with self._command_lock:
            # A cancellation before prepare_loop must not start landing later.
            if self._start_future is None:
                self._cancel_requested = True
                return True
            accepted = self._request_abort("Landing action cancelled")
            self._cancel_requested = accepted
            return accepted

    def _prepare_loop(self) -> None:
        with self._command_lock:
            if self._cancel_requested:
                return
            self._goal_started_at = self.now_time
            try:
                self._start_future = self._start_client.call_async(Trigger.Request())
            except Exception as exc:
                self.log(f"Could not request landing start: {exc}")

    def _request_abort(self, reason: str) -> bool:
        """Request abort once; the manager continues its climb/hold independently."""
        if self._abort_started_at is not None:
            return True
        if not self._abort_client.service_is_ready():
            self._node.get_logger().error(f"Cannot abort landing: {self._abort_service} unavailable.")
            return False
        self.log(f"{reason}; requesting abort.")
        try:
            self._abort_future = self._abort_client.call_async(Trigger.Request())
        except Exception as exc:
            self.log(f"Could not request landing abort: {exc}")
            return False
        self._abort_started_at = self.now_time
        self._abort_future.add_done_callback(self._abort_response_callback)
        return True

    def _abort_response_callback(self, future) -> None:
        try:
            response = future.result()
            if response is None or not response.success:
                self.log(f"Landing abort rejected: {response.message if response else 'no response'}")
        except Exception as exc:
            self.log(f"Landing abort service failed: {exc}")

    def _wait_for_abort(self) -> bool | None:
        if self._status_is_fresh() and self._status.state_name == "IDLE":
            if self._abort_future is None or self._abort_future.done():
                self.log("Landing is IDLE after abort.")
                return False
        if self.now_time - self._abort_started_at >= self._abort_timeout:
            self.log("Timed out waiting for landing abort; check landing manager status.")
            return False
        return None

    def _loop_inner(self) -> bool | None:
        if self._abort_started_at is not None:
            return self._wait_for_abort()
        if self._goal_started_at is None or self._start_future is None:
            return False

        elapsed = self.now_time - self._goal_started_at
        if elapsed >= self._timeout:
            with self._command_lock:
                if not self._request_abort(f"Landing timed out after {self._timeout:.1f}s"):
                    return False
            return None

        if not self._started:
            if not self._start_future.done():
                if elapsed >= self._start_timeout:
                    with self._command_lock:
                        if not self._request_abort("Landing start response timed out"):
                            return False
                return None

            try:
                response = self._start_future.result()
            except Exception as exc:
                self.log(f"Landing start service failed: {exc}")
                return False

            if response is None or not response.success:
                self.log(f"Landing start rejected: {response.message if response else 'no response'}")
                return False

            self._started = True
            self.log(response.message)

        # The previous IDLE/LANDED status may still be the latest
        # message when the start service responds, so wait for this attempt first.
        if not self._seen_active:
            if elapsed >= self._start_timeout:
                with self._command_lock:
                    if not self._request_abort("No active status after landing start"):
                        return False
            return None

        if self._status is None or not self._status_is_fresh():
            with self._command_lock:
                if not self._request_abort("Landing status stale"):
                    return False
            return None

        state = self._status.state_name

        if state == "LANDED":
            self.log("Landing completed successfully.")
            return True

        if state in {"ABORT_CLIMB", "ABORT_HOLD"}:
            self._abort_started_at = self.now_time
            return None

        if state == "IDLE":
            self.log("Landing returned to IDLE unexpectedly.")
            return False

        return None

    def _give_feedback(self) -> str:
        if self._status is None:
            return "Waiting for landing status"

        return (
            f"{self._status.state_name} | "
            f"xy={self._status.horizontal_error:.2f}m | "
            f"h={self._status.relative_height:.2f}m | "
            f"vxy={self._status.horizontal_relative_speed:.2f}m/s | "
            f"estimate={'valid' if self._status.estimate_valid else 'invalid'}"
        )


def main(args=None):
    rclpy.init(args=args)

    node = Node("alars_land_action_server")
    executor = MultiThreadedExecutor()
    try:
        land_action = LandAction(node)
        executor.add_node(node)
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
