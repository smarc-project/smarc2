# ALARS rope estimation
## Overview
This package contains a node that estimates the force a rope exerts on a robot based on readings from 3/4 load cells. 
At a fixed rate, the node gathers the latest load cell readings from topics, calculates the exerted force based on the geometry (TF) of the load cells, and publishes the force as `WrenchStamped`.

## Dependencies
- ROS2 Jazzy (tested), Humble should work too but did not test
- numpy

## Interface
The node works with either 3 or 4 load cells.
The topics and frames of individual load cells are contained in the `dji_msgs.Topics` and `dji_msgs.Links`, respectively (located in `messages.dji_msgs`).

### Topics
All topics are relative to the node namespace (`robot_name`).
| Topic | Direction | Type | Description |
|---|---|---|---|
| `sensor/load_cell_X_weight` | Sub | `std_msgs/Float32` | Load cell readings (kg) |
| `alars_rope_estimation/rope_force` | Pub | `geometry_msgs/WrenchStamped` | Exerted rope force (N) |

### Required TF
`<robot_name>/rope_base_link` → `<robot_name>/load_cell_X_link`


## Launch
- Launch the node with 
```bash
ros2 launch alars_rope_estimation rope_estim.launch.py
```
- To specify the robot(namespace) and simulation time, run with
```bash
ros2 launch alars_rope_estimation rope_estim.launch.py use_sim_time:=true robot_name:=M350
```
### Parameters
The node is configured by a single file located in `config/rope_estim_params.yaml`.
This file contains timeout for subscribers (stops publishing output if any reading is older than `topics.sub_timeout`), publishing rate of the estimated force (`topics.publish_rate`) and `logger_info.enable`.
