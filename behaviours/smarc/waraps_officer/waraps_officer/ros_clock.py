"""The node's ROS clock in seconds, for code that keeps time as a float."""

from rclpy.node import Node


def now_s(node: Node) -> float:
    """Sim time under use_sim_time, so a paused or sped-up sim moves the vehicle and the officer with it."""
    return node.get_clock().now().nanoseconds * 1e-9
