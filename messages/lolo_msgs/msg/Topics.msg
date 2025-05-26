# This file defines all the topics used on lolo
# The goal is to have a single location that all cpp/py scripts can easily access

# Example
# string EXAMPLE_TOPIC = 'example_topic'

#Contorl surfaces setpoint
string RUDDER_CMD = "actuators/rudder_cmd"
string ELEVATOR_CMD = "actuators/elevator_cmd"
string ELEVON_PORT_CMD = "actuators/elevon_port_cmd"
string ELEVON_STRB_CMD = "actuators/elevon_strb_cmd"

#Control surfaces feedback
string RUDDER_FB = "actuators/rudder_fb"
string ELEVATOR_FB = "actuators/elevator_fb"
string ELEVON_PORT_FB = "actuators/elevon_port_fb"
string ELEVON_STRB_FB = "actuators/elevon_strb_fb"

#Thrusters setpoint
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
string VERTICAL_THRUSTER_FRONT_PORT_FB = "actuators/vertical_thruster_front_strb_fb"
string VERTICAL_THRUSTER_FRONT_STRB_FB = "actuators/vertical_thruster_front_strb_fb"


# Topics for Payload Sensors

# Topics for ....

#Heartbeat topic
string HEARTBEAT_TOPIC = "heartbeat"

#Leak topic
string LEAK_TOPIC = "leak"

#Battry topics
string BATTERY_1_TOPIC = "extended/battery1"
string BATTERY_2_TOPIC = "extended/battery2"


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



#Communication
string SATELITE_RECEIVED_TOPIC = "communication/satelite_received"
string USBL_RECEIVED_TOPIC = "communication/usbl/received"
string USBL_RECEIVED_CHR_TOPIC = "communication/usbl/received/chr"

#Navigation
string INS_ODOM_TOPIC = "ins_odom"
string INS_RAW_TOPIC = "/ix/ins"
string INS_IMU_TOPIC = "/standard/imu"

#Control topics
#Publish info relevant to control as a Float32
string CONTROL_YAW_TOPIC = "control/yaw"
string CONTROL_YAW_RATE_TOPIC = "control/yawrate"
string CONTROL_PITCH_TOPIC = "control/pitch"
string CONTROL_PITCH_RATE_TOPIC = "control/pitchrate"
string CONTROL_ROLL_TOPIC = "control/roll"
string CONTROL_ROLL_RATE_TOPIC = "control/rollrate"
string CONTROL_SURGE_RATE_TOPIC = "control/surgerate"
string CONTROL_DEPTH_TOPIC = "control/depth"
string CONTROL_ALTITUDE_TOPIC = "control/altitude"
