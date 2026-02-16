import argparse

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


radius = 2
alpha_deg = 180
alpha = np.deg2rad(alpha_deg)
N = 11

# Option to add intermediate waypoints to guide turn direction
# This helps prevent the MPC from turning the "wrong way" around
N_INTERMEDIATE = (
    2  # Number of intermediate waypoints between each main waypoint (0 = none)
    # NOTE: Too many creates tight spacing infeasible for nonholonomic turns!
)

# Coordinate system option
# Set to True if using NED/FRD (marine robotics standard: +yaw = turn right/starboard)
# Set to False if using ENU/FLU (ROS/math standard: +yaw = turn left/counter-clockwise)
USE_NED_CONVENTION = True  # Try flipping this if vehicle turns wrong direction!

filename = f"turbo_turn_N{N}_alpha{alpha_deg}_radius{radius}.csv"
if N_INTERMEDIATE > 0:
    filename = (
        f"turbo_turn_N{N}_alpha{alpha_deg}_radius{radius}_interp{N_INTERMEDIATE}.csv"
    )

i = np.arange(N)
beta = i * alpha + (i % 2) * np.pi

# x = radius * np.cos(beta) + 3
# y = radius * np.sin(beta)

# Turbo-turn debug path:
# Keep first/last points on centerline and move an intermediate point off-axis.
# Flip Y_MID_OFFSET sign to test opposite turn side.
Y_MID_OFFSET = -0.9  # meters, use negative for opposite side
turn_sign = 1.0 if Y_MID_OFFSET >= 0 else -1.0

# Feasible turbo-turn profile:
# 1) straight approach
# 2) gradual turn to +/-90 deg while moving off centerline
# 3) add extra straight-line waypoints first, then densify turn to 180
x = np.array([3.0, 4.5, 6.0, 5.5, 4.5, 4.25, 4.05, 3.80, 3.30, 2.55, 2.00])
y = np.array(
    [
        0.0,
        0.0,
        0.0,
        0.0,
        0.45 * turn_sign,
        0.90 * turn_sign,
        0.75 * turn_sign,
        0.50 * turn_sign,
        0.25 * turn_sign,
        0.10 * turn_sign,
        0.0,
    ]
)
z = np.zeros(len(x))

yaw = np.array(
    [
        0.0,  # straight
        0.0,  # straight
        0.0,  # straight
        0.0,  # straight
        -turn_sign * np.deg2rad(35),
        -turn_sign * np.deg2rad(90),
        -turn_sign * np.deg2rad(100),
        -turn_sign * np.deg2rad(110),
        -turn_sign * np.deg2rad(130),
        -turn_sign * np.deg2rad(155),
        -np.pi,  # final reverse direction
    ]
)

# NOTE:
# These yaw values are intentionally authored directly for the test scenario.
# USE_NED_CONVENTION is therefore informational here.
# Convert yaw angles to quaternions
quaternions = np.array([yaw_to_quaternion(y) for y in yaw])

# Optional: Add intermediate waypoints to guide turn direction
if N_INTERMEDIATE > 0:
    print(
        f"\nAdding {N_INTERMEDIATE} intermediate waypoints between each main waypoint..."
    )

    x_interp = []
    y_interp = []
    z_interp = []
    yaw_interp = []

    for i in range(N - 1):
        # Add the current waypoint
        x_interp.append(x[i])
        y_interp.append(y[i])
        z_interp.append(z[i])
        yaw_interp.append(yaw[i])

        # Add intermediate waypoints
        for j in range(1, N_INTERMEDIATE + 1):
            t = j / (N_INTERMEDIATE + 1)  # Interpolation parameter [0, 1]

            # Linear interpolation of position
            x_mid = x[i] + t * (x[i + 1] - x[i])
            y_mid = y[i] + t * (y[i + 1] - y[i])
            z_mid = z[i] + t * (z[i + 1] - z[i])

            # Interpolate yaw angle (handling wrap-around)
            yaw_diff = yaw[i + 1] - yaw[i]
            # Normalize to [-pi, pi] for shortest path
            while yaw_diff > np.pi:
                yaw_diff -= 2 * np.pi
            while yaw_diff < -np.pi:
                yaw_diff += 2 * np.pi
            yaw_mid = yaw[i] + t * yaw_diff

            x_interp.append(x_mid)
            y_interp.append(y_mid)
            z_interp.append(z_mid)
            yaw_interp.append(yaw_mid)

    # Add the last waypoint
    x_interp.append(x[-1])
    y_interp.append(y[-1])
    z_interp.append(z[-1])
    yaw_interp.append(yaw[-1])

    # Replace original arrays with interpolated ones
    x = np.array(x_interp)
    y = np.array(y_interp)
    z = np.array(z_interp)
    yaw = np.array(yaw_interp)
    quaternions = np.array([yaw_to_quaternion(y) for y in yaw])
    N = len(x)

    print(f"Total waypoints after interpolation: {N}")

