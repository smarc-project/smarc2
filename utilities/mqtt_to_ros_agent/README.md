# WARA-PS MQTT-agent to ROS-agent.
Small utility node that turns one WARA-PS agent's sensor strings into ROS
odometry. The launch starts [`str_json_mqtt_bridge`]() with
`mqtt.to_ros_agents` set to `<user>_<robot>` (the last segment of the broker
path). The bridge publishes `/<user>_<robot>/waraps/sensor/...`. This node
reads those strings and republishes:
  - `MQTT_AGENT_NAME/odom`: an `Odometry` message whose covariance is given
  by the user to roughly approximate its shape.
  - `MQTT_AGENT_NAME/latlon`: a `GeoPoint` message with its coordinates in lat/lon.

Example for running:
```
ros2 launch mqtt_to_ros_agent mqtt_to_ros_agent.launch broker_addr:=20.240.40.232 broker_port:=1884 robot_name:=evolo mqtt_agent_name:=aldo_evolo domain:=surface ellipse_x_m:=1.0 ellipse_y_m:=0.5

```
