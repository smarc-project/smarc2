from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from smarc_msgs.msg import Topics as SmarcTopics
from evolo_msgs.msg import Topics as evoloTopics
from smarc_control_msgs.msg import Topics as ControlTopics


def generate_launch_description():

    robot_ns = LaunchConfiguration('robot_name')
    obstacle_topic = LaunchConfiguration('obstacle_topic')
    obstacle_radius = LaunchConfiguration('obstacle_radius')
    time_to_collision = LaunchConfiguration('time_to_collision')
    obstacle_angle = LaunchConfiguration('obstacle_angle')
    obstacle_speed = LaunchConfiguration('obstacle_speed')
    p_value = LaunchConfiguration('p_value')

    robot_ns_launch_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='evolo'
    )
    obstacle_topic_arg = DeclareLaunchArgument('obstacle_topic', default_value=evoloTopics.EVOLO_CBF_OBSTACLES)
    obstacle_radius_arg = DeclareLaunchArgument('obstacle_radius', default_value="20.0") # [m]
    time_to_collision_arg = DeclareLaunchArgument('time_to_collision', default_value="10.0") #[s]
    obstacle_angle_arg = DeclareLaunchArgument('obstacle_angle', default_value="1.5708") # [rad]
    obstacle_speed_arg = DeclareLaunchArgument('obstacle_speed', default_value="0.0") # [m/s]
    p_value_arg = DeclareLaunchArgument('p_value', default_value="0.5")

    ghost = Node(
        package='evolo_ghost_obstacles',
        namespace=robot_ns,
        executable="ghost_obstacles",
        name='ghost_obstacles',
        parameters=[{"robot_name": robot_ns,
                     "obstacle_topic": obstacle_topic,
                     "obstacle_radius": obstacle_radius,
                     "time_to_collision": time_to_collision,
                     "obstacle_angle": obstacle_angle,
                     "obstacle_speed": obstacle_speed,
                     "p_value": p_value,
                     }]
    )

    return LaunchDescription([
        robot_ns_launch_arg,
        obstacle_topic_arg,
        obstacle_radius_arg,
        time_to_collision_arg,
        obstacle_angle_arg,
        obstacle_speed_arg,
        p_value_arg,
        ghost
    ])
