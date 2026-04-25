#! /bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/tmux_layout.sh"


ROBOT_NAME=$1
if [[ -z "$ROBOT_NAME" ]]; then
    echo "You must pass the robot name as the first argument! Pass one of: M350 or FC30"
    echo "This is required to namespace all the ROS2 nodes and topics correctly."
    echo "As well as to set parameters depending on the platform..."
    echo "Exiting."
    exit 1
fi

if [[ "$ROBOT_NAME" != "M350" && "$ROBOT_NAME" != "FC30" ]]; then
    echo "Invalid robot name: $ROBOT_NAME"
    echo "Please pass either M350 or FC30 as the first argument."
    echo "Exiting."
    exit 1
fi

HOME_ABOVE_WATER=$2
if [[ -z "$HOME_ABOVE_WATER" ]]; then
    echo "You must pass the home altitude above water level as the second argument!"
    echo "This is required for the dji_captain node to function properly."
    echo "Exiting."
    exit 1
fi

if ! [[ "$HOME_ABOVE_WATER" =~ ^[0-9]+\.[0-9]+$ ]]; then
    echo "HOME_ABOVE_WATER must be a floating point number! Adding a decimal point for you..."
    HOME_ABOVE_WATER="${HOME_ABOVE_WATER}.0"
    echo "HOME_ABOVE_WATER is set to $HOME_ABOVE_WATER"
fi


SESSION=${ROBOT_NAME}_bringup

# check if there is already a tmux session with this name
if tmux has-session -t $SESSION 2>/dev/null; then
    echo "There is already a tmux session named $SESSION."
    echo "Please close it before launching this script."
    echo "Exiting."
    exit 1
fi


if [[ "$(whoami)" == *"alars"* ]]; then
    USE_SIM_TIME=False
else
    USE_SIM_TIME=True
fi

if [[ $USE_SIM_TIME == "True" ]]; then
    # useful to make sure we don't accidentally connect to real hardware with the sim bringup
    # or when your pc has these set for the real thing and you dont want to swap around :,)
    export ROS_SUPER_CLIENT=""
    export ROS_DISCOVERY_SERVER=""
    export ROS_DOMAIN_ID=""
fi


# create a tmux session with a name
tmux -2 new-session -d -x 220 -y 60 -s "$SESSION"


# create a bunch of windows. These are the "tabs" you'll
# see at the bottom green line.
# C-b <NUM> will change to the tab.
# default window is 0

############
# 1 Captains
############
if [[ "$ROBOT_NAME" == "M350" ]]; then
    MAX_LOAD_KG="4.0"
    MIN_ALTITUDE_ABOVE_WATER="1.5"
elif [[ "$ROBOT_NAME" == "FC30" ]]; then
    MAX_LOAD_KG="30.0"
    MIN_ALTITUDE_ABOVE_WATER="5.0"
else # this should never happen due to the earlier check, but just in case
    echo "Invalid robot name: $ROBOT_NAME"
    echo "Please pass either M350 or FC30 as the first argument."
    echo "Exiting."
    exit 1
fi

CAPTAIN_CMD="ros2 launch dji_captain alars_captain.launch \
    robot_name:=$ROBOT_NAME \
    use_sim_time:=$USE_SIM_TIME \
    home_altitude_above_water:=$HOME_ABOVE_WATER \
    max_load_kg:=$MAX_LOAD_KG \
    min_altitude_above_water:=$MIN_ALTITUDE_ABOVE_WATER"
CAPTAIN_STATUS_CMD="ros2 topic echo /$ROBOT_NAME/captain_status std_msgs/msg/String --field data"
WRAPPER_CMD="ros2 launch psdk_wrapper wrapper.launch.py namespace:=/$ROBOT_NAME/wrapper"
DISCOVERY_SERVER_CMD="fast-discovery-server -i 0"
SERVICE_CALLER_CMD="ros2 run dji_captain service_caller --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME -p robot_name:=$ROBOT_NAME"
ALARS_SERVICES_CMD="ros2 launch dji_captain alars_services.launch.py robot_name:=$ROBOT_NAME use_sim_time:=$USE_SIM_TIME"

if [[ $USE_SIM_TIME = "False" ]]; then
    tmux_make_layout "$SESSION" Captains "
    col(
        1:row(
            1:var(DISCOVERY_SERVER_CMD),
            3:var(WRAPPER_CMD)
        ),
        3:row(
            2:var(CAPTAIN_CMD),
            3:var(CAPTAIN_STATUS_CMD),
            2:col(
                var(SERVICE_CALLER_CMD),
                var(ALARS_SERVICES_CMD)
            )
        )
    )" 
else
    tmux_make_layout "$SESSION" Captains "
    row(
        2:var(CAPTAIN_CMD),
        3:var(CAPTAIN_STATUS_CMD),
        2:col(
            var(SERVICE_CALLER_CMD),
            var(ALARS_SERVICES_CMD)
        )
    )"
fi


