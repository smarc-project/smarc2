#!/usr/bin/python3

import sys

import rclpy
from rclpy.executors import MultiThreadedExecutor

try:
    from RLControlModel import RLControlModel
except:
    from .RLControlModel import RLControlModel

try:
    from ONNXManager import ONNXManager
except:
    from .ONNXManager import ONNXManager

try:
    from RLActionServer import RLActionServer
except:
    from .RLActionServer import RLActionServer

try:
    from SAMView import SAMView
except:
    from .SAMView import SAMView


class PrimaryNode():

    def __init__(self,
                 global_rate=1 / 10,
                 onnx_path="/home/mart/colcon_ws/src/smarc2/behaviours/rl_control/resource/SAMSimple.onnx"):
        self.node = rclpy.create_node("RLControlNode")

        # This is not a frequency, but a period.
        # t = 10 -> callback gets called every 10 sec
        view_rate = global_rate
        model_rate = global_rate
        controller_rate = global_rate

        onnx_manager = ONNXManager(onnx_path)
        self.view = SAMView(self.node)
        self.controller = RLActionServer(self.node)  # Note, this is a MVC controller, not a control theory controller
        self.model = RLControlModel(self.node, onnx_manager, self.view, self.controller, model_rate)  # This is where the actual PID controller lives.

        self.node.create_timer(global_rate, self.update)

        self.node.get_logger().info("RL Control Node started")
        self.node.get_logger().info("Created MVC")

        self.executor = MultiThreadedExecutor()

    def update(self):
        self.model.update()
        self.controller.update()
        self.view.update()


    def loop(self):
        try:
            self.node.get_logger().info("Spinning up")
            rclpy.spin(self.node, executor=self.executor)
        except KeyboardInterrupt:
            self.node.get_logger().info("Shutting down")


node: PrimaryNode


def main():
    """
    Run control node
    """
    rclpy.init(args=sys.argv)

    node = PrimaryNode()
    node.loop()


if __name__ == "__main__":
    main()
