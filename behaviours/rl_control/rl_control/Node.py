#!/usr/bin/python3

import sys

import rclpy
from rclpy.executors import MultiThreadedExecutor

from behaviours.rl_control.rl_control.RLControlModel import RLControlModel
from .ONNXManager import ONNXManager
from .RLMissionActionServer import RLMissionActionServer
from .SAMView import SAMView


def main():
    """
    Run control node
    """
    rclpy.init(args=sys.argv)

    node = PrimaryNode()
    node.loop()


class PrimaryNode():

    def __init__(self, global_rate=1 / 10, onnx_path="../resource/SAMSimple.onnx"):
        self.node = rclpy.create_node("RLControlNode")

        # This is not a frequency, but a period.
        # t = 10 -> callback gets called every 10 sec
        view_rate = global_rate
        model_rate = global_rate
        controller_rate = global_rate
        onnx_manager = ONNXManager(onnx_path)

        self.view = SAMView(self.node)
        self.controller = RLMissionActionServer(self.node)  # Note, this is a MVC controller, not a control theory controller
        self.model = RLControlModel(self.node, onnx_manager, self.view, self.controller, model_rate)  # This is where the actual PID controller lives.

        self.node.create_timer(view_rate, self.view.update)
        self.node.create_timer(controller_rate, self.controller.update)
        self.node.create_timer(model_rate, self.model.update)

        self.node.get_logger().info(self.node, "RL Control Node started")
        self.node.get_logger().info(self.node, "Created MVC")

        self.executor = MultiThreadedExecutor()

    def loop(self):
        try:
            self.node.get_logger().info("Spinning up")
            rclpy.spin(self.node, executor=self.executor)
        except KeyboardInterrupt:
            pass
        self.node.get_logger().info("Shutting down")


if __name__ == "__main__":
    main()
