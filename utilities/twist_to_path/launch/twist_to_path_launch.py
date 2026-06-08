from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration



def generate_launch_description():
    
    subscribe_topic = LaunchConfiguration('subscribe_topic')
    subscribe_topic_arg = DeclareLaunchArgument('subscribe_topic', default_value='subscribe_topic')

    publish_topic = LaunchConfiguration('publish_topic')
    publish_topic_arg = DeclareLaunchArgument('publish_topic', default_value='publish_topic')

    integration_time = LaunchConfiguration('integration_time')
    integration_time_arg = DeclareLaunchArgument('integration_time', default_value="30.0")

    integration_dt = LaunchConfiguration('integration_dt')
    integration_dt_arg = DeclareLaunchArgument('integration_dt', default_value="0.5")
    
    _node = Node(
        package='twist_to_path',
        executable='twist_to_path',
        name="twist_to_path",
        parameters=[{
                    "subscribe_topic": subscribe_topic,
                    "publish_topic" : publish_topic,
                    "integration_time" : integration_time,
                    "integration_dt" : integration_dt
                    }]
        )

    return LaunchDescription([
        subscribe_topic_arg,
        publish_topic_arg,
        integration_time_arg,
        integration_dt_arg,
        _node
    ])
