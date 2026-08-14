# Evolo Prox-Ops Backend Contract

This document defines the first ROS interface contract between the Evolo prox-ops action servers and the target-tracking / graph-planning backend.

The action server is backend-agnostic. It does not own the graph, GTSAM, or the planner internals. Instead, the backend publishes target state, candidate path, planned control, and status. The action server safety-gates the backend output before forwarding control to Evolo.

## Backend To Action Server

### `backend/status`

Type:

```text
evolo_msgs/msg/ProxOpsBackendStatus
```

Purpose: backend health, current mode, track state, plan availability, and intercept outcome.

Proposed message:

```text
std_msgs/Header header

uint8 MODE_UNKNOWN=0
uint8 MODE_IDLE=1
uint8 MODE_WAITING_FOR_LONG_RANGE=2
uint8 MODE_LONG_RANGE_INTERCEPT=3
uint8 MODE_FUSED_INTERCEPT=4
uint8 MODE_TERMINAL_INTERCEPT=5
uint8 MODE_TARGET_LOST=6
uint8 MODE_INSPECT=7
uint8 mode

uint8 HEALTH_UNKNOWN=0
uint8 HEALTH_OK=1
uint8 HEALTH_DEGRADED=2
uint8 HEALTH_ERROR=3
uint8 health

bool long_range_track_live
bool long_range_track_converged
bool terminal_track_live
bool target_lost
bool plan_available
bool target_intercepted

float32 long_range_confidence
float32 terminal_confidence
float32 target_range_m

string status_text
```

Terminology:

```text
long_range_track
  External / long-distance target track used before close-proximity handoff.

terminal_track
  Close-proximity / endgame target track used for terminal intercept.

target_state
  Backend's fused or best estimate of the target.
```

### `backend/target_state`

Type:

```text
nav_msgs/msg/Odometry
```

Purpose: backend's best or fused target estimate, including pose and twist covariance.

Requirements:

```text
- header.stamp must be meaningful.
- header.frame_id must identify the estimate frame.
- child_frame_id should identify the target frame when available.
- pose covariance and twist covariance should be populated when known.
```

### `backend/candidate_path`

Type:

```text
nav_msgs/msg/Path
```

Purpose: current receding-horizon candidate path proposed by the backend.

The action server validates this path against safety and geofence constraints before forwarding planned control to Evolo.

### `backend/control_planned`

Type:

```text
nav_msgs/msg/Odometry
```

Purpose: backend's next desired control setpoint for the ASV.

The action server reads `pose.pose.orientation` (desired heading in the world/odom frame)
and `twist.twist.linear` (forward velocity in the body frame).  It forwards these to
`ctrl/control_planned` only if the latest candidate path is accepted as safe.

Requirements:

```text
- header.frame_id must not be empty and must identify the orientation reference frame
  (typically the odom / ENU world frame).
- pose.pose.orientation must be a valid, finite, non-zero quaternion.
- child_frame_id should be 'base_link' to indicate the twist reference frame.
- pose.pose.position is ignored by the action server; backends may leave it as zeros.
```

### `smarc/geofence_status`

Type:

```text
smarc_msgs/msg/GeofenceStatusStamped
```

Purpose: current geofence state published by `smarc_basic/geofence_node`.

When `evolo_target_intercept` is started with `geofence_check_enabled:=true`,
this status must be fresh and `STATUS_INSIDE` before backend control is
forwarded.

### `smarc/geofence_polygons`

Type:

```text
smarc_msgs/msg/GeofencePolygonsStamped
```

Purpose: map-frame geofence and island polygons published by
`smarc_basic/geofence_node`.

When `geofence_check_enabled:=true`, `evolo_target_intercept` validates
`backend/candidate_path` against these polygons through the reusable
`smarc_geofence_utils` C++ library.

The node parameter is the default. A specific intercept goal can override it:

```json
{
  "geofence_check_enabled": false
}
```

## Action Server To Backend

### `backend/command`

Type:

```text
std_msgs/msg/String
```

Purpose: JSON command topic from the prox-ops layer to the backend.

Current default model: `prox_ops_bt` sends `RESET` then `START` whenever it
accepts a new prox-ops goal. The BT/action layer then observes
`backend/status`, starts intercept only once the backend is healthy and
controlling, and gates `backend/control_planned` before forwarding to
`ctrl/control_planned`.

`evolo_target_intercept` does not publish START/STOP by default. Backend
lifecycle is owned by `prox_ops_bt`.

Initial commands:

```json
{"command": "START", "goal_id": "...", "config": {}}
{"command": "STOP", "goal_id": "...", "reason": "..."}
{"command": "RESET", "goal_id": "..."}
{"command": "PAUSE", "goal_id": "...", "reason": "..."}
{"command": "RESUME", "goal_id": "..."}
```

Command semantics:

