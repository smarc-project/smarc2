# FloatSam Loiter Action Server

The **loiter action server** maintains FloatSam's position within a specified tolerance circle. When the vehicle drifts outside this circle (due to currents, wind, etc.), it automatically triggers the `move_to` action server with a strict tolerance to return to the center.

## Features

- **Continuous Position Monitoring**: Checks position at 10Hz against loiter circle
- **Automatic Repositioning**: Calls `move_to` action with strict tolerance when out of bounds
- **Time-Limited**: Completes after specified timeout duration (like lolo_loiter)
- **Configurable Parameters** (via launch file):
  - `loiter_tolerance`: Radius of loiter circle (default: 5.0m)
  - `loiter_reposition_tolerance`: Strict tolerance for move_to (default: 0.5m)
  - `loiter_speed`: Repositioning speed in m/s (default: 1.0)
  - `loiter_move_to_speed`: Move_to speed setting - 'slow', 'standard', or 'fast' (default: 'fast')
- **Real-time Feedback**: Reports time remaining and distance from center

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│              LOITER ACTION SERVER                        │
│                                                          │
│  Goal: {"timeout": 600}  (only parameter)                │
│  Loiter center = CURRENT POSITION (when action starts)   │
│                                                          │
│  1. Record start time and current position as center     │
│  2. Monitor distance from center (10Hz)                  │
│  3. If distance > tolerance:                             │
│     ├─ Call move_to action (strict tolerance)            │
│     └─ Wait for completion                               │
│  4. If distance <= tolerance:                            │
│     └─ Publish zero velocity                             │
│  5. If (now - start_time) >= timeout:                    │
│     └─ Complete successfully                             │
│                                                          │
│  Internal Config (node parameters):                      │
│  • loiter_tolerance: 5.0m                                │
│  • loiter_reposition_tolerance: 0.5m                     │
│  • loiter_speed: 1.0 m/s                                 │
│  • loiter_move_to_speed: 'fast'                          │
│                                                          │
│  Dependencies:                                           │
│  • move_to action server (must be running)               │
│  • floatsam_common (for coordinate transforms)           │
└──────────────────────────────────────────────────────────┘
```

## Usage

### 1. Launch the Server

```bash
ros2 launch floatsam_loiter floatsam_loiter_launch.py robot_name:=floatsam_usv
```

**Note**: The `move_to` action server must also be running:
```bash
ros2 run floatsam_move_to floatsam_move_to_action_server
```

### 2. Send a Loiter Goal

**Standard Convention (like lolo_loiter)**: The loiter action accepts only `timeout` parameter. Loiter center is set to the **current position** when the action starts.

```json
{
    "timeout": 600
}
```

#### Parameters:
- **`timeout`** (required, float): Duration to loiter in seconds before completing

#### Internal Configuration (Node Parameters):
These are **not** passed via action goal, but configured at launch time:
- `loiter_tolerance`: Loiter circle radius in meters (default: 5.0)
- `loiter_reposition_tolerance`: Strict tolerance for move_to in meters (default: 0.5)
- `loiter_speed`: Repositioning speed in m/s (default: 1.0)
- `loiter_move_to_speed`: Speed string passed to move_to action - 'slow', 'standard', or 'fast' (default: 'fast')

### 3. Example Using ROS2 Action CLI

```bash
ros2 action send_goal /floatsam_usv/loiter smarc_msgs/action/BaseAction \
  "{goal: {data: '{\"timeout\": 600}'}}"
```

This will make FloatSam loiter at its **current position** for 600 seconds (10 minutes).

## Behavior

### Normal Operation (Inside Tolerance)
When FloatSam is within the tolerance circle:
- Publishes **zero velocity** to maintain position
- Continues monitoring at 10Hz
- **Completes successfully** when timeout expires
- Logs: `"Loitering: time remaining=XXXs, distance from center: X.XXm"`

### Out of Bounds (Outside Tolerance)
When FloatSam drifts outside the tolerance circle:
1. Logs: `"Outside loiter tolerance! Triggering move_to..."`
2. Calls `move_to` action with:
   - Target: Original loiter center (lat/lon)
   - Tolerance: `reposition_tolerance` (strict, e.g., 0.5m)
   - Speed: Configured speed (default: slow)
3. Waits for `move_to` to complete
4. Returns to normal monitoring

### Feedback
The action continuously publishes feedback:
```
Distance from center: 3.42m (tolerance: 5.00m, repositioning: False)
```

## Topics

### Subscribed
- `/{robot_name}/smarc/odom` (nav_msgs/Odometry) - Vehicle position

### Published
- `/{robot_name}/ctrl/yaw_setpoint` (FloatStamped) - Yaw reference (when maneuvering)
- `/{robot_name}/ctrl/velocity_setpoint` (FloatStamped) - Velocity reference

### Action Clients
- `/move_to` (BaseAction) - Called when repositioning needed

## Configuration Tips

### Choosing Tolerances

**Loiter Tolerance** (`waypoint.tolerance`):
- **Calm conditions**: 3-5m
- **Moderate currents**: 5-10m
- **Strong currents**: 10-15m

**Reposition Tolerance** (`reposition_tolerance`):
- **High precision**: 0.5m (default)
- **Standard**: 1.0m
- **Relaxed**: 2.0m

⚠️ **Important**: Always ensure `reposition_tolerance < loiter_tolerance` to avoid constant repositioning!

### Example Configurations

**Harbor/Calm Waters:**
```json
{
    "waypoint": {"latitude": 58.811481, "longitude": 17.596178, "tolerance": 3.0},
    "reposition_tolerance": 0.5,
    "speed": "slow"
}
```

**Open Sea/Current:**
```json
{
    "waypoint": {"latitude": 58.811481, "longitude": 17.596178, "tolerance": 10.0},
    "reposition_tolerance": 2.0,
    "speed": "standard"
}
```

## Code Structure

```
floatsam_move_to/
├── floatsam_move_to/
│   ├── floatsam_common.py         # Shared utilities (coordinate transforms)
│   ├── floatsam_move_to_server.py # Move-to action server
│   └── floatsam_loiter_server.py  # Loiter action server (NEW)
└── launch/
    ├── floatsam_move_to_launch.py
    └── floatsam_loiter_launch.py  # Loiter launch file (NEW)
```

