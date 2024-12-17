#!/usr/bin/python3

import numpy as np
from smarc_control_msgs.msg import ControlError, ControlInput, ControlReference, ControlState
from tf_transformations import euler_from_quaternion

from .RLMissionController import MissionStates


class RLControlModel:

    def __init__(self, node, view, mission, rate=1 / 10):

        self._node = node
        self._mission = mission
        self._view = view
        self._dt = rate

        # Convenience Topics
        self._current_state = None
        self._ref = None
        self._error = None
        self._input = None

        self._loginfo("Dive Controller created")


    def _loginfo(self, s):
        self._node.get_logger().info(s)


    def update(self):
        """
        This is where all the magic happens.
        """
        mission_state = self._mission.get_mission_state()

        if mission_state == MissionStates.RECEIVED:
            self._loginfo("Mission Received")
            u_vbs_neutral = 50.0
            u_lcg_neutral = 50.0
            u_tv_hor_neutral = 0.0
            u_tv_ver_neutral = 0.0
            u_rpm_neutral = 0.0


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
            return

        if mission_state == MissionStates.COMPLETED:
            self._loginfo("Mission Complete")

            u_vbs_neutral = 50.0
            u_lcg_neutral = 50.0
            u_tv_hor_neutral = 0.0
            u_tv_ver_neutral = 0.0
            u_rpm_neutral = 0.0


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
            return

        if mission_state == MissionStates.EMERGENCY:
            self._loginfo("Emergency mode. No controller running")

            u_vbs_neutral = 0.0
            u_lcg_neutral = 50.0
            u_tv_hor_neutral = 0.0
            u_tv_ver_neutral = 0.0
            u_rpm_neutral = 0.0


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
            return

        if mission_state == MissionStates.CANCELLED:
            self._loginfo("Mission Cancelled")

            u_vbs_neutral = 50.0
            u_lcg_neutral = 50.0
            u_tv_hor_neutral = 0.0
            u_tv_ver_neutral = 0.0
            u_rpm_neutral = 0.0


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
            return

        # Get setpoints
        depth_setpoint = self._mission.get_depth_setpoint()
        pitch_setpoint = self._mission.get_pitch_setpoint()
        dive_pitch_setpoint = self._mission.get_dive_pitch()
        heading_setpoint = self._mission.get_heading_setpoint()
        rpm_setpoint = self._mission.get_rpm_setpoint()

        # Get current states
        self._current_state = self._mission.get_states()
        current_depth = self._mission.get_depth()
        current_pitch = self._mission.get_pitch()
        current_heading = self._mission.get_heading()

        if not self._mission.has_waypoint():
            return

        if depth_setpoint is None:
            self._loginfo("No depth setpoint yet")
            return

        distance = self._mission.get_distance()
        goal_tolerance = self._mission.get_goal_tolerance()

        # Sketchy minus signs...
        depth_setpoint *= -1
        current_depth *= -1

        # Choose active vs. static diving based on dive pitch angle
        if np.abs(dive_pitch_setpoint) <= np.abs(np.deg2rad(20)):
            self._loginfo("Active Diving")
            pitch_setpoint = dive_pitch_setpoint

            u_rpm = rpm_setpoint
            u_vbs_raw = 50.0
            u_lcg_raw = 50.0
            u_vbs = u_vbs_raw
            u_lcg = u_lcg_raw

            u_tv_hor, yaw_error, u_tv_hor_raw = self._yaw_pid.get_control(current_heading, heading_setpoint, self._dt)
            u_tv_ver, pitch_error, u_tv_ver_raw = self._pitch_tv_pid.get_control(current_pitch, pitch_setpoint, self._dt)
            depth_error = depth_setpoint - current_depth

        else:
            self._loginfo("Static Diving")
            u_rpm = 0
            u_tv_ver_raw = 0.0
            u_tv_hor_raw = 0.0
            u_tv_ver = u_tv_ver_raw
            u_tv_hor = u_tv_hor_raw

            u_vbs, depth_error, u_vbs_raw = self._depth_vbs_pid.get_control(current_depth, depth_setpoint, self._dt)
            u_lcg, pitch_error, u_lcg_raw = self._pitch_lcg_pid.get_control(current_pitch, pitch_setpoint, self._dt)

            yaw_error = heading_setpoint - current_heading


        self._view.set_vbs(u_vbs)
        self._view.set_lcg(u_lcg)
        self._view.set_thrust_vector(u_tv_hor, -u_tv_ver)
        self._view.set_rpm(u_rpm)

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