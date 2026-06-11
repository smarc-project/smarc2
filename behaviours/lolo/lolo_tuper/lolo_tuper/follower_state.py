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
from rclpy.node import Node


class FollowerState:
    def __init__(self,
                 node: Node,
                 pose_topic: str,
                 setpoint_topic: str,
                 estimate_max_age: float,
                 stop_window_period: float = 60.0):
        self._node = node
        self._estimate_max_age = float(estimate_max_age)
        # The rolling window keeps a bit more history than any expected
        # setpoint_stop_period so the stop-detector always has enough samples.
        self._stop_window_period = float(stop_window_period)

        self._pose: PoseWithCovarianceStamped | None = None

        self._setpoint: GeoPoint | None = None
        self._setpoint_utm: tuple[float, float] | None = None
        self._setpoint_rx_time: float | None = None

        # Rolling deque of (rx_time, x, y) of fresh setpoint receptions.
        self._setpoint_history: deque = deque()

        self._node.create_subscription(
            PoseWithCovarianceStamped, pose_topic, self._pose_cb, 10)
        self._node.create_subscription(
            GeoPoint, setpoint_topic, self._setpoint_cb, 10)

    # ------------------------------------------------------------------ time
    @property
    def _now(self) -> float:
        return self._node.get_clock().now().nanoseconds * 1e-9

    def set_stop_window_period(self, period: float) -> None:
        """Grow the retained history window if a longer stop period is needed."""
        self._stop_window_period = max(self._stop_window_period, float(period))

    # -------------------------------------------------------------- callbacks
    def _pose_cb(self, msg: PoseWithCovarianceStamped) -> None:
        self._pose = msg

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
        if self._pose is None:
            return None
        p = self._pose.pose.pose.position
        return (float(p.x), float(p.y))

    @property
    def heading_enu(self) -> float | None:
        """Estimated heading in ENU radians.

        The estimator encodes heading purely in (z, w) of the quaternion
        (orientation about the vertical axis), so yaw = 2*atan2(z, w).
        """
        if self._pose is None:
            return None
        q = self._pose.pose.pose.orientation
        return 2.0 * math.atan2(q.z, q.w)

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
    def setpoint_stopped(self, tolerance: float, period: float) -> bool:
        """True if the setpoint has stayed within `tolerance` for `period` s.

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
        return max_dist <= tolerance
