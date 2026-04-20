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

        #Open loop gain
        self.declare_parameter("open_loop_gain", 3.0)
        self.open_loop_gain = self.get_parameter("open_loop_gain").value

        self.twist_setpoint = None
        self.twist_setpoint_time = None

        self.odom_feedback = None
        self.odom_feedback_time = None

        #Control inputs.
        self.create_subscription(TwistStamped, evoloTopics.EVOLO_TWIST_SETPOINT , self.twist_cb, 1)

        #Feedback
        self.create_subscription(Odometry, SmarcTopics.ODOM_TOPIC , self.odom_cb, 1)

        #Outputs
        self.steering_pub = self.create_publisher(Float32, evoloTopics.EVOLO_STEERING_SETPOINT, 1)
        self.speed_pub = self.create_publisher(Float32, evoloTopics.EVOLO_SPEED_SETPOINT, 1)

    def time_now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def odom_cb(self,msg):
        self.odom_feedback = msg
        self.odom_feedback_time = self.time_now()

    def twist_cb(self, msg):
        self.twist_setpoint = msg
        self.twist_setpoint_time = self.time_now()


    def update(self):
        now = self.time_now()

        setpoint_OK = self.twist_setpoint_time is not None and now-self.twist_setpoint_time < 1 and self.twist_setpoint is not None
        feedback_OK = self.odom_feedback is not None and now - self.odom_feedback_time < 1

        #TODO closed loop control in the future
        if(self.closed_loop_ctrl):
            self.logger.info(f"Closed loop control is not implemented")
        else:    
            #Open loop control
            if(setpoint_OK):

                #speed = math.sqrt((self.twist_setpoint.twist.linear.x * self.twist_setpoint.twist.linear.x) + 
                #                (self.twist_setpoint.twist.linear.y*self.twist_setpoint.twist.linear.y))
                #steering = math.atan2(self.twist_setpoint.twist.linear.y, self.twist_setpoint.twist.linear.x) # Not used?
                
                speed = max(0, min( self.max_speed, self.twist_setpoint.twist.linear.x)) #m/s
                turnRate_deg = math.degrees(self.twist_setpoint.twist.angular.z)

                steering_output = max(-self.max_steering_output, min(self.max_steering_output, turnRate_deg * self.open_loop_gain)) #rad/s

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
