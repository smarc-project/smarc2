# waraps_officer

WARA-PS level 1 for a SMaRC vehicle. `waraps_vehicle` reads the vehicle's `smarc/*` topics and republishes them as JSON strings under `/<robot_name>/waraps/`.

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
