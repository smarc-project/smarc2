from enum import Enum
import json

import numpy as np

from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry, Path
from std_msgs.msg import String, Header
from smarc_control_msgs.msg import WpMPC, TrajectoryMPC
#import rospy


class ActionComponent(Enum):
    GOAL = 0
    FEEDBACK = 2


class PathAction:
    def __init__(self):
        pass

    def decode(
        self,
        serialized_fmt: String,
        component: ActionComponent,
    ) -> Path:

        """Decodes action message from json to Python / ROS types.

        Note: this is done for the convenience of higher level operations and is not necessary.
        Args:
            serialized_fmt: string format from action
            component: The desired action component that is being parsed (defines how it will be parsed)

        Returns:
            Python and ROS native types for usage in client and server.
            
        """

        fmt_dict = json.loads(serialized_fmt.data)

        if component is ActionComponent.GOAL:
            path = TrajectoryMPC()
            for i in range(0,len(fmt_dict['path']['trajectory'])):
                wp = fmt_dict["path"]["trajectory"][str(i)]
                wp_mpc = WpMPC()
                wp_mpc.header.frame_id = wp["wp"]["frame_id"]
                wp_mpc.wp.pose.position.x = wp["wp"]["position"]["x"]
                wp_mpc.wp.pose.position.y = wp["wp"]["position"]["y"]
                wp_mpc.wp.pose.position.z = wp["wp"]["position"]["z"]
                wp_mpc.wp.pose.orientation.x = wp["wp"]["orientation"]["x"]
                wp_mpc.wp.pose.orientation.y = wp["wp"]["orientation"]["y"]
                wp_mpc.wp.pose.orientation.z = wp["wp"]["orientation"]["z"]
                wp_mpc.wp.pose.orientation.w = wp["wp"]["orientation"]["w"]
                wp_mpc.velocities.linear.x = wp["velocities"]["linear"]["x"]
                wp_mpc.velocities.linear.y = wp["velocities"]["linear"]["y"]
                wp_mpc.velocities.linear.z = wp["velocities"]["linear"]["z"]
                wp_mpc.velocities.angular.x = wp["velocities"]["angular"]["x"]
                wp_mpc.velocities.angular.y = wp["velocities"]["angular"]["y"]
                wp_mpc.velocities.angular.z = wp["velocities"]["angular"]["z"]

                # Actuator references are not tracked by the MPC cost — use
                # neutral defaults regardless of what the JSON carries.
                wp_mpc.nominal_control.vbs.value = 50.0
                wp_mpc.nominal_control.lcg.value = 50.0
                wp_mpc.nominal_control.rpms.thruster_1_rpm = 0
                wp_mpc.nominal_control.rpms.thruster_2_rpm = 0
                wp_mpc.nominal_control.thruster_angles.thruster_vertical_radians = 0.0
                wp_mpc.nominal_control.thruster_angles.thruster_horizontal_radians = 0.0

                path.trajectory.append(wp_mpc)

            return path

        elif component is ActionComponent.FEEDBACK:
            return float(fmt_dict["index"])


    def encode(
        self,
        path: TrajectoryMPC | float,
    ) -> String | None:

        """Encodes action message into string."""

        str_msg = String()
        path_dict = {}

        if isinstance(path, (TrajectoryMPC,)):
            path_dict["path"] = {}
            path_dict["path"]["header"] = ""
            path_dict["path"]["trajectory"] = {}
            for i in range(0,len(path.trajectory)):
                path_dict["path"]["trajectory"][i] = {}
                path_dict["path"]["trajectory"][i]["wp"] = {}
                path_dict["path"]["trajectory"][i]["wp"]["frame_id"] = path.trajectory[i].wp.header.frame_id
                path_dict["path"]["trajectory"][i]["wp"]["position"] = {}
                path_dict["path"]["trajectory"][i]["wp"]["position"]["x"] = path.trajectory[i].wp.pose.position.x
                path_dict["path"]["trajectory"][i]["wp"]["position"]["y"] = path.trajectory[i].wp.pose.position.y
                path_dict["path"]["trajectory"][i]["wp"]["position"]["z"] = path.trajectory[i].wp.pose.position.z
                path_dict["path"]["trajectory"][i]["wp"]["orientation"] = {}
                path_dict["path"]["trajectory"][i]["wp"]["orientation"]["x"] = path.trajectory[i].wp.pose.orientation.x
                path_dict["path"]["trajectory"][i]["wp"]["orientation"]["y"] = path.trajectory[i].wp.pose.orientation.y
                path_dict["path"]["trajectory"][i]["wp"]["orientation"]["z"] = path.trajectory[i].wp.pose.orientation.z
                path_dict["path"]["trajectory"][i]["wp"]["orientation"]["w"] = path.trajectory[i].wp.pose.orientation.w
                path_dict["path"]["trajectory"][i]["velocities"] = {}
                path_dict["path"]["trajectory"][i]["velocities"]["linear"] = {}
                path_dict["path"]["trajectory"][i]["velocities"]["linear"]["x"] = path.trajectory[i].velocities.linear.x
                path_dict["path"]["trajectory"][i]["velocities"]["linear"]["y"] = path.trajectory[i].velocities.linear.y
                path_dict["path"]["trajectory"][i]["velocities"]["linear"]["z"] = path.trajectory[i].velocities.linear.z
                path_dict["path"]["trajectory"][i]["velocities"]["angular"] = {}
                path_dict["path"]["trajectory"][i]["velocities"]["angular"]["x"] = path.trajectory[i].velocities.angular.x
                path_dict["path"]["trajectory"][i]["velocities"]["angular"]["y"] = path.trajectory[i].velocities.angular.y
                path_dict["path"]["trajectory"][i]["velocities"]["angular"]["z"] = path.trajectory[i].velocities.angular.z
                path_dict["path"]["trajectory"][i]["nominal_control"] = {}
                path_dict["path"]["trajectory"][i]["nominal_control"]["rpms"] = {}
                path_dict["path"]["trajectory"][i]["nominal_control"]["rpms"]["thruster_1_rpm"] = path.trajectory[i].nominal_control.rpms.thruster_1_rpm
                path_dict["path"]["trajectory"][i]["nominal_control"]["rpms"]["thruster_2_rpm"] = path.trajectory[i].nominal_control.rpms.thruster_2_rpm
                path_dict["path"]["trajectory"][i]["nominal_control"]["thruster_angles"] = {}
                path_dict["path"]["trajectory"][i]["nominal_control"]["thruster_angles"]["thruster_vertical_radians"] = path.trajectory[i].nominal_control.thruster_angles.thruster_vertical_radians
                path_dict["path"]["trajectory"][i]["nominal_control"]["thruster_angles"]["thruster_horizontal_radians"] = path.trajectory[i].nominal_control.thruster_angles.thruster_horizontal_radians
                path_dict["path"]["trajectory"][i]["nominal_control"]["vbs"] = path.trajectory[i].nominal_control.vbs.value
                path_dict["path"]["trajectory"][i]["nominal_control"]["lcg"] = path.trajectory[i].nominal_control.lcg.value


        elif isinstance(path, (int, float,)):
            path_dict["index"] = path 
        else:
            return None

        str_val = json.dumps(path_dict)
        str_msg.data = str_val
        return str_msg

