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

