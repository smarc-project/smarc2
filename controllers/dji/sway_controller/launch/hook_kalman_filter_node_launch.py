import os

from ament_index_python.packages import get_package_share_directory
from launch.substitutions        import PathJoinSubstitution, LaunchConfiguration
from launch                      import LaunchDescription
from launch.actions              import DeclareLaunchArgument
from launch_ros.actions          import Node

def generate_launch_description():
    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='M350',
        description='Namespace for the robot'
    )
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='False',
        description='Use simulation clock instead of wall clock'
    )
    
    L_arg = DeclareLaunchArgument(
        'L',
        default_value='',
        description='Lenght of the rope, negative value for not identified. NOT settable here, edit hook_kalman_filter_node_config.yaml'
    )
    xi_arg = DeclareLaunchArgument(
        'xi',
        default_value='',
        description='Damping factor, negative value for not identified NOT settable here, edit hook_kalman_filter_node_config.yaml'
    )
    qc_arg = DeclareLaunchArgument(
        'qc',
        default_value='',
        description='Process noise density, rescale with loop_freq by (dt_old/dt_new)^2 NOT settable here, edit hook_kalman_filter_node_config.yaml'
    )
    loop_freq_arg = DeclareLaunchArgument(
        'loop_freq',
        default_value='',
        description='Prediction rate in Hz NOT settable here, edit hook_kalman_filter_node_config.yaml'
    )
    sigma_initial_arg = DeclareLaunchArgument(
        'sigma_initial',
        default_value='',
        description='Initial estimate uncertainty NOT settable here, edit hook_kalman_filter_node_config.yaml'
    )
    mahalanobis_thr_arg = DeclareLaunchArgument(
        'mahalanobis_thr',
        default_value='',
        description='Threshold for outliers rejection NOT settable here, edit hook_kalman_filter_node_config.yaml'
    )
    max_boresight_tilt_deg_arg = DeclareLaunchArgument(
        'max_boresight_tilt_deg',
        default_value='',
        description='Max gimbal tilt from straight-down before detections are dropped NOT settable here, edit hook_kalman_filter_node_config.yaml'
    )
   
    camera_calibration_file_arg = DeclareLaunchArgument(
        'camera_calibration_file',
        default_value='z1_720p_cam_params.yaml',
        description='Camera calibration yaml in auv_state_estimation/config'
    )

    robot_name = LaunchConfiguration('robot_name')
    use_sim_time = LaunchConfiguration('use_sim_time')
    camera_calibration_file = LaunchConfiguration('camera_calibration_file')

    config_file_name = 'hook_kalman_filter_node_config.yaml'
    config_dir = os.path.join(get_package_share_directory('sway_controller'), 'config')
    config_file = PathJoinSubstitution([config_dir, config_file_name])

    node = Node(
            package='sway_controller',
            executable='hook_kalman_filter_node',
            name='hook_kalman_filter_node',
            namespace=robot_name,
            output='screen',
            parameters=[
                config_file,
                {
                'robot_name': robot_name,
                'use_sim_time': use_sim_time,
                'camera_calibration_file': camera_calibration_file,
            }]
        )

    return LaunchDescription([
        robot_name_arg,
        use_sim_time_arg,
        camera_calibration_file_arg,
        L_arg,
        xi_arg,
        qc_arg,
        loop_freq_arg,
        sigma_initial_arg,
        mahalanobis_thr_arg,
        max_boresight_tilt_deg_arg,
        node
    ])
