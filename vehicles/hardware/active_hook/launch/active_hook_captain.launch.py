from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='False',
        description='Use the simulation (Unity) clock instead of the wall clock'
    )

    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        namespace='ActiveHook',
        output='screen',
        parameters=[{
            'deadzone': 0.08,
            'autorepeat_rate': 20.0,
            'use_sim_time': use_sim_time,
        }]
    )

    captain_node = Node(
        package='active_hook',
        executable='active_hook_captain',
        name='active_hook_captain',
        namespace='ActiveHook',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
        }]
    )

    return LaunchDescription([
        use_sim_time_arg,
        joy_node,
        captain_node
    ])