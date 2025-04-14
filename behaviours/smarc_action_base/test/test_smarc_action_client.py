import pytest

import rclpy
from rclpy.node import Node
import smarc_action_base.smarc_action_base as sac

class NodeTest(Node):
    def __init__(self):
        super().__init__("test_node")

class ActServTest(sac.SMARCActionBase):
    def __init__(self, node):
        super().__init__(node)
        pass
    def _execution_callback(self, goal_handle):
        pass


def test_server_construction():
    rclpy.init()
    node = NodeTest()
    ac = ActServTest(node)

