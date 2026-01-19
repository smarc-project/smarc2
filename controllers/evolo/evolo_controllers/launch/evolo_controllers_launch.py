from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from smarc_msgs.msg import Topics as SmarcTopics
from smarc_control_msgs.msg import Topics as ControlTopics


def generate_launch_description():
    robot_ns = LaunchConfiguration('robot_name')

    robot_ns_launch_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='evolo'
    )

    yaw_control = Node(
        package='evolo_controllers',
        namespace=robot_ns,
        executable='yaw_controller',
        name='yaw_controller',
        parameters=[{"robot_name": robot_ns}]
    )

    return LaunchDescription([
        robot_ns_launch_arg,
        yaw_control
    ])
