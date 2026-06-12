#! /bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/tmux_layout.sh"

ROBOT_NAME=evolo
SESSION=${ROBOT_NAME}_bringup

# check if there is already a tmux session with this name
if tmux has-session -t $SESSION 2>/dev/null; then
    echo "There is already a tmux session named $SESSION."
    echo "Please close it before launching this script."
    echo "Exiting."
    exit 1
fi

# New variables for wasp_bt.launch and wasp_mqtt_agent.launch
AGENT_TYPE=surface
PULSE_RATE=0.5 # Hz
CONTEXT=evolo # change this to 'smarc' or something else, then connect to the same context using sim to avoid clutter
# Only pass agent_uuid to launch when set; ros2 launch rejects an empty 'agent_uuid:=' value
if [[ "$(whoami)" == *"evolo"* ]]; then
    AGENT_UUID="7bc11ad5-a2fd-4326-b9d1-6a7b2a68c51d"
    AGENT_UUID_ARG="agent_uuid:=$AGENT_UUID"
elif [[ "$(whoami)" == *"smarc"* ]]; then
    AGENT_UUID="0cc7a470-619b-4ce9-b5f0-0325ed2ba0d3"
    AGENT_UUID_ARG="agent_uuid:=$AGENT_UUID"
else
    AGENT_UUID_ARG=""
fi

BT_LOG_MODE=compact # can be 'compact' or 'verbose'

#Dune backseat driver
DUNE_BACKSEAT_DRIVER=False #[True , False]

#Drivers
CAPTAIN_DRIVER=Serial #[Serial MQTT None]
SBG_DRIVER=False
LIDAR_DRIVER=False
CAMERA_DRIVER=False
YOLO_DRIVER=False
CAMERA_GIMBALL_DRIVER=False
CAMERA_MQTT_CONTORL=False
CAMERA_STREAM=FAlse
SIDESCAN_DRIVER=False
SIMULATOR_DRIVER=False

#Processing
LOCATION_SOURCE=SIM #[SBG MQTT SERIAL SIM]
LIDAR_PROCESSING=False
CAMERA_PROCESSING=False
OBSTACLE_AVOIDANCE=False

#Communication
VIDERO_STREAM=False
TOPIC_TRANSPORT=False
ROSBOARD=False
JSON_TRANSLATOR=False
TWIST_VIZ=False
UW_COM=False

# ---- EXPERIMENTAL ----
PROX_OPS=False

if [[ "$(whoami)" == *"evolo"* ]]; then
    MODE="REAL" #[REAL, SIM, HITL]
else
    MODE="SIM"
fi

#MODE="REAL" #[REAL, SIM, HITL]
if [ "$MODE" == "SIM" ]; then
    REALSIM=simulation
    ROBOT_NAME=evolo
    USE_SIM_TIME=True

    #Drivers
    CAPTAIN_DRIVER=None #[Serial MQTT None]
    SBG_DRIVER=False
    LIDAR_DRIVER=False
    CAMERA_DRIVER=False
    CAMERA_GIMBALL_DRIVER=False
    CAMERA_MQTT_CONTORL=False
    CAMERA_STREAM=FAlse
    SIDESCAN_DRIVER=False
    SIMULATOR_DRIVER=True

    #Processing
    LOCATION_SOURCE=SIM #[SBG MQTT SERIAL SIM]
    LIDAR_PROCESSING=True
    CAMERA_PROCESSING=False
    OBSTACLE_AVOIDANCE=True

    #Communication
    VIDERO_STREAM=False
    TOPIC_TRANSPORT=False
    ROSBOARD=False
    JSON_TRANSLATOR=False
    TWIST_VIZ=True
    UW_COM=False
fi

