import unittest
from unittest.mock import patch, MagicMock

import pytest
import rclpy

from behaviours.rl_control.rl_control.RLMissionActionServer import RLMissionActionServer


# Active tests
class TestRLMissionController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = rclpy.create_node('test_sam_rl_mission_controller')
        self.RLActionServer = RLMissionActionServer(self.node)

    def tearDown(self):
        self.node.destroy_node()

#    def test_sth(self):


