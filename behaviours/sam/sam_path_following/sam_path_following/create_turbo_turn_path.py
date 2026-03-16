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

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Optional plotting
try:
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

    x = np.array([1.5, 3.0, 4.5])
    y = np.array([0.0, 0.5, 1.0])
    z = np.zeros(len(x))
    yaw = np.array([0.0, 0.0, 0.0])

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

def add_starting_point(x, y, z, yaw, u_per_wp, dr_per_wp, start_point):
    """Add a starting point to the waypoints."""
    x = np.insert(x, 0, start_point[0])
    y = np.insert(y, 0, start_point[1])
    z = np.insert(z, 0, start_point[2])
    yaw = np.insert(yaw, 0, start_point[3])
    u_per_wp = np.insert(u_per_wp, 0, 0.0)
    dr_per_wp = np.insert(dr_per_wp, 0, 0.0)
    return x, y, z, yaw, u_per_wp, dr_per_wp


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
        choices=["on_spot", "three_point", "three_point_turn", "zigzag"],
        default="on_spot",
        help="Plan type: on_spot (turn in place), three_point (3-point turn), zigzag (alternating path)",
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
    return parser.parse_args()


def main():
    args = parse_args()

    if args.mode == "on_spot":
        x, y, z, yaw, u_per_wp, dr_per_wp = build_on_spot_path(args)
        mode_label = "on_spot"
    elif args.mode == "three_point":
        x, y, z, yaw, u_per_wp, dr_per_wp = build_three_point_path(args)
        mode_label = "three_point"
    elif args.mode == "three_point_turn":
        x, y, z, yaw, u_per_wp, dr_per_wp = build_three_point_turn_path(args)
        mode_label = "three_point_turn"
    else:  # zigzag
        x, y, z, yaw, u_per_wp, dr_per_wp = build_zigzag_path(args)
        mode_label = "zigzag"

    if getattr(args, "reverse_yaw", False):
        yaw = -yaw
        dr_per_wp = -dr_per_wp

    x, y, z, yaw, u_per_wp, dr_per_wp = add_intermediate_waypoints(
        x, y, z, yaw, u_per_wp, dr_per_wp, args.n_intermediate
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
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.plot(x, y, "o-", markersize=8, label="Waypoints", linewidth=1, alpha=0.5)
        arrow_length = 0.3
        skip = max(1, N // 20)
        for i in range(0, N, skip):
            dx_arrow = arrow_length * np.cos(yaw[i])
            dy_arrow = arrow_length * np.sin(yaw[i])
            color = "green" if u_per_wp[i] >= 0 else "red"
            ax.arrow(
                x[i], y[i], dx_arrow, dy_arrow,
                head_width=0.1, head_length=0.1, fc=color, ec=color,
                linewidth=2, alpha=0.7,
            )
            if i % max(1, skip) == 0 or N <= 20:
                direction = "FWD" if u_per_wp[i] >= 0 else "BWD"
                ax.text(x[i] + 0.15, y[i] + 0.15, f"WP{i}\n({direction})", fontsize=8, ha="left")
        ax.set_xlabel("X Position (m)")
        ax.set_ylabel("Y Position (m)")
        ax.set_title(f"Turbo Turn Path — {args.mode}\nGreen=Forward, Red=Backward")
        ax.grid(True, alpha=0.3)
        ax.axis("equal")
        ax.legend()
        plt.tight_layout()
        plot_path = out_path.replace(".csv", ".png")
        plt.savefig(plot_path, dpi=150)
        print(f"Saved plot: {plot_path}")
        plt.show()
    elif not args.no_plot and not HAS_MATPLOTLIB:
        print("Note: matplotlib not available, skipping visualization")


if __name__ == "__main__":
    main()
