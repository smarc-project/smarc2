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