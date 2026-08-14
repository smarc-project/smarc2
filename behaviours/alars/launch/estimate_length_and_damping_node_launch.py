from launch                import LaunchDescription
from launch.actions        import DeclareLaunchArgument
from launch.substitutions  import LaunchConfiguration
from launch_ros.actions    import Node


def generate_launch_description():
    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='M350',
        description='Namespace for the robot'
    )
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='False',
        description='Use simulation clock instead of wall clock'
    )

    robot_name = LaunchConfiguration('robot_name')
    use_sim_time = LaunchConfiguration('use_sim_time')

    node = Node(
        package='alars',
        executable='alars_estimate_length_and_damping_action_server',
        name='estimate_length_and_damping_node',
        namespace=robot_name,
        output='screen',
        parameters=[{
            'robot_name': robot_name,
            'use_sim_time': use_sim_time,
        }]
    )

    return LaunchDescription([
        robot_name_arg,
        use_sim_time_arg,
        node
    ])
