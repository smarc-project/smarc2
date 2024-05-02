import os
import launch
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, SetLaunchConfiguration
from launch.substitutions import LaunchConfiguration

# TODO xml version of launch file

def generate_launch_description():
    namespace = "sam0"

    print("Launching sam_dr_launch.py")

    return launch.LaunchDescription([

        # Declare the use_sim_time argument
        # DeclareLaunchArgument(
        #     'use_sim_time', default_value='true',
        #     description='Use simulation (Gazebo) clock if true'),
        #
        # # Set the use_sim_time configuration
        # SetLaunchConfiguration(
        #     'use_sim_time', value=LaunchConfiguration('use_sim_time')),

        # TODO include the latlon to utm service ??
        Node(
            package="sam_dead_reckoning",
            executable="depth_node",
            namespace=namespace,
            name="depth_node",
            output="screen",
            parameters=[{
                "use_sim_time": True,
                "robot_name": namespace,
                "simulation": True

            }]
        ),
        Node(
            package="sam_dead_reckoning",
            executable="gps_node",
            namespace=namespace,
            name="gps_node",
            respawn=True,
            output="screen",
            parameters=[{
                "use_sim_time": True,
                "robot_name": namespace,
                "map_frame": "map",
                "utm_frame": "utm"
            }]
        ),
        Node(
            package="sam_dead_reckoning",
            executable="dr_node",
            namespace=namespace,
            name="dr_node",
            output="screen",
            parameters=[{
                "use_sim_time": True,
                "robot_name": namespace,
                "odom_frame": "odom",  # changed
                "map_frame": "map",
                "utm_frame": "utm",
                "dvl_period": 0.1,
                "dr_period": 0.02,
                "simulation": True
            }]
        ),
        Node(
            package="sam_dead_reckoning",
            executable="rpy_node",
            namespace=namespace,
            name="rpy_node",
            output="screen",
            parameters=[{
                "use_sim_time": True,
            }]
        )

    ])



