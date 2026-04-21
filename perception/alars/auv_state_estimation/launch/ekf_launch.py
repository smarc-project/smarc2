from dji_msgs.msg import Topics, Links
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    namespace_arg = DeclareLaunchArgument(
        "namespace",
        default_value="M350"
    )
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='false')

    camera_calibration_file_arg = DeclareLaunchArgument(
        "camera_calibration_file",
        default_value="cam_params.yaml"
    )

    namespace = LaunchConfiguration("namespace")
    use_sim_time = LaunchConfiguration("use_sim_time")
    camera_calibration_file = LaunchConfiguration("camera_calibration_file")

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

    def ekf_node(name, topic_in, link_out, output_topic, obb_length, obb_width):
        return Node(
            package="auv_state_estimation",
            executable="ekf_node",
            namespace=namespace,
            name=name,
            output="screen",
            parameters=[
                params_file,
                {
                    "use_sim_time": use_sim_time,
                    "topics.input_polygon": topic_in,
                    "frames.output_link": link_out,
                    "camera_info": cam_calib_file,
                    "obb.length_m": obb_length,
                    "obb.width_m": obb_width,
                    "topics.output_topic": output_topic,
                }
            ],
        )

    return LaunchDescription([
        namespace_arg,
        use_sim_time_arg,
        camera_calibration_file_arg,
        ekf_node("ekf_auv", topic_in=Topics.ESTIMATED_AUV_OBB_TOPIC, link_out=Links.ESTIMATED_AUV, output_topic="rviz/estimated_auv_pose", obb_length=1.3, obb_width=0.16),
        ekf_node("ekf_buoy", topic_in=Topics.ESTIMATED_BUOY_OBB_TOPIC, link_out=Links.ESTIMATED_BUOY, output_topic="rviz/estimated_buoy_pose", obb_length=0.4, obb_width=0.16),
    ])

