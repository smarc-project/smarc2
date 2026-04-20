#! /bin/bash
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

BT_LOG_MODE=compact # can be 'compact' or 'verbose'

#Dune backseat driver
DUNE_BACKSEAT_DRIVER=False #[True , False]

#Drivers
CAPTAIN_DRIVER=Serial #[Serial MQTT None]
SBG_DRIVER=False
LIDAR_DRIVER=False
CAMERA_DRIVER=False
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
NODE_RED_TRANSLATOR=False
TWIST_VIZ=False


#Simulation
MODE="SIM" #[REAL, SIM, HITL]
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
    NODE_RED_TRANSLATOR=True
    TWIST_VIZ=True

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
    CAMERA_GIMBALL_DRIVER=True
    CAMERA_MQTT_CONTORL=False
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
    NODE_RED_TRANSLATOR=True
    TWIST_VIZ=True

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

# Logging window.
tmux -2 new-session -d -s $SESSION -n 'logging'
tmux select-window -t $SESSION:0
tmux send-keys "Remember to start the logging!" 

#Low level control
tmux new-window -t $SESSION:1 -n 'controllers'
tmux select-window -t $SESSION:1
tmux send-keys "ros2 launch evolo_controllers evolo_controllers_launch.py" C-m

# BT, action servers etc.
tmux new-window -t $SESSION:2 -n 'bt'
tmux select-window -t $SESSION:2
tmux send-keys "ros2 launch wasp_bt wasp_bt.launch robot_name:=$ROBOT_NAME agent_type:=$AGENT_TYPE pulse_rate:=$PULSE_RATE use_sim_time:=$USE_SIM_TIME bt_log_mode:=$BT_LOG_MODE" C-m

# Action servers that are "constantly running"
tmux new-window -t $SESSION:3 -n 'servers'
tmux select-window -t $SESSION:3
tmux select-pane -t $SESSION:3.0
tmux split-window -h -t $SESSION:3.0
tmux split-window -v -t $SESSION:3.0
tmux split-window -v -t $SESSION:3.1
tmux select-layout -t $SESSION:3 tiled

#launch action servers
tmux select-pane -t $SESSION:3.0
tmux send-keys "sleep 4; ros2 run evolo_move_to move_to_server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME" C-m
tmux select-pane -t $SESSION:3.1
#tmux send-keys "sleep 4; ros2 run evolo_move_path move_path_server_dubins_curves --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME" C-m
tmux send-keys "sleep 4; ros2 run evolo_move_path move_path_server_dubins_curves --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME --params-file \$(ros2 pkg prefix evolo_move_path)/share/evolo_move_path/config/evolo_params.yaml" C-m
tmux select-pane -t $SESSION:3.2
tmux send-keys "sleep 4; ros2 run evolo_external_control externalcontrol_server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME" C-m
#tmux select-pane -t $SESSION:3.3
#tmux send-keys "sleep 4; ros2 run lolo_loiter server --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME" C-m

# wara-ps Mqtt bridge.
tmux new-window -t $SESSION:4 -n 'waraps-mqtt'
tmux select-window -t $SESSION:4
tmux send-keys "sleep 7; ros2 launch str_json_mqtt_bridge waraps_bridge.launch broker_addr:=20.240.40.232 broker_port:=1884 robot_name:=$ROBOT_NAME domain:=$AGENT_TYPE realsim:=$REALSIM use_sim_time:=$USE_SIM_TIME context:=$CONTEXT" C-m
#tmux send-keys "sleep 7; ros2 launch str_json_mqtt_bridge waraps_bridge.launch broker_addr:=127.0.0.1 broker_port:=1883 robot_name:=$ROBOT_NAME domain:=$AGENT_TYPE realsim:=$REALSIM use_sim_time:=$USE_SIM_TIME context:=$CONTEXT" C-m

#Health monitoring. TODO make this work.
tmux new-window -t $SESSION:5 -n 'waraps-mqtt'
tmux select-pane -t $SESSION:5.0
tmux send-keys "ros2 topic pub -r 1 /$ROBOT_NAME/smarc/vehicle_health std_msgs/msg/Int8 '{data: 0}' " C-m

