# FloatSam Controllers

**Integrated control stack for FloatSam USV** with cascaded PIDs as Python objects, differential thrust mixing, and delta RPM rate limiting.

## Architecture Overview

FloatSam uses a **single Captain node** that internally manages all control logic, making it highly configurable and generalizable through launch file parameters.

```
┌─────────────────────────────────────────────────────────────────┐
│                 FLOATSAM CAPTAIN (Single Node)                  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              PID Controllers (Python Objects)        │       │
│  │                                                      │       │
│  │  Yaw PID          Yaw Rate PID      Velocity PID     │       │
│  │  (angle→rate)     (rate→actuation)  (vel→RPM)        │       │
│  │  P=0.15           P=20.0             P=500, I=10     │       │
│  └──────────────────────────────────────────────────────┘       │
│                            ↓                                    │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              Differential Thrust Mixer               │       │
│  │  thruster_port = velocity_rpm - yaw_correction       │       │
│  │  thruster_strb = velocity_rpm + yaw_correction       │       │
│  └──────────────────────────────────────────────────────┘       │
│                            ↓                                    │
│  ┌──────────────────────────────────────────────────────┐       │
│  │         Delta RPM Rate Limiter (Health Check)        │       │
│  │  max_delta_rpm = 200 RPM/cycle                       │       │
│  └──────────────────────────────────────────────────────┘       │
│                            ↓                                    │
│             thruster_port_cmd  |  thruster_strb_cmd             │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **PIDs as Objects, Not Nodes**: PID controllers are Python class instances within Captain, not separate ROS nodes
2. **Single Configuration Point**: All gains configured in one place (launch file)
3. **Generalizable**: Easy to swap controller types or add new PIDs by passing different parameters
4. **Health Monitoring**: Delta RPM rate limiting prevents dangerous command spikes

## Control Components

### 1. Integrated PID Controllers (Internal Objects)

#### Yaw Cascade
- **Yaw PID**: `yaw_setpoint` → `yaw_rate_setpoint`
  - Uses vector-based angle difference (no 360° wraparound issues)
  - Default: P=0.15, limit=0.1 rad/s

- **Yaw Rate PID**: `yaw_rate_setpoint` → `yaw_actuation`
  - Default: P=20.0, limit=0.8

#### Velocity Control
- **Velocity PID**: `velocity_setpoint_input` → `velocity_rpm`
  - Default: P=500, I=10, limit=800 RPM

### 2. Differential Thrust Mixer

```python
yaw_correction = yaw_gain * yaw_actuation  
thruster_port = velocity_rpm - yaw_correction
thruster_strb = velocity_rpm + yaw_correction
```

### 3. Delta RPM Rate Limiter ⚠️

**Health check feature** that prevents dangerous rapid changes in thruster commands:

```python
delta = new_command - previous_command
if abs(delta) > max_delta_rpm:
    limited_command = previous_command ± max_delta_rpm
```

- **Default**: 200 RPM per control cycle (at 20Hz = 200 RPM per 50ms)
- **Purpose**: Protects motors from current spikes, prevents mechanical shock
- **Tunable**: Adjust via `max_delta_rpm` parameter

## Topic Interface

### Inputs from Behavior Layer
- `/floatsam_usv/ctrl/yaw_setpoint` (Float32) - Desired heading [rad]
- `/floatsam_usv/ctrl/velocity_setpoint` (Float32) - Desired speed [m/s]

### Sensor Feedback (from odom_splitter)
- `/floatsam_usv/ctrl/yaw` (Float32) - Current heading [rad]
- `/floatsam_usv/ctrl/yaw_rate` (Float32) - Current turn rate [rad/s]
- `/floatsam_usv/ctrl/surge_rate` (Float32) - Current velocity [m/s]

### Outputs to Hardware
- `/floatsam_usv/actuators/thruster_port_cmd` (Float32) - Port thruster RPM
- `/floatsam_usv/actuators/thruster_strb_cmd` (Float32) - Starboard thruster RPM

### Runtime Parameter Updates (from Action Servers)
- `/floatsam_usv/captain_parameters` (String) - JSON dictionary for dynamic PID reconfiguration

**⚠️ Important for Action Server Developers:**

Any action server that publishes setpoints (`yaw_setpoint`, `velocity_setpoint`) and expects the Captain's PIDs to operate **must publish** a JSON dictionary to the `captain_parameters` topic. This allows behaviors to dynamically adjust PID gains for different maneuvers.

**Required JSON Structure:**
```json
{
  "yaw_p_gain": 0.15,
  "yaw_i_gain": 0.0,
  "yaw_d_gain": 0.0,
  "yaw_threshold": 0.1,
  "yawrate_p_gain": 20.0,
  "yawrate_i_gain": 0.0,
  "yawrate_d_gain": 0.0,
  "velocity_p_gain": 500.0,
  "velocity_i_gain": 10.0,
  "velocity_d_gain": 0.0
}
```

**Example Implementation (Python):**
```python
import json
from std_msgs.msg import String