############
# 2 Action Servers
############
ALARS_SEARCH_CMD="ros2 run alars alars_search_action_server --ros-args -r __ns:=/$ROBOT_NAME \
-p robot_name:=$ROBOT_NAME \
-p use_sim_time:=$USE_SIM_TIME \
-p setpoint_threshold:=0.5 \
-p spiral_arm_distance:=2.0 \
-p min_setpoint_distance_to_drone:=1.0 \
-p detection_freshness_threshold:=1.0"

EKF_STALENESS_SECONDS=3.0
ALARS_FOLLOW_AUV_CMD="ros2 run alars alars_follow_auv_action_server --ros-args -r __ns:=/$ROBOT_NAME \
-p robot_name:=$ROBOT_NAME \
-p use_sim_time:=$USE_SIM_TIME \
-p detection_freshness_threshold:=$EKF_STALENESS_SECONDS"

ALARS_RECOVER_SETPOINT_TOLERANCE=0.2
if [[ $USE_SIM_TIME = "True" ]]; then
    ALARS_RECOVER_SETPOINT_TOLERANCE=0.25
fi
ALARS_RECOVER_CMD="ros2 run alars alars_recover_action_server --ros-args -r __ns:=/$ROBOT_NAME \
-p robot_name:=$ROBOT_NAME \
-p use_sim_time:=$USE_SIM_TIME \
-p setpoint_tolerance:=$ALARS_RECOVER_SETPOINT_TOLERANCE \
-p max_rope_length:=5.0"

ALARS_MOVE_TO_CMD="ros2 run alars alars_move_to_action_server --ros-args -r __ns:=/$ROBOT_NAME \
-p robot_name:=$ROBOT_NAME \
-p use_sim_time:=$USE_SIM_TIME"

tmux_make_layout "$SESSION" ALARSActions "
col(
    var(ALARS_SEARCH_CMD),
    var(ALARS_FOLLOW_AUV_CMD),
    var(ALARS_RECOVER_CMD),
    var(ALARS_MOVE_TO_CMD)
)"

############
# 3 BTs
############
# Grace period before WASP BT drops stale action servers from available task list.
WASP_BT_TASK_LIVELINESS_TIMEOUT=10.0

WASP_BT_CMD="ros2 launch wasp_bt wasp_bt.launch \
robot_name:=$ROBOT_NAME \
agent_type:=air \
pulse_rate:=10.0 \
use_sim_time:=$USE_SIM_TIME \
bt_health_timeout:=5.0 \
task_liveliness_timeout:=$WASP_BT_TASK_LIVELINESS_TIMEOUT"

LOADED_WEIGHT_KG=1.8 # real empty sam + hook + rope weight is 1.78kg, just the hook and rope is 0.79kg
ALARS_BT_CMD="ros2 run alars alars_bt --ros-args -r __ns:=/$ROBOT_NAME \
-p robot_name:=$ROBOT_NAME \
-p use_sim_time:=$USE_SIM_TIME \
-p loaded_weight_kg:=$LOADED_WEIGHT_KG \
-p max_detection_age:=15.0"

ALARS_BT_STATUS_CMD="ros2 topic echo ${ROBOT_NAME}/alars_bt/status std_msgs/msg/String --field data"

tmux_make_layout "$SESSION" BTs "row(3:var(WASP_BT_CMD), 3:var(ALARS_BT_CMD), 1:var(ALARS_BT_STATUS_CMD))"


############
# 4 Camera and detection
############
YOLO_DEVICE=0
CAM_CALIBRATION_FILE="real_z1_params.yaml"
YOLO_MODEL="yolo_model_2cls_mixed.pt" # Options: alars_labeling_training/trained_models
if [[ $USE_SIM_TIME = "True" ]]; then
    YOLO_DEVICE=cpu
    CAM_CALIBRATION_FILE="cam_params.yaml"
    # seems to be doing better in sim
    YOLO_MODEL="yolo_model_2cls_mixed.pt"
fi
YOLO_CMD="ros2 launch alars_auv_perception alars_yolo_detector.launch.py \
namespace:=$ROBOT_NAME \
device:=$YOLO_DEVICE \
use_sim_time:=$USE_SIM_TIME \
model_package:=alars_labeling_training \
model_file:=$YOLO_MODEL"

PROJECTION_CMD="ros2 launch auv_state_estimation auv_buoy_ekf_launch.py \
namespace:=$ROBOT_NAME \
use_sim_time:=$USE_SIM_TIME \
camera_calibration_file:=$CAM_CALIBRATION_FILE \
auv_ekf_staleness_seconds:=$EKF_STALENESS_SECONDS \
buoy_ekf_staleness_seconds:=10.0
"

tmux_make_layout "$SESSION" CamProc "row(var(YOLO_CMD), var(PROJECTION_CMD))"


############
# 5 AUX Nodes like geofence etc.
############
GEOFENCE_CMD="ros2 run actionable_geofence geofence_node --ros-args -r __ns:=/$ROBOT_NAME \
-p use_sim_time:=$USE_SIM_TIME \
-p map_frame:=$ROBOT_NAME/map"

