# Used by the dji_captain, namespaced as needed.
# Usually under /M350

# moving around
string MOVE_TO_SETPOINT_TOPIC = 'move_to_setpoint' # PoseStamped
string LABELED_UTM_TOPIC = 'labeled_utm_topic' # String, formatted: "utm_{zone}_{band}"

# user feedback
string CONTROLLER_INPUT_TOPIC = 'joy' # Joy
string CONTROLLER_VIBRATION_TOPIC = 'joy/set_feedback' # JoyFeedback
string TTS_TOPIC = 'speak' # String

# gimbal camera
string GIMBAL_CAMERA_RAW_TOPIC = 'gimbal_camera/image_raw' # Image

# object detectors, these are in normalized camera pixel coordinates
string ESTIMATED_BUOY_TOPIC = 'alars_detection/buoy' # PointStamped
string ESTIMATED_AUV_TOPIC = 'alars_detection/auv' # PointStamped
string ESTIMATED_MIDDLE_TOPIC = 'alars_detection/middle' # PointStamped
string ESTIMATED_HOOK_TOPIC = 'alars_detection/hook_est' #PoseStamped
string ESTIMATED_EKF_HOOK_TOPIC = 'alars_detection/hook_ekf' #PoseStamped

# services
string ENABLE_ALARS_DETECTOR_SERVICE_TOPIC = 'enable_alars_detector' # Trigger
string DISABLE_ALARS_DETECTOR_SERVICE_TOPIC = 'disable_alars_detector' # Trigger
string ENABLE_HOOK_ESTIMATOR_SERVICE_TOPIC = 'enable_hook_estimator' # Trigger
string DISABLE_HOOK_ESTIMATOR_SERVICE_TOPIC = 'disable_hook_estimator' # Trigger

# sensors that are not coming from PSDK
string LOAD_CELL_RAW_TOPIC = 'sensor/load_cell_raw' # Int32
string LOAD_CELL_WEIGHT_TOPIC = 'sensor/load_cell_weight' # Float32
