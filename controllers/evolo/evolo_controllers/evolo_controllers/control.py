#! /usr/bin/env python3

## This node converts the Odometry control message to 
# steering (Float32) and speed (Float32) for 
# evolo flight controller

import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from nav_msgs.msg import Odometry
from rclpy.executors import MultiThreadedExecutor

from transforms3d.euler import quat2euler

from evolo_msgs.msg import Topics as evoloTopics
from smarc_msgs.msg import Topics as SmarcTopics
from smarc_control_msgs.msg import Topics as ControlTopics
import numpy as np

def vec2_directed_angle(v1, v2):
    """
    # Author: Ozer Ozkahraman (ozkahramanozer@gmail.com)
    # Date: 2018-07-10

    returns the shortest angle from v1 to v2 in radians.
    v1 + angle = v2.

    positive value means ccw rotation from v1 to v2.
    negative value means cw.

    v1, v2 can be (N,2)
    """
    v1 = np.array(np.atleast_2d(v1))
    v2 = np.array(np.atleast_2d(v2))
    assert v1.shape == v2.shape

    x1s = v1[:,0]
    x2s = v2[:,0]
    y1s = v1[:,1]
    y2s = v2[:,1]

    dots = x1s*x2s + y1s*y2s
    dets = x1s*y2s - y1s*x2s

    angles = np.arctan2(dets,dots)

    N,_ = v1.shape
    if N == 1:
        return angles[0]
    else:
        return angles


#Basic PID regulator
class PID(object):

    def __init__(self,kP=None,kI=None,kD=None,max_output = None, max_integral = None):
        self.kP = kP if kP is not None else 0.0
        self.kI = kI if kI is not None else 0.0
        self.kD = kD if kD is not None else 0.0
        self.max_output = max_output
        self.integral = 0
        self.max_integral = max_integral if max_integral is not None else max_output
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
        if self.max_integral is not None:
            if(self.integral > self.max_integral): self.integral = self.max_integral
            if(self.integral < -self.max_integral): self.integral = -self.max_integral

        output = proportional + self.integral + derivative
        self.last_update = current_time_s
        self.last_error = error

        return max(-self.max_output, min(self.max_output, output)) if self.max_output is not None else output

#Evolo speed and steering controller
class twist_control(Node):
    def __init__(self):
        super().__init__("evolo_control")
        self.logger = self.get_logger()

        self.declare_parameter("update_rate", 10)
        self.update_rate = float(self.get_parameter("update_rate").value)

        self.declare_parameter("robot_name", "evolo")
        self.robot_name = self.get_parameter("robot_name").value

        #limits
        self.declare_parameter("max_steering_output", 40.0) 
        self.max_steering_output = float(self.get_parameter("max_steering_output").value)

        self.declare_parameter("max_speed", 6) #m/s ~12 knots
        self.max_speed = self.get_parameter("max_speed").value


        #Closed loop gains
        self.declare_parameter("closed_loop_p_gain", 0.0)
        self.declare_parameter("closed_loop_i_gain", 0.0)
        self.declare_parameter("closed_loop_d_gain", 0.0)
        self.declare_parameter("max_integral", 10.0)
        self.closed_loop_p_gain = float(self.get_parameter("closed_loop_p_gain").value)
        self.closed_loop_i_gain = float(self.get_parameter("closed_loop_i_gain").value)
        self.closed_loop_d_gain = float(self.get_parameter("closed_loop_d_gain").value)
        self.max_integral = float(self.get_parameter("max_integral").value)

        self.PID = PID(self.closed_loop_p_gain,
                       self.closed_loop_i_gain,
                       self.closed_loop_d_gain,
                       self.max_steering_output,
                       self.max_integral)

        #Open loop gain
        self.declare_parameter("open_loop_gain", 3.0)
        self.open_loop_gain = self.get_parameter("open_loop_gain").value

        self.logger.info(f"Starting evolo controllers with settings \n \
                    update_rate: {self.update_rate}\n \
                    robot_name: {self.robot_name}\n \
                    max_steering_output: {self.max_steering_output}\n \
                    max_speed: {self.max_speed}\n \
                    closed_loop_p_gain: {self.closed_loop_p_gain}\n \
                    closed_loop_i_gain: {self.closed_loop_i_gain}\n \
                    closed_loop_d_gain: {self.closed_loop_d_gain}\n \
                    open_loop_gain: {self.open_loop_gain}\n")


        #Setpoints
        self.yaw_setpoint = None
        self.linear_vel_setpoint = None
        self.odom_ctrl_time = None

        #Feedback
        self.yaw_feedback = None
        self.odom_feedback_time = None

        #Inputs
        self.create_subscription(Odometry, evoloTopics.EVOLO_CONTROL_SETPOINT , self.odom_ctrl_cb, 1)
        self.create_subscription(Odometry, SmarcTopics.ODOM_TOPIC , self.odom_cb, 1)

        #Outputs
        self.steering_pub = self.create_publisher(Float32, evoloTopics.EVOLO_STEERING_SETPOINT, 1)
        self.speed_pub = self.create_publisher(Float32, evoloTopics.EVOLO_SPEED_SETPOINT, 1)

    def time_now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def odom_cb(self,msg : Odometry):
        self.odom_feedback = msg
        _,_,self.yaw_feedback = quat2euler([msg.pose.pose.orientation.w,
                                            msg.pose.pose.orientation.x,
                                            msg.pose.pose.orientation.y,
                                            msg.pose.pose.orientation.z],
                                            axes='sxyz')
        self.odom_feedback_time = self.time_now()

    def odom_ctrl_cb(self, msg : Odometry):
        _,_,self.yaw_setpoint = quat2euler([msg.pose.pose.orientation.w,
                                            msg.pose.pose.orientation.x,
                                            msg.pose.pose.orientation.y,
                                            msg.pose.pose.orientation.z],
                                            axes='sxyz')
        self.linear_vel_setpoint = msg.twist.twist.linear.x
        self.odom_ctrl_time = self.time_now()


    def update(self):
        now = self.time_now()

        setpoint_OK = self.odom_ctrl_time is not None and now-self.odom_ctrl_time < 1 and self.yaw_setpoint is not None and self.linear_vel_setpoint is not None
        feedback_OK = self.yaw_feedback is not None and now - self.odom_feedback_time < 1

        if(setpoint_OK and feedback_OK): #Closed loop control
            target_speed = max(0, min( self.max_speed, self.linear_vel_setpoint)) #m/s
            setpoint = np.array([np.cos(self.yaw_setpoint) , np.sin(self.yaw_setpoint)])
            meassurement = np.array([np.cos(self.yaw_feedback) , np.sin(self.yaw_feedback)])
            angle_error_rads = -vec2_directed_angle(setpoint,
                                                    meassurement)
            angle_error_degs = math.degrees(angle_error_rads)

            pid_output = self.PID.update_error(angle_error_degs, self.time_now())

            steering_output = max(-self.max_steering_output, min(self.max_steering_output, pid_output))

            steering_msg = Float32()
            steering_msg.data = float(steering_output)
            self.steering_pub.publish(steering_msg)

            speed_msg = Float32()
            speed_msg.data = float(target_speed)
            self.speed_pub.publish(speed_msg)

            self.logger.info(f"Closed loop control")
        else:
            self.logger.info(f"No setpoint or no feedback)")



def main(args=None, namespace=None):
    rclpy.init(args=args)
    control_node = twist_control()

    control_node.create_timer(1.0/control_node.update_rate, control_node.update)
    executor = MultiThreadedExecutor()
    executor.add_node(control_node)
    executor.spin()
