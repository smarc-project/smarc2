#!/usr/bin/python3

import numpy as np
from smarc_control_msgs.msg import ControlError, ControlInput, ControlReference, ControlState
from tf_transformations import euler_from_quaternion

from .ONNXManager import ONNXManager
from .RLMissionController import MissionStates


class RLControlModel:

    def __init__(self, node, onnx: ONNXManager, view, mission, rate=1 / 10):

        self._node = node
        self._onnx = onnx
        self._mission = mission
        self._view = view
        self._dt = rate

        # Convenience Topics
        self._current_state = None
        self._ref = None
        self._error = None
        self._current_input = None

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

            self._current_input = ControlInput()
            self._current_input.vbs = u_vbs_neutral
            self._current_input.lcg = u_lcg_neutral
            self._current_input.thrustervertical = u_tv_ver_neutral
            self._current_input.thrusterhorizontal = u_tv_hor_neutral
            self._current_input.thrusterrpm = float(u_rpm_neutral)
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

            self._current_input = ControlInput()
            self._current_input.vbs = u_vbs_neutral
            self._current_input.lcg = u_lcg_neutral
            self._current_input.thrustervertical = u_tv_ver_neutral
            self._current_input.thrusterhorizontal = u_tv_hor_neutral
            self._current_input.thrusterrpm = float(u_rpm_neutral)
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

            self._current_input = ControlInput()
            self._current_input.vbs = u_vbs_neutral
            self._current_input.lcg = u_lcg_neutral
            self._current_input.thrustervertical = u_tv_ver_neutral
            self._current_input.thrusterhorizontal = u_tv_hor_neutral
            self._current_input.thrusterrpm = float(u_rpm_neutral)
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

            self._current_input = ControlInput()
            self._current_input.vbs = u_vbs_neutral
            self._current_input.lcg = u_lcg_neutral
            self._current_input.thrustervertical = u_tv_ver_neutral
            self._current_input.thrusterhorizontal = u_tv_hor_neutral
            self._current_input.thrusterrpm = float(u_rpm_neutral)
            return



        # Get current states
        self._current_state = self._view.get_states()
        waypoint = self._mission.get_waypoint_body()()

        if not self._mission.has_waypoint():
            return

        self._onnx.get_control((self._current_state, waypoint, 1.0))

        self._view.set_vbs(u_vbs)
        self._view.set_lcg(u_lcg)
        self._view.set_thrust_vector(u_tv_hor, -u_tv_ver)
        self._view.set_rpm(u_rpm)

        return
