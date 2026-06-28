# WARA-PS MQTT-agent to ROS-agent.
Small utility node that uses the [`str_json_mqtt_bridge`]() package to listen
to a given WARA-PS agent broadcasting its state over MQTT, and republishes it
in ROS. The topics republished by the node are:
  - `MQTT_AGENT_NAME/odom`: an `Odometry` message whose covariance is given
  by the user to roughly approximate its shape.
  - `MQTT_AGENT_NAME/latlon`: a `GeoPoint` message with its coordinates in lat/lon.

Example for running:
```
ros2 launch mqtt_to_ros_agent mqtt_to_ros_agent.launch broker_addr:=20.240.40.232 broker_port:=1884 robot_name:=evolo mqtt_agent_name:=aldo_evolo domain:=surface ellipse_x_m:=1.0 ellipse_y_m:=0.5

```
