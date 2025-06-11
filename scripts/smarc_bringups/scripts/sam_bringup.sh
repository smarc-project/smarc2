#! /bin/bash
ROBOT_NAME=sam
SESSION=${ROBOT_NAME}_bringup
USE_SIM_TIME=False
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
# create a tmux session with a name
tmux -2 new-session -d -s $SESSION
if [ $REALSIM = "simulation" ]
then
    # Mostly static stuff that wont be giving much feedback
    # for robot description launch. so we get base_link -> everything else
    tmux new-window -t $SESSION:6 -n 'description'
    tmux select-window -t $SESSION:6
    tmux send-keys "ros2 launch sam_description sam_description.launch robot_name:=$ROBOT_NAME" C-m
    # dummy stuff to temporarily let other stuff work
    # tmux new-window -t $SESSION:9 -n 'dummies'
    # tmux select-window -t $SESSION:9
    # tmux send-keys "ros2 launch smarc_bringups dummies.launch robot_name:=$ROBOT_NAME" C-m
else
    # SAM's drivers and internal comms
    tmux new-window -t $SESSION:0 -n 'core'
    tmux select-window -t $SESSION:0
    tmux send-keys "ros2 launch sam_drivers sam_core.launch robot_name:=$ROBOT_NAME" C-m
    # tmux new-window -t $SESSION:7 -n payloads
    # tmux select-window -t $SESSION:7
    # tmux send-keys "ros2 launch sam_drivers sam_payloads.launch sss_out_file:=$SSS_SAVE_PATH/ high_freq:=true range:=40 robot_name:=$ROBOT_NAME" C-m
    # tmux new-window -t $SESSION:8 -n uwcomms
    # tmux select-window -t $SESSION:8
    # tmux send-keys "ros2 launch sam_drivers sam_uwcomms.launch robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME" C-m
fi
# sam diving controller (action server)
tmux new-window -t $SESSION:1 -n 'servers'
tmux select-window -t $SESSION:1
tmux select-pane -t $SESSION:1.0
tmux split-window -h -t $SESSION:1.0
tmux split-window -v -t $SESSION:1.0
tmux split-window -v -t $SESSION:1.1
tmux select-layout -t $SESSION:1 tiled
tmux select-pane -t $SESSION:1.0
tmux send-keys "ros2 launch sam_diving_controller actionserver.launch robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME" C-m
# fake health node
tmux new-window -t $SESSION:8 -n 'vehicle_health'
tmux select-window -t $SESSION:8
tmux send-keys "ros2 topic pub -r 1 /$ROBOT_NAME/smarc/vehicle_health std_msgs/msg/Int8 '{data: 0}' " # don't use C-m here, we want to keep the command in the window
tmux new-window -t $SESSION:9 -n 'emergency_action'
tmux select-window -t $SESSION:9
# tmux send-keys "ros2 launch smarc_bringups dummies.launch robot_name:=$ROBOT_NAME" C-m
tmux send-keys "ros2 launch sam_emergency_action sam_emergency_action.launch robot_name:=$ROBOT_NAME" C-m
tmux new-window -t $SESSION:10 -n 'mqtt'
tmux select-window -t $SESSION:10
# To connect to our MQTT broker
tmux send-keys "ros2 launch str_json_mqtt_bridge waraps_bridge.launch robot_name:=$ROBOT_NAME realsim:=$REALSIM agent_type:=$AGENT_TYPE broker_addr:=20.240.40.232 broker_port:=1884 " C-m
tmux new-window -t $SESSION:2 -n 'bt'
tmux select-window -t $SESSION:2
tmux send-keys "sleep 5; ros2 launch wasp_bt wasp_bt.launch robot_name:=$ROBOT_NAME agent_type:=$AGENT_TYPE pulse_rate:=$PULSE_RATE use_sim_time:=$USE_SIM_TIME" C-m
tmux new-window -t $SESSION:3 -n 'sam_smarc_publisher'
tmux select-window -t $SESSION:3
tmux send-keys "ros2 launch sam_smarc_publisher default.launch robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME" C-m
USERNAME=$(whoami)
if [ $USERNAME != "sam" ]
then
    echo "You are not the real sam!"
    ROS_IP=127.0.0.1
    # Maybe launch ros-tcp-bridge here?
fi
# Set default window
tmux select-window -t $SESSION:2
# attach to the new session
tmux -2 attach-session -t $SESSION