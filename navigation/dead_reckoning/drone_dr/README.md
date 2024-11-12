# State Estimation Package

## Overview

The `drone_dr` package is responsible for performing the dead reckoning task in ROS 2, particularly designed for quadrotors or similar UAVs. It includes sensor fusion from IMU and GPS  with a Kalman Filter , integrated into a ROS 2 environment to estimate the state of the drone in real time.

## Dependencies

### System Requirements

- ROS 2 Humble (or later)
- Python 3.8+
- Required Python libraries (can be installed via `requirements.txt`):
  ```bash
  pip install numpy scipy scikit-learn
  ```
  
- **Hardware**: Ensure that the UAV/drone is properly connected, with its sensor data being published to the appropriate ROS 2 topics.

### ROS 2 Dependencies
Ensure that the following ROS 2 packages are installed:
- `rclpy`
- `sensor_msgs`
- `geometry_msgs`
- `tf2_ros` (for TF tree manipulation)

### External Tools/Hardware:
- The drone needs to be set up to provide real-time data, such as GPS, camera and IMU data, published to the correct topics in ROS 2 for proper state estimation. The GPS and Camera can operate at a lower frequency but IMU callback is where the estimator is called which helps make an accurate motion model. We also need the **drone_msgs** package for access to relevant topics and link name strings.

---

## Nodes

### 1. **drone_dr.py**
This script is responsible for estimating the current state of the drone using the provided data and state transition models. It is the core state estimation node.

#### Purpose
- To predict the drone's position, velocity, and orientation in real time.
- Integrates measurements from multiple sources (e.g., GPS, IMU).

#### Dependencies
- Needs access to TF frames for calculating transformations between the drone's body frame and world frame.

Certainly! Below is a more refined version of the descriptions for **model_kf.py** and **model_ekf.py** that clearly outlines the purpose, functionality, and context of each filter:

---

### **2. model_kf.py (Kalman Filter)**

#### **Purpose**
This script implements a **Kalman Filter (KF)** for state estimation in scenarios where the system dynamics and measurements are linear. The primary goal is to predict and correct the state of the system (e.g., the position and velocity of a drone) based on sensor inputs.

#### **Description**
The Kalman Filter is a recursive algorithm that operates in two phases: **prediction** and **correction**. It uses:
- **IMU data (acceleration)** as input to predict the next state of the system based on a **linear double integrator model**.
- **GPS-based measurements** to correct the predicted state, minimizing the error between the predicted and observed data.


---

## Launch Files

### 1. `dead_reckoning.launch.xml`
This launch file starts the `estimator` node, which executes the estimation and dead_reckoning algorithm.

#### Usage
```bash
ros2 launch drone_dr dead_reckoning.launch`
```

## Why These Techniques?

  
- **Kalman Filters**: The Kalman Filter (KF) is a standard tool in robotics for state estimation. They help to smooth noisy sensor data and predict future states by combining predictions from motion models with observations.

---

## Example Workflow

1. Make sure your ROS 2 system is set up correctly with the necessary dependencies.
2. Ensure the drone is publishing sensor data, such as IMU and GPS.
3. Run the launch file:
   - For **only detection**: `ros2 launch drone_dr dead_reckoning.launch`
   

4. Verify that the nodes are receiving the data correctly, and check the console output for any state or detection information.

---

## Future Work

- **SLAM Integration**: Incorporating simultaneous localization and mapping (SLAM) algorithms into the estimation pipeline.

---

## Maintainer

**Aryan Dolas**
- Email: aryand@kth.se

Feel free to contribute, report issues, or suggest improvements!

