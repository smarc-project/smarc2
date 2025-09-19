#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from smarc_msgs.msg import  ThrusterFeedback
from sam_msgs.msg import ThrusterAngles

# Some of the messages are missing timestamp so we make new ones
class AddTimestamp(Node):
    def __init__(self):
        super().__init__('add_timestamps')

        # NOTE: Since we reassign the stamps for some of the topics we need to do it to all topics we are going to use
        # so that they exist in the same "timeline"
        # Creating publishers
        self.thruster1_fb_pub = self.create_publisher(ThrusterFeedback, "with_header/thruster1_fb", 10) 
        self.thruster2_fb_pub = self.create_publisher(ThrusterFeedback, "with_header/thruster2_fb", 10)
        self.thruster_vector_pub = self.create_publisher(ThrusterAngles, "with_header/thrust_vector_cmd", 10)

        # Subscribe to topics we want to add timestamps to
        self.thruster1_fb_sub = self.create_subscription(ThrusterFeedback, "/sam/core/thruster1_fb", self.add_stamp_thruster1fb, 10) # No data in stamp
        self.thruster2_fb_sub = self.create_subscription(ThrusterFeedback, "/sam/core/thruster2_fb", self.add_stamp_thruster2fb, 10) # No data in stamp
        self.thrusters_cmd_sub = self.create_subscription(ThrusterAngles, "/sam/core/thrust_vector_cmd", self.add_stamp_vector, 10) # No data in stamp

    def add_stamp_vector(self,msg):

        msg_stamped = msg
        msg_stamped.header.stamp = self.get_clock().now().to_msg()
        self.thruster_vector_pub.publish(msg_stamped)

    def add_stamp_thruster2fb(self, msg):
        msg_stamped = msg
        msg_stamped.header.stamp = self.get_clock().now().to_msg()
        self.thruster2_fb_pub.publish(msg_stamped)

    def add_stamp_thruster1fb(self, msg):

        msg_stamped = msg
        msg_stamped.header.stamp = self.get_clock().now().to_msg()

        self.thruster1_fb_pub.publish(msg_stamped)
    

def main(args=None):
    # Start and run node
    rclpy.init(args=args)

    node_stamp = AddTimestamp()

    executor = MultiThreadedExecutor()
    executor.add_node(node_stamp)
    

    executor.spin()

    node_stamp.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()