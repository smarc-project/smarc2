#! /bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/tmux_layout.sh"

ROBOT_NAME=ActiveHook

MODE=$1
CAMERA=$2

if [[ -z "$MODE" ]]; then
    echo "You must pass the mode as the first argument! Pass one of: real or sim"
    echo "real: also launches mavros and the cameras against the actual vehicle."
    echo "sim: skips mavros and the cameras, you connect the ros-unity bridge yourself."
    echo "Exiting."
    exit 1
fi

if [[ "$MODE" != "real" && "$MODE" != "sim" ]]; then
    echo "Invalid mode: $MODE"
    echo "Please pass either real or sim as the first argument."
    echo "Exiting."
    exit 1
fi

if [[ "$MODE" == "sim" ]]; then
    USE_SIM_TIME=True
else
    USE_SIM_TIME=False
fi

# Camera selection only makes sense in real mode: in sim, video comes
# through the ros-unity bridge, not over UDP from a physical camera.
if [[ "$MODE" == "real" ]]; then
    if [[ -z "$CAMERA" ]]; then
        echo "You must pass the camera selection as the second argument in real mode!"
        echo "Pass one of: front, bottom, both, none."
        echo "Exiting."
        exit 1
    fi

    if [[ "$CAMERA" != "front" && "$CAMERA" != "bottom" && "$CAMERA" != "both" && "$CAMERA" != "none" ]]; then
        echo "Invalid camera option: $CAMERA"
        echo "Please pass one of: front, bottom, both, none as the second argument."
        echo "Exiting."
        exit 1
    fi
fi

YOLO_TEST=False
for arg in "$@"; do
    if [[ "$arg" == "yolo" ]]; then
        echo "Standalone detection test mode enabled: YOLO (sam only) will be launched."
        YOLO_TEST=True
        break
    fi
done

SESSION=${ROBOT_NAME}_bringup

# check if there is already a tmux session with this name
if tmux has-session -t $SESSION 2>/dev/null; then
    echo "There is already a tmux session named $SESSION."
    echo "Please close it before launching this script."
    echo "Exiting."
    exit 1
fi

# create a tmux session with a name
tmux -2 new-session -d -x 220 -y 60 -s "$SESSION"



############
# 1 Captain
############
CAPTAIN_CMD="ros2 launch active_hook active_hook_captain.launch.py use_sim_time:=$USE_SIM_TIME"
MANUAL_CONTROL_ECHO_CMD="ros2 topic echo /$ROBOT_NAME/mavros/manual_control/send mavros_msgs/msg/ManualControl"
STATE_ECHO_CMD="ros2 topic echo /$ROBOT_NAME/mavros/state mavros_msgs/msg/State"

if [[ "$MODE" == "real" ]]; then
    MAVROS_CMD="ros2 run mavros mavros_node --ros-args -r __ns:=/$ROBOT_NAME \
    -p fcu_url:=udp://0.0.0.0:14551@ \
    -p system_id:=255 \
    -p component_id:=191 \
    -p target_system_id:=1 \
    -p target_component_id:=1"

    tmux_make_layout "$SESSION" Captain "
    col(
        row(
            var(CAPTAIN_CMD),
            var(MAVROS_CMD)
        ),
        row(
            var(MANUAL_CONTROL_ECHO_CMD),
            var(STATE_ECHO_CMD)
        )
    )"
else
    tmux_make_layout "$SESSION" Captain "
    col(
        var(CAPTAIN_CMD),
        row(
            var(MANUAL_CONTROL_ECHO_CMD),
            var(STATE_ECHO_CMD)
        )
    )"
fi

