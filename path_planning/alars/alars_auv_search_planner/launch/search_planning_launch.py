from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch.conditions import IfCondition
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from dji_msgs.msg import Links as DJILinks

# Main parameters: change them manually or via CLI
MODE = "as"  # sim, srv, as
PLANNER = "spiral"  # spiral, greedy, astar, apf
NAMESPACE = "/Quadrotor"

def generate_launch_description():

    # ---- frequently changed params as launch arguments ...
    namespace_arg = DeclareLaunchArgument('namespace', default_value=NAMESPACE)
    mode_arg = DeclareLaunchArgument('mode', default_value=MODE)
    path_planner_arg = DeclareLaunchArgument('path_planner', default_value=PLANNER)
    sam_init_pos_arg = DeclareLaunchArgument('sam_init_pos', default_value='[1300.0, 1153.0]')
    drone_init_pos_arg = DeclareLaunchArgument('drone_init_pos', default_value='[5.0, -5.0]')

    # ... and as node params
    namespace = LaunchConfiguration('namespace')
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

    # ---- node if mode == "as"

    as_node = Node(
        package='alars',
        executable="alars_search_action_server",
        namespace='M350',
        output='screen',
        parameters=[
            config_file,
            {
                'namespace': namespace,
                'mode': mode,
                'path_planner': path_planner,
                'sam.init_pos': sam_init_pos,
                'drone.init_pos': drone_init_pos,
            }
        ],
        condition=IfCondition(PythonExpression([mode, " == 'as'"]))
    )

    # ---- node if mode != "as" 
    default_node = Node(
        package='alars_auv_search_planner',
        executable="search_planner_controller",
        namespace='M350',
        output='screen',
        parameters=[
            config_file,
            {
                'namespace': namespace,
                'mode': mode,
                'path_planner': path_planner,
                'sam.init_pos': sam_init_pos,
                'drone.init_pos': drone_init_pos,
            }
        ],
        condition=IfCondition(PythonExpression([mode, " != 'as'"]))
    )

    return LaunchDescription([
        namespace_arg,
        mode_arg,
        path_planner_arg,
        sam_init_pos_arg,
        drone_init_pos_arg,

        # Debug logging
        LogInfo(msg=["[Launch] mode argument = ", mode]),
        LogInfo(msg=["[Launch] namespace argument = ", namespace]),

        as_node,
        default_node,
    ])
