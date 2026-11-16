import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    
    default_config = os.path.join(
        get_package_share_directory('pad_landing_controller'), 'config', 'landing_params.yaml')
    robot_name = LaunchConfiguration('robot_name')
    use_sim_time = LaunchConfiguration('use_sim_time')
    config_file = LaunchConfiguration('config_file')
    max_drone_age_s = LaunchConfiguration('max_drone_age_s')
    max_pad_age_s = LaunchConfiguration('max_pad_age_s')
    max_prediction_s = LaunchConfiguration('max_prediction_s')
    
    return LaunchDescription([
        DeclareLaunchArgument('robot_name', default_value='M350', description='Robot namespace'),
        DeclareLaunchArgument('use_sim_time', default_value='false',
                              description='Use /clock for Unity or rosbag playback'),
        DeclareLaunchArgument('config_file', default_value=default_config),
        DeclareLaunchArgument('max_drone_age_s', default_value='0.8',
                              description='Maximum drone odometry age [s]'),
        DeclareLaunchArgument('max_pad_age_s', default_value='1.5',
                              description='Maximum landing-pad observation age [s]'),
        DeclareLaunchArgument('max_prediction_s', default_value='10.0',
                              description='Maximum prediction duration from the last real pad observation [s]'),
        
        Node(
            package='pad_landing_controller', executable='pad_landing_as',
            name='pad_landing_action_server', namespace=robot_name, output='screen',
            parameters=[
                config_file,
                {
                    'robot_name': robot_name,
                    'use_sim_time': ParameterValue(use_sim_time, value_type=bool),
                    'landing_relative_state.max_drone_age_s': ParameterValue(
                        max_drone_age_s, value_type=float),
                    'landing_relative_state.max_pad_age_s': ParameterValue(
                        max_pad_age_s, value_type=float),
                    'pad_odometry.max_prediction_s': ParameterValue(
                        max_prediction_s, value_type=float),
                },
            ]),
    ])