#Robot description
tmux new-window -t $SESSION:6 -n 'Robot description'
tmux select-window -t $SESSION:6
tmux send-keys "ros2 launch evolo_description evolo_description.launch" C-m

#Obstacle avoidance
if [ $OBSTACLE_AVOIDANCE=False == "True" ]; then
    tmux new-window -t $SESSION:7 -n 'obstacle avoidance'
    tmux select-window -t $SESSION:7
    #TODO launch CBF here
    tmux send-keys "ros2 run topic_tools relay /evolo/ctrl/twist_planned /evolo/ctrl/twist_setpoint" C-m
else
    tmux new-window -t $SESSION:7 -n 'control repub'
    tmux select-window -t $SESSION:7
    tmux send-keys "ros2 run topic_tools relay /evolo/ctrl/twist_planned /evolo/ctrl/twist_setpoint" C-m
fi

########################################################################
####################### Hardware drivers ###############################
########################################################################

#Connection to evolo captain
if [ $CAPTAIN_DRIVER == "Serial" ]; then
    tmux new-window -t $SESSION:10 -n 'Evolo captain'
    tmux select-window -t $SESSION:10
    tmux send-keys "ros2 launch evolo_serial_bridge evolo_serial_launch.py" C-m
fi

if [ $CAPTAIN_DRIVER == "MQTT" ]; then
    tmux new-window -t $SESSION:10 -n 'Evolo captain'
    tmux select-window -t $SESSION:10
    tmux send-keys "ros2 launch evolo_mqtt_bridge evolo_mqtt_launch.py" C-m
fi
#else None

#SBG driver
if [ $SBG_DRIVER == "True" ]; then
    #SBG driver
    tmux new-window -t $SESSION:11 -n 'SBG driver'
    tmux select-window -t $SESSION:11
    tmux send-keys "ros2 launch evolo_config sbg_launch.py robot_name:=$ROBOT_NAME" C-m
fi

#Lidar driver
if [ $LIDAR_DRIVER == "True" ]; then
    tmux new-window -t $SESSION:12 -n 'lidar driver'
    tmux select-window -t $SESSION:12
    tmux send-keys "ros2 launch evolo_config lidar_launch.py ouster_ns:=$ROBOT_NAME/sensors/lidar" C-m
fi

#Camera driver
if [ $CAMERA_DRIVER == "True" ]; then
    tmux new-window -t $SESSION:13 -n 'camera driver'
    tmux select-window -t $SESSION:13
    #tmux send-keys "ros2 run gscam gscam_node --ros-args -p gscam_config:="uridecodebin uri=rtsp://127.0.0.1:5541/27aec28e-6181-4753-9acd-0456a75f0289/0 source::latency=0 ! nvvidconv ! videoconvert" -p frame_id:=evolo_camera_frame -p image_encoding:=rgb8 -p sync_sink:=false -r __ns:=/evolo/gimbal_camera"
    #tmux send-keys 'ros2 run gscam gscam_node --ros-args -p gscam_config:="uridecodebin uri=rtsp://192.168.2.210 source::latency=0 ! decodebin ! videoconvert" -p frame_id:=evolo_camera_frame -p image_encoding:=rgb8 -p sync_sink:=false -r __ns:=/evolo/sensors/gimbal_camera' C-m
    GSCAM_CONFIG="rtspsrc location=rtsp://192.168.2.210 latency=0 ! rtph264depay ! h264parse ! nvv4l2decoder ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! queue max-size-buffers=1 leaky=downstream"
    tmux send-keys "ros2 run gscam gscam_node --ros-args \
    -p gscam_config:=\"$GSCAM_CONFIG\" \
    -p frame_id:=evolo_camera_frame \
    -p image_encoding:=rgb8 \
    -p sync_sink:=false \
    -p camera.image_raw.enable_pub_plugins:="['image_transport/compressed']" \
    -r __ns:=/$ROBOT_NAME/sensors/gimbal_camera" C-m
fi


