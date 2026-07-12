#!/usr/bin/env python3
"""
Launch file for Floatsam SMaRC Topics Publisher
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace
from ament_index_python.packages import get_package_share_directory
import os 
from launch.substitutions import PythonExpression, PathJoinSubstitution

def generate_launch_description():
    # Declare launch arguments
    use_sim_arg = DeclareLaunchArgument(
        'use_sim',
        default_value='True',
        description='Use simulator topics (true) or real hardware topics (false)'
    )
    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='floatsam_usv',
        description='Name of the robot for namespacing'
    )
    thruster_limit_arg = DeclareLaunchArgument(
        'thruster_limit',
        default_value='1000.0',
        description='Thruster limit in RPM used to normalize actuator commands'
    )
    master_floatsam_arg = DeclareLaunchArgument(
        'master_floatsam',
        default_value='floatsam_usv_0',
        description='Name of the floatsam whose rtk position will be set as the /map frame center'
    )
    num_of_robots_arg = DeclareLaunchArgument(
        'num_of_robots',
        default_value='1',
        description='Number of robots in the fleet'
    )

    config_dir = os.path.join(get_package_share_directory('floatsam_topic_bridge'), 'config')

    config_file_name = PythonExpression([
        "'sim_topics.yaml' if '", LaunchConfiguration('use_sim'), "'.lower() == 'true' else 'real_topics.yaml'"
    ])
    config_file = PathJoinSubstitution([config_dir, config_file_name])

    smarc_topics_publisher_node = Node(
        package='floatsam_topic_bridge',
        executable='smarc_topics_publisher',
        name='floatsam_smarc_topics_publisher',
        output='screen',
        parameters=[
            config_file,
                {
                    'use_sim': LaunchConfiguration('use_sim'),
                    'robot_name': LaunchConfiguration('robot_name'),
                    'thruster_limit': LaunchConfiguration('thruster_limit'),
                    'master_floatsam': LaunchConfiguration('master_floatsam'),
                    'num_of_robots': LaunchConfiguration('num_of_robots'),
        }],
        arguments=['--ros-args', '--log-level', 'info']
    )

    return LaunchDescription([
        use_sim_arg,
        robot_name_arg,
        thruster_limit_arg,
        master_floatsam_arg,
        num_of_robots_arg,
        GroupAction([
            PushRosNamespace(LaunchConfiguration('robot_name')),
            smarc_topics_publisher_node,
        ])
    ])