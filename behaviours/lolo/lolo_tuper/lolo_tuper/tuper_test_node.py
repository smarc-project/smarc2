#!/usr/bin/python3
"""Test/faker node for the LoLo TUPER behaviour tree.

Purpose: let you dry-run the tuper mission in sim WITHOUT the real acoustic UKF.
It fakes the two estimator outputs the BT consumes:

  * /follower/ukf/pose      (PoseWithCovarianceStamped, frame 'utm')
  * /follower/ukf/setpoint  (GeoPoint)
  * /follower/ukf/delta_pos (std_msgs/Float32) - measured divergence of the
    faked pose from the (known) truth, so the BT's divergence-failure path can
    be exercised in sim. The pose jumps (enable_pose_jumps) drive this up.

Behaviour:
  1. Do nothing for `warmup_seconds` (default 30 s).
  2. Then fake the follower pose by tracking /lolo/smarc/odom from an absolute
     UTM anchor captured at activation, plus an integrated (random-walk) noise,
     with heading taken from /lolo/smarc/odom. This is what makes the closed
     loop work: as the BT drives LoLo, the fake pose tracks it.
  3. At the same time, move a fake setpoint smoothly along a trajectory defined
     by a list of vertices, at 0.5-0.8 m/s, slowing down around corners, with
     occasional sideways "jumps" and along-track "runaway/snap-back" glitches to
     mimic the jumpiness of a real UKF estimate. When the trajectory finishes,
     the setpoint holds at the last vertex (so the BT's stop-detector fires).

NOTE on position source: the pose the BT expects is in ABSOLUTE UTM. We capture
the vehicle's UTM position ONCE at activation (from /lolo/smarc/latlon) as an
anchor, then integrate /lolo/smarc/odom displacement on top of it. We use odom
(not the live latlon) for the displacement because in the SMARC sim the latlon
is published through a Web-Mercator georeference that compresses ground motion
by ~sec(latitude) (~1.9x at Asko), making the fake pose crawl at half the true
hull speed. odom tracks the real hull motion and matches /lolo/smarc/speed, so
the closed loop behaves realistically. odom is also used for the heading. Both
topics are configurable below.
"""

import math
import sys

import numpy as np
from geodesy import utm as geo_utm
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.parameter import Parameter
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Float32
from tf_transformations import euler_from_quaternion


