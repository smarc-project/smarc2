import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

from dji_msgs.msg import Links, Topics
from smarc_msgs.msg import Topics as SmarcTopics


def generate_launch_description():
    robot_name = LaunchConfiguration("robot_name")

    use_sim_time = ParameterValue(LaunchConfiguration("use_sim_time"), value_type=bool)

    visualization_enable = ParameterValue(LaunchConfiguration("visualization_enable"), value_type=bool)

    config_dir = LaunchConfiguration("config_dir")

    base_params_file = PathJoinSubstitution([config_dir, LaunchConfiguration("base_params_file")])

    object_config_file = PathJoinSubstitution([config_dir, LaunchConfiguration("object_config_file")])

    camera_calibration_file = PathJoinSubstitution([config_dir, LaunchConfiguration("camera_calibration_file")])

    yolo_detections_corners_topic = LaunchConfiguration("yolo_detections_corners_topic")

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
                "visualization_enable",
                default_value="true",
            ),
            DeclareLaunchArgument(
                "config_dir",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("auv_state_estimation"),
                        "config",
                    ]
                ),
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
                "camera_calibration_file",
                default_value="cam_params.yaml",
            ),
            DeclareLaunchArgument(
                "yolo_detections_corners_topic",
                default_value="yolo/detections_with_corners",
            ),

            LogInfo(msg=["[multi_ekf_launch] base params file = ", base_params_file]),
            LogInfo(msg=["[multi_ekf_launch] object config file = ", object_config_file]),
            LogInfo(msg=["[multi_ekf_launch] camera calibration file = ", camera_calibration_file]),

            Node(
                package="auv_state_estimation",
                executable="multi_object_ekf_node",
                namespace=robot_name,
                name="multi_object_ekf_node",
                output="screen",
                parameters=[
                    {
                        "robot_name": robot_name,
                        "use_sim_time": use_sim_time,

                        "base_params_file": base_params_file,
                        "object_config_file": object_config_file,
                        "camera_info": camera_calibration_file,

                        "topics.input_detections_corners": yolo_detections_corners_topic,
                        "topics.odom": SmarcTopics.ODOM_TOPIC,

                        "topics.output_poses_array": Topics.PROJECTED_OBJECT_POSES_ARRAY_TOPIC,
                        "topics.status_array": Topics.OBJECT_EKF_STATUS_ARRAY_TOPIC,

                        "visualization_enable": visualization_enable,
                        "topics.markers": Topics.OBJECT_EKF_MARKERS_TOPIC,

                        "services.reset": Topics.OBJECT_EKF_RESET_SERVICE,

                        "frames.map": Links.MAP,
                        "frames.camera": Links.GIMBAL_OPTICAL_FRAME,
                    }
                ],
            ),
        ]
    )