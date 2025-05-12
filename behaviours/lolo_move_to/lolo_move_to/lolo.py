#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

# Copyright 2023 Ozer Ozkahraman (ozero@kth.se)
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import numpy as np

# TODO: add this as a dependency in package.xml.
from tf_transformations import euler_from_quaternion

from rclpy.node import Node

from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32
from lolo_msgs.msg import Topics as LoloTopics
from smarc_msgs.msg import Topics as SmarcTopics

from lolo_move_to.move_to_goal import MoveToGoal


class SimpleRPMGoal(object):
    GOALTYPE_WAYPOINT = 1
    GOALTYPE_COURSE = 2
    def __init__(self,
                 x = None,
                 y = None,
                 depth = None,
                 altitude = None,
                 rpm = None,
                 tolerance = None,
                 targetCourse = None):
        self.x = x
        self.y = y
        self.depth = depth
        self.altitude = altitude
        self.rpm = rpm
        self.tolerance = tolerance
        self.targetCourse = targetCourse
        self.goal_type = self.GOALTYPE_WAYPOINT

        if(targetCourse is not None):
            self.goal_type = self.GOALTYPE_COURSE

    @property
    def pos(self):
        return np.array([self.x, self.y, self.depth])

class Lolo(Node):

    def __init__(self, robot_name="lolo", ref_link="map", update_freq=10,
                 max_rpm=500):

        super().__init__('some_smart_node_name_ros_lolo')

        self.robot_name = robot_name
        self.ref_link = ref_link

        # Navigation/INS feedback subscriber.
        self.create_subscription(Odometry, f"/{self.robot_name}/{SmarcTopics.SMARC_ODOM_TOPIC}",
                                 self.odometry_callback, 10)
        # Altitude subscriber.
        self.create_subscription(Float32, f"/{self.robot_name}/{SmarcTopics.SMARC_ALTITUDE_TOPIC}",
                                 self.altitude_callback, 10)
        # Absolute depth subscriber.
        self.create_subscription(Float32, f"/{self.robot_name}/{SmarcTopics.SMARC_DEPTH_TOPIC}",
                                 self.depth_callback, 10)

        # Thruster setpoint publishers.
        self.thruster_port_pub = self.create_publisher(Float32, f"{self.robot_name}/{LoloTopics.THRUSTER_PORT_SET_TOPIC}",
                                                       10)
        self.thruster_stbd_pub = self.create_publisher(Float32, f"{self.robot_name}/{LoloTopics.THRUSTER_STBD_SET_TOPIC}",
                                                       10)
        self.v_thruster_front_pub = self.create_publisher(Float32, f"{self.robot_name}/{LoloTopics.V_THRUSTER_FRONT_SET_TOPIC}",
                                                          10)
        self.v_thruster_back_pub = self.create_publisher(Float32, f"{self.robot_name}/{LoloTopics.V_THRUSTER_BACK_SET_TOPIC}",
                                                          10)
        # Orientation setpoint publishers.
        self.yaw_pub = self.create_publisher(Float32, f"{self.robot_name}/{LoloTopics.YAW_SET_TOPIC}",
                                             10)
        self.roll_pub = self.create_publisher(Float32, f"{self.robot_name}/{LoloTopics.ROLL_SET_TOPIC}",
                                             10)
        self.depth_pub = self.create_publisher(Float32, f"{self.robot_name}/{LoloTopics.DEPTH_SET_TOPIC}",
                                               10)


        # TODO: String that tells lolo what sensors to use
        self.vehicle_mode = ""
        self.max_rpm = max_rpm
        self.goal = None

        #Vehicle state values
        self.pos_x = 0
        self.pos_y = 0
        self.pos_depth = 0
        self.altitude = None
        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        self.pitchRate = 0  # rotation rate around Y axis
        self.rollRate = 0   # rotation rate around X axis
        self.yawRate = 0    # rotation rate around Z axis
        self.vx = 0         # speed in X direcion
        self.vy = 0         # speed in Y direcion
        self.vz = 0         # speed in Z direcrion

        # FIXME: keeping the "desired" for now.
        #vehicle desired states
        self.desired_yaw = 0
        self.desired_pitch = 0
        self.desired_roll = 0

        #Vehicle actuator vaues
        self.thruster_rpms = np.zeros(2)
        self.desired_rpms = np.zeros(2)
        self.desired_rpm = 0

        self.elevon_angles = np.zeros(2)
        self.desired_elevon_angles = np.zeros(2)

        self.rudder_angle = 0
        self.desired_rudder_angle = 0

        self.elevator_angle = 0
        self.desired_elevator_angle = 0

    ######################################
    # Call this when you want lolo to actually control something
    ######################################
    def update(self):
        if self.goal is None:
            # TODO: publish zeros?
            return

        #TODO make special modes for diving and surface
        # self._change_mode(Lolo.DRIVE)

        # Calculate and publish setpoints for controllers.
        self.control_wp()
        self.control_speed()
        self.control_roll()
        self.control_depth()
        return

    #High level Control
    def control_wp(self):
        #set setpoint for yaw
        if(self.goal.goal_type == self.goal.GOALTYPE_WAYPOINT):
            # FIXME: sanity check arctan2 wrt ENU frame.
            self.desired_yaw = np.arctan2(self.position_error[1], self.position_error[0])
            self.yaw_pub.publish(self.desired_yaw)
        elif (self.goal.goal_type == self.goal.GOALTYPE_COURSE):
            self.desired_yaw = self.goal.targetCourse
            self.yaw_pub.publish(self.desired_yaw)
        else:
            self.get_logger().info("Unknown goal type.")

    def control_depth(self):
        #set setpoint for depth based on depth setpoint or altitude
        self.desired_depth = min(self.goal.depth, (self.depth+self.altitude) - self.target_altitude) if self.target_altitude is not None and self.altitude is not None else self.goal.depth
        self.depth_pub.publish(self.desired_depth)

    def control_speed(self):
        #set setpoints for RPM based on speed setpoint
        self.desired_rpm = self.goal.rpm
        self.thruster_stbd_pub.publish(self.desired_rpm)
        self.thruster_port_pub.publish(self.desired_rpm)
        # TODO: should we control how we want to use the vertical thrusters here?
        # e.g. if goal.rpm < config.min_dive_rpm: do something smart.

    def control_roll(self):
        #set setpoint for rollrate
        self.desired_roll = 0 # FIXME: Hard coded for now.
        self.roll_pub.publish(self.desired_roll)

    def set_moveto_goal(self, target_pose : PoseStamped, goal : MoveToGoal):
        self.goal = SimpleRPMGoal(x=target_pose.position.x,
                                  y=target_pose.position.y,
                                  depth=goal.target_depth,
                                  altitude=goal.min_altitude,
                                  rpm=goal.rpm)

    def reset_goal(self):
        self.goal = None
        self.update()

    # ---------
    # Callbacks
    # ---------

    def odometry_callback(self, msg: Odometry) -> None:
        self.pos_x = msg.pose.pose.position.x
        self.pos_y = msg.pose.pose.position.y

        [roll, pitch, yaw] = euler_from_quaternion([msg.pose.pose.orientation.w,
                                                    msg.pose.pose.orientation.x,
                                                    msg.pose.pose.orientation.y,
                                                    msg.pose.pose.orientation.z],
                                                   axes='sxyz')
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw

        self.rollRate = msg.twist.twist.angular.x
        self.pitchRate = msg.twist.twist.angular.y
        self.yawRate = msg.twist.twist.angular.z

        self.vx = msg.twist.twist.linear.x
        self.vy = msg.twist.twist.linear.y
        self.vz = msg.twist.twist.linear.z

    def altitude_callback(self, msg: Float32) -> None:
        self.altitude = msg.data
        # TODO: keep track of how old this message is.

    def depth_callback(self, msg: Float32) -> None:
        self.pos_depth = msg.data


    ###############################
    ### Properties for convenience
    ###############################
    @property
    def x(self):
        return self.pos_x
    @property
    def y(self):
        return self.pos_y
    @property
    def depth(self):
        return self.pos_depth
    @property
    def pos(self):
        return np.array([self.x, self.y, self.depth])
    @property
    def yaw_vec(self):
        return np.array([np.cos(self.yaw), np.sin(self.yaw)])
    @property
    def ori_quat(self):
        # return tf.transformations.quaternion_from_euler(self.roll, self.pitch, self.yaw)
        pass
    @property
    def port_rpm(self):
        return self.thruster_rpms[0]
    @property
    def strb_rpm(self):
        return self.thruster_rpms[1]
    @property
    def port_elevon_angle(self):
        return self.elevon_angles[0]
    @property
    def strb_elevon_angle(self):
        return self.elevon_angles[1]
    @property
    def position_error(self):
        return self.goal.pos - self.pos
    @property
    def depth_to_goal(self):
        return self.goal.depth - self.depth
