# STRING JSON MQTT Bridge

## Why this when the general purpose mqtt_bridge exists?
Because if you put a JSON, in string form, inside a ROS std_msgs::String, and send pass it through the `mqtt_bridge`, then the MQTT ouput looks like this:

`{"data":"your json string"}`

Why? Because `mqtt_bridge` is _very general_ and creates a JSON object from each field of a ROS message. A `std_msgs::String` (and any other primitive type) has one field: `data`.

This is annoying when you already have a perfectly well-formed JSON you expected to see as-is in MQTT, for example if you are implementing [the waraps API](https://api-docs.waraps.org).

This bridge ***ONLY*** works with JSON strings.

## Example

> See `config/waraps.yaml`

> See `launch/waraps_bridge.launch`

### ROS to MQTT
```
moquitto -p 1889
ros2 launch str_json_mqtt_bridge waraps_bridge.launch
ros2 topic pub /sam0/waraps/sensor/heading std_msgs/msg/String "{data: ' {\"key\":{\"key2\":\"value\"}} ' }"
```
You should see the JSON in MQTT now.

### MQTT to ROS
```
moquitto -p 1889
ros2 launch str_json_mqtt_bridge waraps_bridge.launch
```

Publish something from MQTT Explorer, ex: publish `{"hi": 5,"hello": "123"}` to `waraps/unit/subsurface/simulation/ozer_sam0/exec/command` 

```
ros2 topic echo /sam0/waraps/exec/command
```

You should see `data: '{"hi": 5,"hello": "123"}'` 

In your application, to recover the JSON object from this string, you should do:

```python
import ast
json_obj = ast.literal_eval(msg.data)
```

> **Eval?!?!** Relax. `ast.literal_eval` only evaluates primitive objects, lists and dicts. It won't _run_ anything.


## Footguns
- Be careful of quotation marks. Terminals, ROS, JSON, MQTT all have their own quirks with them...
- This bridge CAN consume it's own output. If you put the same topic in both `ros_to_mqtt` and `mqtt_to_ros` fields, the first message in either direction will create an epic spammer.







