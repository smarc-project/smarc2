# Camera Calibration

## Purpose
This document describes how to calibrate the monocular camera used for AUV estimation.

We use the ROS 2 package `camera_calibration` for this purpose.

For more details, see:  
https://docs.ros.org/en/rolling/p/camera_calibration/doc/index.html

---

## Requirements
Before starting, make sure:

- ROS 2 environment is sourced
- The camera is publishing images
- You have a checkerboard with known:
  - inner-corner dimensions (e.g. 8x6)
  - square size (in meters)

---

## Installation
Install the camera calibration package:

```bash
sudo apt install ros-<distro>-camera-calibration
```

Replace `<distro>` with your ROS 2 version (e.g. `humble`).

---

## Run Calibration

Run:

```bash
ros2 run camera_calibration cameracalibrator --size 8x6 --square 0.108 image:=/camera/image_raw camera:=/camera
```

---

## Parameters

- `--size`: number of inner corners
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

---

## Save Calibration

Click "Save" in the calibration window.

The result will be saved to:

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

Place the `.yaml` file in config and name it cam_params.
