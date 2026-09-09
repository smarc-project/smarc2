from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

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
        mavros_node
    ])