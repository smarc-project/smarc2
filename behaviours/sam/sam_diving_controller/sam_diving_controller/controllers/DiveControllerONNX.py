from nav_msgs.msg import Odometry
import numpy as np

from sam_diving_controller.DiveController import DiveControllerInterface
from sam_diving_controller.controllers.ONNXManager import ONNXManager
from scipy.spatial.transform import Rotation as R

from smarc_control_msgs.msg import ControlError, ControlInput, ControlReference, ControlState
from geometry_msgs.msg import PoseStamped, Pose

from behaviours.sam.sam_diving_controller.sam_diving_controller.IDivePub import MissionStates, ActuatorStates

import time


class DiveControllerONNX(DiveControllerInterface):

    def __init__(self, node, dive_pub, dive_sub, param, rate=0.2):
        super().__init__(node, dive_pub, dive_sub, param, rate)

        # Convenience Topics
        self._current_state = None
        self._current_state_in_odom = None
        self._current_state_in_mocap = None
        self._current_control = None
        self._ref = None
        self._error = None
        self._input = None
        self.waypoint = None

        self.onnx_manager = ONNXManager("DR_temp")

        self._loginfo("ONNX Dive Controller created")

    def update(self):
        mission_state = self._dive_sub.get_mission_state()

        if mission_state != MissionStates.RUNNING:
            self._loginfo_once(f"Mission not running. State: {mission_state}")
            self._set_actuators_neutral()
            return

        # Engage actuators in case they were off before.
        self._dive_pub.set_actuator_states(ActuatorStates.ENGAGED, "DP")

        waypoint = self._get_waypoint()
        if waypoint is None:
            return

        # Get the current states
        current_state_in_odom = self._dive_sub.get_states()
        current_state_in_mocap = self._dive_sub.get_states_in_mocap()

        if current_state_in_odom is None:
            self._loginfo(f"No state available yet.")
            return

        mocap_ned = self.convert_enu_to_ned(current_state_in_mocap, convert_state=True)
        control_input = self._dive_sub.get_control_input()

        onnx_input = self.onnx_manager.prepare_state((mocap_ned, control_input, waypoint))
        control_output = self.onnx_manager.get_control_scaled(onnx_input)

        self.set_publishers(control_output)

    def convert_enu_to_ned(self, enu_msg, convert_state=True):
        """
        If convert_state, it converts an odometry message from ENU to NED

        """
        ned_odometry = Odometry()
        ned_odometry.header.frame_id = "/mocap"  # state_msg.header.frame_id# + "_conv"
        ned_odometry.header.stamp = enu_msg.header.stamp
        if convert_state:
            ned_odometry.pose.pose.position.x = enu_msg.pose.pose.position.y
            ned_odometry.pose.pose.position.y = enu_msg.pose.pose.position.x
            ned_odometry.pose.pose.position.z = -enu_msg.pose.pose.position.z
            ned_odometry.pose.pose.orientation = enu_msg.pose.pose.orientation

            quat = self.quat_enu_to_ned([enu_msg.pose.pose.orientation.x,
                                         enu_msg.pose.pose.orientation.y,
                                         enu_msg.pose.pose.orientation.z,
                                         enu_msg.pose.pose.orientation.w])

            ned_odometry.pose.pose.orientation.x = quat[0]
            ned_odometry.pose.pose.orientation.y = quat[1]
            ned_odometry.pose.pose.orientation.z = quat[2]
            ned_odometry.pose.pose.orientation.w = quat[3]

            ned_odometry.twist.twist.linear.x = enu_msg.twist.twist.linear.y
            ned_odometry.twist.twist.linear.y = enu_msg.twist.twist.linear.x
            ned_odometry.twist.twist.linear.z = -enu_msg.twist.twist.linear.z
            ned_odometry.twist.twist.angular.x = enu_msg.twist.twist.angular.y
            ned_odometry.twist.twist.angular.y = enu_msg.twist.twist.angular.x
            ned_odometry.twist.twist.angular.z = -enu_msg.twist.twist.angular.z

        else:
            ned_odometry = enu_msg

        return ned_odometry

    def quat_enu_to_ned(self, quat_enu):
        """
        Transform quaternion from ENU to NED.
        """
        q = quat_enu

        q_ned = 1 / np.sqrt(2) * np.array([q[0] + q[3], q[1] + q[2], q[1] - q[2], q[0] - q[3]])
        q_ned /= np.linalg.norm(q_ned)

        return q_ned

    def convert_wp_to_odometry(self, wp_msg):
        """
        Returns waypoint as Odometry
        """
        odom_wp = Odometry()

        if isinstance(wp_msg, PoseStamped):
            odom_wp.header.frame_id = wp_msg.header.frame_id
            odom_wp.header.stamp = wp_msg.header.stamp

            odom_wp.pose.pose = wp_msg.pose

        elif isinstance(wp_msg, Pose):
            odom_wp.header.frame_id = '/mocap'
            odom_wp.header.stamp = self._node.get_clock().now().to_msg()
            odom_wp.pose.pose.position = wp_msg.position
            odom_wp.pose.pose.orientation = wp_msg.orientation

        elif isinstance(wp_msg, Odometry):
            odom_wp = wp_msg

        else:
            return None

        return odom_wp


    def set_publishers(self, mpc_solution):
        """
        Set the corresponding publishers for the actuators and convenience topics
        """
        u_rpm1 = mpc_solution[0]
        u_rpm2 = mpc_solution[0]
        u_stern = mpc_solution[1]
        u_rudder = mpc_solution[2]
        u_vbs = mpc_solution[3]
        u_lcg = mpc_solution[4]

        # Publish the control input
        self._dive_pub.set_vbs(u_vbs)
        self._dive_pub.set_lcg(u_lcg)
        self._dive_pub.set_thrust_vector(u_rudder, u_stern)
        self._dive_pub.set_rpm(u_rpm1, u_rpm2)

        # Set control input (For convenience topics)
        self._input = ControlInput()
        self._input.vbs = u_vbs
        self._input.lcg = u_lcg
        self._input.thrustervertical = u_stern
        self._input.thrusterhorizontal = u_rudder
        self._input.thrusterrpm = float(u_rpm1)

    def _get_waypoint(self):
        if not self._dive_sub.has_waypoint():
            return None

        waypoint_in_mocap = self._dive_sub.get_waypoint()
        # FIXME: This might be useless.
        if waypoint_in_mocap is None:
            self._loginfo(f"waypoint_in_mocap is None")
            return False

        odometry = self.convert_wp_to_odometry(waypoint_in_mocap)
        # TODO: Convert waypoint to body frame
        return odometry