if [ "$MODE" == "REAL" ]; then
    REALSIM=real
    #USE_SIM_TIME=False
    USE_SIM_TIME=False #Useful for rosbags
    LOCATION_SOURCE=SBG #[SBG MQTT SERIAL]
    CAPTAIN_COM=SERIAL #[SERIAL MQTT]

    #Drivers
    CAPTAIN_DRIVER=Serial #[Serial MQTT None]
    SBG_DRIVER=True
    LIDAR_DRIVER=True
    CAMERA_DRIVER=True
    YOLO_DRIVER=True
    CAMERA_GIMBALL_DRIVER=True
    CAMERA_MQTT_CONTORL=True
    CAMERA_STREAM=True
    SIDESCAN_DRIVER=True
    SIMULATOR_DRIVER=False

    #Processing
    LOCATION_SOURCE=SBG #[SBG MQTT SERIAL SIM]
    LIDAR_PROCESSING=True
    CAMERA_PROCESSING=False
    OBSTACLE_AVOIDANCE=True

    #Communication
    VIDERO_STREAM=True
    TOPIC_TRANSPORT=True
    ROSBOARD=True
    JSON_TRANSLATOR=True
    TWIST_VIZ=True
    UW_COM=True

fi

if [ "$MODE" == "HITL" ]; then
    REALSIM=simulation
    USE_SIM_TIME=true
    LOCATION_SOURCE=SIM #[SBG MQTT SERIAL]
    CAPTAIN_COM=SERIAL #[SERIAL MQTT]
fi


########################################################################
################## Nodes that will always run ##########################
########################################################################

# create a tmux session with a name
tmux -2 new-session -d -x 220 -y 60 -s "$SESSION"

#Logging
tmux select-window -t $SESSION:0
tmux send-keys "Remember to start the logging!" 

# Controllers
CONTROLLER_CMD="ros2 launch evolo_controllers evolo_controllers_launch.py closed_loop_p_gain:=0.5 closed_loop_i_gain:=0.0 closed_loop_d_gain:=0.0 max_steering_output:=40.0"
tmux_make_layout "$SESSION" Controllers "
col(
    var(CONTROLLER_CMD)
)"


# BT
SMARC_BT_CMD="ros2 launch wasp_bt wasp_bt.launch robot_name:=$ROBOT_NAME agent_type:=$AGENT_TYPE pulse_rate:=$PULSE_RATE use_sim_time:=$USE_SIM_TIME bt_log_mode:=$BT_LOG_MODE $AGENT_UUID_ARG"
tmux_make_layout "$SESSION" wasp-bt "
col(
    var(SMARC_BT_CMD)
)"


# Evolo action servers
MOVE_TO_ACTION_CMD="sleep 4; ros2 run evolo_move_to move_to_server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"
MOVE_PATH_ACTION_CMD="sleep 4; ros2 run evolo_move_path move_path_server_dubins_curves --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME --params-file \$(ros2 pkg prefix evolo_move_path)/share/evolo_move_path/config/evolo_params.yaml"
EXTERNAL_CTRL_ACTION_CMD="sleep 4; ros2 run evolo_external_control externalcontrol_server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"
EMERGENCY_ACTION_CMD="ros2 run evolo_emergency_action server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"
DEPLOY_ACTION_CMD="ros2 run evolo_deploy evolo_deploy_server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"
DEPLOY_AT_ACTION_CMD="ros2 run evolo_deploy_at evolo_deploy_at_server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"
tmux_make_layout "$SESSION" Actions "
col(
    row(
        var(MOVE_TO_ACTION_CMD),
        var(MOVE_PATH_ACTION_CMD),
        var(DEPLOY_ACTION_CMD)
    ),
    row(
        var(EXTERNAL_CTRL_ACTION_CMD),
        var(EMERGENCY_ACTION_CMD),
        var(DEPLOY_AT_ACTION_CMD)
    )
)"

# SMaRC Basic actions
GEOFENCE_CMD="ros2 run smarc_basic geofence_node --ros-args -r __ns:=/$ROBOT_NAME \
-p use_sim_time:=$USE_SIM_TIME \
-p map_frame:=$ROBOT_NAME/odom"

HUMAN_LOG_CMD="ros2 run smarc_basic log_action --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"
WAIT_CMD="ros2 run smarc_basic wait_action --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"

tmux_make_layout "$SESSION" BasicActions "
row(
    col(var(GEOFENCE_CMD), var(HUMAN_LOG_CMD)),
    col(var(WAIT_CMD))
)"

