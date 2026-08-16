import os

from ament_index_python.packages import get_package_share_directory
from launch.substitutions        import PythonExpression, PathJoinSubstitution, LaunchConfiguration
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

    #  * --> NOT settable here, edit alars_move_to_damped_server_config_M350.yaml
   
    enable_lqg_arg = DeclareLaunchArgument(
        'enable_lqg',
        default_value='',
        description='False = ZVD feedforward only, no LQG feedback trim *'
    )
    goal_tolerance_arg = DeclareLaunchArgument(
        'goal_tolerance',
        default_value='',
        description='Distance to the goal that counts as arrived, m *'
    )
    max_speed_arg = DeclareLaunchArgument(
        'max_speed',
        default_value='',
        description='Speed limit, m/s. Also sets the LQR control weight 1/v_max^2 *'
    )
    max_acceleration_arg = DeclareLaunchArgument(
        'max_acceleration',
        default_value='',
        description='Acceleration limit used to time the path, m/s^2 *'
    )
    settle_extra_arg = DeclareLaunchArgument(
        'settle_extra',
        default_value='',
        description='Extra time allowed after the plan ends, s *'
    )
    lqg_rho_arg = DeclareLaunchArgument(
        'lqg_rho',
        default_value='',
        description='Mission control penalty. Enters the gain as ~sqrt(rho), so move it '
                    'by decades. Too low and the trim saturates *'
    )
    lqg_theta_max_arg = DeclareLaunchArgument(
        'lqg_theta_max',
        default_value='',
        description='Swing tolerance for the mission gain, rad, Bryson weight 1/x^2 *'
    )
    lqg_position_max_arg = DeclareLaunchArgument(
        'lqg_position_max',
        default_value='',
        description='Position tolerance for the mission gain, m *'
    )
    max_estimate_age_arg = DeclareLaunchArgument(
        'max_estimate_age',
        default_value='',
        description='Older than this the swing estimate is unusable -> feedforward only, s *'
    )
    max_trim_speed_arg = DeclareLaunchArgument(
        'max_trim_speed',
        default_value='',
        description='Cap on the feedback trim alone, m/s. Must exceed L*omega_peak or the '
                    'loop cannot chase the payload *'
    )
    max_theta_for_lqg_arg = DeclareLaunchArgument(
        'max_theta_for_lqg',
        default_value='',
        description='Beyond this the linearised model is invalid and feedback is dropped, rad *'
    )
    stabilize_before_mission_arg = DeclareLaunchArgument(
        'stabilize_before_mission',
        default_value='',
        description='Damp the payload before departing *'
    )
    stabilize_theta_tol_arg = DeclareLaunchArgument(
        'stabilize_theta_tol',
        default_value='',
        description='Swing considered settled below this, rad *'
    )
    stabilize_omega_tol_arg = DeclareLaunchArgument(
        'stabilize_omega_tol',
        default_value='',
        description='Swing rate considered settled below this, rad/s *'
    )
    stabilize_settle_time_arg = DeclareLaunchArgument(
        'stabilize_settle_time',
        default_value='',
        description='Time to stay within tolerance before departing, s *'
    )
    stabilize_timeout_arg = DeclareLaunchArgument(
        'stabilize_timeout',
        default_value='',
        description='Give up stabilising and depart anyway after this, s *'
    )
    stabilize_rho_arg = DeclareLaunchArgument(
        'stabilize_rho',
        default_value='',
        description='Control penalty while stabilising. Lower than lqg_rho because here '
                    'the command IS the whole control action *'
    )
    stabilize_theta_max_arg = DeclareLaunchArgument(
        'stabilize_theta_max',
        default_value='',
        description='Swing tolerance for the stabilising gain, rad *'
    )
    stabilize_position_max_arg = DeclareLaunchArgument(
        'stabilize_position_max',
        default_value='',
        description='Position tolerance while stabilising, m - loose on purpose *'
    )

    robot_name = LaunchConfiguration('robot_name')
    use_sim_time = LaunchConfiguration('use_sim_time')

    config_file_name = PythonExpression([
        "'alars_move_to_damped_server_config_M350.yaml' if '", robot_name, "' == 'M350' else 'alars_move_to_damped_server_config_FC30.yaml'"
    ])
    config_dir = os.path.join(get_package_share_directory('alars'), 'config')

    config_file = PathJoinSubstitution([config_dir, config_file_name])

    dji_captain_model_dir = PathJoinSubstitution([
        get_package_share_directory('dji_captain'), 'models', robot_name
    ])
    continuous_model_path = PathJoinSubstitution([
        dji_captain_model_dir, 'continuous_model', 'model_bla_diag_cmdvle.npz'
    ])
    discrete_model_path = PathJoinSubstitution([
        dji_captain_model_dir, 'discrete_model', 'discrete_models.npz'
    ])


    node = Node(
        package='alars',
        executable='alars_move_to_damped_action_server',
        name='alars_move_to_damped_server',
        namespace=robot_name,
        output='screen',
        parameters=[
            config_file,
            {
                'robot_name': robot_name,
                'use_sim_time': use_sim_time,
                'continuous_model_path': continuous_model_path,
                'discrete_model_path': discrete_model_path,
            },
            
        ]
    )
    

    return LaunchDescription([
        robot_name_arg,
        use_sim_time_arg,
        enable_lqg_arg,
        goal_tolerance_arg,
        max_speed_arg,
        max_acceleration_arg,
        settle_extra_arg,
        lqg_rho_arg,
        lqg_theta_max_arg,
        lqg_position_max_arg,
        max_estimate_age_arg,
        max_trim_speed_arg,
        max_theta_for_lqg_arg,
        stabilize_before_mission_arg,
        stabilize_theta_tol_arg,
        stabilize_omega_tol_arg,
        stabilize_settle_time_arg,
        stabilize_timeout_arg,
        stabilize_rho_arg,
        stabilize_theta_max_arg,
        stabilize_position_max_arg,
        node
    ])
