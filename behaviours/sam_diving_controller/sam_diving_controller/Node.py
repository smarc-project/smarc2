#!/usr/bin/python3

import rclpy
from rclpy.node import Node
import sys

from .ParamUtils import DivingModelParam
from .SAMDivePub import SAMDivePub
from .ActionServerDiveSub import DiveActionServerSub
from .DiveSub import DiveSub
from .DiveController import DepthJoyControllerPID, DiveControllerPID, DiveControllerMPC 
from .ConveniencePub import ConveniencePub

from rclpy.executors import MultiThreadedExecutor

def main():
    """
    Run manual setpoints
    """

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("DivingNode")

    node.declare_parameter('dive_pub_rate', 0.1)
    node.declare_parameter('dive_controller_rate', 0.1)
    node.declare_parameter('dive_sub_rate', 0.1)
    node.declare_parameter('convenience_rate', 0.1)

    # This is not a frequency, but a period.
    # t = 10 -> callback gets called every 10 sec
    dive_pub_rate = node.get_parameter('dive_pub_rate').get_parameter_value().double_value
    dive_controller_rate = node.get_parameter('dive_controller_rate').get_parameter_value().double_value
    dive_sub_rate = node.get_parameter('dive_sub_rate').get_parameter_value().double_value

    convenience_pub_rate = node.get_parameter('convenience_rate').get_parameter_value().double_value

    dive_pub = SAMDivePub(node)
    dive_sub = DiveSub(node, dive_pub) 
    dive_controller = DiveControllerMPC(node, dive_pub, dive_sub, dive_controller_rate)
    #dive_controller = DiveControllerPID(node, dive_pub, dive_sub, dive_controller_rate) 

    #convenience_pub = ConveniencePub(node, dive_sub, dive_controller)

    node.create_timer(dive_pub_rate, dive_pub.update)
    node.create_timer(dive_controller_rate, dive_controller.update)
    node.create_timer(dive_sub_rate, dive_sub.update)

    #node.create_timer(convenience_pub_rate, convenience_pub.update)

    def _loginfo(node, s):
        node.get_logger().info(s)

    _loginfo(node,"Setpoints in Topic")
    _loginfo(node,"Created MVC")

    executor = MultiThreadedExecutor()

    try:
        rclpy.spin(node, executor=executor)
        #rclpy.spin(node)
        _loginfo(node, "Spinning up")
    except KeyboardInterrupt:
        pass

    _loginfo(node,"Shutting down")

def joy_depth():
    """
    Run manual setpoints
    """

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("DivingNode")

    node.declare_parameter('dive_pub_rate', 0.1)
    node.declare_parameter('dive_controller_rate', 0.1)
    node.declare_parameter('dive_sub_rate', 0.1)
    node.declare_parameter('convenience_rate', 0.1)

    # This is not a frequency, but a period.
    # t = 10 -> callback gets called every 10 sec
    dive_pub_rate = node.get_parameter('dive_pub_rate').get_parameter_value().double_value
    dive_controller_rate = node.get_parameter('dive_controller_rate').get_parameter_value().double_value
    dive_sub_rate = node.get_parameter('dive_sub_rate').get_parameter_value().double_value

    convenience_pub_rate = node.get_parameter('convenience_rate').get_parameter_value().double_value

    dive_pub = SAMDivePub(node)
    dive_sub = DiveSub(node, dive_pub) 
    dive_controller = DepthJoyControllerPID(node, dive_pub, dive_sub, dive_controller_rate)

    #convenience_pub = ConveniencePub(node, dive_sub, dive_controller)

    node.create_timer(dive_pub_rate, dive_pub.joy_update)
    node.create_timer(dive_controller_rate, dive_controller.update)
    node.create_timer(dive_sub_rate, dive_sub.update)

    #node.create_timer(convenience_pub_rate, convenience_pub.update)

    def _loginfo(node, s):
        node.get_logger().info(s)

    _loginfo(node,"Setpoints in Topic")
    _loginfo(node,"Created MVC")

    executor = MultiThreadedExecutor()

    try:
        rclpy.spin(node, executor=executor)
        #rclpy.spin(node)
        _loginfo(node, "Spinning up")
    except KeyboardInterrupt:
        pass

    _loginfo(node,"Shutting down")


def action_server():

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("DivingNode")

    node.declare_parameter('dive_pub_rate', 0.1)
    node.declare_parameter('dive_controller_rate', 0.1)
    node.declare_parameter('dive_sub_rate', 0.1)
    node.declare_parameter('convenience_rate', 0.1)

    # This is not a frequency, but a period.
    # t = 10 -> callback gets called every 10 sec
    dive_pub_rate = node.get_parameter('dive_pub_rate').get_parameter_value().double_value
    dive_controller_rate = node.get_parameter('dive_controller_rate').get_parameter_value().double_value
    dive_sub_rate = node.get_parameter('dive_sub_rate').get_parameter_value().double_value

    convenience_pub_rate = node.get_parameter('convenience_rate').get_parameter_value().double_value

    param = DivingModelParam(node).get_param()
    dive_pub = SAMDivePub(node, param)
    dive_sub = DiveActionServerSub(node, dive_pub, param)
    dive_controller = DiveControllerPID(node, dive_pub, dive_sub, param, dive_controller_rate)

    convenience_pub = ConveniencePub(node, dive_sub, dive_controller)


    node.create_timer(dive_pub_rate, dive_pub.update)
    node.create_timer(dive_controller_rate, dive_controller.update)
    node.create_timer(dive_sub_rate, dive_sub.update)

    node.create_timer(convenience_pub_rate, convenience_pub.update)

    def _loginfo(node, s):
        node.get_logger().info(s)

    _loginfo(node,"Action Server")
    _loginfo(node,"Created MVC")

    executor = MultiThreadedExecutor()

    try:
        rclpy.spin(node, executor=executor)
        #rclpy.spin(node)
        _loginfo(node, "Spinning up")
    except KeyboardInterrupt:
        pass

    _loginfo(node,"Shutting down")


if __name__ == "__main__":
    main()
