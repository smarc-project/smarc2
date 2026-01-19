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

   
    # 'brov_package': 'brov2heavy_description',
    # 'brov_package_path': PathJoinSubstitution(['robots', 'brov2heavy_default.urdf.xacro']),

    # robot_name = LaunchConfiguration('brov_name')
    robot_name = "saabmarine"
    # brov_package_dir = 'brov2heavy_description'
    brov_package_dir = FindPackageShare('brov2heavy_description')
    brov_path = PathJoinSubstitution([brov_package_dir, PathJoinSubstitution(['robots', 'brov2heavy_default.urdf.xacro'])])

    robot_description_content = ParameterValue(Command(['xacro ', brov_path, ' ', f'robot_name:={robot_name}']), value_type=str)

    robot_state_publisher_node_1 = Node(package='robot_state_publisher',
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

    ld.add_action(robot_state_publisher_node_1)

    ld.add_action(Node(
        package='brov_dr',
        executable='brov_dr_node',
        output='screen',
    ))

    return ld
