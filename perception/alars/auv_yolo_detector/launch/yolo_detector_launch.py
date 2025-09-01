from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

    # ---- frequently changed params as launch arguments ...
    mode_arg = DeclareLaunchArgument('mode', default_value='sim')
    inference_frequency_arg = DeclareLaunchArgument('inference_frequency', default_value='0.5')
    model_path_arg = DeclareLaunchArgument('model_path',
                                       default_value = '/home/fm/KTH_Courses/ResearchProject/RProj_GitRepoFork/colcon_ws/src/smarc2/perception/auv_yolo_detector')

    # ... and as node params
    mode = LaunchConfiguration('mode')
    inference_frequency = LaunchConfiguration('inference_frequency')
    model_path = LaunchConfiguration('model_path')

    # ---- rarely changed params from yaml (yaml has every parameter but launch arguments will override)
    config_file = PathJoinSubstitution([
        FindPackageShare('auv_yolo_detector'),
        'config',
        'params.yaml'
    ])

    detector_node = Node(
        package='auv_yolo_detector',
        executable='auv_yolo_detector',
        namespace='Quadrotor',
        output='screen',
        parameters=[
            config_file,
            {
                'mode': mode,
                'inference_frequency': inference_frequency,
                'model_path': model_path
            }
        ]
    )

    return LaunchDescription([
        mode_arg,
        inference_frequency_arg,
        model_path_arg,
        detector_node
    ])
