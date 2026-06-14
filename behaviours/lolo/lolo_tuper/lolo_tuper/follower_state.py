#!/usr/bin/python3
"""Follower state holder for the LoLo TUPER behaviour tree.

This is purely a subscriber/holder: it does NO estimation of its own. It listens
to the follower UKF outputs produced by a separate estimator package and exposes
parsed, control-ready quantities (the analogue of alars' DroneState).

Per the design decision, `/follower/ukf/pose` is the single source of truth for
position, heading and uncertainty; the navsatfix topic is ignored.

All positions are kept in absolute UTM metres (easting=x, northing=y). The pose
topic is already published in the 'utm' frame, and the GeoPoint setpoint is
converted with geodesy.utm, so both live in the same world (assuming a single
UTM zone for the operating area).
"""

import math
from collections import deque

import numpy as np
from geodesy import utm
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import Float32


class FollowerState:
    def __init__(self,
                 node: Node,
                 pose_topic: str,
                 setpoint_topic: str,
                 estimate_max_age: float,
                 odom_topic: str = "smarc/odom",
                 latlon_topic: str = "smarc/latlon",
                 delta_pos_topic: str = "/follower/ukf/delta_pos",
                 stop_window_period: float = 60.0):
        self._node = node
        self._estimate_max_age = float(estimate_max_age)
        # The rolling window keeps a bit more history than any expected
        # setpoint_stop_period so the stop-detector always has enough samples.
        self._stop_window_period = float(stop_window_period)

        self._pose: PoseWithCovarianceStamped | None = None

        # Measured divergence (m) of the UKF estimate from a known truth, as
        # published by the estimator on delta_pos. Unlike the covariance, this
        # is the ACTUAL position error, so a confidently-wrong filter still
        # trips it. Float32 carries no stamp, so we time the reception ourselves.
        self._delta_pos: float | None = None
        self._delta_pos_rx_time: float | None = None

        self._setpoint: GeoPoint | None = None
        self._setpoint_utm: tuple[float, float] | None = None
        self._setpoint_rx_time: float | None = None

        # Rolling deque of (rx_time, x, y) of fresh setpoint receptions.
        self._setpoint_history: deque = deque()

        # --- Onboard navigation (used to bootstrap toward initial_setpoint
        # while there is no live UKF). Position from /smarc/latlon -> UTM,
        # heading from /smarc/odom. The Unity odom frame is translation-only
        # vs UTM (verified from field bags), so the odom quaternion yaw is the
        # same ENU heading the UTM COURSE loop expects.
        self._onboard_utm: tuple[float, float] | None = None
        self._onboard_utm_time: float | None = None
        self._onboard_heading: float | None = None
        self._onboard_heading_time: float | None = None

        self._node.create_subscription(
            PoseWithCovarianceStamped, pose_topic, self._pose_cb, 10)
        self._node.create_subscription(
            GeoPoint, setpoint_topic, self._setpoint_cb, 10)
        self._node.create_subscription(
            Odometry, odom_topic, self._odom_cb, 10)
        self._node.create_subscription(
            GeoPoint, latlon_topic, self._latlon_cb, 10)
        self._node.create_subscription(
            Float32, delta_pos_topic, self._delta_pos_cb, 10)

    # ------------------------------------------------------------------ time
    @property
    def _now(self) -> float:
        return self._node.get_clock().now().nanoseconds * 1e-9

    def set_stop_window_period(self, period: float) -> None:
        """Grow the retained history window if a longer stop period is needed."""
        self._stop_window_period = max(self._stop_window_period, float(period))

    def reset(self) -> None:
        """Clear cached UKF estimates so a new mission cannot reuse stale data.

        Onboard nav (latlon/odom) is intentionally NOT cleared: it is a live,
        continuously-published source and has nothing to do with mission state.
        """
        self._pose = None
        self._setpoint = None
        self._setpoint_utm = None
        self._setpoint_rx_time = None
        self._setpoint_history.clear()
        self._delta_pos = None
        self._delta_pos_rx_time = None

    # -------------------------------------------------------------- callbacks
    def _pose_cb(self, msg: PoseWithCovarianceStamped) -> None:
        self._pose = msg

    def _odom_cb(self, msg: Odometry) -> None:
        q = msg.pose.pose.orientation
        # Standard ENU yaw from a quaternion (x, y, z, w).
        self._onboard_heading = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        self._onboard_heading_time = self._now

    def _latlon_cb(self, msg: GeoPoint) -> None:
        try:
            point = utm.fromMsg(msg).toPoint()
        except Exception as e:  # noqa: BLE001
            self._node.get_logger().warn(
                f"(FollowerState) Failed to convert latlon to UTM: {e}",
                throttle_duration_sec=5.0)
            return
        self._onboard_utm = (float(point.x), float(point.y))
        self._onboard_utm_time = self._now

    def _delta_pos_cb(self, msg: Float32) -> None:
        self._delta_pos = float(msg.data)
        self._delta_pos_rx_time = self._now

    def _setpoint_cb(self, msg: GeoPoint) -> None:
        try:
            utm_point = utm.fromMsg(msg)
            point = utm_point.toPoint()
        except Exception as e:  # noqa: BLE001 - log and ignore bad conversions
            self._node.get_logger().warn(
                f"(FollowerState) Failed to convert setpoint to UTM: {e}")
            return

        now = self._now
        self._setpoint = msg
        self._setpoint_utm = (float(point.x), float(point.y))
        self._setpoint_rx_time = now

        self._setpoint_history.append((now, float(point.x), float(point.y)))
        self._prune_history(now)

    def _prune_history(self, now: float) -> None:
        while (self._setpoint_history and
               now - self._setpoint_history[0][0] > self._stop_window_period):
            self._setpoint_history.popleft()

    # ----------------------------------------------------------------- pose
    @property
    def has_pose(self) -> bool:
        return self._pose is not None

    @property
    def pose_age(self) -> float | None:
        if self._pose is None:
            return None
        stamp = self._pose.header.stamp
        if stamp.sec == 0 and stamp.nanosec == 0:
            return None
        return self._now - (stamp.sec + stamp.nanosec * 1e-9)

    @property
    def pose_fresh(self) -> bool:
        age = self.pose_age
        if age is None:
            return False
        return 0.0 <= age <= self._estimate_max_age

    @property
    def pose_utm(self) -> tuple[float, float] | None:
        # Freshness-gated: a stale pose must NOT leak into the control loop.
        if self._pose is None or not self.pose_fresh:
            return None
        p = self._pose.pose.pose.position
        return (float(p.x), float(p.y))

    @property
    def heading_enu(self) -> float | None:
        """Estimated heading in ENU radians (None when the pose is stale).

        The estimator encodes heading purely in (z, w) of the quaternion
        (orientation about the vertical axis), so yaw = 2*atan2(z, w).
        """
        if self._pose is None or not self.pose_fresh:
            return None
        q = self._pose.pose.pose.orientation
        return 2.0 * math.atan2(q.z, q.w)

    # ------------------------------------------------------------ onboard nav
    @property
    def onboard_utm(self) -> tuple[float, float] | None:
        """Vehicle position in UTM from /smarc/latlon (None if stale/missing)."""
        if self._onboard_utm is None or self._onboard_utm_time is None:
            return None
        if self._now - self._onboard_utm_time > self._estimate_max_age:
            return None
        return self._onboard_utm

    @property
    def onboard_heading_enu(self) -> float | None:
        """Vehicle ENU heading from /smarc/odom (None if stale/missing)."""
        if self._onboard_heading is None or self._onboard_heading_time is None:
            return None
        if self._now - self._onboard_heading_time > self._estimate_max_age:
            return None
        return self._onboard_heading

    @property
    def uncertainty_semimajor(self) -> float | None:
        """1-sigma semi-major axis (m) of the 2x2 position covariance."""
        if self._pose is None:
            return None
        cov = self._pose.pose.covariance
        # Row-major 6x6: [x, y, z, rx, ry, rz]. Position block indices: 0,1,6,7.
        cxx = float(cov[0])
        cxy = float(cov[1])
        cyx = float(cov[6])
        cyy = float(cov[7])
        c = np.array([[cxx, cxy], [cyx, cyy]], dtype=float)
        # Symmetrize to be robust to tiny asymmetries before eigvalsh.
        c = 0.5 * (c + c.T)
        try:
            eigvals = np.linalg.eigvalsh(c)
        except np.linalg.LinAlgError:
            return None
        max_eig = float(max(eigvals[-1], 0.0))
        return math.sqrt(max_eig)

    # --------------------------------------------------------- divergence
    @property
    def delta_pos_age(self) -> float | None:
        if self._delta_pos_rx_time is None:
            return None
        return self._now - self._delta_pos_rx_time

    @property
    def delta_pos_fresh(self) -> bool:
        """True only if a divergence sample arrived within estimate_max_age.

        delta_pos is published only when a known truth (e.g. follower GPS) is
        available, so it can legitimately be absent (deep dives, comms loss).
        Callers must treat 'not fresh' as 'divergence unknown', not as zero.
        """
        age = self.delta_pos_age
        if age is None:
            return False
        return 0.0 <= age <= self._estimate_max_age

    @property
    def delta_pos(self) -> float | None:
        """Latest measured divergence (m) of the estimate from truth, or None.

        Freshness-gated: a stale divergence sample is reported as None so a old
        value cannot mask a current problem (or trip a false failure).
        """
        if self._delta_pos is None or not self.delta_pos_fresh:
            return None
        return self._delta_pos

    # ------------------------------------------------------------- setpoint
    @property
    def has_setpoint(self) -> bool:
        return self._setpoint_utm is not None

    @property
    def setpoint_age(self) -> float | None:
        if self._setpoint_rx_time is None:
            return None
        return self._now - self._setpoint_rx_time

    @property
    def setpoint_fresh(self) -> bool:
        age = self.setpoint_age
        if age is None:
            return False
        return 0.0 <= age <= self._estimate_max_age

    @property
    def setpoint_utm(self) -> tuple[float, float] | None:
        return self._setpoint_utm

    def setpoint_velocity(self, window: float = 5.0) -> tuple[float, float] | None:
        """Estimate the setpoint (leader) velocity in UTM, in m/s.

        Returns (ve, vn) east/north velocity, or None if there are not enough
        fresh samples. A least-squares line is fit to x(t) and y(t) over the
        last `window` seconds, which is robust to the single-sample sideways
        glitches the UKF setpoint exhibits (a least-squares slope ignores
        symmetric outliers far better than a two-point finite difference).
        """
        now = self._now
        self._prune_history(now)

        # A stale setpoint means comms loss, not a known velocity.
        if not self.setpoint_fresh:
            return None

        samples = [s for s in self._setpoint_history if now - s[0] <= window]
        if len(samples) < 3:
            return None

        ts = np.array([s[0] for s in samples], dtype=float)
        # Need a real time span to estimate a slope.
        if ts[-1] - ts[0] < 1e-3:
            return None
        ts = ts - ts[0]
        xs = np.array([s[1] for s in samples], dtype=float)
        ys = np.array([s[2] for s in samples], dtype=float)
        try:
            ve = float(np.polyfit(ts, xs, 1)[0])
            vn = float(np.polyfit(ts, ys, 1)[0])
        except (np.linalg.LinAlgError, ValueError):
            return None
        return (ve, vn)

    def setpoint_speed(self, window: float = 5.0) -> float | None:
        """Scalar leader ground speed (m/s) over the recent window."""
        vel = self.setpoint_velocity(window)
        if vel is None:
            return None
        return math.hypot(vel[0], vel[1])

    # --------------------------------------------------------- stop detection
    def setpoint_stopped(self, tolerance: float, period: float,
                         speed_threshold: float = 0.1) -> bool:
        """True if the leaders' setpoint has genuinely stopped.

        Two conditions must BOTH hold over the last `period` seconds:
          1. the regression (least-squares) leader speed is below
             `speed_threshold` m/s, and
          2. every sample lies within `tolerance` of the window centroid.

        The speed test is the important one: the old centroid-only test was, for
        steady motion, equivalent to a speed threshold of ~2*tolerance/period
        (e.g. 5 m / 30 s ~= 0.33 m/s), so a leader merely cruising slowly around
        a corner tripped a false "stop". Keying on the fitted speed (with a
        threshold well below the leaders' cruise) decouples the two. The
        centroid test stays as a cheap guard against wander/oscillation.

        Requires fresh, continuously-received samples spanning the full period
        so that a comms dropout (no new samples) is NOT mistaken for a stop.
        """
        now = self._now
        self._prune_history(now)

        # Need fresh reception right now; a stale setpoint means comms loss,
        # not a genuine stop.
        if not self.setpoint_fresh:
            return False

        samples = list(self._setpoint_history)
        if len(samples) < 2:
            return False

        # The retained history must reach back far enough, but the exact
        # last-period sample window will almost always be a little shorter than
        # `period` at finite publish rates. Requiring exact span can therefore
        # miss a genuine stop forever.
        window_start = now - period
        if samples[-1][0] - samples[0][0] < period:
            return False

        hist = [s for s in samples if s[0] >= window_start]
        if len(hist) < 2:
            return False

        # Catch dropouts inside the stop window. Include the sample immediately
        # before the window boundary, if any, so a boundary gap is visible.
        prev = next((s for s in reversed(samples) if s[0] < window_start), None)
        gap_hist = ([prev] if prev is not None else []) + hist
        if len(gap_hist) >= 2:
            max_gap = max(gap_hist[i + 1][0] - gap_hist[i][0]
                          for i in range(len(gap_hist) - 1))
            if max_gap > self._estimate_max_age:
                return False

        xs = np.array([s[1] for s in hist], dtype=float)
        ys = np.array([s[2] for s in hist], dtype=float)
        cx = float(xs.mean())
        cy = float(ys.mean())
        max_dist = float(np.max(np.hypot(xs - cx, ys - cy)))
        if max_dist > tolerance:
            return False

        # Speed gate: fit a line over the same period and require a near-zero
        # ground speed. None (too few samples) is treated as "not stopped".
        speed = self.setpoint_speed(period)
        if speed is None:
            return False
        return speed <= speed_threshold
