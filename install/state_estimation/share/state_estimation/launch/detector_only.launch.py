# state_estimation/launch/detector_only.launch.py

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='state_estimation',
            executable='detector',
            name='detector_node'
        ),
    ])
