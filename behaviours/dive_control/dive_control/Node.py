#!/usr/bin/python3

import rclpy
import sys

from .SAMDiveView import SAMDiveView
from .ActionServerDiveController import DiveActionServerController
from .DiveController import DiveController
from .DivingModel import DiveControlModel
from .ConvenienceView import ConvenienceView

from rclpy.executors import MultiThreadedExecutor

def main():
    """
    Run manual setpoints
    """

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("DivingNode")


    # This is not a frequency, but a period.
    # t = 10 -> callback gets called every 10 sec
    view_rate = 1/10
    model_rate = 1/10
    controller_rate = 1/10

    convenience_view_rate = 1/10

    view = SAMDiveView(node)
    controller = DiveController(node, view)   # Note, this is a MVC controller, not a control theory controller
    model = DiveControlModel(node, view, controller, model_rate)  # This is where the actual PID controller lives.

    convenience_view = ConvenienceView(node, controller, model)


    node.create_timer(view_rate, view.update)
    node.create_timer(model_rate, model.update)
    node.create_timer(controller_rate, controller.update)

    node.create_timer(convenience_view_rate, convenience_view.update)

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


    # This is not a frequency, but a period.
    # t = 10 -> callback gets called every 10 sec
    view_rate = 1/10
    model_rate = 1/10
    controller_rate = 1/10

    convenience_view_rate = 1/10

    view = SAMDiveView(node)
    controller = DiveActionServerController(node, view)   # Note, this is a MVC controller, not a control theory controller
    model = DiveControlModel(node, view, controller, model_rate)  # This is where the actual PID controller lives.

    convenience_view = ConvenienceView(node, controller, model)


    node.create_timer(view_rate, view.update)
    node.create_timer(model_rate, model.update)
    node.create_timer(controller_rate, controller.update)

    node.create_timer(convenience_view_rate, convenience_view.update)

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
