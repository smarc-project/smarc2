from nav_msgs.msg import Odometry
import numpy as np
from pathlib import Path

from sam_diving_controller.DiveController import DiveControllerInterface
from sam_diving_controller.controllers.ONNXManager import ONNXManager
from tf_transformations import euler_from_quaternion
from scipy.spatial.transform import Rotation as R

from smarc_control_msgs.msg import ControlError, ControlInput, ControlReference, ControlState
from geometry_msgs.msg import PoseStamped, Pose

# from .ParamUtils import DivingModelParam
from behaviours.sam.sam_diving_controller.sam_diving_controller.IDivePub import MissionStates, ActuatorStates

import time


class DiveControllerMPC(DiveControllerInterface):

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

        # Declare counter
        self.i = 0
        self.traj_len = 0

        self.onnx_manager = ONNXManager("DR_temp")

        # NOTE: This needs to happen in the update function with some check
        # before proceeding. Otherwise, you don't get the right data from the
        # dive sub node, because it's not yet spinning and thus doesn't get the
        # topics yet.
        self._initialized = False

        # FIXME: This should change. We don't want to change code when
        # switching between trajectories and waypoints
        self.ref_is_traj = False  # Flag to indicate if the reference is a trajectory or not
        self._loginfo("Dive Controller created")

        self._acados_status = {0: "ACADOS_SUCCESS",
                               1: "ACADOS_NAN_DETECTED",
                               2: "ACADOS_MAXITER",
                               3: "ACADOS_MINSTEP",
                               4: "ACADOS_QP_FAILURE",
                               5: "ACADOS_READY",
                               6: "ACADOS_UNBOUNDED"}

    def update(self):
        mission_state = self._dive_sub.get_mission_state()
        # if mission_state == MissionStates.RECEIVED:
        #    self._loginfo_once("Mission Received")
        #    self._set_actuators_neutral()
        #    return

        # if mission_state == MissionStates.COMPLETED:
        #    self._loginfo_once("Mission Complete")
        #    self._set_actuators_neutral()
        #    return

        # if mission_state == MissionStates.CANCELLED:
        #    self._loginfo_once("Mission Cancelled")
        #    self._set_actuators_neutral()
        #    return

        if mission_state != MissionStates.RUNNING:
            self._loginfo_once("Mission not running")
            self._set_actuators_neutral()
            return

        # Engage actuators in case they were off before.
        self._dive_pub.set_actuator_states(ActuatorStates.ENGAGED, "DP")

        if not self.get_reference():
            return

        # Get the current states
        convert_state = True  # Flag to convert states
        self._current_state_in_odom = self._dive_sub.get_states()
        self._current_state_in_mocap = self._dive_sub.get_states_in_mocap()

        if self._current_state_in_odom is None:
            self._loginfo(f"No state available yet.")
            return

        self._current_state = self.convert_enu_to_ned(self._current_state_in_odom, convert_state)
        self._current_control = self._dive_sub.get_control_input()

        if not self._initialized:
            self.initialize_mpc()

        x_current = self.get_state_array(self._current_state,
                                         self._current_control,
                                         is_init_state=self._initialized,
                                         is_trajectory=self.ref_is_traj)
        self.get_current_ref_array()

        # Update reference vector
        # NOTE: we use p bc. we have a custom cost function.
        for stage in range(self.N_horizon):
            if self.ref.shape[0] < self.N_horizon and self.ref.shape[0] != 0:
                self.ocp_solver.set(stage, "p", self.ref[self.ref.shape[0] - 1, :])
            else:
                self.ocp_solver.set(stage, "p", self.ref[stage, :])

        # FIXME: We also have a custom cost function for the terminal cost. So this might collide with it?
        # Set the terminal state reference to the value at N_horizon
        self.ocp_solver.set(self.N_horizon, "yref", self.ref[-1, :self.nx])

        # Set current state
        self.ocp_solver.set(0, "lbx", x_current)
        self.ocp_solver.set(0, "ubx", x_current)

        # solve ocp and get next control input
        start_time = time.time()
        status = self.ocp_solver.solve()
        end_time = time.time()

        # simulate system:
        # NOTE: May be possible to use get(0, "x") to acquire the actual control input.
        self.simU = self.ocp_solver.get(0, "u")

        self.pred_mpc = []
        for j in range(self.N_horizon + 1):
            self.pred_mpc.append(self.ocp_solver.get(j, 'x'))

        # The integrator of the control signal is needed, since u is the control derivative.
        mpc_solution = self.integrator.simulate(x=x_current, u=self.simU)

        self.set_publishers(mpc_solution)

        # FIXME: Remove all the print statements here. They only should appear in the convenience node
        s = f"\nNMPC INFO\n"  # {self._dive_sub.current_idx}/{self.traj_len}:\n"
        s += f"NMPC solver status: {self._acados_status[status]}\n"
        s += f"NMPC solve time: {(end_time - start_time) * 1000:.1f} ms\n"
        s += f"Traj. index: {self._dive_sub.current_idx}/{self.traj_len}:\n" if self.ref_is_traj else f""

        s += f"\n ----\n"
        s += f"mocap: x: {self._current_state_in_mocap.pose.pose.position.x:.3f}"
        s += f" y: {self._current_state_in_mocap.pose.pose.position.y:.3f}"
        s += f" z: {self._current_state_in_mocap.pose.pose.position.z:.3f}\n"
        s += f"odom: x: {self._current_state_in_odom.pose.pose.position.x:.3f}"
        s += f" y: {self._current_state_in_odom.pose.pose.position.y:.3f}"
        s += f" z: {self._current_state_in_odom.pose.pose.position.z:.3f}\n"
        s += f"current: x: {self._current_state.pose.pose.position.x:.3f}"
        s += f" y: {self._current_state.pose.pose.position.y:.3f}"
        s += f" z: {self._current_state.pose.pose.position.z:.3f}\n"

        self._loginfo(s)

        # Increment trajectory window index
        self.i += 1
        self._dive_sub.set_current_idx(self.i)

        return

    def get_reference(self):
        # TODO: refactor this if-statement as function.
        if self.ref_is_traj and not self._initialized:
            self.trajectory = self._dive_sub.get_path()

            if self.trajectory is None:
                self._loginfo_once("No trajectory received")
                return False
            else:
                self.trajectory = np.array(self.trajectory)  # Convert/make sure it is a numpy array

            # Declare duration of sim.
            self.traj_len = self.trajectory.shape[0]

            # Augment the trajectory and control input reference
            Uref = np.zeros(
                (self.trajectory.shape[0], self.nu))  # Derivative reference - set to 0 to penalize large rate of change
            self.trajectory = np.concatenate((self.trajectory, Uref), axis=1)


        elif not self.ref_is_traj:

            if not self._dive_sub.has_waypoint():
                self._loginfo(f"No waypoint available")
                return False

            # Get Waypoint information
            waypoint_in_mocap = self._dive_sub.get_waypoint()

            # FIXME: This might be useless.
            if waypoint_in_mocap is None:
                self._loginfo(f"waypoint_in_mocap is None")
                return False

            self.waypoint = self.convert_wp_to_odometry(waypoint_in_mocap)

            self.wp_array = self.get_wp_array(self.waypoint)

        return True

    #    def convert_flu_to_frd(self, flu_msg, convert_state=True):
    #        """
    #        If convert_state, it converts an odometry message from FLU to FRD
    #
    #        """
    #        frd_odometry = Odometry()
    #        frd_odometry.header.frame_id = flu_msg.header.frame_id
    #        frd_odometry.header.stamp = flu_msg.header.stamp
    #        if convert_state:
    #            frd_odometry.pose.pose.position.x = flu_msg.pose.pose.position.x
    #            frd_odometry.pose.pose.position.y = flu_msg.pose.pose.position.y
    #            frd_odometry.pose.pose.position.z = flu_msg.pose.pose.position.z
    #            quat = self.quat_flu_to_frd([flu_msg.pose.pose.orientation.x,
    #                                      flu_msg.pose.pose.orientation.y,
    #                                      flu_msg.pose.pose.orientation.z,
    #                                      flu_msg.pose.pose.orientation.w])
    #            frd_odometry.pose.pose.orientation.x = quat[0]
    #            frd_odometry.pose.pose.orientation.y = quat[1]
    #            frd_odometry.pose.pose.orientation.z = quat[2]
    #            frd_odometry.pose.pose.orientation.w = quat[3]
    #
    #            frd_odometry.twist.twist.linear.x = flu_msg.twist.twist.linear.x
    #            frd_odometry.twist.twist.linear.y = flu_msg.twist.twist.linear.y
    #            frd_odometry.twist.twist.linear.z = flu_msg.twist.twist.linear.z
    #            frd_odometry.twist.twist.angular.x = flu_msg.twist.twist.angular.x
    #            frd_odometry.twist.twist.angular.y = flu_msg.twist.twist.angular.y
    #            frd_odometry.twist.twist.angular.z = flu_msg.twist.twist.angular.z
    #
    #        else:
    #            frd_odometry = flu_msg
    #
    #        return frd_odometry

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

    def get_state_array(self, state_msg, control_msg,
                        is_init_state=False,
                        is_trajectory=False):
        """
        Merges states and controls into numpy array and returns the state of
        the controller as the state vector x (numpy array)

        convert_state: state_msg is in ENU, x will be in NED
        """
        x = np.zeros(19)

        x[0] = state_msg.pose.pose.position.x
        x[1] = state_msg.pose.pose.position.y
        x[2] = state_msg.pose.pose.position.z
        x[3:7] = [state_msg.pose.pose.orientation.x,
                  state_msg.pose.pose.orientation.y,
                  state_msg.pose.pose.orientation.z,
                  state_msg.pose.pose.orientation.w]
        x[7] = state_msg.twist.twist.linear.x
        x[8] = state_msg.twist.twist.linear.y
        x[9] = state_msg.twist.twist.linear.z
        x[10] = state_msg.twist.twist.angular.x
        x[11] = state_msg.twist.twist.angular.y
        x[12] = state_msg.twist.twist.angular.z
        x[13] = control_msg['vbs']
        x[14] = control_msg['lcg']
        x[15] = control_msg['stern']
        x[16] = control_msg['rudder']
        x[17] = control_msg['rpm1']
        x[18] = control_msg['rpm2']

        # Due to numerical reasons, we add a small noise to the rpms in
        # waypoint following mode
        if is_init_state:
            if is_trajectory:
                x[17] = control_msg['rpm1']
                x[18] = control_msg['rpm2']
            else:
                x[17] = 1e-6
                x[18] = 1e-6

        return x

    def get_wp_array(self, waypoint):

        ref = np.zeros(self.nx + self.nu)

        ref[0] = waypoint.pose.pose.position.x
        ref[1] = waypoint.pose.pose.position.y
        ref[2] = waypoint.pose.pose.position.z
        ref[3] = waypoint.pose.pose.orientation.w
        ref[4] = waypoint.pose.pose.orientation.x
        ref[5] = waypoint.pose.pose.orientation.y
        ref[6] = waypoint.pose.pose.orientation.z

        # Neutral actuator reference for VBS and LCG. Rest is 0
        ref[13] = 50
        ref[14] = 50

        return ref

    #    def quat_flu_to_frd(self, quat_enu):
    #
    #        rot = R.from_euler('x', 180, degrees=True)
    #        r_enu = R.from_quat(quat_enu)  # Convert ENU quaternion to rotation object
    #        r_ned = rot.as_matrix() @ r_enu.as_matrix()
    #        quat_ned = R.from_matrix(r_ned).as_quat()  # Convert back to quaternion with scalar first
    #        quat_ned_right_order = np.array([quat_ned[3], # w
    #                                        quat_ned[0],  # x
    #                                        quat_ned[1],  # y
    #                                        quat_ned[2]   # z
    #                                        ])
    #        return quat_ned_right_order

    def initialize_mpc(self):
        """
        Set the initial state for the MPC
        """
        x0 = self.get_state_array(self._current_state,
                                  self._current_control,
                                  is_init_state=not self._initialized,
                                  is_trajectory=self.ref_is_traj)

        # Initialize the state and control vector
        for stage in range(self.N_horizon + 1):
            self.ocp_solver.set(stage, "x", x0)
        for stage in range(self.N_horizon):
            # u here is the rate of change, that's why we initialize it
            # with 0
            self.ocp_solver.set(stage, "u", np.zeros(self.nu, ))

        self._initialized = True

    def get_current_ref_array(self):
        """
        Populate reference array depending on whether we have a trajectory or waypoint.
        """
        if self.ref_is_traj:
            if self.i < self.traj_len:
                # extract the sub-trajectory to track under the prediction horizon
                if self.i <= (self.traj_len - self.N_horizon):
                    self.ref = self.trajectory[self.i:self.i + self.N_horizon, :]
                else:
                    self.ref = self.trajectory[self.i:, :]

            else:
                self._loginfo_once("Trajectory Tracking Complete")
                self._set_actuators_neutral()
                return

        else:
            self.ref = np.zeros((self.N_horizon, (self.nx + self.nu)))
            self.ref[:, :] = self.wp_array

    def set_publishers(self, mpc_solution):
        """
        Set the corresponding publishers for the actuators and convenience topics
        """
        # Assign the calculated control signal to actuators
        u_vbs = mpc_solution[13]
        u_lcg = mpc_solution[14]
        u_stern = mpc_solution[15]
        u_rudder = mpc_solution[16]
        u_rpm1 = mpc_solution[17]
        u_rpm2 = mpc_solution[18]

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

        # Convenience Topics
        # FIXME: This if statement is weird.
        if self.ref is not None:
            self._ref = ControlReference()
            self._ref.x = self.ref[0, 0]
            self._ref.y = self.ref[0, 1]
            self._ref.z = self.ref[0, 2]

            r = R.from_quat([self.ref[0, 4],  # x
                             self.ref[0, 5],  # y
                             self.ref[0, 6],  # z
                             self.ref[0, 3]])  # w
            euler_angles = r.as_euler('xyz', degrees=False)
            self._ref.roll = euler_angles[0]
            self._ref.pitch = euler_angles[1]
            self._ref.yaw = euler_angles[2]

    def get_mpc_pred(self):
        """
        Get method for the MPC predictions
        """

        return self.pred_mpc
