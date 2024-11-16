#!/usr/bin/python3

import rclpy
import sys

from rclpy.node import Node

from smarc_msgs.msg import ThrusterRPM, PercentStamped
from sam_msgs.msg import ThrusterAngles
from sam_msgs.msg import Topics as SamTopics


class SAMView:
    """
    A View class that can tell sam to do things.
    If you wanted to be fancy, you could also create a
    base class for a generic thrust-vectoring system and extend it
    with sam-specifics here, but for simplicity, we shan't do that here.

    If needed, you can extend _this_ class with one that also writes the control
    inputs to file, to plot or something as well!
    """
    def __init__(self, node: Node):
        # bunch of topics to publish to

        # lets actually use private variable notations this time around eh?
        # ROS2 introduces a QoS setting to publishing and subsciribing(optional)
        # that might be of use later, but for this simple example, we just set
        # a default value of "10" which more or less mimics ROS1
        self._lcg_pub = node.create_publisher(PercentStamped, SamTopics.LCG_CMD_TOPIC, 10)
        self._vbs_pub = node.create_publisher(PercentStamped, SamTopics.VBS_CMD_TOPIC, 10)
        self._rpm1_pub = node.create_publisher(ThrusterRPM, SamTopics.THRUSTER1_CMD_TOPIC, 10)
        self._rpm2_pub = node.create_publisher(ThrusterRPM, SamTopics.THRUSTER2_CMD_TOPIC, 10)
        self._thrust_vector_pub = node.create_publisher(ThrusterAngles, SamTopics.THRUST_VECTOR_CMD_TOPIC, 10)

        self._t1_msg = ThrusterRPM()
        self._t2_msg = ThrusterRPM()
        self._vec_msg = ThrusterAngles()
        self._vbs_msg = PercentStamped()
        self._lcg_msg = PercentStamped()


    def set_control_inputs(self,
                           rpm = None,
                           thruster_horizontal_radians = None,
                           thruster_vertical_radians = None,
                           vbs = None,
                           lcg = None):
        """
        This should be called by a model to set the control inputs
        and can be done arbitrarily frequently
        """
        # check for validity and limits here as needed
        # also for types, like how rpms are ints but a control model
        # would likely give out floats and that setting radians=0
        # should make sure those ints become 0.0 floats
        if(rpm):
            self._t1_msg.rpm = int(rpm)
            self._t2_msg.rpm = int(rpm)

        if(thruster_horizontal_radians):
            assert abs(thruster_horizontal_radians) < 3.15, "Thruster horizontal RADIANS, not degrees! Normalize your stuff!"
            self._vec_msg.thruster_horizontal_radians = float(thruster_horizontal_radians)

        if(thruster_vertical_radians):
            assert abs(thruster_vertical_radians) < 3.15, "Thruster vertical RADIANS, not degrees! Normalize your stuff!"
            self._vec_msg.thruster_vertical_radians = float(thruster_vertical_radians)

        if(vbs):
            assert (vbs>=0 and vbs<=100), "VBS input must be 0<=vbs<=1"
            self._vbs_msg.value = float(vbs)

        if(lcg):
            assert (lcg>=0 and lcg<=100), "LCG input must be 0<=lcg<=1"
            self._lcg_msg.value = float(lcg)

        # you could also keep track of all the inputs given, record them,
        # write to file, even publish a different topic for debugging purposes
        # _lots of LOOKING, from the VIEW class_


    def update(self):
        """
        The actual publishing is done here for all the topics
        you can call this as fast the receiver needs the data repeated
        independently of the rate in which said data is updated.

        Method is called "update" rather than "publish" because maybe
        another view would change numbers on a display and having a list
        of views to call "update" on would make life easy.
        """
        self._vbs_pub.publish(self._vbs_msg)
        self._lcg_pub.publish(self._lcg_msg)
        self._thrust_vector_pub.publish(self._vec_msg)
        self._rpm1_pub.publish(self._t1_msg)
        self._rpm2_pub.publish(self._t2_msg)



if __name__ == "__main__":
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("SAMViewTestNode")
    view = SAMView(node)

    us = [
        [0,       0,   0,0,0],
        [500.14,  0,   0,0,0],
        [-500.21, 0,   0,0,0],
        [500.12,  0.15,0,0,0],
        [500.12, -0.15,0,0,0]
    ]

    # we wanna publish the above Us on a timer
    # could have also created a timer object instead of
    # doing the while loop, but this loop is a very common
    # thing we used to do in ros1 that an example is nice to have
    ###############################################################
    # see controller_controller.py for the better way with timers.
    ###############################################################
    rate = node.create_rate(0.5)
    i = 0
    while(rclpy.ok()):
        # the new rate objects dont auto-spin, they just sleep
        # this is a general trend in ros2, most things do _one thing_
        # and dont do much else implicitly.

        # see controller_controller.py for the better way of doing the
        # main loop here! I'm using this here as an example of what ros1 looks
        # like in ros2-world.

        view.set_control_inputs(us[i])
        view.update()
        node.get_logger().info(f"u = {us[i]}")

        i+=1
        i = i%len(us)

        rclpy.spin_once(node)
        rate.sleep()
