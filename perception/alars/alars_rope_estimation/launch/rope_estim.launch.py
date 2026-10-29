from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    robot_name_arg = DeclareLaunchArgument(
        "robot_name",
        default_value="M350"
    )
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='false')

    robot_name = LaunchConfiguration("robot_name")
    use_sim_time = LaunchConfiguration("use_sim_time")

    params_file = PathJoinSubstitution([
        FindPackageShare("alars_rope_estimation"),
        "config",
        "rope_estim_params.yaml"
    ])

    robot_frame_name = "sim_M350" #TODO: resolve with if else based on use sim time

    rope_estim_node = Node(
        package="alars_rope_estimation",
        executable="rope_estimation_node",
        namespace=robot_name,
        name="rope_estimation_node",
        output="screen",
        parameters=[
            params_file,
            {
                "robot_name": robot_frame_name,
                "use_sim_time": use_sim_time,
            }
        ]
    )      
    return LaunchDescription([
        robot_name_arg,
        use_sim_time_arg,
        rope_estim_node
    ])

