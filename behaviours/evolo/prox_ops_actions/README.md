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
uint8 MODE_SUCCESS=7
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
bool intercept_success

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

### `backend/twist_planned`

Type:

```text
geometry_msgs/msg/TwistStamped
```

Purpose: backend's next desired control setpoint for the ASV.

The action server forwards this to `ctrl/twist_planned` only if the latest candidate path is accepted as safe.

## Action Server To Backend

### `backend/command`

Type:

```text
std_msgs/msg/String
```

Purpose: JSON command topic from the action server to the backend.

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
  Start or arm the backend for the current intercept goal.

STOP
  Stop planning/control output for the current goal. The backend must clear or invalidate terminal state for the stopped goal, including intercept_success, target_lost, plan_available, candidate path, and planned twist. A future START must not reuse stale state from a previous goal.

RESET
  Clear backend state for a new run.

PAUSE
  Temporarily pause backend planning/control output.

RESUME
  Resume planning/control output after pause.
```

## Action Server To Controller

### `ctrl/twist_planned`

Type:

```text
geometry_msgs/msg/TwistStamped
```

Purpose: safety-gated control setpoint forwarded from the backend to Evolo.

Flow:

```text
backend/candidate_path
backend/twist_planned
        |
        v
evolo_target_intercept safety gate
        |
        v
ctrl/twist_planned
```

If the candidate path is unsafe, the action server does not forward `backend/twist_planned`.

Current safety gate before forwarding:

```text
- backend/status must be fresh and newer than the action start.
- backend/candidate_path must be fresh and newer than the action start.
- backend/twist_planned must be fresh and newer than the action start.
- backend/candidate_path must have a non-empty frame_id.
- backend/candidate_path must contain at least one pose.
- backend/candidate_path poses must not contradict the path frame_id.
- backend/twist_planned must have a non-empty frame_id.
```

Geofence/path-boundary validation will be added on top of this gate.

## Contract Semantics

```text
1. All backend messages must be timestamped with the time they became valid.
2. The action server will treat stale status, path, and twist messages as unsafe.
3. The action server will not forward backend/twist_planned unless the latest backend/candidate_path is safe.
4. backend/twist_planned and backend/candidate_path should be consistent; the twist should correspond to the currently published candidate path.
5. If the backend has no valid plan, set plan_available=false.
6. If backend health is HEALTH_ERROR, the action server may abort the intercept action.
7. If intercept_success=true, the action server may return action success and stop forwarding intercept commands.
8. If target_lost=true for longer than the configured timeout, the BT will move to fallback behavior.
9. Frame IDs must be agreed ahead of time; candidate_path and target_state should be in a fixed world/map frame unless explicitly stated otherwise.
10. backend/command STOP means stop planning/control output for the current goal; RESET means clear backend state for a new run.
11. Backend messages older than the current action start are ignored, even if their fields indicate success or a valid plan.
12. Backend messages with zero timestamps are treated as stale.
```

