import os
import sys
import subprocess
import time
import unittest

import launch
from launch.launch_service import LaunchService
import launch_ros
import launch_testing.actions
import rclpy
from rclpy.executors import MultiThreadedExecutor, SingleThreadedExecutor
from rclpy.node import Node

from geometry_msgs.msg import TransformStamped
from launch_ros.actions import (
    Node as LaunchNode,
)  # This is for launching nodes in the test
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
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster


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
                output="screen",
            ),
            # Launch tests 0.5 s later
            launch.actions.TimerAction(
                period=1.0, actions=[launch_testing.actions.ReadyToTest()]
            ),
        ],
    )


class StaticFramePublisher(Node):
    """
    Broadcast transforms that never change.

    This example publishes transforms from `world` to a static turtle frame.
    The transforms are only published once at startup, and are constant for all
    time.
    """

    def __init__(self):
        super().__init__("tf_broadcast")

        self.tf_static_broadcaster = StaticTransformBroadcaster(self)

        # Publish static transforms once at startup
        self.make_transforms()

    def make_transforms(self):
        t = TransformStamped()

        t.header.frame_id = "utm_33_V"
        t.child_frame_id = "odom_gt"
        t.transform.translation.x = 652149.81493
        t.transform.translation.y = 6523374.62748
        t2 = TransformStamped()

        t2.header.frame_id = "odom_gt"
        t2.child_frame_id = "base_link_gt"
        self.tf_static_broadcaster.sendTransform([t, t2])


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
        self._broadcaster = None
        launch.LaunchService()

    def tearDown(self):
        """This teardown is run every test."""
        self.executor.remove_node(self.node)
        self.node.destroy_node()
        if self._broadcaster is not None:
            self.executor.remove_node(self._broadcaster)
            self._broadcaster.destroy_node()

    def transform_setup(self):
        self._broadcaster = StaticFramePublisher()
        self.executor.add_node(self._broadcaster)

    def while_loop_state(self, expected_state, max_time = time.time() + 10):
        while max_time > time.time():
            self.executor.spin_once(timeout_sec = 0.2)
            if self.setpoint.state == expected_state:
                return True
        return False

    def test_client_connect(self, proc_output):
        """Tests whether or not the client connects properly to the server."""
        print("Spinning executor")
        self.executor.spin_once(timeout_sec=0.5)
        self.assertTrue(self.setpoint.state == ActionClientState.READY)

    def test_client_goal(self, proc_output):
        """Tests whether or not the client properly sends test messages."""
        print("Spinning executor")
        self.executor.spin_once(timeout_sec=0.2)
        self.setpoint._test_geopoint()
        is_sent = self.while_loop_state(ActionClientState.SENT)
        self.assertTrue(is_sent)
        print(proc_output)

    def test_client_accept(self, proc_output):
        """Tests whether or not the client properly transitions after accepting goal and running."""
        print("Spinning executor")
        self.transform_setup()
        self.executor.spin_once(timeout_sec=0.4)
        self.setpoint._test_geopoint()
        is_accepted = self.while_loop_state(ActionClientState.ACCEPTED)
        is_running = self.while_loop_state(ActionClientState.RUNNING)

        self.assertTrue(is_accepted)
        self.assertTrue(is_running)

    def test_client_cancel(self, proc_output):
        """Tests whether or not the client can cancel goals successfully."""
        print("Spinning executor")
        self.transform_setup()
        self.executor.spin_once(timeout_sec=0.4)
        self.setpoint._test_geopoint()
        # while looping till we are accepted and getting feedback
        is_running = self.while_loop_state(ActionClientState.RUNNING)
        if is_running:
            self.setpoint.cancel_geopoint()
        else:
            print("Failed to get to running state, so test case failed.")
            self.assertTrue(is_running)

        is_cancelled = self.while_loop_state(ActionClientState.CANCELLED)
        self.assertTrue(is_cancelled)
