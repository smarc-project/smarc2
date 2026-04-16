from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    robot_ns = LaunchConfiguration('robot_name')

    robot_ns_launch_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='floatsam_usv'
    )

    loiter_server_node = Node(
        package='floatsam_loiter',
        namespace=robot_ns,
        executable='floatsam_loiter_action_server',
        name='floatsam_loiter_action_server',
        parameters=[{
            'robot_name': robot_ns,
            'loiter_tolerance': 2.0,  # meters - loiter circle radius
            'loiter_reposition_tolerance': 0.5,  # meters - strict tolerance for move_to
            'loiter_speed': 1.0,  # m/s - repositioning speed
            'loiter_move_to_speed': 'fast',  # move_to speed: 'slow', 'standard', or 'fast'

            "yaw_p_gain": 0.3,
            "yaw_i_gain": 0.0,
            "yaw_d_gain": 0.1,  
            "yaw_threshold": 0.5,
            
            "yawrate_p_gain": 300.0,
            "yawrate_i_gain": 0.0,
            "yawrate_d_gain": 30.0,  
            
            "velocity_p_gain": 500.0,
            "velocity_i_gain": 10.0,
            "velocity_d_gain": 0.0
        }],
        output='screen'
    )

    return LaunchDescription([
        robot_ns_launch_arg,
        loiter_server_node
    ])
