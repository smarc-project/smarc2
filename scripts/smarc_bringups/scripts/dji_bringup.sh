#! /bin/bash

ROBOT_NAME=M350
SESSION=${ROBOT_NAME}_bringup

# check if there is already a tmux session with this name
if tmux has-session -t $SESSION 2>/dev/null; then
    echo "There is already a tmux session named $SESSION."
    echo "Please close it before launching this script."
    echo "Exiting."
    exit 1
fi

MQTT_ADDR=20.240.40.232
MQTT_PORT=1884

if [[ "$(whoami)" == *"alars"* ]]; then
    USE_SIM_TIME=False
    REALSIM="real"
else
    USE_SIM_TIME=True
    REALSIM="simulation"
fi

# the mqtt stuff on unity on linux is wonky, so use localhost for that
# a broker will be launched in a tmux pane later.
if [[ "$(uname)" == "Linux" ]]; then
    ON_LINUX=True
else
    ON_LINUX=False
fi


if [[ $ON_LINUX == "True" && $USE_SIM_TIME == "True" ]]; then
    MQTT_ADDR=localhost
    MQTT_PORT=1889
fi

HOME_ABOVE_WATER=$1
if [[ -z "$HOME_ABOVE_WATER" ]]; then
    echo "You must pass the home altitude above water level as the first argument!"
    echo "This is required for the dji_captain node to function properly."
    echo "Exiting."
    exit 1
fi

# New variables for wasp_bt.launch and wasp_mqtt_agent.launch
AGENT_TYPE=air
PULSE_RATE=10.0

# create a tmux session with a name
tmux -2 new-session -d -s $SESSION




# create a bunch of windows. These are the "tabs" you'll
# see at the bottom green line.
# C-b <NUM> will change to the tab.
# default window is 0

tmux new-window -t $SESSION:0 -n 'Captains'
tmux rename-window "Captains"
# only launch if not the simulator
if [[ $USE_SIM_TIME = "False" ]]; then
    # PSDK_ROS2_BRIDGE
    
    tmux select-window -t $SESSION:0
    # split the first window into two panes
    tmux split-window -h -t $SESSION:0.0      # Split window into left (0.0) and right (0.1)
    tmux split-window -v -t $SESSION:0.0      # Split left pane into top-left (0.0) and bottom-left (0.2)
    tmux split-window -v -t $SESSION:0.1      # Split right pane into top-right (0.1) and bottom-right (0.3)
    tmux select-layout -t $SESSION:0 tiled    # Arrange as a 2x2 grid
    # 0.0 | 0.1
    # ----+----
    # 0.2 | 0.3
    tmux select-pane -t $SESSION:0.0
    tmux send-keys "ros2 launch psdk_wrapper wrapper.launch.py namespace:=/$ROBOT_NAME/wrapper" C-m
    
    tmux select-pane -t $SESSION:0.1
    tmux send-keys "ros2 run dji_captain dji_captain --ros-args -p use_sim_time:=$USE_SIM_TIME  -p home_altitude_above_water:=$HOME_ABOVE_WATER -r __ns:=/$ROBOT_NAME " C-m

    tmux select-pane -t $SESSION:0.2
    tmux send-keys "fast-discovery-server -i 0" C-m
    
    tmux select-pane -t $SESSION:0.3
    tmux send-keys "ros2 topic echo /$ROBOT_NAME/captain_status std_msgs/msg/String --field data" C-m

else
    tmux select-window -t $SESSION:0
    tmux split-window -h -t $SESSION:0.0
    tmux select-pane -t $SESSION:0.0
    tmux send-keys "ros2 run dji_captain dji_captain --ros-args -p use_sim_time:=$USE_SIM_TIME  -p home_altitude_above_water:=$HOME_ABOVE_WATER -r __ns:=/$ROBOT_NAME " C-m

    tmux select-pane -t $SESSION:0.1
    tmux send-keys "ros2 topic echo /$ROBOT_NAME/captain_status std_msgs/msg/String --field data" C-m
fi


