from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, ExecuteProcess, OpaqueFunction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    package_name = 'alars_auv_perception'

    namespace = LaunchConfiguration('namespace')
    device = LaunchConfiguration('device')
    use_sim_time = LaunchConfiguration('use_sim_time')
    model_package = LaunchConfiguration('model_package')
    model_file = LaunchConfiguration('model_file')

    bag_path = LaunchConfiguration('bag_path').perform(context)
    bag_rate = LaunchConfiguration('bag_rate')
    bag_loop = LaunchConfiguration('bag_loop').perform(context).lower() == 'true'
    bag_start_paused = LaunchConfiguration('bag_start_paused').perform(context).lower() == 'true'
    bag_remap = LaunchConfiguration('bag_remap').perform(context).strip()

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

    if not bag_path:
        raise RuntimeError("Launch argument 'bag_path' must be provided.")

    bag_cmd = [
        'ros2', 'bag', 'play',
        bag_path,
        '--clock',
        '--rate', bag_rate,
    ]

    if bag_loop:
        bag_cmd.append('--loop')

    if bag_start_paused:
        bag_cmd.append('--start-paused')

    if bag_remap:
        bag_cmd.extend(['--remap', bag_remap])

    bag_play = ExecuteProcess(
        cmd=bag_cmd,
        output='screen',
    )

    return [
        LogInfo(msg=['[Launch] namespace = ', namespace]),
        LogInfo(msg=['[Launch] device = ', device]),
        LogInfo(msg=['[Launch] use_sim_time = ', use_sim_time]),
        LogInfo(msg=['[Launch] model package = ', model_package]),
        LogInfo(msg=['[Launch] model path = ', model_path]),
        LogInfo(msg=[f'[Launch] bag path = {bag_path}']),
        LogInfo(msg=['[Launch] bag rate = ', bag_rate]),
        LogInfo(msg=[f'[Launch] bag loop = {bag_loop}']),
        LogInfo(msg=[f'[Launch] bag start paused = {bag_start_paused}']),
        LogInfo(msg=[f'[Launch] bag remap = {bag_remap}']),
        detector_node,
        bag_play,
    ]


def generate_launch_description():
    package_name = 'alars_auv_perception'

    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace',
            default_value='M350'
        ),
        DeclareLaunchArgument(
            'device',
            default_value='cpu'
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true'
        ),
        DeclareLaunchArgument(
            'model_package',
            default_value=package_name
        ),
        DeclareLaunchArgument(
            'model_file',
            default_value='yolo_model_5cls.pt'
        ),
        DeclareLaunchArgument(
            'bag_path',
            default_value=''
        ),
        DeclareLaunchArgument(
            'bag_rate',
            default_value='1.0'
        ),
        DeclareLaunchArgument(
            'bag_loop',
            default_value='false'
        ),
        DeclareLaunchArgument(
            'bag_start_paused',
            default_value='false'
        ),
        DeclareLaunchArgument(
            'bag_remap',
            default_value=''
        ),
        OpaqueFunction(function=launch_setup),
    ])