#!/usr/bin/python3

import rclpy
import sys

from .SAMThrustView import SAMThrustView
from .ActionserverControllerNode import GoToWaypointActionServerController
from .WaypointFollowingModel import WaypointFollowing
from .ConvenienceView import ConvenienceView

from rclpy.executors import MultiThreadedExecutor

def main():

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("WaypointNode")

    # This is not a frequency, but a period.
    # t = 10 -> callback gets called every 10 sec
    view_rate = 1/10
    model_rate = 1/10
    controller_rate = 1/10

    convenience_view_rate = 1/10

    view = SAMThrustView(node)
    controller = GoToWaypointActionServerController(node, view)   # Note, this is a MVC controller, not a control theory controller
    model = WaypointFollowing(node, view, controller, model_rate)  # This is where the actual PID controller lives.

    convenience_view = ConvenienceView(node, controller)


    node.create_timer(view_rate, view.update)
    node.create_timer(model_rate, model.update)
    node.create_timer(controller_rate, controller.update)

    node.create_timer(convenience_view_rate, convenience_view.update)

    def _loginfo(node, s):
        node.get_logger().info(s)

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
