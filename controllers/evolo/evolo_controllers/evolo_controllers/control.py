#! /usr/bin/env python3

## This node converts TwistStamped to 
# steering (Float32) and speed (Float32) for 
# evolo flight controller

import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TwistStamped
from rclpy.executors import MultiThreadedExecutor

from evolo_msgs.msg import Topics as evoloTopics
from smarc_msgs.msg import Topics as SmarcTopics
from smarc_control_msgs.msg import Topics as ControlTopics

#Basic PID regulator
class PID(object):

    def __init__(self,kP=None,kI=None,kD=None,max_output = None):
        self.kP = kP if kP is not None else 0.0
        self.kI = kI if kI is not None else 0.0
        self.kD = kD if kD is not None else 0.0
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
        self.declare_parameter("max_steering_output", 179.0) 
        self.max_steering_output = float(self.get_parameter("max_steering_output").value)

        self.declare_parameter("max_speed", 6) #m/s ~12 knots
        self.max_speed = self.get_parameter("max_speed").value

        #Open or closed loop control
        self.declare_parameter("closed_loop_control", False)
        self.closed_loop_ctrl = self.get_parameter("closed_loop_control").value

        #Closed loop gains
        self.declare_parameter("closed_loop_p_gain", 0.0)
        self.declare_parameter("closed_loop_i_gain", 0.0)
        self.declare_parameter("closed_loop_d_gain", 0.0)
        self.closed_loop_p_gain = float(self.get_parameter("closed_loop_p_gain").value)
        self.closed_loop_i_gain = float(self.get_parameter("closed_loop_i_gain").value)
        self.closed_loop_d_gain = float(self.get_parameter("closed_loop_d_gain").value)

        self.PID = PID(self.closed_loop_p_gain, self.closed_loop_i_gain, self.closed_loop_d_gain)

        #Open loop gain
        self.declare_parameter("open_loop_gain", 3.0)
        self.open_loop_gain = self.get_parameter("open_loop_gain").value

        self.logger.info(f"Starting evolo controllers with settings \n \
                    update_rate: {self.update_rate}\n \
                    robot_name: {self.robot_name}\n \
                    max_steering_output: {self.max_steering_output}\n \
                    max_speed: {self.max_speed}\n \
                    closed_loop_control: {self.closed_loop_ctrl}\n \
                    closed_loop_p_gain: {self.closed_loop_p_gain}\n \
                    closed_loop_i_gain: {self.closed_loop_i_gain}\n \
                    closed_loop_d_gain: {self.closed_loop_d_gain}\n \
                    open_loop_gain: {self.open_loop_gain}\n")


        #Setpoint
        self.twist_setpoint = None
        self.twist_setpoint_time = None

        #Feedback
        self.odom_feedback = None
        self.odom_feedback_time = None

        #Inputs
        self.create_subscription(TwistStamped, evoloTopics.EVOLO_TWIST_SETPOINT , self.twist_cb, 1)
        self.create_subscription(Odometry, SmarcTopics.ODOM_TOPIC , self.odom_cb, 1)

        #Outputs
        self.steering_pub = self.create_publisher(Float32, evoloTopics.EVOLO_STEERING_SETPOINT, 1)
        self.speed_pub = self.create_publisher(Float32, evoloTopics.EVOLO_SPEED_SETPOINT, 1)

    def time_now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def odom_cb(self,msg : Odometry):
        self.odom_feedback = msg
        self.odom_feedback_time = self.time_now()

    def twist_cb(self, msg : TwistStamped):
        self.twist_setpoint = msg
        self.twist_setpoint_time = self.time_now()


    def update(self):
        now = self.time_now()

        setpoint_OK = self.twist_setpoint_time is not None and now-self.twist_setpoint_time < 1 and self.twist_setpoint is not None
        feedback_OK = self.odom_feedback is not None and now - self.odom_feedback_time < 1

        if(self.closed_loop_ctrl):
            if(setpoint_OK and feedback_OK): #Closed loop control
                target_speed = max(0, min( self.max_speed, self.twist_setpoint.twist.linear.x)) #m/s
                target_turnRate_deg = math.degrees(self.twist_setpoint.twist.angular.z) #deg/s
                feedback_turnRate_deg = math.degrees(self.odom_feedback.twist.twist.angular.z) #deg/s

                error = target_turnRate_deg - feedback_turnRate_deg
                pid_output = self.PID.update_error(error, self.time_now())

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

        else: #Open loop control
            if(setpoint_OK):

                #speed = math.sqrt((self.twist_setpoint.twist.linear.x * self.twist_setpoint.twist.linear.x) + 
                #                (self.twist_setpoint.twist.linear.y*self.twist_setpoint.twist.linear.y))
                #steering = math.atan2(self.twist_setpoint.twist.linear.y, self.twist_setpoint.twist.linear.x) # Not used?
                
                speed = max(0, min( self.max_speed, self.twist_setpoint.twist.linear.x)) #m/s
                turnRate_deg = math.degrees(self.twist_setpoint.twist.angular.z)

                steering_output = max(-self.max_steering_output, min(self.max_steering_output, turnRate_deg * self.open_loop_gain))

                steering_msg = Float32()
                steering_msg.data = float(steering_output)
                self.steering_pub.publish(steering_msg)

                speed_msg = Float32()
                speed_msg.data = float(speed)
                self.speed_pub.publish(speed_msg)

                self.logger.info(f"Open loop control")
            else:
                self.logger.info(f"No setpoint")


def main(args=None, namespace=None):
    rclpy.init(args=args)
    control_node = twist_control()

    control_node.create_timer(1.0/control_node.update_rate, control_node.update)
    executor = MultiThreadedExecutor()
    executor.add_node(control_node)
    executor.spin()
