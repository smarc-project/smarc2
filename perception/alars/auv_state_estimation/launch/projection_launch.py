from dji_msgs.msg import Topics
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

    namespace = LaunchConfiguration("namespace")
    use_sim_time = LaunchConfiguration("use_sim_time")

    params_file = PathJoinSubstitution([
        FindPackageShare("auv_state_estimation"),
        "config",
        "params.yaml"
    ])

    def project_node(name, topic_in, topic_out):
        return Node(
            package="auv_state_estimation",
            executable="projection",
            namespace=namespace,
            name=name,
            output="screen",
            parameters=[
                params_file,
                {
                    "use_sim_time": use_sim_time,
                    "topics.input_polygon": topic_in,
                    "topics.output_projected_polygon": topic_out
                }
            ],
        )

    return LaunchDescription([
        namespace_arg,
        use_sim_time_arg,
        project_node("projection_auv_obb", Topics.ESTIMATED_AUV_OBB_TOPIC, Topics.PROJECTED_AUV_OBB_TOPIC),
        project_node("projection_auv_head", Topics.ESTIMATED_AUV_HEAD_TOPIC, Topics.PROJECTED_AUV_HEAD_TOPIC),
        project_node("projection_buoy_obb", Topics.ESTIMATED_BUOY_OBB_TOPIC, Topics.PROJECTED_BUOY_OBB_TOPIC),
    ])

