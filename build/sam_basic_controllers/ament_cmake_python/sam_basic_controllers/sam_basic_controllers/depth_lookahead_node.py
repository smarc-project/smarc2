#!/usr/bin/python3

import rclpy
import sys
import numpy as np
import message_filters
from std_msgs.msg import Float64

class LookAheadDepthNode(object):

    def __init__(self, node):

        depth_top = node.declare_parameter('depth_top', '/yomama4').value
        pitch_top = node.declare_parameter('pitch_top', '/yomama5').value
        ahead_depth = node.declare_parameter('lookahead_depth', '/yomama6').value
        self.dist = node.declare_parameter('lookahead_dist', '/yomama7').value
       
        self.depth_ahead_pub = node.create_publisher(Float64, ahead_depth, 10)

        # Connect
        self.depth_sub = message_filters.Subscriber(node, Float64, depth_top)
        self.pitch_sub = message_filters.Subscriber(node, Float64, pitch_top)
        self.ts = message_filters.ApproximateTimeSynchronizer([self.depth_sub, self.pitch_sub],
                                                              queue_size=10,
                                                              slop=1.0,
                                                              allow_headerless=True)
        self.ts.registerCallback(self.lookahead)

        node.get_logger().info("Running")

        rclpy.spin(node)

    def lookahead(self, depth_msg, pitch_msg):

        depth_ahead = depth_msg.data - np.abs(self.dist) * np.sin(pitch_msg.data)

        self.depth_ahead_pub.publish(depth_ahead)


if __name__ == "__main__":
    rclpy.init(args=sys.argv)
    node = rclpy.create_node('lookahead_depth_node')
    LookAheadDepthNode(node)
