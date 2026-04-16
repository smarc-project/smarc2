from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
import math

AO=180.0 / math.pi 

def generate_launch_description():
    robot_ns = LaunchConfiguration('robot_name')

    robot_ns_launch_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='floatsam_usv'
    )

    odom_splitter_node = Node(
        package='odom_splitter',
        namespace=robot_ns,
        executable='odom_splitter',
        name='odom_splitter',
        parameters=[{"robot_name": robot_ns}]
    )

    # ============================================
    # CAPTAIN NODE - Integrated Controller
    # ============================================
    
    captain_node = Node(
        package='floatsam_controllers',
        namespace=robot_ns,
        executable='captain',
        name='captain',
        parameters=[{
            "robot_name": robot_ns,
            "update_rate": 20.0,
            
            # ===== YAW PID PARAMETERS =====
            "yaw_p_gain": 0.3,
            "yaw_i_gain": 0.0,
            "yaw_d_gain": 0.1,
            "yaw_output_limit": 1.0,  # rad/s max yaw rate
            "yaw_threshold": 0.5,
            
            # ===== YAW RATE PID PARAMETERS =====
            "yawrate_p_gain": 300.0,
            "yawrate_i_gain": 0.0,
            "yawrate_d_gain": 30.0,
            "yawrate_output_limit": 800.0,  # RPM
            
            # ===== VELOCITY PID PARAMETERS =====
            "velocity_p_gain": 500.0,
            "velocity_i_gain": 10.0,
            "velocity_d_gain": 0.0,
            "velocity_output_limit": 1000.0,  # RPM
            
            # ===== MIXER PARAMETERS =====
            "rpm_deadband": 50.0,  # Minimum RPM threshold
            "thruster_limit": 1000.0,  # Maximum RPM
            "turn_in_place_min_rpm": 100.0,  # Minimum RPM for turn-in-place
            "turn_in_place_gain": 10.0,  # RPM per radian of heading error
            
            # ===== HEALTH CHECK PARAMETERS =====
            "max_delta_rpm": 200.0,  # Maximum RPM change per control cycle (rate limiter)
        }]
    )

    return LaunchDescription([
        robot_ns_launch_arg,
        odom_splitter_node,
        captain_node
    ])
