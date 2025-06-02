#! /bin/bash
ROBOT_NAME=lolo
SESSION=${ROBOT_NAME}_bringup

# New variables for wasp_bt.launch and wasp_mqtt_agent.launch
AGENT_TYPE=subsurface
LEVELS="['sensor','direct_execution']"
PULSE_RATE=1
LINK_SUFFIX=_gt
REALSIM=simulation

# create a tmux session with a name
tmux -2 new-session -d -s $SESSION


# create a bunch of windows. These are the "tabs" you'll
# see at the bottom green line.
# C-b <NUM> will change to the tab.
# default window is 0

# state estimation stuff like pressure->depth, imu->tf etc
tmux new-window -t $SESSION:0 -n 'controllers'
tmux rename-window "controllers"
# BT, action servers etc.
tmux new-window -t $SESSION:1 -n 'bt'
tmux rename-window "bt"
# controllers that are "constantly running"
tmux new-window -t $SESSION:2 -n 'auv_depth_move_to'
# connection to different GUIs
tmux new-window -t $SESSION:3 -n 'gui'
# utility stuff like dubins planning and lat/lon conversions that other stuff rely on
tmux new-window -t $SESSION:4 -n 'utils'

# for robot description launch. so we get base_link -> everything else
tmux new-window -t $SESSION:8 -n 'description'
# dummy stuff to temporarily let other stuff work
tmux new-window -t $SESSION:9 -n 'dummies'

# for the mqtt bridge.
tmux new-window -t $SESSION:10 -n 'mqtt_bridge'



# Now we launch things in each window.
tmux select-window -t $SESSION:0
tmux send-keys "ros2 launch lolo_controllers lolo_controllers_launch.py robot_name:=$ROBOT_NAME" C-m

tmux select-window -t $SESSION:1
tmux send-keys "ros2 launch wasp_bt wasp_bt.launch robot_name:=$ROBOT_NAME link_suffix:=$LINK_SUFFIX agent_type:=$AGENT_TYPE levels:=$LEVELS pulse_rate:=$PULSE_RATE" C-m

tmux select-window -t $SESSION:2
tmux send-keys "ros2 run lolo_depth_move_to server --ros-args -r __ns:=/$ROBOT_NAME" C-m

tmux select-window -t $SESSION:3
tmux send-keys "ros2 launch smarc_nodered smarc_nodered.launch robot_name:=$ROBOT_NAME" C-m

tmux select-window -t $SESSION:4
tmux send-keys "ros2 launch smarc_bringups utilities.launch robot_name:=$ROBOT_NAME" C-m

# Mostly static stuff that wont be giving much feedback
tmux select-window -t $SESSION:8
# tmux send-keys "ros2 launch sam_description sam_description.launch robot_name:=$ROBOT_NAME" C-m

tmux select-window -t $SESSION:9
# tmux send-keys "ros2 launch smarc_bringups dummies.launch robot_name:=$ROBOT_NAME" C-m

tmux select-window -t $SESSION:10
# To connect to our MQTT broker
# tmux send-keys "ros2 launch str_json_mqtt_bridge waraps_bridge.launch broker_addr:=20.240.40.232 broker_port:=1884 " C-m
# For local testing: use defaults
tmux send-keys "ros2 launch str_json_mqtt_bridge waraps_bridge.launch robot_name:=$ROBOT_NAME domain:=$AGENT_TYPE realsim:=$REALSIM" C-m 

# Conditional launches, for sim-only or real-only things
# the real sam's username is "sam" and lolo's "lolo".
# So we can switch on that.

# Set default window
tmux select-window -t $SESSION:1
# attach to the new session
tmux -2 attach-session -t $SESSION