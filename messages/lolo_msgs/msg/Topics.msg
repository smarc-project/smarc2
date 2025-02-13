# This file defines all the topics used on lolo
# The goal is to have a single location that all cpp/py scripts can easily access

# Example
# string EXAMPLE_TOPIC = 'lolo/example_topic'

# Topics for Navigation and Control
string DVL_TOPIC = 'dvl/bottomtrack'

#Contorl surfaces setpoint
string RUDDER_CMD = "lolo/actuators/rudder_cmd"
string ELEVATOR_CMD = "lolo/actuators/elevator_cmd"
string ELEVON_PORT_CMD = "lolo/actuators/elevon_port_cmd"
string ELEVON_STRB_CMD = "lolo/actuators/elevon_strb_cmd"

#Control surfaces feedback
string RUDDER_FB = "lolo/actuators/rudder_fb"
string ELEVATOR_FB = "lolo/actuators/elevator_fb"
string ELEVON_PORT_FB = "lolo/actuators/elevon_port_fb"
string ELEVON_STRB_FB = "lolo/actuators/elevon_strb_fb"

#Thrusters setpoint
string THRUSTER_PORT_CMD = "lolo/actuators/thruster_port_cmd"
string THRUSTER_STRB_CMD = "lolo/actuators/thruster_strb_cmd"
string VERTICAL_THRUSTER_1_CMD = "lolo/actuators/vertical_thruster_1_cmd"
string VERTICAL_THRUSTER_2_CMD = "lolo/actuators/vertical_thruster_2_cmd"
string VERTICAL_THRUSTER_3_CMD = "lolo/actuators/vertical_thruster_3_cmd"
string VERTICAL_THRUSTER_4_CMD = "lolo/actuators/vertical_thruster_4_cmd"

#Thrusters feedback
string THRUSTER_PORT_FB = "lolo/actuators/thruster_port_fb"
string THRUSTER_STRB_FB = "lolo/actuators/thruster_strb_fb"
string VERTICAL_THRUSTER_1_FB = "lolo/actuators/vertical_thruster_1_fb"
string VERTICAL_THRUSTER_2_FB = "lolo/actuators/vertical_thruster_2_fb"
string VERTICAL_THRUSTER_3_FB = "lolo/actuators/vertical_thruster_3_fb"
string VERTICAL_THRUSTER_4_FB = "lolo/actuators/vertical_thruster_4_fb"


# Topics for Payload Sensors

# Topics for ....

#Heartbeat topic
string HEARTBEAT_TOPIC = "lolo/heartbeat"

string LOLO_ABORT_TOPIC = "lolo/lolo_abort"

#Leak topic
string LEAK_TOPIC = "lolo/leak"

#Battry topics
string BATTERY_1_TOPIC = "lolo/battery1"
string BATTERY_2_TOPIC = "lolo/battery2"


#Extended interface
string EXTENDED_STATUS_TOPIC = "lolo/extended/status"
string EXTENDED_INTERNAL_TEMPERATURE_TOPIC = "lolo/extended/internal_temperature"
string EXTENDED_INTERNAL_PRESSURE_TOPIC = "lolo/extended/internal_pressure"

string EXTENDED_RUDDER_FB_TOPIC = "lolo/extended/actuators/rudder_fb"
string EXTENDED_ELEVATOR_FB_TOPIC = "lolo/extended/actuators/elevator_fb"
string EXTENDED_PORT_ELEVON_FB_TOPIC = "lolo/extended/actuators/elevon_port_fb"
string EXTENDED_STRB_ELEVON_FB_TOPIC = "lolo/extended/actuators/elevon_strb_fb"
string EXTENDED_PORT_THRUSTER_FB_TOPIC = "lolo/extended/actuators/thruster_port_fb"
string EXTENDED_STRB_THRUSTER_FB_TOPIC = "lolo/extended/actuators/thruster_strb_fb"
string EXTENDED_VERTICAL_THRUSTER_1_FB_TOPIC = "lolo/extended/actuators/vertical_thruster_1_fb"
string EXTENDED_VERTICAL_THRUSTER_2_FB_TOPIC = "lolo/extended/actuators/vertical_thruster_2_fb"
string EXTENDED_VERTICAL_THRUSTER_3_FB_TOPIC = "lolo/extended/actuators/vertical_thruster_3_fb"
string EXTENDED_VERTICAL_THRUSTER_4_FB_TOPIC = "lolo/extended/actuators/vertical_thruster_4_fb"


#Communication
string SATELITE_RECEIVED_TOPIC = "lolo/communication/satelite_received"
string USBL_RECEIVED_TOPIC = "/lolo/communication/usbl/received"
string USBL_RECEIVED_CHR_TOPIC = "/lolo/communication/usbl/received/chr"