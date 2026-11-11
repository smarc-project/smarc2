# waraps_officer

WARA-PS agent nodes for a SMaRC vehicle. `waraps_vehicle` is level 1. `waraps_officer` is levels 2 and 3: it runs one task at a time on the vehicle's action servers.

Everything is plain `std_msgs/String` carrying JSON, for `str_json_mqtt_bridge` to put on the broker.

## waraps_vehicle

Runs in the robot namespace. Replaces `wasp_bt.waraps.waraps_vehicle`, which goes when `wasp_bt` is deleted with the rest of the behaviour tree; until then the bringups pick one.

```bash
ros2 launch waraps_officer waraps_vehicle.launch robot_name:=sam0 agent_type:=underwater pulse_rate:=1.0 use_sim_time:=true
```

### Subscribes

All relative to the robot namespace, all from `smarc_msgs/msg/Topics`.

| Constant | Type | Becomes |
|---|---|---|
| `POS_LATLON_TOPIC` | `geographic_msgs/GeoPoint` | `sensor/position`. `altitude` is the GeoPoint's own field, relative to the water level. |
| `ALTITUDE_TOPIC` | `std_msgs/Float32` | `sensor/altitude`, height above the ground below, a JSON number |
| `HEADING_TOPIC`, `COURSE_TOPIC`, `SPEED_TOPIC`, `DEPTH_TOPIC` | `std_msgs/Float32` | `sensor/heading`, `sensor/course`, `sensor/speed`, `sensor/depth`, each a JSON number |
| `ODOM_TOPIC` | `nav_msgs/Odometry` | `sensor/roll`, `sensor/pitch` (radians, from the orientation quaternion) |

### Publishes (once per pulse)

| Constant | Payload |
|---|---|
| `WARA_PS_HEARTBEAT_TOPIC` | `{"agent-type", "agent-uuid", "levels", "name", "rate", "stamp", "type": "HeartBeat"}` |
| `WARA_PS_SENSOR_*_TOPIC` | one per reading that is finite and younger than `stale_after_s`. A publisher is created the first time a reading qualifies, so a vehicle with no depth sensor never advertises `sensor/depth`. |
| `WARA_PS_SENSOR_INFO_TOPIC` | `{"name", "rate", "sensor-data-provided": [...], "stamp", "type": "SensorInfo"}` |

`sensor-data-provided` is read off the graph: every `std_msgs/String` topic that a node under `/<robot_name>` publishes under `WARA_PS_SENSOR_PREFIX` (`waraps/sensor`), by the part of the name after the prefix. This node's own sensors are in it, and so is anything another node adds (a stick publishing `waraps/sensor/acoustic`). Nothing to configure. The scan is `smarc_utilities.topic_utils.node_string_topics_under`, the same one the bridge uses.

`levels` is `["sensor"]`, plus `"direct_execution"` while some node under the robot publishes `WARA_PS_DIRECT_EXECUTION_INFO_TOPIC`, plus `"tst_execution"` likewise for `WARA_PS_TST_EXEC_INFO_TOPIC`. No subscription; it counts publishers.

### Parameters

| Name | Default | |
|---|---|---|
| `robot_name` | required | `name` in heartbeat and sensor_info; the node refuses to start without it |
| `agent_type` | `air` | `agent-type` in the heartbeat (`underwater`, `surface`, `air`, ...) |
| `pulse_rate` | `1.0` | Hz; one heartbeat, sensor sweep and sensor_info per pulse |
| `agent_uuid` | `""` → random uuid4 | fixed id if the WARA-PS side needs one |
| `stale_after_s` | `10.0` | a reading older than this is not published |
| `use_sim_time` | | stamps and staleness follow the ROS clock |

### Tests

```bash
cd behaviours/smarc/waraps_officer && python3 -m pytest -q
```

`level1.py` has no rclpy. The live tests run on a private ROS domain: a fake vehicle publishes lat/lon, depth and odom, and the node republishes them as JSON.

## waraps_officer

Runs tasks. One at a time: a `start-task` while anything is running is rejected, and a TST is accepted only as a flat `seq`, whose next leaf starts when the current one finishes. A `conc` or a nested container is rejected with `rejected: only a flat seq is supported`.

