import os

from ament_index_python.packages import get_package_share_directory
from dji_msgs.msg import Links as DjiLinks
from dji_msgs.msg import Topics as DjiTopics
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
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
    pad_class_name = LaunchConfiguration("pad_class_name")
    enable_descent = LaunchConfiguration("enable_descent")
    require_pad_status = LaunchConfiguration("require_pad_status")
    pad_velocity_filter_tau = LaunchConfiguration("pad_velocity_filter_tau_s")
    pad_status_max_covariance = LaunchConfiguration("pad_status_max_covariance_trace")
    use_sim_time = LaunchConfiguration("use_sim_time")

    map_frame = PythonExpression(["'", robot_name, "/", DjiLinks.MAP, "'"])
    controller_frame = PythonExpression(["'", robot_name, "/", DjiLinks.BASE_FLAT, "'"])
    drone_reference_frame = PythonExpression(
        ["'", robot_name, "/", DjiLinks.LANDING_GEAR_CENTER, "'"])

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
        DeclareLaunchArgument("pad_class_name", default_value="land_pad"),
        DeclareLaunchArgument("enable_descent", default_value="false", description="Remain in ALIGN at fixed height when false."),
        DeclareLaunchArgument("require_pad_status", default_value="true"),
        DeclareLaunchArgument("pad_velocity_filter_tau_s", default_value="0.25"),
        DeclareLaunchArgument("pad_status_max_covariance_trace", default_value="-1.0", description="Optional full-state EKF covariance-trace gate. Negative disables it."),
        DeclareLaunchArgument("use_sim_time", default_value="false", description="Use /clock for Unity or rosbag simulation time."),

        Node(
            package="landing_controller",
            executable="object_array_to_odometry",
            name="landing_pad_odom_adapter",
            namespace=robot_name,
            output="screen",
            parameters=[
                config_file,
                {
                    "landing_pad_odom_adapter.pose_array_topic": DjiTopics.PROJECTED_OBJECT_POSES_ARRAY_TOPIC,
                    "landing_pad_odom_adapter.status_array_topic": DjiTopics.OBJECT_EKF_STATUS_ARRAY_TOPIC,
                    "landing_pad_odom_adapter.class_name": pad_class_name,
                    "landing_pad_odom_adapter.output_topic": DjiTopics.PAD_ODOM_TOPIC,
                    "landing_pad_odom_adapter.landing_status_topic": DjiTopics.STATUS_TOPIC,
                    "landing_pad_odom_adapter.drone_odom_topic": SmarcTopics.ODOM_TOPIC,
                    "landing_pad_odom_adapter.child_frame_id": "land_pad",
                    "landing_pad_odom_adapter.require_status": ParameterValue(require_pad_status, value_type=bool),
                    "landing_pad_odom_adapter.velocity_filter_tau_s": ParameterValue(pad_velocity_filter_tau, value_type=float),
                    "landing_pad_odom_adapter.max_covariance_trace": ParameterValue(pad_status_max_covariance, value_type=float),
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
                config_file,
                {
                    "landing_relative_state.drone_odom_topic": SmarcTopics.ODOM_TOPIC,
                    "landing_relative_state.pad_odom_topic": DjiTopics.PAD_ODOM_TOPIC,
                    "landing_relative_state.output_topic": DjiTopics.RELATIVE_STATE_TOPIC,
                    "landing_relative_state.map_frame": map_frame,
                    "landing_relative_state.drone_reference_frame": ParameterValue(
                        LaunchConfiguration("drone_reference_frame"), value_type=str),
                    "landing_relative_state.drone_twist_frame_mode": "header",
                    "landing_relative_state.pad_twist_frame_mode": "header",
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
                config_file,
                {
                    "robot_name": robot_name,
                    "landing_manager.relative_state_topic": DjiTopics.RELATIVE_STATE_TOPIC,
                    "landing_manager.status_topic": DjiTopics.STATUS_TOPIC,
                    "landing_lqr_controller.controller_frame": controller_frame,
                    "landing_manager.output_topic": DjiTopics.VELOCITY_SETPOINT_TOPIC,
                    "landing_lqr_controller.model_path": model_path,
                    "landing_lqr_controller.model_kind": model_kind,
                    "landing_lqr_controller.model_sample_time_s": ParameterValue(model_sample_time, value_type=float),
                    "landing_lqr_controller.debug_topic": DjiTopics.CONTROLLER_DEBUG_TOPIC,
                    "landing_manager.enable_descent": ParameterValue(enable_descent, value_type=bool),
                    "use_sim_time": ParameterValue(use_sim_time, value_type=bool),
                },
            ],
        ),
    ])
