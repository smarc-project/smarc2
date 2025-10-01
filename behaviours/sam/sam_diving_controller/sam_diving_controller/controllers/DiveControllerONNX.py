import numpy as np
from geometry_msgs.msg import PoseStamped, Pose
from nav_msgs.msg import Odometry
from sam_diving_controller.controllers.DiveControllerInterface import DiveControllerInterface
from sam_diving_controller.controllers.ONNXManager import ONNXManager

from behaviours.sam.sam_diving_controller.sam_diving_controller import TransformUtils
from behaviours.sam.sam_diving_controller.sam_diving_controller.IDivePub import MissionStates, ActuatorStates


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
        self.waypoint = None

        self.onnx_manager = ONNXManager("DR_temp")

        self._loginfo("ONNX Dive Controller created")

    def update(self):
        mission_state = self._dive_sub.get_mission_state()

        if mission_state == MissionStates.RECEIVED or mission_state == MissionStates.COMPLETED or mission_state == MissionStates.CANCELLED:
            self._loginfo_once(f"Mission not running. State: {mission_state}")
            self._set_actuators_neutral()
            return

        # Engage actuators in case they were off before.
        self._dive_pub.set_actuator_states(ActuatorStates.ENGAGED, "DP")

        waypoint_mocap_frd = self._get_waypoint()
        if waypoint_mocap_frd is None:
            return

        # Get the current states
        current_state_in_mocap = self._dive_sub.get_states_in_mocap()

        if current_state_in_mocap is None:
            self._loginfo(f"No state available yet.")
            return

        odometry_mocap_ned = self.convert_enu_to_ned(current_state_in_mocap, convert_state=True)
        odometry_body_ned = self.convert_to_body(current_state_in_mocap, odometry_mocap_ned)
        waypoint_body_ned = self.convert_to_body(current_state_in_mocap, waypoint_mocap_frd)
        control_input = self._dive_sub.get_control_input()

        onnx_input = self.onnx_manager.prepare_state((odometry_mocap_ned,
                                                      odometry_body_ned,
                                                      waypoint_body_ned,
                                                      control_input))
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

    def set_publishers(self, outputs):
        """
        Set the corresponding publishers for the actuators and convenience topics
        """
        u_rpm1 = outputs[0]
        u_rpm2 = outputs[0]
        u_stern = outputs[1]
        u_rudder = outputs[2]
        u_vbs = outputs[3]
        u_lcg = outputs[4]

        # Publish the control input
        self._dive_pub.set_vbs(u_vbs)
        self._dive_pub.set_lcg(u_lcg)
        self._dive_pub.set_thrust_vector(u_rudder, u_stern)
        self._dive_pub.set_rpm(u_rpm1, u_rpm2)

    def _get_waypoint(self):
        if not self._dive_sub.has_waypoint():
            return None

        waypoint_in_mocap = self._dive_sub.get_waypoint()
        # FIXME: This might be useless.
        if waypoint_in_mocap is None:
            self._loginfo(f"waypoint_in_mocap is None")
            return False

        odometry = self.convert_wp_to_odometry(waypoint_in_mocap)
        return odometry

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

    def convert_to_body(self, mocap_odometry: Odometry, odometry: Odometry):
        odom = Odometry()

        odom.child_frame_id = ""
        odom.header.frame_id = "base_link"
        odom.header.stamp = self._node.get_clock().now().to_msg()

        odom.pose.pose.position = TransformUtils.transform_point_to_child(mocap_odometry, odometry.pose.pose.position).point
        odom.pose.pose.orientation = TransformUtils.rotate_quat_to_child(mocap_odometry, odometry.pose.pose.orientation)

        odom.twist.twist.linear = TransformUtils.rotate_vector_to_child(mocap_odometry, odometry.twist.twist.linear)
        odom.twist.twist.angular = TransformUtils.rotate_vector_to_child(mocap_odometry, odometry.twist.twist.angular)

        return odom
