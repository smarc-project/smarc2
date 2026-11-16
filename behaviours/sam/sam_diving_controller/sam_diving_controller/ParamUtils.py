#!/usr/bin/python3

import rclpy
import sys

class DivingModelParam():

    def __init__(self, node):

        self._node = node

        self._node.declare_parameter('vbs_pid_kp', 40.0) 
        self._node.declare_parameter('vbs_pid_ki', 5.0)
        self._node.declare_parameter('vbs_pid_kd', 1.0)
        self._node.declare_parameter('vbs_pid_kaw', 1.0)
        self._node.declare_parameter('vbs_u_neutral', 0.0)
        self._node.declare_parameter('vbs_u_min', 0.0)
        self._node.declare_parameter('vbs_u_max', 100.0)
        self._node.declare_parameter('vbs_u_emergency', 0.0)

        self._node.declare_parameter('lcg_pid_kp', 40.0)
        self._node.declare_parameter('lcg_pid_ki', 5.0)
        self._node.declare_parameter('lcg_pid_kd', 1.0)
        self._node.declare_parameter('lcg_pid_kaw', 1.0)
        self._node.declare_parameter('lcg_u_neutral', 50.0)
        self._node.declare_parameter('lcg_u_min', 0.0)
        self._node.declare_parameter('lcg_u_max', 100.0)
        self._node.declare_parameter('lcg_u_emergency', 50.0)

        self._node.declare_parameter('tv_pid_kp', 1.0)
        self._node.declare_parameter('tv_pid_ki', 0.25)
        self._node.declare_parameter('tv_pid_kd', 0.5)
        self._node.declare_parameter('tv_pid_kaw', 1.0)
        self._node.declare_parameter('tv_u_neutral', 0.0)
        self._node.declare_parameter('tv_u_min', -0.122173)
        self._node.declare_parameter('tv_u_max', 0.122173)
        self._node.declare_parameter('tv_u_emergency', 0.0)

        self._node.declare_parameter('yaw_pid_kp', 2.5)
        self._node.declare_parameter('yaw_pid_ki', 0.25)
        self._node.declare_parameter('yaw_pid_kd', 0.5)
        self._node.declare_parameter('yaw_pid_kaw', 1.0)
        self._node.declare_parameter('yaw_u_neutral', 0.0)
        self._node.declare_parameter('yaw_u_min', -0.122173)
        self._node.declare_parameter('yaw_u_max', 0.122173)

        self._node.declare_parameter('rpm_u_neutral', 0)
        self._node.declare_parameter('rpm_u_min', -400)
        self._node.declare_parameter('rpm_u_max', 800)
        self._node.declare_parameter('rpm_u_emergency', 0)

        self._node.declare_parameter('max_dive_pitch', 0.349)

        # Opt-in Unity static allocation experiment. Zero slew rate disables
        # command slew limiting; these are not identified actuator dynamics.
        self._allocation_defaults = {
            'allocation_test_enabled': False,
            'allocation_front_gain': 0.005,
            'allocation_back_gain': 0.005,
            'allocation_reverse_multiplier': 0.6,
            'allocation_vbs_gain': 997.0 * 9.81 * 0.00025 / 100.0,
            'allocation_lcg_gain': -2.7 * 9.81 * 0.00057,
            'allocation_vbs_trim': 50.0,
            'allocation_lcg_trim': 50.0,
            'allocation_heave_offset': 0.0,
            'allocation_pitch_offset': 0.0,
            'allocation_rpm_rate': 0.0,
            'allocation_vbs_rate': 0.0,
            'allocation_lcg_rate': 0.0,
        }
        for name, value in self._allocation_defaults.items():
            self._node.declare_parameter(name, value)

    def get_param(self):

        param = {}

        param['vbs_pid_kp'] = self._node.get_parameter('vbs_pid_kp').get_parameter_value().double_value
        param['vbs_pid_ki'] = self._node.get_parameter('vbs_pid_ki').get_parameter_value().double_value
        param['vbs_pid_kd'] = self._node.get_parameter('vbs_pid_kd').get_parameter_value().double_value
        param['vbs_pid_kaw'] = self._node.get_parameter('vbs_pid_kaw').get_parameter_value().double_value
        param['vbs_u_neutral'] = self._node.get_parameter('vbs_u_neutral').get_parameter_value().double_value
        param['vbs_u_min'] = self._node.get_parameter('vbs_u_min').get_parameter_value().double_value
        param['vbs_u_max'] = self._node.get_parameter('vbs_u_max').get_parameter_value().double_value
        param['vbs_u_emergency'] = self._node.get_parameter('vbs_u_emergency').get_parameter_value().double_value

        param['lcg_pid_kp'] = self._node.get_parameter('lcg_pid_kp').get_parameter_value().double_value
        param['lcg_pid_ki'] = self._node.get_parameter('lcg_pid_ki').get_parameter_value().double_value
        param['lcg_pid_kd'] = self._node.get_parameter('lcg_pid_kd').get_parameter_value().double_value
        param['lcg_pid_kaw'] = self._node.get_parameter('lcg_pid_kaw').get_parameter_value().double_value
        param['lcg_u_neutral'] = self._node.get_parameter('lcg_u_neutral').get_parameter_value().double_value
        param['lcg_u_min'] = self._node.get_parameter('lcg_u_min').get_parameter_value().double_value
        param['lcg_u_max'] = self._node.get_parameter('lcg_u_max').get_parameter_value().double_value
        param['lcg_u_emergency'] = self._node.get_parameter('lcg_u_emergency').get_parameter_value().double_value

        param['tv_pid_kp'] = self._node.get_parameter('tv_pid_kp').get_parameter_value().double_value
        param['tv_pid_ki'] = self._node.get_parameter('tv_pid_ki').get_parameter_value().double_value
        param['tv_pid_kd'] = self._node.get_parameter('tv_pid_kd').get_parameter_value().double_value
        param['tv_pid_kaw'] = self._node.get_parameter('tv_pid_kaw').get_parameter_value().double_value
        param['tv_u_neutral'] = self._node.get_parameter('tv_u_neutral').get_parameter_value().double_value
        param['tv_u_min'] = self._node.get_parameter('tv_u_min').get_parameter_value().double_value
        param['tv_u_max'] = self._node.get_parameter('tv_u_max').get_parameter_value().double_value
        param['tv_u_emergency'] = self._node.get_parameter('tv_u_emergency').get_parameter_value().double_value

        param['yaw_pid_kp'] = self._node.get_parameter('yaw_pid_kp').get_parameter_value().double_value
        param['yaw_pid_ki'] = self._node.get_parameter('yaw_pid_ki').get_parameter_value().double_value
        param['yaw_pid_kd'] = self._node.get_parameter('yaw_pid_kd').get_parameter_value().double_value
        param['yaw_pid_kaw'] = self._node.get_parameter('yaw_pid_kaw').get_parameter_value().double_value
        param['yaw_u_neutral'] = self._node.get_parameter('yaw_u_neutral').get_parameter_value().double_value
        param['yaw_u_min'] = self._node.get_parameter('yaw_u_min').get_parameter_value().double_value
        param['yaw_u_max'] = self._node.get_parameter('yaw_u_max').get_parameter_value().double_value

        param['rpm_u_neutral'] = self._node.get_parameter('rpm_u_neutral').get_parameter_value().integer_value
        param['rpm_u_min'] = self._node.get_parameter('rpm_u_min').get_parameter_value().integer_value
        param['rpm_u_max'] = self._node.get_parameter('rpm_u_max').get_parameter_value().integer_value
        param['rpm_u_emergency'] = self._node.get_parameter('rpm_u_emergency').get_parameter_value().integer_value

        param['max_dive_pitch'] = self._node.get_parameter('max_dive_pitch').get_parameter_value().double_value

        for name in self._allocation_defaults:
            param[name] = self._node.get_parameter(name).value

        return param
