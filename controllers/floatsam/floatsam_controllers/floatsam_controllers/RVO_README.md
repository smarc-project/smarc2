# RVO Safe Velocity Service

The `RVOservice` is a ROS 2 node designed to compute collision-free velocities for multi-robot systems using a sampling-based Reciprocal Velocity Obstacles (RVO) approach. It listens to the odometry of surrounding robots and provides a service to evaluate and adjust a robot's preferred velocity to ensure safe navigation.

## Overview

When queried via the `get_safe_velocity` service, the node checks if the requesting robot's preferred velocity is safe (i.e., falls outside the collision cones of all other robots). If the preferred velocity leads to a potential collision within the configured `time_horizon`, the node searches through a discrete set of velocity samples to find the closest safe alternative.

## Dependencies

* **ROS 2** (Tested on Humble)
* **Python Packages:** `numpy`
* **Custom Interfaces/Modules:** * `floatsam_interfaces.srv.GetSafeVelocity`
  * `floatsam_common.FloatSam`
* **Standard ROS 2 Messages:** `nav_msgs/Odometry`, `geometry_msgs/PoseStamped`

## Node Details

* **Node Name:** `rvo_service_node`

### Services Provided

* **`get_safe_velocity`** (`floatsam_interfaces/srv/GetSafeVelocity`)
  * **Request:** * `robot_id` (int/string): The ID of the robot requesting a safe velocity.
    * `pref_velocity` (list/array): The desired velocity vector $[v_x, v_y]$.
  * **Response:** * `safe_velocity` (list): The computed safe speed and angle `[speed, angle]`.
    * `success` (bool): `True` if a safe velocity was found, `False` otherwise.
    * `change` (bool): `True` if the velocity had to be altered from the preferred input for safety, `False` if the original preferred velocity was already safe.

### Subscribed Topics

The node automatically subscribes to the odometry topics of all robots in the swarm based on the `num_robot` parameter.

* **`/<robot_base_name>_<id>/smarc/odom`** (`nav_msgs/Odometry`)
  * Used to track the current positions and velocities of all simulated robots. *Note: Poses are internally transformed to the map frame using `tf2`.*

### Parameters

You can configure the behavior of the RVO service using the following ROS 2 parameters:

| Parameter Name | Default Value | Description |
| :--- | :--- | :--- |
| `robot_name` | `"floatsam_0"` | The base name and ID of the robot running this specific node instance. |
| `num_robot` | `3` | The total number of robots in the environment to track for collision avoidance. |
| `time_horizon` | `0.5` | The look-ahead time (in seconds) used to predict and avoid collisions. |
| `safety_margin` | `0.5` | The physical buffer distance kept between robots. |
| `max_speed` | `3.0` | The maximum allowable speed for the robot. |
| `update_rate` | `0.0` | Target execution rate (currently unused in the main loop). |

## How it Works

1. **State Tracking:** The node continuously updates the positions and velocities of all robots via odometry callbacks.
2. **Cone Check:** When the service is called, it computes the collision cone for every neighboring robot. 
3. **Validation:** It tests the requested `pref_velocity`. If the relative velocity vector falls inside any neighbor's collision cone, it is flagged as unsafe.
4. **Sampling:** If unsafe, the node evaluates a pre-generated grid of velocity samples (speeds from 0 to `max_speed` and 120 directional angles). It selects the velocity that is physically safe and mathematically closest to the original `pref_velocity`.