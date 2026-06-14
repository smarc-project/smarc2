# prox_ops_bt

Python behaviour tree action server for Evolo prox-ops missions.

## Goal Format

`prox_ops_bt` uses `smarc_msgs/action/BaseAction`. The mission JSON is carried
in `BaseAction.goal.data`.

The preferred WARA-compatible form wraps the mission in `json-params`:

```json
{
  "json-params": "{\"inspect\":{\"timeout_s\":5.0},\"intercept\":{\"geofence_check_enabled\":false},\"loiter_patrol\":{\"timeout_s\":30.0,\"speed\":\"standard\",\"waypoints\":[{\"latitude\":58.822943,\"longitude\":17.634076},{\"latitude\":58.821758,\"longitude\":17.634371}]}}"
}
```

For developer tests, the server also accepts the inner mission object directly:

```json
{
  "inspect": {"timeout_s": 5.0},
  "intercept": {"geofence_check_enabled": false},
  "loiter_patrol": {
    "timeout_s": 30.0,
    "speed": "standard",
    "waypoints": [
      {"latitude": 58.822943, "longitude": 17.634076},
      {"latitude": 58.821758, "longitude": 17.634371}
    ]
  }
}
```

See `goal_example.json` and `goal_example.md` for a complete example and field
descriptions.

## Sending A Goal

```bash
GOAL_JSON="$(jq -c . install/share/prox_ops_bt/goal_example.json)"
ros2 action send_goal /evolo/prox_ops_bt smarc_msgs/action/BaseAction \
"{goal: {data: '${GOAL_JSON}'}}"
```
