# This file defines all the topics used on Evolo
# The goal is to have a single location that all cpp/py scripts can easily access

#Control
string EVOLO_STEERING_SETPOINT = "ctrl/steering_setpoint"
string EVOLO_SPEED_SETPOINT = "ctrl/speed_setpoint"
string EVOLO_TWIST_SETPOINT = "ctrl/twist_setpoint" #Type: TwistStamped
string EVOLO_CONTROL_SETPOINT = "ctrl/control_setpoint" #Type: Odometry
string EVOLO_TWIST_PLANNED = "ctrl/twist_planned" #Type: TwistStamped
string EVOLO_CONTROL_PLANNED = "ctrl/control_planned" #Type: Odometry
string EVOLO_CURRENT_WP = "ctrl/target_wp" # type: PointStamped

# Prox-ops backend/action-server contract.
string PROX_OPS_BACKEND_STATUS = "backend/status" #Type: evolo_msgs/ProxOpsBackendStatus
string PROX_OPS_BACKEND_TARGET_STATE = "backend/target_state" #Type: nav_msgs/Odometry
string PROX_OPS_BACKEND_CANDIDATE_PATH = "backend/candidate_path" #Type: nav_msgs/Path
string PROX_OPS_BACKEND_TWIST_PLANNED = "backend/twist_planned" #Type: geometry_msgs/TwistStamped
string PROX_OPS_BACKEND_COMMAND = "backend/command" #Type: std_msgs/String

#communication to and from captain
string EVOLO_CAPTAIN_TO = "captain/to"
string EVOLO_CAPTAIN_FROM = "captain/from"
string EVOLO_CAPTAIN_STATE = "captain/state"

string EVOLO_MQTT_RECEIVE = "mqtt/fromevolo"
string EVOLO_MQTT_SEND = "mqtt/toevolo"

# LIDAR
string EVOLO_OCCUPANCY_GRID = "occupancyMap"
string EVOLO_CBF_OBSTACLES = "obstacles"

# Gimbal control.
string EVOLO_MQTT_GIMBAL_CAMCMD = "mqtt/cam_cmd"
string EVOLO_ROS_GIMBAL_CAMCMD = "gimbal/cam_cmd"
string EVOLO_GIMBAL_FEEDBACK = "gimbal/feedback"
string EVOLO_GIMBAL_CTRL = "gimbal/ctrl"
#TODO: string MQTT_GIMBAL_CMD_TOPIC: The topic name in MQTT. 

#TODO SIDESCAN