tmux_make_layout "$SESSION" Aux "row(var(GEOFENCE_CMD))"

############
# 6 Drivers
############
NAU_DRIVER_CMD="ros2 run nau7802_ros2_driver nau7802_ros2_driver --ros-args -r __ns:=/$ROBOT_NAME"
GIMBAL_IP=192.168.1.108
GIMBAL_PORT=2332
GSCAM_CONFIG_GIMBAL="rtspsrc location=rtsp://$GIMBAL_IP latency=0 ! rtph264depay ! h264parse ! nvv4l2decoder ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! queue max-size-buffers=1 leaky=downstream"
GIMBAL_CAM_TOPIC_NS=gimbal_camera
GIMBAL_CAM_VIDEO_CMD="ros2 run gscam gscam_node --ros-args \
    -p gscam_config:=\"$GSCAM_CONFIG_GIMBAL\" \
    -p frame_id:=z1_optical_frame \
    -p image_encoding:=rgb8 \
    -p sync_sink:=false \
    -p camera.image_raw.enable_pub_plugins:="['image_transport/compressed','image_transport/raw']" \
    -r __ns:=/$ROBOT_NAME/$GIMBAL_CAM_TOPIC_NS"
GIMBAL_CAM_DRIVER_CMD="ros2 launch z1_pro_driver z1_pro_driver_launch.py \
    robot_name:=$ROBOT_NAME \
    tf_frame_prefix:=$ROBOT_NAME/ \
    camera_ip:=$GIMBAL_IP \
    camera_port:=$GIMBAL_PORT \
    camera_below_base:=True"
GIMBAL_CMD_ACTION_CMD="ros2 launch z1_pro_driver z1_pro_action_launch.py \
    robot_name:=\"$ROBOT_NAME\" \
    use_sim_time:=$USE_SIM_TIME"

# GSCAM_CONFIG_FISH="v4l2src device=/dev/insta360x4 ! image/jpeg,width=1920,height=1080,framerate=30/1 ! jpegdec ! videoconvert ! video/x-raw,format=BGR"
# FISH_VIDEO_CMD="ros2 run gscam gscam_node --ros-args \
#     -p gscam_config:=\"$GSCAM_CONFIG_FISH\" \
#     -p frame_id:=fisheye_optical_frame \
#     -p image_encoding:=rgb8 \
#     -p sync_sink:=false \
#     -r __ns:=/$ROBOT_NAME/fisheye_camera"

if [[ $USE_SIM_TIME = "False" ]]; then
    tmux_make_layout "$SESSION" Drivers "
    row(
        col(
            var(NAU_DRIVER_CMD),
            var(GIMBAL_CAM_VIDEO_CMD)
        ),
        var(GIMBAL_CAM_DRIVER_CMD),
        var(GIMBAL_CMD_ACTION_CMD)
    )"
else
    tmux_make_layout "$SESSION" Drivers "
    row(
        var(GIMBAL_CMD_ACTION_CMD)
    )"
fi

############
# 7 mqtt bridge, rosboard etc
############
MQTT_ADDR=20.240.40.232
MQTT_PORT=1884
# the mqtt stuff on unity on linux is wonky, so use localhost for that
# a broker will be launched in a tmux pane later.
if [[ "$(uname)" == "Linux" ]]; then
    ON_LINUX=True
else
    ON_LINUX=False
fi
if [[ $ON_LINUX == "True" && $USE_SIM_TIME == "True" ]]; then
    MQTT_ADDR=localhost
    MQTT_PORT=1889
fi
if [[ $USE_SIM_TIME = "True" ]]; then
    REALSIM="simulation"
else
    REALSIM="real"
fi

STR_MQTT_BRIDGE_CMD="ros2 launch str_json_mqtt_bridge waraps_bridge.launch robot_name:=$ROBOT_NAME domain:=air realsim:=$REALSIM broker_addr:=$MQTT_ADDR broker_port:=$MQTT_PORT context:=alars"
ROSBOARD_CMD="ros2 run rosboard rosboard_node --ros-args -r __ns:=/$ROBOT_NAME"
tmux_make_layout "$SESSION" Bridges "row(var(STR_MQTT_BRIDGE_CMD), var(ROSBOARD_CMD))"


############
# 8 sim connection
############
if [[ $USE_SIM_TIME = "True" ]]; then
    ROS_TCP_ENDPOINT_CMD="ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p tcp_ip:=localhost -p tcp_port:=10000"
    if [[ $ON_LINUX = "True" ]]; then
        MOSQUITTO_CMD="mosquitto -p $MQTT_PORT"
        tmux_make_layout "$SESSION" SimConnection "row(var(ROS_TCP_ENDPOINT_CMD), var(MOSQUITTO_CMD))"
    else
        tmux_make_layout "$SESSION" SimConnection "row(var(ROS_TCP_ENDPOINT_CMD))"
    fi
fi


tmux -2 attach-session -t "$SESSION"
tmux set-option -t "$SESSION" mouse on
tmux select-window -t "$SESSION:Captains"
