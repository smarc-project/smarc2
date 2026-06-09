from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from smarc_msgs.msg import Topics as SmarcTopics
from smarc_control_msgs.msg import Topics as ControlTopics


def generate_launch_description():
    robot_ns = LaunchConfiguration('robot_name')

    update_rate = LaunchConfiguration('update_rate')  #, 10)
    max_steering_output = LaunchConfiguration('max_steering_output')  #, 40.0) 
    max_integral = LaunchConfiguration('max_integral')  #, 10.0) 
    max_speed = LaunchConfiguration('max_speed')    #, 6) #m/s ~12 knots
    closed_loop_p_gain = LaunchConfiguration('closed_loop_p_gain')   #, 0.0)
    closed_loop_i_gain = LaunchConfiguration('closed_loop_i_gain')   #, 0.0)
    closed_loop_d_gain = LaunchConfiguration('closed_loop_d_gain')   #, 0.0)

    robot_ns_launch_arg = DeclareLaunchArgument('robot_name', default_value='evolo')


    update_rate_arg = DeclareLaunchArgument('update_rate', default_value='10')
    max_steering_output_arg = DeclareLaunchArgument('max_steering_output', default_value='40.0')
    max_integral_arg = DeclareLaunchArgument('max_integral', default_value='10.0')
    max_speed_arg = DeclareLaunchArgument('max_speed', default_value='6')
    closed_loop_p_gain_arg = DeclareLaunchArgument('closed_loop_p_gain', default_value='1.0')
    closed_loop_i_gain_arg = DeclareLaunchArgument('closed_loop_i_gain', default_value='0.0')
    closed_loop_d_gain_arg = DeclareLaunchArgument('closed_loop_d_gain', default_value='0.0')


    yaw_control = Node(
        package='evolo_controllers',
        namespace=robot_ns,
        executable='controller',
        name='controller',
        parameters=[{
            "robot_name": robot_ns,
            "update_rate" : update_rate,
            "max_steering_output" : max_steering_output,
            "max_integral" : max_integral,
            "max_speed" : max_speed,
            "closed_loop_p_gain" : closed_loop_p_gain,
            "closed_loop_i_gain" : closed_loop_i_gain,
            "closed_loop_d_gain" : closed_loop_d_gain,
        }]
    )

    return LaunchDescription([
        robot_ns_launch_arg,
        update_rate_arg,
        max_steering_output_arg,
        max_integral_arg,
        max_speed_arg,
        closed_loop_p_gain_arg,
        closed_loop_i_gain_arg,
        closed_loop_d_gain_arg,
        yaw_control
    ])
