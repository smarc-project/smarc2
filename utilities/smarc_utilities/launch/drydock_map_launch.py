import xacro
import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution

from launch_ros.descriptions import ParameterValue

from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    
    actions = []

    # Static transform for the dry dock visualization
    actions.append(
            Node(
                package="tf2_ros",
                executable="static_transform_publisher",
                name="static_tf_map_to_base",
                arguments=[
                    "--x", "335026.125",
                    "--y", "6579293.513",
                    "--z", "-15.854",
                    "--qx", "-0.0325686263",
                    "--qy", "0.0760763836",
                    "--qz", "0.8060420712",
                    "--qw", "-0.5860442372",
                    "--frame-id", "map",           # parent frame
                    "--child-frame-id", "beckholmen_map",  # child frame
                ],
                output="screen",)
    )
    
    # This has the mesh visualization for the dry dock map.
    # The above transform will place the mesh in the correct location in the map frame. 
    # The mesh is published as a marker on the /mesh_marker topic.

    # NOTE: The mesh resource path in beckholmen_vis.py needs to be updated to point to the correct location of the mesh file on your system. 
    # The current path is set to 'file:///root/dufomap_data/models/obj_scaled_no_boat/12_09_2025.obj'.
    # Also possible to use a package resource path like 'package://package_name/meshes/your_mesh.obj' if you place the mesh in the package.
    actions.append(
        Node(
            package="smarc_utilities",
            executable="beckholmen_vis",
            name="beckholmen_vis",
            output="screen",
        )
    )

    return LaunchDescription(actions)