#Gimbal driver
if [ $CAMERA_GIMBALL_DRIVER == "True" ]; then
    tmux new-window -t $SESSION:14 -n 'gimbal driver'
    tmux select-window -t $SESSION:14
    tmux send-keys "ros2 launch evolo_config z1_pro_launch.py namespace:=$ROBOT_NAME use_vehicle_altitude:=false" C-m
fi

if [ $CAMERA_MQTT_CONTORL == "True" ]; then
    tmux new-window -t $SESSION:15 -n 'cam cmd'
    tmux select-window -t $SESSION:15
    tmux split-window -h -t $SESSION:15.0
    # Json parser
    tmux select-pane -t $SESSION:15.0
    tmux send-keys "ros2 launch evolo_gimbal_remote_control gimbal_remote_control.launch.py robot_name:=$ROBOT_NAME" C-m
    # Mqtt bridge
    tmux select-pane -t $SESSION:15.1
    tmux send-keys "ros2 launch evolo_gimbal_remote_control mqtt_camcmd_listener.launch.py robot_name:=$ROBOT_NAME" C-m
fi

if [ $SIDESCAN_DRIVER == "True" ]; then
    tmux new-window -t $SESSION:16 -n 'sidescan driver'
    tmux select-window -t $SESSION:16
    tmux send-keys "ros2 run dv_sidescan_g5_interface interfaceG5.py --ros-args -r __ns:=/$ROBOT_NAME -p output_topic:="sensors/sidescan"" C-m
fi

#Simulator "diver"
if [ $SIMULATOR_DRIVER == "True" ]; then
    tmux new-window -t $SESSION:17 -n 'Simulator'
    tmux select-window -t $SESSION:17
    tmux split-window -h -t $SESSION:17.0
    # Siumulator tcp connection
    tmux select-pane -t $SESSION:17.0
    tmux send-keys "ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=127.0.0.1" C-m
    #Simulator control republisher
    tmux select-pane -t $SESSION:17.1
    tmux send-keys "ros2 run topic_tools relay /evolo/ctrl/twist_setpoint /evolo/evolo_cmd" C-m
fi




########################################################################
######################## Location source ###############################
########################################################################

if [ "$LOCATION_SOURCE" = "SBG" ]; then
    #Odom
    tmux new-window -t $SESSION:20 -n 'Localization to Odom'
    tmux select-window -t $SESSION:20
    tmux split-window -h -t $SESSION:20.0

    #Odom initializer
    tmux select-pane -t $SESSION:20.0
    tmux send-keys "ros2 run sbg_to_odom_initializer odom_initializer --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME" C-m

    #sbg to odom node
    tmux select-pane -t $SESSION:20.1
    tmux send-keys "ros2 run sbg_to_odom sbg_nav_to_evolo_odom --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME" C-m
fi

if [ "$LOCATION_SOURCE" = "MQTT" ] || [ "$LOCATION_SOURCE" = "SERIAL" ]; then
    #Odom
    tmux new-window -t $SESSION:20 -n 'Localization to Odom'
    tmux select-window -t $SESSION:20
    tmux split-window -h -t $SESSION:20.0

    #Odom initializer
    tmux select-pane -t $SESSION:20.0
    tmux send-keys "ros2 launch evolo_captain_interface evolo_captain_odom_initializer_launch.py use_sim_time:=$USE_SIM_TIME" C-m

    #sbg to odom node
    tmux select-pane -t $SESSION:20.1
    tmux send-keys "ros2 launch evolo_captain_interface evolo_captain_odom_launch.py use_sim_time:=$USE_SIM_TIME" C-m
fi


########################################################################
################## Perception / processing #############################
########################################################################

# Perception
if [ $LIDAR_PROCESSING == "True" ]; then
    tmux new-window -t $SESSION:30 -n 'Perception'
    tmux select-window -t $SESSION:30
    tmux split-window -h -t $SESSION:30.0

    #Pointcloud preprocessing
    tmux select-pane -t $SESSION:30.0
    tmux send-keys "ros2 launch pointcloud_preprocessing pointcloud_preprocessing_launch_evolo.py use_sim_time:=$USE_SIM_TIME" C-m
    #occupancy grid
    tmux select-pane -t $SESSION:30.1
    #tmux send-keys "ros2 run clustering_segmentation clustering_segmentation --ros-args -p use_sim_time:=$USE_SIM_TIME" C-m
    tmux send-keys "ros2 run clustering_segmentation clustering_segmentation --ros-args -p use_sim_time:=$USE_SIM_TIME -p DynamicStatic_clusters_segmentation:=True" C-m
