from dji_msgs.msg import PsdkTopics
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

    robot_name = LaunchConfiguration("robot_name")
    use_sim_time = LaunchConfiguration("use_sim_time")

    take_control_action = Node(
        package="smarc_action_base",
        executable="trigger_service_action_server",
        namespace=robot_name,
        name="take_control_action_server",
        output="screen",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "service_name": PsdkTopics.TAKE_CONTROL_SRV,
                "task_name": "alars_take_control"
            }
        ],
    )

    release_control_action = Node(
        package="smarc_action_base",
        executable="trigger_service_action_server",
        namespace=robot_name,
        name="release_control_action_server",
        output="screen",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "service_name": PsdkTopics.RELEASE_CONTROL_SRV,
                "task_name": "alars_release_control"
            }
        ],
    )

    takeoff_action = Node(
        package="smarc_action_base",
        executable="trigger_service_action_server",
        namespace=robot_name,
        name="takeoff_action_server",
        output="screen",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "service_name": PsdkTopics.TAKEOFF_SRV,
                "task_name": "alars_takeoff"
            }
        ],
    )

    land_action = Node(
        package="smarc_action_base",
        executable="trigger_service_action_server",
        namespace=robot_name,
        name="land_action_server",
        output="screen",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "service_name": PsdkTopics.LAND_SRV,
                "task_name": "alars_land"
            }
        ],
    )


    return LaunchDescription([
        robot_name_arg,
        use_sim_time_arg,
        take_control_action,
        release_control_action,
        takeoff_action,
        land_action
    ])