# In your action server __init__:
self._captain_parameters_publisher = self.create_publisher(
    String, 
    'captain_parameters', 
    1
)

 # Timer to publish captain parameters continuously 
self._captain_params_timer = self._node.create_timer(0.5, self._publish_captain_parametrs)


# Publish parameters:
def _publish_captain_parameters(self):
    parameters = {
        "yaw_p_gain": self._yaw_p_gain,
        "yaw_i_gain": self._yaw_i_gain,
        "yaw_d_gain": self._yaw_d_gain,
        "yaw_threshold": self._yaw_threshold,
        "yawrate_p_gain": self._yawrate_p_gain,
        "yawrate_i_gain": self._yawrate_i_gain,
        "yawrate_d_gain": self._yawrate_d_gain,
        "velocity_p_gain": self._velocity_p_gain,
        "velocity_i_gain": self._velocity_i_gain,
        "velocity_d_gain": self._velocity_d_gain
    }
    msg = String()
    msg.data = json.dumps(parameters)
    self._captain_parameters_publisher.publish(msg)
```

**See Examples:**
- [floatsam_move_to_server.py](vsls:/behaviours/floatsam/floatsam_move_to/floatsam_move_to/floatsam_move_to_server.py#L264-L280)
- [floatsam_loiter_server.py](vsls:/behaviours/floatsam/floatsam_move_to/floatsam_move_to/floatsam_loiter_server.py#L432-L448)

## Usage

### Launch the control stack:
```bash
ros2 launch floatsam_controllers floatsam_controllers_launch.py
```

### With custom PID gains:
```bash
ros2 launch floatsam_controllers floatsam_controllers_launch.py \
    yaw_p_gain:=0.2 \
    velocity_p_gain:=600.0 \
    max_delta_rpm:=150.0
```

### With custom robot name:
```bash
ros2 launch floatsam_controllers floatsam_controllers_launch.py robot_name:=my_floatsam
```

### Manual testing:
```bash
# Set yaw setpoint (90 degrees = π/2 radians)
ros2 topic pub /floatsam_usv/ctrl/yaw_setpoint std_msgs/msg/Float32 "{data: 1.57}"

# Set velocity setpoint (0.5 m/s forward)
ros2 topic pub /floatsam_usv/ctrl/velocity_setpoint std_msgs/msg/Float32 "{data: 0.5}"
```

## Configuration Parameters

All parameters in `floatsam_controllers_launch.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `update_rate` | 20.0 | Control loop frequency (Hz) |
| **Yaw PID** | | |
| `yaw_p_gain` | 0.15 | Proportional gain |
| `yaw_i_gain` | 0.0 | Integral gain |
| `yaw_d_gain` | 0.0 | Derivative gain |
| `yaw_output_limit` | 0.1 | Max yaw rate (rad/s) |
| **Yaw Rate PID** | | |
| `yawrate_p_gain` | 20.0 | Proportional gain |
| `yawrate_i_gain` | 0.0 | Integral gain |
| `yawrate_d_gain` | 0.0 | Derivative gain |
| `yawrate_output_limit` | 0.8 | Max actuation |
| **Velocity PID** | | |
| `velocity_p_gain` | 500.0 | Proportional gain |
| `velocity_i_gain` | 10.0 | Integral gain |
| `velocity_d_gain` | 0.0 | Derivative gain |
| `velocity_output_limit` | 800.0 | Max RPM |
| **Mixer** | | |
| `yaw_gain` | 800.0 | Differential thrust strength |
| `rpm_deadband` | 50.0 | Min RPM threshold |
| `thruster_limit` | 1000.0 | Absolute max RPM |
| **Health Check** | | |
| `max_delta_rpm` | 200.0 | Max RPM change/cycle |

## Tuning Guidelines

### PID Gains

**Start Conservative, Increase Gradually:**

1. **Yaw P-gain** (`yaw_p_gain`):
   - Higher → faster heading response
   - Too high → oscillation/overshoot
   - Test range: 0.1 - 0.3

2. **Yaw Rate P-gain** (`yawrate_p_gain`):
   - Higher → more aggressive turning
   - Too high → jerky motion
   - Test range: 10 - 40

