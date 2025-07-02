#!/usr/bin/python3

import numpy as np
from pathlib import Path

from tf_transformations import euler_from_quaternion
from scipy.spatial.transform import Rotation as R

import csv

from smarc_control_msgs.msg import ControlError, ControlInput, ControlReference, ControlState

#from .ParamUtils import DivingModelParam
from .IDivePub import MissionStates, ActuatorStates

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

    def __init__(self, node, dive_pub, dive_sub, param, rate=0.1):

        self._node = node
        self._dive_sub =dive_sub 
        self._dive_pub =dive_pub  
        self._dt = rate

        # Convenience Topics
        self._current_state = None
        self._ref = None
        self._error = None
        self._input = None
        self._dive_mode = None

        self.param = param

    def _loginfo(self, s):
        self._node.get_logger().info(s)

    def _loginfo_once(self, s):
        self._node.get_logger().info(s, once=True)


    def _set_actuators_neutral(self):
        """
        Setting all actuators to neutral.
        """

        actuator_state = self._dive_pub.get_actuator_states()

        if actuator_state == ActuatorStates.ENGAGED:
            u_vbs_neutral = self.param['vbs_u_neutral'] 
            u_lcg_neutral = self.param['lcg_u_neutral']
            u_tv_hor_neutral = self.param['tv_u_neutral']
            u_tv_ver_neutral = self.param['tv_u_neutral']
            u_rpm_neutral = self.param['rpm_u_neutral']

            self._dive_pub.set_vbs(u_vbs_neutral)
            self._dive_pub.set_lcg(u_lcg_neutral)
            self._dive_pub.set_thrust_vector(u_tv_hor_neutral, -u_tv_ver_neutral)
            self._dive_pub.set_rpm(u_rpm_neutral, u_rpm_neutral)

            self._input = ControlInput()
            self._input.vbs = u_vbs_neutral
            self._input.lcg = u_lcg_neutral
            self._input.thrustervertical = u_tv_ver_neutral
            self._input.thrusterhorizontal = u_tv_hor_neutral
            self._input.thrusterrpm = float(u_rpm_neutral)

            self._dive_pub.set_actuator_states(ActuatorStates.NEUTRAL, "DC")


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
        self._dive_pub.set_rpm(u_rpm_emergency, u_rpm_emergency)

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

    def get_dive_mode(self):
        return self._dive_mode


class DiveControllerPID(DiveControllerInterface):

    def __init__(self, node, dive_pub, dive_sub, param, rate=0.1):

        self._node = node
        self._dive_sub = dive_sub
        self._dive_pub = dive_pub  
        self._dt = rate
        self.param = param

        super().__init__(self._node, self._dive_pub, self._dive_sub, self.param, self._dt)

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

        #self._loginfo_once(f"DC: {mission_state}")

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

        # Engage actuators in case they were off before.
        self._dive_pub.set_actuator_states(ActuatorStates.ENGAGED, "DP")

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

        #self._loginfo(f"state: {self._current_state}, depth: {current_depth}, pitch: {current_pitch}, heading: {current_heading}")

        if not self._dive_sub.has_waypoint():
            return

        if depth_setpoint is None:
            self._loginfo("No depth setpoint yet")
            return

        # Sketchy minus signs...
        depth_setpoint *= -1
        current_depth *= -1

        # Choose active vs. static diving based on dive pitch angle
        if np.abs(dive_pitch_setpoint) <= self.param['max_dive_pitch']:
            self._dive_mode = "Active Diving"
            pitch_setpoint = dive_pitch_setpoint

            u_rpm = rpm_setpoint 
            u_vbs_raw = self.param['vbs_u_neutral']
            u_lcg_raw = self.param['lcg_u_neutral']
            u_vbs = u_vbs_raw
            u_lcg = u_lcg_raw

            u_tv_rudder, yaw_error, u_tv_rudder_raw = self._yaw_pid.get_control(current_heading, heading_setpoint, self._dt)
            u_tv_stern, pitch_error, u_tv_stern_raw = self._pitch_tv_pid.get_control(current_pitch, pitch_setpoint, self._dt)
            depth_error = depth_setpoint - current_depth

        else:
            self._dive_mode = "Static Diving"
            u_rpm = self.param['rpm_u_neutral']
            u_tv_stern_raw = self.param['tv_u_neutral']
            u_tv_rudder_raw = self.param['tv_u_neutral']
            u_tv_stern = u_tv_stern_raw
            u_tv_rudder = u_tv_rudder_raw

            u_vbs, depth_error, u_vbs_raw = self._depth_vbs_pid.get_control(current_depth, depth_setpoint, self._dt)
            u_lcg, pitch_error, u_lcg_raw = self._pitch_lcg_pid.get_control(current_pitch, pitch_setpoint, self._dt)

            yaw_error = heading_setpoint - current_heading

        #s_ctrl = ""
        #s_ctrl += f"current depth: {current_depth}\n"
        #s_ctrl += f"depth setpoint: {depth_setpoint}\n"
        #s_ctrl += f"depth error: {depth_error}\n"
        #s_ctrl += f"VBS: {u_vbs}\n"

        #self._loginfo(s_ctrl)


        self._dive_pub.set_vbs(u_vbs)
        self._dive_pub.set_lcg(u_lcg)
        self._dive_pub.set_thrust_vector(u_tv_rudder, -u_tv_stern) 
        self._dive_pub.set_rpm(u_rpm, u_rpm) 

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
        self._input.thrustervertical = -u_tv_stern
        self._input.thrusterhorizontal = u_tv_rudder
        self._input.thrusterrpm = float(u_rpm)

        return


