#!/usr/bin/env python3
"""
Launch file for Floatsam SMaRC Topics Publisher
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python.packages import get_package_prefix


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
    
    # Get the install directory and construct the path to the executable in bin/
    install_dir = get_package_prefix('floatsam_topic_bridge')
    executable_path = os.path.join(install_dir, 'bin', 'smarc_topics_publisher')
    
    # Run the node using ExecuteProcess to bypass package structure validation
    smarc_topics_publisher_node = ExecuteProcess(
        cmd=[
            executable_path,
            '--ros-args',
            '-p', ['use_sim:=', LaunchConfiguration('use_sim')],
            '-p', ['robot_name:=', LaunchConfiguration('robot_name')],
            '-p', ['thruster_limit:=', LaunchConfiguration('thruster_limit')],
            '-p', ['master_floatsam:=', LaunchConfiguration('master_floatsam')],
            '--log-level', 'info'
        ],
        output='screen',
        name='floatsam_smarc_topics_publisher'
    )
    
    return LaunchDescription([
        use_sim_arg,
        robot_name_arg,
        thruster_limit_arg,
        master_floatsam_arg,
        smarc_topics_publisher_node,
    ])
