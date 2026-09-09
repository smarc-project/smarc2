#! /bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/tmux_layout.sh"

ROBOT_NAME=ActiveHook

MODE=$1
if [[ -z "$MODE" ]]; then
    echo "You must pass the mode as the first argument! Pass one of: real or sim"
    echo "real: also launches mavros against the actual vehicle."
    echo "sim: skips mavros, you connect the ros-unity bridge yourself."
    echo "Exiting."
    exit 1
fi

if [[ "$MODE" != "real" && "$MODE" != "sim" ]]; then
    echo "Invalid mode: $MODE"
    echo "Please pass either real or sim as the first argument."
    echo "Exiting."
    exit 1
fi

if [[ "$MODE" == "sim" ]]; then
    USE_SIM_TIME=True   
else
    USE_SIM_TIME=False
fi

SESSION=${ROBOT_NAME}_bringup

# check if there is already a tmux session with this name
if tmux has-session -t $SESSION 2>/dev/null; then
    echo "There is already a tmux session named $SESSION."
    echo "Please close it before launching this script."
    echo "Exiting."
    exit 1
fi

# create a tmux session with a name
tmux -2 new-session -d -x 220 -y 60 -s "$SESSION"

############
# 1 Captain
############
CAPTAIN_CMD="ros2 launch active_hook active_hook_captain.launch.py use_sim_time:=$USE_SIM_TIME"
MANUAL_CONTROL_ECHO_CMD="ros2 topic echo /$ROBOT_NAME/mavros/manual_control/send mavros_msgs/msg/ManualControl"
STATE_ECHO_CMD="ros2 topic echo /$ROBOT_NAME/mavros/state mavros_msgs/msg/State"

if [[ "$MODE" == "real" ]]; then
    MAVROS_CMD="ros2 run mavros mavros_node --ros-args -r __ns:=/$ROBOT_NAME/mavros \
    -p fcu_url:=udp://0.0.0.0:14551@ \
    -p system_id:=255 \
    -p component_id:=191 \
    -p target_system_id:=1 \
    -p target_component_id:=1"

    tmux_make_layout "$SESSION" Captain "
    col(
        row(
            var(CAPTAIN_CMD),
            var(MAVROS_CMD)
        ),
        row(
            var(MANUAL_CONTROL_ECHO_CMD),
            var(STATE_ECHO_CMD)
        )
    )"
else
    tmux_make_layout "$SESSION" Captain "
    col(
        var(CAPTAIN_CMD),
        row(
            var(MANUAL_CONTROL_ECHO_CMD),
            var(STATE_ECHO_CMD)
        )
    )"
fi

tmux -2 attach-session -t "$SESSION"
tmux set-option -t "$SESSION" mouse on
tmux select-window -t "$SESSION:Captain"