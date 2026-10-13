# ALARS landing controller

Tracks a moving pad through alignment, descent and touchdown.
`alars_stack_landing.launch.py` starts the five landing nodes.

## Pipeline

```text
Camera → YOLO OBB → multi-object EKF (pose + status arrays)
  → landing_pad_odom_adapter → landing/pad_odom
  → landing_relative_state (+ smarc/odom + gear TF) → landing/relative_state
  → landing_manager → landing/reference + landing/status
  → landing_lqr_controller (XY LQR + Z PD) → landing/controller_cmd
  → landing_velocity_command_mux → cmd_vel → DJI captain
```

`robot_name` selects the namespace. For M350, positions use `M350/map` and
commands use `M350/base_flat_link`.As well, **relative height is clearance from
`M350/landing_gear_center_link` to the estimated pad**; zero means estimated deck
contact. Missing gear TF invalidates the state.

## Build and run

From the ROS workspace root:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-up-to landing_controller dji_captain alars dji_msgs
source install/setup.bash
```

Examples use Unity; use `use_sim_time:=false` in both
commands for hardware.

```bash
ros2 launch landing_controller alars_stack_landing.launch.py \
  robot_name:=M350 model_kind:=discrete use_sim_time:=true auto_start:=false enable_descent:=true
```

```bash
ros2 run alars alars_land_action_server --ros-args \
  -r __ns:=/M350 -p use_sim_time:=true
```

Check that the moving-pad action has exactly one server,
`/M350/alars_land_action_server`, before sending a goal:

```bash
ros2 action info /M350/alars_land_on_pad
```

Send a goal once the manager publishes fresh landing status:

```bash
ros2 action send_goal /M350/alars_land_on_pad smarc_msgs/action/BaseAction \
  '{"goal": {"data": "{\"timeout\": 120.0}"}}' --feedback
```

Useful commands, run individually:

```bash
# Monitor state, tracking errors and estimate validity.
ros2 topic echo /M350/landing/status

# Start directly through the manager instead of sending an action goal.
ros2 service call /M350/landing/start std_srvs/srv/Trigger '{}'

# Abort: climb, hold, then return to IDLE.
ros2 service call /M350/landing/abort std_srvs/srv/Trigger '{}'
```

## Main parameters

The parameters can be found in [config/landing_params.yaml](config/landing_params.yaml). Launch arguments
override matching YAML values, might need to restart the stack after editing.

### Landing manager

`IDLE → ACQUIRE → ALIGN → DESCEND → FINAL_DESCENT → TOUCHDOWN → LANDED`

| Parameter | Meaning / current setting |
| --- | --- |
| `auto_start`, `enable_descent` | Launch defaults: both **false**. Auto-start begins once a valid estimate arrives; otherwise send a goal. Enabling descent allows ALIGN to advance. |
| `update_rate_hz`, `minimum_align_height_m` | FSM: **40 Hz**. Minimum alignment clearance: **8 m**; higher initial clearance is retained with `capture_current_height_on_align`. |
| `align_xy_tolerance_m`, `align_speed_tolerance_mps`, `align_dwell_s` | XY error ≤ **0.2 m** and relative XY speed ≤ **0.2 m/s** for **2 s** before descent. |
| `descent_rate_mps`, `final_descent_height_m`, `final_descent_rate_mps` | Reference descent: **0.8 m/s**, slowing to **0.35 m/s** near **3 m**. Controller speed limits also apply. |
| `descent_pause_xy_m`, `descent_pause_speed_mps` | Pause reference descent above **0.2 m** XY error or **0.6 m/s** relative XY speed. |
| `touchdown_height_m`, `touchdown_detection_height_m` | Commanded clearance: **0.20 m**. Maximum clearance for touchdown detection: **0.25 m**. |
| `touchdown_xy_tolerance_m`, `touchdown_vertical_speed_mps`, `touchdown_dwell_s` | Touchdown also needs XY error ≤ **0.2 m** and absolute relative vertical speed ≤ **0.2 m/s** for **0.5 s**. |
| `touchdown_hold_s`, `turn_off_motors_on_landed` | Hold **1 s**, enter LANDED, request motor-off when enabled (**true** here). |
| `estimate_loss_abort_s`, `abort_xy_error_m` | Abort tracking after **2 s** of invalid estimates or XY error above **6 m**. |

Touchdown uses the estimated relative state. No physical-contact input is connected for now.

### Estimation and controller

| Node section | Important parameters |
| --- | --- |
| `landing_relative_state` | `max_drone_age_s`, `max_pad_age_s` and covariance-trace limits gate validity. `max_prediction_horizon_s` caps latency compensation at **0.2 s**. |
| `landing_pad_odom_adapter` | `max_prediction_s: 10.0` caps dropout prediction. `prediction_only_in_final_descent: true` restricts it to FINAL_DESCENT. |
| `landing_lqr_controller` | `q_diagonal_xy` weights position/velocity errors; `r_diagonal_xy` weights command effort. `z_kp` / `z_kd` tune vertical feedback. |
| `landing_lqr_controller` | `max_xy_speed_mps`, `max_xy_speed_final_mps`, `max_up_speed_mps`, `max_down_speed_mps` and `max_down_speed_final_mps` cap commands. `command_cutoff_hz` and `max_command_rate_mps2` smooth them. |
| `landing_velocity_command_mux` | `controller_timeout_s` and `reference_timeout_s` stop forwarding stale landing commands. |

## Vehicle and pad models

The default velocity model comes from **dji_captain**:
`models/M350/discrete_model/discrete_models.yaml`, resolved through the ROS
package index. It sets the LQR rate to **50 Hz**, independently of the FSM rate.
Override `model_path` and `model_kind` (`auto`, `discrete`, `continuous`) for another
vehicle/model; continuous models are discretized. `robot_name` only changes the
namespace. NPZ files without timing metadata need `model_sample_time_s`,
e.g. `0.02` for 50 Hz.

In [object_estimation.yaml](../../../perception/alars/auv_state_estimation/config/object_estimation.yaml),
switch `classes.land_pad.motion_model_type` between `depth` (estimate Z/vertical
velocity) and `surface` (fixed deck Z). Keep `parameters.measurement.geometry`
set to `flat_rectangle`, then restart the EKF.
`environment.water_surface_height` is nominal deck Z for `depth` and fixed Z for
`surface`. Calibration and height-reference setup are covered in the
[estimation README](../../../perception/alars/auv_state_estimation/README.md).
