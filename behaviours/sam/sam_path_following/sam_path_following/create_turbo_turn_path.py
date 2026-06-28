"""
Create turbo-turn or on-spot turn trajectory CSVs for SAM path following.

Modes:
  on_spot   - Turn on the spot: fixed position, alternate forward/backward surge
              and rudder angle (horizontal thrust vectoring) to rotate in place.
  three_point - Classic 3-point turn: straight approach, turn off centerline,
                straight back (multiple waypoints for MPC).
  zigzag    - Zigzag path: waypoints on a multi-point pattern with alternating
              heading (forward/backward along path).
"""
import argparse
import os

from scipy.interpolate import CubicSpline, PchipInterpolator

import numpy as np
import pandas as pd

try:
    import matplotlib.pyplot as plt

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def yaw_to_quaternion(yaw):
    """
    Convert yaw angle (rotation around z-axis) to quaternion.

    Args:
        yaw: Yaw angle in radians

    Returns:
        Quaternion as [q0, q1, q2, q3] = [qw, qx, qy, qz]
    """
    q0 = np.cos(yaw / 2.0)
    q1 = 0.0
    q2 = 0.0
    q3 = np.sin(yaw / 2.0)
    return np.array([q0, q1, q2, q3])


def build_on_spot_path(args):
    """
    Build waypoints for turning on the spot: same position, alternate
    forward/backward surge and rudder (horizontal thrust vectoring).
    """
    N = args.n_waypoints
    total_yaw_rad = np.deg2rad(args.total_yaw_deg)
    cx, cy, cz = args.center_x, args.center_y, args.center_z
    surge = args.surge_speed
    rudder_deg = args.rudder_angle_deg
    rudder_rad = np.deg2rad(rudder_deg)

    # Position constant at center
    x = np.full(N, cx)
    y = np.full(N, cy)
    z = np.full(N, cz)

    # Yaw: linear progression from 0 to total_yaw_rad (turn in place)
    yaw = np.linspace(0.0, total_yaw_rad, N)

    # Surge: alternate forward / backward
    u_per_wp = np.array([surge if i % 2 == 0 else -surge for i in range(N)])
    u_per_wp[-1] = 0.0  # zero velocity at final WP so the MPC brakes to a stop

    # Rudder: alternate left/right (dr) to support turning while moving fwd/back
    # Positive dr = one side, negative = other (alternate each step)
    dr_per_wp = np.array([
        rudder_rad if i % 2 == 0 else -rudder_rad for i in range(N)
    ])
    dr_per_wp[-1] = 0.0

    return x, y, z, yaw, u_per_wp, dr_per_wp


def build_three_point_turn_path(args):
    """
    Build the classic 3-point turbo-turn: straight, turn off axis, straight back.
    """
    Y_MID_OFFSET = args.y_mid_offset
    turn_sign = 1.0 if Y_MID_OFFSET >= 0 else -1.0

    x = np.array([
        3.0, 4.5, 6.0, 5.5, 4.5, 4.25, 4.05, 3.80, 3.30, 2.55, 2.00
    ])
    y = np.array([
        0.0, 0.0, 0.0, 0.0,
        0.45 * turn_sign, 0.90 * turn_sign, 0.75 * turn_sign, 0.50 * turn_sign,
        0.25 * turn_sign, 0.10 * turn_sign, 0.0,
    ])
    z = np.zeros(len(x))
    yaw = np.array([
        0.0, 0.0, 0.0, 0.0,
        -turn_sign * np.deg2rad(35), -turn_sign * np.deg2rad(90),
        -turn_sign * np.deg2rad(100), -turn_sign * np.deg2rad(110),
        -turn_sign * np.deg2rad(130), -turn_sign * np.deg2rad(155),
        -np.pi,
    ])

    N = len(x)
    SURGE_SPEED = args.surge_speed
    u_per_wp = np.zeros(N)
    for i in range(N):
        if i < N - 1:
            dx = x[i + 1] - x[i]
            dy = y[i + 1] - y[i]
            seg_len = np.hypot(dx, dy)
            if seg_len < 1e-6:
                u_per_wp[i] = u_per_wp[i - 1] if i > 0 else SURGE_SPEED
            else:
                align = dx * np.cos(yaw[i]) + dy * np.sin(yaw[i])
                u_per_wp[i] = SURGE_SPEED if align >= 0 else -SURGE_SPEED
        else:
            u_per_wp[i] = 0.0  # zero velocity at final WP so the MPC brakes
    dr_per_wp = np.zeros(N)  # three_point doesn't set rudder explicitly
    return x, y, z, yaw, u_per_wp, dr_per_wp