class DepthJoyControllerPID(DiveControllerInterface):

    def __init__(self, node, dive_pub, dive_sub, param, rate=0.1):

        self._node = node
        self._dive_sub = dive_sub
        self._dive_pub = dive_pub  
        self._dt = rate
        self.param = param

        super().__init__(self._node, self._dive_pub, self._dive_sub, self.param, self._dt)

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

        self._loginfo("Dive Controller created")


    def update(self):
        """
        This is where all the magic happens.
        """
        # Get setpoints
        depth_setpoint = self._dive_sub.get_joy_depth_setpoint()
        pitch_setpoint = self._dive_sub.get_joy_pitch_setpoint()

        # Get current states
        current_depth = self._dive_sub.get_sensor_depth()
        current_pitch = self._dive_sub.get_sensor_pitch()

        if depth_setpoint is None:
            self._loginfo_once("No depth setpoint received")
            return

        if pitch_setpoint is None:
            self._loginfo("No pitch setpoint yet")
            return

        if current_depth is None:
            self._loginfo("No depth measurement yet")
            return

        if current_pitch is None:
            self._loginfo("No pitch measurement yet")
            return

        # Sketchy minus signs...
        depth_setpoint *= -1.0
        current_depth *= -1.0

        # This is due to the fact that we want to move the LCG forward when
        # having a negative real pitch error.

        pitch_setpoint *= -1.0
        current_pitch *= -1.0

        # Choose active vs. static diving based on dive pitch angle
        #s = f"Control States:\n"
        #s += f"Depth: {current_depth}, Pitch: {current_pitch}\n"
        #s += f"SP depth: {depth_setpoint}, pitch: {pitch_setpoint}\n"
        #s += f"Errors: depth: {depth_error}, pitch: {pitch_error}\n"
        #s += f"VBS: {u_vbs}, LCG: {u_lcg}, tv: {u_tv_ver}\n"
        #s += f"[-----]"
        #self._loginfo(s)

        self._loginfo(f"Joy Update: Begin Control Loop")

        depth_error = depth_setpoint - current_depth

        if np.abs(depth_error) <= 0.5:
            self._loginfo("Active Diving")

            u_vbs_raw = self.param['vbs_u_neutral']
            u_lcg_raw = self.param['lcg_u_neutral']
            u_vbs = u_vbs_raw
            u_lcg = u_lcg_raw

            u_tv_ver, pitch_error, u_tv_ver_raw = self._pitch_tv_pid.get_control(current_pitch, pitch_setpoint, self._dt)
            depth_error = depth_setpoint - current_depth

        else:
            self._loginfo("Static Diving")
            u_tv_ver_raw = self.param['tv_u_neutral']
            u_tv_ver = u_tv_ver_raw

            u_vbs, depth_error, u_vbs_raw = self._depth_vbs_pid.get_control(current_depth, depth_setpoint, self._dt)
            u_lcg, pitch_error, u_lcg_raw = self._pitch_lcg_pid.get_control(current_pitch, pitch_setpoint, self._dt)


        s = f"Control States:\n"
        s += f"Depth: {current_depth:.3f}, Pitch: {current_pitch:.3f}\n"
        s += f"SP depth: {depth_setpoint}, pitch: {pitch_setpoint}\n"
        s += f"Errors: depth: {depth_error:.3f}, pitch: {pitch_error:.3f}\n"
        s += f"VBS: {u_vbs:.3f}, LCG: {u_lcg:.3f}, tv: {u_tv_ver:.3f}\n"
        s += f"[-----]"
        self._loginfo(s)


        self._dive_pub.set_vbs(u_vbs)
        self._dive_pub.set_lcg(u_lcg)
        self._dive_pub.set_stern(u_tv_ver) # FIXME: Check if you need a sign or not.

        # Convenience Topics
        self._ref = ControlReference()
        self._ref.z = depth_setpoint
        self._ref.pitch = pitch_setpoint

        self._error = ControlError()
        self._error.z = depth_error
        self._error.pitch = pitch_error

        self._input = ControlInput()
        self._input.vbs = u_vbs
        self._input.lcg = u_lcg
        self._input.thrustervertical = u_tv_ver

        return

