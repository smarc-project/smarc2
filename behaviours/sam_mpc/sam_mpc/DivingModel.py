#!/usr/bin/python3

import numpy as np

from tf_transformations import euler_from_quaternion

import csv

from smarc_control_msgs.msg import ControlError, ControlInput, ControlReference, ControlState

from .ParamUtils import DivingModelParam
from .IDiveView import MissionStates

from smarc_msgs.msg import ThrusterRPM, PercentStamped
from sam_msgs.msg import Topics as SamTopics
from sam_msgs.msg import ThrusterAngles


try:
    from .IDiveView import IDiveView, MissionStates
    from .SAM_casadi import SAM_casadi
    from .control import *
except: 
    from IDiveView import IDiveView, MissionStates
    from SAM_casadi import SAM_casadi
    from control import *


#from smarc_modelling.vehicles import *
#from smarc_modelling.lib import *


class PIDControl:
    """
    From:  https://github.com/DoernerD/Python_Control/blob/main/src/PID_control.py
    To simplify the PIDModel by using this.
    """
    # TODO: Add anti-windup + saturations
    def __init__(self, Kp=1.0, Ki=0.1, Kd=2.0, Kaw=0.0, u_neutral = 0.0, u_min = -1.0, u_max = 1.0):
        self._Kp = Kp
        self._Ki = Ki
        self._Kd = Kd
        self._Kaw = Kaw
        self._u_neutral = u_neutral
        self._u_min = u_min
        self._u_max = u_max

        # This also initializes all control variables
        self.reset()

    def get_control(self, x:float, x_ref:float, dt:float):
        """
        Returns the control input to the system given its current state x, its desired state x_ref
        and the time since last update dt in seconds.
        x and x_ref have to be 1 dimensional floats of the same quantity (e.g. current and desired
        heading angle)
        """
        self._error_prev = self._error
        self._error = x_ref - x
        self._integral = self._integral + self._error*dt
        self._derivative = (self._error - self._error_prev)/dt

        _u = self._Kp*self._error + self._Ki*(self._integral + self._anti_windup) + self._Kd*self._derivative + self._u_neutral

        u_lim = self._limit_control_action(_u, self._u_min, self._u_max)

        self._compute_anti_windup(_u, u_lim, dt)

        return u_lim, self._error, _u

    def _limit_control_action(self, u, u_min, u_max):
        """
        Take the hardware constraints into account.
        """
        u_lim = None

        if u > u_max:
            u_lim = u_max
        elif u < u_min:
            u_lim = u_min
        else:
            u_lim = u

        return u_lim

    def _compute_anti_windup(self, u, u_lim, dt):
        """
        Anti windup since we have hardware constraints as well as
        and integral part in our controller.
        """

        self._anti_windup += self._Kaw * (u_lim - u) * dt

    def reset(self):
        self._error = 0.0
        self._integral = 0.0
        self._anti_windup = 0.0
        self._derivative = 0.0
        self._error_prev = 0.0


