import os
import sys
import time
import unittest

import launch
from launch.launch_service import LaunchService
import launch_ros
import launch_testing.actions
import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from launch_ros.actions import Node as LaunchNode  # This is for launching nodes in the test
from go_to_geopoint.geopoint_client import GeopointClient
from smarc_action_base.smarc_action_base import (
    ActionFeedback,
    ActionResult,
    ActionType,
    ActionClientState,
    SMARCActionClient,
)
from smarc_mission_msgs.action import BaseAction
import pytest


# WARN: (Tim) Make sure this mark is here otherwise launch doesn't run
# Documentation https://github.com/ros2/launch_ros/blob/master/launch_testing_ros/test/examples/talker_listener_launch_test.py
@pytest.mark.rostest
def generate_test_description():
    return launch.LaunchDescription(
        [
            launch_ros.actions.Node(
                package="go_to_geopoint",
                # namespace='',
                executable="server",
            ),
        # Launch tests 0.5 s later
        launch.actions.TimerAction(
            period=0.5, actions=[launch_testing.actions.ReadyToTest()]),
        ],
    )


# Active tests
class TestClass(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()


    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        """This setup is run every test."""
        # launch_testing.loa
        node_name = "setpoint_client"
        self.node = Node(node_name)
        action_type = ActionType(BaseAction)
        self.setpoint = GeopointClient(self.node, "go_to_setpoint", action_type)
        self.executor = MultiThreadedExecutor()
        self.executor.add_node(self.node)
        launch.LaunchService()
    

    def tearDown(self):
        """This teardown is run every test."""
        self.executor.remove_node(self.node)
        self.node.destroy_node()

    def test_client_connect(self, proc_output):
        """Tests whether or not the client connects properly to the server."""
        print("Spinning executor")
        self.executor.spin_once(timeout_sec=2.0)
        self.assertTrue(self.setpoint.state == ActionClientState.READY)

    def test_client_goal(self, proc_output):
        """Tests whether or not the client properly sends test messages."""
        print("Spinning executor")
        self.executor.spin_once(timeout_sec=2.0)
        self.assertTrue(self.setpoint.state == ActionClientState.READY)
        self.setpoint._test_geopoint()
        self.executor.spin_once(timeout_sec=1.0)
        self.assertTrue(self.setpoint.state == ActionClientState.SENT)
        print(proc_output)

    def test_client_reject(self, proc_output):
        """Tests whether or not the client properly sends test messages."""
        print("Spinning executor")
        self.executor.spin_once(timeout_sec=2.0)
        self.setpoint._test_geopoint()
        self.executor.spin_once(timeout_sec=1.0)
        self.executor.spin_once(timeout_sec=1.0)
        self.executor.spin_once(timeout_sec=1.0)
        self.assertTrue(self.setpoint.state == ActionClientState.REJECTED)

        print(proc_output)
