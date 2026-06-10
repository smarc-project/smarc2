#!/usr/bin/python3
"""Custom py_trees behaviours for the LoLo TUPER mission.

These behaviours implement the UKF-consistent COURSE control loop: bearing to
the target is computed in absolute UTM from the follower pose and the setpoint,
and handed to the Lolo vehicle object as a COURSE goal (yaw_enu) together with a
PID/bang-bang RPM command, the mission depth and the min-altitude floor.

The depth + min-altitude behaviour is delegated to Lolo.control_depth(), which
already implements min(goal.depth, (depth+altitude) - goal.altitude) - i.e. the
exact min-altitude floor used by the cruise-depth-at-heading server.
"""

import math
from dataclasses import dataclass

from geodesy import utm
from geographic_msgs.msg import GeoPoint
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from rclpy.node import Node

from virtual_lolo.lolo import Lolo

from lolo_tuper.follower_state import FollowerState


@dataclass
class ControlGains:
    """Node-level (non-mission) control tuning constants."""
    kp_rpm: float
    ki_rpm: float
    kd_rpm: float
    integral_limit: float
    hold_rpm: float
    heading_gate_deg: float
    uncertainty_deadband_k: float
    stale_grace_period: float
    control_period: float  # nominal loop period (s), used as dt fallback.


@dataclass
class TuperGoal:
    """Parsed per-mission goal."""
    start_lat: float
    start_lon: float
    initial_setpoint_lat: float
    initial_setpoint_lon: float
    mission_depth: float
    min_altitude: float
    min_rpm: float
    max_rpm: float
    max_pos_uncertainty: float
    setpoint_stop_tolerance: float
    setpoint_stop_period: float
    arrival_tolerance: float
    start_tolerance: float
    timeout: float


def latlon_to_utm(lat: float, lon: float) -> tuple[float, float]:
    """Convert lat/lon (deg) to absolute UTM (easting, northing) metres."""
    gp = GeoPoint()
    gp.latitude = float(lat)
    gp.longitude = float(lon)
    gp.altitude = 0.0
    point = utm.fromMsg(gp).toPoint()
    return (float(point.x), float(point.y))


def wrap_angle(a: float) -> float:
    """Wrap an angle to (-pi, pi]."""
    return math.atan2(math.sin(a), math.cos(a))