class DiveControlModel:

    def __init__(self, node, view, controller, rate=0.1):

        self._node = node
        self._controller = controller
        self._view = view
        self._dt = rate

        self.param = DivingModelParam(self._node).get_param()

        # Convenience Topics
        self._current_state = None
        self._current_control = None
        self._ref = None
        self._error = None
        self._input = None

        # Extract the CasADi model
        sam = SAM_casadi()


        # create ocp object to formulate the OCP
        Ts = 0.1            # Sampling time
        self.N_horizon = 10      # Prediction horizon
        nmpc = NMPC_trajectory(sam, Ts, self.N_horizon)
        self.nx = nmpc.nx        # State vector length + control vector
        nu = nmpc.nu        # Control derivative vector length

        
        # load trajectory - Replace with your actual file path
        #file_path = "/home/admin/smarc_modelling/src/Trajectories/simonTrajectory.csv"
        file_path = "/home/parallels/ros2_ws/src/smarc2/behaviours/sam_mpc/sam_mpc/trajectoryComplexity3.csv"
        #file_path = "/home/admin/smarc_modelling/src/Trajectories/resolution01.csv"  
        #file_path = "/home/admin/smarc_modelling/src/Trajectories/straight_trajectory.csv"
        #self.trajectory = self._read_csv_to_array(file_path)


        self.trajectory = np.zeros((self.N_horizon, 19))
        self.trajectory[:, 3] = 1.
        self.trajectory[:, 0] = 10.
        self.trajectory[0, 0] = 0.
        self.trajectory[0, 7] = 1e-7
        self.trajectory[0, 17] = 1e-7
        self.trajectory[0, 18] = 1e-7
        self.i = 0

        # Declare duration of sim. and the x_axis in the plots
        self.Nsim = (self.trajectory.shape[0])            # The sim length should be equal to the number of waypoints
        x_axis = np.linspace(0, Ts*self.Nsim, self.Nsim)

        self.simU = np.zeros((self.Nsim, nu))     # Matrix to store the optimal control derivative
        self.simX = np.zeros((self.Nsim+1, self.nx))     # Matrix to store the optimal control derivative


        # Declare the initial state
        x0 = self.trajectory[0] 
        self.simX[0,:] = x0

        # Augment the trajectory and control input reference 
        Uref = np.zeros((self.trajectory.shape[0], nu))  # Derivative reference - set to 0 to penalize fast control changes
        self.trajectory = np.concatenate((self.trajectory, Uref), axis=1) 

        # Run the MPC setup
        self.ocp_solver, self.integrator = nmpc.setup(x0)

        # Initialize the state and control vector as David does
        for stage in range(self.N_horizon + 1):
            self.ocp_solver.set(stage, "x", x0)
        for stage in range(self.N_horizon):
            self.ocp_solver.set(stage, "u", np.zeros(nu,))

        # Array to store the time values
        self.t = np.zeros((self.Nsim))

        self._loginfo("Dive Controller created")


    def _loginfo(self, s):
        self._node.get_logger().info(s)

    def _loginfo_once(self, s):
        self._node.get_logger().info(s, once=True)

    def _read_csv_to_array(self, file_path: str):
        """
        Reads a CSV file and converts the elements to a NumPy array.

        Parameters:
        file_path (str): The path to the CSV file.

        Returns:
        np.array: A NumPy array containing the CSV data.
        """
        data = []
        with open(file_path, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)
            for row in csvreader:
                data.append([float(element) for element in row])

        
        return np.array(data)

    def _set_actuators_neutral(self):
        """
        Setting all actuators to neutral.
        """

        u_vbs_neutral = self.param['vbs_u_neutral']
        u_lcg_neutral = self.param['lcg_u_neutral']
        u_tv_hor_neutral = self.param['tv_u_neutral']
        u_tv_ver_neutral = self.param['tv_u_neutral']
        u_rpm_neutral = self.param['rpm_u_neutral']

        self._view.set_vbs(u_vbs_neutral)
        self._view.set_lcg(u_lcg_neutral)
        self._view.set_thrust_vector(u_tv_hor_neutral, -u_tv_ver_neutral)
        self._view.set_rpm(u_rpm_neutral)

        self._input = ControlInput()
        self._input.vbs = u_vbs_neutral
        self._input.lcg = u_lcg_neutral
        self._input.thrustervertical = u_tv_ver_neutral
        self._input.thrusterhorizontal = u_tv_hor_neutral
        self._input.thrusterrpm = float(u_rpm_neutral)

    def _set_actuators_emergency(self):
        """
        Setting all actuators to neutral.
        """

        u_vbs_emergency = self.param['vbs_u_emergency']
        u_lcg_emergency= self.param['lcg_u_emergency']
        u_tv_hor_emergency= self.param['tv_u_emergency']
        u_tv_ver_emergency= self.param['tv_u_emergency']
        u_rpm_emergency= self.param['rpm_u_emergency']

        self._view.set_vbs(u_vbs_emergency)
        self._view.set_lcg(u_lcg_emergency)
        self._view.set_thrust_vector(u_tv_hor_emergency, -u_tv_ver_emergency)
        self._view.set_rpm(u_rpm_emergency)

        self._input = ControlInput()
        self._input.vbs = u_vbs_emergency
        self._input.lcg = u_lcg_emergency
        self._input.thrustervertical = u_tv_ver_emergency
        self._input.thrusterhorizontal = u_tv_hor_emergency
        self._input.thrusterrpm = float(u_rpm_emergency)


    def update(self):
        """
        This is where all the magic happens.
        """
        # Get setpoints
        depth_setpoint = self._controller.get_depth_setpoint()
        pitch_setpoint = self._controller.get_pitch_setpoint()
        dive_pitch_setpoint = self._controller.get_dive_pitch()
        heading_setpoint = self._controller.get_heading_setpoint()
        rpm_setpoint = self._controller.get_rpm_setpoint()

        # Get current states
        self._current_state = self._controller.get_states()
        self._current_control = self._controller.get_control_input()
        current_depth = self._controller.get_depth()
        current_pitch = self._controller.get_pitch()
        current_heading = self._controller.get_heading()

        x_current = self.simX[self.i, :]
        #x_current = np.zeros(19)
        #x_current[0] = self._current_state.pose.pose.position.x
        #x_current[1] = self._current_state.pose.pose.position.y
        #x_current[2] = self._current_state.pose.pose.position.z
        #x_current[3] = self._current_state.pose.pose.orientation.w
        #x_current[4] = self._current_state.pose.pose.orientation.x
        #x_current[5] = self._current_state.pose.pose.orientation.y
        #x_current[6] = self._current_state.pose.pose.orientation.z
        #x_current[7] = self._current_state.twist.twist.linear.x
        #x_current[8] = self._current_state.twist.twist.linear.y
        #x_current[9] = self._current_state.twist.twist.linear.z
        #x_current[10] = self._current_state.twist.twist.angular.x
        #x_current[11] = self._current_state.twist.twist.angular.y
        #x_current[12] = self._current_state.twist.twist.angular.z
        #x_current[13] = self._current_control['vbs']
        #x_current[14] = self._current_control['lcg']
        #x_current[15] = self._current_control['stern']
        #x_current[16] = self._current_control['rudder']
        #x_current[17] = self._current_control['rpm1']
        #x_current[18] = self._current_control['rpm2']

        # NOTE: This is the current time step in the trajctory
        # FIXME: We want to take care of the trajectory and iterate through it
        # until we either succeed or can't complete it anymore. Then we send
        # the response with the action server back to either say mission
        # success or need new trajectory.
        print(f"self.Nsim: {self.i}")
        #print(f"x_current: {x_current}")

        # FIXME: This is for debugging only!
        if self.i == self.Nsim:
            self.i = 0

        # extract the sub-trajectory for the horizon
        if self.i <= (self.Nsim - self.N_horizon):
            ref = self.trajectory[self.i:self.i + self.N_horizon, :]
        else:
            ref = self.trajectory[self.i:, :]

        # Update reference vector
        # If the end of the trajectory has been reached, (ref.shape < N_horizon)
        # set the following waypoints in the horizon to the last waypoint of the trajectory
        for stage in range(self.N_horizon):
            if ref.shape[0] < self.N_horizon and ref.shape[0] != 0:
                self.ocp_solver.set(stage, "p", ref[ref.shape[0]-1,:])
            else:
                self.ocp_solver.set(stage, "p", ref[stage,:])

        # Set the terminal state reference
        self.ocp_solver.set(self.N_horizon, "yref", ref[-1,:self.nx])
 
        # Set current state
        self.ocp_solver.set(0, "lbx", x_current)
        self.ocp_solver.set(0, "ubx", x_current)

        # solve ocp and get next control input
        status = self.ocp_solver.solve()
        #ocp_solver.print_statistics()
        if status != 0:
            print(f" Note: acados_ocp_solver returned status: {status}")

        # simulate system
        self.t[self.i] = self.ocp_solver.get_stats('time_tot')
        self.simU[self.i, :] = self.ocp_solver.get(0, "u")
        #X_eval = ocp_solver.get(0, "x")
        mpc_solution = self.integrator.simulate(x=x_current, u=self.simU[self.i, :])

        u_vbs = mpc_solution[13]
        u_lcg = mpc_solution[14]
        u_stern = mpc_solution[15]
        u_rudder = mpc_solution[16]
        u_rpm1 = mpc_solution[17]
        u_rpm2 = mpc_solution[18]

        print(f"u_vbs: {u_vbs}, u_lcg: {u_lcg}, u_stern: {u_stern}, u_rudder: {u_rudder}, u_rpm1: {u_rpm1}, u_rpm2: {u_rpm2}")

        self.simX[self.i+1, :] = mpc_solution


        self._view.set_vbs(u_vbs)
        self._view.set_lcg(u_lcg)
        self._view.set_thrust_vector(u_rudder, u_stern) 
        self._view.set_rpm(u_rpm1, u_rpm2)

        self.i += 1


        #mission_state = self._controller.get_mission_state()

        #if mission_state == MissionStates.RECEIVED:
        #    self._loginfo_once("Mission Received")
        #    self._set_actuators_neutral()
        #    return

        #if mission_state == MissionStates.COMPLETED:
        #    self._loginfo_once("Mission Complete")
        #    self._set_actuators_neutral()
        #    return

        #if mission_state == MissionStates.CANCELLED:
        #    self._loginfo_once("Mission Cancelled")
        #    self._set_actuators_neutral()
        #    return

        #if not self._controller.has_waypoint():
        #    return

        #if depth_setpoint is None:
        #    self._loginfo("No depth setpoint yet")
        #    return

        #distance = self._controller.get_distance()
        #goal_tolerance = self._controller.get_goal_tolerance()

        ## Sketchy minus signs...
        #depth_setpoint *= -1
        #current_depth *= -1

        ## Choose active vs. static diving based on dive pitch angle
        #if np.abs(dive_pitch_setpoint) <= self.param['max_dive_pitch']:
        #    self._loginfo("Active Diving")
        #    pitch_setpoint = dive_pitch_setpoint

        #    u_rpm = rpm_setpoint
        #    u_vbs_raw = self.param['vbs_u_neutral']
        #    u_lcg_raw = self.param['lcg_u_neutral']
        #    u_vbs = u_vbs_raw
        #    u_lcg = u_lcg_raw

        #    u_tv_hor, yaw_error, u_tv_hor_raw = self._yaw_pid.get_control(current_heading, heading_setpoint, self._dt)
        #    u_tv_ver, pitch_error, u_tv_ver_raw = self._pitch_tv_pid.get_control(current_pitch, pitch_setpoint, self._dt)
        #    depth_error = depth_setpoint - current_depth

        #else:
        #    self._loginfo("Static Diving")
        #    u_rpm = self.param['rpm_u_neutral']
        #    u_tv_ver_raw = self.param['tv_u_neutral']
        #    u_tv_hor_raw = self.param['tv_u_neutral']
        #    u_tv_ver = u_tv_ver_raw
        #    u_tv_hor = u_tv_hor_raw

        #    u_vbs, depth_error, u_vbs_raw = self._depth_vbs_pid.get_control(current_depth, depth_setpoint, self._dt)
        #    u_lcg, pitch_error, u_lcg_raw = self._pitch_lcg_pid.get_control(current_pitch, pitch_setpoint, self._dt)

        #    yaw_error = heading_setpoint - current_heading


        #self._view.set_vbs(u_vbs)
        #self._view.set_lcg(u_lcg)
        #self._view.set_thrust_vector(u_tv_hor, -u_tv_ver) 
        #self._view.set_rpm(u_rpm)

        ## Convenience Topics
        #self._ref = ControlReference()
        #self._ref.z = depth_setpoint
        #self._ref.pitch = pitch_setpoint

        #self._error = ControlError()
        #self._error.z = depth_error
        #self._error.pitch = pitch_error
        #self._error.yaw = yaw_error
        #self._error.heading = current_heading

        #self._input = ControlInput()
        #self._input.vbs = u_vbs
        #self._input.lcg = u_lcg
        #self._input.thrustervertical = u_tv_ver
        #self._input.thrusterhorizontal = u_tv_hor
        #self._input.thrusterrpm = float(u_rpm)

        return


    def get_state(self):
        '''
        For the ConvenienceView
        '''
        if self._current_state is None:
            return None

        state = ControlState()
        state.pose.x = self._current_state.pose.pose.position.x
        state.pose.y = self._current_state.pose.pose.position.y
        state.pose.z = self._current_state.pose.pose.position.z

        rpy = euler_from_quaternion([
            self._current_state.pose.pose.orientation.x,
            self._current_state.pose.pose.orientation.y,
            self._current_state.pose.pose.orientation.z,
            self._current_state.pose.pose.orientation.w])

        state.pose.roll = rpy[0]
        state.pose.pitch = rpy[1]
        state.pose.yaw = rpy[2]

        # TODO: Add the velocity

        return state

    def get_ref(self):
        return self._ref

    def get_error(self):
        return self._error

    def get_input(self):
        return self._input

# TODO: Write unit tests here that do one loop of everything

