# TwistStamped to path

This package contains a node for creating a path from a TwistStamped by integrating it x seconds into the future.


## Usage
```bash
ros2 launch twist_to_path twist_to_path_launch.py subscribe_topic:=/evolo/ctrl/twist_setpoint publish_topic:=/evolo/ctrl/twist_setpoint/path integration_time:=10.0 integration_dt:=0.5
```
