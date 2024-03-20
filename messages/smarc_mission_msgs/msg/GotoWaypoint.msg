# target pose in local UTM zone ENU coordinates
# UTM zone used defined by global
# /utm_zone and /utm_band ROS params
geometry_msgs/PoseStamped pose
# required proximity in meters to waypoint in
# order to consider the waypoint as reached
float64 goal_tolerance

# Defines the type of z control used going there
uint8 Z_CONTROL_NONE = 0
uint8 Z_CONTROL_DEPTH = 1
uint8 Z_CONTROL_ALTITUDE = 2

uint8 z_control_mode
float64 travel_altitude
float64 travel_depth

# Defines the type of speed control used going there
uint8 SPEED_CONTROL_NONE = 0
uint8 SPEED_CONTROL_RPM = 1
uint8 SPEED_CONTROL_SPEED = 2

uint8 speed_control_mode
float64 travel_rpm
float64 travel_speed

float64 lat
float64 lon
float64 arrival_heading
bool use_heading

string name