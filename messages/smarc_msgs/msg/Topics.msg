string ABORT_TOPIC = 'smarc/abort' #empty
string BT_HEARTBEAT_TOPIC = 'smarc/heartbeat' #empty

int8 VEHICLE_HEALTH_READY = 0
int8 VEHICLE_HEALTH_WAITING = 1
int8 VEHICLE_HEALTH_ERROR = 2
string VEHICLE_HEALTH_TOPIC = 'smarc/vehicle_health' #int

string ODOM_TOPIC = 'smarc/odom'  #odom
string HEADING_TOPIC = 'smarc/heading' #float32
string COURSE_TOPIC = 'smarc/course' #float32
string SPEED_TOPIC = 'smarc/speed' #float32
string POS_LATLON_TOPIC = 'smarc/latlon' #geopoint
string BATTERY_PERCENT_TOPIC = 'smarc/battery_percent' #float32
string DEPTH_TOPIC = 'smarc/depth' #float32
string ALTITUDE_TOPIC = 'smarc/altitude' #float32
string BT_STATUS_TOPIC = 'smarc/bt_status' #string

string HUMAN_LOG_TOPIC = 'smarc/human_log' #string
string HUMAN_LOG_SIGNAL_TOPIC = 'smarc/human_log/signal' #bool


string CHECK_GEOFENCE_SERVICE_TOPIC = 'smarc/srv/check_geofence' # geographic_msgs/srv/GetGeoPath
string GEOFENCE_STATUS_TOPIC = 'smarc/geofence_status' # smarc_msgs/msg/GeofenceStatusStamped
string GEOFENCE_POLYGONS_TOPIC = 'smarc/geofence_polygons' #smarc_msgs/msg/GeofencePolygonsStamped

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
string WARA_PS_SENSOR_EXECUTING_TASKS_TOPIC = 'waraps/sensor/executing_tasks'
string WARA_PS_SENSOR_BT_TOPIC = 'waraps/sensor/bt'

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




################
# DEPRECATED TOPICS - to be removed
################
#string BATTERY_TOPIC = 'core/battery'
string GPS_TOPIC = 'core/gps'
#string HEADING_TOPIC = 'core/heading'
#string ABORT_TOPIC = 'core/abort'
string HEARTBEAT_TOPIC = 'core/heartbeat'
string VEHICLE_READY_TOPIC = 'core/vehicle_ready'