# action servers
tmux new-window -t $SESSION:1 -n 'ALARSActions'
tmux rename-window "ALARSActions"
tmux select-window -t $SESSION:1
tmux split-window -h -t $SESSION:1.0      # Split window into left (0.0) and right (0.1)
tmux split-window -v -t $SESSION:1.0      # Split left pane into top-left (0.0) and bottom-left (0.2)
tmux split-window -v -t $SESSION:1.1      # Split right pane into top-right (0.1) and bottom-right (0.3)
tmux select-layout -t $SESSION:1 tiled    # Arrange as a 2x2 grid

tmux select-pane -t $SESSION:1.0
tmux send-keys "ros2 launch alars_auv_search_planner search_planning_launch.py  mode:=\"'as'\" namespace:=\"'$ROBOT_NAME'\"" C-m
# the line above with all the quotes is annyoing but it works...

tmux select-pane -t $SESSION:1.1
tmux send-keys "ros2 run alars alars_localize_action_server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME" C-m

tmux select-pane -t $SESSION:1.2
tmux send-keys "echo 'This will be alars-recover'" C-m

tmux select-pane -t $SESSION:1.3
tmux send-keys "echo 'This will be alars-checkload'" C-m


# bt
tmux new-window -t $SESSION:2 -n 'BT'
tmux rename-window "BT"
tmux select-window -t $SESSION:2
tmux send-keys "ros2 launch wasp_bt wasp_bt.launch \
robot_name:=$ROBOT_NAME \
agent_type:=$AGENT_TYPE \
pulse_rate:=$PULSE_RATE \
use_sim_time:=$USE_SIM_TIME \
bt_timeout:=5.0" C-m

# move-to
tmux new-window -t $SESSION:3 -n 'MoveTo'
tmux rename-window "MoveTo"
tmux select-window -t $SESSION:3
tmux send-keys "ros2 launch go_to_geopoint go_to_geopoint_server.launch robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME setpoint_topic:=move_to_setpoint" C-m


# camera and detection node
tmux new-window -t $SESSION:4 -n 'Camera'
tmux rename-window "Cam"
tmux select-window -t $SESSION:4
tmux split-window -h -t $SESSION:4.0
tmux select-pane -t $SESSION:4.0

# auv buoy detector
AUV_DETECTOR_CONFIG_FILENAME=auv_detector_field_calibration.yaml
if [[ $USE_SIM_TIME = "True" ]]; then
    AUV_DETECTOR_CONFIG_FILENAME=auv_detector_sim_calibration.yaml
fi
AUV_DETECTOR_CONFIG_FILE=$(ros2 pkg prefix auv_detector --share)/config/$AUV_DETECTOR_CONFIG_FILENAME

tmux send-keys "ros2 run auv_detector auv_buoy_detector --ros-args \
-r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME \
--params-file $AUV_DETECTOR_CONFIG_FILE" C-m

# the cam driver is needed just for the real thing
if [[ $USE_SIM_TIME = "False" ]]; then
    tmux select-pane -t $SESSION:4.1
    tmux send-keys "ros2 run usb_cam usb_cam_node_exe --ros-args -r __ns:=/$ROBOT_NAME/gimbal_camera" C-m
fi


# mqtt bridge
tmux new-window -t $SESSION:8 -n 'MQTTBridge'
tmux rename-window "MQTTBridge"
tmux select-window -t $SESSION:8
tmux send-keys "ros2 launch str_json_mqtt_bridge waraps_bridge.launch robot_name:=$ROBOT_NAME domain:=air realsim:=$REALSIM broker_addr:=$MQTT_ADDR broker_port:=$MQTT_PORT context:=alars" C-m


# only needed when running the sim
if [[ $USE_SIM_TIME = "True" ]]; then
    # ROS2Bridge
    tmux new-window -t $SESSION:9 -n 'SimConn'
    tmux select-window -t $SESSION:9
    tmux send-keys "ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p tcp_ip:=localhost -p tcp_port:=10000" C-m
    if [[ $ON_LINUX = "True" ]]; then
        # mqtt broker
        tmux split-window -h -t $SESSION:9.0
        tmux select-pane -t $SESSION:9.1
        tmux send-keys "mosquitto -p $MQTT_PORT" C-m
    fi
fi

# Set default window to either the captain 
# or the psdk node depending on real/sim
# both are on 0.0
tmux select-window -t $SESSION:0
tmux select-pane -t $SESSION:0.0
# attach to the new session
tmux -2 attach-session -t $SESSION
