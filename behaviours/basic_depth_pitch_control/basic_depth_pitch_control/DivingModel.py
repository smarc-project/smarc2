#!/usr/bin/python3

import numpy as np
import math

import tf2_geometry_msgs.tf2_geometry_msgs
from tf_transformations import euler_from_quaternion

from geometry_msgs.msg import PoseStamped, TransformStamped

from smarc_control_msgs.msg import ControlError, ControlInput, ControlReference, ControlState


class PIDControl:
    """
    From:  https://github.com/DoernerD/Python_Control/blob/main/src/PID_control.py
    To simplify the PIDModel by using this.
    """
    # TODO: Add anti-windup + saturations
    def __init__(self, Kp=1.0, Ki=0.1, Kd=2.0, Kaw=0.0, u_neutral = 0.0):
        self._Kp = Kp
        self._Ki = Ki
        self._Kd = Kd
        self._Kaw = Kaw
        self._u_neutral = u_neutral

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

        u = self._Kp*self._error + self._Ki*(self._integral - self._anti_windup) + self._Kd*self._derivative + self._u_neutral

        return u, self._error

    def reset(self):
        self._error = 0.0
        self._integral = 0.0
        self._anti_windup = 0.0
        self._derivative = 0.0
        self._error_prev = 0.0


class DepthPitchControl:

    def __init__(self, node, view, controller, rate=1/10):

        self._node = node
        self._controller = controller
        self._view = view
        self._dt = rate

        # Convenience Topics
        self._current_state = None
        self._ref = None
        self._error = None
        self._input = None


        self._depth_pid = PIDControl(Kp = 40.0, Ki = 5.0, Kd = 0.0, Kaw = 0.0, u_neutral = 50.0)
        self._pitch_pid = PIDControl(Kp = 40.0, Ki = 5.0, Kd = 0.0, Kaw = 0.0, u_neutral = 50.0)

        self._loginfo("Depth Controller created")


    def _loginfo(self, s):
        self._node.get_logger().info(s)


    def update(self):
        """
        This is where all the magic happens.
        """
        # Get setpoints
        depth_setpoint = self._controller.get_depth_setpoint()
        pitch_setpoint = self._controller.get_pitch_setpoint()

        # Get current states
        self._current_state = self._controller.get_states()
        current_depth = self._controller.get_depth()
        current_pitch = self._controller.get_pitch()

        if depth_setpoint is None:
            self._loginfo("No depth setpoint received")
            return

        if pitch_setpoint is None:
            self._loginfo("No pitch setpint received")
            return


        # Sketchy minus signs...
        depth_setpoint *= -1
        current_depth *= -1


        u_vbs, depth_error = self._depth_pid.get_control(current_depth, depth_setpoint, self._dt)
        u_lcg, pitch_error = self._pitch_pid.get_control(current_pitch, pitch_setpoint, self._dt)


        self._view.set_vbs(u_vbs)
        self._view.set_lcg(u_lcg)

#        self._loginfo(f"Depth: {current_depth:.3f}, setpoint: {depth_setpoint:.3f}, error: {depth_error:.3f}, VBS: {u_vbs:.3f}")
#        self._loginfo(f"Pitch: {current_pitch:.3f}, setpoint: {pitch_setpoint:.3f}, error: {pitch_error:.3f}, LCG: {u_lcg:.3f}")

        # TODO: Could be done nicer probably
        self._ref = ControlReference()
        self._ref.z = depth_setpoint
        self._ref.pitch = pitch_setpoint

        self._error = ControlError()
        self._error.z = depth_error
        self._error.pitch = pitch_error

        self._input = ControlInput()
        self._input.vbs = u_vbs
        self._input.lcg = u_lcg

        return


    def limit_control_action(self, u, u_min, u_max):
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


    def get_state(self):
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