```text
START
  Sent by prox_ops_bt after RESET when a new prox-ops goal starts. Start or arm
  the backend for prox-ops.

STOP
  Sent by prox_ops_bt after RESET when inspection timeout or patrol timeout is
  exceeded. Stop planning/control output for the current prox-ops run.

RESET
  Sent before START on new goal, and before STOP when inspection timeout or
  patrol timeout is exceeded. Clear backend state for a new run.

PAUSE
  Temporarily pause backend planning/control output.

RESUME
  Resume planning/control output after pause.
```

## Action Server To Controller

### `ctrl/control_planned`

Type:

```text
nav_msgs/msg/Odometry
```

Purpose: safety-gated control setpoint forwarded from the backend to Evolo.

Flow:

```text
backend/candidate_path
backend/control_planned
        |
        v
evolo_target_intercept safety gate
        |
        v
ctrl/control_planned
```

If the candidate path is unsafe, the action server does not forward `backend/control_planned`.

Current safety gate before forwarding:

```text
- backend/status must be fresh and newer than the action start.
- backend/candidate_path must be fresh and newer than the action start.
- backend/control_planned must be fresh and newer than the action start.
- backend/candidate_path must have a non-empty frame_id.
- backend/candidate_path must contain at least one pose.
- backend/candidate_path poses must not contradict the path frame_id.
- backend/control_planned must have a non-empty frame_id.
- backend/control_planned orientation quaternion must be finite and non-zero.
```

Optional geofence gate:

```text
- Enable with evolo_target_intercept parameter geofence_check_enabled:=true.
- smarc/geofence_status must be fresh.
- geofence status must be STATUS_INSIDE.
- smarc/geofence_polygons must be fresh.
- candidate_path frame_id must match geofence polygon frame_id.
- candidate_path points must be inside at least one geofence polygon.
- candidate_path points must not be inside an island polygon.
- candidate_path segments must not cross geofence or island boundaries.
```

## Prox-Ops Action Servers

```text
evolo_target_intercept
  Implemented C++ action. It owns the runtime control gate from backend output
  to ctrl/control_planned.

evolo_loiter_patrol
  Implemented C++ action. It delegates to Evolo's existing `move_to` action,
  alternates between two patrol waypoints, and remains RUNNING until the BT
  preempts or cancels it.

evolo_target_inspect
  Placeholder C++ action. It accepts goals and remains RUNNING until the BT
  post-condition/timeout preempts it. It does not command Evolo yet.
```

### `evolo_loiter_patrol` Goal

The action accepts either an explicit waypoint list:

```json
{
  "speed": "standard",
  "waypoints": [
    {"latitude": 58.822943, "longitude": 17.634076},
    {"latitude": 58.821758, "longitude": 17.634371}
  ]
}
```

or the older LoLo-style waypoint keys:

```json
{
  "speed": "standard",
  "loiter_1": [58.822943, 17.634076],
  "loiter_2": [58.821758, 17.634371]
}
```

Useful params:

```text
move_to_action_name        default: move_to
move_to_wait_timeout_s     default: 5.0
default_speed              default: standard
```

The action does not inspect backend status. `prox_ops_bt` owns the precondition
for when patrol should run and preempts patrol when another branch becomes
active.

## Contract Semantics

```text
1. All backend messages must be timestamped with the time they became valid.
2. The action server will treat stale status, path, and twist messages as unsafe.
3. The action server will not forward backend/control_planned unless the latest backend/candidate_path is safe.
4. backend/control_planned and backend/candidate_path should be consistent; the control setpoint should correspond to the currently published candidate path.
5. If the backend has no valid plan, set plan_available=false.
6. If backend health is HEALTH_ERROR, the action server may abort the intercept action.
7. If target_intercepted=true or mode=MODE_INSPECT, the BT will preempt intercept and move into inspection.
8. If target_lost=true for longer than the configured timeout, the BT will move to fallback behavior.
9. Frame IDs must be agreed ahead of time; candidate_path and target_state should be in a fixed world/map frame unless explicitly stated otherwise.
10. prox_ops_bt owns backend lifecycle: RESET/START on goal start, RESET/STOP on inspection or patrol timeout.
11. Backend messages older than the current action start are ignored, even if their fields indicate success or a valid plan.
12. Backend messages with zero timestamps are treated as stale.
13. Geofence validation reuses `smarc_basic/geofence_node` as the source of
    geofence status and map-frame polygons; the per-path geometry check lives in
    `smarc_geofence_utils`.
```

## Fake Backend

`fake_prox_ops_backend` defaults to `autostart:=false`, so it waits for
`prox_ops_bt` to publish `backend/command START`.

Useful params:

```text
autostart
publish_frequency_hz
long_range_convergence_delay_s
success_delay_s
target_range_start_m
target_range_rate_mps
```
