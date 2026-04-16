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
            package='floatsam_controllers',
            executable='rvo_service_node',
            name='rvo_service_node',
            namespace=robot_name,
            parameters=[{
                'robot_name': robot_name,
                'time_horizon': 1.0,                # [s]
                'safety_margin': 1.0,               # [m]
                'max_speed': 2.0,                   # [m/s]
                'update_rate': 20.0,                # [Hz]
                'num_robot': 3,                      #integer
                'use_sim': use_sim
            }],
        )
    
    return LaunchDescription([
    robot_name_arg,
    use_sim_arg,
    node
    ])