# --------------------------------------------------------------------------- #
# Smooth trajectory through vertices (Catmull-Rom) with per-sample curvature so
# we can slow down around corners.
# --------------------------------------------------------------------------- #
class _TestTrajectory:
    def __init__(self, points_xy: np.ndarray, samples_per_segment: int = 60):
        pts = np.asarray(points_xy, dtype=float)
        if pts.shape[0] < 2:
            raise ValueError("Need at least 2 vertices for a trajectory.")

        # Duplicate endpoints so Catmull-Rom passes through the first/last vertex.
        padded = np.vstack([pts[0], pts, pts[-1]])
        dense = []
        for i in range(1, len(padded) - 2):
            p0, p1, p2, p3 = padded[i - 1], padded[i], padded[i + 1], padded[i + 2]
            for t in np.linspace(0.0, 1.0, samples_per_segment, endpoint=False):
                dense.append(self._catmull_rom(p0, p1, p2, p3, t))
        dense.append(pts[-1])
        self.pts = np.asarray(dense, dtype=float)

        # Arc length parameterisation.
        seg = np.linalg.norm(np.diff(self.pts, axis=0), axis=1)
        self.s = np.concatenate([[0.0], np.cumsum(seg)])
        self.total_length = float(self.s[-1])

        # Tangent heading and curvature (|dtheta/ds|) per sample, smoothed so a
        # corner influences a broad neighbourhood.
        diffs = np.diff(self.pts, axis=0)
        theta = np.arctan2(diffs[:, 1], diffs[:, 0])
        theta = np.concatenate([theta, [theta[-1]]])  # match pts length
        dtheta = np.abs(np.diff(np.unwrap(theta)))
        ds = np.maximum(seg, 1e-6)
        kappa = np.concatenate([dtheta / ds, [0.0]])
        self.kappa = self._smooth(kappa, win=max(3, samples_per_segment // 4))
        self.theta = theta

    @staticmethod
    def _catmull_rom(p0, p1, p2, p3, t):
        t2 = t * t
        t3 = t2 * t
        return 0.5 * ((2 * p1)
                      + (-p0 + p2) * t
                      + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                      + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)

    @staticmethod
    def _smooth(arr, win):
        if win <= 1 or arr.size <= win:
            return arr
        kernel = np.ones(win) / win
        return np.convolve(arr, kernel, mode='same')

    def sample(self, s: float, speed_min: float, speed_max: float,
               curvature_ref: float):
        """Return (point_xy, tangent_angle, speed) at arc length s."""
        s = float(np.clip(s, 0.0, self.total_length))
        idx = int(np.searchsorted(self.s, s))
        idx = max(1, min(idx, len(self.s) - 1))
        s0, s1 = self.s[idx - 1], self.s[idx]
        frac = 0.0 if s1 <= s0 else (s - s0) / (s1 - s0)
        point = self.pts[idx - 1] + frac * (self.pts[idx] - self.pts[idx - 1])
        kappa = self.kappa[idx - 1]
        theta = self.theta[idx - 1]
        # straightness in [0,1]: 1 = straight (speed_max), 0 = sharp (speed_min)
        straightness = 1.0 / (1.0 + kappa / max(curvature_ref, 1e-6))
        speed = speed_min + (speed_max - speed_min) * straightness
        return point, theta, speed


class TuperTestNode(Node):
    def __init__(self):
        super().__init__('tuper_test_node')

        self._declare_params()

        self._rng = np.random.default_rng()

        # State.
        self._truth_latlon = None       # (lat, lon) from /smarc/latlon
        self._odom_yaw = None           # ENU yaw from /smarc/odom
        self._odom_xy = None            # (x, y) position from /smarc/odom
        self._utm_anchor = None         # absolute UTM (e, n) captured at activation
        self._odom_xy0 = None           # odom (x, y) captured at activation
        self._start_time = self._now
        self._active = False
        self._traj: _TestTrajectory | None = None
        self._zone = None
        self._band = None

        # Pose integrated-noise (random walk with slight mean reversion).
        self._pose_noise = np.zeros(2)

        # Glitches in UKF pose estimate
        self._pose_jump_offset = np.zeros(2)
        self._pose_jump_mag = np.zeros(2)
        self._pose_jump_start = 0.0
        self._next_pose_jump_time = self._start_time + self._warmup + self._pose_jump_period

        # Setpoint progression + glitch state.
        self._s = 0.0
        self._finished = False
        self._glitch_offset = np.zeros(2)
        self._glitch_start = 0.0
        self._glitch_mag = np.zeros(2)
        self._next_glitch_time = self._start_time + self._warmup + self._jump_period
        self._speed_factor = 1.0  # OU jitter on base speed

        # I/O.
        self.create_subscription(GeoPoint, self._latlon_topic,
                                 self._latlon_cb, 10)
        self.create_subscription(Odometry, self._odom_topic, self._odom_cb, 10)
        self._pose_pub = self.create_publisher(
            PoseWithCovarianceStamped, self._pose_topic, 10)
        self._setpoint_pub = self.create_publisher(
            GeoPoint, self._setpoint_topic, 10)
        self._delta_pos_pub = self.create_publisher(
            Float32, self._delta_pos_topic, 10)

        self._dt = 1.0 / max(self._publish_rate, 1e-3)
        self.create_timer(self._dt, self._tick)

        self.get_logger().info(
            f"tuper_test_node up. Faking after {self._warmup:.0f}s warmup. "
            f"pose->{self._pose_topic}, setpoint->{self._setpoint_topic}")

    # ------------------------------------------------------------- params
    def _declare_params(self):
        d = self.declare_parameter

        self._warmup = float(d('warmup_seconds', 30.0).value)
        self._publish_rate = float(d('publish_rate', 10.0).value)

        self._latlon_topic = d('latlon_topic', '/lolo/smarc/latlon').value
        self._odom_topic = d('odom_topic', '/lolo/smarc/odom').value
        self._pose_topic = d('pose_topic', '/follower/ukf/pose').value
        self._setpoint_topic = d('setpoint_topic', '/follower/ukf/setpoint').value
        self._delta_pos_topic = d('delta_pos_topic', '/follower/ukf/delta_pos').value
        self._ahead_distance_m = float(d('ahead_distance_m', 15.0).value)

        # Pose integrated noise (random walk: n <- (1-theta)*n + sigma*N(0,1)).
        self._pose_noise_sigma = float(d('pose_noise_sigma', 0.05).value)
        self._pose_noise_theta = float(d('pose_noise_theta', 0.01).value)
        # Reported 1-sigma (m) that becomes the pose covariance the BT gates on.
        self._reported_sigma = float(d('reported_sigma', 1.0).value)

        # Pose estimate jumps: simulates the UKF briefly estimating the wrong position.
        self._enable_pose_jumps = bool(d('enable_pose_jumps', True).value)
        self._pose_jump_period = float(d('pose_jump_period_s', 2.0).value)
        self._pose_jump_std = float(d('pose_jump_std', 1.5).value)
        self._pose_jump_decay_s = float(d('pose_jump_decay_s', 1.0).value)

        # Trajectory vertices.
        #   vertices_frame: 'relative' -> (east, north) metres from the vehicle's
        #                   position captured when faking starts.
        #                   'latlon'  -> absolute (latitude, longitude) degrees.
        self._vertices_frame = d('vertices_frame', 'relative').value

        # IMPORTANT:
        # Do not declare empty array defaults with [] in rclpy. An empty Python
        # list is inferred as BYTE_ARRAY, so YAML overrides like
        # vertices_lat: [58.8, 58.9] later fail with:
        # "DOUBLE_ARRAY, expecting BYTE_ARRAY".
        #
        # For parameters that may legitimately default to an empty list, declare
        # the parameter using Parameter.Type.DOUBLE_ARRAY instead. If the YAML
        # file supplies values, rclpy accepts them as a double array; if not, the
        # value remains unset/None and we return the requested Python default.
        def declare_double_array(name: str, default: list[float]) -> list[float]:
            default = [float(x) for x in default]
            if default:
                return list(d(name, default).value or [])

            self.declare_parameter(name, Parameter.Type.DOUBLE_ARRAY)
            value = self.get_parameter(name).value
            return list(value) if value is not None else []

        self._vertices_a = declare_double_array(
            'vertices_east', [0.0, 30.0, 60.0, 60.0])
        self._vertices_b = declare_double_array(
            'vertices_north', [0.0, 0.0, 30.0, 60.0])
        self._vertices_lat = declare_double_array('vertices_lat', [])
        self._vertices_lon = declare_double_array('vertices_lon', [])

        # Setpoint motion.
        self._speed_min = float(d('speed_min', 0.5).value)
        self._speed_max = float(d('speed_max', 0.8).value)
        self._curvature_ref = float(d('corner_curvature_ref', 0.15).value)
        self._speed_jitter = float(d('speed_jitter', 0.08).value)
        self._loop_trajectory = bool(d('loop_trajectory', False).value)

        # Glitches ("jumpy UKF": sideways jumps + along-track runaway/snap-back).
        self._enable_trajectory_jumps = bool(d('enable_trajectory_jumps', True).value)
        self._jump_period = float(d('jump_period_s', 2.0).value)
        self._jump_lateral_std = float(d('jump_lateral_std', 1.5).value)
        self._jump_along_std = float(d('jump_along_std', 1.5).value)
        self._jump_decay_s = float(d('jump_decay_s', 0.6).value)

    # ------------------------------------------------------------- helpers
    @property
    def _now(self) -> float:
        return self.get_clock().now().nanoseconds * 1e-9

    def _latlon_cb(self, msg: GeoPoint):
        self._truth_latlon = (msg.latitude, msg.longitude)

    def _odom_cb(self, msg: Odometry):
        q = msg.pose.pose.orientation
        _, _, yaw = euler_from_quaternion([q.x, q.y, q.z, q.w])
        self._odom_yaw = yaw
        p = msg.pose.pose.position
        self._odom_xy = (p.x, p.y)

    def _latlon_to_utm(self, lat, lon):
        gp = GeoPoint()
        gp.latitude = float(lat)
        gp.longitude = float(lon)
        gp.altitude = 0.0
        p = geo_utm.fromMsg(gp)
        return p

    # ------------------------------------------------------------- activation
    def _try_activate(self) -> bool:
        if self._truth_latlon is None:
            self.get_logger().warn(
                f"Warmup done but no truth position on {self._latlon_topic} yet; "
                "waiting before faking.", throttle_duration_sec=5.0)
            return False
        if self._odom_yaw is None or self._odom_xy is None:
            self.get_logger().warn(
                f"Warmup done but no odom on {self._odom_topic} yet; "
                "waiting before faking.", throttle_duration_sec=5.0)
            return False

        origin = self._latlon_to_utm(*self._truth_latlon)
        self._zone = origin.zone
        self._band = origin.band

        # Anchor the fake pose: absolute UTM position now, and the odom position
        # now. The pose is then anchor_utm + (odom - odom0), so it tracks the
        # real hull motion (odom) while staying in absolute UTM.
        self._utm_anchor = (origin.easting, origin.northing)
        self._odom_xy0 = self._odom_xy

        # Anchor the fake trajectory ahead of the current vehicle pose so the
        # first setpoint starts in front of LoLo instead of beside/behind it.
        origin_easting = origin.easting + self._ahead_distance_m * math.cos(self._odom_yaw)
        origin_northing = origin.northing + self._ahead_distance_m * math.sin(self._odom_yaw)

        if self._vertices_frame == 'latlon':
            if len(self._vertices_lat) < 2 or \
               len(self._vertices_lat) != len(self._vertices_lon):
                self.get_logger().error(
                    "vertices_frame='latlon' needs matching vertices_lat / "
                    "vertices_lon of length >= 2. Setpoint disabled.")
                return False
            xy = []
            for la, lo in zip(self._vertices_lat, self._vertices_lon):
                p = self._latlon_to_utm(la, lo)
                xy.append([p.easting, p.northing])
            points = np.asarray(xy)
        else:  # 'relative'
            if len(self._vertices_a) < 2 or \
               len(self._vertices_a) != len(self._vertices_b):
                self.get_logger().error(
                    "vertices_frame='relative' needs matching vertices_east / "
                    "vertices_north of length >= 2. Setpoint disabled.")
                return False
            points = np.column_stack([
                origin_easting + np.asarray(self._vertices_a, dtype=float),
                origin_northing + np.asarray(self._vertices_b, dtype=float),
            ])

        try:
            self._traj = _TestTrajectory(points)
        except ValueError as e:
            self.get_logger().error(f"Trajectory build failed: {e}")
            return False

        self.get_logger().info(
            f"Faking started. Trajectory length {self._traj.total_length:.1f} m "
            f"over {points.shape[0]} vertices ({self._vertices_frame}).")
        return True

    # ------------------------------------------------------------- main tick
    def _tick(self):
        elapsed = self._now - self._start_time
        if elapsed < self._warmup:
            self.get_logger().info(
                f"tuper_test warmup: {self._warmup - elapsed:.0f}s left...",
                throttle_duration_sec=5.0)
            return

        if not self._active:
            if not self._try_activate():
                return
            self._active = True
            self._next_glitch_time = self._now + self._sample_glitch_interval()

        self._publish_pose()
        if self._traj is not None:
            self._publish_setpoint()

    # ------------------------------------------------------------- pose
    def _publish_pose(self):
        if self._utm_anchor is None or self._odom_xy0 is None \
                or self._odom_xy is None:
            return
        # Track odom displacement from the absolute UTM anchor (odom is
        # direction-aligned with UTM and reflects the true hull speed; the live
        # latlon is Web-Mercator-compressed in sim, see module docstring).
        truth_e = self._utm_anchor[0] + (self._odom_xy[0] - self._odom_xy0[0])
        truth_n = self._utm_anchor[1] + (self._odom_xy[1] - self._odom_xy0[1])

        # Integrated (random-walk) noise with mild mean reversion.
        self._pose_noise = ((1.0 - self._pose_noise_theta) * self._pose_noise
                            + self._pose_noise_sigma * self._rng.standard_normal(2))

        now = self._now
        if self._enable_pose_jumps:
            # Sometimes wrong-estimate jump
            if now >= self._next_pose_jump_time:
                angle = self._rng.uniform(0.0, 2.0 * math.pi)
                mag = abs(self._rng.normal(0.0, self._pose_jump_std))
                self._pose_jump_mag = mag * np.array([
                    math.cos(angle),
                    math.sin(angle)
                ])
                self._pose_jump_start = now
                self._next_pose_jump_time = now + self._sample_jump_interval()

            # Decay jump back to zero, like the estimator snapping back.
            age = now - self._pose_jump_start
            decay = max(0.0, 1.0 - age / max(self._pose_jump_decay_s, 1e-3))
            self._pose_jump_offset = self._pose_jump_mag * decay
        else:
            self._pose_jump_offset = np.zeros(2)

        px = truth_e + self._pose_noise[0] + self._pose_jump_offset[0]
        py = truth_n + self._pose_noise[1] + self._pose_jump_offset[1]

        msg = PoseWithCovarianceStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'utm'
        msg.pose.pose.position.x = float(px)
        msg.pose.pose.position.y = float(py)
        msg.pose.pose.position.z = 0.0

        yaw = self._odom_yaw if self._odom_yaw is not None else 0.0
        msg.pose.pose.orientation.z = math.sin(yaw / 2.0)
        msg.pose.pose.orientation.w = math.cos(yaw / 2.0)

        var = self._reported_sigma ** 2
        cov = [0.0] * 36
        cov[0] = var      # xx
        cov[7] = var      # yy
        cov[14] = 1e6     # zz unknown
        cov[21] = 1e6     # rot x
        cov[28] = 1e6     # rot y
        cov[35] = 1e6     # rot z
        msg.pose.covariance = cov
        self._pose_pub.publish(msg)

        # Measured divergence of the faked estimate from the (known) truth, in
        # metres. This is what the BT now gates on instead of the covariance, so
        # a wrong-but-confident pose jump still trips the divergence failure.
        delta = math.hypot(px - truth_e, py - truth_n)
        self._delta_pos_pub.publish(Float32(data=float(delta)))

    # ------------------------------------------------------------- setpoint
    def _sample_glitch_interval(self) -> float:
        # Poisson-ish spacing around the mean jump period.
        return float(self._rng.exponential(max(self._jump_period, 0.1)))
    
    def _sample_jump_interval(self) -> float:
        # Poisson-ish spacing around the mean jump period.
        return float(self._rng.exponential(max(self._pose_jump_period, 0.1)))

    def _publish_setpoint(self):
        now = self._now

        # Base smooth motion along the trajectory.
        point, theta, base_speed = self._traj.sample(
            self._s, self._speed_min, self._speed_max, self._curvature_ref)

        if self._enable_trajectory_jumps and not self._finished:
            # Gentle OU jitter on speed, kept within [speed_min, speed_max].
            self._speed_factor += (-0.1 * (self._speed_factor - 1.0)
                                   + self._speed_jitter * self._rng.standard_normal())
            speed = float(np.clip(base_speed * self._speed_factor,
                                  self._speed_min, self._speed_max))
            self._s += speed * self._dt

            if self._s >= self._traj.total_length:
                if self._loop_trajectory:
                    self._s = 0.0
                else:
                    self._s = self._traj.total_length
                    self._finished = True
                    self.get_logger().info(
                        "Trajectory finished; setpoint now holding at last "
                        "vertex (stop-detector should fire).")

        # Glitches: only while moving. When finished, hold steady so the BT can
        # detect that the setpoint has stopped.
        if not self._finished:
            if now >= self._next_glitch_time:
                tangent = np.array([math.cos(theta), math.sin(theta)])
                normal = np.array([-tangent[1], tangent[0]])
                lateral = self._rng.normal(0.0, self._jump_lateral_std)
                along = self._rng.normal(0.0, self._jump_along_std)  # runaway/snap-back
                self._glitch_mag = lateral * normal + along * tangent
                self._glitch_start = now
                self._next_glitch_time = now + self._sample_glitch_interval()

            # Decay the glitch offset back to zero ("snap back").
            age = now - self._glitch_start
            decay = max(0.0, 1.0 - age / max(self._jump_decay_s, 1e-3))
            self._glitch_offset = self._glitch_mag * decay
        else:
            self._glitch_offset = np.zeros(2)

        out = point + self._glitch_offset

        up = geo_utm.UTMPoint(easting=float(out[0]), northing=float(out[1]),
                              altitude=0.0, zone=self._zone, band=self._band)
        geo = up.toMsg()
        self._setpoint_pub.publish(geo)


def main():
    rclpy.init(args=sys.argv)
    node = TuperTestNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
