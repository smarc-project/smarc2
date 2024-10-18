# This is a file that defines all the topics of drone.
# The goal is to have one location that all cpp/py scripts
# can easily access and thus avoid having 100 parameters for topics all
# over the place, repeated for all subs/pubs...
# It is assumed that the nodes will namespace as needed.

####################
# Actuator commands
####################

string PROP1_CMD_TOPIC = 'drone/prop_1/cmd'
string PROP2_CMD_TOPIC = 'drone/prop_2/cmd'
string PROP1_CMD_TOPIC = 'drone/prop_3/cmd'
string PROP2_CMD_TOPIC = 'drone/prop_4/cmd'

string DRONE_ODOM_GT_TOPIC = 'odom_gt'
string CAMERA_DATA_TOPIC = 'drone/fpcamera/image'
string CAMERA_COMPRESSED_DATA_TOPIC = 'drone/fpcamera/image_compressed'


string PROP1_FB_TOPIC = 'drone/prop_1/feedback'
string PROP2_FB_TOPIC = 'drone/prop_2/feedback'
string PROP3_FB_TOPIC = 'drone/prop_3/feedback'
string PROP4_FB_TOPIC = 'drone/prop_4/feedback'

string DRONE_IMU_TOPIC = 'drone/imu'
string DRONE_GPS_TOPIC = 'drone/gps'
string DRONE_RANGE_TOPIC = 'drone/range'
string DRONE_DEPTH_TOPIC = 'drone/depth'


