from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from lolo_msgs.msg import Topics as LoloTopics
from smarc_msgs.msg import Topics as SmarcTopics
from smarc_control_msgs.msg import Topics as ControlTopics


def generate_launch_description():
    robot_ns = LaunchConfiguration('robot_name')

    robot_ns_launch_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='lolo'
    )

    odom_splitter_node = Node(
        package='odom_splitter',
        namespace=robot_ns,
        executable='odom_splitter',
        name='odom_splitter',
        parameters=[{"robot_name": robot_ns
        }]
    )

    # TODO: Put all PID values in a config file and read from there.

    yaw_pid_node = Node(
        package='lolo_controllers',
        namespace=robot_ns,
        executable='pid',
        name="yaw_pid",
        parameters=[{"robot_name": robot_ns,
                     "p_gain": 0.1,
                     "i_gain": 0.0,
                     "d_gain": 0.0,
                     "output_limit": 0.05,
                     "meassurement_topic": ControlTopics.CONTROL_YAW_TOPIC,
                     "setpoint_topic": LoloTopics.YAW_SETPOINT,
                     "output_topic": LoloTopics.YAW_RATE_SETPOINT,
                     "controller_type": 'yaw'
                     }]
    )

    yawrate_pid_node = Node(
        package='lolo_controllers',
        namespace=robot_ns,
        executable='pid',
        name="yawrate_pid",
        parameters=[{"robot_name": robot_ns,
                     "p_gain": 40.0,
                     "i_gain": 0.0,
                     "d_gain": 0.0,
                     "output_limit": 0.7,
                     "meassurement_topic": ControlTopics.CONTROL_YAW_RATE_TOPIC,
                     "setpoint_topic": LoloTopics.YAW_RATE_SETPOINT,
                     "output_topic": LoloTopics.YAW_ACTUATION
                     }]
    )

    roll_pid_node = Node(
        package='lolo_controllers',
        namespace=robot_ns,
        executable='pid',
        name="roll_pid",
        parameters=[{"robot_name": robot_ns,
                     "p_gain": 1.0,
                     "i_gain": 0.0,
                     "d_gain": 0.0,
                     "output_limit": 0.1,
                     "meassurement_topic": ControlTopics.CONTROL_ROLL_TOPIC,
                     "setpoint_topic": LoloTopics.ROLL_SETPOINT,
                     "output_topic": LoloTopics.ROLL_RATE_SETPOINT
                     }]
    )

    rollrate_pid_node = Node(
        package='lolo_controllers',
        namespace=robot_ns,
        executable='pid',
        name="rollrate_pid",
        parameters=[{"robot_name": robot_ns,
                     "p_gain": 2.0,
                     "i_gain": 0.0,
                     "d_gain": 0.0,
                     "output_limit": 0.35,
                     "meassurement_topic": ControlTopics.CONTROL_ROLL_RATE_TOPIC,
                     "setpoint_topic": LoloTopics.ROLL_RATE_SETPOINT,
                     "output_topic": LoloTopics.ROLL_ACTUATION
                     }]
    )

    depth_pid_node = Node(
        package='lolo_controllers',
        namespace=robot_ns,
        executable='pid',
        name="depth_pid",
        parameters=[{"robot_name": robot_ns,
                     "p_gain": 0.1,
                     "i_gain": 0.0,
                     "d_gain": 0.0,
                     "output_limit": 0.4,
                     "meassurement_topic": SmarcTopics.DEPTH_TOPIC,
                     "setpoint_topic": LoloTopics.DEPTH_SETPOINT,
                     "output_topic": LoloTopics.PITCH_SETPOINT
                     }]
    )

    pitch_pid_node = Node(
        package='lolo_controllers',
        namespace=robot_ns,
        executable='pid',
        name="pitch_pid",
        parameters=[{"robot_name": robot_ns,
                     "p_gain": 0.5,
                     "i_gain": 0.1,
                     "d_gain": 0.0,
                     "output_limit": 0.1,
                     "meassurement_topic": ControlTopics.CONTROL_PITCH_TOPIC,
                     "setpoint_topic": LoloTopics.PITCH_SETPOINT,
                     "output_topic": LoloTopics.PITCH_RATE_SETPOINT
                     }]
    )

    pitchrate_pid_node = Node(
        package='lolo_controllers',
        namespace=robot_ns,
        executable='pid',
        name="pitchrate_pid",
        parameters=[{"robot_name": robot_ns,
                     "p_gain": 8.0,
                     "i_gain": 0.0,
                     "d_gain": 0.0,
                     "output_limit": 0.5,
                     "meassurement_topic": ControlTopics.CONTROL_PITCH_RATE_TOPIC,
                     "setpoint_topic": LoloTopics.PITCH_RATE_SETPOINT,
                     "output_topic": LoloTopics.PITCH_ACTUATION
                     }]
    )

    mixer_node = Node(
        package='lolo_controllers',
        namespace=robot_ns,
        executable='mixer',
        name='control_mixer',
        parameters=[{"robot_name": robot_ns}]
    )

    return LaunchDescription([
        robot_ns_launch_arg, odom_splitter_node,
        yaw_pid_node, yawrate_pid_node,
        roll_pid_node, rollrate_pid_node,
        pitch_pid_node, pitchrate_pid_node,
        depth_pid_node, mixer_node
    ])
