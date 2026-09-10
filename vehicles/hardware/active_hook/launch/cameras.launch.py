from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    robot_name = LaunchConfiguration('robot_name')

    return LaunchDescription([
        DeclareLaunchArgument('robot_name', default_value='ActiveHook'),

        Node(
            package='active_hook',
            executable='camera_node',
            name='cam1_camera_node',
            namespace=[robot_name, '/cam1'],
            parameters=[{
                'port': 5601,
                'frame_id': 'cam1_optical_frame',
                'topic': 'image_raw',
            }],
        ),
        Node(
            package='active_hook',
            executable='camera_node',
            name='cam2_camera_node',
            namespace=[robot_name, '/cam2'],
            parameters=[{
                'port': 5602,
                'frame_id': 'cam2_optical_frame',
                'topic': 'image_raw',
            }],
        ),
    ])
