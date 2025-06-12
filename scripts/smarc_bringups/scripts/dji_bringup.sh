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
tmux new-window -t $SESSION:0 -n 'Captains'
tmux rename-window "Captains"
# split the first window into two panes
tmux split-window -h -t $SESSION:0.0      # Split window into left (0.0) and right (0.1)
tmux split-window -v -t $SESSION:0.0      # Split left pane into top-left (0.0) and bottom-left (0.2)
tmux split-window -v -t $SESSION:0.1      # Split right pane into top-right (0.1) and bottom-right (0.3)
tmux select-layout -t $SESSION:0 tiled    # Arrange as a 2x2 grid
# 0.0 | 0.1
# ----+----
# 0.2 | 0.3

# only launch if not the simulator
if [ "$USE_SIM_TIME" = "False" ]; then
    tmux select-window -t $SESSION:0
    tmux select-pane -t $SESSION:0.0
    tmux send-keys "ros2 launch psdk_wrapper wrapper.launch.py" C-m
    
    tmux select-pane -t $SESSION:0.1
    tmux send-keys "ros2 run dji_captain dji_captain --ros-args --remap __ns:=/$ROBOT_NAME" C-m

    tmux select-pane -t $SESSION:0.2
    tmux send-keys "ros2 topic echo /$ROBOT_NAME/captain_status" C-m

    # tmux select-pane -t $SESSION:0.3
fi


# action servers
tmux new-window -t $SESSION:1 -n 'action_servers'
tmux rename-window "action_servers"
tmux select-window -t $SESSION:1
tmux send-keys "ros2 launch go_to_geopoint go_to_geopoint_server.launch robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME setpoint_topic:=move_to_setpoint" C-m


# bt
tmux new-window -t $SESSION:2 -n 'bt'
tmux rename-window "bt"
tmux select-window -t $SESSION:2
tmux send-keys "ros2 launch wasp_bt wasp_bt.launch robot_name:=$ROBOT_NAME agent_type:=$AGENT_TYPE pulse_rate:=$PULSE_RATE use_sim_time:=$USE_SIM_TIME" C-m



# mqtt bridge
tmux new-window -t $SESSION:3 -n 'mqtt_bridge'
tmux rename-window "mqtt_bridge"
tmux select-window -t $SESSION:3
if [ "$USE_SIM_TIME" = "True" ]; then
    tmux send-keys "ros2 launch str_json_mqtt_bridge waraps_bridge.launch robot_name:=$ROBOT_NAME domain:=air realsim:=simulation" C-m
else
    tmux send-keys "ros2 launch str_json_mqtt_bridge waraps_bridge.launch robot_name:=$ROBOT_NAME domain:=air realsim:=real broker_addr:=20.240.40.232 broker_port:=1884 context:=alars" C-m
fi



# only launch if not the simulator
# camera node
if [ "$USE_SIM_TIME" = "False" ]; then
    tmux new-window -t $SESSION:4 -n 'cam'
    tmux rename-window "cam"
    tmux select-window -t $SESSION:4
    tmux send-keys "ros2 run usb_cam usb_cam_node_exe --ros-args --remap __ns:=/$ROBOT_NAME/gimbal_camera" C-m
fi



# Set default window
tmux select-window -t $SESSION:0
tmux select-pane -t $SESSION:0.1
# attach to the new session
tmux -2 attach-session -t $SESSION