3. **Velocity P-gain** (`velocity_p_gain`):
   - Higher → faster speed tracking
   - Depends on thruster/hull characteristics
   - Test range: 300 - 700

4. **Velocity I-gain** (`velocity_i_gain`):
   - Eliminates steady-state error (drag compensation)
   - Too high → overshoot/oscillation
   - Test range: 0 - 20

### Mixer Parameters

**Yaw Gain** (`yaw_gain`):
- Controls turning sharpness via differential thrust
- Higher → tighter turns but loses forward speed
- Lower → gentler turns, maintains speed
- Test range: 500 - 1200

**Max Delta RPM** (`max_delta_rpm`):
- Safety parameter for rate of change limiting
- Lower → smoother but slower response
- Higher → faster response but more motor stress
- Typical: 100-300 RPM per cycle (at 20Hz = 5-15 RPM/ms)

## Advantages Over Separate PID Nodes

| Aspect | Old (Separate Nodes) | New (Integrated) |
|--------|----------------------|------------------|
| **Configuration** | Spread across 3+ nodes | Single launch file |
| **Latency** | Inter-node communication | In-memory function calls |
| **Debugging** | Track multiple nodes | Single node logs |
| **Flexibility** | Hard to swap controllers | Easy to modify/extend |
| **Safety** | No rate limiting | Built-in delta RPM check |
| **Node Count** | 4 nodes (3 PIDs + mixer) | 1 node (captain) |

## Differences from Lolo

| Feature | Lolo (AUV) | FloatSam (USV) |
|---------|------------|----------------|
| **Architecture** | Separate PID nodes | PIDs as Python objects |
| **Node Count** | 10 nodes (9 PIDs + mixer) | 2 nodes (odom_splitter + captain) |
| **PIDs** | 9 controllers | 3 controllers |
| **Rate Limiting** | ❌ None | ✅ Delta RPM limiter |
| **Configuration** | Hardcoded in launch | All parameters tunable |
| **Depth Control** | 3-level cascade | ❌ None (surface vehicle) |
| **Roll Control** | 2-level cascade | ❌ None (passive stability) |

## Files Structure

```
floatsam_controllers/
├── floatsam_controllers/
│   ├── __init__.py
│   ├── pid.py           # PID class (imported by captain)
│   ├── geometry.py      # Vector math utilities
│   └── captain.py       # Main controller node (integrates all PIDs)
├── launch/
│   └── floatsam_controllers_launch.py  # Single configuration point
├── resource/
│   └── floatsam_controllers
├── README.md
├── package.xml
├── setup.py
└── setup.cfg
```

## Building

```bash
cd /path/to/smarc2
colcon build --packages-select floatsam_controllers
source install/setup.bash
```

## Testing

### Monitor all topics:
```bash
# Terminal 1: Launch
ros2 launch floatsam_controllers floatsam_controllers_launch.py

# Terminal 2: Monitor outputs
ros2 topic echo /floatsam_usv/actuators/thruster_port_cmd
ros2 topic echo /floatsam_usv/actuators/thruster_strb_cmd

# Terminal 3: Publish test setpoints
ros2 topic pub /floatsam_usv/ctrl/yaw_setpoint std_msgs/msg/Float32 "{data: 0.0}"
ros2 topic pub /floatsam_usv/ctrl/velocity_setpoint std_msgs/msg/Float32 "{data: 0.5}"
```

### Check delta RPM rate limiting:
Send rapid changing setpoints and watch for warnings:
```bash
# This should trigger rate limiting
ros2 topic pub /floatsam_usv/ctrl/velocity_setpoint std_msgs/msg/Float32 "{data: 2.0}" --once
sleep 0.1
ros2 topic pub /floatsam_usv/ctrl/velocity_setpoint std_msgs/msg/Float32 "{data: 0.0}" --once
```

Look for warnings in captain node logs:
```
[WARN] Port: Delta RPM 450.0 exceeds limit 200.0. Limiting to 350.0
```

## Integration with Action Server

[floatsam_move_to_server.py](../../behaviours/floatsam/floatsam_move_to/floatsam_move_to/floatsam_move_to_server.py) should publish to:

```python
from floatsam_msgs.msg import Topics as FloatsamTopics

yaw_setpoint_pub = self.create_publisher(Float32, FloatsamTopics.YAW_SETPOINT, 1)
velocity_setpoint_pub = self.create_publisher(Float32, FloatsamTopics.VELOCITY_SETPOINT, 1)

# In control loop:
yaw_setpoint_pub.publish(Float32(data=desired_heading_rad))
velocity_setpoint_pub.publish(Float32(data=desired_speed_m_s))
```

## Future Improvements


