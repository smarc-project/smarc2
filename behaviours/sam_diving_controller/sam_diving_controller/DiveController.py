#!/usr/bin/python3

import numpy as np

from tf_transformations import euler_from_quaternion


from smarc_control_msgs.msg import ControlError, ControlInput, ControlReference, ControlState

from .ParamUtils import DivingModelParam
from .IDivePub import MissionStates

from smarc_modelling.vehicles.SAM_casadi import SAM_casadi
from smarc_modelling.control.control import *

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


class DiveControllerInterface:

    def __init__(self, node, dive_pub, dive_sub, rate=0.1):

        self._node = node
        self._dive_sub =dive_sub 
        self._dive_pub =dive_pub  
        self._dt = rate

        # Convenience Topics
        self._current_state = None
        self._ref = None
        self._error = None
        self._input = None

    def _loginfo(self, s):
        self._node.get_logger().info(s)

    def _loginfo_once(self, s):
        self._node.get_logger().info(s, once=True)


    def _set_actuators_neutral(self):
        """
        Setting all actuators to neutral.
        """

        u_vbs_neutral = self.param['vbs_u_neutral']
        u_lcg_neutral = self.param['lcg_u_neutral']
        u_tv_hor_neutral = self.param['tv_u_neutral']
        u_tv_ver_neutral = self.param['tv_u_neutral']
        u_rpm_neutral = self.param['rpm_u_neutral']

        self._dive_pub.set_vbs(u_vbs_neutral)
        self._dive_pub.set_lcg(u_lcg_neutral)
        self._dive_pub.set_thrust_vector(u_tv_hor_neutral, -u_tv_ver_neutral)
        self._dive_pub.set_rpm(u_rpm_neutral)

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

        self._dive_pub.set_vbs(u_vbs_emergency)
        self._dive_pub.set_lcg(u_lcg_emergency)
        self._dive_pub.set_thrust_vector(u_tv_hor_emergency, -u_tv_ver_emergency)
        self._dive_pub.set_rpm(u_rpm_emergency)

        self._input = ControlInput()
        self._input.vbs = u_vbs_emergency
        self._input.lcg = u_lcg_emergency
        self._input.thrustervertical = u_tv_ver_emergency
        self._input.thrusterhorizontal = u_tv_hor_emergency
        self._input.thrusterrpm = float(u_rpm_emergency)

    def get_state(self):
        '''
        For the ConveniencePub
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


class DiveControllerPID(DiveControllerInterface):

    def __init__(self, node, dive_pub, dive_sub, rate=0.1):

        self._node = node
        self._dive_sub =dive_sub
        self._dive_pub =dive_pub  
        self._dt = rate

        super().__init__(self._node, self._dive_pub, self._dive_sub, self._dt)

        self.param = DivingModelParam(self._node).get_param()

        # Convenience Topics
        #self._current_state = None
        #self._ref = None
        #self._error = None
        #self._input = None

        self._depth_vbs_pid = PIDControl(Kp = self.param['vbs_pid_kp'],
                                         Ki = self.param['vbs_pid_ki'],
                                         Kd = self.param['vbs_pid_kd'],
                                         Kaw = self.param['vbs_pid_kaw'],
                                         u_neutral = self.param['vbs_u_neutral'],
                                         u_min = self.param['vbs_u_min'],
                                         u_max = self.param['vbs_u_max'])
        self._pitch_lcg_pid = PIDControl(Kp = self.param['lcg_pid_kp'],
                                         Ki = self.param['lcg_pid_ki'],
                                         Kd = self.param['lcg_pid_kd'],
                                         Kaw = self.param['lcg_pid_kaw'],
                                         u_neutral = self.param['lcg_u_neutral'],
                                         u_min = self.param['lcg_u_min'],
                                         u_max = self.param['lcg_u_max'])
        self._pitch_tv_pid = PIDControl(Kp = self.param['tv_pid_kp'],
                                        Ki = self.param['tv_pid_ki'],
                                        Kd = self.param['tv_pid_kd'],
                                        Kaw = self.param['tv_pid_kaw'],
                                        u_neutral = self.param['tv_u_neutral'],
                                        u_min = self.param['tv_u_min'],
                                        u_max = self.param['tv_u_max'])
        self._yaw_pid = PIDControl(Kp = self.param['yaw_pid_kp'],
                                   Ki = self.param['yaw_pid_ki'],
                                   Kd = self.param['yaw_pid_kd'],
                                   Kaw = self.param['yaw_pid_kaw'],
                                   u_neutral = self.param['yaw_u_neutral'],
                                   u_min = self.param['yaw_u_min'],
                                   u_max = self.param['yaw_u_max'])

        self._loginfo("Dive Controller created")




    def update(self):
        """
        This is where all the magic happens.
        """
        mission_state = self._dive_sub.get_mission_state()

        if mission_state == MissionStates.RECEIVED:
            self._loginfo_once("Mission Received")
            self._set_actuators_neutral()
            return

        if mission_state == MissionStates.COMPLETED:
            self._loginfo_once("Mission Complete")
            self._set_actuators_neutral()
            return

        if mission_state == MissionStates.CANCELLED:
            self._loginfo_once("Mission Cancelled")
            self._set_actuators_neutral()
            return

        # Get setpoints
        depth_setpoint = self._dive_sub.get_depth_setpoint()
        pitch_setpoint = self._dive_sub.get_pitch_setpoint()
        dive_pitch_setpoint = self._dive_sub.get_dive_pitch()
        heading_setpoint = self._dive_sub.get_heading_setpoint()
        rpm_setpoint = self._dive_sub.get_rpm_setpoint()

        # Get current states
        self._current_state = self._dive_sub.get_states()
        current_depth = self._dive_sub.get_depth()
        current_pitch = self._dive_sub.get_pitch()
        current_heading = self._dive_sub.get_heading()

        if not self._dive_sub.has_waypoint():
            return

        if depth_setpoint is None:
            self._loginfo("No depth setpoint yet")
            return

        distance = self._dive_sub.get_distance()
        goal_tolerance = self._dive_sub.get_goal_tolerance()

        # Sketchy minus signs...
        depth_setpoint *= -1
        current_depth *= -1

        # Choose active vs. static diving based on dive pitch angle
        if np.abs(dive_pitch_setpoint) <= self.param['max_dive_pitch']:
            self._loginfo("Active Diving")
            pitch_setpoint = dive_pitch_setpoint

            u_rpm = rpm_setpoint
            u_vbs_raw = self.param['vbs_u_neutral']
            u_lcg_raw = self.param['lcg_u_neutral']
            u_vbs = u_vbs_raw
            u_lcg = u_lcg_raw

            u_tv_hor, yaw_error, u_tv_hor_raw = self._yaw_pid.get_control(current_heading, heading_setpoint, self._dt)
            u_tv_ver, pitch_error, u_tv_ver_raw = self._pitch_tv_pid.get_control(current_pitch, pitch_setpoint, self._dt)
            depth_error = depth_setpoint - current_depth

        else:
            self._loginfo("Static Diving")
            u_rpm = self.param['rpm_u_neutral']
            u_tv_ver_raw = self.param['tv_u_neutral']
            u_tv_hor_raw = self.param['tv_u_neutral']
            u_tv_ver = u_tv_ver_raw
            u_tv_hor = u_tv_hor_raw

            u_vbs, depth_error, u_vbs_raw = self._depth_vbs_pid.get_control(current_depth, depth_setpoint, self._dt)
            u_lcg, pitch_error, u_lcg_raw = self._pitch_lcg_pid.get_control(current_pitch, pitch_setpoint, self._dt)

            yaw_error = heading_setpoint - current_heading


        self._dive_pub.set_vbs(u_vbs)
        self._dive_pub.set_lcg(u_lcg)
        self._dive_pub.set_thrust_vector(u_tv_hor, -u_tv_ver) 
        self._dive_pub.set_rpm(u_rpm, u_rpm) # FIXME: rpm1 and rpm2 can be set individually

        # Convenience Topics
        self._ref = ControlReference()
        self._ref.z = depth_setpoint
        self._ref.pitch = pitch_setpoint

        self._error = ControlError()
        self._error.z = depth_error
        self._error.pitch = pitch_error
        self._error.yaw = yaw_error
        self._error.heading = current_heading

        self._input = ControlInput()
        self._input.vbs = u_vbs
        self._input.lcg = u_lcg
        self._input.thrustervertical = u_tv_ver
        self._input.thrusterhorizontal = u_tv_hor
        self._input.thrusterrpm = float(u_rpm)

        return




class DiveControllerMPC(DiveControllerInterface):

    def __init__(self, node, dive_pub, dive_sub, rate=0.1):

        self._node = node
        self._dive_sub = dive_sub 
        self._dive_pub = dive_pub  
        self._dt = rate

        super().__init__(self._node, self._dive_pub, self._dive_sub, self._dt)

        self.param = DivingModelParam(self._node).get_param()
        self.acados_dir = self._dive_sub.acados_dir

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
        nmpc = NMPC_trajectory(sam, Ts, self.N_horizon, False, self.acados_dir)
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

        # Augment the trajectory and control input r0.0eference 
        Uref = np.zeros((self.trajectory.shape[0], nu))  # Derivative reference - set to 0 to penalize fast control changes
        self.trajectory = np.concatenate((self.trajectory, Uref), axis=1) 

        self.ref = np.zeros(self.trajectory.shape)

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


    # FIXME: This is for development only. The trajectory is later provided by
    # the planning node
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


    def update(self):
        """
        This is where all the magic happens.
        """
        # Get setpoints
        waypoint = self._dive_sub.get_waypoint()

        # Get current states
        self._current_state = self._dive_sub.get_states()
        self._current_control = self._dive_sub.get_control_input()

        x_current = np.zeros(19)
        x_current[0] = self._current_state.pose.pose.position.x
        x_current[1] = self._current_state.pose.pose.position.y
        x_current[2] = self._current_state.pose.pose.position.z 
        x_current[3] = self._current_state.pose.pose.orientation.w
        x_current[4] = self._current_state.pose.pose.orientation.x
        x_current[5] = self._current_state.pose.pose.orientation.y
        x_current[6] = self._current_state.pose.pose.orientation.z
        x_current[7] = self._current_state.twist.twist.linear.x
        x_current[8] = self._current_state.twist.twist.linear.y
        x_current[9] = self._current_state.twist.twist.linear.z
        x_current[10] = self._current_state.twist.twist.angular.x
        x_current[11] = self._current_state.twist.twist.angular.y
        x_current[12] = self._current_state.twist.twist.angular.z
        x_current[13] = self._current_control['vbs']
        x_current[14] = self._current_control['lcg']
        x_current[15] = self._current_control['stern']
        x_current[16] = self._current_control['rudder']
        x_current[17] = self._current_control['rpm1']
        x_current[18] = self._current_control['rpm2']

        # FIXME: This is for debugging only!
        if self.i == self.Nsim:
            self.i = 0

        ## extract the sub-trajectory for the horizon
        #if self.i <= (self.Nsim - self.N_horizon):
        #    self.ref = self.trajectory[self.i:self.i + self.N_horizon, :]
        #else:
        #    self.ref = self.trajectory[self.i:, :]

        if waypoint is not None:
            self.ref[:,0] = waypoint.pose.position.x
            self.ref[:,1] = waypoint.pose.position.y
            self.ref[:,2] = waypoint.pose.position.z
            self.ref[:,3] = waypoint.pose.orientation.w
            self.ref[:,4] = waypoint.pose.orientation.x
            self.ref[:,5] = waypoint.pose.orientation.y
            self.ref[:,5] = waypoint.pose.orientation.z


        # Update reference vector
        # If the end of the trajectory has been reached, (ref.shape < N_horizon)
        # set the following waypoints in the horizon to the last waypoint of the trajectory
        for stage in range(self.N_horizon):
            if self.ref.shape[0] < self.N_horizon and self.ref.shape[0] != 0:
                self.ocp_solver.set(stage, "p", self.ref[self.ref.shape[0]-1,:])
            else:
                self.ocp_solver.set(stage, "p", self.ref[stage,:])

        # Set the terminal state reference
        self.ocp_solver.set(self.N_horizon, "yref", self.ref[-1,:self.nx])
 
        # Set current state
        self.ocp_solver.set(0, "lbx", x_current)
        self.ocp_solver.set(0, "ubx", x_current)

        # solve ocp and get next control input
        status = self.ocp_solver.solve()
        #ocp_solver.print_statistics()
        #if status != 0:
            #print(f" Note: acados_ocp_solver returned status: {status}")

        # simulate system
        self.t[self.i] = self.ocp_solver.get_stats('time_tot')
        self.simU[self.i, :] = self.ocp_solver.get(0, "u")
        #X_eval = ocp_solver.get(0, "x")
        mpc_solution = self.integrator.simulate(x=x_current, u=self.simU[self.i, :])

        # TODO: Check that the outputs fit the actual actuators
        u_vbs = mpc_solution[13]
        u_lcg = mpc_solution[14]
        u_stern = mpc_solution[15] 
        u_rudder = mpc_solution[16]
        u_rpm1 = mpc_solution[17]
        u_rpm2 = mpc_solution[18]

        self.simX[self.i+1, :] = mpc_solution

        self._dive_pub.set_vbs(u_vbs)
        self._dive_pub.set_lcg(u_lcg)
        self._dive_pub.set_thrust_vector(u_rudder, u_stern) 
        self._dive_pub.set_rpm(u_rpm1, u_rpm2)

        # Convenience Topics
        if self.ref is not None:
            self._ref = ControlReference()
            self._ref.x = self.ref[0,0]
            self._ref.y = self.ref[0,1]
            self._ref.z = self.ref[0,2]

        self._error = ControlError()
        self._error.x = self.ref[0,2] - x_current[2]
        self._error.z = self.ref[0,2] - x_current[2]
        self._error.z = self.ref[0,2] - x_current[2]
        # TODO: Finish this. Use euler_from_quaternion(quaternion) to do the conversion.
        self._error.pitch = 0.# pitch_error
        self._error.yaw =  0.#yaw_error
        self._error.heading =  0.#current_heading

        self._input = ControlInput()
        self._input.vbs = u_vbs
        self._input.lcg = u_lcg
        self._input.thrustervertical = u_stern
        self._input.thrusterhorizontal = u_rudder
        self._input.thrusterrpm = float(u_rpm1)

        self.i += 1

        return



# TODO: Write unit tests here that do one loop of everything