def build_three_point_path(args):
    """
    Just three waypoints, start, middle, end.
    """

    # Three point dive
    x = np.array([1.0, 3.0, 6.0])
    y = np.array([0.0, 0.0, 0.0])
    z = np.array([0.0, 0.5, 1.0])
    yaw = np.array([0.0, 0.0, 0.0])

    # Three point 180 turn
    # x = np.array([1.5, 4.0, 0.5])
    # y = np.array([0.0, 1.0, 0.0])
    # z = np.array([0.0, 0.0, 0.0])
    # yaw = np.array([0.0, 0.0, 0.0])

    # Three point turn
    #x = np.array([1.5, 3.5, 2.0])
    #y = np.array([0.0, 0.0, 0.0])
    #z = np.array([0.0, 0.0, 0.0])
    #yaw = np.array([0.0, 0.0, 0.0])

    N = len(x)
    u_per_wp = np.zeros(N)
    dr_per_wp = np.zeros(N)  
    start_point = (0.5, 0.0, 0.0, 0.0)
    x, y, z, yaw, u_per_wp, dr_per_wp = add_starting_point(x, y, z, yaw, u_per_wp, dr_per_wp, start_point)
    return x, y, z, yaw, u_per_wp, dr_per_wp

def build_N_point_path(args):
    """
    Just three waypoints, start, middle, end.
    """

    # Circle
    #x = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 0.5])
    #y = np.array([0.0, 0.5, 1.0, 0.5, 0.0, -0.5, -1.0, -0.5, 0.0, 0.0])
    #z = np.zeros(len(x))
    #yaw = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    # 

    x = np.array([1.5, 2.5, 3.0,  1.5])
    y = np.array([-1.0, 1.0, -1.0, 1.0])
    z = np.zeros(len(x))
    yaw = np.array([0.0, 0.0, 0.0, 0.0])

    N = len(x)
    u_per_wp = np.zeros(N)
    dr_per_wp = np.zeros(N)  
    start_point = (0.5, 0.0, 0.0, 0.0)
    x, y, z, yaw, u_per_wp, dr_per_wp = add_starting_point(x, y, z, yaw, u_per_wp, dr_per_wp, start_point)
    return x, y, z, yaw, u_per_wp, dr_per_wp


def build_zigzag_path(args):
    """
    Build zigzag path: waypoints on a multi-point pattern. AUV starts at (0,0),
    moves forward to wp0, backward to wp1, forward to wp2, etc. Yaw at each
    waypoint increases by alpha_deg from the previous: yaw[i] = i * alpha,
    so the increment between waypoints is exactly the angle you set with
    alpha_deg (and total yaw over the path is (N-1)*alpha_deg).
    """
    N = args.n_waypoints
    radius = args.radius
    alpha_deg = args.alpha_deg
    alpha = np.deg2rad(alpha_deg)

    i = np.arange(N)
    beta = i * alpha + (i % 2) * np.pi
    x = radius * np.cos(beta) + 4.5
    y = radius * np.sin(beta) + 0.0
    z = np.ones(N) * 0.0

    # Yaw: increase by alpha (rad) per waypoint: yaw[i] = i * alpha
    yaw = np.arange(N, dtype=float) * alpha

    # Surge: from wp0 forward to wp1, from wp1 backward to wp2, etc.
    SURGE_SPEED = args.surge_speed
    u_per_wp = np.array(
        [SURGE_SPEED if i % 2 == 0 else -SURGE_SPEED for i in range(N)]
    )
    u_per_wp[-1] = 0.0  # zero velocity at final WP so the MPC brakes to a stop
    dr_per_wp = np.zeros(N)
    start_point = (0.5, 0.0, 0.0, 0.0)
    x, y, z, yaw, u_per_wp, dr_per_wp = add_starting_point(x, y, z, yaw, u_per_wp, dr_per_wp, start_point)
    return x, y, z, yaw, u_per_wp, dr_per_wp

