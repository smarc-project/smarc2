# floatsam_go_to_formation_rvo

A ROS 2 action server that commands a fleet of Floatsam USVs into a geographic formation using a simplified **py_trees behavior tree**. Each robot is assigned an optimal formation slot via the Hungarian algorithm. Navigation and decentralized collision avoidance are handled by delegating path execution to the `move_to` action server, which strictly relies on **Reciprocal Velocity Obstacles (RVO)**.

---

## Overview

    Goal (JSON via BaseAction)
        └── formation_points: [{latitude, longitude, heading}, ...]

    Action server: /go_to_formation_rvo
    Action type:   smarc_action_base/action/BaseAction

When a goal is accepted, the server:

1. Waits for all robots to publish valid odometry in the map frame.
2. Builds a py_trees behavior tree and ticks it at **10 Hz**.
3. Runs the **Hungarian algorithm** to optimally assign each robot to a formation slot.
4. Sends goals to the `move_to` action client, which handles the localized routing and RVO-based collision avoidance.
5. Once every robot arrives, sends `loiter_heading` action goals to hold position and orientation for 400 seconds.

---

## Core Functionalities

### 1. Optimal Target Assignment
The `HungarianAssignment` behavior maps each robot to a formation point. It computes a cost matrix based on the squared Euclidean distance between every robot's current position and every goal point, ensuring the fleet travels the minimum collective distance.

### 2. RVO-Based Collision Avoidance
Unlike previous implementations that required manual priority checks and side-stepping maneuvers within the behavior tree, **collision avoidance is now fully delegated to the RVO service running inside the `move_to` server**. This significantly simplifies the behavior tree, as the underlying action server dynamically computes safe velocities to avoid neighboring agents without requiring tree-level oversight. 

### 3. Navigation to Target
The `MoveToClient` constructs a standard waypoint dictionary containing the target's latitude, longitude, arrival tolerance, and the fleet's maximum velocity. This payload is passed asynchronously to the `move_to` action server. 

### 4. Arrival and Loitering
The `AllArrivalCheck` behavior monitors the loiter feedback for all robots. Once every robot confirms arrival, the `LoiterWithHeadingClient` executes, keeping the robots at their designated coordinates and headings for 400 seconds.

---

## Behavior Tree Structure

    MainTree [Sequence]
    ├── FirstSelector [Selector]
    │   ├── HaveGoal              – succeeds if assignments already exist
    │   └── HungarianAssignment   – assigns robots to slots via optimal assignment
    └── SecondSequence [Sequence]
        ├── FifthSelector [Selector]
        │   ├── ArrivalCheck      – succeeds if robot already at target
        │   └── MoveToClient      – calls move_to action server (RVO handles collisions)
        └── SixthSelector [Selector]
            ├── AllArrivalCheck          – succeeds when every robot has arrived
            └── LoiterWithHeadingClient  – calls loiter_heading action server

---

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `robot_name` | `floatsam_usv_0` | Base name of the robot executing the server. |
| `num_robots` | `3` | Total number of USVs in the fleet. IDs are `0 .. num_robots-1`. |
| `max_velocity` | `2.0` | Maximum speed parameter passed to the `move_to` server. |
| `last_point_tolerance_move_path` | `0.5` | Acceptable radius (meters) to declare arrival at the target point. |

*(Note: Parameters like `collision_radius` and `max_num_collisions` are initialized in the server but their manual processing is bypassed due to the use of RVO).*

---

## Running and Activating the Server

### 1. Launch the Server

```bash
# Default parameters
ros2 launch floatsam_go_to_formation floatsam_go_to_formation_rvo.launch.py

# Custom fleet size (e.g., 5 robots)
ros2 launch floatsam_go_to_formation floatsam_go_to_formation_rvo.launch.py \
    robot_name:=floatsam_usv \
    num_robots:=5

```
### 2. Send a Formation Mission (Terminal Command)

You can activate the server and assign a mission using the ROS 2 CLI. The goal string must be a YAML representation containing the JSON payload. Ensure the number of coordinate sets exactly matches num_robots.

#### Example: Five-Robot Formation Mission
ros2 action send_goal /floatsam_usv_0/go_to_formation_rvo smarc_msgs/action/BaseAction "{goal: {data: '{\"formation_points\": [{\"latitude\": 58.8408761736411, \"longitude\": 17.6513505304756, \"heading\": 90.0}, {\"latitude\": 58.8410112590599, \"longitude\": 17.6515537892541, \"heading\": 90.0}, {\"latitude\": 58.8409725040742, \"longitude\": 17.6519172840096, \"heading\": 90.0}]}'}}"