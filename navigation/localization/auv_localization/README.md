# State Estimation Package

## Overview

The `state_estimation` package is responsible for performing perception and estimation tasks in ROS 2, particularly designed for quadrotors or similar UAVs. It includes several estimation techniques, such as K-Nearest Neighbors (KNN) and Kalman Filters (KF and EKF), integrated into a ROS 2 environment to estimate the state of the drone and that of an AUV/ROV on water surface, relative to the drone in real time.

This package contains different modules for sensor fusion, state prediction, and data filtering. The estimators and detection methods can be launched separately or together based on the use case.

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
- The drone needs to be set up to provide real-time data, such as GPS, camera and IMU data, published to the correct topics in ROS 2 for proper state estimation. The GPS and Camera can operate at a lower frequency but IMU callback is where the estimator is called which helps make an accurate motion model.

---

## Nodes

### 1. **detector.py (KNN)**
This script uses a K-Nearest Neighbors (KNN) algorithm to classify or detect objects based on sensor inputs. The KNN classifier can be trained with labeled data and then used to infer object identities during runtime.

#### Purpose
- To classify sensor data from the drone.
- Can be extended for object detection, collision avoidance, etc.

#### Parameters
- `k`: Number of neighbors for KNN.
- `input_topic`: The topic where sensor data (e.g., point clouds) are received.

---

### 2. **estimator.py**
This script is responsible for estimating the current state of the drone using the provided data and state transition models. It is the core state estimation node.

#### Purpose
- To predict the drone's position, velocity, and orientation in real time.
- Integrates measurements from multiple sources (e.g., odometry, IMU).

#### Dependencies
- Needs access to TF frames for calculating transformations between the drone's body frame and world frame.

Certainly! Below is a more refined version of the descriptions for **model_kf.py** and **model_ekf.py** that clearly outlines the purpose, functionality, and context of each filter:

---

### **3. model_kf.py (Kalman Filter)**

#### **Purpose**
This script implements a **Kalman Filter (KF)** for state estimation in scenarios where the system dynamics and measurements are linear. The primary goal is to predict and correct the state of the system (e.g., the position and velocity of a drone) based on sensor inputs.

#### **Description**
The Kalman Filter is a recursive algorithm that operates in two phases: **prediction** and **correction**. It uses:
- **IMU data (acceleration)** as input to predict the next state of the system based on a **linear double integrator model**.
- **GPS-based measurements** to correct the predicted state, minimizing the error between the predicted and observed data.


---

### **4. model_ekf.py (Extended Kalman Filter)**

#### **Purpose**
The **Extended Kalman Filter (EKF)** is an extension of the standard Kalman Filter, designed to handle **non-linear system dynamics** and **non-linear measurement models**. It is used when the linearity assumptions of the standard KF do not hold, such as when the drone's movement and the measurement data are complex and non-linear.

#### **Description**
This script implements the EKF, which operates similarly to the Kalman Filter but with additional steps to linearize the non-linear dynamics. Specifically:
- The system dynamics and measurements are **non-linear**, meaning that a direct application of the Kalman Filter would be inaccurate.
- The EKF works by **linearizing** the non-linear models at each time step using Jacobians.
- In this context, the EKF is used for estimating the position of an AUV/ROV relative to a drone, where the **measurement model** converts feedback from **image space** (e.g., visual data) to real-world coordinates.

---

## Launch Files

### 1. `detector_only.launch.xml`
This launch file starts only the `detector` node, which executes the KNN-based detection algorithm.

#### Usage
```bash
ros2 launch state_estimation detector_only.launch.xml
```
This is useful in cases where only object detection is required without running the state estimator.

### 2. `estimator_detector.launch.xml`
This launch file starts both the `estimator` and `detector` nodes, allowing both state estimation and object detection to run simultaneously.

#### Usage
```bash
ros2 launch state_estimation estimator_detector.launch.xml
```
This is suitable when you need simultaneous estimation and detection.

---

## Why These Techniques?

- **KNN for Detection**: KNN is simple and effective when you have labeled sensor data. It's also non-parametric, meaning it doesn’t make strong assumptions about the data distribution, making it versatile in changing environments.
  
- **Kalman Filters**: The Kalman Filter (KF) and Extended Kalman Filter (EKF) are standard tools in robotics for state estimation. They help to smooth noisy sensor data and predict future states by combining predictions from motion models with observations. The EKF extends this capability to non-linear systems, making it ideal for drones that operate in non-linear environments.

---

## Example Workflow

1. Make sure your ROS 2 system is set up correctly with the necessary dependencies.
2. Ensure the drone is publishing sensor data, such as IMU and GPS.
3. Run the appropriate launch file based on your task:
   - For **only detection**: `ros2 launch state_estimation detector_only.launch.xml`
   - For **estimation and detection**: `ros2 launch state_estimation estimator_detector.launch.xml`

4. Verify that the nodes are receiving the data correctly, and check the console output for any state or detection information.

---

## Future Work

- **Integration with Deep Learning**: Future versions may integrate deep learning-based models (e.g., CNN) for detection instead of KNN.
- **SLAM Integration**: Incorporating simultaneous localization and mapping (SLAM) algorithms into the estimation pipeline.

---

## Maintainer

**Aryan Dolas**
- Email: aryand@kth.se

Feel free to contribute, report issues, or suggest improvements!

