#!/usr/bin/python3
from sam_diving_controller.controllers.PIDControl import PIDControl
from sam_diving_controller.IDivePub import MissionStates, ActuatorStates
from sam_diving_controller.controllers.DiveControllerInterface import DiveControllerInterface
from smarc_control_msgs.msg import ControlError, ControlInput, ControlReference

from smarc_modelling.control.control import *


class DiveControllerPID(DiveControllerInterface):

    def __init__(self, node, dive_pub, dive_sub, param, rate=0.1):

        self._node = node
        self._dive_sub = dive_sub
        self._dive_pub = dive_pub
        self._dt = rate
        self.param = param

        super().__init__(self._node, self._dive_pub, self._dive_sub, self.param, self._dt)

        self._depth_vbs_pid = PIDControl(Kp=self.param['vbs_pid_kp'],
                                         Ki=self.param['vbs_pid_ki'],
                                         Kd=self.param['vbs_pid_kd'],
                                         Kaw=self.param['vbs_pid_kaw'],
                                         u_neutral=self.param['vbs_u_neutral'],
                                         u_min=self.param['vbs_u_min'],
                                         u_max=self.param['vbs_u_max'])
        self._pitch_lcg_pid = PIDControl(Kp=self.param['lcg_pid_kp'],
                                         Ki=self.param['lcg_pid_ki'],
                                         Kd=self.param['lcg_pid_kd'],
                                         Kaw=self.param['lcg_pid_kaw'],
                                         u_neutral=self.param['lcg_u_neutral'],
                                         u_min=self.param['lcg_u_min'],
                                         u_max=self.param['lcg_u_max'])
        self._pitch_tv_pid = PIDControl(Kp=self.param['tv_pid_kp'],
                                        Ki=self.param['tv_pid_ki'],
                                        Kd=self.param['tv_pid_kd'],
                                        Kaw=self.param['tv_pid_kaw'],
                                        u_neutral=self.param['tv_u_neutral'],
                                        u_min=self.param['tv_u_min'],
                                        u_max=self.param['tv_u_max'])
        self._yaw_pid = PIDControl(Kp=self.param['yaw_pid_kp'],
                                   Ki=self.param['yaw_pid_ki'],
                                   Kd=self.param['yaw_pid_kd'],
                                   Kaw=self.param['yaw_pid_kaw'],
                                   u_neutral=self.param['yaw_u_neutral'],
                                   u_min=self.param['yaw_u_min'],
                                   u_max=self.param['yaw_u_max'])

        self._loginfo("Dive Controller created")

    def update(self):
        """
        This is where all the magic happens.
        """
        mission_state = self._dive_sub.get_mission_state()

        # self._loginfo_once(f"DC: {mission_state}")

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
        waypoint_odom = self._dive_sub.get_odom_waypoint()
        waypoint_global = self._dive_sub.get_waypoint()

        # Get current states
        self._current_state = self._dive_sub.get_states()
        current_depth = self._dive_sub.get_depth()
        current_pitch = self._dive_sub.get_pitch()
        current_heading = self._dive_sub.get_heading()
        current_distance = self._dive_sub.get_distance()

        if not self._dive_sub.has_waypoint():
            return

        if depth_setpoint is None:
            self._loginfo("No depth setpoint yet")
            return

        # Debug prints
        s = ''
        s += f'state: x: {self._current_state.pose.pose.position.x:.3f}'
        s += f' y: {self._current_state.pose.pose.position.y:.3f}'
        s += f' z: {self._current_state.pose.pose.position.z:.3f}\n'
        s += f'wp odom: x: {waypoint_odom.position.x:.3f}'
        s += f' y: {waypoint_odom.position.y:.3f}'
        s += f' z: {waypoint_odom.position.z:.3f}'
        s += f'wp global: x: {waypoint_global.pose.position.x:.3f}'
        s += f' y: {waypoint_global.pose.position.y:.3f}'
        s += f' z: {waypoint_global.pose.position.z:.3f}'

        self._loginfo(s)

        # Sketchy minus signs...
        depth_setpoint *= -1
        current_depth *= -1

        depth_error = depth_setpoint - current_depth

        # Choose active vs. static diving based on dive pitch angle
        # if np.abs(dive_pitch_setpoint) <= self.param['max_dive_pitch']:

        # Choose active vs. static diving based on depth error, needed when
        # doing look ahead diving with fixed look ahead distance
        if np.abs(depth_error) <= 0.5:
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

        # Sketchy minus sign for the stern steering because we need a positive
        # steering angle when compensating for a negative pitch
        u_tv_stern = -u_tv_stern

        self._dive_pub.set_vbs(u_vbs)
        self._dive_pub.set_lcg(u_lcg)
        self._dive_pub.set_thrust_vector(u_tv_rudder, u_tv_stern)
        self._dive_pub.set_rpm(u_rpm, u_rpm)

        # Convenience Topics
        self._ref = ControlReference()
        self._ref.z = depth_setpoint
        self._ref.pitch = pitch_setpoint
        self._ref.x = waypoint_odom.position.x
        self._ref.y = waypoint_odom.position.y

        self._error = ControlError()
        self._error.z = depth_error
        self._error.pitch = pitch_error
        self._error.yaw = yaw_error
        self._error.heading = current_heading
        self._error.distance = current_distance

        self._input = ControlInput()
        self._input.vbs = u_vbs
        self._input.lcg = u_lcg
        self._input.thrustervertical = u_tv_stern
        self._input.thrusterhorizontal = u_tv_rudder
        self._input.thrusterrpm = float(u_rpm)

        return
