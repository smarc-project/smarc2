from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace


def generate_launch_description():
    """
    Launch the go_to_formation behavior tree action server.

    Each floatsam USV is brought up with floatsam_bringup.sh <id>, giving names
    floatsam_usv_0, floatsam_usv_1, ... floatsam_usv_(num_robots-1).
    Pass robot_name as the full name of the robot running this algorithm (e.g. floatsam_usv_0).
    The server derives the base name (floatsam_usv) from it to enumerate the whole fleet.
    """

    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='floatsam_usv_0',
        description='Full name of the robot running this algorithm (e.g. floatsam_usv_0)'
    )

    num_robots_arg = DeclareLaunchArgument(
        'num_robots',
        default_value='3',
        description='Total number of floatsam USVs in the fleet (IDs will be 0 .. num_robots-1)'
    )

    last_point_tolerance_move_path_arg = DeclareLaunchArgument(
        'last_point_tolerance_move_path',
        default_value='0.5',
        description='Tolerance to consider the last point of the path reached (in meters)'
    )
    
    use_sim_arg = DeclareLaunchArgument(
        'use_sim',
        default_value='true',
        description='Set to true when running in Unity simulator'
    )

    max_velocity_arg = DeclareLaunchArgument(
        'max_velocity',
        default_value='2.0',
        description='Maximum speed [m/s] used by the furthest robot; others scale to arrive at the same time'
    )

    robot_name = LaunchConfiguration('robot_name')
    num_robots = LaunchConfiguration('num_robots')
    last_point_tolerance_move_path = LaunchConfiguration('last_point_tolerance_move_path')
    use_sim = LaunchConfiguration('use_sim')
    max_velocity = LaunchConfiguration('max_velocity')

    node = GroupAction([
        PushRosNamespace(robot_name),
        Node(
            package='floatsam_go_to_formation_rvo',
            executable='floatsam_go_to_formation_rvo_action_server',
            name='floatsam_go_to_formation_rvo_action_server',
            parameters=[{
                'robot_name': robot_name,
                'num_robots': num_robots,
                'last_point_tolerance_move_path': last_point_tolerance_move_path,
                'max_velocity': max_velocity,
                'use_sim': use_sim
            }],
            output='screen'
        )
    ])

    return LaunchDescription([
        robot_name_arg,
        num_robots_arg,
        last_point_tolerance_move_path_arg,
        use_sim_arg,
        max_velocity_arg,
        node
    ])