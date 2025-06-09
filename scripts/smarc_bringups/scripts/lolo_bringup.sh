#! /bin/bash
ROBOT_NAME=lolo
SESSION=${ROBOT_NAME}_bringup
USE_SIM_TIME=True

# New variables for wasp_bt.launch and wasp_mqtt_agent.launch
AGENT_TYPE=subsurface
PULSE_RATE=0.5 # Hz

if [ "$USE_SIM_TIME" = "True" ]; then
    REALSIM=simulation
    LINK_SUFFIX="_gt"
else
    REALSIM=real
    LINK_SUFFIX=""
fi

tmux -2 new-session -d -s $SESSION -n 'controllers'
tmux select-window -t $SESSION:0
tmux send-keys "ros2 launch lolo_controllers lolo_controllers_launch.py robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME" C-m

# BT, action servers etc.
tmux new-window -t $SESSION:1 -n 'bt'
tmux select-window -t $SESSION:1
tmux send-keys "ros2 launch wasp_bt wasp_bt.launch robot_name:=$ROBOT_NAME agent_type:=$AGENT_TYPE pulse_rate:=$PULSE_RATE use_sim_time:=$USE_SIM_TIME" C-m

# controllers that are "constantly running"
tmux new-window -t $SESSION:2 -n 'servers'
tmux select-window -t $SESSION:2
tmux select-pane -t $SESSION:2.0
tmux split-window -h -t $SESSION:2.0
tmux split-window -v -t $SESSION:2.0
tmux split-window -v -t $SESSION:2.1
tmux select-layout -t $SESSION:2 tiled

tmux select-pane -t $SESSION:2.0
tmux send-keys "ros2 run lolo_depth_move_to server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME" C-m
tmux select-pane -t $SESSION:2.1
tmux send-keys "ros2 run lolo_cruise_depth_at_heading server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME" C-m
tmux select-pane -t $SESSION:2.2
tmux send-keys "ros2 run lolo_emergency_action server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME" C-m
tmux select-pane -t $SESSION:2.3
tmux send-keys "ros2 run lolo_loiter server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME" C-m

# for the mqtt bridge.
tmux new-window -t $SESSION:3 -n 'mqtt_bridge'
tmux select-window -t $SESSION:3

# To connect to our MQTT broker
tmux send-keys "ros2 launch str_json_mqtt_bridge waraps_bridge.launch broker_addr:=20.240.40.232 broker_port:=1884 robot_name:=$ROBOT_NAME domain:=$AGENT_TYPE realsim:=$REALSIM use_sim_time:=$USE_SIM_TIME" C-m

# For local testing: use defaults
# tmux send-keys "ros2 launch str_json_mqtt_bridge waraps_bridge.launch robot_name:=$ROBOT_NAME domain:=$AGENT_TYPE realsim:=$REALSIM use_sim_time:=$USE_SIM_TIME" C-m

# launch hardware drivers if REALSIM is set to real
if [ "$REALSIM" = "real" ]; then
    
    tmux new-window -t $SESSION:4 -n 'hardware1'
    tmux select-window -t $SESSION:4
    tmux send-keys "ros2 launch lolo_drivers lolo_hardware1_launch.py robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME" C-m
    tmux new-window -t $SESSION:5 -n 'hardware2'
    tmux select-window -t $SESSION:5
    tmux send-keys "ros2 launch lolo_drivers lolo_hardware2_launch.py robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME" C-m
    tmux new-window -t $SESSION:6 -n 'hardware3'
    tmux select-window -t $SESSION:6
    tmux send-keys "ros2 launch lolo_drivers lolo_hardware3_launch.py robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME" C-m
    tmux new-window -t $SESSION:7 -n 'usbl_interface'
    tmux select-window -t $SESSION:7
    tmux send-keys "ros2 run lolo_drivers usbl_interface --ros-args -r __ns:=/$ROBOT_NAME use_sim_time:=$USE_SIM_TIME" C-m
    
    echo "Launching hardware drivers in real mode."

else
    echo "Skipping hardware drivers launch in simulation mode."
fi

if [ "$USE_SIM_TIME" = "True" ]; then
    # new window just publishing int8 0 to /lolo/smarc/vehicle_health
    tmux new-window -t $SESSION:8 -n 'vehicle_health'
    tmux select-window -t $SESSION:8
    tmux send-keys "ros2 topic pub -r 1 /$ROBOT_NAME/smarc/vehicle_health std_msgs/msg/Int8 '{data: 0}' " C-m
else
    tmux new-window -t $SESSION:8 -n 'vehicle_health'
    tmux select-window -t $SESSION:8
    #tmux send-keys "ros2 launch lolo_health_checker lolo_health_checker.launch robot_name:=$ROBOT_NAME" C-m
    tmux send-keys "ros2 topic pub -r 1 /$ROBOT_NAME/smarc/vehicle_health std_msgs/msg/Int8 '{data: 0}' " C-m
fi

# Set default window
tmux select-window -t $SESSION:1
tmux -2 attach-session -t $SESSION
