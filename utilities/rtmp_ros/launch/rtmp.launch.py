from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "image_topic",
            default_value="/camera/image_raw/compressed",
            description="ROS 2 topic (sensor_msgs/Image or CompressedImage)",
        ),
        DeclareLaunchArgument(
            "url",
            default_value="rtmp://localhost:1935/live/test",
            description="RTMP ingest URL",
        ),
        DeclareLaunchArgument(
            "bitrate",
            default_value="2000000",
            description="H.264 encoder bitrate in bps",
        ),
        DeclareLaunchArgument(
            "output_width",
            default_value="0",
            description="Output width in pixels; 0 = keep source resolution",
        ),
        Node(
            package="rtmp_ros",
            executable="rtmp_ros_node",
            name="rtmp_ros_node",
            parameters=[{
                "image_topic":  LaunchConfiguration("image_topic"),
                "url":          LaunchConfiguration("url"),
                "bitrate":      LaunchConfiguration("bitrate"),
                "output_width": LaunchConfiguration("output_width"),
            }],
            output="screen",
        ),
    ])
