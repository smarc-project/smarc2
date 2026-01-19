from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument,LogInfo
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition, LaunchConfigurationEquals

def generate_launch_description():

    # ---- frequently changed params as launch arguments ...
    namespace_arg = DeclareLaunchArgument('namespace', default_value='Quadrotor')
    device_arg = DeclareLaunchArgument('device', default_value='cpu')
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='false')
    model_file_arg = DeclareLaunchArgument('model_file', default_value='yolo_model.pt')

    # ... and as node params
    namespace = LaunchConfiguration('namespace')
    device = LaunchConfiguration('device')
    use_sim_time = LaunchConfiguration('use_sim_time')
    model_file = LaunchConfiguration('model_file')

    # ---- Paths for config files and model.
    real_config = PathJoinSubstitution([
        FindPackageShare('auv_yolo_detector'),
        'config',
        'params.yaml'
    ])


    model_path = PathJoinSubstitution([
        FindPackageShare('auv_yolo_detector'),
        'config',
        model_file
    ])

    # ----Node declaration, while making sure config file matches the mode

    detector_node_real = Node(
        package='auv_yolo_detector',
        executable='auv_yolo_detector',
        namespace=namespace,
        output='screen',
        parameters=[
            real_config,
            {
                'namespace': namespace,
                'device': device,
                'use_sim_time': use_sim_time,
                'model_path': model_path
            }
        ],
        
    )

    return LaunchDescription([
        namespace_arg,
        device_arg,
        use_sim_time_arg,
        model_file_arg,
        LogInfo(msg=["[Launch] namespace argument = ", namespace]),
        LogInfo(msg=["[Launch] device argument = ", device]),
        LogInfo(msg=["[Launch] use_sim_time argument = ", use_sim_time]),
        LogInfo(msg=["[Launch] yolo model path = ", model_path]),
        detector_node_real
    ])
