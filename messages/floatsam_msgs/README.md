# FloatSam Messages

Topic definitions for FloatSam USV.

## Topics.msg

Defines all standard topics used by FloatSam controllers and behaviors.

### Control Setpoints
- `YAW_SETPOINT`: Desired heading angle [rad]
- `VELOCITY_SETPOINT`: Desired forward velocity [m/s]

### Actuator Commands
- `THRUSTER_PORT_CMD`: Port thruster command [RPM]
- `THRUSTER_STRB_CMD`: Starboard thruster command [RPM]

### Actuator Feedback
- `THRUSTER_PORT_FB`: Port thruster feedback [RPM]
- `THRUSTER_STRB_FB`: Starboard thruster feedback [RPM]

## Usage

```python
from floatsam_msgs.msg import Topics as FloatsamTopics

# Create publisher
self.yaw_pub = self.create_publisher(Float32, FloatsamTopics.YAW_SETPOINT, 1)

# Create subscriber
self.create_subscription(Float32, FloatsamTopics.THRUSTER_PORT_CMD, self.callback, 1)
```
