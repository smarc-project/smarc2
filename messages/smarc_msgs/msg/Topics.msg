#string BATTERY_TOPIC = 'core/battery'
string GPS_TOPIC = 'core/gps'
#string HEADING_TOPIC = 'core/heading'
#string ABORT_TOPIC = 'core/abort'
string HEARTBEAT_TOPIC = 'core/heartbeat'
string VEHICLE_READY_TOPIC = 'core/vehicle_ready'

int8 VEHICLE_HEALTH_READY = 0
int8 VEHICLE_HEALTH_WAITING = 1
int8 VEHICLE_HEALTH_ERROR = 2


#Topics for all vehicles
string ABORT_TOPIC = 'smarc/abort' #empty
string BT_HEARTBEAT_TOPIC = 'smarc/heartbeat' #empty
string VEHICLE_HEALTH_TOPIC = 'smarc/vehicle_health' #int
string ODOM_TOPIC = 'smarc/odom'  #odom
string HEADING_TOPIC = 'smarc/heading' #float32
string COURSE_TOPIC = 'smarc/course' #float32
string SPEED_TOPIC = 'smarc/speed' #float32
string POS_LATLON_TOPIC = 'smarc/latlon' #geopoint
string BATTERY_PERCENT_TOPIC = 'smarc/battery_percent' #batterystate
string DEPTH_TOPIC = 'smarc/depth' #float32
string ALTITUDE_TOPIC = 'smarc/altitude' #float32
string ROLL_TOPIC = 'smarc/roll' #float32
string PITCH_TOPIC = 'smarc/pitch' #float32

################
# WARA-PS Topics
################
## Level 1
string WARA_PS_HEARTBEAT_TOPIC = 'waraps/heartbeat'
string WARA_PS_SENSOR_INFO_TOPIC = 'waraps/sensor_info'
string WARA_PS_SENSOR_POSITION_TOPIC = 'waraps/sensor/position'
string WARA_PS_SENSOR_HEADING_TOPIC = 'waraps/sensor/heading'
string WARA_PS_SENSOR_COURSE_TOPIC = 'waraps/sensor/course'
string WARA_PS_SENSOR_SPEED_TOPIC = 'waraps/sensor/speed'
string WARA_PS_SENSOR_DEPTH_TOPIC = 'waraps/sensor/depth'
string WARA_PS_SENSOR_ROLL_TOPIC = 'waraps/sensor/roll'
string WARA_PS_SENSOR_PITCH_TOPIC = 'waraps/sensor/pitch'

## Level 2
string WARA_PS_DIRECT_EXECUTION_INFO_TOPIC = 'waraps/direct_execution_info'
string WARA_PS_EXEC_RESPONSE_TOPIC = 'waraps/exec/response'
string WARA_PS_EXEC_FEEDBACK_TOPIC = 'waraps/exec/feedback'
string WARA_PS_EXEC_COMMAND_TOPIC = 'waraps/exec/command'

# Level 3
string WARA_PS_TST_EXEC_INFO_TOPIC = 'waraps/tst_execution_info'
string WARA_PS_TST_COMMAND_TOPIC = 'waraps/tst/command'
string WARA_PS_TST_RESPONSE_TOPIC = 'waraps/tst/response'
string WARA_PS_TST_FEEDBACK_TOPIC = 'waraps/tst/feedback'

# WARA-PS Abort Topic
string WARA_PS_ABORT_TOPIC = 'waraps/abort'

# Action Server Heartbeat
string WARA_PS_ACTION_SERVER_HB_TOPIC = 'waraps/action_server_heartbeat'
