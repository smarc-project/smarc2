# Used by the dji_captain, namespaced as needed.
# Usually under /M350

# moving around
string MOVE_TO_SETPOINT_TOPIC = 'move_to_setpoint' # PoseStamped
string LABELED_UTM_TOPIC = 'labeled_utm_topic' # String, formatted: "utm_{zone}_{band}"


# cameras
string GIMBAL_CAMERA_RAW_TOPIC = 'gimbal_camera/camera/image_raw' # Image
string GIMBAL_CAMERA_INFO_TOPIC = 'gimbal_camera/camera/camera_info' #CameraInfo
string FISHEYE_CAMERA_RAW_TOPIC = 'fisheye_camera/camera/image_raw' # Image
string FISHEYE_CAMERA_INFO_TOPIC = 'fisheye_camera/camera/camera_info' #CameraInfo


# sensors that are not coming from PSDK
string LOAD_CELL_RAW_TOPIC = 'sensor/load_cell_raw' # Int32
string LOAD_CELL_WEIGHT_TOPIC = 'sensor/load_cell_weight' # Float32


# propeller rpms all Float32, corresponds to esc_data[0..3] in this order
string PROP_RPM_FR = 'sensor/props/fr'
string PROP_RPM_FL = 'sensor/props/fl'
string PROP_RPM_BL = 'sensor/props/bl'
string PROP_RPM_BR = 'sensor/props/br'
# bottom ones for FC30
string PROP_RPM_FR_BOTTOM = 'sensor/props/frb'
string PROP_RPM_FL_BOTTOM = 'sensor/props/flb'
string PROP_RPM_BL_BOTTOM = 'sensor/props/blb'
string PROP_RPM_BR_BOTTOM = 'sensor/props/brb'




# object detectors in normalized image coordinates [-1,1]
# (0,0) is the center of the image, +x is right, +y is up!
# If this is not the case, FIX IT.
string ESTIMATED_BUOY_TOPIC = 'alars_detection/buoy' # PointStamped, 
string ESTIMATED_AUV_TOPIC = 'alars_detection/auv' # PointStamped
string ESTIMATED_AUV_OBB_TOPIC = "alars_detection/auv_obb" # PolygonStamped
string ESTIMATED_AUV_HEAD_TOPIC = "alars_detection/auv_head" # PolygonStamped
string ESTIMATED_BUOY_OBB_TOPIC = "alars_detection/buoy_obb" # PolygonStamped
string ESTIMATED_MIDDLE_TOPIC = 'alars_detection/middle' # PointStamped
string ESTIMATED_CNN_HOOK_ANCHOR_TOPIC = 'alars_detection/cnn' # PointStamped
string ESTIMATED_CNN_AFTER_CATCH_FLY_DIRECTION_TOPIC = 'alars_detection/cnn_vec' # PointStamped
# instead of captain subbing to image and so on
# let the consumer of camera data tell it if the camera is good, detection can happen etc.
string CAM_PROCESSOR_HAPPY_TOPIC = 'alars_detection/cam_processor_happy' # Bool

# Topic for publishing detected objects (excluding SAM and buoy) as labeled OBBs.
# Each message contains Polygon[] obbs and string[] ids (class names).
string LABELED_OBBS_TOPIC="alars_detection/labeled_obbs"

# projected points
string PROJECTED_AUV_HEAD_TOPIC = 'alars_projection/auv_head' # PolygonStamped
string PROJECTED_AUV_OBB_TOPIC = 'alars_projection/auv_obb' # PolygonStamped
string PROJECTED_BUOY_OBB_TOPIC = 'alars_projection/buoy_obb' # PolygonStamped


# services
string ENABLE_ALARS_DETECTOR_SERVICE_TOPIC = 'enable_alars_detector' # Trigger
string DISABLE_ALARS_DETECTOR_SERVICE_TOPIC = 'disable_alars_detector' # Trigger


