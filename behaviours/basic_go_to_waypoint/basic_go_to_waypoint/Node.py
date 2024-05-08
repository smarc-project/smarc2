#!/usr/bin/python3

import rclpy
import sys

from .SAMThrustView import SAMThrustView
from .ActionserverControllerNode import GoToWaypointActionServerController
from .WaypointFollowingModel import WaypointFollowing


def main():

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("WaypointNode")

    view_rate = 10
    model_rate = 10
    controller_rate = 10

    view = SAMThrustView(node)
    controller = GoToWaypointActionServerController(node, view)   # Note, this is a MVC controller, not a control theory controller
    model = WaypointFollowing(node, view, controller, model_rate)  # This is where the actual PID controller lives.


    node.create_timer(view_rate, view.update)
    node.create_timer(model_rate, model.update)
    node.create_timer(controller_rate, controller.update)


    def _loginfo(node, s):
        node.get_logger().info(s)

    _loginfo(node,"Created MVC")

    try:
        rclpy.spin(node)
        _loginfo(node, "Spinning up")
    except KeyboardInterrupt:
        pass

    _loginfo(node,"Shutting down")


if __name__ == "__main__":
    main()
