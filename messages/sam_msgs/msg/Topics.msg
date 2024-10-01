# This is a file that defines all the topics of sam.
# The goal is to have one location that all cpp/py scripts
# can easily access and thus avoid having 100 parameters for topics all
# over the place, repeated for all subs/pubs...
# It is assumed that the nodes will namespace as needed.

####################
# Actuator commands
####################
string VBS_CMD_TOPIC = 'core/vbs_cmd'
string LCG_CMD_TOPIC = 'core/lcg_cmd'
string THRUSTER1_CMD_TOPIC = 'core/thruster1_cmd'
string THRUSTER2_CMD_TOPIC = 'core/thruster2_cmd'
string THRUST_VECTOR_CMD_TOPIC = 'core/thrust_vector_cmd'
string RPM_CMD_TOPIC = 'core/rpm_cmd'
string DEPTH_TOPIC = 'core/depth20_pressure'
string DVL_TOPIC = 'core/dvl'
string LEAK_TOPIC = 'core/leak'
string VBS_FB_TOPIC = 'core/vbs_fb'
string LCG_FB_TOPIC = 'core/lcg_fb'
string THRUSTER1_FB_TOPIC = 'core/thruster1_fb'
string THRUSTER2_FB_TOPIC = 'core/thruster2_fb'

string STIM_IMU_TOPIC = 'core/imu'
string SBG_IMU_TOPIC = 'core/sbg_imu'

string PRESS_DEPTH20_TOPIC = 'core/depth20_pressure'

string SIDESCAN_TOPIC = 'payload/sidescan'
string TOGGLE_SIDESCAN_SERVICE = 'payload/toggle_sidescan'
string SIDESCAN_STATUS_TOPIC = 'payload/sidescan_status'

#UAVCAN bridge topics
string GPS_FIX_TOPIC = 'core/can_gps'
string MAGNETIC_FIELD_TOPIC = 'core/compass'
string VBS_TANK_TEMPERATURE_TOPIC = 'core/vbs_tank_temperature'
string ESC_STATUS0_TOPIC = 'core/esc_status0_fb'
string ESC_STATUS1_TOPIC = 'core/esc_status1_fb'
string CIRCUIT_STATUS_TOPIC = 'core/circuit_status'
string YOST_IMU_TOPIC = 'core/yost_imu'
string PRESS_DEPTH300_TOPIC = 'core/depth3000_pressure'
string MOTOR_TEMP_TOPIC = 'core/motor_temp'
string MOTOR_OIL_PRESSURE_TOPIC = 'core/motor_oil_pressure'
string VBS_TANK_PRESSURE_TOPIC = 'core/vbs_tank_pressure'
string BATTERY_STATUS_TOPIC = 'core/battery_status'
string CONSUMED_CHARED_ARRAY_TOPIC = 'core/consumed_charged_array'
string CTD_FB_TOPIC = 'core/ctd_fb'
string THRUSTERS_FEEDBACK_TOPIC = 'core/thrusters_fb'
string PANIC_FB_TOPIC = 'core/panic_fb'
string LEAK_TOPIC_FB = 'core/leak_fb'

string UTIL_CMD_TOPIC = 'core/util_cmd'
string ARRAY_CMD_TOPIC = 'core/util_array_cmd'
string TCG_CMD_TOPIC = 'core/tcg_cmd'
string DUAL_THRUSTER_CMD_TOPIC = 'core/thruster_cmd'
string LIGHTS_CMD_TOPIC = 'core/light_cmd'
string PANIC_CMD_TOPIC = 'core/panic_cmd'
string DROPWEIGHTS_CMD_TOPIC = 'core/dropweights_cmd'
string LED_CMD_TOPIC = 'core/led_cmd'
string DVL_CMD_TOPIC = 'core/dvl_relay'
string SSS_CMD_TOPIC = 'core/sss_relay'
string TOGGLE_7V_CMD_TOPIC = 'core/enable_7v'

string GET_NODE_INFO_SRV = 'core/uavcan_get_node_info'
string GET_TRANSPORT_STATS_SRV = 'core/uavcan_get_transport_stats'
string RESTART_NODE_SRV = 'core/uavcan_restart_node'
string UPDATE_BATTERY_SRV = 'core/uavcan_update_battery'