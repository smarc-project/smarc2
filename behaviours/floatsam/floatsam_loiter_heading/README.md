# floatsam_loiter_heading

A ROS 2 action server that commands a Floatsam USV to loiter (hold position) at its current location while maintaining a specified heading for a designated duration. It actively monitors its position and automatically dispatches correction goals to a `move_to` action server if the vehicle drifts beyond a defined tolerance.

---

## Overview

    Goal (JSON via BaseAction)
        └── duration: <float>
        └── heading: <float>

    Action server: /loiter_heading
    Action type:   smarc_action_base/action/BaseAction

When a goal is accepted, the server:

1. Records the vehicle's current map coordinates and GPS position to establish the "loiter center".
2. Publishes zero-velocity and targeted yaw setpoints to keep the vehicle stationary and properly oriented.
3. Continuously calculates the distance from the loiter center.
4. **Dynamic Repositioning**: If the vehicle drifts beyond the `loiter_tolerance`, the server automatically sends a high-priority goal to the `move_to` action server to drive the robot back to the center point. 
5. Publishes dynamic PID tuning parameters to the lower-level controllers to optimize heading maintenance.
6. Returns a success state once the specified `duration` (timeout) is reached, provided the vehicle is within the acceptable tolerances.

---

## Core Functionalities

### 1. Position Holding & Heading Control
The server directly controls the vehicle's orientation by publishing the desired heading (converted to radians) to the `yaw_setpoint` topic, while continuously commanding a `0.0` speed to the `velocity_setpoint` topic. 

### 2. Drift Correction via `move_to`
To handle environmental drift (like wind or currents), the server monitors the Euclidean distance between the initial "loiter center" and the current position. If this distance exceeds `loiter_tolerance`, the server suspends its stationary commands and triggers a `move_to` action goal with a strict `loiter_reposition_tolerance` to drive the vehicle back to the center.

### 3. Live Feedback
The server continuously publishes loiter status feedback to the `loiter_heading_fb` topic (1.0 if successfully holding position and heading, 0.0 otherwise). This allows higher-level mission planners (like the formation behavior tree) to verify arrival and synchronization.

---

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `robot_name` | `floatsam_usv` | Base name of the robot executing the server. |
| `loiter_tolerance` | `5.0` | Maximum allowed drift (meters) before triggering a repositioning maneuver. |
| `loiter_reposition_tolerance` | `0.5` | The strict arrival tolerance (meters) used when returning to the center. |
| `loiter_move_to_speed` | `'fast'` | The speed profile sent to the `move_to` server during a repositioning maneuver. |
| `heading_tolerance` | `5.0` | Acceptable error margin (degrees) for the vehicle's orientation. |

*Note: The server also accepts extensive PID tuning parameters (e.g., `yaw_p_gain`, `yawrate_p_gain`, `velocity_p_gain`) which are actively published to the `captain_parameters` topic.*

---

## Running and Activating the Server

### 1. Launch the Server

```bash
ros2 run floatsam_go_to_formation floatsam_loiter_heading_action_server \
    --ros-args -p robot_name:=floatsam_usv_0

```
### 2. Send a Loiter Mission (Terminal Command)
You can activate the server using the ROS 2 CLI. The goal string is a YAML representation containing the JSON payload. duration is in seconds, and heading is in degrees (0-360).
#### Example: Loiter for 5 minutes (300 seconds) facing East (90 degrees)
ros2 action send_goal /floatsam_usv_0/loiter_heading smarc_msgs/action/BaseAction "{goal: {data: '{\"duration\": 300.0, \"heading\": 90.0}'}}"