def build_waypoints_path(args):
    """Build a trajectory from user-supplied x,y,z waypoints.

    Waypoints are given as semicolon-separated x,y,z triplets, e.g.
        --wp "0.5,0,0; 1,0,0; 3,0,0.5; 6,0,1"

    Yaw at each waypoint is computed from the XY heading toward the next
    waypoint (last waypoint inherits the previous heading).
    
    Full command:
    python3 create_turbo_turn_path.py --mode waypoints \
    --wp "0.5,0,0; 1,0,0; 3,0,0.75; 6,0,1.5; 2.5, 0, 1.5" \
    -o trajectories/straight_line_s-curve_depth-1.5_return_dive.csv

    gentle straight dive
    python3 create_turbo_turn_path.py --mode waypoints \
    --wp "1.0,0.0,0.0; 2.0,0.0,0.0; 3.0,0.0,0.3; 4.5,0.00,0.8; 5.5,0.00,1.3; 6.0,0.0,1.5" \
    -o trajectories/gentle_straight_dive.csv

    gentle straight dive with return
    python3 create_turbo_turn_path.py --mode waypoints \
    --wp "1.0,0.0,0.0; 2.0,0.0,0.0; 3.0,0.0,0.3; 4.5,0.00,0.8; 5.5,0.00,1.3; 6.0,0.0,1.5; 3.5, 0, 1.5" \
    -o trajectories/gentle_straight_dive_with_return.csv

    steep straight dive
    python3 create_turbo_turn_path.py --mode waypoints \
    --wp "1.0,0.0,0.0; 2.0,0.0,0.0; 3.0,0.0,0.75; 4.0,0.00,1.5; 2.5, 0, 1.5" \
    -o trajectories/steep_straight_dive.csv

    gentle turn dive
    python3 create_turbo_turn_path.py --mode waypoints \
    --wp "1.0,0.0,0.0; 2.0,0.0,0.0; 3.0,0.0,0.3; 4.5,0.5,0.8; 5.5,0.75,1.3; 6.0,1.0,1.5" \
    -o trajectories/gentle_turn_dive.csv

    sharper turn dive (full 90 degree turn)
    python3 create_turbo_turn_path.py --mode waypoints \
    --wp "1.0,0.0,0.0; 2.0,0.0,0.0; 3.0,0.0,0.3; 5.0,0.0,0.8; 5.5,0.0,1.3; 6.0,0.0,1.5; 6.0,1.0,1.5" \
    -o trajectories/sharper_turn_dive.cs    
    
    sharper left turn dive (full 90 degree turn)
    python3 create_turbo_turn_path.py --mode waypoints \
    --wp "1.0,0.0,0.0; 2.0,0.0,0.0; 3.0,0.0,0.3; 5.0,0.0,0.8; 5.5,0.0,1.3; 6.0,0.0,1.5; 6.0,-1.0,1.5" \
    -o trajectories/sharper_left_turn_dive.csv

    sharper turn dive (full 90 degree turn) with small return
    python3 create_turbo_turn_path.py --mode waypoints \
    --wp "1.0,0.0,0.0; 2.0,0.0,0.0; 3.0,0.0,0.3; 5.0,-0.25,0.8; 5.5,-0.25,1.3; 6.0,0.0,1.5; 6.0,1.0,1.5; 5.5, 1.5, 1.5" \
    -o trajectories/sharper_turn_dive_2.csv
    
    turning test
    python3 create_turbo_turn_path.py --mode waypoints \
    --wp "1.0,0.0,0.0; 2.0,0.0,0.0; 3.0,0.0,0.3; 4.5,0.02,0.8; 5.5,0.05,1.3; 6.0,0.25,1.5; 5.8,0.45,1.5; 5.5,0.5,1.5; 3.0,0.5,1.5" \
    -o trajectories/return_dive.csv
    
    """
    raw = args.wp.replace(" ", "")
    tokens = [t for t in raw.split(";") if t]
    if len(tokens) < 2:
        raise ValueError("Need at least 2 waypoints (semicolon-separated x,y,z)")

    pts = []
    for t in tokens:
        coords = t.split(",")
        if len(coords) < 3:
            raise ValueError(f"Each waypoint needs x,y,z — got '{t}'")
        pts.append([float(c) for c in coords[:3]])
    pts = np.array(pts)

    x = pts[:, 0]
    y = pts[:, 1]
    z = pts[:, 2]

    N = len(x)
    yaw = np.zeros(N)
    for i in range(N - 1):
        dx = x[i + 1] - x[i]
        dy = y[i + 1] - y[i]
        if abs(dx) > 1e-8 or abs(dy) > 1e-8:
            yaw[i] = np.arctan2(dy, dx)
        elif i > 0:
            yaw[i] = yaw[i - 1]
    yaw[-1] = yaw[-2] if N >= 2 else 0.0

    u_per_wp = np.full(N, args.surge_speed)
    u_per_wp[-1] = 0.0
    dr_per_wp = np.zeros(N)
    return x, y, z, yaw, u_per_wp, dr_per_wp


