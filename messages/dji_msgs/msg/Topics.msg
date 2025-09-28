# Used by the dji_captain, namespaced as needed.
# Usually under /M350

# moving around
string MOVE_TO_SETPOINT_TOPIC = 'move_to_setpoint' # PoseStamped

# user feedback
string CONTROLLER_INPUT_TOPIC = 'joy' # Joy
string CONTROLLER_VIBRATION_TOPIC = 'joy/set_feedback' # JoyFeedback
string TTS_TOPIC = 'speak' # String

# gimbal camera
string GIMBAL_CAMERA_RAW_TOPIC = 'gimbal_camera/image_raw' # Image

# object detectors
string ESTIMATED_BUOY_TOPIC = 'alars_detection/buoy' # Float32MultiArray
string ESTIMATED_AUV_TOPIC = 'alars_detection/auv' # Float32MultiArray
string ESTIMATED_MIDDLE_TOPIC = 'alars_detection/middle' # Float32MultiArray

# services
string ENABLE_ALARS_DETECTOR_SERVICE_TOPIC = 'enable_alars_detector' # Trigger
string DISABLE_ALARS_DETECTOR_SERVICE_TOPIC = 'disable_alars_detector' # Trigger