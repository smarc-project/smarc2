from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    package_name = 'alars_auv_perception'

    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='Quadrotor'
    )
    device_arg = DeclareLaunchArgument(
        'device',
        default_value='cpu'
    )
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false'
    )
    model_package_arg = DeclareLaunchArgument(
        'model_package',
        default_value=package_name
    )
    model_file_arg = DeclareLaunchArgument(
        'model_file',
        default_value='yolo_model_5cls.pt'
    )
    raw_image_topic_arg = DeclareLaunchArgument(
        'raw_image_topic',
        default_value=''
    )

    robot_name = LaunchConfiguration('robot_name')
    device = LaunchConfiguration('device')
    use_sim_time = LaunchConfiguration('use_sim_time')
    model_package = LaunchConfiguration('model_package')
    model_file = LaunchConfiguration('model_file')
    raw_image_topic = LaunchConfiguration('raw_image_topic')

    detection_config = PathJoinSubstitution([
        FindPackageShare(package_name),
        'config',
        'parameters',
        'detection_parameters.yaml'
    ])

    model_path = PathJoinSubstitution([
        FindPackageShare(model_package),
        'trained_models',
        model_file
    ])

    detector_node = Node(
        package=package_name,
        executable='alars_yolo_detector',
        namespace=robot_name,
        output='screen',
        parameters=[
            detection_config,
            {
                'namespace': robot_name,
                'device': device,
                'use_sim_time': use_sim_time,
                'model_path': model_path,
                'topics.raw_image': raw_image_topic,
            }
        ],
    )

    return LaunchDescription([
        robot_name_arg,
        device_arg,
        use_sim_time_arg,
        model_package_arg,
        model_file_arg,
        raw_image_topic_arg,
        LogInfo(msg=['[Launch] robot_name = ', robot_name]),
        LogInfo(msg=['[Launch] device = ', device]),
        LogInfo(msg=['[Launch] use_sim_time = ', use_sim_time]),
        LogInfo(msg=['[Launch] model package = ', model_package]),
        LogInfo(msg=['[Launch] model path = ', model_path]),
        LogInfo(msg=['[Launch] raw image topic = ', raw_image_topic]),
        detector_node,
    ])