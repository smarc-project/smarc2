#!/usr/bin/python3

import rclpy

from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from std_msgs.msg import String, Bool

from smarc_action_base.gentler_action_server import GentlerActionServer
from smarc_msgs.msg import Topics


class LogAction():
    def __init__(self, node: Node):
        self._node = node

        self._start_as = GentlerActionServer(
            node,
            "smarc_log",
            self._on_goal_received,
            lambda: True,
            lambda: None,
            lambda: True,
            lambda: "Logged",
            loop_frequency = 5
        )

        self._pub = node.create_publisher(String, Topics.HUMAN_LOG_TOPIC, 10)
        self._signal_pub = node.create_publisher(Bool, Topics.HUMAN_LOG_SIGNAL_TOPIC, 10)

    def _on_goal_received(self, goal_request: dict) -> bool:
        try:
            str = goal_request['log_str']
            self._pub.publish(String(data=str))
            self._signal_pub.publish(Bool(data=True))
            return True
        except Exception as e:
            self._node.get_logger().error(f"Error parsing timeout: {e}")
            return False
    
    
def main():
    rclpy.init()
    node = Node("log_action_node")
    log_action_node = LogAction(node)
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down")
        node.destroy_node()

