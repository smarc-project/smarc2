from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command

def generate_launch_description():
    ld = LaunchDescription()

    # Bluerov model for visualization

    # robot_name = LaunchConfiguration('brov_name')
    robot_name = "bluerov_saab"
    brov_package_dir = FindPackageShare(LaunchConfiguration('brov_package'))
    brov_path = PathJoinSubstitution([brov_package_dir, LaunchConfiguration('brov_package_path')])

    robot_description_content = ParameterValue(Command(['xacro ', brov_path, ' ', f'robot_name:={robot_name}']), value_type=str)

    robot_state_publisher_node_0 = Node(package='robot_state_publisher',
                                      executable='robot_state_publisher',
                                      parameters=[{
                                          'robot_description': robot_description_content,
                                        #   'robot_description': Command([
                                        #             'xacro ', brov_path, f'robot_name:={bluerov1}'])
                                      }], 
                                      remappings=[
                                            ('robot_description', 'brov2heavy_description'),
                                        ]
                                      )

    ld.add_action(robot_state_publisher_node_0)

    # Watertank model
    tank_package_dir = FindPackageShare(LaunchConfiguration('tank_package'))
    tank_path = PathJoinSubstitution([tank_package_dir, LaunchConfiguration('tank_package_path')])

    robot_description_content = ParameterValue(Command(['xacro ', tank_path]), value_type=str)

    robot_state_publisher_node_1 = Node(package='robot_state_publisher',
                                      executable='robot_state_publisher',
                                      parameters=[{
                                          'robot_description': robot_description_content,
                                      }], 
                                      remappings=[
                                            ('robot_description', 'watertank_description'),
                                        ]
                                      )

    ld.add_action(robot_state_publisher_node_1)

    # RVIZ
    watertank_utils_package = FindPackageShare('watertank_utils')
    default_rviz_config_path = PathJoinSubstitution([watertank_utils_package, 'config', 'watertank.rviz'])
    ld.add_action(DeclareLaunchArgument(name='rviz_config', default_value=default_rviz_config_path,
                                        description='Absolute path to rviz config file'))

    ld.add_action(Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config')],
    ))
    return ld
