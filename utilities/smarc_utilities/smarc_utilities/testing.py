"""pytest scaffolding for tests that need a live rclpy graph.

Import the fixture into a package's ``test/conftest.py``::

    from smarc_utilities.testing import ros_graph  # noqa: F401

and ``wait_for`` into the tests. Only tests import this module; it needs
pytest, which is a test_depend.
"""

import os
import random
import threading
import time

import pytest


def wait_for(predicate, timeout_s=5.0, period_s=0.05):
    """Poll ``predicate`` until it returns something truthy or the timeout
    passes. Returns the last value either way, so ``assert wait_for(...)``
    reads as the condition."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        result = predicate()
        if result:
            return result
        time.sleep(period_s)
    return predicate()


@pytest.fixture
def ros_graph():
    """A private ROS domain with a spinning MultiThreadedExecutor.

    Yields ``make_node(name, namespace='/', **node_kwargs)``; every node it
    makes is spun by the executor, so callbacks, timers and action servers
    run while the test thread polls with ``wait_for``. Tears everything down
    even when the test fails. The domain id is random in 71-95 with
    ``ROS_LOCALHOST_ONLY=1`` so a test never sees a real vehicle graph.
    """
    import rclpy
    from rclpy.executors import MultiThreadedExecutor
    from rclpy.node import Node

    saved = {k: os.environ.get(k) for k in ('ROS_DOMAIN_ID', 'ROS_LOCALHOST_ONLY')}
    os.environ['ROS_DOMAIN_ID'] = str(random.randint(71, 95))
    os.environ['ROS_LOCALHOST_ONLY'] = '1'
    rclpy.init()
    executor = MultiThreadedExecutor(num_threads=4)
    nodes = []

    def make_node(name, namespace='/', **node_kwargs):
        node = Node(name, namespace=namespace, **node_kwargs)
        nodes.append(node)
        executor.add_node(node)
        return node

    spinner = threading.Thread(target=executor.spin, daemon=True)
    spinner.start()
    try:
        yield make_node
    finally:
        # Context first: a server loop inside rate.sleep() only wakes on
        # context shutdown, and executor.shutdown() would wait on it forever.
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