fi


#TODO launch TwistStamped to path nodes

########################################################################
##################### Visualization / debug ############################
########################################################################

if [ $ROSBOARD == "True" ]; then
    tmux new-window -t $SESSION:40 -n 'visualization'
    tmux select-window -t $SESSION:40
    tmux send-keys "sleep 15; ros2 run rosboard rosboard_node" C-m
fi

if [ $TWIST_VIZ == "True" ]; then

    tmux new-window -t $SESSION:41 -n 'twist_planned'
    tmux select-window -t $SESSION:41
    tmux send-keys "sleep 10; ros2 launch twist_to_path twist_to_path_launch.py subscribe_topic:=/evolo/ctrl/twist_planned publish_topic:=/evolo/ctrl/viz/twist_planned_path integration_time:=15.0 integration_dt:=0.5" C-m

    tmux new-window -t $SESSION:42 -n 'twist_setpoint'
    tmux select-window -t $SESSION:42
    tmux send-keys "sleep 10; ros2 launch twist_to_path twist_to_path_launch.py subscribe_topic:=/evolo/ctrl/twist_setpoint publish_topic:=/evolo/ctrl/viz/twist_setpoint_path integration_time:=15.0 integration_dt:=0.5" C-m
fi

########################################################################
########################## Communiation ################################
########################################################################

#Video stream
if [ $VIDERO_STREAM == "True" ]; then
    tmux new-window -t $SESSION:50 -n 'Streaming'
    tmux select-window -t $SESSION:50
    #tmux send-keys "cd ~/RTSPtoWeb/ ; GO111MODULE=on go run *.go" C-m
    tmux send-keys "bash ~/video_streaming/stream.sh" C-m
fi

#Topic transport
if [ $TOPIC_TRANSPORT == "True" ]; then
    #Message transport
    tmux new-window -t $SESSION:51 -n 'message transport'
    tmux select-window -t $SESSION:51
    tmux send-keys "ros2 launch evolo_config network_bridge_evolo_tcp.launch.py" C-m
fi

#Node-red-translator
if [ $NODE_RED_TRANSLATOR == "True" ]; then
    tmux new-window -t $SESSION:51 -n 'message transport'
    tmux select-window -t $SESSION:51
    tmux send-keys "ros2 launch evolo_config network_bridge_evolo_tcp.launch.py" C-m
fi


########################################################################
############################## Dune ####################################
########################################################################
if [ "$DUNE_BACKSEAT_DRIVER" = "True" ]; then
    tmux new-window -t $SESSION:60 -n 'dune'
    tmux select-window -t $SESSION:60
    tmux send-keys "cd ~/Documents/lsts/dune; ./dune -c evolo -p Hardware" C-m

    tmux new-window -t $SESSION:61 -n 'imc_ros_bridge'
    tmux select-window -t $SESSION:61
    tmux send-keys "sleep 10; ros2 run imc_ros_bridge imc_ros2_bridge.py --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME -p server_ip:=127.0.0.1 -p tcp_port:=7001 -p imc_src:=0x0806" C-m

    tmux new-window -t $SESSION:62 -n 'evolo imc translator'
    tmux select-window -t $SESSION:62
    tmux send-keys "ros2 run evolo_imc_translator evolo_imc_translator.py --ros-args -r __ns:=/$ROBOT_NAME -p use_sim_time:=$USE_SIM_TIME"  C-m
fi


tmux new-window -t $SESSION:99 -n 'zenoh router'p
tmux select-window -t $SESSION:99
tmux send-keys "ros2 run rmw_zenoh_cpp rmw_zenohd" C-m


# Set default window
tmux select-window -t $SESSION:1
tmux -2 attach-session -t $SESSION