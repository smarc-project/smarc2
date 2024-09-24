#!/usr/bin/python3

import rclpy, sys, time
from rclpy.node import Node

import numpy as np

import tf2_geometry_msgs.tf2_geometry_msgs
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped, TransformStamped

from smarc_control_msgs.msg import Topics as ControlTopics

from tf_transformations import euler_from_quaternion

from .IDiveView import IDiveView

class DiveController():
    """
    Simple Controller to listen to a depth and pitch setpoint and provide it to the
    DivingModel within the MVC framework
    """
    def __init__(self,
                 node: Node,
                 view: IDiveView):

        self._node = node
        self._view = view

        self._depth_setpoint = None
        self._pitch_setpoint = None

        self._states = Odometry()

        self.depth_sub = node.create_subscription(msg_type=Float64, topic=ControlTopics.DEPTH_SETPOINT, callback=self._depth_cb, qos_profile=10)
        self.pitch_sub = node.create_subscription(msg_type=Float64, topic=ControlTopics.PITCH_SETPOINT, callback=self._pitch_cb, qos_profile=10)
        self.state_sub = node.create_subscription(msg_type=Odometry, topic=ControlTopics.STATES, callback=self._states_cb, qos_profile=10)

        self._loginfo("DCN started")


    def _loginfo(self, s):
        self._node.get_logger().info(s)


    def _depth_cb(self, depth):
        self._depth_setpoint = depth.data

    def _pitch_cb(self, pitch):
        self._pitch_setpoint = pitch.data


    def _states_cb(self, msg):
        self._states = msg


    def get_depth_setpoint(self):
        return self._depth_setpoint

    def get_pitch_setpoint(self):
        return self._pitch_setpoint


    def get_states(self):
        # TODO: Might be better to split this by what 
        # state you're interested in, then you can get them
        # directly.
        return self._states

    def get_depth(self):
        return self._states.pose.pose.position.z

    def get_pitch(self):

        rpy = euler_from_quaternion([
            self._states.pose.pose.orientation.x,
            self._states.pose.pose.orientation.y,
            self._states.pose.pose.orientation.z,
            self._states.pose.pose.orientation.w])

        return rpy[1]


    def update(self):
        """
        All the things when updating
        """
        #self._loginfo("DCN running")
        #self._update_states()



def main():
#    # when creating the _object_ rather than the _class_, we use the concrete classes
#    from .SAMDiveView import SAMThrustView
#
    # create a node and our objects in the usual manner.
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("DiveNode")
    node._logger("not implemented")
#    view = SAMThrustView(node)
#    controller = GoToWaypointActionServerController(node, view)
#
    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)


if __name__ == "__main__":
    main()
