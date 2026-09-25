# Used by the dji_captain, namespaced as needed.
# Usually under /M350

# Status strings, for human-readable strings in topics
# Captain's status string
string CAPTAIN_STATUS_STR_TOPIC = 'status_str/captain_status'
string ALARS_BT_STATUS_STR_TOPIC = 'status_str/alars_bt'
string ALARS_PING_SEARCH_STATUS_STR_TOPIC = 'status_str/ping_search'

# moving around
string MOVE_TO_SETPOINT_TOPIC = 'move_base' # PoseStamped
string VELOCITY_SETPOINT_TOPIC = 'cmd_vel' # TwistStamped

string LABELED_UTM_TOPIC = 'labeled_utm_topic' # String, formatted: "utm_{zone}_{band}"
string BASE_LINK_IN_MAP_TOPIC = 'base_link_in_map' # PoseStamped with header.frame_id == /robot_name/map


# cameras
string GIMBAL_CAMERA_RAW_TOPIC = 'gimbal_camera/camera/image_raw' # Image
string GIMBAL_CAMERA_INFO_TOPIC = 'gimbal_camera/camera/camera_info' #CameraInfo


# sensors that are not coming from PSDK
string LOAD_CELL_RAW_TOPIC = 'sensor/load_cell_raw' # Int32
string LOAD_CELL_WEIGHT_TOPIC = 'sensor/load_cell_weight' # Float32
string HOOK_DEPTH_TOPIC = 'sensor/hook_depth' # Float32
string SUCCOR_ESTIMATE_TOPIC = 'sensor/succorfish_geopoint' #GeoPointStamped


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

# mirrors the hardcoded topics of yolo_ros
string YOLO_DETECTIONS = 'yolo/detections' # yolo_msgs.msg::DetectionArray


# Multi-object estimation outputs.
string PROJECTED_OBJECT_POSES_ARRAY_TOPIC = 'alars_projection/object_poses_array' # dji_msgs/ObjectPoseWithCovarianceArray
string OBJECT_EKF_STATUS_ARRAY_TOPIC = 'alars_ekf/status_array' # dji_msgs/ObjectEkfStatusArray
string OBJECT_EKF_RESET_SERVICE = 'alars_ekf/reset' # dji_msgs/ResetObjectEkf

# Only for visualization
string OBJECT_EKF_MARKERS_TOPIC = 'rviz/alars_projection/object_pose_markers' # visualization_msgs/MarkerArray

# Hook Kalman Filter Topics 
string HOOK_STATE_CARTESIAN = "alars_hook_kf/hook_state" # nav_msgs.msg/Odometry                -- hook estimate in cartesian coordinates 
string HOOK_STATE_ANGULAR = "alars_hook_kf/hook_swing_state" # nav_msgs.msg/Odometry            -- hook state estimate in angular coordinates, needed for LQG controller 
string HOOK_RAW_MEASUREMENT = "alars_hook_kf/hook_raw_measurement" # sensor_msgs.msg/JointState -- takes the yolo measurement and compute the hook position, needed for diagnostic

# Hook Parameters
string HOOK_PENDULUM_PARAMETERS = "alars_pendulum/hook_pendulum_parameters" # std_msgs.msg/Float64MultiArray
# Raw sysid output: estimate_length_and_damping -> hook_kalman_filter_node. 
string HOOK_PENDULUM_PARAMETERS_IDENTIFIED = "alars_pendulum/hook_pendulum_parameters_identified" # std_msgs.msg/Float64MultiArray

# Move_to_damped Topics 
string CMD_VELOCITY_DRONE_FRAME = "alars_move_to_damped/cmd_vel_drone_frame" # geometry_msgs.msg/Vector3Stamped