def add_level_off_waypoints(x, y, z, yaw, u_per_wp, dr_per_wp,
                            distance=1.5, n_points=2,
                            do_start=False, do_end=True):
    """Extend the trajectory at the start/end so the cubic-spline tangent
    is horizontal (dz/ds ≈ 0) at the endpoints.

    At the end: appends *n_points* waypoints at the final z, extending in
    the XY heading direction of the last segment.

    At the start (opt-in): prepends 1 waypoint at the starting z, extending
    backward from the first segment's XY heading.
    """
    if do_end and len(x) >= 2:
        end_x, end_y, end_z = x[-1], y[-1], z[-1]
        end_yaw = yaw[-1]

        dx = x[-1] - x[-2]
        dy = y[-1] - y[-2]
        norm_xy = np.hypot(dx, dy)
        if norm_xy < 1e-8:
            for k in range(len(x) - 3, -1, -1):
                dx = x[-1] - x[k]
                dy = y[-1] - y[k]
                norm_xy = np.hypot(dx, dy)
                if norm_xy > 1e-8:
                    break
        if norm_xy > 1e-8:
            hx, hy = dx / norm_xy, dy / norm_xy
        else:
            hx, hy = 1.0, 0.0

        spacing = distance / n_points
        for i in range(1, n_points + 1):
            x = np.append(x, end_x + hx * spacing * i)
            y = np.append(y, end_y + hy * spacing * i)
            z = np.append(z, end_z)
            yaw = np.append(yaw, end_yaw)
            u_per_wp = np.append(u_per_wp, 0.0)
            dr_per_wp = np.append(dr_per_wp, 0.0)

    if do_start and len(x) >= 2:
        dx = x[1] - x[0]
        dy = y[1] - y[0]
        norm_xy = np.hypot(dx, dy)
        if norm_xy < 1e-8:
            for k in range(2, len(x)):
                dx = x[k] - x[0]
                dy = y[k] - y[0]
                norm_xy = np.hypot(dx, dy)
                if norm_xy > 1e-8:
                    break
        if norm_xy > 1e-8:
            hx, hy = dx / norm_xy, dy / norm_xy
        else:
            hx, hy = 1.0, 0.0

        lead_in_dist = distance / n_points
        px = x[0] - hx * lead_in_dist
        py = y[0] - hy * lead_in_dist
        x = np.insert(x, 0, px)
        y = np.insert(y, 0, py)
        z = np.insert(z, 0, z[1])
        yaw = np.insert(yaw, 0, yaw[1])
        u_per_wp = np.insert(u_per_wp, 0, u_per_wp[1])
        dr_per_wp = np.insert(dr_per_wp, 0, 0.0)

    return x, y, z, yaw, u_per_wp, dr_per_wp


def add_starting_point(x, y, z, yaw, u_per_wp, dr_per_wp, start_point):
    """Add a starting point to the waypoints."""
    x = np.insert(x, 0, start_point[0])
    y = np.insert(y, 0, start_point[1])
    z = np.insert(z, 0, start_point[2])
    yaw = np.insert(yaw, 0, start_point[3])
    u_per_wp = np.insert(u_per_wp, 0, 0.0)
    dr_per_wp = np.insert(dr_per_wp, 0, 0.0)
    return x, y, z, yaw, u_per_wp, dr_per_wp


def _spline_dense_samples(spl_x, spl_y, spl_z, theta_total, n_waypoints, n_min=200):
    """Sample splines along arc length for plotting."""
    n_pts = min(4000, max(n_min, 40 * max(2, n_waypoints)))
    s_fine = np.linspace(0.0, float(theta_total), n_pts)
    return s_fine, spl_x(s_fine), spl_y(s_fine), spl_z(s_fine)


