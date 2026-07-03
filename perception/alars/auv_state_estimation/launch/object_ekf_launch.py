import os
import yaml

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, LogInfo
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

from dji_msgs.msg import Links, Topics
from smarc_msgs.msg import Topics as SmarcTopics

# Default configuration for known objects. If an object is not listed here, the defaults_for_object function will generate default values based on the object name.
OBJECT_DEFAULTS = {
    "sam": {
        "input_polygon": Topics.ESTIMATED_AUV_OBB_TOPIC,
        "input_head": Topics.ESTIMATED_AUV_HEAD_TOPIC,
        "output_topic": Topics.PROJECTED_AUV_POSE_WITH_COV_TOPIC,
        "output_link": Links.ESTIMATED_AUV,
        "ekf_status": "alars_auv_ekf/status",
        "reset_service": "alars_auv_ekf/reset",
    },
    "buoy": {
        "input_polygon": Topics.ESTIMATED_BUOY_OBB_TOPIC,
        "input_head": "",
        "output_topic": Topics.PROJECTED_BUOY_POSE_WITH_COV_TOPIC,
        "output_link": Links.ESTIMATED_BUOY,
        "ekf_status": "buoy_ekf/status",
        "reset_service": "buoy_ekf/reset",
    },
}

def defaults_for_object(object_name):
    if object_name in OBJECT_DEFAULTS:
        return OBJECT_DEFAULTS[object_name]

    return {
        "input_polygon": f"alars_detection/{object_name}_obb",
        "input_head": "",
        "output_topic": f"alars_projection/{object_name}_pose_with_cov",
        "output_link": f"estimated_{object_name}",
        "ekf_status": f"{object_name}_ekf/status",
        "reset_service": f"{object_name}_ekf/reset",
    }

def as_bool(value):
    return str(value).lower() in ["true", "1", "yes"]


def resolve_config_path(pkg_dir, value):
    if os.path.isabs(value):
        return value

    return os.path.join(pkg_dir, "config", value)


def flatten_params(params, prefix=""):
    flat = {}

    for key, value in params.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            flat.update(flatten_params(value, full_key))
        else:
            flat[full_key] = value

    return flat


def launch_setup(context, *args, **kwargs):
    pkg_dir = get_package_share_directory("auv_state_estimation")

    robot_name = LaunchConfiguration("robot_name").perform(context)
    use_sim_time = as_bool(LaunchConfiguration("use_sim_time").perform(context))

    base_params_file_name = LaunchConfiguration("base_params_file").perform(context)
    object_config_file_name = LaunchConfiguration("object_config_file").perform(context)
    camera_calibration_file_name = LaunchConfiguration(
        "camera_calibration_file"
    ).perform(context)

    yolo_detections_topic = LaunchConfiguration(
        "yolo_detections_topic"
    ).perform(context)

    base_params_file = resolve_config_path(pkg_dir, base_params_file_name)
    object_config_file = resolve_config_path(pkg_dir, object_config_file_name)
    camera_calibration_file = resolve_config_path(
        pkg_dir,
        camera_calibration_file_name,
    )

    with open(object_config_file, "r") as f:
        object_config = yaml.safe_load(f) or {}

    objects = object_config.get("objects", {})

    launch_entities = [
        LogInfo(msg=["[object_ekf_launch] base params file = ", base_params_file]),
        LogInfo(msg=["[object_ekf_launch] object config file = ", object_config_file]),
        LogInfo(msg=["[object_ekf_launch] camera calibration file = ", camera_calibration_file]),
        LogInfo(msg=["[object_ekf_launch] yolo detections topic = ", yolo_detections_topic]),
    ]

    # One shared adapter for all enabled objects.
    launch_entities.append(
        Node(
            package="auv_state_estimation",
            executable="yolo_estimator_adapter",
            namespace=robot_name,
            name="yolo_estimator_adapter",
            output="screen",
            parameters=[
                {
                    "robot_name": robot_name,
                    "use_sim_time": use_sim_time,

                    "object_config_file": object_config_file,
                    "camera_calibration_file": camera_calibration_file,

                    "topics.yolo_detections": yolo_detections_topic,

                    "frames.camera": Links.GIMBAL_OPTICAL_FRAME,

                    "yolo_msg_timeout": 5.0,
                    "default_confidence_threshold": 0.5,
                }
            ],
        )
    )

    for object_name, cfg in objects.items():
        if not cfg.get("enabled", True):
            continue

        defaults = defaults_for_object(object_name)

        object_params = {
            "object_name": object_name,
            "robot_name": robot_name,
            "use_sim_time": use_sim_time,

            "camera_info": camera_calibration_file,

            "topics.input_polygon": cfg.get("input_polygon", defaults["input_polygon"]),
            "topics.input_head": cfg.get("input_head", defaults["input_head"]),
            "topics.output_topic": cfg.get("output_topic", defaults["output_topic"]),
            "topics.ekf_status": cfg.get("ekf_status", defaults["ekf_status"]),
            
            "topics.odom": SmarcTopics.ODOM_TOPIC,
            "frames.map": Links.MAP,
            "frames.camera": Links.GIMBAL_OPTICAL_FRAME,
            
            "frames.output_link": cfg.get("output_link", defaults["output_link"]),

            "obb.length_m": float(cfg["length_m"]),
            "obb.width_m": float(cfg["width_m"]),

            "motion.model_type": cfg.get("motion_model_type", "surface"),
            "stale_state_age": float(cfg.get("stale_state_age", 3.0)),

            "enable_head_disambiguation": bool(
                cfg.get("enable_head_disambiguation", False)
            ),

            "reset_service": cfg.get("reset_service", defaults["reset_service"]),
        }   

        extra_params = cfg.get("parameters", {})
        if extra_params:
            object_params.update(flatten_params(extra_params))

        launch_entities.append(
            LogInfo(
                msg=[
                    "[object_ekf_launch] launching ",
                    object_name,
                    " EKF | input polygon: ",
                    object_params["topics.input_polygon"],
                    " | output pose: ",
                    object_params["topics.output_topic"],
                    " | frame: ",
                    object_params["frames.output_link"],
                ]
            )
        )

        launch_entities.append(
            Node(
                package="auv_state_estimation",
                executable="ekf_node",
                namespace=robot_name,
                name=f"{object_name}_ekf_node",
                output="screen",
                parameters=[
                    base_params_file,
                    object_params,
                ],
            )
        )

    return launch_entities


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "robot_name",
                default_value="M350",
            ),
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="false",
            ),
            DeclareLaunchArgument(
                "camera_calibration_file",
                default_value="cam_params.yaml",
            ),
            DeclareLaunchArgument(
                "base_params_file",
                default_value="ekf_params.yaml",
            ),
            DeclareLaunchArgument(
                "object_config_file",
                default_value="object_estimation.yaml",
            ),
            DeclareLaunchArgument(
                "yolo_detections_topic",
                default_value="yolo/detections",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )