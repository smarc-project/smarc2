from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

    # ---- frequently changed params as launch arguments ...
    mode_arg = DeclareLaunchArgument('mode', default_value='real')
    path_planner_arg = DeclareLaunchArgument('path_planner', default_value='spiral')
    sam_init_pos_arg = DeclareLaunchArgument('sam_init_pos', default_value='[1297.0, 1153.0]')
    drone_init_pos_arg = DeclareLaunchArgument('drone_init_pos', default_value='[5.0, 5.0]')

    # ... and as node params
    mode = LaunchConfiguration('mode')
    path_planner = LaunchConfiguration('path_planner')
    sam_init_pos = LaunchConfiguration('sam_init_pos')
    drone_init_pos = LaunchConfiguration('drone_init_pos')

    # ---- rarely changed params from yaml (yaml has every parameter but launch arguments will override)
    config_file = PathJoinSubstitution([
        FindPackageShare('alars_auv_search_planner'),
        'config',
        'params.yaml'

    ])

    planner_node = Node(
        package='alars_auv_search_planner',
        executable='search_planner_controller',
        namespace='Quadrotor',
        output='screen',
        parameters=[
            config_file,
            {
                'mode': mode,
                'path_planner': path_planner,
                'sam.init_pos': sam_init_pos,
                'drone.init_pos': drone_init_pos,
            }
        ]
    )

    return LaunchDescription([
        mode_arg,
        path_planner_arg,
        sam_init_pos_arg,
        drone_init_pos_arg,
        planner_node,
    ])
