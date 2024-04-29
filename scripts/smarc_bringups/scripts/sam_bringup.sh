ROBOT_NAME=sam92
SESSION=${ROBOT_NAME}_bringup

# create a tmux session with a name
tmux -2 new-session -d -s $SESSION


# create a bunch of windows. These are the "tabs" you'll
# see at the bottom green line.
# C-b <NUM> will change to the tab.
# default window is 0
tmux rename-window "dr"
tmux new-window -t $SESSION:1 -n 'bt'
tmux new-window -t $SESSION:2 -n 'control'
tmux new-window -t $SESSION:3 -n 'gui'


# Now we launch things in each window.
tmux select-window -t $SESSION:0
tmux send-keys "ros2 launch sam_dead_reckoning sam_dr_launch.launch robot_name:=$ROBOT_NAME" C-m

