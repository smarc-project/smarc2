import os

import yaml

from ament_index_python.packages import get_package_share_directory
from dji_msgs.msg import Links as DjiLinks
from dji_msgs.msg import Topics as DjiTopics
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from smarc_msgs.msg import Topics as SmarcTopics


def generate_launch_description() -> LaunchDescription:
    share = get_package_share_directory("landing_controller")
    captain_share = get_package_share_directory("dji_captain")
    default_model = os.path.join(
        captain_share, "models", "M350", "discrete_model", "discrete_models.yaml"
    )
    default_config = os.path.join(share, "config", "landing_params.yaml")
    robot_name = LaunchConfiguration("robot_name")
    model_path = LaunchConfiguration("model_path")
    model_kind = LaunchConfiguration("model_kind")
    model_sample_time = LaunchConfiguration("model_sample_time_s")
    config_file = LaunchConfiguration("config_file")
    command_mirror_topic = LaunchConfiguration("command_mirror_topic")
    pad_class_name = LaunchConfiguration("pad_class_name")
    auto_start = LaunchConfiguration("auto_start")
    enable_descent = LaunchConfiguration("enable_descent")
    require_pad_status = LaunchConfiguration("require_pad_status")
    pad_velocity_filter_tau = LaunchConfiguration("pad_velocity_filter_tau_s")
    pad_status_max_covariance = LaunchConfiguration("pad_status_max_covariance_trace")
    use_sim_time = LaunchConfiguration("use_sim_time")

    map_frame = PythonExpression(["'", robot_name, "/", DjiLinks.MAP, "'"])
    controller_frame = PythonExpression(["'", robot_name, "/", DjiLinks.BASE_FLAT, "'"])
    drone_reference_frame = PythonExpression(
        ["'", robot_name, "/", DjiLinks.LANDING_GEAR_CENTER, "'"])
    def launch_landing_nodes(context):
        # Sections share one YAML root but remain isolated between nodes. Passing
        # the whole wildcard file would apply unrelated same-name parameters.
        path = config_file.perform(context)
        with open(path, encoding="utf-8") as stream:
            document = yaml.safe_load(stream)
        try:
            settings = document["/**"]["ros__parameters"]
        except (KeyError, TypeError) as error:
            raise ValueError(f"{path}: expected /** -> ros__parameters -> node sections") from error
        for name in (
            "landing_pad_odom_adapter", "landing_relative_state", "landing_manager",
            "landing_lqr_controller", "landing_velocity_command_mux",
        ):
            if not isinstance(settings, dict) or not isinstance(settings.get(name), dict):
                raise ValueError(f"{path}: missing or invalid parameter section '{name}'")

        return [
            Node(
                package="landing_controller",
                executable="object_array_to_odometry",
                name="landing_pad_odom_adapter",
                namespace=robot_name,
                output="screen",
                parameters=[
                    settings["landing_pad_odom_adapter"],
                    {
                        "pose_array_topic": DjiTopics.PROJECTED_OBJECT_POSES_ARRAY_TOPIC,
                        "status_array_topic": DjiTopics.OBJECT_EKF_STATUS_ARRAY_TOPIC,
                        "class_name": pad_class_name,
                        "output_topic": DjiTopics.PAD_ODOM_TOPIC,
                        "landing_status_topic": DjiTopics.STATUS_TOPIC,
                        "drone_odom_topic": SmarcTopics.ODOM_TOPIC,
                        "child_frame_id": "land_pad",
                        "require_status": ParameterValue(require_pad_status, value_type=bool),
                        "velocity_filter_tau_s": ParameterValue(pad_velocity_filter_tau, value_type=float),
                        "max_covariance_trace": ParameterValue(pad_status_max_covariance, value_type=float),
                        "use_sim_time": ParameterValue(use_sim_time, value_type=bool),
                    },
                ],
            ),

            Node(
                package="landing_controller",
                executable="relative_state",
                name="landing_relative_state",
                namespace=robot_name,
                output="screen",
                parameters=[
                    settings["landing_relative_state"],
                    {
                        "drone_odom_topic": SmarcTopics.ODOM_TOPIC,
                        "pad_odom_topic": DjiTopics.PAD_ODOM_TOPIC,
                        "output_topic": DjiTopics.RELATIVE_STATE_TOPIC,
                        "map_frame": map_frame,
                        "drone_reference_frame": ParameterValue(
                            LaunchConfiguration("drone_reference_frame"), value_type=str),
                        "drone_twist_frame_mode": "header",
                        "pad_twist_frame_mode": "header",
                        "use_sim_time": ParameterValue(use_sim_time, value_type=bool),
                    },
                ],
            ),

            Node(
                package="landing_controller",
                executable="landing_manager",
                name="landing_manager",
                namespace=robot_name,
                output="screen",
                parameters=[
                    settings["landing_manager"],
                    {
                        "robot_name": robot_name,
                        "relative_state_topic": DjiTopics.RELATIVE_STATE_TOPIC,
                        "reference_topic": DjiTopics.REFERENCE_TOPIC,
                        "status_topic": DjiTopics.STATUS_TOPIC,
                        "controller_frame": controller_frame,
                        "auto_start": ParameterValue(auto_start, value_type=bool),
                        "enable_descent": ParameterValue(enable_descent, value_type=bool),
                        "use_sim_time": ParameterValue(use_sim_time, value_type=bool),
                    },
                ],
            ),

            Node(
                package="landing_controller",
                executable="lqr_controller",
                name="landing_lqr_controller",
                namespace=robot_name,
                output="screen",
                parameters=[
                    settings["landing_lqr_controller"],
                    {
                        "robot_name": robot_name,
                        "model_path": model_path,
                        "model_kind": model_kind,
                        "model_sample_time_s": ParameterValue(model_sample_time, value_type=float),
                        "relative_state_topic": DjiTopics.RELATIVE_STATE_TOPIC,
                        "reference_topic": DjiTopics.REFERENCE_TOPIC,
                        "controller_command_topic": DjiTopics.CONTROLLER_CMD_TOPIC,
                        "debug_topic": DjiTopics.CONTROLLER_DEBUG_TOPIC,
                        "controller_frame": controller_frame,
                        "use_sim_time": ParameterValue(use_sim_time, value_type=bool),
                    },
                ],
            ),

            Node(
                package="landing_controller",
                executable="velocity_command_mux",
                name="landing_velocity_command_mux",
                namespace=robot_name,
                output="screen",
                parameters=[
                    settings["landing_velocity_command_mux"],
                    {
                        "robot_name": robot_name,
                        "controller_command_topic": DjiTopics.CONTROLLER_CMD_TOPIC,
                        "reference_topic": DjiTopics.REFERENCE_TOPIC,
                        "output_topic": DjiTopics.VELOCITY_SETPOINT_TOPIC,
                        "mirror_vector_topic": command_mirror_topic,
                        "controller_frame": controller_frame,
                        "use_sim_time": ParameterValue(use_sim_time, value_type=bool),
                    },
                ],
            ),
        ]

    return LaunchDescription([
        DeclareLaunchArgument("robot_name", default_value="M350", description="Robot namespace"),
        DeclareLaunchArgument("drone_reference_frame", default_value=drone_reference_frame,
                             description="Frame rigidly attached to the odometry child; landing height is clearance from this point to the estimated pad."),
        DeclareLaunchArgument(
            "model_path", default_value=default_model,
            description="Identified YAML/NPZ model; defaults to the M350 discrete model in dji_captain.",
        ),
        DeclareLaunchArgument("model_kind", default_value="auto"),
        DeclareLaunchArgument("model_sample_time_s", default_value="0.0"),
        DeclareLaunchArgument("config_file", default_value=default_config),
        DeclareLaunchArgument("command_mirror_topic", default_value=""),
        DeclareLaunchArgument("pad_class_name", default_value="land_pad"),
        DeclareLaunchArgument("auto_start", default_value="false"),
        DeclareLaunchArgument("enable_descent", default_value="false", description="Remain in ALIGN at fixed height when false."),
        DeclareLaunchArgument("require_pad_status", default_value="true"),
        DeclareLaunchArgument("pad_velocity_filter_tau_s", default_value="0.25"),
        DeclareLaunchArgument("pad_status_max_covariance_trace", default_value="-1.0", description="Optional full-state EKF covariance-trace gate. Negative disables it."),
        DeclareLaunchArgument("use_sim_time", default_value="false", description="Use /clock for Unity or rosbag simulation time."),

        OpaqueFunction(function=launch_landing_nodes),
    ])
