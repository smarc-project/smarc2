#!/usr/bin/python3
import sys
import rclpy
from rclpy.node import Node
from rclpy import time

# ROS imports
from builtin_interfaces.msg import Time as Stamp
from geometry_msgs.msg import TransformStamped
from rclpy.time import Time as rcl_Time

from std_msgs.msg import Float64
from smarc_msgs.msg import ThrusterRPM, PercentStamped
from sam_msgs.msg import Topics as SamTopics
from sam_msgs.msg import ThrusterAngles
from nav_msgs.msg import Odometry

from rclpy.executors import MultiThreadedExecutor

class SetpointPublisher():
    """
    Simple set point publisher for development and debuggin purposes.
    Publishes setpoint pose to a topic the controller listens to.
    """
    def __init__(self, node: Node) -> None:

        self._node = node

        self._setpoint_pub = node.create_publisher(Odometry, '/ctrl/waypoint', 10)
        self._setpoint_msg = Odometry()
        self._setpoint_msg.header.stamp = self.rcl_time_to_stamp(self._node.get_clock().now())
        self._setpoint_msg.header.frame_id = 'sam0/odom_gt'
        self._setpoint_msg.pose.pose.position.x = 40.0
        self._setpoint_msg.pose.pose.position.y = 10.0
        self._setpoint_msg.pose.pose.position.z = -5.0
        self._setpoint_msg.pose.pose.orientation.x = 0.0
        self._setpoint_msg.pose.pose.orientation.y = 0.0
        self._setpoint_msg.pose.pose.orientation.z = 0.0
        self._setpoint_msg.pose.pose.orientation.w = 1.0

        self._loginfo("Created Setpoint Publisher")


    def _loginfo(self, s):
        self._node.get_logger().info(s)


    def rcl_time_to_stamp(self,time: rcl_Time) -> Stamp:
        """
        Converts rcl Time to stamp
        :param time:
        :return:
        """
        stamp = Stamp()
        stamp.sec = int(time.nanoseconds // 1e9)
        stamp.nanosec = int(time.nanoseconds % 1e9)
        return stamp

    def update(self) -> None:
        """
        Publish setpoint message
        """
        self._setpoint_pub.publish(self._setpoint_msg)


def main():
    """
    Node to publish a setpoint when debugging controller
    Use with: ros2 run dive_control setpoint
    """

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("SetpointNode")
    setpoint_pub = SetpointPublisher(node)

    node_rate = 1/10

    node.create_timer(node_rate, setpoint_pub.update)

    executor = MultiThreadedExecutor()

    try:
        rclpy.spin(node, executor=executor)
    except KeyboardInterrupt:
        pass

    node.get_logger().info("Shutting down")


# Could also run this without ros2
if __name__ == "__main__":
    main()
