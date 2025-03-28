#! /bin/bash
ROBOT_NAME=lolo_auv_test
SESSION=${ROBOT_NAME}_bringup

# create a tmux session with a name
tmux -2 new-session -d -s $SESSION


# create a bunch of windows. These are the "tabs" you'll
# see at the bottom green line.
# C-b <NUM> will change to the tab.
# default window is 0

# launch rqt to publish messages as needed to ros2 topics
tmux new-window -t $SESSION:0 -n 'rqt'
tmux rename-window "rqt"
tmux send-keys "ros2 run rqt_gui rqt_gui" C-m

# window for publishing messages to topics that lolo_auv needs
tmux new-window -t $SESSION:1 -n 'mock_lolo_publishers'
tmux rename-window "mock_lolo_publishers"
# 

# set up local mqtt broker
tmux new-window -t $SESSION:2 -n 'mqtt'
tmux rename-window "mqtt"
tmux send-keys "moquitto -p 1889" C-m
tmux send-keys "ros2 launch str_json_mqtt_bridge waraps_bridge.launch" C-m

# 



# Conditional launches, for sim-only or real-only things
# the real sam's username is "sam" and lolo's "lolo".
# So we can switch on that.

USERNAME=$(whoami)
if [ $USERNAME != "sam" ]
then
    echo "You are not the real sam!"
    ROS_IP=127.0.0.1
    # Maybe launch ros-tcp-bridge here?
fi

# Set default window
tmux select-window -t $SESSION:1
# attach to the new session
tmux -2 attach-session -t $SESSION
