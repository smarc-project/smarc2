#! /usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from rclpy.executors import MultiThreadedExecutor

from lolo_msgs.msg import Topics as LoloTopics
from smarc_msgs.msg import Topics as SmarcTopics
from smarc_control_msgs.msg import Topics as ControlTopics

#Basic PID regulator
class control_mixer(Node):
    def __init__(self):
        super().__init__("control_mixer_node")
        self.logger = self.get_logger()
        self.logger.info("Initializing mixer node!")

        self.declare_node_parameters()

        self.update_rate = float(self.get_parameter("update_rate").value)
        self.logger.info(f"update rate: {self.update_rate}")
        self.robot_name = self.get_parameter("robot_name").value

        #Mixer gain parameters
        self.pitch_gain = 1
        self.yaw_gain = 1200
        self.rpm_deadband = 50

        self.yaw_actuation_msg = Float32()
        self.elevator_actuation_msg = Float32()
        self.elevon_port_actuation_msg = Float32()
        self.elevon_strb_actuation_msg = Float32()

        self.thruster_port_actuation_msg = Float32()
        self.thruster_strb_actuation_msg = Float32()
        #Hack to not send thruster setpoints all the time
        self.thruster_setpoint_couter = 0
        self.thruster_setpoint_interval = 40 # Only send every 40th value -> 1 setpoint every 2s

        self.yaw_actuation_filtered = 0
        self.yaw_actuation_filter_setting = 1.0/30.0
        self.yaw_error_bucket = 0
        self.yaw_error_bucket_leak = 0.3
        self.yaw_error_bucket_limit = 15
        self.yaw_error_bucket_max = 20
        self.dive_diff_thrust_limit = 150

        #Last time an input was received. Used for timeouts
        self.lastyaw_time = 0
        self.lastroll_time = 0
        self.lastpitch_time = 0
        self.lastrpm_time = 0
        self.lastsurge_time = 0
        self.lastdepth_time = 0
        self.lastdepth_setpoint_time = 0

        #last input values
        self.pitch_actuation = 0
        self.roll_actuation = 0
        self.yaw_actuation = 0
        self.rpm_actuation = 0
        self.vehicle_surge = 0
        self.depth = 0
        self.depth_setpoint = 0

        #Control inputs.
        self.create_subscription(Float32, f"{LoloTopics.YAW_ACTUATION}",
                                 self.yaw_cb, 1)
        self.create_subscription(Float32, f"{LoloTopics.ROLL_ACTUATION}",
                                 self.roll_cb, 1)
        self.create_subscription(Float32, f"{LoloTopics.PITCH_ACTUATION}",
                                 self.pitch_cb, 1)
        self.create_subscription(Float32, f"{LoloTopics.RPM_SETPOINT}",
                                 self.rpm_cb, 1)
        self.create_subscription(Float32, f"{LoloTopics.DEPTH_SETPOINT}",
                                 self.depth_setpoint_cb, 1)


        #Vehicle feedback.
        self.create_subscription(Float32, f"{ControlTopics.CONTROL_SURGE_RATE_TOPIC}",
                                 self.surge_cb, 1)
        self.create_subscription(Float32, f"{SmarcTopics.DEPTH_TOPIC}",
                                 self.depth_cb, 1)

        #Output limits
        # TODO: Maybe these can be part of virtual_lolo/config/lolo_default_limits.yaml.
        self.rudder_limit = 0.78 # ~30 deg
        self.elevon_limit = 0.5 # ~30 deg
        self.elevator_limit = 0.5 # ~30 deg
        self.thruster_limit = 1000

        #Outputs
        self.rudder_pub = self.create_publisher(Float32,
                                                f"{LoloTopics.RUDDER_CMD}", 1)
        self.elevon_port_pub = self.create_publisher(Float32,
                                                     f"{LoloTopics.ELEVON_PORT_CMD}", 1)
        self.elevon_strb_pub = self.create_publisher(Float32,
                                                     f"{LoloTopics.ELEVON_STRB_CMD}", 1)
        self.thruster_port_pub = self.create_publisher(Float32,
                                                       f"{LoloTopics.THRUSTER_PORT_CMD}", 1)
        self.thruster_strb_pub = self.create_publisher(Float32,
                                                       f"{LoloTopics.THRUSTER_STRB_CMD}", 1)
        self.elevator_pub = self.create_publisher(Float32,
                                                  f"{LoloTopics.ELEVATOR_CMD}", 1)

        self.vertical_front_port = self.create_publisher(Float32,
                                                  f"{LoloTopics.ELEVATOR_CMD}", 1)

        self.vertical_thruster_back_port_pub = self.create_publisher(Float32,
                                                f"{LoloTopics.VERTICAL_THRUSTER_BACK_PORT_CMD}",1)
        self.vertical_thruster_back_strb_pub = self.create_publisher(Float32,
                                                f"{LoloTopics.VERTICAL_THRUSTER_BACK_STRB_CMD}",1)
        self.vertical_thruster_front_port_pub = self.create_publisher(Float32,
                                                f"{LoloTopics.VERTICAL_THRUSTER_FRONT_PORT_CMD}",1)
        self.vertical_thruster_front_strb_pub = self.create_publisher(Float32,
                                                f"{LoloTopics.VERTICAL_THRUSTER_FRONT_STRB_CMD}",1)


    def time_now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def declare_node_parameters(self):
        self.declare_parameter("update_rate", 20)
        self.declare_parameter("robot_name", "lolo")

    def depth_cb(self, msg):
        self.depth = msg.data
    def depth_setpoint_cb(self,msg):
        self.depth_setpoint = msg.data
        self.lastdepth_setpoint_time = self.time_now()
    def pitch_cb(self,msg):
        self.pitch_actuation = msg.data
        self.lastpitch_time = self.time_now()
    def roll_cb(self,msg):
        self.roll_actuation = msg.data
        self.lastroll_time = self.time_now()
    def yaw_cb(self,msg):
        self.yaw_actuation = msg.data
        self.lastyaw_time = self.time_now()
    def rpm_cb(self,msg):
        self.rpm_actuation = msg.data
        self.lastrpm_time = self.time_now()
    def surge_cb(self,msg):
        self.vehicle_surge = msg.data
        self.lastsurge_time = self.time_now()
    

    def update(self):
        now = self.time_now()

        #elevons
        elevon_port = None
        elevon_strb = None

        #Thrusters
        thruster_port = None
        thruster_strb = None

        #Depth (Vertical thrusters)
        if now - self.lastdepth_setpoint_time < 1 and now-self.lastdepth_time < 1:
            if(self.depth_setpoint > self.depth):
                if(self.depth < 0.75 and self.depth_setpoint > 0):
                    #Publish vertical thruster data
                    vertical_thruster_msg = Float32()
                    vertical_thruster_msg.data = 2000.0
                    
                    #self.vertical_thruster_back_port_pub.publish(vertical_thruster_msg)
                    #self.vertical_thruster_back_strb_pub.publish(vertical_thruster_msg)
                    self.vertical_thruster_front_port_pub.publish(vertical_thruster_msg)
                    self.vertical_thruster_front_strb_pub.publish(vertical_thruster_msg)

        #yaw
        self.yaw_error_bucket = max(0, self.yaw_error_bucket-self.yaw_error_bucket_leak)
        self.yaw_error_bucket = min(self.yaw_error_bucket, self.yaw_error_bucket_max)

        if self.lastyaw_time is not None and now-self.lastyaw_time < 1:
            yaw_actuation = max(-self.rudder_limit, min(self.rudder_limit, self.yaw_actuation))
            if(self.depth > 0.5): #diving
                self.yaw_actuation_msg.data = -yaw_actuation
                self.rudder_pub.publish(self.yaw_actuation_msg)
            else:# surface
                #self.rudder_pub.publish(-yaw_actuation*0.2)
                self.yaw_actuation_msg.data = -yaw_actuation
                self.rudder_pub.publish(self.yaw_actuation_msg)

            self.yaw_actuation_filtered = (1.0-self.yaw_actuation_filter_setting)*self.yaw_actuation_filtered + self.yaw_actuation_filter_setting*yaw_actuation
            thruster_port = -self.yaw_gain*self.yaw_actuation_filtered
            thruster_strb = self.yaw_gain*self.yaw_actuation_filtered
            self.yaw_error_bucket += abs(self.yaw_actuation_filtered)
            self.logger.info("Yaw error bucket: "  + str(self.yaw_error_bucket), throttle_duration_sec=1)

        #pitch
        if self.lastpitch_time is not None and now-self.lastpitch_time < 1:
            elevator_actuation = -max(-self.elevator_limit, min(self.elevator_limit, self.pitch_actuation))
            # FIXME: what's this 10 degree offset?
            self.elevator_actuation_msg.data = elevator_actuation + math.radians(-10)
            self.elevator_pub.publish(self.elevator_actuation_msg)
            elevon_port = self.pitch_gain*elevator_actuation
            elevon_strb = self.pitch_gain*elevator_actuation

        #roll
        if self.lastroll_time is not None and now-self.lastroll_time < 1:
            if(elevon_port is not None): elevon_port -= self.roll_actuation
            else: elevon_port=-self.roll_actuation
            if(elevon_strb is not None): elevon_strb += self.roll_actuation
            else: elevon_strb=self.roll_actuation
        if(elevon_port is not None):
            self.elevon_port_actuation_msg.data = elevon_port
            self.elevon_port_pub.publish(self.elevon_port_actuation_msg) #TODO add limits
        if(elevon_strb is not None):
            self.elevon_strb_actuation_msg.data = elevon_strb
            self.elevon_strb_pub.publish(self.elevon_strb_actuation_msg)

        '''
        #Thrusters 1: scale the values added by the yaw controller based on vehicle speed
        fadeout_scaling = 1
        if self.lastsurge_time is not None and now - self.lastsurge_time < 1:
            fadeout_scaling = 0.5 - abs(self.vehicle_surge)
            fadeout_scaling = max(0, min(1, fadeout_scaling))

        if self.depth > 0.5:
            #rospy.loginfo_throttle(1,"fadeout scaling applied: " + str(fadeout_scaling))
            if thruster_port is not None:
                thruster_port *= fadeout_scaling
            if thruster_strb is not None:
                thruster_strb *= fadeout_scaling
        '''

        if(self.depth < 0.5): #At the surface
            pass
        else: #diving
            if(self.yaw_error_bucket > self.yaw_error_bucket_limit): #Do thrust vectoring under water
                if thruster_port != None: thruster_port = max(-self.dive_diff_thrust_limit, min(self.dive_diff_thrust_limit, thruster_port))
                if thruster_strb != None: thruster_strb = max(-self.dive_diff_thrust_limit, min(self.dive_diff_thrust_limit, thruster_strb))
            else: #No need for thrust vectoring
                thruster_port = None
                thruster_strb = None


        #Thrusters 2: Add the desired RPM from the rpm setpoint
        if self.rpm_actuation is not None and now - self.lastrpm_time < 1:
            if self.yaw_actuation is not None and self.depth < 0.5:
                rpm_reduction = max(0, 1 - 1.5*(abs(self.yaw_actuation_filtered)))
            else:
                rpm_reduction = 1

            self.logger.info("rpm reduction: " + str(rpm_reduction), throttle_duration_sec=1)
            if thruster_port is not None: thruster_port += self.rpm_actuation*rpm_reduction
            else: thruster_port = self.rpm_actuation*rpm_reduction
            if thruster_strb is not None: thruster_strb += self.rpm_actuation*rpm_reduction
            else: thruster_strb = self.rpm_actuation*rpm_reduction

        #Publish thruster setpoints
        self.thruster_setpoint_couter += 1
        self.thruster_setpoint_couter = self.thruster_setpoint_couter % self.thruster_setpoint_interval

        if thruster_port is not None:
            rpm = max(-self.thruster_limit, min(self.thruster_limit, thruster_port))
            if(abs(rpm) < self.rpm_deadband):
                rpm = self.rpm_deadband if rpm > 0 else -self.rpm_deadband
            if self.thruster_setpoint_couter == 0:
                self.thruster_port_actuation_msg.data = float(rpm)
            self.thruster_port_pub.publish(self.thruster_port_actuation_msg)

        if thruster_strb is not None:
            rpm = max(-self.thruster_limit, min(self.thruster_limit, thruster_strb))
            if(abs(rpm) < self.rpm_deadband):
                rpm = self.rpm_deadband if rpm > 0 else -self.rpm_deadband
            if self.thruster_setpoint_couter == 0:
                self.thruster_strb_actuation_msg.data = float(rpm)
            self.thruster_strb_pub.publish(self.thruster_strb_actuation_msg)


def main(args=None, namespace=None):
    rclpy.init(args=args)
    mixer_node = control_mixer()

    mixer_node.create_timer(1.0/mixer_node.update_rate, mixer_node.update)
    executor = MultiThreadedExecutor()
    executor.add_node(mixer_node)
    executor.spin()
