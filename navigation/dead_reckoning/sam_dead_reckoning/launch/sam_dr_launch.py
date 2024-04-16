import os
import launch
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

# TODO xml version of launch file

def generate_launch_description():
    namespace = "sam0"
    # These topics are specific to sam dr
    depth_topic = f"{namespace}/dr/depth"
    odom_topic = f"/{namespace}/dr/odom"
    gps_odom_topic = f"/{namespace}/dr/gps_odom"

    print("Launching sam_dr_launch.py")

    return launch.LaunchDescription([
        # TODO include the latlon to utm service ??
        Node(
            package="sam_dead_reckoning",
            executable="depth_node",
            namespace=namespace,
            name="depth_node",
            output="screen",
            parameters=[{
                "odom_frame":  f"{namespace}/odom",
                "base_frame": f"{namespace}/base_link",
                "pressure_frame": f"{namespace}/pressure_link",
                "pressure_topic": f"/{namespace}/core/depth20_pressure",
                "depth_topic": depth_topic,
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
                "gps_odom_topic": gps_odom_topic,
                "map_frame": "map",
                "utm_frame": "utm",
                "gps_frame": f"{namespace}/gps_link"
            }]
        ),
        Node(
            package="sam_dead_reckoning",
            executable="dr_node",
            namespace=namespace,
            name="dr_node",
            output="screen",
            parameters=[{
                "gps_odom_topic": gps_odom_topic,
                "depth_topic": depth_topic,
                "odom_topic": odom_topic,
                "base_frame": f"{namespace}_base_link",
                "base_frame_2d": f"{namespace}_base_link_2d",
                "odom_frame": "odom",  # changed
                "map_frame": "map",
                "utm_frame": "utm",
                "dvl_frame": f"{namespace}_dvl_link",
                "pressure_frame": f"{namespace}_pressure_link",
                "dvl_period": 0.1,
                "dr_period": 0.02,
                "simulation": True
            }]
        )
    ])



