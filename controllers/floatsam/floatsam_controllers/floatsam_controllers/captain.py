#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# FloatSam Captain - Integrated controller for surface USV

import numpy as np
import rclpy
import json
from rclpy.node import Node
from std_msgs.msg import Float32
from std_msgs.msg import String
from rclpy.executors import MultiThreadedExecutor

from smarc_msgs.msg import Topics as SmarcTopics
from smarc_msgs.msg import FloatStamped
from smarc_control_msgs.msg import Topics as ControlTopics
from floatsam_msgs.msg import Topics as FloatsamTopics
from std_msgs.msg import Bool

from floatsam_controllers.pid import PID
import floatsam_controllers.geometry as geom


class Captain(Node):
    """
    Captain is the main controller for FloatSam USV.
    
    It integrates:
    - 3 PID controllers (yaw, yaw_rate, velocity) as Python objects
    - Control signal mixing (differential thrust)
    - Delta RPM rate limiting for safety
    
    All PID gains are configurable via launch file parameters.
    """
    def __init__(self):
        super().__init__("captain_node")
        self.logger = self.get_logger()
        self.logger.info("Initializing FloatSam Captain node!")

        self.declare_node_parameters()

        self.update_rate = float(self.get_parameter("update_rate").value)
        self.logger.info(f"Update rate: {self.update_rate} Hz")
        self.robot_name = self.get_parameter("robot_name").value
        self.yaw_threshold = float(self.get_parameter("yaw_threshold").value)
        self.move_on_place_flag = True

        
        self.yaw_pid = PID(
            kP=float(self.get_parameter("yaw_p_gain").value),
            kI=float(self.get_parameter("yaw_i_gain").value),
            kD=float(self.get_parameter("yaw_d_gain").value),
            max_output=float(self.get_parameter("yaw_output_limit").value)
        )
        
        self.yawrate_pid = PID(
            kP=float(self.get_parameter("yawrate_p_gain").value),
            kI=float(self.get_parameter("yawrate_i_gain").value),
            kD=float(self.get_parameter("yawrate_d_gain").value),
            max_output=float(self.get_parameter("yawrate_output_limit").value)
        )
        
        self.velocity_pid = PID(
            kP=float(self.get_parameter("velocity_p_gain").value),
            kI=float(self.get_parameter("velocity_i_gain").value),
            kD=float(self.get_parameter("velocity_d_gain").value),
            max_output=float(self.get_parameter("velocity_output_limit").value)
        )
        
        self.logger.info("Initialized 3 PID controllers with configurable gains")

        
        self.rpm_deadband = float(self.get_parameter("rpm_deadband").value)
        self.thruster_limit = float(self.get_parameter("thruster_limit").value)
        
        self.turn_in_place_min_rpm = float(self.get_parameter("turn_in_place_min_rpm").value)
        self.turn_in_place_gain = float(self.get_parameter("turn_in_place_gain").value)
        
        self.max_delta_rpm = float(self.get_parameter("max_delta_rpm").value)
        self.last_thruster_port_cmd = 0.0
        self.last_thruster_strb_cmd = 0.0
                
        self.yaw_measurement = 0.0
        self.yaw_rate_measurement = 0.0
        self.velocity_measurement = 0.0
        
        self.yaw_setpoint = 0.0
        self.velocity_setpoint = 0.0
        
        self.last_yaw_meas_time = 0.0
        self.last_yawrate_meas_time = 0.0
        self.last_velocity_meas_time = 0.0
        self.last_yaw_setpoint_time = 0.0
        self.last_velocity_setpoint_time = 0.0

        
        self.create_subscription(Float32, ControlTopics.CONTROL_YAW_TOPIC,
                                 self.yaw_meas_cb, 1)
        self.create_subscription(Float32, ControlTopics.CONTROL_YAW_RATE_TOPIC,
                                 self.yawrate_meas_cb, 1)
        self.create_subscription(Float32, ControlTopics.CONTROL_SURGE_RATE_TOPIC,
                                 self.velocity_meas_cb, 1)
    
        
        self.create_subscription(FloatStamped, FloatsamTopics.YAW_SETPOINT,
                                 self.yaw_setpoint_cb, 1)
        self.create_subscription(FloatStamped, FloatsamTopics.VELOCITY_SETPOINT,
                                 self.velocity_setpoint_cb, 1)
        

        self.create_subscription(String, 
                                 f"/{self.robot_name}/captain_parameters",
                                 self.captain_parameters_cb, 1
                                 )
        
        self.create_subscription(Bool, 'move_on_place', self.move_on_place_cb, 1)
        
        self.thruster_port_msg = Float32()
        self.thruster_strb_msg = Float32()
        
        self.thruster_port_pub = self.create_publisher(Float32,
                                                       FloatsamTopics.THRUSTER_PORT_CMD, 1)
        self.thruster_strb_pub = self.create_publisher(Float32,
                                                       FloatsamTopics.THRUSTER_STRB_CMD, 1)
        
        

    def time_now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def declare_node_parameters(self):
        """Declare all configurable parameters for PIDs and mixer"""
        self.declare_parameter("robot_name", "floatsam_usv")
        self.declare_parameter("update_rate", 20.0)
        
        self.declare_parameter("yaw_p_gain", 0.15)
        self.declare_parameter("yaw_i_gain", 0.0)
        self.declare_parameter("yaw_d_gain", 0.0)
        self.declare_parameter("yaw_output_limit", 0.1)  # rad/s
        self.declare_parameter("yaw_threshold", 0.5)
        
        self.declare_parameter("yawrate_p_gain", 20.0)
        self.declare_parameter("yawrate_i_gain", 0.0)
        self.declare_parameter("yawrate_d_gain", 0.0)
        self.declare_parameter("yawrate_output_limit", 800.0)  # RPM
        
        self.declare_parameter("velocity_p_gain", 500.0)
        self.declare_parameter("velocity_i_gain", 10.0)
        self.declare_parameter("velocity_d_gain", 0.0)
        self.declare_parameter("velocity_output_limit", 800.0)  # RPM
        
        self.declare_parameter("rpm_deadband", 50.0)  # RPM
        self.declare_parameter("thruster_limit", 1000.0)  # RPM
        self.declare_parameter("max_delta_rpm", 200.0)  # RPM per control cycle
        self.declare_parameter("turn_in_place_min_rpm", 100.0)  # RPM, minimum to overcome stiction
        self.declare_parameter("turn_in_place_gain", 10.0)  # RPM per radian of heading error

    # Callbacks: Sensor measurements
    
    def yaw_meas_cb(self, msg):
        self.last_yaw_meas_time = self.time_now()
        self.yaw_measurement = msg.data 


    def yawrate_meas_cb(self, msg):
        self.last_yawrate_meas_time = self.time_now()
        self.yaw_rate_measurement = msg.data


    def velocity_meas_cb(self, msg):
        self.last_velocity_meas_time = self.time_now()
        self.velocity_measurement = msg.data

    def move_on_place_cb(self, msg):
        self.move_on_place_flag = msg.data
    
    def yaw_setpoint_cb(self, msg):

        self.last_yaw_setpoint_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        self.yaw_setpoint = msg.data

    def velocity_setpoint_cb(self, msg):
        self.last_velocity_setpoint_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        self.velocity_setpoint_input = msg.data

    def captain_parameters_cb(self, msg):
        try:
            paramaters = json.loads(msg.data)
            self.yaw_pid.kP = float(paramaters["yaw_p_gain"])
            self.yaw_pid.kI = float(paramaters["yaw_i_gain"])
            self.yaw_pid.kD = float(paramaters["yaw_d_gain"])
            self.yaw_threshold = float(paramaters["yaw_threshold"])   
            self.yawrate_pid.kP = float(paramaters["yawrate_p_gain"])
            self.yawrate_pid.kI = float(paramaters["yawrate_i_gain"])
            self.yawrate_pid.kD = float(paramaters["yawrate_d_gain"])
            self.velocity_pid.kP = float(paramaters["velocity_p_gain"])
            self.velocity_pid.kI = float(paramaters["velocity_i_gain"])
            self.velocity_pid.kD = float(paramaters["velocity_d_gain"])
            
        except Exception as e:
            self.logger.error(f"Failed to parse captain parameters: {e}")
    
    # Rate limiter (delta RPM health check)
    def apply_rate_limit(self, new_cmd, last_cmd, name):
        """
        Limit the rate of change of thruster commands.
        
        Args:
            new_cmd: Newly computed thruster command (RPM)
            last_cmd: Previous thruster command (RPM)
            name: Thruster name for logging
            
        Returns:
            Rate-limited command (RPM)
        """
        delta = new_cmd - last_cmd
        
        if abs(delta) > self.max_delta_rpm:
            limited_delta = self.max_delta_rpm if delta > 0 else -self.max_delta_rpm
            limited_cmd = last_cmd + limited_delta
            return limited_cmd
        
        return new_cmd

    def compute_turn_in_place_actuation(self, yaw_error, yaw_actuation):
            """
            Compute a stable yaw actuation for turn-in-place behaviour.
            - Use the sign of `yaw_error` to determine rotation direction to
                avoid oscillation when the PID output crosses zero.
            - Ensure a minimum RPM magnitude to overcome stiction and
                accelerate convergence, and scale with error magnitude.
            - Limit to `thruster_limit`.
            """
            err_mag = abs(yaw_error)
            if err_mag == 0.0:
                    return 0.0
            mag = max(abs(yaw_actuation), self.turn_in_place_min_rpm, self.turn_in_place_gain * err_mag)
            mag = min(mag, self.thruster_limit)
            return np.sign(yaw_error) * mag

    def update(self):
        """
        Main control loop: Run PIDs, mix signals, apply safety limits.
        
        Control flow:
        1. Check timeouts on all inputs
        2. Run Yaw PID (angle → rate)
        3. Run Yaw Rate PID (rate → actuation)
        4. Run Velocity PID (velocity → RPM)
        5. Mix yaw actuation + velocity RPM into differential thrust
        6. Apply delta RPM rate limiting
        7. Apply saturation and deadband
        8. Publish thruster commands
        """
        now = self.time_now()
        timeout = 1.0  
        
        measurements_ok = (
            (now - self.last_yaw_meas_time) < timeout and
            (now - self.last_yawrate_meas_time) < timeout and
            (now - self.last_velocity_meas_time) < timeout
        )
        

        setpoints_ok = (
            (now - self.last_yaw_setpoint_time) < timeout and
            (now - self.last_velocity_setpoint_time) < timeout
        )
        
        
        if not measurements_ok or not setpoints_ok:
            self.thruster_port_msg.data = 0.0
            self.thruster_strb_msg.data = 0.0
            self.thruster_port_pub.publish(self.thruster_port_msg)
            self.thruster_strb_pub.publish(self.thruster_strb_msg)
            
            self.last_thruster_port_cmd = 0.0
            self.last_thruster_strb_cmd = 0.0
            return

        # --- PID Control Cascade ---
        
        setpoint_vec = np.array([np.cos(self.yaw_setpoint), np.sin(self.yaw_setpoint)])
        measurement_vec = np.array([np.cos(self.yaw_measurement), np.sin(self.yaw_measurement)])
        yaw_error = -geom.vec2_directed_angle(setpoint_vec, measurement_vec)
        
        yaw_rate_setpoint = self.yaw_pid.update_error(yaw_error, now)
        
        yaw_rate_error = yaw_rate_setpoint - self.yaw_rate_measurement
        yaw_actuation = self.yawrate_pid.update_error(yaw_rate_error, now)
        

        if np.abs(yaw_error) <= self.yaw_threshold or not self.move_on_place_flag:
            velocity_error = self.velocity_setpoint_input - self.velocity_measurement
            velocity_rpm_setpoint = self.velocity_pid.update_error(velocity_error, now)
        else:
            velocity_rpm_setpoint = 0
            
        
        if velocity_rpm_setpoint == 0:
            yaw_correction = self.compute_turn_in_place_actuation(yaw_error, yaw_actuation)
        else:
            yaw_correction = yaw_actuation
        
        thruster_port_raw = velocity_rpm_setpoint - yaw_correction
        thruster_strb_raw = velocity_rpm_setpoint + yaw_correction
        
        thruster_port = self.apply_rate_limit(
            thruster_port_raw, 
            self.last_thruster_port_cmd,
            "Port"
        )
        
        thruster_strb = self.apply_rate_limit(
            thruster_strb_raw,
            self.last_thruster_strb_cmd,
            "Starboard"
        )

        thruster_port = max(-self.thruster_limit, min(self.thruster_limit, thruster_port))
        thruster_strb = max(-self.thruster_limit, min(self.thruster_limit, thruster_strb))

        if abs(thruster_port) < self.rpm_deadband:
            thruster_port = 0.0
        if abs(thruster_strb) < self.rpm_deadband:
            thruster_strb = 0.0

        self.thruster_port_msg.data = thruster_port
        self.thruster_strb_msg.data = thruster_strb
        
        self.thruster_port_pub.publish(self.thruster_port_msg)
        self.thruster_strb_pub.publish(self.thruster_strb_msg)
        
        self.last_thruster_port_cmd = thruster_port
        self.last_thruster_strb_cmd = thruster_strb


def main(args=None, namespace=None):
    rclpy.init(args=args)
    captain_node = Captain()

    captain_node.create_timer(1.0/captain_node.update_rate, captain_node.update)
    executor = MultiThreadedExecutor()
    executor.add_node(captain_node)
    executor.spin()

if __name__ == '__main__':
    main()
