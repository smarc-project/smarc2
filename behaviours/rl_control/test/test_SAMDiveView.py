import os
import sys
import time
import unittest

import pytest
from sam_msgs.msg import Topics as SamTopics, ThrusterAngles

import launch
import launch_ros
import launch_testing.actions
import rclpy
from smarc_msgs.msg import PercentStamped, ThrusterRPM

from behaviours.rl_control.rl_control.SAMDiveView import SAMDiveView


# Active tests
class TestTurtleSim(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = rclpy.create_node('test_sam_rl')
        self.view = SAMDiveView(self.node)

    def tearDown(self):
        self.node.destroy_node()

    def test_vbs_subscriber(self):
        """Check whether pose messages published"""
        self.set_view(vbs=20)
        msgs = self.simple_subscriber_test(PercentStamped, SamTopics.VBS_CMD_TOPIC)
        assert len(msgs) == 1
        assert msgs[0].value == 20

    def test_lcg_subscriber(self):
        """Check whether pose messages published"""
        self.set_view(lcg = 75)
        msgs = self.simple_subscriber_test(PercentStamped, SamTopics.LCG_CMD_TOPIC)
        assert len(msgs) == 1
        assert msgs[0].value == 75

    def test_rpm1_subscriber(self):
        """Check whether pose messages published"""
        self.set_view(rpm = 300)
        msgs = self.simple_subscriber_test(ThrusterRPM, SamTopics.THRUSTER1_CMD_TOPIC)
        assert len(msgs) == 1
        assert msgs[0].rpm == 300

    def test_rpm2_subscriber(self):
        """Check whether pose messages published"""
        self.set_view(rpm=500)
        msgs = self.simple_subscriber_test(ThrusterRPM, SamTopics.THRUSTER2_CMD_TOPIC)
        assert len(msgs) == 1
        assert msgs[0].rpm == 500

    def test_thrust_vector_subscriber(self):
        """Check whether pose messages published"""
        self.set_view(aileron= 0.01, rudder=-0.2)
        msgs = self.simple_subscriber_test(ThrusterAngles, SamTopics.THRUST_VECTOR_CMD_TOPIC)
        assert len(msgs) == 1
        assert msgs[0].thruster_horizontal_radians == pytest.approx(-0.2, 0.0001)
        assert msgs[0].thruster_vertical_radians == pytest.approx(0.01, 0.0001)


    def simple_subscriber_test(self, msg_type, topic):
        msgs_rx = []
        node = rclpy.create_node('test_sub_rl_control')
        sub = node.create_subscription(
            msg_type,
            topic,
            lambda msg: msgs_rx.append(msg), 10)

        self.view.update()

        try:
            # Listen to the pose topic for 1 s
            end_time = time.time() + 1
            while time.time() < end_time:
                # spin to get subscriber callback executed
                rclpy.spin_once(node, timeout_sec=1)
        finally:
            node.destroy_subscription(sub)
        return msgs_rx

    def set_view(self, rpm=200, rudder=0.1, aileron=-0.1, lcg=55, vbs=45):
        self.view.set_rpm(rpm)
        self.view.set_thrust_vector(rudder, aileron)
        self.view.set_lcg(lcg)
        self.view.set_vbs(vbs)