columns = [
    "x",
    "y",
    "z",
    "q0",
    "q1",
    "q2",
    "q3",
    "u",
    "v",
    "w",
    "q",
    "p",
    "r",
    "V_bs",
    "l_cg",
    "ds",
    "dr",
    "rpm_1",
    "rpm_2",
]

df = pd.DataFrame(0.0, index=np.arange(N), columns=columns)

df["x"] = x
df["y"] = y
df["z"] = z
df["q0"] = quaternions[:, 0]
df["q1"] = quaternions[:, 1]
df["q2"] = quaternions[:, 2]
df["q3"] = quaternions[:, 3]

# Add desired velocities for better tracking
# Surge velocity: maintain forward motion for control authority
df["u"] = 0.3  # m/s - adjust based on vehicle capability

# Print waypoint info for debugging
print(f"Generating turbo turn path: {filename}")
print(f"Number of waypoints: {N}")
print(f"Radius: {radius} m")
print(f"Angular spacing: {alpha_deg} degrees")
if N_INTERMEDIATE > 0:
    print(f"Intermediate waypoints: {N_INTERMEDIATE} per segment")
print("\nTurbo turn pattern: Heading alternates by 180° at each main waypoint")
print(
    "Vehicle uses forward thrust, but alternating heading creates back-and-forth motion\n"
)
print("Waypoint details (first 10):")
for i in range(min(N, 10)):
    # Calculate and show segment direction for context
    if i < N - 1:
        seg_dir = np.arctan2(y[i + 1] - y[i], x[i + 1] - x[i])
        seg_info = f", seg→WP{i + 1}={np.rad2deg(seg_dir):.1f}°"
    else:
        seg_info = ""

    # Show if this should be forward or backward motion
    main_idx = i // (N_INTERMEDIATE + 1) if N_INTERMEDIATE > 0 else i
    direction = "FWD" if main_idx % 2 == 0 else "BWD"

    print(
        f"  WP {i} ({direction}): pos=({x[i]:.2f}, {y[i]:.2f}, {z[i]:.2f}), "
        f"yaw={np.rad2deg(yaw[i]):.1f}°{seg_info}"
    )

    # Show heading change between waypoints
    if i > 0:
        yaw_change = yaw[i] - yaw[i - 1]
        # Normalize to [-pi, pi]
        while yaw_change > np.pi:
            yaw_change -= 2 * np.pi
        while yaw_change < -np.pi:
            yaw_change += 2 * np.pi
        turn_dir = "PORT (left)" if yaw_change > 0 else "STBD (right)"
        print(
            f"       → Heading change from WP{i - 1}: {np.rad2deg(yaw_change):.1f}° ({turn_dir})"
        )

if N > 10:
    print(f"  ... ({N - 10} more waypoints)")

print("\n" + "=" * 70)
print("COORDINATE SYSTEM CHECK:")
print("=" * 70)
print("Expected behavior for turbo turn:")
print("  - Even waypoints (0,2,4,...): Vehicle moves FORWARD to next waypoint")
print("  - Odd waypoints (1,3,5,...): Vehicle moves BACKWARD to next waypoint")
print("Yaw angle convention:")
if USE_NED_CONVENTION:
    print("  - Using NED/FRD convention: +yaw = clockwise/STARBOARD turn")
else:
    print("  - Using ENU/FLU convention: +yaw = counter-clockwise/PORT turn")
print(f"  - USE_NED_CONVENTION = {USE_NED_CONVENTION}")
print("  - If vehicle turns wrong direction, flip this flag!")
print("\nQuick check:")
print(f"  WP0 → WP1: Should turn {np.rad2deg(yaw[1] - yaw[0]):.1f}°")
# print(f"  WP1 → WP2: Should turn {np.rad2deg(yaw[2] - yaw[1]) if len(yaw) > 2 else 'N/A':.1f}°")
print("=" * 70 + "\n")

