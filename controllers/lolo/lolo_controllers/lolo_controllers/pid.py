#! /usr/bin/env python3

import math
import numpy as np
import lolo_controllers.geometry as geom

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

from std_msgs.msg import Float32

#Basic PID regulator
class PID(object):

    def __init__(self,kP=None,kI=None,kD=None,max_output = None):
        self.kP = kP if kP is not None else 0
        self.kI = kI if kI is not None else 0
        self.kD = kD if kD is not None else 0
        self.max_output = max_output
        self.integral = 0
        self.last_update = None
        self.last_error = None
        self.last_derivative = None
        self._fCut = 20

    def reset(self):
        self.integral = 0
        self.last_update = None
        self.last_meassurement = None

    def update_error(self, error, time_s):
        #print("PID update: " + str(error))
        current_time_s = time_s
        dt = current_time_s - self.last_update if self.last_update is not None else None

        #reset I of dt > 1s
        if(dt is not None and dt > 1):
            self.integral = 0
            self.last_derivative = None

        proportional = self.kP*error
        if dt is not None and dt < 1: self.integral +=  dt*self.kI*error

        if dt is not None and self.last_error is not None and self.last_derivative is not None:
            derivative = self.kD*(error - self.last_error) / dt

            # discrete low pass filter, cuts out the
            # high frequency noise that can drive the controller crazy
            RC = 1/(2*math.pi*self._fCut)
            derivative = self.last_derivative + ((dt / (RC + dt))*(derivative - self.last_derivative))
        else:
            derivative = 0
        self.last_derivative = derivative

        #prevent integral windup
        if self.max_output is not None:
            if(self.integral > self.max_output): self.integral = self.max_output
            if(self.integral < -self.max_output): self.integral = -self.max_output

        output = proportional + self.integral + derivative
        self.last_update = current_time_s
        self.last_error = error

        return max(-self.max_output, min(self.max_output, output)) if self.max_output is not None else output



#Wrapper for the PID class with subscribers and publishers
class PID_wrapper(Node):
    def __init__(self):
        super().__init__("pid_node")

        self.logger = self.get_logger()

        self.declare_node_parameters()

        self.robot_name = self.get_parameter("robot_name").value

        self.output = Float32()
        self.meassurement = 0
        self.meassurement_time = 0
        self.setpoint = 0
        self.setpoint_time = 0
        self.pid = PID
        self.version = self.get_parameter("controller_type").value
        self.update_rate = float(self.get_parameter("update_rate").value)
        self.pid = PID(float(self.get_parameter("p_gain").value),
                    float(self.get_parameter("i_gain").value),
                    float(self.get_parameter("d_gain").value),
                    float(self.get_parameter("output_limit").value))

        self.create_subscription(Float32, self.get_parameter("meassurement_topic").value,
                                 self.meassurement_cb, 1)
        self.create_subscription(Float32, self.get_parameter("setpoint_topic").value,
                                 self.setpoint_cb, 1)
        self.output_pub = self.create_publisher(Float32, self.get_parameter("output_topic").value,
                                                1)

    def declare_node_parameters(self):
        self.declare_parameter("robot_name", "lolo")
        self.declare_parameter("controller_type", "Normal")
        self.declare_parameter("update_rate", 20.0)
        self.declare_parameter("p_gain", 0.0)
        self.declare_parameter("i_gain", 0.0)
        self.declare_parameter("d_gain", 0.0)
        self.declare_parameter("output_limit", 0.0)
        self.declare_parameter("meassurement_topic", "/pid_test/meassurement")
        self.declare_parameter("setpoint_topic", "/pid_test/setpoint")
        self.declare_parameter("output_topic", "/pid_test/output")

    def time_now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def meassurement_cb(self, msg):
        self.meassurement_time = self.time_now()
        self.meassurement = msg.data

    def setpoint_cb(self, msg):
        self.setpoint_time = self.time_now()
        self.setpoint = msg.data

    def update(self):
        #Check if we have timed out
        #print("wrapper update")
        now = self.time_now()
        if(now - self.meassurement_time < 1 and now - self.setpoint_time < 1):
            if self.version == 'yaw':
                setpoint = np.array([np.cos(self.setpoint) , np.sin(self.setpoint)])
                meassurement = np.array([np.cos(self.meassurement) , np.sin(self.meassurement)])
                error = -geom.vec2_directed_angle(setpoint, meassurement)
                #print("Yaw controller update")
            else:
                error = self.setpoint - self.meassurement
            self.output.data = self.pid.update_error(error, self.time_now())
            self.output_pub.publish(self.output)
        else:
            #print("setpoint or meassurement timout")
            pass


def main(args=None, namespace=None):
    rclpy.init(args=args)
    pid_node = PID_wrapper()

    pid_node.create_timer(1.0/pid_node.update_rate, pid_node.update)
    executor = MultiThreadedExecutor()
    executor.add_node(pid_node)
    executor.spin()