# Health monitoring
HEALTH_MONITORING_CMD="ros2 topic pub -r 1 /$ROBOT_NAME/smarc/vehicle_health std_msgs/msg/Int8 '{data: 0}' "
tmux_make_layout "$SESSION" Health-monitoring "
col(
    var(HEALTH_MONITORING_CMD)
)"

# WARA-PS bridge
WARA_PS_MQTT_CMD="sleep 7; ros2 launch str_json_mqtt_bridge waraps_bridge.launch broker_addr:=20.240.40.232 broker_port:=1884 robot_name:=$ROBOT_NAME domain:=$AGENT_TYPE realsim:=$REALSIM use_sim_time:=$USE_SIM_TIME context:=$CONTEXT"
#Evolo/ puffin broker
EVOLO_WARA_PS_MQTT_CMD="sleep 7; ros2 launch evolo_private waraps_bridge.launch robot_name:=$ROBOT_NAME domain:=$AGENT_TYPE realsim:=$REALSIM use_sim_time:=$USE_SIM_TIME context:=$CONTEXT"

tmux_make_layout "$SESSION" waraps-mqtt "
col(
    var(WARA_PS_MQTT_CMD),
    var(EVOLO_WARA_PS_MQTT_CMD)
)"


#Robot description
ROBOT_DESCRIPTION_CMD="ros2 launch evolo_description evolo_description.launch"
tmux_make_layout "$SESSION" Robot-description "
col(
    var(ROBOT_DESCRIPTION_CMD)
)"

#Obstacle avoidance
if [ $OBSTACLE_AVOIDANCE == "True" ]; then
    OBSTACLE_AVOIDANCE_CMD="ros2 launch evolo_obstacle_avoidance evolo_obstacle_avoidance_launch.py"
    CLUSTERING_CMD="ros2 launch evolo_map_cluster evolo_map_cluster_launch.py"
    tmux_make_layout "$SESSION" Obstacle-avoidance "
    col(
        var(OBSTACLE_AVOIDANCE_CMD),
        var(CLUSTERING_CMD)
    )"
else
    OBSTACLE_AVOIDANCE_CMD="ros2 run topic_tools relay /evolo/ctrl/twist_planned /evolo/ctrl/twist_setpoint"
    tmux_make_layout "$SESSION" Obstacle-avoidance "
    col(
        var(OBSTACLE_AVOIDANCE_CMD)
    )"
fi

########################################################################
####################### Hardware drivers ###############################
########################################################################

#Connection to evolo captain
if [ $CAPTAIN_DRIVER == "Serial" ]; then
    CAPTAIN_DRIVER_CMD="ros2 launch evolo_serial_bridge evolo_serial_launch.py"
    tmux_make_layout "$SESSION" Evolo-captain "
    col(
        var(CAPTAIN_DRIVER_CMD)
    )"
fi

if [ $CAPTAIN_DRIVER == "MQTT" ]; then
    CAPTAIN_DRIVER_CMD="ros2 launch evolo_mqtt_bridge evolo_mqtt_launch.py"
    tmux_make_layout "$SESSION" Evolo-captain "
    col(
        var(CAPTAIN_DRIVER_CMD)
    )"
fi
#else None

#SBG driver
if [ $SBG_DRIVER == "True" ]; then
    SBG_DRIVER_CMD="ros2 launch evolo_config sbg_launch.py robot_name:=$ROBOT_NAME"
    tmux_make_layout "$SESSION" SBG-driver "
    col(
        var(SBG_DRIVER_CMD)
    )"
fi

#Lidar driver
if [ $LIDAR_DRIVER == "True" ]; then
    LIDAR_DRIVER_CMD="ros2 launch evolo_config lidar_launch.py ouster_ns:=$ROBOT_NAME/sensors/lidar"
    tmux_make_layout "$SESSION" lidar-driver "
    col(
        var(LIDAR_DRIVER_CMD)
    )"
fi

