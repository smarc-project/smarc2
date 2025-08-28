#! /bin/bash
# Set LOCAL_ROBOT_NAME, LOCAL_MQTT_BROKER_IP, and LOCAL_MQTT_BROKER_PORT in your bashrc
ROBOT_NAME=$LOCAL_ROBOT_NAME
# ROBOT_NAME=sam
# MQTT_BROKER_IP=$LOCAL_MQTT_BROKER_IP
MQTT_BROKER_IP=20.240.40.232
# MQTT_BROKER_PORT=$LOCAL_MQTT_BROKER_PORT
MQTT_BROKER_PORT=1884
SSS_SAVE_PATH=/home/orin/sss_auto_save

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

    # TODO: this can be used in both, remove from here
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
    
    tmux new-window -t $SESSION:8 -n payloads
    tmux select-window -t $SESSION:8
    tmux send-keys "ros2 launch sam_drivers sam_payloads.launch sss_out_file:=$SSS_SAVE_PATH/ high_freq:=true robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME" C-m

    tmux new-window -t $SESSION:9 -n uwcomms
    tmux select-window -t $SESSION:9
    tmux send-keys "ros2 launch sam_drivers sam_uwcomms.launch robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME" C-m

    # Mostly static stuff that wont be giving much feedback
    # for robot description launch. so we get base_link -> everything else
    tmux new-window -t $SESSION:10 -n 'description'
    tmux select-window -t $SESSION:10
    tmux send-keys "ros2 launch sam_description sam_description.launch robot_name:=$ROBOT_NAME" C-m

fi    

# state estimation stuff like pressure->depth, imu->tf etc
tmux new-window -t $SESSION:1 -n 'dr'
tmux rename-window "dr"
tmux select-window -t $SESSION:1
tmux send-keys "ros2 launch hydrobatic_localization state_estimator.launch robot_name:=$ROBOT_NAME" C-m
# tmux send-keys "echo 'Not launching sam_dead_reckoning sam_dr_launch.launch until someone fixes it!'" C-m

# BT, action servers etc.
tmux new-window -t $SESSION:2 -n 'bt'
tmux rename-window "bt"
# FIXME: Ideally we want to launch the bt here already instead of last to avoid any other confusion.
#tmux select-window -t $SESSION:2
#tmux send-keys "ros2 launch wasp_bt wasp_bt.launch robot_name:=$ROBOT_NAME" C-m

# controllers that are "constantly running"
tmux new-window -t $SESSION:3 -n 'control'
tmux select-window -t $SESSION:3
tmux send-keys "ros2 launch sam_diving_controller actionserver.launch robot_name:=$ROBOT_NAME" C-m

# SMaRC Publisher
tmux new-window -t $SESSION:4 -n 'smcp'
tmux select-window -t $SESSION:4
tmux send-keys "ros2 launch sam_smarc_publisher default.launch robot_name:=$ROBOT_NAME" C-m

# for the mqtt bridge.
tmux new-window -t $SESSION:5 -n 'mqtt'
# Set your MQTT Broker IP and Port in your bashrc
tmux select-window -t $SESSION:5
tmux send-keys "ros2 launch str_json_mqtt_bridge waraps_bridge.launch broker_addr:=$MQTT_BROKER_IP broker_port:=$MQTT_BROKER_PORT robot_name:=$ROBOT_NAME" C-m

tmux new-window -t $SESSION:6 -n 'emergency'
tmux select-window -t $SESSION:6
# tmux send-keys "ros2 launch smarc_bringups dummies.launch robot_name:=$ROBOT_NAME" C-m
tmux send-keys "ros2 launch sam_emergency_action sam_emergency_action.launch robot_name:=$ROBOT_NAME" C-m

# utility stuff like dubins planning and lat/lon conversions that other stuff rely on
# tmux new-window -t $SESSION:5 -n 'utils'
# tmux select-window -t $SESSION:5
# tmux send-keys "ros2 launch smarc_bringups utilities.launch robot_name:=$ROBOT_NAME" C-m

# for robot description launch. so we get base_link -> everything else
tmux new-window -t $SESSION:7 -n 'health'
tmux select-window -t $SESSION:7
# tmux send-keys "ros2 topic pub -r 1 /$ROBOT_NAME/smarc/vehicle_health std_msgs/msg/Int8 '{data: 0}' " # don't use C-m here, we want to keep the command in the window
tmux send-keys "ros2 launch sam_health_checker sam_rate_health_checker.launch robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME" C-m

# Launch the wasp_bt LAST, to give action servers time to start publishing heartbeats
tmux select-window -t $SESSION:2
tmux send-keys "ros2 launch wasp_bt wasp_bt.launch robot_name:=$ROBOT_NAME agent_type:=$AGENT_TYPE pulse_rate:=$PULSE_RATE use_sim_time:=$USE_SIM_TIME" C-m

#USERNAME=$(whoami)
#if [ $USERNAME != "sam" ]
#then
#    echo "You are not the real sam!"
#    ROS_IP=127.0.0.1
#    # Maybe launch ros-tcp-bridge here?
#fi

# Set default window
tmux select-window -t $SESSION:0
# attach to the new session
tmux -2 attach-session -t $SESSION