class DiveControllerMPC(DiveControllerInterface):

    def __init__(self, node, dive_pub, dive_sub, param, rate=0.1):

        self._node = node
        self._dive_sub = dive_sub 
        self._dive_pub = dive_pub 
        self.param = param 
        self._dt = rate


        super().__init__(self._node, self._dive_pub, self._dive_sub, self._dt)

        # FIXME: This needs to be fixed. Acados places the generated C files in
        # the current directory. So we litter the whole ros workspace with
        # them. Not good, but all attempts to force it to use a specific
        # directory failed so far.

        # Flag if you want to rebuild the OCP or not (if changes has been made to the MPC)
        build = False # NOTE: Don't change until the previous fixme is resolved.
        self.acados_dir = f"{Path(__file__).resolve().parents[0]}" 

        # Convenience Topics
        self._current_state = None
        self._current_control = None
        self._ref = None
        self._error = None
        self._input = None

        # Extract the CasADi model
        sam = SAM_casadi(dt=self._dt)

        # Declare counter
        self.i = 0

        # create ocp object to formulate the OCP
        self.N_horizon = 12 # Prediction horizon
        self.nmpc = NMPC(sam, self._dt, self.N_horizon, update_solver_settings=build)
        self.nx = self.nmpc.nx        # State vector length + control vector
        self.nu = self.nmpc.nu        # Control derivative vector length
        
        self.ref_is_traj = True
        difficulty = 'easy'
        if self.ref_is_traj:
            # load trajectory - Replace with your actual file path
            if difficulty == 'easy':
                file_path = "/home/admin/smarc_modelling/src/Trajectories/report_update/easy/trajectories/case_easy0.csv"
                self.q_rot = R.from_euler('z', 0, degrees=True)
            elif difficulty == 'medium':
                file_path = "/home/admin/smarc_modelling/src/Trajectories/report_update/medium/trajectories/case_medium0.csv"
                self.q_rot = R.from_euler('z', 90, degrees=True)
            elif difficulty == 'hard':
                file_path = "/home/admin/smarc_modelling/src/Trajectories/report_update/hard/trajectories/case_hard0.csv"
                self.q_rot = R.from_euler('z', 180, degrees=True)
            self.trajectory = self._read_csv_to_array(file_path)

            # Declare duration of sim. 
            self.Nsim = (self.trajectory.shape[0])         # The sim length should be equal to the number of waypoints
            self.x0 = self.trajectory[0] 
                    # Augment the trajectory and control input r0.0eference 
            Uref = np.zeros((self.trajectory.shape[0], self.nu))  # Derivative reference - set to 0 to penalize large control increments
            self.trajectory = np.concatenate((self.trajectory, Uref), axis=1) 

        # NOTE: This needs to happen in the update function with some check before proceeding. Otherwise, you don't get the right data from the dive sub node, because it's not yet spinning and thus doesn't get the topics yet. 
        self._initialized = False
        self._init_state = np.zeros(13)  #self._dive_sub.get_states()
        self._init_control = np.zeros(6) #self._dive_sub.get_control_input()

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

        # Get the init. states msg
        self._init_state = self._dive_sub.get_states()
        self._init_control = self._dive_sub.get_control_input()

        # Get the current states msg
        self._current_state = self._dive_sub.get_states()
        self._current_control = self._dive_sub.get_control_input()

        if not self._initialized and self.ref_is_traj == True:
            # Declare the initial state based on where the robot is right now
            tmp = self._dive_sub.get_states()
            while tmp is None:
                self._loginfo(f"tmp: {tmp}")
                self._loginfo_once("Waiting for states")
                return
            
            self.x0 = self.get_init_state(self._init_state, self._init_control)

            # Match the starting position in unity with the one from the trajectory.
            self.trajectory[:,0] +=  self.x0[0] - self.trajectory[0,0]
            self.trajectory[:,1] +=  self.x0[1] - self.trajectory[0,1]
            self.trajectory[:,2] +=  self.x0[2] - self.trajectory[0,2]

            # Match the starting orientation with the one from the trajectory
            for index, waypoint in enumerate(self.trajectory):
                q_waypoint = R.from_quat(waypoint[3:7], scalar_first = True)
                q_new = self.q_rot * q_waypoint
                q_new = q_new.as_quat()
                q_new = [q_new[3], q_new[0], q_new[1], q_new[2]] #Convert back to w,x,y,z
                self.trajectory[index, 3:7] = q_new
            # Run the MPC setup
            self.ocp_solver, self.integrator = self.nmpc.setup(self.x0)

            # Initialize the state and control vector as David does
            for stage in range(self.N_horizon + 1):
                self.ocp_solver.set(stage, "x", self.x0)
            for stage in range(self.N_horizon):
                self.ocp_solver.set(stage, "u", np.zeros(self.nu,))

            self._initialized = True

        elif self.ref_is_traj == False:
            self.Nsim = 1 # TODO:fix the Nsim issue. This is to trick the print statement in the loginfo
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

        # Engage actuators in case they were off before.
        self._dive_pub.set_actuator_states(ActuatorStates.ENGAGED, "DP")
        
        if not self.ref_is_traj:
            
            if not self._dive_sub.has_waypoint():
                self._loginfo(f"No waypoint available")
                return
            
            self.x0 = self.get_init_state(self._init_state, self._init_control, is_trajectory=False)

            # Run the MPC setup
            self.ocp_solver, self.integrator = self.nmpc.setup(self.x0)

            # Initialize the state and control vector as David does
            for stage in range(self.N_horizon+1):
                self.ocp_solver.set(stage, "x", self.x0)
            for stage in range(self.N_horizon):
                self.ocp_solver.set(stage, "u", np.zeros(self.nu,))

            # Get Waypoint information
            waypoint = self._dive_sub.get_odom_waypoint()
            self._loginfo("Getting waypoint information")
            self._loginfo(f"Waypoint: {waypoint}")
            waypoint_x = waypoint.position.x
            waypoint_y = waypoint.position.y
            waypoint_z = waypoint.position.z
            waypoint_q_w = waypoint.orientation.w
            waypoint_q_x = waypoint.orientation.x
            waypoint_q_y = waypoint.orientation.y
            waypoint_q_z = waypoint.orientation.z
            rpm_setpoint = self._dive_sub.get_rpm_setpoint()

            self._initialized = True

        # Get the current state
        x_current = self.get_current_state(self._current_state, self._current_control)

        # # FIXME: Only for trajectory tracking of length Nsim, edit this to fit waypoints too
        if self.ref_is_traj:
            if self.i < self.Nsim:
                # extract the sub-trajectory to track under the prediction horizon
                if self.i <= (self.Nsim - self.N_horizon):
                    self.ref = self.trajectory[self.i:self.i + self.N_horizon, :]
                else:
                    self.ref = self.trajectory[self.i:, :]

                # Update reference vector
                # If the end of the trajectory has been reached, (ref.shape < N_horizon from above)
                # set the following waypoints in the horizon to the last waypoint of the trajectory
                for stage in range(self.N_horizon):
                    if self.ref.shape[0] < self.N_horizon and self.ref.shape[0] != 0:
                        self.ocp_solver.set(stage, "p", self.ref[self.ref.shape[0]-1,:])
                    else:
                        self.ocp_solver.set(stage, "p", self.ref[stage,:])

                # Set the terminal state reference to the value at N_horizon
                self.ocp_solver.set(self.N_horizon, "yref", self.ref[-1,:self.nx])

                # Set current state
                self.ocp_solver.set(0, "lbx", x_current)
                self.ocp_solver.set(0, "ubx", x_current)

                # solve ocp and get next control input
                status = self.ocp_solver.solve()

                # simulate system
                self.simU = self.ocp_solver.get(0, "u")
                mpc_solution = self.integrator.simulate(x=x_current, u=self.simU)

                # TODO: Check that the outputs fit the actual actuators - X_current is two timestep behind?
                u_vbs = mpc_solution[13]
                u_lcg = mpc_solution[14]
                u_stern = mpc_solution[15] 
                u_rudder = mpc_solution[16]
                u_rpm1 = mpc_solution[17]
                u_rpm2 = mpc_solution[18]

            else:
                self.i = self.Nsim-1 # so it stays here and read the sim data from last step
                u_vbs = self.prev_vbs
                u_lcg = self.prev_lcg
                u_stern = 0.0
                u_rudder = 0.0
                u_rpm1 = 0.0
                u_rpm2 = 0.0
        else:
            self.ref = np.zeros((self.N_horizon, (self.nx+self.nu)))
            self.ref[:, 0] = waypoint_x
            self.ref[:, 1] = waypoint_y
            self.ref[:, 2] = waypoint_z
            self.ref[:, 3] = waypoint_q_w
            self.ref[:, 4] = waypoint_q_x
            self.ref[:, 5] = waypoint_q_y
            self.ref[:, 6] = waypoint_q_z

            # Update reference vector
            # If the end of the trajectory has been reached, (ref.shape < N_horizon from above)
            # set the following waypoints in the horizon to the last waypoint of the trajectory
            for stage in range(self.N_horizon):
                if self.ref.shape[0] < self.N_horizon and self.ref.shape[0] != 0:
                    self.ocp_solver.set(stage, "p", self.ref[self.ref.shape[0]-1,:])
                else:
                    self.ocp_solver.set(stage, "p", self.ref[stage,:])

            # Set the terminal state reference to the value at N_horizon
            self.ocp_solver.set(self.N_horizon, "yref", self.ref[-1,:self.nx])


            # Set current state
            self.ocp_solver.set(0, "lbx", x_current)
            self.ocp_solver.set(0, "ubx", x_current)

            # solve ocp and get next control input
            status = self.ocp_solver.solve()

            # simulate system
            self.simU = self.ocp_solver.get(0, "u")
            mpc_solution = self.integrator.simulate(x=x_current, u=self.simU)


            # TODO: Check that the outputs fit the actual actuators - X_current is two timestep behind?
            u_vbs = mpc_solution[13]
            u_lcg = mpc_solution[14]
            u_stern = mpc_solution[15] 
            u_rudder = mpc_solution[16]
            u_rpm1 = mpc_solution[17]
            u_rpm2 = mpc_solution[18]

        self.prev_vbs = u_vbs
        self.prev_lcg = u_lcg

        s = f"\nMPC Check step {self.i}/{self.Nsim}: \n"
        s += "Linear:\n"
        s += f"Unity:    x: {x_current[0]:.3f}, y: {x_current[1]:.3f}, z: {x_current[2]:.3f}\n"
        s += f"Uni. Ref: x: {self.ref[0,0]:.3f},   y: {self.ref[0,1]:.3f}, z: {self.ref[0,2]}\n"

        s += "Quaternions:\n"
        s += f"Unity   : w: {x_current[3]:.3f}, x: {x_current[4]:.3f}, y: {x_current[5]:.3f}, z: {x_current[6]:.3f}\n"
        s += f"Uni. Ref: w: {self.ref[0,3]:.3f}, x: {self.ref[0,4]:.3f}, z: {self.ref[0,5]:.3f}, w: {self.ref[0,6]:.3f}\n"
        s += f"NMPC:      Control:\nvbs: {u_vbs:.2f}, lcg: {u_lcg:.3f}, stern: {u_stern:.3f}, rudder: {u_rudder:.3f}, rpm1: {u_rpm1:.0f}, rpm2: {u_rpm2:.0f}\n"
        s += f"X_CURRENT: Control:\nvbs: {x_current[13]:.4f}, lcg: {x_current[14]:.4f}, stern: {x_current[15]:.4f}, rudder: {x_current[16]:.4f}, rpm1: {x_current[17]:.2f}, rpm2: {x_current[18]:.2f}\n"

        self._loginfo(s)

        # Publish the control input
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
            r = R.from_quat(self.ref[0,3:7], scalar_first = True)
            euler_angles = r.as_euler('xyz', degrees=False)
            self._loginfo(f"{euler_angles[2]}")

            self._ref.roll  = euler_angles[0]
            self._ref.pitch = euler_angles[1]
            self._ref.yaw   = euler_angles[2]

        # Set control input
        self._input = ControlInput()
        self._input.vbs = u_vbs
        self._input.lcg = u_lcg
        self._input.thrustervertical = u_stern
        self._input.thrusterhorizontal = u_rudder
        self._input.thrusterrpm = float(u_rpm1)

        self.i += 1

        return
    
    def get_init_state(self, state_msg, control_msg, is_trajectory=True):
        """
        Returns the initial state of the controller as the state vector x (numpy array)
        """
        x0 = np.zeros(19)
        x0[0] = state_msg.pose.pose.position.x
        x0[1] = state_msg.pose.pose.position.y
        x0[2] = state_msg.pose.pose.position.z 
        x0[3] = state_msg.pose.pose.orientation.w
        x0[4] = state_msg.pose.pose.orientation.x
        x0[5] = state_msg.pose.pose.orientation.y
        x0[6] = state_msg.pose.pose.orientation.z
        x0[7] = state_msg.twist.twist.linear.x
        x0[8] = state_msg.twist.twist.linear.y
        x0[9] = state_msg.twist.twist.linear.z
        x0[10] = state_msg.twist.twist.angular.x
        x0[11] = state_msg.twist.twist.angular.y
        x0[12] = state_msg.twist.twist.angular.z
        x0[13] = control_msg['vbs']
        x0[14] = control_msg['lcg']
        x0[15] = control_msg['stern']
        x0[16] = control_msg['rudder']
        if is_trajectory:
            x0[17] = control_msg['rpm1']
            x0[18] = control_msg['rpm2']
        else:
            x0[17] = 1e-6 
            x0[18] = 1e-6 
        return x0
    
    def get_current_state(self, state_msg, control_msg):
        """
        Returns the current state of the controller as the state vector x (numpy array)
        """
        x_current = np.zeros(19)
        x_current[0] = state_msg.pose.pose.position.x
        x_current[1] = state_msg.pose.pose.position.y
        x_current[2] = state_msg.pose.pose.position.z 
        x_current[3] = state_msg.pose.pose.orientation.w
        x_current[4] = state_msg.pose.pose.orientation.x
        x_current[5] = state_msg.pose.pose.orientation.y
        x_current[6] = state_msg.pose.pose.orientation.z
        x_current[7] = state_msg.twist.twist.linear.x
        x_current[8] = state_msg.twist.twist.linear.y
        x_current[9] = state_msg.twist.twist.linear.z
        x_current[10] = state_msg.twist.twist.angular.x
        x_current[11] = state_msg.twist.twist.angular.y
        x_current[12] = state_msg.twist.twist.angular.z
        x_current[13] = control_msg['vbs']
        x_current[14] = control_msg['lcg']
        x_current[15] = control_msg['stern']
        x_current[16] = control_msg['rudder']
        x_current[17] = control_msg['rpm1']
        x_current[18] = control_msg['rpm2']
        
        return x_current

# TODO: Write unit tests here that do one loop of everything