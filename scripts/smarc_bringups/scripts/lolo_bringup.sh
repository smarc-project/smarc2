#! /bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/tmux_layout.sh"

# Allow custom robot name as first argument, default to 'lolo'
ROBOT_NAME=${1:-lolo}
SESSION=${ROBOT_NAME}_bringup

if [[ "$(whoami)" == *"lolo"* ]]; then
    USE_SIM_TIME=False
else
    USE_SIM_TIME=True
fi

# New variables for wasp_bt.launch and wasp_mqtt_agent.launch
AGENT_TYPE=subsurface
PULSE_RATE=0.5 # Hz
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

################## TMUX WINDOWS ##################

# create a tmux session with a name
tmux -2 new-session -d -x 220 -y 60 -s "$SESSION"

#Logging
tmux select-window -t $SESSION:0
tmux send-keys "Remember to start the logging!" 

# Controllers
CONTROLLER_CMD="sleep 2; ros2 launch lolo_controllers lolo_controllers_launch.py robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME"
DESCRIPTION_CMD="sleep 2; ros2 launch lolo_description lolo_description.launch"
tmux_make_layout "$SESSION" Controllers "
col(
    var(CONTROLLER_CMD),
    var(DESCRIPTION_CMD)
)"

# BT.
SMARC_BT_CMD="ros2 launch wasp_bt wasp_bt.launch robot_name:=$ROBOT_NAME agent_type:=$AGENT_TYPE pulse_rate:=$PULSE_RATE use_sim_time:=$USE_SIM_TIME bt_log_mode:=$BT_LOG_MODE $AGENT_UUID_ARG"
tmux_make_layout "$SESSION" wasp-bt "
col(
    var(SMARC_BT_CMD)
)"

# Lolo Action servers
AUV_DEPTH_MOVE_TO_CMD="sleep 4; ros2 run lolo_depth_move_to server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"
AUV_DEPTH_AT_HEADING="sleep 4; ros2 run lolo_cruise_depth_at_heading server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"
EMERGENCY_ACTION_CMD="sleep 4; ros2 run lolo_emergency_action server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"
LOITER_CMD="sleep 4; ros2 run lolo_loiter server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"
tmux_make_layout "$SESSION" Actions "
col(
    row(
        var(AUV_DEPTH_MOVE_TO_CMD),
        var(AUV_DEPTH_AT_HEADING)
    ),
    row(
        var(EMERGENCY_ACTION_CMD),
        var(LOITER_CMD)
    )
)"

echo "Hejsan"

# SMaRC Basic actions
GEOFENCE_CMD="ros2 run smarc_basic geofence_node --ros-args -r __ns:=/$ROBOT_NAME \
-p use_sim_time:=$USE_SIM_TIME \
-p map_frame:=$ROBOT_NAME/odom"

HUMAN_LOG_CMD="ros2 run smarc_basic log_action --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"
WAIT_CMD="ros2 run smarc_basic wait_action --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"

tmux_make_layout "$SESSION" BasicActions "
row(
    col(var(GEOFENCE_CMD), var(HUMAN_LOG_CMD)),
    col(var(WAIT_CMD))
)"

# WARA-PS bridge
WARA_PS_MQTT_CMD="sleep 7; ros2 launch str_json_mqtt_bridge waraps_bridge.launch broker_addr:=20.240.40.232 broker_port:=1884 robot_name:=$ROBOT_NAME domain:=$AGENT_TYPE realsim:=$REALSIM use_sim_time:=$USE_SIM_TIME context:=$CONTEXT"
tmux_make_layout "$SESSION" waraps-mqtt "
col(
    var(WARA_PS_MQTT_CMD)
)"


# launch hardware drivers if REALSIM is set to real
if [ "$REALSIM" = "real" ]; then
    
    hardware_1_CMD="ros2 launch lolo_drivers lolo_hardware1_launch.py robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME"
    hardware_2_CMD="sleep 1; ros2 launch lolo_drivers lolo_hardware2_launch.py robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME"
    hardware_3_CMD="ros2 launch lolo_drivers lolo_hardware3_launch.py robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME"
    hardware_4_CMD="ros2 run lolo_drivers usbl_interface --ros-args -r __ns:=/$ROBOT_NAME"
    hardware_5_CMD="ros2 launch lolo_drivers spinnaker_camera_node_launch.py camera_type:=blackfly_s serial:="'23182955'" gev_scps_packet_size:=9000"
    
    tmux_make_layout "$SESSION" Hardware "
    col(
        var(hardware_1_CMD),
        var(hardware_2_CMD),
        var(hardware_3_CMD),
        var(hardware_4_CMD),
        var(hardware_5_CMD)
    )"
    echo "Launching hardware drivers in real mode."

else
    echo "Skipping hardware drivers launch in simulation mode."
fi

if [ "$REALSIM" = "real" ]; then
    HEALTH_MONITORING_CMD="sleep 5; ros2 launch lolo_health_checker lolo_health_checker.launch robot_name:=$ROBOT_NAME"
    LOLO_MQTT_BRIDGE_CMD="ros2 run lolo_local_mqtt_translator lolo_local_translator_node"
    tmux_make_layout "$SESSION" Health-monitoring "
    col(
        var(HEALTH_MONITORING_CMD),
        var(LOLO_MQTT_BRIDGE_CMD)
    )"
    
else
    # new window just publishing int8 0 to /lolo/smarc/vehicle_health
    HEALTH_MONITORING_CMD="ros2 topic pub -r 1 /$ROBOT_NAME/smarc/vehicle_health std_msgs/msg/Int8 '{data: 0}' "
    tmux_make_layout "$SESSION" Fake-health-monitoring "
    col(
        var(HEALTH_MONITORING_CMD)
    )"
fi



#Lolo prox ops action

PROX_OPS_CMD="sleep 4; ros2 launch lolo_prox_ops lolo_prox_ops.launch robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME"
tmux_make_layout "$SESSION" prox-ops "
col(
    var(PROX_OPS_CMD)
)"

#Lolo TUPER task (action-server-as-BT). In sim, also run the estimate faker
#(tuper_test) so the mission can be dry-run without the real acoustic UKF.
tmux new-window -t $SESSION:13 -n 'tuper'
tmux select-window -t $SESSION:13
tmux send-keys "sleep 8; ros2 launch lolo_tuper lolo_tuper.launch robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME" C-m
if [ "$REALSIM" = "simulation" ]; then
    tmux split-window -h -t $SESSION:13.0
    tmux select-pane -t $SESSION:13.1
    tmux send-keys "sleep 10; ros2 run lolo_tuper tuper_test --ros-args --params-file \$(ros2 pkg prefix lolo_tuper)/share/lolo_tuper/config/tuper_test_params.yaml -p use_sim_time:=$USE_SIM_TIME -p latlon_topic:=/$ROBOT_NAME/smarc/latlon -p odom_topic:=/$ROBOT_NAME/smarc/odom" C-m
fi

#Lolo menu
if [ "$REALSIM" = "real" ]; then
    
    MENU_CMD_1="ros2 run lolo_drivers menu_output"
    MENU_CMD_2="ros2 run lolo_drivers menu_input"
    tmux_make_layout "$SESSION" Menu "
    col(
        var(MENU_CMD_1),
        var(MENU_CMD_2)
    )"
fi

ZENOH_CMD="ros2 run rmw_zenoh_cpp rmw_zenohd"

tmux_make_layout "$SESSION" zenoh "
col(
    var(ZENOH_CMD)
)"

# Set default window
tmux select-window -t $SESSION:1
tmux -2 attach-session -t $SESSION
