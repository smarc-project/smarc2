from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from smarc_msgs.msg import Topics as SmarcTopics
from evolo_msgs.msg import Topics as evoloTopics
from smarc_control_msgs.msg import Topics as ControlTopics


def generate_launch_description():

    robot_ns = LaunchConfiguration('robot_name')
    requested_ctrl_topic = LaunchConfiguration('requested_ctrl_topic')
    safe_ctrl_topic = LaunchConfiguration('safe_ctrl_topic')
    obstacle_topic = LaunchConfiguration('obstacle_topic')
    max_yaw_diff = LaunchConfiguration('max_yaw_diff')
    p_value = LaunchConfiguration('p_value')
    alpha_value = LaunchConfiguration('alpha_value')
    robot_radius = LaunchConfiguration('robot_radius')

    robot_ns_launch_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='evolo'
    )
    requested_ctrl_topic_arg = DeclareLaunchArgument('requested_ctrl_topic', default_value=evoloTopics.EVOLO_CONTROL_PLANNED)
    safe_ctrl_topic_arg = DeclareLaunchArgument('safe_ctrl_topic', default_value=evoloTopics.EVOLO_CONTROL_SETPOINT)
    obstacle_topic_arg = DeclareLaunchArgument('obstacle_topic', default_value=evoloTopics.EVOLO_CBF_OBSTACLES)
    max_yaw_diff_arg = DeclareLaunchArgument('max_yaw_diff', default_value="40.0") # In [deg]
    p_value_arg = DeclareLaunchArgument('p_value', default_value="0.5")
    alpha_value_arg = DeclareLaunchArgument('alpha_value', default_value="1.0")
    robot_radius_arg = DeclareLaunchArgument('robot_radius', default_value="2.0")

    cbf = Node(
        package='evolo_obstacle_avoidance',
        namespace=robot_ns,
        executable='cbf_avoidance',
        name='cbf_avoidance',
        parameters=[{"robot_name": robot_ns,
                     "requested_ctrl_topic": requested_ctrl_topic,
                     "safe_ctrl_topic": safe_ctrl_topic,
                     "obstacle_topic": obstacle_topic,
                     "max_yaw_diff": max_yaw_diff,
                     "p_value": p_value,
                     "alpha_value": alpha_value,
                     "robot_radius": robot_radius,
                     }]
    )

    return LaunchDescription([
        robot_ns_launch_arg,
        requested_ctrl_topic_arg,
        safe_ctrl_topic_arg,
        obstacle_topic_arg,
        max_yaw_diff_arg,
        p_value_arg,
        alpha_value_arg,
        robot_radius_arg,
        cbf
    ])
