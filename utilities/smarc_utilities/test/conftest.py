"""Shared fixtures. Live-graph tests run on a private ROS domain so they never
see, or disturb, a real vehicle graph on the same machine."""

import os
import random

import pytest


@pytest.fixture
def ros_graph():
    """Start rclpy on a throwaway domain, hand out a node factory, tear it all
    down even when the test fails."""
    import rclpy
    from rclpy.node import Node

    saved = {k: os.environ.get(k) for k in ('ROS_DOMAIN_ID', 'ROS_LOCALHOST_ONLY')}
    os.environ['ROS_DOMAIN_ID'] = str(random.randint(71, 95))
    os.environ['ROS_LOCALHOST_ONLY'] = '1'
    rclpy.init()
    nodes = []

    def make_node(name, namespace):
        node = Node(name, namespace=namespace)
        nodes.append(node)
        return node

    try:
        yield make_node
    finally:
        for node in nodes:
            node.destroy_node()
        rclpy.shutdown()
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
