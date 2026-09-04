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

    mavros_node = Node(
    package='mavros',
    executable='mavros_node',
    namespace='ActiveHook/mavros',
    output='screen',
    parameters=[{
        'fcu_url': 'udp://0.0.0.0:14551@',
        'system_id': 255,
        'component_id': 191,
        'target_system_id': 1,
        'target_component_id': 1,
    }]
)

    return LaunchDescription([
        joy_node,
        captain_node,
        teleop_node,
        mavros_node
    ])