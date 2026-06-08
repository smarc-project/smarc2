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

    robot_ns_launch_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='evolo'
    )
    requested_ctrl_topic_arg = DeclareLaunchArgument('requested_ctrl_topic', default_value=evoloTopics.EVOLO_TWIST_PLANNED)
    safe_ctrl_topic_arg = DeclareLaunchArgument('safe_ctrl_topic', default_value=evoloTopics.EVOLO_TWIST_SETPOINT)
    obstacle_topic_arg = DeclareLaunchArgument('obstacle_topic', default_value=evoloTopics.EVOLO_CBF_OBSTACLES)

    cbf = Node(
        package='evolo_obstacle_avoidance',
        namespace=robot_ns,
        executable='cbf_avoidance',
        name='cbf_avoidance',
        parameters=[{"robot_name": robot_ns,
                     "requested_ctrl_topic": requested_ctrl_topic,
                     "safe_ctrl_topic": safe_ctrl_topic,
                     "obstacle_topic": obstacle_topic,
                     }]
    )

    return LaunchDescription([
        robot_ns_launch_arg,
        requested_ctrl_topic_arg,
        safe_ctrl_topic_arg,
        obstacle_topic_arg,
        cbf
    ])
