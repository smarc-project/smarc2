# ALARS rope estimation
## Overview
This package contains a node that estimates the force a rope exerts on a robot based on readings from load cells. 
At a fixed rate, the node gathers the latest load cell readings from topics, calculates the exerted force based on the geometry (TF) of the load cells, and publishes the force as `WrenchStamped`.

## Dependencies
- ROS2 Jazzy (tested), Humble should work too but did not test
- numpy

## Interface
The node works with a variable number of load cells, set by the `num_load_cells`>=3 parameter.
For all load cell interfaces, we assume the naming convention to follow this rule: both the topics and TFs are given as `topics.load_cell_template` and `frames.load_cell_template`, where `{}` is replaced by i = 1, ..., `num_load_cells`.
We assume that topic and TF with the same index i come from the same load cell.

### Topics
All topics are relative to the node namespace (`robot_name`).
| Topic | Direction | Type | Description |
|---|---|---|---|
| `sensor/load_cell_{}` | Sub | `std_msgs/Float32` | Load cell readings (kg) |
| `rope_force` | Pub | `geometry_msgs/WrenchStamped` | Exerted rope force (N) |

### Required TF
`<robot_name>/rope_base_link` → `<robot_name>/LoadCell{}`


## Launch
- Launch the node with 
```bash
ros2 launch alars_rope_estimation rope_estim.launch.py
```
- To specify the robot(namespace) and simulation time, run with
```bash
ros2 launch alars_rope_estimation rope_estim.launch.py use_sim_time:=true robot_name:=M350
```
### Configuration
The node is configured by a single file located in `config/rope_estim_params.yaml`.
This file contains load cell topic and frame templates, output topic, timeout for subscribers (stops publishing output if any reading is older than `sub_timeout`), `plate_width`, `publish_rate` and `logger_info.enable`.