class _CourseControlBehaviour(Behaviour):
    """Shared base: hold depth/altitude, steer toward a target, modulate RPM.

    Subclasses provide the target (UTM) and the success/exit condition.
    Returns FAILURE on excessive position uncertainty or on a UKF pose that
    stays stale beyond the grace period.
    """

    def __init__(self,
                 name: str,
                 node: Node,
                 follower_state: FollowerState,
                 vehicle: Lolo,
                 get_goal):
        super().__init__(name)
        self._node = node
        self._fs = follower_state
        self._vehicle = vehicle
        self._get_goal = get_goal  # Callable[[], TuperGoal | None]
        self._gains: ControlGains | None = None  # set via set_gains()

        self._reset_control_state()

    def set_gains(self, gains: ControlGains) -> None:
        self._gains = gains

    # ------------------------------------------------------ lifecycle
    def _reset_control_state(self) -> None:
        self._integral = 0.0
        self._last_time = None
        self._last_dist = None
        self._stale_since = None
        self._last_bearing = 0.0

    def initialise(self) -> None:
        self._reset_control_state()

    # ------------------------------------------------------ helpers
    @property
    def _now(self) -> float:
        return self._node.get_clock().now().nanoseconds * 1e-9

    def _safe_hold_rpm(self, goal: TuperGoal) -> float:
        return max(goal.min_rpm, self._gains.hold_rpm)

    def _hold(self, goal: TuperGoal) -> None:
        """Hold heading and command safe hold RPM."""
        heading = self._fs.heading_enu
        yaw = heading if heading is not None else self._last_bearing
        self._command(yaw, self._safe_hold_rpm(goal), goal)

    def _command(self, yaw_enu: float, rpm: float, goal: TuperGoal) -> bool:
        self._last_bearing = yaw_enu
        ok = self._vehicle.set_goal(
            yaw_enu=float(yaw_enu),
            depth=float(goal.mission_depth),
            altitude=float(goal.min_altitude),
            rpm=float(rpm),
            timeout=float(min(goal.timeout, 1500.0)),
        )
        if not ok:
            self.feedback_message = "Lolo rejected COURSE goal (check depth/alt/rpm limits)."
            self._node.get_logger().error(
                f"({self.name}) Lolo rejected goal: depth={goal.mission_depth}, "
                f"alt={goal.min_altitude}, rpm={rpm}",
                throttle_duration_sec=5.0)
            return False
        self._vehicle.update()
        return True

    def _wait_when_target_not_ahead(self) -> bool:
        """True for live-following phases where the setpoint may catch up."""
        return False

    def _compute_rpm(self, dist: float, forward_error: float,
                     heading_err: float, uncertainty: float,
                     goal: TuperGoal) -> tuple[float, str | None]:
        gains = self._gains
        now = self._now
        if self._last_time is None:
            dt = max(gains.control_period, 1e-3)
        else:
            dt = max(now - self._last_time, 1e-3)

        tracking_error = max(0.0, forward_error)
        if self._last_dist is None:
            error_dot = 0.0
        else:
            error_dot = (tracking_error - self._last_dist) / dt

        deadband = max(goal.arrival_tolerance,
                       gains.uncertainty_deadband_k * uncertainty)

        hold_reason = None
        if dist <= deadband:
            hold_reason = "deadband"
        elif self._wait_when_target_not_ahead() and tracking_error <= deadband:
            hold_reason = "target_not_ahead"

        if hold_reason is not None:
            # For live setpoint following, do not turn toward side/behind
            # targets. Keep only the safe forward RPM needed for depth control.
            self._integral = 0.0
            self._last_time = now
            self._last_dist = None
            return self._safe_hold_rpm(goal), hold_reason

        if (not self._wait_when_target_not_ahead() and
                abs(heading_err) > math.radians(gains.heading_gate_deg)):
            # Static-target phases still need some flow over the rudder to turn.
            self._integral = 0.0
            rpm = goal.min_rpm
        else:
            self._integral += tracking_error * dt
            i_term = gains.ki_rpm * self._integral
            i_term = max(-gains.integral_limit, min(gains.integral_limit, i_term))
            rpm = (goal.min_rpm
                   + gains.kp_rpm * tracking_error
                   + i_term
                   + gains.kd_rpm * max(error_dot, 0.0))

        rpm = max(goal.min_rpm, min(goal.max_rpm, rpm))

        self._last_time = now
        self._last_dist = tracking_error
        return rpm, None

    def _drive_toward(self, target_xy: tuple[float, float], goal: TuperGoal,
                      uncertainty: float) -> float:
        pose_xy = self._fs.pose_utm
        de = target_xy[0] - pose_xy[0]
        dn = target_xy[1] - pose_xy[1]
        dist = math.hypot(de, dn)
        bearing = math.atan2(dn, de)
        heading = self._fs.heading_enu
        heading_err = wrap_angle(bearing - heading) if heading is not None else 0.0
        forward_error = (de * math.cos(heading) + dn * math.sin(heading)
                         if heading is not None else dist)

        rpm, hold_reason = self._compute_rpm(
            dist, forward_error, heading_err, uncertainty, goal)
        yaw_cmd = heading if hold_reason is not None and heading is not None else bearing
        self._command(yaw_cmd, rpm, goal)
        hold_str = f" hold={hold_reason}" if hold_reason is not None else ""
        self.feedback_message = (
            f"dist={dist:.1f}m hErr={math.degrees(heading_err):.0f}deg "
            f"rpm={rpm:.0f} sigma={uncertainty:.2f}m "
            f"fwd={forward_error:.1f}m{hold_str}")
        return dist

    # ------------------------------------------------------ subclass hooks
    def _target(self, goal: TuperGoal) -> tuple[float, float] | None:
        raise NotImplementedError

    def _check_exit(self, goal: TuperGoal, target_xy: tuple[float, float],
                    dist: float) -> Status | None:
        raise NotImplementedError

    # ------------------------------------------------------ main tick
    def update(self) -> Status:
        # py_trees tick callback for the custom control phases (Follow / MoveToLast).
        # Called once per BT tick; returns RUNNING to keep the phase going,
        # SUCCESS to advance the mission Sequence, or FAILURE to abort the task.
        goal = self._get_goal()
        if goal is None or self._gains is None:
            self.feedback_message = "No goal/gains set."
            return Status.FAILURE

        # 1. Freshness: if the UKF pose is stale we cannot verify safety, so we
        #    hold heading at safe hold RPM and start a grace timer; fail if it lasts.
        if not self._fs.pose_fresh:
            self._hold(goal)
            if self._stale_since is None:
                self._stale_since = self._now
            stale_for = self._now - self._stale_since
            self.feedback_message = f"UKF pose stale for {stale_for:.1f}s, holding."
            if stale_for > self._gains.stale_grace_period:
                self.feedback_message = "UKF pose stale beyond grace period, failing."
                return Status.FAILURE
            return Status.RUNNING
        self._stale_since = None

        # 2. Uncertainty guard.
        uncertainty = self._fs.uncertainty_semimajor
        if uncertainty is None or uncertainty > goal.max_pos_uncertainty:
            self.feedback_message = (
                f"Position uncertainty {uncertainty} > "
                f"{goal.max_pos_uncertainty}m, failing.")
            return Status.FAILURE

        # 3. Determine target.
        target_xy = self._target(goal)
        if target_xy is None:
            self._hold(goal)
            self.feedback_message = "No target available yet, holding."
            return Status.RUNNING

        # 4. Drive, then check exit condition.
        dist = self._drive_toward(target_xy, goal, uncertainty)
        exit_status = self._check_exit(goal, target_xy, dist)
        if exit_status is not None:
            return exit_status
        return Status.RUNNING

    def terminate(self, new_status: Status) -> None:
        # Stop issuing course goals when we leave this behaviour.
        if new_status in (Status.SUCCESS, Status.FAILURE, Status.INVALID):
            self._vehicle.reset_goal()


