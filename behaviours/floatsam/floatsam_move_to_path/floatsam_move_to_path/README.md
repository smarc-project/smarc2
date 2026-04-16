# floatsam_move_path

A ROS 2 action server that commands a Floatsam USV to navigate through a sequence of geographic waypoints (latitude and longitude). It features dynamic, real-time speed adjustments via a live override topic and smooth deceleration upon approaching the final destination.

---

## Overview

    Goal (JSON via BaseAction)
        └── waypoints: [
              {
                "latitude": <float>, 
                "longitude": <float>, 
                "tolerance": <float> (optional)
              }, ...
            ]
        └── speed: <float> or <string> ("slow", "standard", "fast", "override")
        └── constant_speed: <boolean> (optional)

    Action server: /move_path
    Action type:   smarc_action_base/action/BaseAction

When a goal is accepted, the server:

1. Converts the list of GPS waypoints into the local map frame.
2. Navigates to each waypoint sequentially. Once the vehicle is within a waypoint's `tolerance`, it immediately targets the next one.
3. **Live Speed Overriding**: Subscribes to the `speed_override` topic. If the goal speed is set to `"override"`, the vehicle's speed will be dictated entirely by the real-time values published to this topic.
4. **Smart Deceleration**: When approaching the *final* waypoint in the list, it automatically scales down the velocity linearly once it is within 5 meters of the target to prevent overshooting. This can be disabled by setting `"constant_speed": true`.
5. Publishes heading and speed setpoints directly to the low-level controllers (`yaw_setpoint` and `velocity_setpoint`).

*(Note: Unlike the `move_to` server, this `move_path` implementation directly controls the vehicle's setpoints and does **not** route through the Reciprocal Velocity Obstacles (RVO) collision avoidance service).*

---

## Core Functionalities

### 1. Multi-Waypoint Sequential Routing
The server handles a list of coordinates rather than a single point. It tracks the active waypoint index, calculates the required heading and distance, and smoothly transitions to the next coordinate once the current tolerance radius is breached.

### 2. Real-Time Speed Override
This server is highly dynamic. By setting the goal's `speed` parameter to `"override"`, external nodes (such as formation controllers) can actively throttle the vehicle's speed by publishing to the `speed_override` topic while the action server handles the routing. 

### 3. Final Approach Profiling
To ensure efficient transit without stopping at intermediate points, the server maintains its requested speed through the middle waypoints. Deceleration logic is strictly reserved for the final waypoint in the sequence, ensuring a smooth stop at the end of the mission.

### 4. Dynamic Controller Tuning
The server actively publishes PID tuning parameters (for yaw, yaw rate, and velocity) to the `captain_parameters` topic, ensuring the lower-level controllers are appropriately tuned for path-following maneuvers.

---

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `robot_name` | `floatsam_usv` | Base name of the robot executing the server. |
| `_tolerance` | `5.0` | Default global tolerance if not specified per-waypoint. |
| `yaw_p_gain`, `yaw_i_gain`, `yaw_d_gain` | `0.3`, `0.0`, `0.1` | PID gains for yaw control. |
| `yawrate_p_gain`, `yawrate_i_gain`, `yawrate_d_gain`| `300.0`, `0.0`, `30.0` | PID gains for yaw rate control. |
| `velocity_p_gain`, `velocity_i_gain`, `velocity_d_gain`| `500.0`, `10.0`, `0.0` | PID gains for velocity control. |

---

## Running and Activating the Server

### 1. Launch the Server

```bash
ros2 run floatsam_go_to_formation floatsam_move_to_path_action_server \
    --ros-args -p robot_name:=floatsam_usv_0

```
### 2. Send a Path Mission (Terminal Command)
You can activate the server using the ROS 2 CLI. The goal string is a YAML representation containing the JSON payload.
#### Example: Two-waypoint path with speed override mode
```bash
ros2 action send_goal /floatsam_usv_0/move_path smarc_msgs/action/BaseAction "{goal: {data: '{\"waypoints\": [{\"latitude\": 58.8405, \"longitude\": 17.6520, \"tolerance\": 2.0}, {\"latitude\": 58.8410, \"longitude\": 17.6530, \"tolerance\": 1.0}], \"speed\": \"override\", \"constant_speed\": false}'}}"