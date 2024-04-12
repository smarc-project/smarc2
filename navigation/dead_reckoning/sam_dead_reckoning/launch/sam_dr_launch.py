import os
import launch
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node


def generate_launch_description():
    # Example: using a yaml file for parameters
    # param_config = os.path.join(
    #     get_package_share_directory('sam_graph_slam_2'),
    #     'config',
    #     'pipeline_config.yaml'
    # )

    # TODO this is not the correct way to set the name
    # I think we should talk about how launch files should be set up
    robot_name = "sam0"
    odom_topic = f"/{robot_name}/dr/odom"
    gps_odom_topic = f"/{robot_name}/dr/gps_odom"

    print("Launching sam_dr_launch.py")

    return launch.LaunchDescription([
        # Example: ExecuteProcess
        # ExecuteProcess(
        #     cmd=['ros2', 'bag', 'play', '/home/julian/bag_files/pipeline_sim'],
        #     output='screen'
        # ),
        # TODO include the latlon to utm service
        Node(
            package="sam_dead_reckoning",
            executable="depth_node",
            name="depth_node",
            output="screen",
            parameters=[{
                "odom_frame":  f"{robot_name}/odom",
                "base_frame": f"{robot_name}/base_link",
                "pressure_frame": f"{robot_name}/pressure_link",
                "pressure_topic": f"/{robot_name}/core/depth20_pressure",
                "depth_topic": f"/{robot_name}/dr/depth",
                "simulation": True

            }]
        ),
        Node(
            package="sam_dead_reckoning",
            executable="gps_node",
            name="gps_node",
            respawn=True,
            output="screen",
            parameters=[{
                "gps_topic": f"/{robot_name}/core/gps",
                "gps_odom_topic": gps_odom_topic,
                "map_frame": "map",
                "utm_frame": "utm",
                "gps_frame": f"{robot_name}/gps_link"
            }]
        )


    ])



