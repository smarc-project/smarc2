from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from smarc_msgs.msg import Topics as SmarcTopics
from evolo_msgs.msg import Topics as evoloTopics
from smarc_control_msgs.msg import Topics as ControlTopics


def generate_launch_description():

    robot_ns = LaunchConfiguration('robot_name')
    grid_topic = LaunchConfiguration('grid_topic')
    obstacle_topic = LaunchConfiguration('obstacle_topic')

    robot_ns_launch_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='evolo'
    )
    grid_topic_arg = DeclareLaunchArgument('grid_topic', default_value=evoloTopics.EVOLO_OCCUPANCY_GRID)
    obstacle_topic_arg = DeclareLaunchArgument('obstacle_topic', default_value=evoloTopics.EVOLO_CBF_OBSTACLES)

    cluster_grid = Node(
        package='evolo_map_cluster',
        namespace=robot_ns,
        executable='clustering_grid',
        name='clustering_grid',
        parameters=[{"robot_name": robot_ns,
                     "grid_topic": grid_topic,
                     "obstacle_topic": obstacle_topic,
                     }]
    )

    return LaunchDescription([
        robot_ns_launch_arg,
        grid_topic_arg,
        obstacle_topic_arg,
        cluster_grid
    ])
