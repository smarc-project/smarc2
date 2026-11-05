# ALARS landing controller

Tracks a moving pad through alignment, descent and touchdown.
`alars_stack_landing.launch.py` starts the three landing nodes.

## Pipeline

```text
Camera → YOLO OBB → multi-object EKF (pose + status arrays)
  → landing_pad_odom_adapter → pad_landing/pad_odom
  → landing_relative_state (+ smarc/odom + gear TF) → pad_landing/relative_state
  → landing_manager (FSM + XY LQR + Z PD + command output) → cmd_vel → DJI captain
```

The manager combines the FSM, XY LQR/Z PD and command output, with helpers in `landing_control.py`, `landing_command.py` and `landing_action_server.py`. References and controller commands stay internal; status, controller debug and the `alars_land_on_pad` action expose progress. The FSM, control and output run at **50 Hz** with the default model (FSM frequency can be modified).


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

Examples use Unity; for hardware, use `use_sim_time:=false` in both the landing
stack and DJI captain.

```bash
ros2 launch landing_controller alars_stack_landing.launch.py \
  robot_name:=M350 use_sim_time:=true
```

Check that the moving-pad action has exactly one server,
`/M350/landing_manager`, before sending a goal.

```bash
ros2 action info /M350/alars_land_on_pad
```

Send a goal after launching the stack:

```bash
ros2 action send_goal /M350/alars_land_on_pad smarc_msgs/action/BaseAction \
  '{"goal": {"data": "{\"timeout\": 120.0, \"enable_descent\": true}"}}' --feedback
```

`enable_descent` defaults to `false` (tracking only), set it to `true` to allow descent. Goals start in IDLE, and successful landing returns to IDLE. Timeout runs abort climb/hold before failure.

Useful commands, run individually:

```bash
# Monitor state, tracking errors and estimate validity.
ros2 topic echo /M350/pad_landing/status

# Start tracking-only through the manager's service.
ros2 service call /M350/pad_landing/start std_srvs/srv/Trigger '{}'

# Abort: climb, hold, then return to IDLE.
ros2 service call /M350/pad_landing/abort std_srvs/srv/Trigger '{}'
```

## Main parameters

The launch passes [config/landing_params.yaml](config/landing_params.yaml) directly to each node.
Use `config_file` for another YAML and `pad_class_name` to select the pad class. Topics come from message-package constants.

### Landing manager

`IDLE → ACQUIRE → ALIGN → DESCEND → FINAL_DESCENT → TOUCHDOWN → LANDED → IDLE`

Each attempt resets timers, references and controller history. After movement, stopping sends one zero command and log, then output stays silent. The start/abort/reset services remain available; resetting an active action returns failure.

| Parameter | Meaning / current setting |
| --- | --- |
| `action_name`, `default_timeout` | Action: **alars_land_on_pad**. Goal timeout: **120 s**, overridden by the goal's `timeout`. |
| `update_rate_hz`, `minimum_align_height_m` | FSM: **50 Hz**. Minimum alignment clearance: **8 m**; higher initial clearance is retained with `capture_current_height_on_align`. |
| `align_xy_tolerance_m`, `align_speed_tolerance_mps`, `align_dwell_s` | XY error ≤ **0.35 m** and relative XY speed ≤ **0.2 m/s** for **2 s** before descent. |
| `descent_rate_mps`, `final_descent_height_m`, `final_descent_rate_mps` | Reference descent: **0.8 m/s**, slowing to **0.35 m/s** near **3 m**. Controller speed limits also apply. |
| `descent_pause_xy_m`, `descent_pause_speed_mps` | Pause reference descent above **0.2 m** XY error or **0.6 m/s** relative XY speed. |
| `touchdown_height_m`, `touchdown_detection_height_m` | Commanded clearance: **0.20 m**. Maximum clearance for touchdown detection: **0.25 m**. |
| `touchdown_xy_tolerance_m`, `touchdown_vertical_speed_mps`, `touchdown_dwell_s` | Touchdown also needs XY error ≤ **0.2 m** and absolute relative vertical speed ≤ **0.2 m/s** for **0.5 s**. |
| `touchdown_hold_s`, `turn_off_motors_on_landed` | Hold **1 s**, enter LANDED, request motor-off when enabled (**true** here). |
| `estimate_loss_abort_s`, `abort_xy_error_m` | Abort tracking after **2 s** of invalid estimates or XY error above **6 m**. |

Touchdown uses the estimated relative state. No physical-contact input is connected for now.

### Estimation and controller

| Parameter group | Important parameters |
| --- | --- |
| `landing_relative_state` | `max_drone_age_s`, `max_pad_age_s` and covariance-trace limits gate validity. `max_prediction_horizon_s` caps latency compensation at **0.2 s**. `publish_rate_hz` sets the output rate; `tf_fallback_to_latest` enables TF fallback. |
| `landing_pad_odom_adapter` | `max_prediction_s: 10.0` caps dropout prediction. `prediction_only_in_final_descent: true` restricts it to FINAL_DESCENT. |
| `landing_pad_odom_adapter` | `class_name` selects the EKF object; `require_status` and `max_covariance_trace` gate its estimate. `velocity_filter_tau_s` smooths pad velocity (**0.25 s**). |
| `landing_lqr_controller` | `q_diagonal_xy` weights position/velocity errors; `r_diagonal_xy` weights command effort. `z_kp` / `z_kd` tune vertical feedback. |
| `landing_lqr_controller` | `max_xy_speed_mps`, `max_xy_speed_final_mps`, `max_up_speed_mps`, `max_down_speed_mps` and `max_down_speed_final_mps` cap commands. `command_cutoff_hz` and `max_command_rate_mps2` smooth them. |
| `landing_manager` | `publish_rate_hz`: **50 Hz**. `controller_timeout_s` and `reference_timeout_s` stop forwarding stale commands/references. |

## Vehicle and pad models

The default velocity model comes from **dji_captain**:
`models/M350/discrete_model/discrete_models.yaml`, resolved through the ROS
package index. It sets the LQR rate to **50 Hz**, independently of the FSM rate.
Override `model_path` at launch for another vehicle/model. In the YAML's
`landing_lqr_controller` group, `model_kind` selects `auto`, `discrete` or
`continuous`; continuous models are discretized. NPZ files without timing metadata
need `model_sample_time_s`, e.g. `0.02` for 50 Hz.

In [object_estimation.yaml](../../../perception/alars/auv_state_estimation/config/object_estimation.yaml),
switch `classes.land_pad.motion_model_type` between `depth` (estimate Z/vertical
velocity) and `surface` (fixed deck Z). Keep `parameters.measurement.geometry`
set to `circle`, then restart the EKF.
`environment.water_surface_height` is nominal deck Z for `depth` and fixed Z for
`surface`. Calibration and height-reference setup are covered in the
[estimation README](../../../perception/alars/auv_state_estimation/README.md).
