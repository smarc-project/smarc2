from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    robot_name = LaunchConfiguration('robot_name')
    use_sim_time = LaunchConfiguration('use_sim_time')
    log_level = LaunchConfiguration('log_level')

    return LaunchDescription([
        DeclareLaunchArgument(
            'robot_name',
            default_value='sam',
            description='Robot namespace and name used by SAM Captain.',
        ),
        DeclareLaunchArgument(
            'log_level',
            default_value='warn',
            description='Logging level for the SAM Captain node.',
        ),
        Node(
            package='sam_captain',
            executable='sam_captain',
            namespace=robot_name,
            name='sam_captain',
            output='screen',
            parameters=[{
                'robot_name': robot_name,
            }],
            arguments=['--ros-args', '--log-level', log_level],
        )
    ])