def plot_path(x, y, z, yaw, u_per_wp, dr_per_wp, args, out_path):
    """Plot waypoints and arc-length cubic spline in a vertical stack:
    XY, XZ, X/Y/Z vs arc length, pitch (if depth varies), and curvature."""
    N = len(x)
    has_depth = np.ptp(z) > 1e-3

    spline_ok = False
    if N >= 2:
        arc_lengths, theta_total, spl_x, spl_y, spl_z = compute_spline(x, y, z)
        if theta_total > 1e-9 and np.all(np.diff(arc_lengths) > 1e-15):
            try:
                s_fine, xs, ys, zs = _spline_dense_samples(
                    spl_x, spl_y, spl_z, theta_total, N, n_min=200
                )
                spline_ok = True
            except ValueError:
                spline_ok = False

    # Pre-compute curvature so we can mark the peak on every subplot
    peak_s = peak_x = peak_y = peak_z = peak_curv = None
    curvature = None
    if spline_ok:
        dx_ds = spl_x(s_fine, 1)
        dy_ds = spl_y(s_fine, 1)
        dz_ds = spl_z(s_fine, 1)
        d2x_ds2 = spl_x(s_fine, 2)
        d2y_ds2 = spl_y(s_fine, 2)
        d2z_ds2 = spl_z(s_fine, 2)
        cross_x = dy_ds * d2z_ds2 - dz_ds * d2y_ds2
        cross_y = dz_ds * d2x_ds2 - dx_ds * d2z_ds2
        cross_z = dx_ds * d2y_ds2 - dy_ds * d2x_ds2
        cross_mag = np.sqrt(cross_x**2 + cross_y**2 + cross_z**2)
        speed = np.sqrt(dx_ds**2 + dy_ds**2 + dz_ds**2)
        curvature = np.where(speed > 1e-12, cross_mag / speed**3, 0.0)

        i_peak = int(np.argmax(curvature))
        peak_s = s_fine[i_peak]
        peak_x = float(spl_x(peak_s))
        peak_y = float(spl_y(peak_s))
        peak_z = float(spl_z(peak_s))
        peak_curv = curvature[i_peak]

    PEAK_KW = dict(marker="*", color="magenta", markersize=14, zorder=10,
                   label="Max κ")

    # Near-end trigger: theta_total - 0.7
    NEAR_END_OFFSET = 0.7
    ne_s = ne_x = ne_y = ne_z = None
    if spline_ok and theta_total > NEAR_END_OFFSET:
        ne_s = theta_total - NEAR_END_OFFSET
        ne_x = float(spl_x(ne_s))
        ne_y = float(spl_y(ne_s))
        ne_z = float(spl_z(ne_s))
    NE_KW = dict(marker="D", color="red", markersize=10, zorder=10,
                 label=f"Near end (θ_total − {NEAR_END_OFFSET})")
    NE_VLINE_KW = dict(color="red", linewidth=1.0, alpha=0.6, linestyle="-.")

    # Rows: XY, XZ, X(s), Y(s), Z(s), [pitch], [curvature]
    n_rows = 5 + int(has_depth) + int(spline_ok)
    fig, axes = plt.subplots(n_rows, 1, figsize=(12, 4 * n_rows))
    row = 0

    # --- XY (top-down) ---
    ax_xy = axes[row]; row += 1
    if spline_ok:
        ax_xy.plot(xs, ys, "-", color="C0", linewidth=2.0, label="Spline", zorder=1)
    ax_xy.plot(
        x, y, "o-", markersize=8, color="C1", label="Waypoints",
        linewidth=1, alpha=0.75, zorder=2,
    )
    if peak_s is not None:
        ax_xy.plot(peak_x, peak_y, **PEAK_KW)
    if ne_s is not None:
        ax_xy.plot(ne_x, ne_y, **NE_KW)
    for i in range(N):
        ax_xy.annotate(
            str(i), (x[i], y[i]),
            xytext=(5, 5), textcoords="offset points", fontsize=9, zorder=3,
        )
    arrow_length = 0.3
    skip = max(1, N // 20)
    for i in range(0, N, skip):
        dx_arrow = arrow_length * np.cos(yaw[i])
        dy_arrow = arrow_length * np.sin(yaw[i])
        color = "green" if u_per_wp[i] >= 0 else "red"
        ax_xy.arrow(
            x[i], y[i], dx_arrow, dy_arrow,
            head_width=0.1, head_length=0.1, fc=color, ec=color,
            linewidth=2, alpha=0.7,
        )
    ax_xy.set_xlabel("X (m)")
    ax_xy.set_ylabel("Y (m)")
    ax_xy.set_title("Top view (XY)")
    ax_xy.grid(True, alpha=0.3)
    ax_xy.axis("equal")
    ax_xy.legend(loc="best")

    # --- XZ (side) ---
    ax_xz = axes[row]; row += 1
    if spline_ok:
        ax_xz.plot(xs, zs, "-", color="C0", linewidth=2.0, label="Spline", zorder=1)
    ax_xz.plot(
        x, z, "o-", markersize=8, color="C1", label="Waypoints",
        linewidth=1, alpha=0.75, zorder=2,
    )
    if peak_s is not None:
        ax_xz.plot(peak_x, peak_z, **PEAK_KW)
    if ne_s is not None:
        ax_xz.plot(ne_x, ne_z, **NE_KW)
    for i in range(N):
        ax_xz.annotate(
            str(i), (x[i], z[i]),
            xytext=(5, 5), textcoords="offset points", fontsize=9, zorder=3,
        )
    ax_xz.set_xlabel("X (m)")
    ax_xz.set_ylabel("Z (m)")
    ax_xz.set_title("Depth view (XZ)")
    ax_xz.grid(True, alpha=0.3)
    ax_xz.axis("equal")
    ax_xz.invert_yaxis()
    ax_xz.legend(loc="best")

    # --- X, Y, Z vs arc length ---
    peak_coord_vals = {"X": peak_x, "Y": peak_y, "Z": peak_z}
    ne_coord_vals = {"X": ne_x, "Y": ne_y, "Z": ne_z}
    for coord_label, wp_vals, spl, color_spl in [
        ("X", x, spl_x if spline_ok else None, "C0"),
        ("Y", y, spl_y if spline_ok else None, "C3"),
        ("Z", z, spl_z if spline_ok else None, "C4"),
    ]:
        ax = axes[row]; row += 1
        if spl is not None:
            ax.plot(s_fine, spl(s_fine), "-", color=color_spl, linewidth=2.0,
                    label="Spline", zorder=1)
        ax.plot(arc_lengths if spline_ok else np.arange(len(wp_vals)),
                wp_vals, "o", markersize=6, color="C1", label="Waypoints",
                zorder=2)
        if peak_s is not None:
            ax.plot(peak_s, peak_coord_vals[coord_label], **PEAK_KW)
        if ne_s is not None:
            ax.plot(ne_s, ne_coord_vals[coord_label], **NE_KW)
            ax.axvline(ne_s, **NE_VLINE_KW)
        for s_wp in (arc_lengths if spline_ok else []):
            ax.axvline(s_wp, color="C1", linewidth=0.6, alpha=0.4, linestyle="--")
        ax.set_xlabel("Arc length (m)")
        ax.set_ylabel(f"{coord_label} (m)")
        ax.set_title(f"{coord_label} vs arc length")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best")

    # --- Pitch angle (only when depth varies) ---
    if has_depth:
        ax_pitch = axes[row]; row += 1
        arc = np.zeros(N)
        for i in range(1, N):
            arc[i] = arc[i - 1] + np.sqrt(
                (x[i] - x[i - 1]) ** 2 + (y[i] - y[i - 1]) ** 2 + (z[i] - z[i - 1]) ** 2
            )
        pitch = np.zeros(N)
        for i in range(1, N):
            dxy = np.sqrt((x[i] - x[i - 1]) ** 2 + (y[i] - y[i - 1]) ** 2)
            dz = z[i] - z[i - 1]
            if dxy > 1e-8 or abs(dz) > 1e-8:
                pitch[i] = np.arctan2(dz, dxy)
        pitch[0] = pitch[1] if N >= 2 else 0.0

        ax_pitch.plot(arc, np.rad2deg(pitch), "o-", markersize=6, color="tab:orange")
        if peak_s is not None:
            pitch_at_peak = np.interp(peak_s, arc, np.rad2deg(pitch))
            ax_pitch.plot(peak_s, pitch_at_peak, **PEAK_KW)
        if ne_s is not None:
            pitch_at_ne = np.interp(ne_s, arc, np.rad2deg(pitch))
            ax_pitch.plot(ne_s, pitch_at_ne, **NE_KW)
            ax_pitch.axvline(ne_s, **NE_VLINE_KW)
        ax_pitch.set_xlabel("Arc length (m)")
        ax_pitch.set_ylabel("Pitch angle (deg)")
        ax_pitch.set_title("Pitch angle along trajectory")
        ax_pitch.axhline(0, color="grey", linewidth=0.5, linestyle="--")
        ax_pitch.grid(True, alpha=0.3)

    # --- Curvature vs arc length ---
    if spline_ok:
        ax_curv = axes[row]; row += 1
        ax_curv.plot(s_fine, curvature, "-", color="C2", linewidth=1.5)
        ax_curv.plot(peak_s, peak_curv, **PEAK_KW)
        if ne_s is not None:
            ne_curv = float(np.interp(ne_s, s_fine, curvature))
            ax_curv.plot(ne_s, ne_curv, **NE_KW)
            ax_curv.axvline(ne_s, **NE_VLINE_KW)
        for s_wp in arc_lengths:
            ax_curv.axvline(s_wp, color="C1", linewidth=0.6, alpha=0.5, linestyle="--")
        ax_curv.set_xlabel("Arc length (m)")
        ax_curv.set_ylabel("Curvature κ (1/m)")
        ax_curv.set_title("Spline curvature")
        ax_curv.grid(True, alpha=0.3)
        ax_curv.legend(loc="best")

    fig.suptitle(
        f"Turbo turn path — {args.mode}  (Green=FWD, Red=BWD)",
        fontsize=14,
    )
    plt.tight_layout()
    out_path = out_path.replace(".csv", ".png")
    plt.savefig(out_path, dpi=150)
    print(f"Saved plot: {out_path}")
    plt.show()

def compute_spline(x, y, z):
    """Compute cumulative arc-lengths and fit cubic splines through the waypoints.

    After this call:
      self.arc_lengths  — cumulative arc-length at each waypoint
      self.theta_total  — total path length
      self._spl_x/y/z   — CubicSpline: arc_length -> position (C2 smooth)
    """
    arc_lengths = np.zeros(len(x))
    for i in range(1, len(x)):
        d = np.array([x[i] - x[i - 1], y[i] - y[i - 1], z[i] - z[i - 1]], dtype=float)
        arc_lengths[i] = arc_lengths[i - 1] + np.linalg.norm(d)
    theta_total = arc_lengths[-1]

    s = arc_lengths
    # "not-a-knot" gives smooth, non-zero tangents at the endpoints
    # (unlike "clamped" which forces zero derivative).
    # Falls back to "natural" for 2-point paths where "not-a-knot" needs >= 3.
    bc = "not-a-knot" if len(x) >= 3 else "natural"
    spl_x = CubicSpline(s, x, bc_type=bc)
    spl_y = CubicSpline(s, y, bc_type=bc) #PchipInterpolator(s, y)
    spl_z = CubicSpline(s, z, bc_type=bc)
    return arc_lengths, theta_total, spl_x, spl_y, spl_z

def add_intermediate_waypoints(x, y, z, yaw, u_per_wp, dr_per_wp, n_intermediate):
    """Insert n_intermediate waypoints between each consecutive pair."""
    if n_intermediate <= 0:
        return x, y, z, yaw, u_per_wp, dr_per_wp

    N = len(x)
    x_list, y_list, z_list, yaw_list, u_list, dr_list = [], [], [], [], [], []

    for i in range(N - 1):
        x_list.append(x[i])
        y_list.append(y[i])
        z_list.append(z[i])
        yaw_list.append(yaw[i])
        u_list.append(u_per_wp[i])
        dr_list.append(dr_per_wp[i])
        for j in range(1, n_intermediate + 1):
            t = j / (n_intermediate + 1)
            x_list.append(x[i] + t * (x[i + 1] - x[i]))
            y_list.append(y[i] + t * (y[i + 1] - y[i]))
            z_list.append(z[i] + t * (z[i + 1] - z[i]))
            yaw_diff = yaw[i + 1] - yaw[i]
            while yaw_diff > np.pi:
                yaw_diff -= 2 * np.pi
            while yaw_diff < -np.pi:
                yaw_diff += 2 * np.pi
            yaw_list.append(yaw[i] + t * yaw_diff)
            u_list.append(u_per_wp[i] + t * (u_per_wp[i + 1] - u_per_wp[i]))
            dr_list.append(dr_per_wp[i] + t * (dr_per_wp[i + 1] - dr_per_wp[i]))
    x_list.append(x[-1])
    y_list.append(y[-1])
    z_list.append(z[-1])
    yaw_list.append(yaw[-1])
    u_list.append(u_per_wp[-1])
    dr_list.append(dr_per_wp[-1])

    return (
        np.array(x_list), np.array(y_list), np.array(z_list),
        np.array(yaw_list), np.array(u_list), np.array(dr_list),
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create turbo-turn or on-spot turn trajectory CSV for path following."
    )
    parser.add_argument(
        "--mode",
        choices=["on_spot", "three_point", "three_point_turn", "N_point", "zigzag", "waypoints"],
        default="on_spot",
        help="Plan type: on_spot, three_point, three_point_turn, N_point, zigzag, or waypoints (custom x,y,z)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output CSV path (default: auto under ./trajectories/)",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Disable visualization",
    )
    # Shared
    parser.add_argument(
        "--n-intermediate",
        type=int,
        default=0,
        help="Intermediate waypoints between each main waypoint (0 = none)",
    )
    parser.add_argument(
        "--surge-speed",
        type=float,
        default=0.2,
        help="Nominal surge speed magnitude (m/s) for forward/backward segments",
    )
    # On-spot
    parser.add_argument(
        "--n-waypoints",
        type=int,
        default=12,
        help="Number of waypoints (on_spot and zigzag)",
    )
    parser.add_argument(
        "--total-yaw-deg",
        type=float,
        default=180.0,
        help="Total yaw change for on_spot (degrees)",
    )
    parser.add_argument(
        "--center-x", "--cx",
        type=float,
        default=3.0,
        dest="center_x",
        help="Center X for on_spot",
    )
    parser.add_argument(
        "--center-y", "--cy",
        type=float,
        default=0.0,
        dest="center_y",
        help="Center Y for on_spot",
    )
    parser.add_argument(
        "--center-z", "--cz",
        type=float,
        default=0.0,
        dest="center_z",
        help="Center Z for on_spot",
    )
    parser.add_argument(
        "--rudder-angle-deg",
        type=float,
        default=15.0,
        help="Rudder angle magnitude (deg) for on_spot alternating thrust vectoring",
    )
    parser.add_argument(
        "--reverse-yaw",
        action="store_true",
        help="Reverse turn direction: yaw goes 0 -> -total_yaw (and rudder sign flipped). Use if MPC turns the AUV the wrong way (e.g. port instead of starboard).",
    )
    # Three-point
    parser.add_argument(
        "--y-mid-offset",
        type=float,
        default=-0.9,
        help="Mid turn lateral offset (m); sign controls turn side (three_point)",
    )
    # Zigzag
    parser.add_argument(
        "--radius",
        type=float,
        default=1.0,
        help="Radius for zigzag pattern (m)",
    )
    parser.add_argument(
        "--alpha-deg",
        type=float,
        default=7.0,
        help="Angular spacing (deg) between zigzag waypoints; also the yaw increment per waypoint",
    )
    # Waypoints mode
    parser.add_argument(
        "--wp",
        type=str,
        default=None,
        help='Semicolon-separated x,y,z waypoints for "waypoints" mode, '
             'e.g. "0.5,0,0; 1,0,0; 3,0,0.5; 6,0,1"',
    )
    # Level-off
    parser.add_argument(
        "--level-off",
        action="store_true",
        default=False,
        help="Append/prepend flat waypoints so the spline tangent is horizontal "
             "at the trajectory endpoints (auto-enabled for waypoints mode)",
    )
    parser.add_argument(
        "--level-off-distance",
        type=float,
        default=0.5,
        help="Total distance (m) of the level-off extension at the endpoint (default: 0.5)",
    )
    parser.add_argument(
        "--level-off-points",
        type=int,
        default=2,
        help="Number of level-off waypoints to add at the end (default: 2)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.mode == "on_spot":
        x, y, z, yaw, u_per_wp, dr_per_wp = build_on_spot_path(args)
        mode_label = "on_spot"
    elif args.mode == "three_point":
        x, y, z, yaw, u_per_wp, dr_per_wp = build_three_point_path(args)
        mode_label = "three_point"
    elif args.mode == "N_point":
        x, y, z, yaw, u_per_wp, dr_per_wp = build_N_point_path(args)
        mode_label = "N_point"
    elif args.mode == "three_point_turn":
        x, y, z, yaw, u_per_wp, dr_per_wp = build_three_point_turn_path(args)
        mode_label = "three_point_turn"
    elif args.mode == "waypoints":
        if not args.wp:
            raise ValueError('--wp is required for waypoints mode, e.g. --wp "0.5,0,0; 3,0,0.5; 6,0,1"')
        x, y, z, yaw, u_per_wp, dr_per_wp = build_waypoints_path(args)
        mode_label = "waypoints"
    else:  # zigzag
        x, y, z, yaw, u_per_wp, dr_per_wp = build_zigzag_path(args)
        mode_label = "zigzag"

    if getattr(args, "reverse_yaw", False):
        yaw = -yaw
        dr_per_wp = -dr_per_wp

    x, y, z, yaw, u_per_wp, dr_per_wp = add_intermediate_waypoints(
        x, y, z, yaw, u_per_wp, dr_per_wp, args.n_intermediate
    )

    do_level_off = args.level_off or args.mode == "waypoints"
    if do_level_off:
        x, y, z, yaw, u_per_wp, dr_per_wp = add_level_off_waypoints(
            x, y, z, yaw, u_per_wp, dr_per_wp,
            distance=args.level_off_distance,
            n_points=args.level_off_points,
        )
    N = len(x)

    quaternions = np.array([yaw_to_quaternion(yw) for yw in yaw])

    # Output filename
    if args.output:
        filename = os.path.basename(args.output)
        out_dir = os.path.dirname(args.output) or "."
    else:
        out_dir = "./trajectories"
        if args.mode in ["on_spot", "three_point_turn"]:
            filename = (
                f"turbo_turn_{mode_label}_N{N}_yaw{int(args.total_yaw_deg)}_"
                f"rudder{int(args.rudder_angle_deg)}.csv"
            )
        elif args.mode == "three_point":
            filename = f"{mode_label}.csv"
        elif args.mode == "N_point":
            filename = f"{mode_label}_N{N}.csv"
        elif args.mode == "waypoints":
            filename = f"waypoints_N{N}.csv"
        else:
            interp_suffix = f"_interp{args.n_intermediate}" if args.n_intermediate > 0 else ""
            filename = (
                f"turbo_turn_{mode_label}_N{N}_alpha{int(args.alpha_deg)}_"
                f"radius{args.radius}{interp_suffix}.csv"
            )
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)

    # CSV contains position, quaternion, and velocity references.
    # The MPC stage cost tracks position + quaternion + surge velocity;
    # the terminal cost additionally tracks the full velocity vector.
    # Actuator states (VBS, LCG, stern, rudder, RPM) are omitted —
    # neutral defaults are applied downstream in path_client / ActionServerDiveSub.
    columns = [
        "x", "y", "z", "q0", "q1", "q2", "q3",
        "u", "v", "w", "q", "p", "r",
    ]
    df = pd.DataFrame(0.0, index=np.arange(N), columns=columns)
    df["x"] = x
    df["y"] = y
    df["z"] = z
    df["q0"] = quaternions[:, 0]
    df["q1"] = quaternions[:, 1]
    df["q2"] = quaternions[:, 2]
    df["q3"] = quaternions[:, 3]
    df["u"] = u_per_wp

    # Print summary
    print(f"Mode: {args.mode}")
    print(f"Waypoints: {N}")
    print(f"Output: {out_path}")
    if args.mode == "on_spot":
        print(f"  Total yaw: {args.total_yaw_deg} deg, rudder: ±{args.rudder_angle_deg} deg")
    print("\nWaypoint details (first 10):")
    for i in range(min(N, 10)):
        direction = "FWD" if u_per_wp[i] >= 0 else "BWD"
        dr_deg = np.rad2deg(dr_per_wp[i])
        print(
            f"  WP {i} ({direction}, u={u_per_wp[i]:.2f}, dr={dr_deg:.1f}°): "
            f"pos=({x[i]:.2f}, {y[i]:.2f}, {z[i]:.2f}), yaw={np.rad2deg(yaw[i]):.1f}°"
        )
    if N > 10:
        print(f"  ... ({N - 10} more)")

    df.to_csv(out_path, index=False)
    print(f"\nSaved: {out_path}")

    # Visualization
    if not args.no_plot and HAS_MATPLOTLIB:
        plot_path(x, y, z, yaw, u_per_wp, dr_per_wp, args, out_path)
    elif not args.no_plot and not HAS_MATPLOTLIB:
        print("Note: matplotlib not available, skipping visualization")


if __name__ == "__main__":
    main()
