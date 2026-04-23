import os
from dji_msgs.msg import Topics, Links
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory




def generate_launch_description():

    robot_name_arg = DeclareLaunchArgument("robot_name", default_value="M350")
    robot_name = LaunchConfiguration("robot_name")

    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='false')
    use_sim_time = LaunchConfiguration("use_sim_time")

    camera_calibration_file_arg = DeclareLaunchArgument("camera_calibration_file", default_value="cam_params.yaml")
    camera_calibration_file = LaunchConfiguration("camera_calibration_file")

    auv_staleness_arg = DeclareLaunchArgument("auv_ekf_staleness_seconds", default_value="3.0")
    auv_ekf_staleness_seconds = LaunchConfiguration("auv_ekf_staleness_seconds")

    buoy_staleness_arg = DeclareLaunchArgument("buoy_ekf_staleness_seconds", default_value="10.0")
    buoy_ekf_staleness_seconds = LaunchConfiguration("buoy_ekf_staleness_seconds")
    
    auv_poly_in = Topics.ESTIMATED_AUV_OBB_TOPIC
    buoy_poly_in = Topics.ESTIMATED_BUOY_OBB_TOPIC

    auv_link_out = Links.ESTIMATED_AUV
    buoy_link_out = Links.ESTIMATED_BUOY

    auv_length = "1.3"
    auv_width = "0.16"

    buoy_length = "0.27"
    buoy_width = "0.09"
    
    auv_cov_pose_out = Topics.PROJECTED_AUV_POSE_WITH_COV_TOPIC
    buoy_cov_pose_out = Topics.PROJECTED_BUOY_POSE_WITH_COV_TOPIC
    

    pkg_dir = get_package_share_directory('auv_state_estimation')

    auv_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_dir, 'launch', 'ekf_launch.py')),
        launch_arguments={
            'robot_name': robot_name,
            'use_sim_time': use_sim_time,
            'camera_calibration_file': camera_calibration_file,
            'input_polygon': auv_poly_in,
            'output_link': auv_link_out,
            'obb_length': auv_length,
            'obb_width': auv_width,
            'output_cov_pose_topic': auv_cov_pose_out,
            'stale_state_age': auv_ekf_staleness_seconds
        }.items()
    )

    buoy_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_dir, 'launch', 'ekf_launch.py')),
        launch_arguments={
            'robot_name': robot_name,
            'use_sim_time': use_sim_time,
            'camera_calibration_file': camera_calibration_file,
            'input_polygon': buoy_poly_in,
            'output_link': buoy_link_out,
            'obb_length': buoy_length,
            'obb_width': buoy_width,
            'output_cov_pose_topic': buoy_cov_pose_out,
            'stale_state_age': buoy_ekf_staleness_seconds
        }.items()
    )

    return LaunchDescription([
        robot_name_arg,
        use_sim_time_arg,
        camera_calibration_file_arg,
        auv_staleness_arg,
        buoy_staleness_arg,
        auv_launch,
        buoy_launch
    ])

