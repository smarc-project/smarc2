# AUV Localization Package

## Overview

The `auv_detector` package is responsible for performing perception and estimation tasks in ROS 2, particularly designed for quadrotors or similar UAVs. It includes several estimation techniques, such as K-Nearest Neighbors (KNN) and an extended Kalman Filter (EKF), integrated into a ROS 2 environment to estimate the state of the drone and that of an AUV/ROV on water surface, relative to the drone in real time.

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
- The drone needs to be set up to provide real-time data such as depth sensor and camera, published to the correct topics in ROS 2 for proper state estimation. The estimator publishes a detection in the camera space whose subscription callback is where the estimator is called and an the data is fused to make a gloval georeferenced estimate of the AUV.

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

### 2. **auv_detector.py**
This script is responsible for data fusion and goreferencing of the image space feedback. It is the core state estimation node.

#### Purpose

- To estimate the position of AUV relative to the drone

#### Dependencies
- Needs access to TF frames for calculating transformations between the drone's body frame and world frame.

Certainly! Below is a more refined version of the descriptions for **model_kf.py** and **model_ekf.py** that clearly outlines the purpose, functionality, and context of each filter:

---


### **3. model_ekf.py (Extended Kalman Filter)**

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
  
- **Kalman Filters**: The Extended Kalman Filter (EKF) is a standard tool in robotics for state estimation. They help to smooth noisy sensor data and predict future states by combining predictions from motion models with observations. The EKF extends this capability to non-linear systems, making it ideal for drones that operate in non-linear environments.

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

---

## Maintainer

**Aryan Dolas**
- Email: aryand@kth.se

Feel free to contribute, report issues, or suggest improvements!

