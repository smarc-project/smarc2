from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    robot_name_arg = DeclareLaunchArgument(
        'robot_name', default_value='floatsam_usv', description='Robot namespace')
    use_sim_arg = DeclareLaunchArgument(
        'use_sim', default_value='true', description='Use simulation flag')

    robot_name = LaunchConfiguration('robot_name')
    use_sim = LaunchConfiguration('use_sim')

    node = Node(
        package='floatsam_loiter_heading',
        executable='floatsam_loiter_heading_action_server',
        name='floatsam_loiter_heading_action_server',
        namespace=robot_name,
        parameters=[{
            "robot_name": robot_name,
            "use_sim": use_sim,
            "loiter_tolerance" : 5.0,               
            "heading_tolerance": 6.0,               # degrees 
            "loiter_reposition_tolerance": 0.5,
            "loiter_move_to_speed": 'fast',

            "yaw_p_gain": 0.3,
            "yaw_i_gain": 0.0,
            "yaw_d_gain": 0.1,  
            "yaw_threshold": 0.1,                   
            
            "yawrate_p_gain": 100.0, 
            "yawrate_i_gain": 0.0,
            "yawrate_d_gain": 30.0, 
            
            "velocity_p_gain": 500.0,
            "velocity_i_gain": 10.0,
            "velocity_d_gain": 0.0
            }],
        output='screen'
    )

    return LaunchDescription([
        robot_name_arg,
        use_sim_arg,
        node
    ])
