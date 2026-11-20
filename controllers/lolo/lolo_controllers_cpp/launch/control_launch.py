from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    robot_ns = LaunchConfiguration('robot_name')

    robot_ns_launch_arg = DeclareLaunchArgument('robot_name', default_value='lolo')

    controller_node = Node(
        package='lolo_controllers_cpp',
        executable='lolo_controllers',
        name='controller',
        namespace=robot_ns,
        output='screen',
        parameters=[{
            # General
            # All values are written as floats (e.g. 10.0, not 10):
            # float/double parameters reject integer values.
            'update_rate': 10.0,
            'min_altitude': 2.0,
            'max_rpm': 900.0,
            'differential_thrust_gain': 1200.0,

            # Yaw PID
            'pid_yaw_p': 0.1,
            'pid_yaw_i': 0.0,
            'pid_yaw_d': 0.0,
            'pid_yaw_limit': 0.1,
            'pid_yaw_i_limit': 0.01,

            # Yaw rate PID
            'pid_yaw_rate_p': 40.0,
            'pid_yaw_rate_i': 0.0,
            'pid_yaw_rate_d': 0.0,
            'pid_yaw_rate_limit': 0.7,
            'pid_yaw_rate_i_limit': 0.7,

            # Roll PID
            'pid_roll_p': 0.5,
            'pid_roll_i': 0.01,
            'pid_roll_d': 0.0,
            'pid_roll_limit': 0.35,
            'pid_roll_i_limit': 0.2,

            # Depth PID
            'pid_depth_p': 0.1,
            'pid_depth_i': 0.05,
            'pid_depth_d': 0.0,
            'pid_depth_limit': 0.52,
            'pid_depth_i_limit': 0.1,

            # Pitch PID
            'pid_pitch_p': 4.0,
            'pid_pitch_i': 0.1,
            'pid_pitch_d': 0.0,
            'pid_pitch_limit': 0.7,
            'pid_pitch_i_limit': 0.5,

            # Speed PID
            'pid_speed_p': 1.0,
            'pid_speed_i': 0.0,
            'pid_speed_d': 0.0,
            'pid_speed_limit': 1.0,
            'pid_speed_i_limit': 1.0,
        }],
    )

    return LaunchDescription([
        robot_ns_launch_arg,
        controller_node
    ])