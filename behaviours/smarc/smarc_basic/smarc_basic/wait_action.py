#!/usr/bin/python3

import rclpy

from rclpy.node import Node
from rclpy.time import Time, Duration
from rclpy.executors import MultiThreadedExecutor
from builtin_interfaces.msg import Time as TimeMsg

from smarc_action_base.gentler_action_server import GentlerActionServer


class WaitAction():
    def __init__(self, node: Node):
        self._node = node

        self._start_as = GentlerActionServer(
            node,
            "smarc_wait",
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._feedback,
            loop_frequency = 20
        )

    def _reset(self):
        self._started_waiting : Time|None = None
        self._timeout : float|None = None
        

    def _on_goal_received(self, goal_request: dict) -> bool:
        try:
            self._timeout = float(goal_request['timeout'])
            return True
        except Exception as e:
            self._node.get_logger().error(f"Error parsing timeout: {e}")
            return False
    
        
    def _on_cancel_received(self) -> bool:
        self._reset()
        return True
    
    def _prepare_loop(self) -> None:
        self._started_waiting = self._node.get_clock().now()
        self._node.get_logger().info(f"Started waiting for {self._timeout:.2f} seconds")

    @property
    def _elapsed_time(self) -> float:
        if self._started_waiting is None:
            return -1.0
        
        return (self._node.get_clock().now() - self._started_waiting).nanoseconds / 1e9

    def _loop_inner(self) -> bool|None:
        if self._started_waiting is None or self._timeout is None:
            return False
        if self._elapsed_time >= self._timeout:
            self._node.get_logger().info(f"Finished waiting.")
            return True
        else:
            self._node.get_logger().debug(f"Waiting... Elapsed time: {self._elapsed_time:.2f} seconds / {self._timeout:.2f} seconds")
            return None
        
    def _feedback(self) -> str:
        if self._started_waiting is None or self._timeout is None:
            return "Not started"
        else:
            return f"Elapsed time: {self._elapsed_time:.2f} seconds / {self._timeout:.2f} seconds"
    
    
def main():
    rclpy.init()
    node = Node("wait_action_node")
    wait_action_node = WaitAction(node)
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down")
        node.destroy_node()

