#!/usr/bin/python3
from tkinter import W
from sam_diving_controller.controllers.PIDControl import PIDControl
from sam_diving_controller.IDivePub import MissionStates, ActuatorStates
from sam_diving_controller.controllers.DiveControllerInterface import DiveControllerInterface
from smarc_control_msgs.msg import ControlError, ControlInput, ControlReference
from nav_msgs.msg import Odometry

# from smarc_modelling.control.control import *

import numpy as np # david plz :,(

class DiveControllerPID(DiveControllerInterface):

    def __init__(self, node, dive_pub, dive_sub, param, rate=0.1):

        self._node = node
        self._dive_sub = dive_sub
        self._dive_pub = dive_pub
        self._dt = rate
        self.param = param
        
        self.traj_index = 0
        self._control_ref = None
        self._current_state_in_dr = None

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

        self.param['surge_rpm_pid_kp'] = 100.0
        self.param['surge_rpm_pid_ki'] = 5.25
        self.param['surge_rpm_pid_kd'] = 1.5
        self.param['surge_rpm_pid_kaw'] = 1.0
        self.param['surge_rpm_u_neutral'] = 0
        self.param['surge_rpm_u_min'] = -400
        self.param['surge_rpm_u_max'] = 450

        self._surge_rpm_pid = PIDControl(Kp=self.param['surge_rpm_pid_kp'],
                                         Ki=self.param['surge_rpm_pid_ki'],
                                         Kd=self.param['surge_rpm_pid_kd'],
                                         Kaw=self.param['surge_rpm_pid_kaw'],
                                         u_neutral=self.param['surge_rpm_u_neutral'],
                                         u_min=self.param['surge_rpm_u_min'],
                                         u_max=self.param['surge_rpm_u_max'])

        self._loginfo("Dive Controller created")

    def update(self):
        """
        This is where all the magic happens.
        """
        mission_state = self._dive_sub.get_mission_state()

        self._loginfo_once(f"DC: {mission_state}")

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
        rpm_setpoint = 450 #self._dive_sub.get_rpm_setpoint()
        waypoint_odom = self._dive_sub.get_waypoint_in_odom()
        waypoint_global = self._dive_sub.get_waypoint()

        # Get current states
        self._current_state = self._dive_sub.get_states()
        self._current_state_in_dr = self._dive_sub.get_states_in_dr()
        current_depth = self._dive_sub.get_depth()
        current_pitch = self._dive_sub.get_pitch()
        current_heading = self._dive_sub.get_heading()
        current_distance = self._dive_sub.get_distance()

        if not self._dive_sub.has_waypoint():
            self._loginfo("No waypoint yet")
            return

        if depth_setpoint is None:
            self._loginfo("No depth setpoint yet")
            return

        # Sketchy minus signs...
        #depth_setpoint *= -1
        # current_depth *= -1

        depth_error = depth_setpoint - current_depth      
        
        a_brake = 0.005  # m/s^2  — was 0.10; tightened to match real SAM capability
        d_eps   = 0.5   # m      — was 1.5; reduced to match final_pos_tolerance

        surge_ref = np.sqrt(2.0 * a_brake * (current_distance + d_eps))
        current_surge = self._current_state.twist.twist.linear.x

        # Choose active vs. static diving based on dive pitch angle
        # if np.abs(dive_pitch_setpoint) <= self.param['max_dive_pitch']:

        # Choose active vs. static diving based on depth error, needed when
        # doing look ahead diving with fixed look ahead distance
        if current_depth is not None and depth_setpoint is not None:
            current_depth = np.abs(current_depth)
            depth_setpoint = np.abs(depth_setpoint)
            
        if np.abs(depth_error) <= 0.5:
            print("Active diving")
            self._dive_mode = "Active Diving"
            pitch_setpoint = -1.0 * dive_pitch_setpoint

            #u_rpm = rpm_setpoint
            u_rpm, surge_error, u_rpm_raw = self._surge_rpm_pid.get_control(current_surge, surge_ref, self._dt) 
            u_vbs_raw = self.param['vbs_u_neutral']
            u_lcg_raw = self.param['lcg_u_neutral']
            u_vbs = u_vbs_raw
            u_lcg = u_lcg_raw

            u_tv_rudder, yaw_error, u_tv_rudder_raw = self._yaw_pid.get_control(current_heading, heading_setpoint, self._dt)
            u_tv_stern, pitch_error, u_tv_stern_raw = self._pitch_tv_pid.get_control(current_pitch, pitch_setpoint, self._dt)
            depth_error = depth_setpoint - current_depth

        else:
            print("Static diving")
            self._dive_mode = "Static Diving"
            u_rpm = self.param['rpm_u_neutral']
            u_rpm_raw = self.param['rpm_u_neutral']
            u_tv_stern_raw = self.param['tv_u_neutral']
            u_tv_rudder_raw = self.param['tv_u_neutral']
            u_tv_stern = u_tv_stern_raw
            u_tv_rudder = u_tv_rudder_raw

            u_vbs, depth_error, u_vbs_raw = self._depth_vbs_pid.get_control(current_depth, depth_setpoint, self._dt)
            u_lcg, pitch_error, u_lcg_raw = self._pitch_lcg_pid.get_control(current_pitch, pitch_setpoint, self._dt)

            yaw_error = heading_setpoint - current_heading
            surge_error = current_surge - surge_ref

        # Sketchy minus sign for the stern steering because we need a positive
        # steering angle when compensating for a negative pitch
        u_tv_stern = -u_tv_stern

        print(f"Nacho u_vbs: {u_vbs :.3f}")

        self._dive_pub.set_vbs(u_vbs)
        self._dive_pub.set_lcg(u_lcg)
        self._dive_pub.set_thrust_vector(u_tv_rudder, u_tv_stern)
        self._dive_pub.set_rpm(u_rpm, u_rpm)

        # Convenience Topics
        #self._ref = ControlReference()
        #self._ref.z = depth_setpoint
        #self._ref.pitch = pitch_setpoint
        #self._ref.x = waypoint_odom.position.x
        #self._ref.y = waypoint_odom.position.y
        
        
        self._ref = Odometry() 
        self._ref.pose.pose.position.x = waypoint_odom.position.x
        self._ref.pose.pose.position.y = waypoint_odom.position.y
        self._ref.pose.pose.position.z = waypoint_odom.position.z
        self._ref.pose.pose.orientation.w = waypoint_odom.orientation.w
        self._ref.pose.pose.orientation.x = waypoint_odom.orientation.x
        self._ref.pose.pose.orientation.y = waypoint_odom.orientation.y
        self._ref.pose.pose.orientation.z = waypoint_odom.orientation.z

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
        self._input.thrusterrpm1 = float(u_rpm)
        self._input.thrusterrpm2 = float(u_rpm)
        
        if current_distance < 0.75:
            self.traj_index += 1
            
        self._dive_sub.set_current_idx(self.traj_index)

        # Debug prints
        s = f'\nPID INFO for index {self.traj_index}\n'
        s += f'state: frame: {self._current_state.header.frame_id}\n'
        s += f' x: {self._current_state.pose.pose.position.x:.3f}'
        s += f' y: {self._current_state.pose.pose.position.y:.3f}'
        s += f' z: {self._current_state.pose.pose.position.z:.3f}\n'
        s += f'state dr: frame: {self._current_state_in_dr.header.frame_id}\n'
        s += f' x: {self._current_state_in_dr.pose.pose.position.x:.3f}'
        s += f' y: {self._current_state_in_dr.pose.pose.position.y:.3f}'
        s += f' z: {self._current_state_in_dr.pose.pose.position.z:.3f}\n'
        s += f'wp odom: x: {waypoint_odom.position.x:.3f}'
        s += f' y: {waypoint_odom.position.y:.3f}'
        s += f' z: {waypoint_odom.position.z:.3f}\n '
        s += f'wp global: x: {waypoint_global.pose.position.x:.3f}'
        s += f' y: {waypoint_global.pose.position.y:.3f}'
        s += f' z: {waypoint_global.pose.position.z:.3f}\n'
        s += f'distance: {current_distance:.3f}\n'
        s += f'heading: {current_heading:.3f}\n'
        s += f'heading setpoint: {heading_setpoint:.3f}\n'
        s += f'pitch: {current_pitch:.3f} pitch setpoint: {pitch_setpoint:.3f}\n'
        s += f'dive pitch: {dive_pitch_setpoint:.3f}\n'
        s += f'rpm: {rpm_setpoint:.3f} surge error: {surge_error:.3f} surge ref: {surge_ref:.3f}\n'
        s += f'vbs: {u_vbs:.3f} lcg: {u_lcg:.3f}\n'
        s += f'tv stern: {u_tv_stern:.3f} tv rudder: {u_tv_rudder:.3f}\n'
        s += f'rpm1: {u_rpm:.3f} rpm2: {u_rpm:.3f} u_rpm_raw: {u_rpm_raw:.3f}\n'
        s += f'depth error: {depth_error:.3f} depth setpoint: {depth_setpoint:.3f}\n'
        s += f'pitch error: {pitch_error:.3f} pitch setpoint: {pitch_setpoint:.3f}\n'
        s += f'yaw error: {yaw_error:.3f}\n'

        self._loginfo(s)

        return
