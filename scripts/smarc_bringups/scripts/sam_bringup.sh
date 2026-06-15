#! /bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/tmux_layout.sh"

# Set LOCAL_ROBOT_NAME, LOCAL_MQTT_BROKER_IP, and LOCAL_MQTT_BROKER_PORT in your bashrc
ROBOT_NAME=$LOCAL_ROBOT_NAME
MQTT_BROKER_IP=$LOCAL_MQTT_BROKER_IP
MQTT_BROKER_PORT=$LOCAL_MQTT_BROKER_PORT
SSS_SAVE_PATH=/home/orin/sss_auto_save

SESSION=${ROBOT_NAME}_bringup
# check if there is already a tmux session with this name
if tmux has-session -t $SESSION 2>/dev/null; then
    echo "There is already a tmux session named $SESSION."
    echo "Please close it before launching this script."
    echo "Exiting."
    exit 1
fi


if [[ "$(whoami)" == "orin" ]]; then
    USE_SIM_TIME=False
    REALSIM=real
    MQTT_BROKER_IP=20.240.40.232
    MQTT_BROKER_PORT=1884
else
    USE_SIM_TIME=True
    REALSIM=simulation
fi

# Variables for wasp_bt.launch and wasp_mqtt_agent.launch
AGENT_TYPE=subsurface
PULSE_RATE=0.5 # Hz


# create a tmux session with a name
tmux -2 new-session -d -x 220 -y 60 -s "$SESSION"


if [[ $USE_SIM_TIME == "False" ]]; then
    SAM_CORE_CMD="ros2 launch sam_drivers sam_core.launch robot_name:=$ROBOT_NAME"
    SAM_PAYLOADS_CMD="ros2 launch sam_drivers sam_payloads.launch sss_out_file:=$SSS_SAVE_PATH/ high_freq:=true robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME"
    SAM_UWCOMMS_CMD="ros2 launch sam_drivers sam_uwcomms.launch robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME"
    tmux_make_layout "$SESSION" core "
    col(
        var(SAM_CORE_CMD),
        var(SAM_PAYLOADS_CMD),
        var(SAM_UWCOMMS_CMD)
    )"
fi

DESCRIPTION_CMD="ros2 launch sam_description sam_description.launch robot_name:=$ROBOT_NAME"
DR_CMD="ros2 launch hydrobatic_localization state_estimator.launch robot_name:=$ROBOT_NAME  use_motion_model:=false inference_strategy:=FixedLagSmoothing kf_interval_hz:=10 use_sensor_covariance:=false init_from_ground_truth:=false"

tmux_make_layout "$SESSION" dr "
col(
    3:var(DR_CMD),
    1:var(DESCRIPTION_CMD)
)"

BT_CMD="ros2 launch wasp_bt wasp_bt.launch robot_name:=$ROBOT_NAME agent_type:=$AGENT_TYPE pulse_rate:=$PULSE_RATE use_sim_time:=$USE_SIM_TIME"
CONTROLLER_CMD="ros2 launch sam_diving_controller pid_wp_following.launch robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME"
# EMERGENCY_ACTION_CMD="ros2 launch sam_emergency_action sam_emergency_action.launch robot_name:=$ROBOT_NAME"
HEALTH_FAKER_CMD="ros2 topic pub /sam/smarc/vehicle_health std_msgs/msg/Int8 data:\ 0\ "
DISCOVERY_SERVER_CMD="export ZENOH_CONFIG_OVERRIDE='listen/endpoints=[\"tcp/0.0.0.0:7447\"]' && ros2 run rmw_zenoh_cpp rmw_zenohd"
tmux_make_layout "$SESSION" bt+cont "
row(
    var(BT_CMD),
    col(
        2:var(CONTROLLER_CMD),
        1:var(HEALTH_FAKER_CMD),
        1:var(DISCOVERY_SERVER_CMD)
    )
)"

SMARC_PUB_CMD="ros2 launch sam_smarc_publisher default.launch robot_name:=$ROBOT_NAME"
MQTT_BRIDGE_CMD="ros2 launch str_json_mqtt_bridge waraps_bridge.launch broker_addr:=$MQTT_BROKER_IP broker_port:=$MQTT_BROKER_PORT robot_name:=$ROBOT_NAME domain:=subsurface context:=isee realsim:=$REALSIM use_sim_time:=$USE_SIM_TIME"
# HEALTH_CHECKER_CMD="ros2 launch sam_health_checker sam_rate_health_checker.launch robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME"
# UTILS_CMD="ros2 launch smarc_bringups utilities.launch robot_name:=$ROBOT_NAME"
tmux_make_layout "$SESSION" utils "
row(
    var(MQTT_BRIDGE_CMD),
    var(SMARC_PUB_CMD)
)"





# Set default window
tmux select-window -t $SESSION:0
# attach to the new session
tmux -2 attach-session -t $SESSION
