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
string VERTICAL_THRUSTER_1_CMD = "actuators/vertical_thruster_1_cmd"
string VERTICAL_THRUSTER_2_CMD = "actuators/vertical_thruster_2_cmd"
string VERTICAL_THRUSTER_3_CMD = "actuators/vertical_thruster_3_cmd"
string VERTICAL_THRUSTER_4_CMD = "actuators/vertical_thruster_4_cmd"

#Thrusters feedback
string THRUSTER_PORT_FB = "actuators/thruster_port_fb"
string THRUSTER_STRB_FB = "actuators/thruster_strb_fb"
string VERTICAL_THRUSTER_1_FB = "actuators/vertical_thruster_1_fb"
string VERTICAL_THRUSTER_2_FB = "actuators/vertical_thruster_2_fb"
string VERTICAL_THRUSTER_3_FB = "actuators/vertical_thruster_3_fb"
string VERTICAL_THRUSTER_4_FB = "actuators/vertical_thruster_4_fb"


# Topics for Payload Sensors

# Topics for ....

#Leak topic
string LEAK_TOPIC = "core/leak"


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
string EXTENDED_VERTICAL_THRUSTER_1_FB_TOPIC = "extended/actuators/vertical_thruster_1_fb"
string EXTENDED_VERTICAL_THRUSTER_2_FB_TOPIC = "extended/actuators/vertical_thruster_2_fb"
string EXTENDED_VERTICAL_THRUSTER_3_FB_TOPIC = "extended/actuators/vertical_thruster_3_fb"
string EXTENDED_VERTICAL_THRUSTER_4_FB_TOPIC = "extended/actuators/vertical_thruster_4_fb"

#Extended Battery topics
string EXTENDED_BATTERY_1_TOPIC = "extended/battery1"
string EXTENDED_BATTERY_2_TOPIC = "extended/battery2"



#Communication
string SATELITE_RECEIVED_TOPIC = "communication/satelite_received"
string USBL_RECEIVED_TOPIC = "communication/usbl/received"
string USBL_RECEIVED_CHR_TOPIC = "communication/usbl/received/chr"