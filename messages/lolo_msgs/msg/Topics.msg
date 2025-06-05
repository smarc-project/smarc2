# This file defines all the topics used on lolo
# The goal is to have a single location that all cpp/py scripts can easily access

# Example
# string EXAMPLE_TOPIC = 'example_topic'

# PID controllers setpoints. All Float32s.
string YAW_SETPOINT = "ctrl/yaw_setpoint"
string YAW_RATE_SETPOINT = "ctrl/yawrate_setpoint"
string YAW_ACTUATION = "ctrl/yaw_actuation"
string ROLL_SETPOINT = "ctrl/roll_setpoint"
string ROLL_RATE_SETPOINT = "ctrl/rollrate_setpoint"
string ROLL_ACTUATION = "ctrl/roll_actuation"
string PITCH_SETPOINT = "ctrl/pitch_setpoint"
string PITCH_RATE_SETPOINT = "ctrl/pitchrate_setpoint"
string PITCH_ACTUATION = "ctrl/pitch_actuation"
# This value is also under smarc_control_msgs, leave it here for convenience?
string DEPTH_SETPOINT = "ctrl/depth_setpoint"
string RPM_SETPOINT = "ctrl/rpm_setpoint"

#Contorl surfaces setpoint. All Float32s.
string RUDDER_CMD = "actuators/rudder_cmd"
string ELEVATOR_CMD = "actuators/elevator_cmd"
string ELEVON_PORT_CMD = "actuators/elevon_port_cmd"
string ELEVON_STRB_CMD = "actuators/elevon_strb_cmd"

#Control surfaces feedback. All Float32s.
string RUDDER_FB = "actuators/rudder_fb"
string ELEVATOR_FB = "actuators/elevator_fb"
string ELEVON_PORT_FB = "actuators/elevon_port_fb"
string ELEVON_STRB_FB = "actuators/elevon_strb_fb"

#Thrusters setpoint. All Float32s.
string THRUSTER_PORT_CMD = "actuators/thruster_port_cmd"
string THRUSTER_STRB_CMD = "actuators/thruster_strb_cmd"
string VERTICAL_THRUSTER_BACK_PORT_CMD = "actuators/vertical_thruster_back_port_cmd"
string VERTICAL_THRUSTER_BACK_STRB_CMD = "actuators/vertical_thruster_back_strb_cmd"
string VERTICAL_THRUSTER_FRONT_PORT_CMD = "actuators/vertical_thruster_front_port_cmd"
string VERTICAL_THRUSTER_FRONT_STRB_CMD = "actuators/vertical_thruster_front_strb_cmd"

#Thrusters feedback
string THRUSTER_PORT_FB = "actuators/thruster_port_fb"
string THRUSTER_STRB_FB = "actuators/thruster_strb_fb"
string VERTICAL_THRUSTER_BACK_PORT_FB = "actuators/vertical_thruster_back_port_fb"
string VERTICAL_THRUSTER_BACK_STRB_FB = "actuators/vertical_thruster_back_strb_fb"
string VERTICAL_THRUSTER_FRONT_PORT_FB = "actuators/vertical_thruster_front_port_fb"
string VERTICAL_THRUSTER_FRONT_STRB_FB = "actuators/vertical_thruster_front_strb_fb"


#Extended interface
string EXTENDED_STATUS_TOPIC = "extended/status"
string EXTENDED_SETTINGS_TOPIC = "extended/settings_cmd"
string EXTENDED_INTERNAL_TEMPERATURE_TOPIC = "extended/internal_temperature"
string EXTENDED_INTERNAL_PRESSURE_TOPIC = "extended/internal_pressure"

string EXTENDED_RUDDER_FB_TOPIC = "extended/actuators/rudder_fb"
string EXTENDED_ELEVATOR_FB_TOPIC = "extended/actuators/elevator_fb"
string EXTENDED_PORT_ELEVON_FB_TOPIC = "extended/actuators/elevon_port_fb"
string EXTENDED_STRB_ELEVON_FB_TOPIC = "extended/actuators/elevon_strb_fb"
string EXTENDED_PORT_THRUSTER_FB_TOPIC = "extended/actuators/thruster_port_fb"
string EXTENDED_STRB_THRUSTER_FB_TOPIC = "extended/actuators/thruster_strb_fb"
string EXTENDED_VERTICAL_THRUSTER_FRONT_PORT_FB_TOPIC = "extended/actuators/vertical_thruster_front_port_fb"
string EXTENDED_VERTICAL_THRUSTER_FRONT_STRB_FB_TOPIC = "extended/actuators/vertical_thruster_front_strb_fb"
string EXTENDED_VERTICAL_THRUSTER_BACK_PORT_FB_TOPIC = "extended/actuators/vertical_thruster_back_port_fb"
string EXTENDED_VERTICAL_THRUSTER_BACK_STRB_FB_TOPIC = "extended/actuators/vertical_thruster_back_strb_fb"

#Extended Battery topics
string EXTENDED_BATTERY_1_TOPIC = "extended/battery1"
string EXTENDED_BATTERY_2_TOPIC = "extended/battery2"



#Communication
string SATELITE_RECEIVED_TOPIC = "communication/satelite_received"
string USBL_RECEIVED_TOPIC = "communication/usbl/received"
string USBL_RECEIVED_CHR_TOPIC = "communication/usbl/received/chr"

#Navigation
string INS_ODOM_TOPIC = "ins_odom"
string INS_RAW_TOPIC = "/ix/ins"
string INS_IMU_TOPIC = "/standard/imu"


#Sensors
string GPS_RAW_TOPIC = sensors/gps/raw
string GPS_TOPIC = sensors/gps

string SVS_RAW_TOPIC = sensors/svs/raw
string SVS_TOPIC = sensors/svs

string CTD_RAW_TOPIC = sensors/ctd/raw
string CTD_TOPIC = sensors/ctd

string DO_RAW_REQUEST_TOPIC = sensors/do/raw_request
string DO_RAW_TOPIC = sensors/do/raw
string DO_TOPIC = sensors/do

string TURB_RAW_TOPIC = sensors/turbidity/raw
string TURB_TOPIC = sensors/turbidity

string FLUORESCENCE_RAW_TOPIC = sensors/fluorescence/raw
string FLUORESCENCE_TOPIC = sensors/fluorescence

string DVL_TOPIC = sensors/dvl

string FLS_WC_TOPIC = sensors/fls/watercolumn
string FLS_IMAGE_TOPIC = sensors/fls/watercolumn/image

string MBES_WC_TOPIC = sensors/fls/watercolumn
string MBES_IMAGE_TOPIC = sensors/fls/watercolumn/image
string MBES_BATHY_TOPIC = sensors/fls/bathymetry
string MBES_BATHY_POINTCLOUD_TOPIC = sensors/fls/bathymetry/points

string LEAK_TOPIC = "sensor/leak"