############
# 2 Drivers 
############
if [[ "$MODE" == "real" ]]; then

    FRONT_CAM_PORT=5602
    BOTTOM_CAM_PORT=5601


    GSCAM_CONFIG_FRONT="udpsrc port=$FRONT_CAM_PORT ! application/x-rtp,payload=96 ! \
    rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! \
    video/x-raw,format=RGB ! queue max-size-buffers=1 leaky=downstream"

    GSCAM_CONFIG_BOTTOM="udpsrc port=$BOTTOM_CAM_PORT ! application/x-rtp,payload=96 ! \
    rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! \
    video/x-raw,format=RGB ! queue max-size-buffers=1 leaky=downstream"

    FRONT_CAM_CMD="ros2 run gscam gscam_node --ros-args \
        -p gscam_config:=\"$GSCAM_CONFIG_FRONT\" \
        -p frame_id:=front_camera_optical_frame \
        -p image_encoding:=rgb8 \
        -p sync_sink:=false \
        -p camera_name:=front_camera \
        -p camera_info_url:=\"file://$HOME/.ros/camera_info/front_camera.yaml\" \
        -p camera.image_raw.enable_pub_plugins:="['image_transport/raw']" \
        -r __ns:=/$ROBOT_NAME/front_camera"

    BOTTOM_CAM_CMD="ros2 run gscam gscam_node --ros-args \
        -p gscam_config:=\"$GSCAM_CONFIG_BOTTOM\" \
        -p frame_id:=bottom_camera_optical_frame \
        -p image_encoding:=rgb8 \
        -p sync_sink:=false \
        -p camera_name:=bottom_camera \
        -p camera_info_url:=\"file://$HOME/.ros/camera_info/bottom_camera.yaml\" \
        -p camera.image_raw.enable_pub_plugins:="['image_transport/raw']" \
        -r __ns:=/$ROBOT_NAME/bottom_camera"

    case "$CAMERA" in
        front)
            FRONT_PANE_CMD="$FRONT_CAM_CMD"
            BOTTOM_PANE_CMD="echo 'Bottom camera disabled (camera=$CAMERA)'"
            ;;
        bottom)
            FRONT_PANE_CMD="echo 'Front camera disabled (camera=$CAMERA)'"
            BOTTOM_PANE_CMD="$BOTTOM_CAM_CMD"
            ;;
        both)
            FRONT_PANE_CMD="$FRONT_CAM_CMD"
            BOTTOM_PANE_CMD="$BOTTOM_CAM_CMD"
            ;;
        none)
            FRONT_PANE_CMD="echo 'Cameras disabled (camera=none)'"
            BOTTOM_PANE_CMD="echo 'Cameras disabled (camera=none)'"
            ;;
    esac

    tmux_make_layout "$SESSION" Drivers "
    row(
        var(FRONT_PANE_CMD),
        var(BOTTOM_PANE_CMD)
    )"
fi

############
# 3 Camera & Detection
############

if [[ "$YOLO_TEST" == "True" ]]; then
    YOLO_MODEL="yolo_model_4cls_august.pt"
    OBJECT_CONFIG_FILE="object_estimation.yaml"
    MARKERS_VISUALIZATION_ENABLE=True

    YOLO_DEVICE="cuda:0"
    YOLO_THRESHOLD=0.5
    YOLO_ENABLE=True

    YOLO_MODEL="yolo_model_4cls_august.pt" # Options: alars_labeling_training/trained_models
    OBJECT_CONFIG_FILE="object_estimation.yaml" # Config file to edit each object's parameters for the EKF 
    MARKERS_VISUALIZATION_ENABLE=True # Only used for debugging, since we cannot visualize new custom array for the poses in RViz
    if [[ $USE_SIM_TIME = "True" ]]; then
        YOLO_DEVICE="cpu"
    fi

    CAMERA_IMAGE_TOPIC="/$ROBOT_NAME/front_camera/camera/image_raw"

    YOLO_CMD="ros2 launch yolo_bringup yolocustom.launch.py \
    input_image_topic:=$CAMERA_IMAGE_TOPIC \
    robot_name:=$ROBOT_NAME \
    model_package:=alars_labeling_training \
    model_subdir:=trained_models \
    model_file:=$YOLO_MODEL \
    device:=$YOLO_DEVICE \
    threshold:=$YOLO_THRESHOLD \
    enable:=$YOLO_ENABLE
    "

else
    YOLO_CMD="echo 'yolo flag not given, skipping standalone detection test'"
    PROJECTION_CMD="echo 'yolo flag not given, skipping projection node'"
fi

tmux_make_layout "$SESSION" CamProc "
row(
    var(YOLO_CMD),
    var(PROJECTION_CMD)
)"

############


tmux -2 attach-session -t "$SESSION"
tmux set-option -t "$SESSION" mouse on
tmux select-window -t "$SESSION:Captain"