#! /bin/bash
# $1 is the number you type (0, 1, etc.)
# If you don't type a number, it keeps asking until you do
IDX=$1
while [[ -z "$IDX" ]]; do
    read -rp "Enter floatsam index (e.g. 0, 1, 2): " IDX
done

# Now the name includes the index
ROBOT_NAME=floatsam_usv_$IDX
SESSION=${ROBOT_NAME}_bringup
SIM_TRUE=true
USE_SIM_TIME=$SIM_TRUE

# WASP / MQTT settings
AGENT_TYPE=subsurface
PULSE_RATE=20.0
CONTEXT=tuper
BT_LOG_MODE=compact
DOMAIN=surface

if [ "$SIM_TRUE" = "true" ]; then
    REALSIM=simulation
    LINK_SUFFIX="_gt"
else
    REALSIM=real
    LINK_SUFFIX=""
fi

# --- Vehicle health publisher (simulation uses publisher) ---
tmux -2 new-session -d -s $SESSION -n 'vehicle_health'
tmux select-window -t $SESSION:0

# if [ "$REALSIM" = "real" ]; then
#     tmux send-keys "sleep 5; ros2 launch floatsam_topic_bridge floatsam_health_checker.launch.py robot_name:=$ROBOT_NAME" C-m
# else
#     tmux send-keys "ros2 topic pub -r 1 /$ROBOT_NAME/smarc/vehicle_health std_msgs/msg/Int8 '{data: 0}'" C-m
# fi

# Momentarily always publish 0 for health, since all sensors are not attached yet
tmux send-keys "ros2 topic pub -r 1 /$ROBOT_NAME/smarc/vehicle_health std_msgs/msg/Int8 '{data: 0}'" C-m


# --- MQTT bridge ---
tmux new-window -t $SESSION:1 -n 'mqtt_bridge'
tmux select-window -t $SESSION:1
tmux send-keys "sleep 3; ros2 launch str_json_mqtt_bridge waraps_bridge.launch broker_addr:=20.240.40.232 broker_port:=1884 robot_name:=$ROBOT_NAME domain:=$DOMAIN realsim:=$REALSIM use_sim_time:=$USE_SIM_TIME context:=$CONTEXT" C-m

# --- Topic bridge for floatsam ---
tmux new-window -t $SESSION:2 -n 'topic_bridge'
tmux select-window -t $SESSION:2
tmux send-keys "sleep 3; ros2 launch floatsam_topic_bridge floatsam_bridge.launch.py robot_name:=$ROBOT_NAME use_sim:=$SIM_TRUE" C-m

# --- Controllers window (main controllers + description if any) ---
tmux new-window -t $SESSION:3 -n 'controllers'
tmux select-window -t $SESSION:3
tmux select-pane -t $SESSION:3.0
tmux split-window -v -t $SESSION:3.0
tmux select-layout -t $SESSION:3 tiled
tmux select-pane -t $SESSION:3.0
tmux send-keys "sleep 2; ros2 launch floatsam_controllers floatsam_controllers_launch.py robot_name:=$ROBOT_NAME" C-m
tmux select-pane -t $SESSION:3.1
tmux send-keys "sleep 3; ros2 launch floatsam_controllers rvo_launch.py robot_name:=$ROBOT_NAME use_sim:=$SIM_TRUE" C-m

# --- Servers / action servers ---
tmux new-window -t $SESSION:4 -n 'servers'
tmux select-window -t $SESSION:4
tmux select-pane -t $SESSION:4.0
tmux split-window -h -t $SESSION:4.0
tmux select-pane -t $SESSION:4.1
tmux split-window -v -t $SESSION:4.1
tmux select-pane -t $SESSION:4.0
tmux split-window -v -t $SESSION:4.0

tmux select-pane -t $SESSION:4.0
tmux send-keys "sleep 4; ros2 launch floatsam_move_to floatsam_move_to.launch.py robot_name:=$ROBOT_NAME use_sim:=$SIM_TRUE" C-m
tmux select-pane -t $SESSION:4.1
tmux send-keys "sleep 5; ros2 run floatsam_move_to floatsam_loiter_action_server --ros-args -r __ns:=/$ROBOT_NAME -p robot_name:=$ROBOT_NAME -p loiter_move_to_speed:=fast -p use_sim:=$SIM_TRUE" C-m
tmux select-pane -t $SESSION:4.2
tmux send-keys "sleep 4; ros2 launch floatsam_move_to_path floatsam_move_to_path.launch.py robot_name:=$ROBOT_NAME use_sim:=$SIM_TRUE" C-m
tmux select-pane -t $SESSION:4.3
tmux send-keys "sleep 5; ros2 launch floatsam_loiter_heading floatsam_loiter_heading.launch.py robot_name:=$ROBOT_NAME use_sim:=$SIM_TRUE" C-m

# --- Go_to_formation ---
tmux new-window -t $SESSION:5 -n 'go_to_formation'
tmux select-window -t $SESSION:5
tmux select-pane -t $SESSION:5.0
tmux send-keys "sleep 4; ros2 launch floatsam_go_to_formation floatsam_go_to_formation.launch.py robot_name:=$ROBOT_NAME use_sim:=$SIM_TRUE" C-m


# --- Go_to_formation ---
tmux new-window -t $SESSION:6 -n 'go_to_formation_rvo'
tmux select-window -t $SESSION:6
tmux select-pane -t $SESSION:6.0
tmux send-keys "sleep 4; ros2 launch floatsam_go_to_formation_rvo floatsam_go_to_formation_rvo.launch.py robot_name:=$ROBOT_NAME use_sim:=$SIM_TRUE" C-m


# --- Behavior tree (WASP BT) ---
tmux new-window -t $SESSION:7 -n 'bt'
tmux select-window -t $SESSION:7
tmux send-keys "sleep 2; ros2 launch wasp_bt wasp_bt.launch robot_name:=$ROBOT_NAME agent_type:=$AGENT_TYPE pulse_rate:=$PULSE_RATE use_sim_time:=$USE_SIM_TIME bt_log_mode:=$BT_LOG_MODE" C-m


# Logging window.
tmux new-window -t $SESSION:8 -n 'logging'
tmux select-window -t $SESSION:8

# Set default window and attach
tmux select-window -t $SESSION:6
tmux -2 attach-session -t $SESSION



