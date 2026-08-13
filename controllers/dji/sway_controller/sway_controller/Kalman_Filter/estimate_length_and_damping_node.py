#!/usr/bin/env python3


import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from sway_controller.EstimateLengthAndDamping import EstimateLengthAndDamping


def main():
    rclpy.init()

    node = Node("estimate_length_and_damping_node")

    node.declare_parameter("robot_name", "M350")

    robot_name = node.get_parameter("robot_name").value


    EstimateLengthAndDamping(
        node,
        robot_name=robot_name,
    )


    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
