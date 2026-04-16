# floatsam_move_to

A ROS 2 action server that commands a Floatsam USV to navigate to a specific geographic coordinate (latitude and longitude). It features dynamic speed profiling and strictly relies on a Reciprocal Velocity Obstacles (RVO) service to ensure safe, collision-free routing.

---

## Overview

    Goal (JSON via BaseAction)
        └── waypoint: 
            ├── latitude: <float>
            ├── longitude: <float>
            └── tolerance: <float>
        └── speed: <float> or <string> ("slow", "standard", "fast")
        └── constant_speed: <boolean> (optional)

    Action server: /move_to
    Action type:   smarc_action_base/action/BaseAction

When a goal is accepted, the server:

1. Converts the target GPS coordinate (latitude/longitude) into the local map frame.
2. Continuously calculates the Euclidean distance and heading error between the vehicle's current position and the target.
3. **Speed Profiling**: Automatically reduces speed linearly as the vehicle approaches within 10 meters of the target to prevent overshooting (unless `constant_speed` is explicitly set to `true`).
4. **Collision Avoidance (RVO)**: Sends its preferred velocity vector to the `get_safe_velocity` RVO service. The RVO service evaluates nearby obstacles/agents and returns a safe velocity and heading.
5. Publishes the RVO-adjusted speed and heading to the low-level controllers (`velocity_setpoint` and `yaw_setpoint`).
6. Declares success once the vehicle arrives within the defined `tolerance` radius.

---

## Core Functionalities

### 1. Point-to-Point Navigation
The server handles the core routing logic, translating high-level geographic goals into continuous heading and speed setpoints for the vehicle's low-level PID controllers. 

### 2. RVO-Based Collision Avoidance
Instead of blindly following the direct vector to the target, the server passes its desired speed and heading to the `get_safe_velocity` service. If a potential collision is detected, the RVO service returns an altered, safe velocity and angle. The server immediately applies these safe setpoints, allowing decentralized collision avoidance without needing complex behavior trees.

### 3. Smart Speed Scaling
The server supports named speed presets (`slow` = 1.0 m/s, `standard` = 2.0 m/s, `fast` = 5.0 m/s) alongside raw float values. To ensure smooth arrivals, it automatically scales down the velocity when the vehicle is within 10 meters of the goal. This feature can be bypassed by setting `"constant_speed": true` in the goal request.

### 4. Dynamic Controller Tuning
The server actively publishes PID tuning parameters (for yaw, yaw rate, and velocity) to the `captain_parameters` topic, ensuring the lower-level controllers are appropriately tuned for transit maneuvers.

---

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `robot_name` | `floatsam_usv` | Base name of the robot executing the server. |
| `yaw_p_gain`, `yaw_i_gain`, `yaw_d_gain` | `0.3`, `0.0`, `0.1` | PID gains for yaw control. |
| `yawrate_p_gain`, `yawrate_i_gain`, `yawrate_d_gain`| `300.0`, `0.0`, `30.0` | PID gains for yaw rate control. |
| `velocity_p_gain`, `velocity_i_gain`, `velocity_d_gain`| `500.0`, `10.0`, `0.0` | PID gains for velocity control. |

---

## Running and Activating the Server

### 1. Launch the Server

```bash
ros2 run floatsam_go_to_formation floatsam_move_to_action_server \
    --ros-args -p robot_name:=floatsam_usv_0

```
#### 2. Send a Move Mission (Terminal Command)
You can activate the server using the ROS 2 CLI. The goal string is a YAML representation containing the JSON payload.

#### Example: Move to coordinates at standard speed with a 1.0m tolerance
```bash
ros2 action send_goal /floatsam_usv_0/move_to smarc_msgs/action/BaseAction "{goal: {data: '{\"waypoint\": {\"latitude\": 58.8405, \"longitude\": 17.6520, \"tolerance\": 1.0}, \"speed\": \"standard\", \"constant_speed\": false}'}}"
```