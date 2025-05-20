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
string SPEED_TOPIC = 'smarc/speed' #float32
string POS_LATLON_TOPIC = 'smarc/latlon' #geopoint
string BATTERY_PERCENT_TOPIC = 'smarc/battery_percent'
string DEPTH_TOPIC = 'smarc/depth'
string ALTITUDE_TOPIC = 'smarc/altitude'


#Wara PS
string WARA_PS_ACTION_SERVER_HB_TOPIC = 'waraps/action_server_heartbeat'
