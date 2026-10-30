std_msgs/Header header

geometry_msgs/Point drone_position
geometry_msgs/Vector3 drone_velocity
geometry_msgs/Point pad_position
geometry_msgs/Vector3 pad_velocity

# Defined as drone minus landing-pad state, expressed in header.frame_id.
geometry_msgs/Vector3 relative_position
geometry_msgs/Vector3 relative_velocity

float64 drone_age
float64 pad_age
float64 pad_position_covariance_trace
float64 pad_velocity_covariance_trace

bool valid
string invalid_reason
