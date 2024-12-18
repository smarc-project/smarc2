#! /bin/bash
ROBOT_NAME=sam_auv_v1
SESSION=${ROBOT_NAME}_bringup

# create a tmux session with a name
tmux -2 new-session -d -s $SESSION


# create a bunch of windows. These are the "tabs" you'll
# see at the bottom green line.
# C-b <NUM> will change to the tab.
# default window is 0

# state estimation stuff like pressure->depth, imu->tf etc
tmux new-window -t $SESSION:0 -n 'dr'
tmux rename-window "dr"
# BT, action servers etc.
tmux new-window -t $SESSION:1 -n 'bt'
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


# Now we launch things in each window.
tmux select-window -t $SESSION:0
#tmux send-keys "ros2 launch sam_dead_reckoning sam_dr_launch.launch robot_name:=$ROBOT_NAME" C-m
tmux send-keys "echo 'Not launching sam_dead_reckoning sam_dr_launch.launch until someone fixes it!'" C-m

tmux select-window -t $SESSION:1
#tmux send-keys "ros2 launch smarc_bt smarc_bt.launch robot_name:=$ROBOT_NAME link_suffix:=_gt" C-m

tmux select-window -t $SESSION:2
# tmux send-keys "ros2 launch dive_control actionserver.launch robot_name:=$ROBOT_NAME" C-m
tmux send-keys "ros2 launch rl_control actionserver.launch robot_name:=$ROBOT_NAME" C-m

tmux select-window -t $SESSION:3
tmux send-keys "ros2 launch smarc_nodered smarc_nodered.launch robot_name:=$ROBOT_NAME" C-m

tmux select-window -t $SESSION:4
tmux send-keys "ros2 launch smarc_bringups utilities.launch robot_name:=$ROBOT_NAME" C-m


# Mostly static stuff that wont be giving much feedback
tmux select-window -t $SESSION:8
tmux send-keys "ros2 launch sam_description sam_description.launch robot_name:=$ROBOT_NAME" C-m

tmux select-window -t $SESSION:9
tmux send-keys "ros2 launch smarc_bringups dummies.launch robot_name:=$ROBOT_NAME" C-m


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
