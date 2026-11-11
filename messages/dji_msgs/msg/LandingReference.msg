std_msgs/Header header

uint8 state
string state_name

# Desired drone height above the pad in the landing frame.
float64 height_above_pad
# Desired derivative of height_above_pad. Negative means descending toward the pad.
float64 vertical_reference_velocity

bool control_enabled
bool descent_allowed

# Safety override is already expressed in controller_frame.
bool override_active
geometry_msgs/Vector3 override_velocity
string controller_frame
