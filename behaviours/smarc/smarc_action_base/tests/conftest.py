"""Live-graph fixtures. Each test gets a private ROS domain and a spinning
MultiThreadedExecutor, so a GentlerActionServer's blocking execution loop and
the client's callbacks both run while the test thread polls."""

import os
import random
import threading

import pytest


@pytest.fixture
def ros_graph():
    import rclpy
    from rclpy.executors import MultiThreadedExecutor
    from rclpy.node import Node

    saved = {k: os.environ.get(k) for k in ('ROS_DOMAIN_ID', 'ROS_LOCALHOST_ONLY')}
    os.environ['ROS_DOMAIN_ID'] = str(random.randint(71, 95))
    os.environ['ROS_LOCALHOST_ONLY'] = '1'
    rclpy.init()
    executor = MultiThreadedExecutor(num_threads=4)
    nodes = []

    def make_node(name, namespace='/'):
        node = Node(name, namespace=namespace)
        nodes.append(node)
        executor.add_node(node)
        return node

    spinner = threading.Thread(target=executor.spin, daemon=True)
    spinner.start()
    try:
        yield make_node
    finally:
        # Shut the context down first: a server loop still inside rate.sleep()
        # only wakes up on context shutdown, and executor.shutdown() would
        # otherwise wait on that thread forever.
        rclpy.shutdown()
        executor.shutdown(timeout_sec=2.0)
        spinner.join(timeout=5.0)
        for node in nodes:
            node.destroy_node()
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
