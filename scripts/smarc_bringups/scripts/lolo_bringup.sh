#! /bin/bash

# Allow custom robot name as first argument, default to 'lolo'
ROBOT_NAME=${1:-lolo}
SESSION=${ROBOT_NAME}_bringup
USE_SIM_TIME=True

# New variables for wasp_bt.launch and wasp_mqtt_agent.launch
AGENT_TYPE=subsurface
PULSE_RATE=0.5 # Hz
AGENT_UUID="lolo-is-great" # set to a fixed UUID string to keep it stable across launches, leave empty for random
# Only pass agent_uuid to launch when set; ros2 launch rejects an empty 'agent_uuid:=' value
if [ -n "$AGENT_UUID" ]; then
    AGENT_UUID_ARG="agent_uuid:=$AGENT_UUID"
else
    AGENT_UUID_ARG=""
fi
CONTEXT=tuper # change this to 'smarc' or something else, then connect to the same context using sim to avoid clutter

BT_LOG_MODE=compact # can be 'compact' or 'verbose'

if [ "$USE_SIM_TIME" = "True" ]; then
    REALSIM=simulation
    LINK_SUFFIX="_gt"
    # Optionally override robot name for simulation, but only if not set by user
    if [ -z "$1" ]; then
        ROBOT_NAME=lolo_auv_v1
    fi
else
    REALSIM=real
    LINK_SUFFIX=""
fi

tmux -2 new-session -d -s $SESSION -n 'controllers'
tmux select-window -t $SESSION:0
tmux select-pane -t $SESSION:0.0
tmux split-window -v -t $SESSION:0.0
tmux select-layout -t $SESSION:0 tiled
tmux select-pane -t $SESSION:0.0
tmux send-keys "sleep 2; ros2 launch lolo_controllers lolo_controllers_launch.py robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME" C-m
tmux select-pane -t $SESSION:0.1
tmux send-keys "sleep 2; ros2 launch lolo_description lolo_description.launch" C-m

# BT, action servers etc.
tmux new-window -t $SESSION:1 -n 'bt'
tmux select-window -t $SESSION:1
tmux send-keys "ros2 launch wasp_bt wasp_bt.launch robot_name:=$ROBOT_NAME agent_type:=$AGENT_TYPE pulse_rate:=$PULSE_RATE use_sim_time:=$USE_SIM_TIME bt_log_mode:=$BT_LOG_MODE $AGENT_UUID_ARG" C-m

# controllers that are "constantly running"
tmux new-window -t $SESSION:2 -n 'servers'
tmux select-window -t $SESSION:2
tmux select-pane -t $SESSION:2.0
tmux split-window -h -t $SESSION:2.0
tmux split-window -v -t $SESSION:2.0
tmux split-window -v -t $SESSION:2.1
tmux select-layout -t $SESSION:2 tiled

tmux select-pane -t $SESSION:2.0
tmux send-keys "sleep 4; ros2 run lolo_depth_move_to server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME" C-m
tmux select-pane -t $SESSION:2.1
tmux send-keys "sleep 4; ros2 run lolo_cruise_depth_at_heading server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME" C-m
tmux select-pane -t $SESSION:2.2
tmux send-keys "sleep 4; ros2 run lolo_emergency_action server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME" C-m
tmux select-pane -t $SESSION:2.3
tmux send-keys "sleep 4; ros2 run lolo_loiter server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME" C-m

# for the mqtt bridge.
tmux new-window -t $SESSION:3 -n 'mqtt_bridge'
tmux select-window -t $SESSION:3

# To connect to our MQTT broker
if [ "$REALSIM" = "real" ]; then
    tmux send-keys "sleep 7; ros2 launch str_json_mqtt_bridge waraps_bridge.launch broker_addr:=20.240.40.232 broker_port:=1884 robot_name:=$ROBOT_NAME domain:=$AGENT_TYPE realsim:=$REALSIM use_sim_time:=$USE_SIM_TIME context:=$CONTEXT" C-m
