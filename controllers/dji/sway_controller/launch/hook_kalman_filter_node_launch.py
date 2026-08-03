import os

from ament_index_python.packages import get_package_share_directory
from launch.substitutions        import PathJoinSubstitution, LaunchConfiguration
from launch                      import LaunchDescription
from launch.actions              import DeclareLaunchArgument, OpaqueFunction
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
    # The tunables below default to '' (empty) rather than to a value, so that
    # anything not passed on the command line falls through to the config yaml.
    # A real default here would always beat the yaml and it would stop being the
    # fallback. default_value must be a STRING - a float raises.
    L_arg = DeclareLaunchArgument(
        'L',
        default_value='',
        description='Lenght of the rope, negative value for not identified (unset -> yaml)'
    )
    xi_arg = DeclareLaunchArgument(
        'xi',
        default_value='',
        description='Damping factor, negative value for not identified (unset -> yaml)'
    )
    qc_arg = DeclareLaunchArgument(
        'qc',
        default_value='',
        description='Process noise density, rescale with loop_freq by (dt_old/dt_new)^2 (unset -> yaml)'
    )
    loop_freq_arg = DeclareLaunchArgument(
        'loop_freq',
        default_value='',
        description='Prediction rate in Hz (unset -> yaml)'
    )
    sigma_initial_arg = DeclareLaunchArgument(
        'sigma_initial',
        default_value='',
        description='Initial estimate uncertainty (unset -> yaml)'
    )
    mahalanobis_thr_arg = DeclareLaunchArgument(
        'mahalanobis_thr',
        default_value='',
        description='Threshold for outliers rejection (unset -> yaml)'
    )
    max_boresight_tilt_deg_arg = DeclareLaunchArgument(
        'max_boresight_tilt_deg',
        default_value='',
        description='Max gimbal tilt from straight-down before detections are dropped (unset -> yaml)'
    )
    robot_name = LaunchConfiguration('robot_name')
    use_sim_time = LaunchConfiguration('use_sim_time')

    config_file_name = 'hook_kalman_filter_node_config.yaml'
    config_dir = os.path.join(get_package_share_directory('sway_controller'), 'config')
    config_file = PathJoinSubstitution([config_dir, config_file_name])

    def make_node(context, *args, **kwargs):
        # A LaunchConfiguration can only be read inside a context, which is why
        # this lives in an OpaqueFunction: an argument becomes a ROS parameter
        # only if it was actually typed, otherwise the yaml value stands.
        overrides = {}
        for name, cast in (('L', float),
                           ('xi', float),
                           ('qc', float),
                           ('loop_freq', int),
                           ('sigma_initial', float),
                           ('mahalanobis_thr', float),
                           ('max_boresight_tilt_deg', float)):
            value = LaunchConfiguration(name).perform(context)
            if value != '':
                overrides[name] = cast(value)

        node = Node(
            package='sway_controller',
            executable='hook_kalman_filter_node',
            name='hook_kalman_filter_node',
            namespace=robot_name,
            output='screen',
            # Later entries win: yaml < robot_name/use_sim_time < command line
            parameters=[
                config_file,
                {
                    'robot_name':robot_name,
                    'use_sim_time':use_sim_time
                },
                overrides
            ]
        )
        return [node]

    return LaunchDescription([
        robot_name_arg,
        use_sim_time_arg,
        L_arg,
        xi_arg,
        qc_arg,
        loop_freq_arg,
        sigma_initial_arg,
        mahalanobis_thr_arg,
        max_boresight_tilt_deg_arg,
        OpaqueFunction(function=make_node)
    ])
