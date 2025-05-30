import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch_ros.actions import Node, SetParameter, PushRosNamespace
from launch_ros.substitutions import FindPackagePrefix, FindPackageShare
from launch.substitutions import TextSubstitution, PathJoinSubstitution
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import ThisLaunchFileDir
from launch.actions import ExecuteProcess
import xacro
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    return LaunchDescription([
        
        # Qualisys driver
        GroupAction([
            PushRosNamespace('mocap'),
            IncludeLaunchDescription(
            PathJoinSubstitution([FindPackageShare('mocap_qualisys'), 'launch', 'qualisys.launch.py']),
            launch_arguments={
                'server_address': '192.168.32.32'}.items()
            ),
        ]),   

        # RVIZ2 + robot models come in this launch file
        # TODO: modify to add more than one Bluerov with different names
        IncludeLaunchDescription(
        PathJoinSubstitution([FindPackageShare('watertank_utils'), 'launch', 'tank_visualization.launch.py']),
        launch_arguments={
            'sam_package': 'sam_description',
            'sam_package_path': PathJoinSubstitution(['robots', 'sam_auv_default.urdf.xacro']),
            'brov_name': 'bluerov_saab',
            'brov_package': 'brov2heavy_description',
            'brov_package_path': PathJoinSubstitution(['robots', 'brov2heavy_default.urdf.xacro']),
            'tank_package': 'watertank_description',
            'tank_package_path': PathJoinSubstitution(['robots', 'watertank_default.urdf.xacro']),
            'hula_package': 'hula_description',
            'hula_package_path': PathJoinSubstitution(['robots', 'hula_default.urdf.xacro'])
            }.items()
        ),

        # Utils here
        Node(
            package='watertank_utils',
            executable='watertank_tf_utils',
            name='watertank_tf_utils_node',
            # parameters=[],
            output='screen',
            arguments=['--ros-args', '--log-level', 'info']),

        Node(
            package='watertank_utils',
            executable='mocap_odom_sam',
            name='mocap_odom_sam',
            # parameters=[],
            output='screen',
            arguments=['--ros-args', '--log-level', 'info'])

    ])
    
generate_launch_description()
