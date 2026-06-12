std_msgs/Header header

uint8 MODE_UNKNOWN=0
uint8 MODE_IDLE=1
uint8 MODE_WAITING_FOR_LONG_RANGE=2
uint8 MODE_LONG_RANGE_INTERCEPT=3
uint8 MODE_FUSED_INTERCEPT=4
uint8 MODE_TERMINAL_INTERCEPT=5
uint8 MODE_TARGET_LOST=6
uint8 MODE_INSPECT=7
uint8 mode

uint8 HEALTH_UNKNOWN=0
uint8 HEALTH_OK=1
uint8 HEALTH_DEGRADED=2
uint8 HEALTH_ERROR=3
uint8 health

bool long_range_track_live
bool long_range_track_converged
bool terminal_track_live
bool target_lost
bool plan_available
bool target_intercepted

float32 long_range_confidence
float32 terminal_confidence
float32 target_range_m

string status_text
