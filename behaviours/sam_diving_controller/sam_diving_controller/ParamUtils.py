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
        self._node.declare_parameter('vbs_u_neutral', 50.0)
        self._node.declare_parameter('vbs_u_min', 0.0)
        self._node.declare_parameter('vbs_u_max', 100.0)

        self._node.declare_parameter('lcg_pid_kp', 40.0)
        self._node.declare_parameter('lcg_pid_ki', 5.0)
        self._node.declare_parameter('lcg_pid_kd', 1.0)
        self._node.declare_parameter('lcg_pid_kaw', 1.0)
        self._node.declare_parameter('lcg_u_neutral', 50.0)
        self._node.declare_parameter('lcg_u_min', 0.0)
        self._node.declare_parameter('lcg_u_max', 100.0)

        self._node.declare_parameter('tv_pid_kp', 2.5)
        self._node.declare_parameter('tv_pid_ki', 0.25)
        self._node.declare_parameter('tv_pid_kd', 0.5)
        self._node.declare_parameter('tv_pid_kaw', 1.0)
        self._node.declare_parameter('tv_u_neutral', 0.0)
        self._node.declare_parameter('tv_u_min', -0.122173)
        self._node.declare_parameter('tv_u_max', 0.122173)

        self._node.declare_parameter('yaw_pid_kp', 2.5)
        self._node.declare_parameter('yaw_pid_ki', 0.25)
        self._node.declare_parameter('yaw_pid_kd', 0.5)
        self._node.declare_parameter('yaw_pid_kaw', 1.0)
        self._node.declare_parameter('yaw_u_neutral', 0.0)
        self._node.declare_parameter('yaw_u_min', -0.122173)
        self._node.declare_parameter('yaw_u_max', 0.122173)

    def get_param(self):

        param = {}

        param['vbs_pid_kp'] = self._node.get_parameter('vbs_pid_kp').get_parameter_value().integer_value
        param['vbs_pid_ki'] = self._node.get_parameter('vbs_pid_ki').get_parameter_value().integer_value
        param['vbs_pid_kd'] = self._node.get_parameter('vbs_pid_kd').get_parameter_value().integer_value
        param['vbs_pid_kaw'] = self._node.get_parameter('vbs_pid_kaw').get_parameter_value().integer_value
        param['vbs_u_neutral'] = self._node.get_parameter('vbs_u_neutral').get_parameter_value().integer_value
        param['vbs_u_min'] = self._node.get_parameter('vbs_u_min').get_parameter_value().integer_value
        param['vbs_u_max'] = self._node.get_parameter('vbs_u_max').get_parameter_value().integer_value

        param['lcg_pid_kp'] = self._node.get_parameter('lcg_pid_kp').get_parameter_value().integer_value
        param['lcg_pid_ki'] = self._node.get_parameter('lcg_pid_ki').get_parameter_value().integer_value
        param['lcg_pid_kd'] = self._node.get_parameter('lcg_pid_kd').get_parameter_value().integer_value
        param['lcg_pid_kaw'] = self._node.get_parameter('lcg_pid_kaw').get_parameter_value().integer_value
        param['lcg_u_neutral'] = self._node.get_parameter('lcg_u_neutral').get_parameter_value().integer_value
        param['lcg_u_min'] = self._node.get_parameter('lcg_u_min').get_parameter_value().integer_value
        param['lcg_u_max'] = self._node.get_parameter('lcg_u_max').get_parameter_value().integer_value

        param['tv_pid_kp'] = self._node.get_parameter('tv_pid_kp').get_parameter_value().integer_value
        param['tv_pid_ki'] = self._node.get_parameter('tv_pid_ki').get_parameter_value().integer_value
        param['tv_pid_kd'] = self._node.get_parameter('tv_pid_kd').get_parameter_value().integer_value
        param['tv_pid_kaw'] = self._node.get_parameter('tv_pid_kaw').get_parameter_value().integer_value
        param['tv_u_neutral'] = self._node.get_parameter('tv_u_neutral').get_parameter_value().integer_value
        param['tv_u_min'] = self._node.get_parameter('tv_u_min').get_parameter_value().integer_value
        param['tv_u_max'] = self._node.get_parameter('tv_u_max').get_parameter_value().integer_value

        param['yaw_pid_kp'] = self._node.get_parameter('yaw_pid_kp').get_parameter_value().integer_value
        param['yaw_pid_ki'] = self._node.get_parameter('yaw_pid_ki').get_parameter_value().integer_value
        param['yaw_pid_kd'] = self._node.get_parameter('yaw_pid_kd').get_parameter_value().integer_value
        param['yaw_pid_kaw'] = self._node.get_parameter('yaw_pid_kaw').get_parameter_value().integer_value
        param['yaw_u_neutral'] = self._node.get_parameter('yaw_u_neutral').get_parameter_value().integer_value
        param['yaw_u_min'] = self._node.get_parameter('yaw_u_min').get_parameter_value().integer_value
        param['yaw_u_max'] = self._node.get_parameter('yaw_u_max').get_parameter_value().integer_value

        return param
