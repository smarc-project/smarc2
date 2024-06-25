# This is a file that defines all the topics of dead reckoning.
# The goal is to have one location that all cpp/py scripts
# can easily access and thus avoid having 100 parameters for topics all
# over the place, repeated for all subs/pubs...
# It is assumed that the nodes will namespace as needed.

########################
# Dead reckoning topics
########################
# DR node
string DR_ODOM_TOPIC = 'dr/odom'  # Type: Odometry
string DR_DEPTH_POSE_TOPIC = 'dr/depth_pose'  # Type: PoseWithCovarianceStamped
string DR_GPS_ODOM_TOPIC = 'dr/gps_odom'  # Type: Odometry

# IMU
string DR_ROLL_TOPIC = 'dr/roll'  # Type: Float64
string DR_PITCH_TOPIC = 'dr/pitch'  # Type: Float64
string DR_YAW_TOPIC = 'dr/yaw'  # Type: Float64

# DEPTH
string DR_DEPTH_TOPIC = 'dr/depth'  # Type: Float64

# Other
string DR_COMPASS_HEADING_TOPIC = 'dr/compass_heading'  # Type: Float64
string DR_LAT_LON_TOPIC = 'dr/lat_lon'  # Type: GeoPoint

string DR_ODOM_X_TOPIC = 'dr/x'  # Type: Float64
string DR_ODOM_Y_TOPIC = 'dr/y'  # Type: Float64
string DR_ODOM_Z_TOPIC = 'dr/z'  # Type: Float64
string DR_ODOM_U_TOPIC = 'dr/u'  # Type: Float64
string DR_ODOM_V_TOPIC = 'dr/v'  # Type: Float64
string DR_ODOM_W_TOPIC = 'dr/w'  # Type: Float64
string DR_ODOM_P_TOPIC = 'dr/p'  # Type: Float64
string DR_ODOM_Q_TOPIC = 'dr/q'  # Type: Float64
string DR_ODOM_R_TOPIC = 'dr/r'  # Type: Float64
string DR_ODOM_ALT_TOPIC = 'dr/alt'  # Type: Float64