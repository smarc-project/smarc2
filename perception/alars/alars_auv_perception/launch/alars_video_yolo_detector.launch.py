from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    package_name = 'alars_auv_perception'

    namespace_arg = DeclareLaunchArgument(
        'namespace',
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

    namespace = LaunchConfiguration('namespace')
    device = LaunchConfiguration('device')
    use_sim_time = LaunchConfiguration('use_sim_time')
    model_package = LaunchConfiguration('model_package')
    model_file = LaunchConfiguration('model_file')

    detection_config = PathJoinSubstitution([
        FindPackageShare(package_name),
        'config',
        'parameters',
        'detection_parameters.yaml'
    ])

    video_publisher_config = PathJoinSubstitution([
        FindPackageShare(package_name),
        'config',
        'parameters',
        'video_publisher_parameters.yaml'
    ])

    model_path = PathJoinSubstitution([
        FindPackageShare(model_package),
        'trained_models',
        model_file
    ])

    detector_node = Node(
        package=package_name,
        executable='alars_yolo_detector',
        namespace=namespace,
        output='screen',
        parameters=[
            detection_config,
            {
                'namespace': namespace,
                'device': device,
                'use_sim_time': use_sim_time,
                'model_path': model_path,
            }
        ],
    )

    video_publisher_node = Node(
        package=package_name,
        executable='alars_video_publisher',
        namespace=namespace,
        output='screen',
        parameters=[
            video_publisher_config,
            {
                'use_sim_time': False,
            }
        ],
    )

    return LaunchDescription([
        namespace_arg,
        device_arg,
        use_sim_time_arg,
        model_package_arg,
        model_file_arg,

        LogInfo(msg=['[Launch] namespace = ', namespace]),
        LogInfo(msg=['[Launch] device = ', device]),
        LogInfo(msg=['[Launch] use_sim_time = ', use_sim_time]),
        LogInfo(msg=['[Launch] model package = ', model_package]),
        LogInfo(msg=['[Launch] model path = ', model_path]),
        LogInfo(msg=['[Launch] detection params = ', detection_config]),
        LogInfo(msg=['[Launch] video publisher params = ', video_publisher_config]),

        video_publisher_node,
        detector_node,
    ])