```bash
ros2 launch waraps_officer waraps_officer.launch robot_name:=sam0 use_sim_time:=true
```

The node lives in the robot namespace, next to `waraps_vehicle`. It reads `agent-uuid` from the first `waraps/heartbeat` and then drops that subscription.

### Subscribes

| Constant | Type | |
|---|---|---|
| `WARA_PS_ACTION_SERVER_HB_TOPIC` | `std_msgs/String` | the ROS action name. The task name is its last segment, `_` written as `-`. A server that goes quiet for `task_liveliness_timeout` is dropped. |
| `WARA_PS_EXEC_COMMAND_TOPIC` | `std_msgs/String` | JSON: `ping`, `start-task`, `signal-task`, `query-task`, `signal-unit` |
| `WARA_PS_TST_COMMAND_TOPIC` | `std_msgs/String` | JSON: `start-tst`, `signal-unit` |
| `WARA_PS_ABORT_TOPIC` | `std_msgs/String` | cancel every task and publish `ABORT_TOPIC` |
| `WARA_PS_HEARTBEAT_TOPIC` | `std_msgs/String` | one `agent-uuid`, then unsubscribed |
| `VEHICLE_HEALTH_TOPIC` | `std_msgs/Int8` | last value and its stamp |

`start-task` and `start-tst` are refused with `rejected: vehicle health status is not ok` unless the last health is `VEHICLE_HEALTH_READY` and younger than `health_timeout_s`. They are refused with `task not available` when that server is not heartbeating, and with `task already executing on <name>` while a task is running. A `custom-task` uses `params.action-name` as the task name.

While health is `WAITING`, `ERROR`, or silent past `health_timeout_s`, every running task is cancelled and reported as `cancelled: vehicle health <STATE>`.

`signal-unit` `$abort` and `WARA_PS_ABORT_TOPIC` also publish `smarc/abort` (`Empty`). The captain decides what that does to the actuators. `$abort` and `$enough` on one task cancel that task and do not publish `smarc/abort`. `$cancel_abort` is rejected: there is no emergency flag here.

### Publishes

| Constant | When |
|---|---|
| `WARA_PS_DIRECT_EXECUTION_INFO_TOPIC` | every pulse. `tasks-available`, `tasks-executing` |
| `WARA_PS_TST_EXEC_INFO_TOPIC` | every pulse, same body, `type: TSTExecutionInfo` |
| `WARA_PS_EXEC_RESPONSE_TOPIC`, `WARA_PS_TST_RESPONSE_TOPIC` | one per command |
| `WARA_PS_EXEC_FEEDBACK_TOPIC`, `WARA_PS_TST_FEEDBACK_TOPIC` | every pulse, per running task, carrying the action server's feedback |
| `WARA_PS_SENSOR_EXECUTING_TASKS_TOPIC` | every pulse. `[{task-uuid, task-name, status, description}]` |
| `ABORT_TOPIC` | unit abort only |

A goal sent to an action server is `json.dumps` of the task's `params`. `params.timeout` (seconds) cancels the goal from the client; a TST leaf without one has no client timeout, and a mission without `params.timeout` runs for 1800 s.

```json
{"command": "start-task", "com-uuid": "c1", "task-uuid": "t1", "task": {"name": "move-to", "params": {"waypoint": {"latitude": 58.85, "longitude": 17.67}}}}
```

### Parameters

| Name | Default | |
|---|---|---|
| `robot_name` | required | `name` in the execution info; the node refuses to start without it |
| `pulse_rate` | `1.0` | Hz; execution info, feedback, `tasks-executing` |
| `tick_rate` | `10.0` | Hz; `step()` polls the action clients |
| `task_liveliness_timeout` | `10.0` | seconds without an action-server heartbeat before it is forgotten |
| `health_timeout_s` | `10.0` | a health sample older than this means the vehicle is not ready |
| `use_sim_time` | | stamps follow the ROS clock |

`commands.py` has no rclpy; the health numbers it compares are `Topics.VEHICLE_HEALTH_*`. `Officer.step` is run against a fake client. The live tests run on a private ROS domain: one rejects a start while health is `ERROR`, one drives a `GentlerActionServer` through `start-task` until `tasks-executing` is empty.
