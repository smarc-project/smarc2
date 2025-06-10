#! /bin/bash
ROBOT_NAME=acoustic_relay
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

tmux -2 new-session -d -s $SESSION -n 'acoustic_receiver'

tmux select-window -t $SESSION:0
tmux send-keys "ros2 launch serial_ping_pkg smarc_pos_receiver_node.launch serial_port:='/dev/ttyUSB0'" C-m

# one window for sam: left:waraps_agent launch, right: sam_waraps_bridge launch
tmux new-window -t $SESSION:1 -n 'sam'
tmux select-window -t $SESSION:1
tmux split-window -h -t $SESSION:1.0
tmux select-pane -t $SESSION:1.0
# spin the waraps agent
tmux send-keys "ros2 launch wasp_bt wasp_mqtt_agent.launch robot_name:=relay_sam agent_type:=$AGENT_TYPE pulse_rate:=$PULSE_RATE use_sim_time:=$USE_SIM_TIME" C-m
# spin the waraps bridge
tmux select-pane -t $SESSION:1.1
tmux send-keys "ros2 launch str_json_mqtt_bridge waraps_bridge.launch broker_addr:=20.240.40.232 broker_port:=1884 robot_name:=relay_sam domain:=$AGENT_TYPE realsim:=$REALSIM use_sim_time:=$USE_SIM_TIME" C-m

tmux new-window -t $SESSION:2 -n 'lolo'
# one window for lolo: left:waraps_agent launch, right: lolo_waraps_bridge launch
tmux select-window -t $SESSION:2
tmux split-window -h -t $SESSION:2.0
tmux select-pane -t $SESSION:2.0
# spin the waraps agent
tmux send-keys "ros2 launch wasp_bt wasp_mqtt_agent.launch robot_name:=relay_lolo agent_type:=$AGENT_TYPE pulse_rate:=$PULSE_RATE use_sim_time:=$USE_SIM_TIME" C-m
tmux select-pane -t $SESSION:2.1
# spin the waraps bridge
tmux send-keys "ros2 launch str_json_mqtt_bridge waraps_bridge.launch broker_addr:=20.240.40.232 broker_port:=1884 robot_name:=relay_lolo domain:=$AGENT_TYPE realsim:=$REALSIM use_sim_time:=$USE_SIM_TIME" C-m

# Set default window
tmux select-window -t $SESSION:0
tmux -2 attach-session -t $SESSION