# This is a file that defines all the topics of sam_graph_slam_2.
# This package is relevant to localization in semi-structured environments with detectable point or line features.
# Specifically involving the algae farm.
# It is assumed that the nodes will namespace as needed.

######
# MAP
######
string MAP_LINE_DEPTH_TOPIC = 'map/line_depth'
string MAP_POINT_FEATURE_TOPIC = 'map/point_features'
string MAP_LINE_FEATURE_TOPIC = 'map/line_features'
string MAP_MARKED_LINE_SPHERES_TOPIC = 'map/marked_lines_spheres'
string MAP_MARKED_LINE_LINES_TOPIC = 'map/marked_lines_lines'

###########
# Detector
###########
string DETECTOR_HYPOTH_TOPIC = 'payload/sidescan/detection_hypothesis'  # Msg type: Detection2DArray
string DETECTOR_MARKER_TOPIC = 'payload/sidescan/detection_markers'  # Msg type:MarkerArray
string DETECTOR_RAW_SSS_TOPIC = 'payload/sidescan/image'  # Msg type: Image
string DETECTOR_MARKED_SSS_TOPIC = 'payload/sidescan/detection_hypothesis_image'  # Msg Type: Image

#################
# Dead reckoning
#################
# This is only intended for use with the temporary DR, defined in pipeline_slam_dr_gt_publisher
string DR_ODOM_TOPIC = 'graph_dr/dr_odom'
string GT_ODOM_TOPIC = 'graph_dr/gt_odom'