if [ $SIDESCAN_DRIVER == "True" ]; then

    SIDESCAN_DRIVER_CMD="ros2 run dv_sidescan_g5_interface interfaceG5.py --ros-args -r __ns:=/$ROBOT_NAME -p output_topic:="sensors/sidescan""
    tmux_make_layout "$SESSION" sidescan-driver "
    col(
        var(SIDESCAN_DRIVER_CMD)
    )"
fi

#Camera driver
if [ $CAMERA_DRIVER == "True" ]; then
    GSCAM_CONFIG="rtspsrc location=rtsp://192.168.2.210 latency=0 ! rtph264depay ! h264parse ! nvv4l2decoder ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! queue max-size-buffers=1 leaky=downstream"
    CAMERA_DRIVER_CMD="ros2 run gscam gscam_node --ros-args \
        -p gscam_config:=\"$GSCAM_CONFIG\" \
        -p frame_id:=evolo_camera_frame \
        -p image_encoding:=rgb8 \
        -p sync_sink:=false \
        -p use_sensor_data_qos:=true \
        -p camera.image_raw.enable_pub_plugins:=\"['image_transport/raw']\" \
        -r __ns:=/$ROBOT_NAME/sensors/gimbal_camera_DONT_SUBSCRIBE"
    TOPIC_1_RELAY_CMD="ros2 run topic_tools relay /evolo/sensors/gimbal_camera_DONT_SUBSCRIBE/camera/image_raw /evolo/sensors/gimbal_camera/camera/image_raw"
    tmux_make_layout "$SESSION" camera-driver "
    col(
        var(CAMERA_DRIVER_CMD),
        var(TOPIC_1_RELAY_CMD)
    )"
fi

#Yolo
if [ $YOLO_DRIVER == "True" ]; then
    YOLO_PYTHONPATH="/home/evolo/yolov-env/lib/python3.10/site-packages:/home/evolo/yolov-env/local/lib/python3.10/dist-packages:/home/evolo/yolov-env/lib/python3/dist-packages:/home/evolo/yolov-env/lib/python3.10/dist-packages"
    YOLO_CMD="export PYTHONPATH=$YOLO_PYTHONPATH:\$PYTHONPATH && \
        ros2 launch yolo_bringup yolo.launch.py \
        model_type:=YOLOE \
        model:=/home/evolo/yolo/yoloe-26s-seg.pt \
        input_image_topic:=/$ROBOT_NAME/sensors/gimbal_camera/camera/image_raw \
        image_reliability:=2 \
        device:=cuda:0 \
        use_tracking:=True \
        use_debug:=True"
    YOLO_ACTION_CMD="ros2 launch yolo_smarc_actions smarc_yolo_action_launch.py robot_name:=evolo"
    tmux_make_layout "$SESSION" YOLO "
    col(
        var(YOLO_CMD),
        var(YOLO_ACTION_CMD)
    )"
fi

#Gimbal driver
if [ $CAMERA_GIMBALL_DRIVER == "True" ]; then
    GIMBAL_CAM_DRIVER_CMD="ros2 launch z1_pro_driver z1_pro_driver_launch.py \
        robot_name:=$ROBOT_NAME \
        tf_frame_prefix:=$ROBOT_NAME/ \
        camera_ip:=192.168.2.210 \
        camera_port:=2332 \
        camera_below_base:=False"
    GIMBAL_CAM_ACTION_CMD="ros2 launch z1_pro_driver z1_pro_action_launch.py \
        robot_name:=\"$ROBOT_NAME\" \
        use_sim_time:=$USE_SIM_TIME"
    GIMBAL_CAM_ACTION_CLIENT_CMD="ros2 launch evolo_gimbal_remote_control gimbal_remote_control.launch.py robot_name:=evolo"
    GIMBAL_JSON_FEEDBACK_CMD="ros2 run evolo_gimbal_remote_control gimbal_json_publisher.py"

    if [ $CAMERA_MQTT_CONTORL == "True" ]; then
        tmux_make_layout "$SESSION" Gimbal-driver "
        col(
            row(
                var(GIMBAL_CAM_DRIVER_CMD),
                var(GIMBAL_CAM_ACTION_CMD)
            ),
            row(
                var(GIMBAL_CAM_ACTION_CLIENT_CMD),
                var(GIMBAL_JSON_FEEDBACK_CMD)
            )
        )" 
    else
        tmux_make_layout "$SESSION" Gimbal-driver "
        col(
            var(GIMBAL_CAM_DRIVER_CMD),
            var(GIMBAL_CAM_ACTION_CMD)
        )"
    fi
