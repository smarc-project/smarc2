#!/usr/bin/env python3
"""Launch FloatSam health checker."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python.packages import get_package_prefix


def generate_launch_description():
    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='floatsam_usv',
        description='Name of the robot for namespacing',
    )

    check_rate_hz_arg = DeclareLaunchArgument(
        'check_rate_hz',
        default_value='1.0',
        description='Health status publication rate (Hz)',
    )

    stale_timeout_sec_arg = DeclareLaunchArgument(
        'stale_timeout_sec',
        default_value='5.0',
        description='Max age for required topics before ERROR',
    )

    ready_battery_percent_arg = DeclareLaunchArgument(
        'ready_battery_percent',
        default_value='25.0',
        description='Battery threshold (%) required to report READY',
    )

    error_battery_percent_arg = DeclareLaunchArgument(
        'error_battery_percent',
        default_value='15.0',
        description='Battery threshold (%) below which ERROR is reported while propelling',
    )

    thruster_active_rpm_arg = DeclareLaunchArgument(
        'thruster_active_rpm',
        default_value='100.0',
        description='Thruster RPM magnitude above which vehicle is considered propelling',
    )

    install_dir = get_package_prefix('floatsam_topic_bridge')
    executable_path = os.path.join(install_dir, 'bin', 'floatsam_health_checker')

    health_checker_node = ExecuteProcess(
        cmd=[
            executable_path,
            '--ros-args',
            '-p', ['robot_name:=', LaunchConfiguration('robot_name')],
            '-p', ['check_rate_hz:=', LaunchConfiguration('check_rate_hz')],
            '-p', ['stale_timeout_sec:=', LaunchConfiguration('stale_timeout_sec')],
            '-p', ['ready_battery_percent:=', LaunchConfiguration('ready_battery_percent')],
            '-p', ['error_battery_percent:=', LaunchConfiguration('error_battery_percent')],
            '-p', ['thruster_active_rpm:=', LaunchConfiguration('thruster_active_rpm')],
            '--log-level', 'info',
        ],
        output='screen',
        name='floatsam_health_checker',
    )

    return LaunchDescription([
        robot_name_arg,
        check_rate_hz_arg,
        stale_timeout_sec_arg,
        ready_battery_percent_arg,
        error_battery_percent_arg,
        thruster_active_rpm_arg,
        health_checker_node,
    ])
