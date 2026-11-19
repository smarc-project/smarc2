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

    def make_node(name, namespace, **kwargs):
        node = Node(name, namespace=namespace, **kwargs)
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


class FakeMqttClient:
    """Records what the bridge does to the broker. Stands in for paho."""

    def __init__(self, connected=True):
        self.connected = connected
        self.published = []        # (topic, payload)
        self.subscribed = []       # topic filters, in order
        self.callbacks = {}        # filter -> callback

    def is_connected(self):
        return self.connected

    def publish(self, topic, payload):
        self.published.append((topic, payload))

    def subscribe(self, topic_filter):
        self.subscribed.append(topic_filter)

    def unsubscribe(self, topic_filter):
        self.subscribed.remove(topic_filter)

    def message_callback_add(self, topic_filter, callback):
        self.callbacks[topic_filter] = callback

    def message_callback_remove(self, topic_filter):
        self.callbacks.pop(topic_filter, None)


@pytest.fixture
def mqtt_client():
    return FakeMqttClient()
