#
# DJI Drone links and relevant frames
# Most are published by the dji_captain node
#

# UTM == Universal Transverse Mercator, globally defined frame that is usually very far that floats have problem doing math
# UTM altitude 0 = sea level
string UTM = 'utm'
# A point inside UTM, also at sea level. Use this for basically all control and navigation.
string MAP = 'map'
# ODOM == HOME_POINT == where the drone is turned on usually.
# Not necessarily at sea level. Could be above, could be below.
string ODOM = 'odom'
string HOME_POINT = 'home_point'

# The drone's body, defined as the point between the thick parts
# of the legs.
string BASE_LINK = 'base_link'
# Same BASE_LINK, but only has the yaw component of the orientation.
string BASE_FLAT = 'base_flat_link'
# middle of the 4 points of the landing gear
string LANDING_GEAR_CENTER = 'landing_gear_center_link'


# parts of the alars module that are relevant. in-between parts
# like the roll/pitch/yaw arms of the gimbal are not included here
# even though they are published by the z1_pro_driver node
string ROPE_BASE_LINK = 'rope_base_link'

string GIMBAL_CAMERA_LINK = 'z1_camera_link'
#string GIMBAL_CAMERA_LINK = 'z1_global_camera_link'
string FISHEYE_CAMERA_LINK = 'fisheye_camera_link'

# optical frames: z "depth", x "right", y "down" with top-left origin
string GIMBAL_OPTICAL_FRAME = 'z1_optical_frame'
#string GIMBAL_OPTICAL_FRAME = 'z1_global_optical_frame'
string FISHEYE_OPTICAL_FRAME = 'fisheye_optical_frame'



# Used by projection/filter
string ESTIMATED_AUV = 'estimated_auv'
string ESTIMATED_BUOY = 'estimated_buoy'