fi

#Simulator "diver"
if [ $SIMULATOR_DRIVER == "True" ]; then
    UNITY_BRIDGE_CMD="ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=127.0.0.1"
    UNITY_TOPIC_RELAY_CMD="ros2 run topic_tools relay /evolo/ctrl/twist_setpoint /evolo/evolo_cmd"

    tmux_make_layout "$SESSION" Simulator "
    col(
        var(UNITY_BRIDGE_CMD),
        var(UNITY_TOPIC_RELAY_CMD)
    )"
fi

#Uw com
if [ $UW_COM == "True" ]; then
    SERIAL_PARSER_CMD="ros2 run serial_parser serial_parser --ros-args   -p port:=\"/dev/ttyUSB0\"   -p baudrate:=9600   -p listen_to_topic:=\"/evolo/sensors/succor/to\"   -p publish_to_topic:=\"/evolo/sensors/succor/from\""
    UWCOM_SCHEDULER="ros2 run evolo_accoustic_com succor_command_scheduler"
    tmux_make_layout "$SESSION" succorfish "
    col(
        var(SERIAL_PARSER_CMD),
        var(UWCOM_SCHEDULER)
    )"
fi
    
########################################################################
######################## Location source ###############################
########################################################################

#SBG
if [ "$LOCATION_SOURCE" = "SBG" ]; then
    ODOM_INIT_CMD="ros2 run sbg_to_odom_initializer odom_initializer --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"
    SBG_TO_ODOM_CMD="ros2 run sbg_to_odom sbg_nav_to_evolo_odom --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"
    tmux_make_layout "$SESSION" SBG-localization "
    col(
        var(ODOM_INIT_CMD),
        var(SBG_TO_ODOM_CMD)
    )"
fi


# Captain over serial or mqtt
if [ "$LOCATION_SOURCE" = "MQTT" ] || [ "$LOCATION_SOURCE" = "SERIAL" ]; then
    ODOM_INIT_CMD="ros2 launch evolo_captain_interface evolo_captain_odom_initializer_launch.py use_sim_time:=$USE_SIM_TIME"
    CAPTAIN_TO_ODOM_CMD="ros2 launch evolo_captain_interface evolo_captain_odom_launch.py use_sim_time:=$USE_SIM_TIME"
    tmux_make_layout "$SESSION" SBG-localization "
    col(
        var(ODOM_INIT_CMD),
        var(CAPTAIN_TO_ODOM_CMD)
    )"

fi

########################################################################
################## Perception / processing #############################
########################################################################

# Perception
if [ $LIDAR_PROCESSING == "True" ]; then
    POINTCLOUD_PEPROCESSING_CMD="ros2 launch pointcloud_preprocessing pointcloud_preprocessing_launch_evolo.py use_sim_time:=$USE_SIM_TIME"
    POINTCLOUD_CLUSTERING_CMD="ros2 run clustering_segmentation clustering_segmentation --ros-args -p use_sim_time:=$USE_SIM_TIME -p DynamicStatic_clusters_segmentation:=True"
    tmux_make_layout "$SESSION" SBG-localization "
    col(
        var(POINTCLOUD_PEPROCESSING_CMD),
        var(POINTCLOUD_CLUSTERING_CMD)
    )"
fi


########################################################################
##################### Visualization / debug ############################
########################################################################

if [ $ROSBOARD == "True" ]; then
    ROSBOARD_CMD="ros2 run rosboard rosboard_node"
    tmux_make_layout "$SESSION" rosboard "
    col(
        var(ROSBOARD_CMD),
    )"
fi

