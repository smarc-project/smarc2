# name of the plan
string name
# a hash derived frm this entire message. optional.
string hash
# a timeout in seconds, in which the vehicle should stop
# doing what this mission control message wants it to do
# after trying for this many seconds
uint64 timeout

# start or stop the current plan
# stop will stop and delete the plan
# pause will stop the execution, but not delete it
# start either starts a new plan or continues a paused one
uint8 CMD_START = 0
uint8 CMD_STOP = 1
uint8 CMD_PAUSE = 2
# one-way stop button. no plan should be started
# after this is received
uint8 CMD_EMERGENCY = 3
# re-set the plan with the given waypoints
uint8 CMD_SET_PLAN = 4
# to indicate that this is just feedback
uint8 CMD_IS_FEEDBACK = 5
# to specifically request a feedback message
uint8 CMD_REQUEST_FEEDBACK = 6
uint8 command


# corresponding to each command
uint8 FB_RUNNING = 0
uint8 FB_STOPPED = 1
uint8 FB_PAUSED = 2
uint8 FB_EMERGENCY = 3
uint8 FB_RECEIVED = 4
uint8 FB_COMPLETED = 5
uint8 plan_state
# and some extra string, because why not
string feedback_str


# if the cmd is set plan, then this should contain the waypoints
# to follow, otherwise ignored
smarc_mission_msgs/GotoWaypoint[] waypoints