#! /bin/bash
# Set LOCAL_ROBOT_NAME in your bashrc
ROBOT_NAME=$LOCAL_ROBOT_NAME
SESSION=${ROBOT_NAME}_bringup
USE_SIM_TIME=True

AGENT_TYPE=subsurface
PULSE_RATE=0.5 # Hz

SIM=${USE_SIM_TIME}
SESSION=${ROBOT_NAME}_bringup
# create a tmux session with a name
tmux -2 new-session -d -s $SESSION

# create a bunch of windows. These are the "tabs" you'll
# see at the bottom green line.
# C-b <NUM> will change to the tab.
# default window is 0

# Conditional launches, for sim-only or real-only things
# USE_SIM_TIME will be true for anything running in the sim, false for the real vehicles
if [ $SIM = "true" ]
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

    tmux new-window -t $SESSION:7 -n payloads
    tmux select-window -t $SESSION:7
    tmux send-keys "ros2 launch sam_drivers sam_payloads.launch sss_out_file:=$SSS_SAVE_PATH/ high_freq:=true range:=40 robot_name:=$ROBOT_NAME" C-m

    tmux new-window -t $SESSION:8 -n uwcomms
    tmux select-window -t $SESSION:8
    tmux send-keys "ros2 launch sam_drivers sam_uwcomms.launch robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME" C-m

fi    

# state estimation stuff like pressure->depth, imu->tf etc
tmux new-window -t $SESSION:0 -n 'dr'
tmux rename-window "dr"
# BT, action servers etc.
tmux new-window -t $SESSION:1 -n 'bt'
tmux rename-window "bt"
# controllers that are "constantly running"
tmux new-window -t $SESSION:2 -n 'control'
# connection to different GUIs
tmux new-window -t $SESSION:3 -n 'gui'
# utility stuff like dubins planning and lat/lon conversions that other stuff rely on
tmux new-window -t $SESSION:4 -n 'utils'

# for robot description launch. so we get base_link -> everything else
tmux new-window -t $SESSION:8 -n 'description'
# dummy stuff to temporarily let other stuff work
tmux new-window -t $SESSION:9 -n 'dummies'

# for the mqtt bridge.
tmux new-window -t $SESSION:10 -n 'mqtt'



# Now we launch things in each window.
tmux select-window -t $SESSION:0
#tmux send-keys "ros2 launch sam_dead_reckoning sam_dr_launch.launch robot_name:=$ROBOT_NAME" C-m
tmux send-keys "echo 'Not launching sam_dead_reckoning sam_dr_launch.launch until someone fixes it!'" C-m

tmux select-window -t $SESSION:1
tmux send-keys "ros2 launch wasp_bt wasp_bt.launch robot_name:=$ROBOT_NAME" C-m

tmux select-window -t $SESSION:2
tmux send-keys "ros2 launch sam_diving_controller actionserver.launch robot_name:=$ROBOT_NAME" C-m

# controllers that are "constantly running"
#tmux new-window -t $SESSION:3 -n 'control'
#tmux select-window -t $SESSION:3
#tmux send-keys "ros2 launch sam_diving_controller actionserver.launch robot_name:=$ROBOT_NAME tf_suffix:=_gt" C-m
#tmux send-keys "ros2 launch sam_diving_controller actionserver.launch robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME" C-m

# connection to different GUIs
#tmux new-window -t $SESSION:4 -n 'gui'
#tmux select-window -t $SESSION:4
#tmux send-keys "ros2 launch smarc_nodered smarc_nodered.launch robot_name:=$ROBOT_NAME" C-m

# utility stuff like dubins planning and lat/lon conversions that other stuff rely on
tmux new-window -t $SESSION:5 -n 'utils'
tmux select-window -t $SESSION:5
tmux send-keys "ros2 launch smarc_bringups utilities.launch robot_name:=$ROBOT_NAME" C-m


# Mostly static stuff that wont be giving much feedback
tmux select-window -t $SESSION:8
tmux send-keys "ros2 topic pub -r 1 /$ROBOT_NAME/smarc/vehicle_health std_msgs/msg/Int8 '{data: 0}' " C-m

tmux select-window -t $SESSION:9
# tmux send-keys "ros2 launch smarc_bringups dummies.launch robot_name:=$ROBOT_NAME" C-m
tmux send-keys "ros2 launch sam_emergency_action sam_emergency_action.launch robot_name:=$ROBOT_NAME" C-m

# Set your MQTT Broker IP and Port in your bashrc
tmux select-window -t $SESSION:10
tmux send-keys "ros2 launch str_json_mqtt_bridge waraps_bridge.launch broker_addr:=$MQTT_BROKER_IP broker_port:=$MQTT_BROKER_PORT robot_name:=$ROBOT_NAME" C-m

# Launch the wasp_bt LAST, to give action servers time to start publishing heartbeats
tmux select-window -t $SESSION:1
tmux send-keys "ros2 launch wasp_bt wasp_bt.launch robot_name:=$ROBOT_NAME agent_type:=$AGENT_TYPE pulse_rate:=$PULSE_RATE use_sim_time:=$USE_SIM_TIME" C-m

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