df.to_csv("./trajectories/" + filename, index=False)
print(f"\nSaved trajectory to: ./trajectories/{filename}")

np.set_printoptions(precision=3)
print(f"\nbeta: {beta}")
print(f"yaw:  {yaw}")

# Quaternion verification
print("\n" + "=" * 70)
print("QUATERNION VERIFICATION:")
print("=" * 70)
print("First 3 waypoints - verify quaternions match yaw angles:")
for i in range(min(3, len(x))):
    print(f"\nWP {i}:")
    print(f"  Yaw angle: {np.rad2deg(yaw[i]):.2f}°")
    print(
        f"  Quaternion: [{quaternions[i, 0]:.4f}, {quaternions[i, 1]:.4f}, {quaternions[i, 2]:.4f}, {quaternions[i, 3]:.4f}]"
    )
    # Verify: q = [cos(yaw/2), 0, 0, sin(yaw/2)]
    expected_q0 = np.cos(yaw[i] / 2.0)
    expected_q3 = np.sin(yaw[i] / 2.0)
    print(f"  Expected:   [{expected_q0:.4f}, 0.0000, 0.0000, {expected_q3:.4f}]")
    match = np.allclose(
        [quaternions[i, 0], quaternions[i, 3]], [expected_q0, expected_q3], atol=1e-4
    )
    print(f"  Match: {'✓ PASS' if match else '✗ FAIL - CHECK QUATERNION CONVERSION!'}")
print("=" * 70)

# Optional visualization
VISUALIZE = True  # Set to False to disable plotting
if VISUALIZE and HAS_MATPLOTLIB:
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot waypoints
    ax.plot(x, y, "o-", markersize=8, label="Waypoints", linewidth=1, alpha=0.5)

    # Plot heading arrows at each waypoint (show every nth for clarity if many waypoints)
    arrow_length = 0.3
    skip = max(1, N // 20)  # Show at most 20 arrows
    for i in range(0, N, skip):
        # Arrow showing vehicle heading
        dx_arrow = arrow_length * np.cos(yaw[i])
        dy_arrow = arrow_length * np.sin(yaw[i])

        # Determine if this is a main waypoint (for coloring)
        if N_INTERMEDIATE > 0:
            is_main = (i % (N_INTERMEDIATE + 1)) == 0
            color = (
                ("green" if i // (N_INTERMEDIATE + 1) % 2 == 0 else "red")
                if is_main
                else "blue"
            )
            alpha_val = 0.9 if is_main else 0.4
        else:
            color = "green" if i % 2 == 0 else "red"
            alpha_val = 0.7

        ax.arrow(
            x[i],
            y[i],
            dx_arrow,
            dy_arrow,
            head_width=0.1,
            head_length=0.1,
            fc=color,
            ec=color,
            linewidth=2,
            alpha=alpha_val,
        )

        # Label main waypoints only
        if N_INTERMEDIATE == 0 or (i % (N_INTERMEDIATE + 1)) == 0:
            main_idx = i // (N_INTERMEDIATE + 1) if N_INTERMEDIATE > 0 else i
            direction = "FWD" if main_idx % 2 == 0 else "BWD"
            ax.text(
                x[i] + 0.15,
                y[i] + 0.15,
                f"WP{main_idx}\n({direction})",
                fontsize=8,
                ha="left",
            )

    ax.set_xlabel("X Position (m)")
    ax.set_ylabel("Y Position (m)")
    title = f"Turbo Turn Path (N={N}, α={alpha_deg}°, r={radius}m)\n"
    title += f"Green=Forward, Red=Backward"
    if N_INTERMEDIATE > 0:
        title += f", Blue=Intermediate ({N_INTERMEDIATE}/segment)"
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.axis("equal")
    ax.legend()

    plt.tight_layout()
    plot_filename = (
        f"./trajectories/turbo_turn_N{N}_alpha{alpha_deg}_radius{radius}.png"
    )
    plot_filename = (
        f"./trajectories/turbo_turn_N{N}_alpha{alpha_deg}_radius{radius}.png"
    )
    plt.savefig(plot_filename, dpi=150)
    print(f"Saved visualization to: {plot_filename}")
    plt.show()
elif VISUALIZE and not HAS_MATPLOTLIB:
    print("\nNote: matplotlib not available, skipping visualization")
