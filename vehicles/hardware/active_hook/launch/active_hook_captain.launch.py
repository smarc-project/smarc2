import os

from launch import LaunchDescription
from launch_ros.actions import Node, ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    package_share = get_package_share_directory('active_hook')

    config_file = os.path.join(package_share, 'config', 'ps5_rov.yaml')

    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        namespace='ActiveHook',
        output='screen',
        parameters=[{'deadzone': 0.08, 'autorepeat_rate': 20.0}]
    )

    captain_node = Node(
        package='active_hook',
        executable='active_hook_captain',
        name='active_hook_captain',
        namespace='ActiveHook',
        output='screen'
    )

    teleop_node = Node(
        package='teleop_twist_joy',
        executable='teleop_node',
        name='teleop_twist_joy_node',
        namespace='ActiveHook',
        output='screen',
        parameters=[config_file],
        remappings=[
            ('joy', 'joy_rov'),
            ('cmd_vel', 'rov/autonomy/cmd_vel')
        ]
    )

    mavros_container = ComposableNodeContainer(
        name='mavros_container',
        namespace='ActiveHook',
        package='rclcpp_components',
        executable='component_container_mt',
        composable_node_descriptions=[
            ComposableNode(
                package='mavros',
                plugin='mavros::router::Router',
                name='router',
                namespace='ActiveHook',
                parameters=[{
                    'fcu_urls': ['udp://0.0.0.0:14551@'],
                    'uas_urls': ['/uas1'],
                }],
            ),
            ComposableNode(
                package='mavros',
                plugin='mavros::uas::UAS',
                name='uas',
                namespace='ActiveHook/mavros',
                parameters=[{
                    'uas_url': '/uas1',
                    'system_id': 255,
                    'component_id': 191,
                    'target_system_id': 1,
                    'target_component_id': 1,
                    'plugin_denylist': [
                        'actuator_control', 'altitude', 'ftp', 'geofence',
                        'global_position', 'home_position', 'imu', 'local_position',
                        'nav_controller_output', 'param', 'rallypoint', 'rc_io',
                        'setpoint_accel', 'setpoint_attitude', 'setpoint_position',
                        'setpoint_raw', 'setpoint_trajectory', 'setpoint_velocity',
                        'sys_time', 'waypoint', 'wind_estimation',
                    ],
                }],
                extra_arguments=[{'use_intra_process_comms': True}]
            ),
        ],
        output='screen',
    )

    return LaunchDescription([
        joy_node,
        captain_node,
        teleop_node,
        mavros_container
    ])