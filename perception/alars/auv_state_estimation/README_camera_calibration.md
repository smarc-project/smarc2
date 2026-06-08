# Camera Calibration

## Purpose
This document describes how to calibrate the camera used by the `auv_state_estimation` package.

For camera calibration we use the ROS2 package `camera_calibration`.

For more details, see:  
https://docs.ros.org/en/rolling/p/camera_calibration/doc/index.html

---
## Installation
To install the camera calibration package, run:

```bash
sudo apt install ros-humble-camera-calibration
```
---

## Requirements
Before starting, make sure:

- ROS 2 environment is sourced
- The camera is publishing images
- You have a checkerboard with known:
  - inner-corner dimensions (e.g. 8x6)
  - square size (in meters)

---
## Run Calibration

Run:

```bash
ros2 run camera_calibration cameracalibrator --size 8x6 --square 0.108 image:=/camera/image_raw camera:=/camera
```

Adjust `ìmage:=` and `camera:=` to match the setup (e.g. /M350/gimbal_camera/camera/image_raw)
---

## Parameters

- `--size`: number of inner corners (NOT squares)
- `--square`: size of one square
- `image:=`: image topic 
- `camera:=`: camera namespace 

---

## Calibration Procedure

- Move the checkerboard slowly in front of the camera
- Make sure you cover:
  - center
  - edges
  - different angles
  - different distances
- As you cover all areas the calibration sidebar will fill.

---

## Save Calibration

Click `"Save"` in the calibration window.

The result will be printed in the terminal and saved to:

```bash
/tmp/calibrationdata.tar.gz
```

Extract it:

```bash
tar -xvf /tmp/calibrationdata.tar.gz
```

This produces a `.yaml` file with camera intrinsics and distortion parameters.

---

## Using the Calibration

Place the `.yaml` file in config as `cam_params.yaml`.
