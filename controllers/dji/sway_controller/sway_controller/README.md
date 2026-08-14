# sway_controller

Payload sway estimation and damping for a hook hanging on a rope below a DJI
M350. Provides the estimator and the control pieces that
`alars_move_to_dumped_action_server` (package `alars`) uses to fly a mission
without exciting the payload.

The hook is modelled as a **damped spherical pendulum, decoupled per axis**,
linearised about hanging straight down. Everything lives in
`<robot>/base_flat_link` — gravity-aligned, but yawing with the drone.

---

## Data flow

```
   YOLO detections ─┐
                    ├─> HookKalmanFilter ──> hook_swing_state ─┐
   smarc/odom ──────┤        (50 Hz)         hook_state        │
   cmd_vel_drone_frame ─┘                    hook_raw_measurement
                                                               │
   EstimateLengthAndDamping ──> hook_pendulum_params_identified │
        (action, one shot)              │                      │
                                        v                      v
                            HookKalmanFilter ──> hook_pendulum_params
                                                        │      │
                                                        v      v
                                        alars_move_to_dumped_action_server
                                          PathParametrizer -> ZVD -> LQR
                                                        │
                                                        v
                                               velocity setpoint (cmd_vel)
```

All names here are **relative**: the nodes are launched into the `/<robot>`
namespace (`ros2 launch sway_controller <node>_launch.py robot_name:=M350`),
never with `ros2 run`. TF frame ids are the exception - they still carry the
`<robot>/` prefix, because frames are not namespaced.

`u = v_feedforward(ZVD) + trim(LQR)` — **the LQR corrects the plan, it never
replaces it.** A persistently large trim means the plan and the plant disagree
(wrong `L`/`xi`, or a real disturbance).

### Topics

| topic | type | QoS | 
|---|---|---|---|
| `hook_pendulum_params_identified` | `Float64MultiArray` (`length`,`damping`) | **latched** 
| `hook_pendulum_params` | `Float64MultiArray` (`length`,`damping`) | **latched** |
| `hook_swing_state` | `JointState` (pos=θ, vel=ω, effort=var) | BEST_EFFORT |
| `hook_state` | `Odometry` (cartesian hook pose) | BEST_EFFORT |
| `hook_raw_measurement` | `Odometry` | BEST_EFFORT |
| `hook_ground_truth_base_flat` | `Odometry` | default |


---

## Files

### `PathParametrizer.py`
Parametrises position/velocity references from the drone's current position to
the goal, along a C² quintic in arc length so acceleration is continuous.

### `ZVD.py`
Zero-Vibration-Derivative input shaper: convolves the reference with three
impulses spaced at half the damped period, so the trailing impulses cancel the
vibration the leading ones excite. Takes the **same `L`/`xi` as the filter**, so
one bad identification degrades both together rather than making them disagree.
Assumes the linear model. Method:
<https://www.tandfonline.com/doi/full/10.1080/21642583.2023.2188401#d1e156>


### `LQG.py` (class `LQR`)
State feedback for the drone+payload. Builds its own 10-state model from
`L, xi` and the drone's identified velocity response `(k, tau)` per axis, so a
caller constructs one per mission:

```
index  0 1 2   3 4 5   6       7       8       9
state  p_x p_y p_z  v_x v_y v_z  theta_x omega_x theta_y omega_y
input  u = [vx_cmd, vy_cmd, vz_cmd]   (velocity setpoints, base_flat_link)
```
Weights are Bryson (`1/max_dev²`), so the tolerances **are** the tuning knobs.

### `EstimateLengthAndDamping.py`
Action `<robot>/estimate_length_and_damping`. Captures equilibrium → velocity
step to excite a swing → observes free decay via YOLO detections → fits the
period (`L = g/(2π/T)²`) and the log-decrement (`xi`).

Picks **which image axis to fit from the data** (`_select_axis`): the
image→body mapping depends on gimbal orientation, so a hardcoded axis can end
up fitting the un-excited, noise-dominated one.

The result leaves via the **latched topic**, not the action Result: `BaseAction`'s
Result is only `bool success`, *and* `GentlerActionServer` publishes feedback
only while `_loop_inner` returns `None`, so no final feedback is ever emitted.

### `HookKalmanFilter.py`
4-state `[θx, ωx, θy, ωy]` KF. Prediction is **re-discretized every tick with
the measured `dt`**, so an irregular or clock-limited rate stays correct.

Measurement: the detection ray is rotated from the camera optical frame into
`base_flat_link` **through TF**, then intersected with the sphere of radius `L` about
`rope_base_link`.

Refuses to start without usable `L`/`xi`; inventing a pendulum would mistune the
estimator and, via `hook_pendulum_params`, the controller too.

