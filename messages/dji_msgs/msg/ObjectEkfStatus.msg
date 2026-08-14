# EKF status information for a single estimated object
std_msgs/Header header

string class_name

bool initialized
float64 time_since_last_processed_measurement
float64 time_since_last_update

int32 consecutive_outliers
int32 consecutive_invalid_measurements

float64 covariance_trace
float64 innovation_norm