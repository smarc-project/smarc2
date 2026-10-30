# ALARS object state estimation

This package estimates SAM, buoy and landing-pad poses from YOLO OBB detections,
camera calibration and TF. Each class has its own EKF, and the node then publishes
`alars_projection/object_poses_array` alongside `alars_ekf/status_array`
under the robot namespace.

Class dimensions, models and noise are defined in
[object_estimation.yaml](config/object_estimation.yaml), while shared settings
are in [ekf_params.yaml](config/ekf_params.yaml).

## Run

From the workspace root, with ROS Humble sourced:

```bash
colcon build --symlink-install --packages-up-to auv_state_estimation
source install/setup.bash
ros2 launch auv_state_estimation multi_ekf_launch.py \
  robot_name:=M350 camera_calibration_file:=z1_720p_cam_params.yaml
```

For Unity, use `camera_calibration_file:=sim_1080p_cam_params.yaml` and
`use_sim_time:=true`. Calibration comes from package YAML files and must match
the camera. Alternatively, `dji_bringup.sh` starts the EKF within the DJI stack.

## Landing pad

Under `classes.land_pad`, set the physical dimensions and
`parameters.measurement.geometry: flat_rectangle`. Since square-pad yaw is
ambiguous, measurements use the OBB center and sorted side lengths, assuming
a horizontal deck.

The `depth` motion model estimates Z and vertical velocity from YOLO, while
`surface` fixes Z. Accordingly, `environment.water_surface_height` sets nominal
map deck Z for `depth` and fixed Z for `surface`. To switch, change
`motion_model_type`, retain the geometry/dimensions and restart the EKF.

The [landing controller](../../../controllers/dji/landing_controller/README.md)
then selects the pad estimate and publishes `landing/pad_odom` through its adapter.
