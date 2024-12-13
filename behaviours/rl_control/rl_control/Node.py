#!/usr/bin/python3

import rclpy
import sys

from .SAMDiveView import SAMDiveView
from .ActionServerDiveController import DiveActionServerController
from .DiveController import DiveController

from rclpy.executors import MultiThreadedExecutor

def main():
    """
    Run manual setpoints
    """

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("RLControlNode")


    # This is not a frequency, but a period.
    # t = 10 -> callback gets called every 10 sec
    global_rate = 1 / 10
    view_rate = global_rate
    model_rate = global_rate
    controller_rate = global_rate

    view = SAMDiveView(node)
    controller = DiveController(node, view)   # Note, this is a MVC controller, not a control theory controller
    model = DiveActionServerController(node, view, controller, model_rate)  # This is where the actual PID controller lives.


    node.create_timer(view_rate, view.update)
    node.create_timer(model_rate, model.update)
    node.create_timer(controller_rate, controller.update)

    def _loginfo(node, s):
        node.get_logger().info(s)

    _loginfo(node,"RL Control Node started")
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
