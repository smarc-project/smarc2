from auv_state_estimation import ekf_node
from dji_msgs.msg import Topics, Links
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    robot_name_arg = DeclareLaunchArgument(
        "robot_name",
        default_value="M350"
    )
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='false')

    camera_calibration_file_arg = DeclareLaunchArgument(
        "camera_calibration_file",
        default_value="cam_params.yaml"
    )

    poly_in_arg = DeclareLaunchArgument(
        "input_polygon",
        default_value=Topics.ESTIMATED_AUV_OBB_TOPIC
    )

    link_out_arg = DeclareLaunchArgument(
        "output_link",
        default_value=Links.ESTIMATED_AUV
    )

    obb_length_arg = DeclareLaunchArgument(
        "obb_length",
        default_value="1.3" 
    )

    obb_width_arg = DeclareLaunchArgument(
        "obb_width",
        default_value="0.16" 
    )

    cov_pose_out_arg = DeclareLaunchArgument(
        "output_cov_pose_topic",
        default_value='rviz/estimated_auv_pose'
    )

    robot_name = LaunchConfiguration("robot_name")
    use_sim_time = LaunchConfiguration("use_sim_time")
    camera_calibration_file = LaunchConfiguration("camera_calibration_file")
    poly_in = LaunchConfiguration("input_polygon")
    link_out = LaunchConfiguration("output_link")
    obb_length = LaunchConfiguration("obb_length")
    obb_width = LaunchConfiguration("obb_width")
    cov_pose_out = LaunchConfiguration("output_cov_pose_topic")

    params_file = PathJoinSubstitution([
        FindPackageShare("auv_state_estimation"),
        "config",
        "ekf_params.yaml"
    ])

    cam_calib_file = PathJoinSubstitution([
        FindPackageShare("auv_state_estimation"),
        "config",
        camera_calibration_file
    ])

    ekf_node = Node(
        package="auv_state_estimation",
        executable="ekf_node",
        namespace=robot_name,
        name="ekf_node",
        output="screen",
        parameters=[
            robot_name,
            params_file,
            {
                "use_sim_time": use_sim_time,
                "topics.input_polygon": poly_in,
                "frames.output_link": link_out,
                "camera_info": cam_calib_file,
                "obb.length_m": obb_length,
                "obb.width_m": obb_width,
                "topics.output_topic": cov_pose_out,

            }
        ],
    )

    return LaunchDescription([
        robot_name_arg,
        use_sim_time_arg,
        camera_calibration_file_arg,
        poly_in_arg,
        link_out_arg,
        obb_length_arg,
        obb_width_arg,
        cov_pose_out_arg,
        ekf_node
    ])