if [ $TWIST_VIZ == "True" ]; then
    TWIST_TO_PATH_PLANNED_CMD="sleep 10; ros2 launch twist_to_path twist_to_path_launch.py subscribe_topic:=/evolo/ctrl/twist_planned publish_topic:=/evolo/rviz/twist_planned_path integration_time:=15.0 integration_dt:=0.5"
    TWIST_TO_PATH_SETPOINT_CMD="sleep 10; ros2 launch twist_to_path twist_to_path_launch.py subscribe_topic:=/evolo/ctrl/twist_setpoint publish_topic:=/evolo/rviz/twist_setpoint_path integration_time:=15.0 integration_dt:=0.5"
    tmux_make_layout "$SESSION" twist-visualization "
    col(
        var(TWIST_TO_PATH_PLANNED_CMD),
        var(TWIST_TO_PATH_SETPOINT_CMD)
    )"
fi

########################################################################
########################## Communiation ################################
########################################################################

#Video stream
if [ $VIDERO_STREAM == "True" ]; then
    MIRAYA_STREAM_CMD="bash ~/video_streaming/stream.sh"
    RED5_STREAM_CMD="placeholder"
    tmux_make_layout "$SESSION" video_stream "
    col(
        var(MIRAYA_STREAM_CMD),
        var(RED5_STREAM_CMD)
    )"
fi

#Topic transport
if [ $TOPIC_TRANSPORT == "True" ]; then
    TOPIC_TRANSPORT_CMD="ros2 launch evolo_config network_bridge_evolo_tcp.launch.py"
    tmux_make_layout "$SESSION" topic-transport "
    col(
        var(TOPIC_TRANSPORT_CMD),
    )"
fi

#Node-red-translator
if [ $JSON_TRANSLATOR == "True" ]; then
    JSON_TRANSLATOR_CMD="ros2 launch evolo_json_bridge json_bridge_launch.py"
    tmux_make_layout "$SESSION" json_translator"
    col(
        var(JSON_TRANSLATOR_CMD),
    )"
fi


########################################################################
############################## Dune ####################################
########################################################################
if [ "$DUNE_BACKSEAT_DRIVER" = "True" ]; then
    DUNE_CMD="cd ~/Documents/lsts/dune; ./dune -c evolo -p Hardware"
    IMC_ROS_BRIDGE_CMD="sleep 10; ros2 run imc_ros_bridge imc_ros2_bridge.py --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME -p server_ip:=127.0.0.1 -p tcp_port:=7001 -p imc_src:=0x0806"
    IMC_TRANSLATOR_CMD="ros2 run evolo_imc_translator evolo_imc_translator.py --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"

    tmux_make_layout "$SESSION" DUNE "
    col(
        4:var(DUNE_CMD),
        1:var(IMC_ROS_BRIDGE_CMD),
        1:var(IMC_TRANSLATOR_CMD),
    )"
fi

########################################################################
########################## EXPERIMENTAL ################################
########################################################################
if [ "$PROX_OPS" = "True" ]; then
    # Prox-ops action servers.
    LOITER_PATROL_ACTION_CMD="sleep 4; ros2 run prox_ops_actions evolo_loiter_patrol --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"
    TARGET_INTERCEPT_ACTION_CMD="sleep 4; ros2 run prox_ops_actions evolo_target_intercept --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"
    TARGET_INSPECT_ACTION_CMD="sleep 4; ros2 run prox_ops_actions evolo_target_inspect --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"
    PROX_OPS_BT_ACTION_CMD="sleep 10; ros2 run prox_ops_bt prox_ops_bt --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"
    tmux_make_layout "$SESSION" Prox_ops_actions "
    col(
        row(
            var(PROX_OPS_BT_ACTION_CMD),
            var(TARGET_INTERCEPT_ACTION_CMD)
        ),
        row(
            var(LOITER_PATROL_ACTION_CMD),
            var(TARGET_INSPECT_ACTION_CMD),
        )
    )"
fi

ZENOH_CMD="ros2 run rmw_zenoh_cpp rmw_zenohd"

tmux_make_layout "$SESSION" zenoh "
col(
    var(ZENOH_CMD)
)"



# Set default window
tmux select-window -t $SESSION:1
tmux -2 attach-session -t $SESSION
