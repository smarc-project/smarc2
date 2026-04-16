from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    robot_name_arg = DeclareLaunchArgument('robot_name', default_value='floatsam_usv', description='Robot namespace')
    use_sim_arg = DeclareLaunchArgument('use_sim', default_value='true', description='Use simulator topics (true/false)')

    robot_name = LaunchConfiguration('robot_name')
    use_sim = LaunchConfiguration('use_sim')

    fm_pkg_share = get_package_share_directory('floatsam_move_to')
    fm_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(fm_pkg_share, 'launch', 'floatsam_move_to.launch.py')),
        launch_arguments={'robot_name': robot_name}.items()
    )

    fc_pkg_share = get_package_share_directory('floatsam_controllers')
    fc_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(fc_pkg_share, 'launch', 'floatsam_controllers_launch.py')),
        launch_arguments={'robot_name': robot_name}.items()
    )

    fb_pkg_share = get_package_share_directory('floatsam_topic_bridge')
    fb_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(fb_pkg_share, 'launch', 'floatsam_bridge.launch.py')),
        launch_arguments={'robot_name': robot_name, 'use_sim': use_sim}.items()
    )

    return LaunchDescription([
        robot_name_arg,
        use_sim_arg,
        fm_launch,
        fc_launch,
        fb_launch,
    ])