else
    tmux send-keys "sleep 7; ros2 launch str_json_mqtt_bridge waraps_bridge.launch broker_addr:=20.240.40.232 broker_port:=1884 robot_name:=$ROBOT_NAME domain:=$AGENT_TYPE realsim:=$REALSIM use_sim_time:=$USE_SIM_TIME context:=$CONTEXT" C-m
    tmux new-window -t $SESSION:4 -n 'tcp-endpoint'
    tmux select-window -t $SESSION:4
    tmux send-keys "ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=127.0.0.1" C-m
fi


# For local testing: use defaults
# tmux send-keys "ros2 launch str_json_mqtt_bridge waraps_bridge.launch robot_name:=$ROBOT_NAME domain:=$AGENT_TYPE realsim:=$REALSIM use_sim_time:=$USE_SIM_TIME" C-m

# launch hardware drivers if REALSIM is set to real
if [ "$REALSIM" = "real" ]; then
    
    tmux new-window -t $SESSION:4 -n 'hardware1'
    tmux select-window -t $SESSION:4
    tmux send-keys "ros2 launch lolo_drivers lolo_hardware1_launch.py robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME" C-m
    tmux new-window -t $SESSION:5 -n 'hardware2'
    tmux select-window -t $SESSION:5
    tmux send-keys "sleep 1; ros2 launch lolo_drivers lolo_hardware2_launch.py robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME" C-m
    tmux new-window -t $SESSION:6 -n 'hardware3'
    tmux select-window -t $SESSION:6
    tmux send-keys "ros2 launch lolo_drivers lolo_hardware3_launch.py robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME"
    tmux new-window -t $SESSION:7 -n 'usbl_interface'
    tmux select-window -t $SESSION:7
    tmux send-keys "ros2 run lolo_drivers usbl_interface --ros-args -r __ns:=/$ROBOT_NAME" C-m
    tmux new-window -t $SESSION:8 -n 'flir_camera'
    tmux select-window -t $SESSION:8
    tmux send-keys "ros2 launch lolo_drivers spinnaker_camera_node_launch.py camera_type:=blackfly_s serial:="'23182955'" gev_scps_packet_size:=9000"
    
    echo "Launching hardware drivers in real mode."

else
    echo "Skipping hardware drivers launch in simulation mode."
fi

if [ "$REALSIM" = "real" ]; then
    tmux new-window -t $SESSION:9 -n 'vehicle_health'
    # one window for lolo: left:waraps_agent launch, right: lolo_waraps_bridge launch
    tmux select-window -t $SESSION:9
    tmux split-window -h -t $SESSION:9.0
    #Health checker
    tmux select-pane -t $SESSION:9.0
    tmux send-keys "sleep 5; ros2 launch lolo_health_checker lolo_health_checker.launch robot_name:=$ROBOT_NAME" C-m
    #Geofence checker
    tmux select-pane -t $SESSION:9.1
    tmux send-keys "sleep 5; ros2 launch lolo_drivers lolo_geofence_check.launch robot_name:=$ROBOT_NAME"
    
else
    # new window just publishing int8 0 to /lolo/smarc/vehicle_health
    tmux new-window -t $SESSION:9 -n 'vehicle_health'
    tmux select-window -t $SESSION:9
    tmux send-keys "ros2 topic pub -r 1 /$ROBOT_NAME/smarc/vehicle_health std_msgs/msg/Int8 '{data: 0}' " C-m
fi

# Logging window.
tmux new-window -t $SESSION:10 -n 'logging'
tmux select-window -t $SESSION:10


#Lolo prox ops action
tmux new-window -t $SESSION:11 -n 'proxops'
tmux select-window -t $SESSION:11
tmux send-keys "sleep 4; ros2 launch lolo_prox_ops lolo_prox_ops.launch robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME" C-m

#Lolo menu
if [ "$REALSIM" = "real" ]; then
    tmux new-window -t $SESSION:12 -n 'lolo_menu'
    tmux select-window -t $SESSION:12
    tmux split-window -h -t $SESSION:12.0
    #Menu output
    tmux select-pane -t $SESSION:12.0
    tmux send-keys "ros2 run lolo_drivers menu_output" C-m
    menu input
    tmux select-pane -t $SESSION:12.1
    tmux send-keys "ros2 run lolo_drivers menu_input" C-m
fi

# Set default window
tmux select-window -t $SESSION:1
tmux -2 attach-session -t $SESSION
