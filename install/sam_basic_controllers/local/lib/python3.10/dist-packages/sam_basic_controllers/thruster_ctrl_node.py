#!/usr/bin/python3

import rclpy
import sys
import message_filters
# from sbg_driver.msg import SbgEkfEuler
from sam_msgs.msg import ThrusterAngles
from std_msgs.msg import Float64


class ThrustCtrlNode(object):

    def __init__(self, node):
        # Unlike cpp, we can declare and get at the same time. gg.
        self.heading_effort = node.declare_parameter('rudder_pid_effort', '/yomama').value # Amazing defaults :,D /Ozer
        self.elevator_effort = node.declare_parameter('elevator_pid_effort', '/yomama2').value
        self.thrust_cmd_top = node.declare_parameter('thrust_cmd_topic', '/yomama3').value
       
        # Connect
        self.head_effort_sub = message_filters.Subscriber(node, Float64, self.heading_effort)
        self.elev_effort_sub = message_filters.Subscriber(node, Float64, self.elevator_effort)
        self.ts = message_filters.ApproximateTimeSynchronizer([self.head_effort_sub, self.elev_effort_sub],
                                                                queue_size=20, slop=20.0, allow_headerless=True)
        self.ts.registerCallback(self.thrust_cb)

        # self.thrust_pub = rclpy.Publisher(self.thrust_cmd_top, ThrusterAngles, queue_size=100)
        self.thrust_pub = node.create_publisher(ThrusterAngles, self.thrust_cmd_top, 100)

        node.get_logger().info("Running")
        rclpy.spin(node)

    def thrust_cb(self, heading_msg, elev_msg):
        cmd = ThrusterAngles()
        cmd.header.stamp = rclpy.Time.now()
        cmd.thruster_horizontal_radians = heading_msg.data
        cmd.thruster_vertical_radians = elev_msg.data

        self.thrust_pub.publish(cmd)


if __name__ == "__main__":
    rclpy.init(args=sys.argv)
    node = rclpy.create_node('thrust_ctrl_node')
    ThrustCtrlNode(node)
