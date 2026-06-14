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
    """Node-level (non-mission) control tuning constants.

    The follow loop is velocity-matching: command the RPM that yields the
    leader's speed (feed-forward) plus a light along-track position correction
    and a slow trim on measured speed. See README "Control law".
    """
    # Feed-forward: commanded ctrl/rpm_setpoint = rpm_idle + rpm_per_mps*v_target.
    rpm_idle: float
    rpm_per_mps: float
    # Position -> target-speed correction (m/s of extra speed per metre of
    # along-track error beyond the standoff).
    kp_pos: float
    # Slow integral trim on measured speed (rpm per (m/s . s)) + clamp (rpm).
    ki_speed: float
    speed_trim_limit: float
    # Safe RPM while holding / waiting (still subject to the dive floor).
    hold_rpm: float
    # Above this |bearing - heading| a live target is treated as behind/side:
    # hold heading and ease instead of U-turning into the error.
    heading_gate_deg: float
    stale_grace_period: float
    # Dive-floor (depths in m, positive down). The entry->hold switch is
    # relative to the mission depth (see _update_dive_state).
    submersion_min_depth: float   # mission_depth above this => submersion needed.
    dive_depth_tolerance: float   # "at depth" band below mission_depth; also the
                                  # under-dive warn threshold.
    dive_warn_period: float       # under-dive sustained for this long (s) -> warn.
    # Window (s) for least-squares leader-velocity estimation.
    leader_speed_window: float
    control_period: float         # nominal loop period (s), used as dt fallback.


