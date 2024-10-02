#!/usr/bin/env python3

"""
MIT License

Copyright (c) 2023 Matthew Lock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Create a ROS node determines the setpoints for the SAM thrusters based on the joystick input


import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Float64
from geometry_msgs.msg import Twist
from sam_msgs.msg import ThrusterAngles, ThrusterRPMs
from smarc_msgs.msg import ThrusterRPM

from sam_msgs.msg import JoyButtons,Topics
from dead_reckoning_msgs.msg import Topics as DR_Topics
import math

class teleop(Node):
    
    # ================================================================================
    # Callback Functions
    # ================================================================================

    def joy_btns_callback(self, msg:JoyButtons):
        """
        Callback function for the joystick subscriber
        """

        RPM_MAX = 1500
        RAD_MAX = 0.1
        RPM_LINEAR_STEP_SIZE = 1/15

        RAD_STEPS = 5
        RAD_STEP_SIZE = RAD_MAX / RAD_STEPS
        LINEAR_STEP_SIZE = 1/RAD_STEPS

        if self.teleop_enabled:

            rpm_cmd = int(msg.left_y* RPM_MAX)
            x_cmd = msg.right_x * RAD_MAX
            y_cmd = msg.right_y * RAD_MAX

            # Round rpm_cmd to nearest 100
            rpm_cmd = int(round(rpm_cmd, -2))

            # Round x_cmd and y_cmd to nearest value on range RAD_MIN to RAD_MAX with RAD_STEPS steps
            x_steps = round(x_cmd / RAD_STEP_SIZE)
            x_cmd = x_steps * RAD_STEP_SIZE
            y_steps = round(y_cmd / RAD_STEP_SIZE)
            y_cmd = y_steps * RAD_STEP_SIZE

            
            # If assisted depth-keeping, ctrl_msg.angular.y is overriden by PID controller
            y_cmd = max(min(y_cmd, 0.1), -0.1)  # Elevator boundaries
            # elev_cmd = self.elev_effort if self.assisted_driving_enabled else y_cmd

            self.rpm_msg.thruster_1_rpm = int(rpm_cmd)
            self.rpm_msg.thruster_2_rpm = int(rpm_cmd)
            self.vec_msg.thruster_horizontal_radians = - x_cmd
            self.vec_msg.thruster_vertical_radians = y_cmd



    def send_cmds(self):
        if self.rpm_msg.thruster_1_rpm != 0 or not self.published_zero_rpm_once:
            rpm_msg = ThrusterRPM()        
            rpm_msg.rpm = self.rpm_msg.thruster_1_rpm
            self.thrrust1_pub.publish(rpm_msg)
            rpm_msg.rpm = self.rpm_msg.thruster_2_rpm
            self.thrrust2_pub.publish(rpm_msg)    
            
            self.thruster_pub.publish(self.rpm_msg)
            zero = self.rpm_msg.thruster_1_rpm == 0
            
            if zero:
                self.get_logger().info(">>>>> Published 0 RPM")
            else:
                self.get_logger().info(f"RPM: {self.rpm_msg.thruster_1_rpm}", throttle_duration_sec=1)
            self.published_zero_rpm_once = zero

        if self.vec_msg.thruster_horizontal_radians != 0 or \
           self.vec_msg.thruster_vertical_radians != 0 or \
           not self.published_zero_vec_once:

            if self.assisted_driving_enabled:
                elev_cmd = self.elev_effort
                self.vec_msg.thruster_vertical_radians = elev_cmd
            self.vector_pub.publish(self.vec_msg)

            zero = self.vec_msg.thruster_horizontal_radians == 0 and\
                   self.vec_msg.thruster_vertical_radians == 0
            
            if zero:
                self.get_logger().info(">>>>> Published 0 thrust vector")
            else:
                self.get_logger().info(f"Vec: {self.vec_msg.thruster_horizontal_radians}, {self.vec_msg.thruster_vertical_radians}", throttle_duration_sec=1)
            self.published_zero_vec_once = zero


            
    def teleop_enabled_callback(self, msg: Bool):
        """
        Callback function for the teleop enabled subscriber
        """
        self.teleop_enabled = msg.data

    def assisted_driving_callback(self, msg: Bool):
        """
        Callback function for the assisted driving subscriber
        """
        self.assisted_driving_enabled = msg.data
        self.start_ad = msg.data

    def depth_cb(self, msg:Float64):

        if self.assisted_driving_enabled:

            # Lock current depth when assisted driving is turned on to
            # be used as PID setpoint
            if self.start_ad:
                self.depth_sp = msg.data
                self.start_ad = False
            self.elev_sp_pub.publish(Float64(self.depth_sp))

    def elev_pid_cb(self, msg:Float64):

        self.elev_effort = msg.data

    # ================================================================================
    # Node Init
    # ================================================================================

    def __init__(self):

        # pub = rospy.Publisher('chatter', String, queue_size=10)
        super().__init__('ds5_teleop')
        self.declare_parameter("rpm_joystick_top", "/rpm_joystick")
        
        rpm_joystick_top = self.get_parameter("rpm_joystick_top").value
        
        self.declare_parameter("vector_deg_joystick_top", "/vector_deg_joystick")
        vector_deg_joystick_top = self.get_parameter("vector_deg_joystick_top").value
         
        
        self.declare_parameter("teleop_enable", "/enable")
        teleop_enable_top = self.get_parameter("teleop_enable").value

        self.declare_parameter("assist_enable", "/assist")
        assist_enable_top = self.get_parameter("assist_enable").value
        
        self.declare_parameter("joy_buttons", "/joy_buttons")
        joy_buttons_top = self.get_parameter("joy_buttons").value
        
        
        self.declare_parameter("elevator_pid_ctrl", "/elevator")
        elevator_pid_top = self.get_parameter("elevator_pid_ctrl").value

        self.declare_parameter("elev_sp_top", "/elev_sp")
        elev_sp_top = self.get_parameter("elev_sp_top").value
        
    

        self.depth_sp = 0.
        self.elev_effort = 0.
        self.start_ad = True

        self.rpm_msg = ThrusterRPMs()
        self.vec_msg = ThrusterAngles()

        self.published_zero_rpm_once = False
        self.published_zero_vec_once = False

        # States
        self.teleop_enabled = False
        self.assisted_driving_enabled = False

        # Publishers
        self.rpm_joystick_pub =self.create_publisher( Twist,rpm_joystick_top, qos_profile=1)
        self.vector_deg_joystick_pub = self.create_publisher(Twist,vector_deg_joystick_top,  qos_profile=1)
        self.elev_sp_pub = self.create_publisher( Float64,elev_sp_top, qos_profile=1)
        self.thruster_pub = self.create_publisher(ThrusterRPMs,Topics.RPM_CMD_TOPIC,  qos_profile=1)
        self.thrrust1_pub = self.create_publisher(ThrusterRPM,Topics.THRUSTER1_CMD_TOPIC,  qos_profile=1)
        self.thrrust2_pub = self.create_publisher(ThrusterRPM,Topics.THRUSTER2_CMD_TOPIC,  qos_profile=1)
        self.vector_pub = self.create_publisher(ThrusterAngles,Topics.THRUST_VECTOR_CMD_TOPIC,  qos_profile=1)

        # Subscribers
        self.joy_btn_sub = self.create_subscription( JoyButtons,joy_buttons_top, self.joy_btns_callback,qos_profile=1)
        self.teleop_enabled_sub = self.create_subscription(Bool,teleop_enable_top,  self.teleop_enabled_callback,qos_profile=1)
        self.assit_driving_sub = self.create_subscription(Bool,assist_enable_top,  self.assisted_driving_callback,qos_profile=1)
        self.depth_sub = self.create_subscription(Float64,DR_Topics.DR_DEPTH_TOPIC,  self.depth_cb,qos_profile=1)
        self.elevator_pid_sub = self.create_subscription(Float64,elevator_pid_top,  self.elev_pid_cb,qos_profile=1)
        self.timer = self.create_timer(0.1, self.send_cmds)
        # rate = self.create_rate(12)
        # while rclpy.ok():
        #     self.send_cmds()
        #     rate.sleep()

        # rospy.spin()
def main(args=None):
    rclpy.init(args=args)

    teleop_node = teleop()
    try:
        rclpy.spin(teleop_node)
    except KeyboardInterrupt:
        pass
    teleop_node.destroy_node()
    rclpy.shutdown()  



if __name__ == '__main__':
    main()