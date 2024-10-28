# This is a file that defines all the topics of drone.
# The goal is to have one location that all cpp/py scripts
# can easily access and thus avoid having 100 parameters for topics all
# over the place, repeated for all subs/pubs...
# It is assumed that the nodes will namespace as needed.

####################
# Actuator commands
####################

string PROP1_CMD_TOPIC = 'core/prop_1/cmd'
string PROP2_CMD_TOPIC = 'core/prop_2/cmd'
string PROP3_CMD_TOPIC = 'core/prop_3/cmd'
string PROP4_CMD_TOPIC = 'core/prop_4/cmd'

string DRONE_ODOM_GT_TOPIC = 'odom_gt'
string CAMERA_DATA_TOPIC = 'core/fpcamera/image'
string CAMERA_COMPRESSED_DATA_TOPIC = 'core/fpcamera/image_compressed'


string PROP1_FB_TOPIC = 'core/prop_1/feedback'
string PROP2_FB_TOPIC = 'core/prop_2/feedback'
string PROP3_FB_TOPIC = 'core/prop_3/feedback'
string PROP4_FB_TOPIC = 'core/prop_4/feedback'

string IMU_TOPIC = 'core/imu'
string GPS_TOPIC = 'core/gps'
string RANGE_TOPIC = 'core/range'
string DEPTH_TOPIC = 'core/depth'

string DR_POSITION_TOPIC = 'est_position'
string AUV_RELATIVE_POSITION_TOPIC = 'auv/estimated_relative_position'
string BUOY_DETECTOR_ESTIMATE_TOPIC = 'auv/buoy_est'

