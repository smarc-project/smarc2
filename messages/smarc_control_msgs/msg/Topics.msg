# This is a file that defines all the topics for control.
# The goal is to have one location that all cpp/py scripts
# can easily access and thus avoid having 100 parameters for topics all
# over the place, repeated for all subs/pubs...
# It is assumed that the nodes will namespace as needed.

########################
# Control topics
########################
# States
string STATES = 'smarc/odom' # Type: Odometry
string DEPTH = 'dr/depth' # Type: Float64
string PITCH = 'core/imu' # Type: 
string MOCAP_STATE = 'smarc/odom' # Type: Odometry

# Setpoints
string DEPTH_SETPOINT = 'ctrl/depth_setpoint' # Type: Float64
string PITCH_SETPOINT = 'ctrl/pitch_setpoint' # Type: Float64
string WAYPOINT = 'ctrl/waypoint' # Type: PoseWithCovarianceStamped
string TRAJ_MPC = 'ctrl/traj_mpc' # Type: smarc_control_msgs/TrajectoryMPC
string MOCAP_HYDROPOINT = '/mocap/hula/pose' # Type: PoseStamped

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

# Convenience topics published by the utilities/odom_splitter node.
string CONTROL_YAW_TOPIC = "ctrl/yaw"              # Float32
string CONTROL_YAW_RATE_TOPIC = "ctrl/yawrate"     # Float32
string CONTROL_PITCH_TOPIC = "ctrl/pitch"          # Float32
string CONTROL_PITCH_RATE_TOPIC = "ctrl/pitchrate" # Float32
string CONTROL_ROLL_TOPIC = "ctrl/roll"            # Float32
string CONTROL_ROLL_RATE_TOPIC = "ctrl/rollrate"   # Float32
string CONTROL_SURGE_RATE_TOPIC = "ctrl/surgerate" # Float32
