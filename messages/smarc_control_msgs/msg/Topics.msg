# This is a file that defines all the topics for control.
# The goal is to have one location that all cpp/py scripts
# can easily access and thus avoid having 100 parameters for topics all
# over the place, repeated for all subs/pubs...
# It is assumed that the nodes will namespace as needed.

########################
# Control topics
########################
# States
string STATES = 'core/odom_gt' # Type: Odometry

# Setpoints
string DEPTH_SETPOINT = 'ctrl/depth_setpoint' # Type: Float64
string PITCH_SETPOINT = 'ctrl/pitch_setpoint' # Type: Float64

# Convenience Topics
string STATES_CONV = 'ctrl/conv/states' # Type: ControlState
string REF_CONV = 'ctrl/conv/ref' # Type: ControlReference
string CONTROL_ERROR_CONV = 'ctrl/conv/error' # Type: ControlError
string CONTROL_INPUT_CONV = 'ctrl/conv/control_input' # Type: ControlInput
string WAYPOINT_CONV = 'ctrl/conv/waypoint' # Type: PoseWithCovarianceStamped

#Joy controllera and teleop topics
string ELEV_SP_TOP = 'ctrl/elevator_pid/setpoint'
string JOY_TOPIC = 'ctrl/joy'
string JOY_BUTTONS_TOPIC = 'ctrl/joy_buttons'
string RPM_JOYSTICK_TOPIC = 'ctrl/rpm_joystick'
string VEC_DEG_JOY_TOPIC =  'actrl/vector_deg_joystick'
string TELEOP_ENABLE = 'teleop/enable'
string ASSIST_ENABLE = 'teleop/drive_assist_enable'
string ELEVATOR_PID_CTRL = 'ctrl/elevator_pid/ctrl_effort'