@dataclass
class TuperGoal:
    """Parsed per-mission goal (defaults resolved from node params upstream)."""
    start_lat: float
    start_lon: float
    initial_setpoint_lat: float
    initial_setpoint_lon: float
    mission_depth: float
    min_altitude: float
    min_rpm: float
    max_rpm: float
    # Fail the task if the estimate's measured divergence from truth (the
    # delta_pos topic) exceeds this, regardless of the filter's own covariance.
    max_delta_pos: float
    setpoint_stop_tolerance: float
    setpoint_stop_period: float
    setpoint_stop_speed: float
    arrival_tolerance: float
    final_arrival_tolerance: float
    start_tolerance: float
    timeout: float
    # Velocity-matching / dive-floor knobs (goal-JSON overridable, node fallback).
    # The follow speed is bounded by the RPM limits (min_rpm / max_rpm) above,
    # NOT by an explicit speed clamp.
    standoff_distance: float
    dive_entry_rpm: float


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
    Returns FAILURE on excessive estimate divergence (the measured delta_pos
    error from truth) or on a UKF pose that stays stale beyond the grace period.
    """

    def __init__(self,
                 name: str,
                 node: Node,
                 follower_state: FollowerState,
                 vehicle: Lolo,
                 get_goal,
                 telemetry: dict | None = None):
        super().__init__(name)
        self._node = node
        self._fs = follower_state
        self._vehicle = vehicle
        self._get_goal = get_goal  # Callable[[], TuperGoal | None]
        self._gains: ControlGains | None = None  # set via set_gains()
        # Shared dict the BT node publishes as structured telemetry. Behaviours
        # write control quantities into it each tick.
        self._telemetry = telemetry if telemetry is not None else {}

        self._reset_control_state()

    def set_gains(self, gains: ControlGains) -> None:
        self._gains = gains

    # ------------------------------------------------------ lifecycle
    def _reset_control_state(self) -> None:
        self._speed_trim = 0.0          # slow measured-speed trim (rpm).
        self._last_time = None
        self._stale_since = None
        self._last_bearing = 0.0
        # Latches True once the UKF has EVER been ready (fresh pose AND fresh
        # setpoint together). Onboard-nav bootstrap is only allowed BEFORE this;
        # afterwards a UKF death must fall through to the staleness grace/fail.
        self._ever_ukf_ready = False
        # Whether THIS tick is running on onboard nav (latlon/odom) rather than
        # the UKF. Set every tick in update(); read by the nav-source hooks.
        self._bootstrap = False
        # Dive-floor hysteresis state + under-dive watchdog timer.
        self._submerged = False
        self._under_dive_since = None

    def initialise(self) -> None:
        self._reset_control_state()

    # ------------------------------------------------------ helpers
    @property
    def _now(self) -> float:
        return self._node.get_clock().now().nanoseconds * 1e-9

    def _dt(self) -> float:
        """Loop dt (s), capped so a long hold does not produce a huge step."""
        now = self._now
        if self._last_time is None:
            dt = max(self._gains.control_period, 1e-3)
        else:
            dt = min(max(now - self._last_time, 1e-3), 1.0)
        self._last_time = now
        return dt

    def _safe_hold_rpm(self, goal: TuperGoal) -> float:
        return max(goal.min_rpm, self._gains.hold_rpm)

    def _measured_speed(self) -> float:
        """Forward speed (m/s) from the vehicle odom twist; clamped >= 0."""
        v = getattr(self._vehicle, 'vx', 0.0) or 0.0
        return max(0.0, float(v))

    def _fresh_heading(self) -> float | None:
        """UKF heading only if the pose is fresh (stale heading is useless)."""
        return self._fs.heading_enu if self._fs.pose_fresh else None

    # -- velocity-matching hooks (overridden by the static move-to phase) --
    def _standoff(self, goal: TuperGoal) -> float:
        return goal.standoff_distance

    def _leader_speed(self, goal: TuperGoal) -> float:
        s = self._fs.setpoint_speed(self._gains.leader_speed_window)
        return float(s) if s is not None else 0.0

    def _can_bootstrap(self) -> bool:
        """Whether this phase may run on onboard nav before the UKF is ready."""
        return False

    # -- nav source (UKF vs onboard). Overridden by FollowSetpoint to fall back
    #    to /smarc/latlon + /smarc/odom while bootstrapping toward the
    #    initial_setpoint. Both are freshness-gated at the FollowerState level.
    def _nav_pose_xy(self, goal: TuperGoal) -> tuple[float, float] | None:
        return self._fs.pose_utm

    def _nav_heading(self, goal: TuperGoal) -> float | None:
        return self._fresh_heading()

    def _hold(self, goal: TuperGoal) -> None:
        """Hold heading and command safe hold RPM (still dive-floored)."""
        heading = self._nav_heading(goal)
        yaw = heading if heading is not None else self._last_bearing
        self._speed_trim = 0.0
        self._command(yaw, self._safe_hold_rpm(goal), goal)
        self._telemetry.update({'v_target': 0.0, 'reason': 'hold'})

    def _speed_to_rpm(self, v_target: float, v_meas: float, dt: float,
                      goal: TuperGoal, integrate: bool) -> float:
        """Feed-forward RPM for v_target plus a slow measured-speed trim."""
        gains = self._gains
        rpm_ff = gains.rpm_idle + gains.rpm_per_mps * v_target
        if integrate:
            self._speed_trim += gains.ki_speed * (v_target - v_meas) * dt
            self._speed_trim = max(-gains.speed_trim_limit,
                                   min(gains.speed_trim_limit, self._speed_trim))
        else:
            self._speed_trim = 0.0
        return rpm_ff + self._speed_trim

    def _update_dive_state(self, goal: TuperGoal) -> tuple[float, bool]:
        """Hysteresis dive floor + warn-only under-dive watchdog.

        Returns (rpm_floor, under_dive_flag). LoLo needs a higher RPM to get
        DOWN (dive_entry_rpm); once at depth she holds station at the ordinary
        min_rpm. The switch is relative to the MISSION DEPTH, not a fixed shallow
        threshold: the entry floor stays engaged until she is within
        dive_depth_tolerance of the commanded depth, so the descent is not cut
        short a metre or two down. Hysteresis (a 2*tolerance band) avoids chatter
        around the threshold.
        """
        gains = self._gains
        depth = getattr(self._vehicle, 'depth', 0.0) or 0.0
        submersion_required = goal.mission_depth > gains.submersion_min_depth
        if not submersion_required:
            self._submerged = False
            self._under_dive_since = None
            return goal.min_rpm, False

        band = gains.dive_depth_tolerance
        enter_at = goal.mission_depth - band         # reached cruising depth.
        exit_at = goal.mission_depth - 2.0 * band    # fell out of it (hysteresis).
        if self._submerged:
            if depth < exit_at:
                self._submerged = False
        else:
            if depth >= enter_at:
                self._submerged = True

        # Entry RPM the whole way down (surface -> depth); ordinary min_rpm at depth.
        floor = goal.min_rpm if self._submerged else goal.dive_entry_rpm
        floor = max(goal.min_rpm, floor)

        under_dive = False
        if depth < goal.mission_depth - band:
            now = self._now
            if self._under_dive_since is None:
                self._under_dive_since = now
            elif now - self._under_dive_since > gains.dive_warn_period:
                under_dive = True
                self._node.get_logger().warn(
                    f"({self.name}) Under-diving: depth={depth:.1f}m < target "
                    f"{goal.mission_depth:.1f}m for >{gains.dive_warn_period:.0f}s "
                    f"at rpm-floor={floor:.0f}.", throttle_duration_sec=5.0)
        else:
            self._under_dive_since = None
        return floor, under_dive

    def _command(self, yaw_enu: float, rpm: float, goal: TuperGoal) -> bool:
        self._last_bearing = yaw_enu
        floor, under_dive = self._update_dive_state(goal)
        # Ordinary commands are capped at the mission cruise cap (max_rpm)...
        rpm_cmd = min(float(rpm), goal.max_rpm)
        # ...but the dive-entry floor may BOOST above max_rpm to punch down to
        # depth when the cruise cap alone is too slow to dive. The only hard
        # ceiling is the vehicle's thruster limit (else set_goal would reject).
        hard_max = float(self._vehicle.limits.get('max_thruster_rpm', goal.max_rpm))
        rpm_cmd = max(rpm_cmd, floor)
        rpm_cmd = min(rpm_cmd, hard_max)
        rpm_cmd = max(rpm_cmd, goal.min_rpm)
        ok = self._vehicle.set_goal(
            yaw_enu=float(yaw_enu),
            depth=float(goal.mission_depth),
            altitude=float(goal.min_altitude),
            rpm=float(rpm_cmd),
            timeout=float(min(goal.timeout, 1500.0)),
        )
        if not ok:
            self.feedback_message = "Lolo rejected COURSE goal (check depth/alt/rpm limits)."
            self._node.get_logger().error(
                f"({self.name}) Lolo rejected goal: depth={goal.mission_depth}, "
                f"alt={goal.min_altitude}, rpm={rpm_cmd}",
                throttle_duration_sec=5.0)
            return False
        self._vehicle.update()
        self._telemetry.update({
            'rpm_desired': round(float(rpm), 1),
            'rpm_cmd': round(rpm_cmd, 1),
            'rpm_floor': round(floor, 1),
            'dive_state': 'submerged' if self._submerged else 'surface',
            'under_dive': bool(under_dive),
        })
        return True

    def _drive_toward(self, target_xy: tuple[float, float], goal: TuperGoal,
                      divergence: float) -> float:
        pose_xy = self._nav_pose_xy(goal)
        if pose_xy is None:
            self._hold(goal)
            self.feedback_message = (
                "No onboard nav yet (latlon/odom), holding." if self._bootstrap
                else "No pose available yet, holding.")
            return float('inf')
        de = target_xy[0] - pose_xy[0]
        dn = target_xy[1] - pose_xy[1]
        dist = math.hypot(de, dn)
        bearing = math.atan2(dn, de)
        heading = self._nav_heading(goal)
        if heading is not None:
            heading_err = wrap_angle(bearing - heading)
            forward_error = de * math.cos(heading) + dn * math.sin(heading)
        else:
            heading_err = 0.0
            forward_error = dist

        gains = self._gains
        v_meas = self._measured_speed()
        dt = self._dt()
        standoff = self._standoff(goal)
        v_leader = self._leader_speed(goal)
        # Fixed follow-phase closeness band. We deliberately do NOT widen this on
        # delta_pos: that is the estimate's measured ERROR (a safety trip handled
        # in update()), not its noisiness, so scaling the deadband on it would
        # make her ease off following precisely as the estimate degrades.
        deadband = goal.arrival_tolerance
        turn_needed = (heading is not None and
                       abs(heading_err) > math.radians(gains.heading_gate_deg))

        reason = None
        if dist <= deadband:
            # Inside the arrival deadband: ease to the RPM floor, hold heading,
            # let the dive floor keep her wet. Avoids chasing estimator jitter.
            yaw_cmd = heading if heading is not None else self._last_bearing
            v_target = 0.0
            self._speed_trim = 0.0
            rpm = goal.min_rpm
            reason = "deadband"
        else:
            # Pure pursuit: ALWAYS steer straight at the target. Speed is the
            # leader's speed plus a light along-track correction toward the
            # desired standoff gap, bounded by min/max_rpm in _command.
            #
            # We deliberately do NOT try to "hold heading and wait" when the
            # target is off to the side or behind: LoLo cannot stop (the dive
            # floor keeps her at min_rpm), so any wait-in-place heuristic just
            # makes her motor away from the target forever. The position term
            # uses forward_error (the along-heading projection), which is small
            # or negative while she is still swinging onto the bearing, so
            # v_target naturally collapses to the floor and she comes about
            # nearly in place; once pointed at the target it grows to the
            # leader's speed and she closes the gap.
            yaw_cmd = bearing
            v_target = max(0.0, v_leader + gains.kp_pos * (forward_error - standoff))
            rpm = self._speed_to_rpm(v_target, v_meas, dt, goal, integrate=True)
            if turn_needed:
                reason = "turning"

        self._command(yaw_cmd, rpm, goal)
        self._telemetry.update({
            'dist': round(dist, 1),
            'fwd_err': round(forward_error, 1),
            'heading_err_deg': round(math.degrees(heading_err), 0),
            'v_leader': round(v_leader, 2),
            'v_target': round(v_target, 2),
            'v_meas': round(v_meas, 2),
            'delta_pos': round(divergence, 2),
            'reason': reason,
        })
        self.feedback_message = (
            f"dist={dist:.1f}m hErr={math.degrees(heading_err):.0f}deg "
            f"vL={v_leader:.2f} vT={v_target:.2f} vM={v_meas:.2f} "
            f"rpm={self._telemetry.get('rpm_cmd', 0):.0f} delta_pos={divergence:.2f}m"
            + (f" [{reason}]" if reason else ""))
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

        # The UKF is "ready" only when BOTH the pose and the setpoint are fresh.
        # We latch that: once the UKF has driven control, a later dropout must
        # trip the staleness failure rather than silently fall back to onboard
        # dead-reckoning.
        if self._fs.pose_fresh and self._fs.setpoint_fresh:
            self._ever_ukf_ready = True
        self._bootstrap = self._can_bootstrap() and not self._ever_ukf_ready

        self._telemetry.update({
            'phase': self.name,
            'pose_fresh': self._fs.pose_fresh,
            'setpoint_fresh': self._fs.setpoint_fresh,
            'bootstrap': self._bootstrap,
        })

        if self._bootstrap:
            # Onboard-nav bootstrap: drive toward the initial_setpoint using
            # /smarc/latlon + /smarc/odom (no UKF yet), diving on the way so
            # acoustic comms can come up. No divergence/staleness gating here;
            # we are explicitly operating without the UKF until it shows up.
            self._stale_since = None
            target_xy = self._target(goal)
            if target_xy is None:
                self._hold(goal)
                self.feedback_message = "Bootstrap: no target available, holding."
                return Status.RUNNING
            self._drive_toward(target_xy, goal, divergence=0.0)
            return Status.RUNNING

        # ---- UKF-driven control ----
        # 1. Freshness: a stale UKF pose means we cannot verify safety, so hold
        #    heading at safe hold RPM and run a grace timer before failing.
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

        # 2. Divergence guard. Gate on the MEASURED error of the estimate from
        #    truth (delta_pos), not the filter's self-reported covariance: a
        #    confidently-wrong UKF must still fail the task. A divergence sample
        #    is only published when a truth is available, so when it is absent we
        #    cannot measure drift and keep going (unknown != diverged).
        divergence = self._fs.delta_pos
        if divergence is not None and divergence > goal.max_delta_pos:
            self.feedback_message = (
                f"UKF diverged: delta_pos {divergence:.2f}m > "
                f"{goal.max_delta_pos}m, failing.")
            return Status.FAILURE

        # 3. Determine target.
        target_xy = self._target(goal)
        if target_xy is None:
            self._hold(goal)
            self.feedback_message = "No target available yet, holding."
            return Status.RUNNING

        # 4. Drive, then check exit condition.
        dist = self._drive_toward(
            target_xy, goal, divergence if divergence is not None else 0.0)
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

    def _can_bootstrap(self) -> bool:
        return True

    def _nav_pose_xy(self, goal: TuperGoal) -> tuple[float, float] | None:
        # While bootstrapping (no live UKF) navigate on onboard /smarc/latlon;
        # once the UKF is driving, use its (fresh) pose.
        if self._bootstrap:
            return self._fs.onboard_utm
        return self._fs.pose_utm

    def _nav_heading(self, goal: TuperGoal) -> float | None:
        if self._bootstrap:
            return self._fs.onboard_heading_enu
        return self._fresh_heading()

    def _target(self, goal: TuperGoal) -> tuple[float, float] | None:
        if self._bootstrap:
            # Steer toward the initial setpoint to get LoLo diving / submerged
            # so acoustic comms (and the UKF) can come up.
            return latlon_to_utm(goal.initial_setpoint_lat,
                                 goal.initial_setpoint_lon)
        if self._fs.setpoint_fresh and self._fs.setpoint_utm is not None:
            return self._fs.setpoint_utm
        # UKF was ready but the setpoint dropped out: hold (do not revert to the
        # bootstrap target).
        return None

    def _check_exit(self, goal: TuperGoal, target_xy: tuple[float, float],
                    dist: float) -> Status | None:
        if self._fs.setpoint_stopped(goal.setpoint_stop_tolerance,
                                      goal.setpoint_stop_period,
                                      goal.setpoint_stop_speed):
            self.feedback_message = "Setpoint stopped moving, leaders done."
            return Status.SUCCESS
        return None


class MoveToLastSetpoint(_CourseControlBehaviour):
    """Drive to the last known UKF setpoint and settle within final_arrival_tolerance.

    Captures the last setpoint at initialise() so it does not keep chasing if
    new (post-stop) setpoints trickle in. Stays UKF-consistent because onboard
    nav is unreliable underwater.
    """

    def initialise(self) -> None:
        super().initialise()
        self._target_xy = self._fs.setpoint_utm

    # Static target: no leader to keep pace with, and close all the way in
    # (the standoff gap only makes sense while chasing a moving setpoint).
    def _standoff(self, goal: TuperGoal) -> float:
        return 0.0

    def _leader_speed(self, goal: TuperGoal) -> float:
        return 0.0

    def _target(self, goal: TuperGoal) -> tuple[float, float] | None:
        if self._target_xy is not None:
            return self._target_xy
        # Fallback if we somehow never saw a setpoint.
        return latlon_to_utm(goal.initial_setpoint_lat, goal.initial_setpoint_lon)

    def _check_exit(self, goal: TuperGoal, target_xy: tuple[float, float],
                    dist: float) -> Status | None:
        # Use the (larger) final tolerance, NOT the follow arrival_tolerance:
        # LoLo cannot stop (min_rpm floor) and has a finite turn radius, so she
        # physically cannot settle on a static point - she overruns and orbits.
        # A roomy final tolerance lets her declare arrival on the first pass
        # instead of circling forever.
        if dist <= goal.final_arrival_tolerance:
            self.feedback_message = f"Reached last setpoint (dist={dist:.1f}m)."
            return Status.SUCCESS
        return None
