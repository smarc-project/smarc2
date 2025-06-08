#! /bin/bash
ROBOT_NAME=Quadrotor
SESSION=${ROBOT_NAME}_bringup

USE_SIM_TIME=False

# New variables for wasp_bt.launch and wasp_mqtt_agent.launch
AGENT_TYPE=air
PULSE_RATE=10.0

# create a tmux session with a name
tmux -2 new-session -d -s $SESSION


# create a bunch of windows. These are the "tabs" you'll
# see at the bottom green line.
# C-b <NUM> will change to the tab.
# default window is 0

# PSDK_ROS2_BRIDGE
tmux new-window -t $SESSION:0 -n 'psdk_bridge'
tmux rename-window "psdk_bridge"

# the dji_captain
tmux new-window -t $SESSION:1 -n 'dji_captain'
tmux rename-window "dji_captain"

# action servers
# split this into panes for more servers
# example: 
# tmux select-pane -t $SESSION:2.0
# tmux split-window -h -t $SESSION:2.0      # Split window into left (2.0) and right (2.1)
# tmux split-window -v -t $SESSION:2.0      # Split left pane into top-left (2.0) and bottom-left (2.2)
# tmux split-window -v -t $SESSION:2.1      # Split right pane into top-right (2.1) and bottom-right (2.3)
# tmux select-layout -t $SESSION:2 tiled    # Arrange as a 2x2 grid
tmux new-window -t $SESSION:2 -n 'action_servers'
tmux rename-window "action_servers"

# bt
tmux new-window -t $SESSION:3 -n 'bt'
tmux rename-window "bt"

# mqtt bridge
tmux new-window -t $SESSION:4 -n 'mqtt_bridge'
tmux rename-window "mqtt_bridge"

# camera node
tmux new-window -t $SESSION:5 -n 'cam'
tmux rename-window "cam"


# only launch if not the simulator
if [ "$USE_SIM_TIME" = "False" ]; then
    tmux select-window -t $SESSION:0
    tmux send-keys "ros2 launch psdk_ros2_bridge psdk_ros2_bridge.launch" C-m
    
    tmux select-window -t $SESSION:1
    tmux send-keys "ros2 run dji_captain dji_captain --ros-args --remap __ns:=/$ROBOT_NAME" C-m
fi


tmux select-window -t $SESSION:2
tmux send-keys "ros2 launch go_to_geopoint go_to_geopoint_server.launch robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME setpoint_topic:=geopoint_setpoint" C-m

tmux select-window -t $SESSION:3
tmux send-keys "ros2 launch wasp_bt wasp_bt.launch robot_name:=$ROBOT_NAME agent_type:=$AGENT_TYPE pulse_rate:=$PULSE_RATE use_sim_time:=$USE_SIM_TIME" C-m

tmux select-window -t $SESSION:4
if [ "$USE_SIM_TIME" = "True" ]; then
    tmux send-keys "ros2 launch str_json_mqtt_bridge waraps_bridge.launch robot_name:=$ROBOT_NAME domain:=air realsim:=simulation" C-m
else
    tmux send-keys "ros2 launch str_json_mqtt_bridge waraps_bridge.launch robot_name:=$ROBOT_NAME domain:=air realsim:=real" C-m
fi

# only launch if not the simulator
if [ "$USE_SIM_TIME" = "False" ]; then
    tmux select-window -t $SESSION:5
    tmux send-keys "echo 'Webcam->ROS node goes here when it exists'" C-m
fi




# Set default window
tmux select-window -t $SESSION:1
# attach to the new session
tmux -2 attach-session -t $SESSION