class FollowSetpoint(_CourseControlBehaviour):
    """Follow the live UKF setpoint until the leaders' setpoint stops moving.

    Bootstraps toward the goal's initial_setpoint until a fresh UKF setpoint is
    available. Succeeds when the setpoint has stayed within
    setpoint_stop_tolerance for setpoint_stop_period.
    """

    def _wait_when_target_not_ahead(self) -> bool:
        return True

    def _target(self, goal: TuperGoal) -> tuple[float, float] | None:
        if self._fs.setpoint_fresh and self._fs.setpoint_utm is not None:
            return self._fs.setpoint_utm
        # Bootstrap toward the initial setpoint until acoustic comms produce a
        # live UKF setpoint.
        return latlon_to_utm(goal.initial_setpoint_lat, goal.initial_setpoint_lon)

    def _check_exit(self, goal: TuperGoal, target_xy: tuple[float, float],
                    dist: float) -> Status | None:
        if self._fs.setpoint_stopped(goal.setpoint_stop_tolerance,
                                      goal.setpoint_stop_period):
            self.feedback_message = "Setpoint stopped moving, leaders done."
            return Status.SUCCESS
        return None


class MoveToLastSetpoint(_CourseControlBehaviour):
    """Drive to the last known UKF setpoint and settle within arrival_tolerance.

    Captures the last setpoint at initialise() so it does not keep chasing if
    new (post-stop) setpoints trickle in. Stays UKF-consistent because onboard
    nav is unreliable underwater.
    """

    def initialise(self) -> None:
        super().initialise()
        self._target_xy = self._fs.setpoint_utm

    def _target(self, goal: TuperGoal) -> tuple[float, float] | None:
        if self._target_xy is not None:
            return self._target_xy
        # Fallback if we somehow never saw a setpoint.
        return latlon_to_utm(goal.initial_setpoint_lat, goal.initial_setpoint_lon)

    def _check_exit(self, goal: TuperGoal, target_xy: tuple[float, float],
                    dist: float) -> Status | None:
        if dist <= goal.arrival_tolerance:
            self.feedback_message = f"Reached last setpoint (dist={dist:.1f}m)."
            return Status.SUCCESS
        return None
