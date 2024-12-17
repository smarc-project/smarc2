import time
import unittest

import pytest
import rclpy
from geometry_msgs.msg import Point, Quaternion
from nav_msgs.msg import Odometry
from sam_msgs.msg import Topics as SamTopics, ThrusterAngles
from smarc_control_msgs.msg import Topics as ControlTopics
from smarc_msgs.msg import PercentStamped, ThrusterRPM

from behaviours.rl_control.rl_control.SAMView import SAMDiveView


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

    def test_vbs_publisher(self):
        """Check whether pose messages published"""
        self.set_view(vbs=20)
        msgs = self.simple_publisher_test(PercentStamped, SamTopics.VBS_CMD_TOPIC)
        assert len(msgs) == 1
        assert msgs[0].value == 20

    def test_lcg_publisher(self):
        """Check whether pose messages published"""
        self.set_view(lcg=75)
        msgs = self.simple_publisher_test(PercentStamped, SamTopics.LCG_CMD_TOPIC)
        assert len(msgs) == 1
        assert msgs[0].value == 75

    def test_rpm1_publisher(self):
        """Check whether pose messages published"""
        self.set_view(rpm=300)
        msgs = self.simple_publisher_test(ThrusterRPM, SamTopics.THRUSTER1_CMD_TOPIC)
        assert len(msgs) == 1
        assert msgs[0].rpm == 300

    def test_rpm2_publisher(self):
        """Check whether pose messages published"""
        self.set_view(rpm=500)
        msgs = self.simple_publisher_test(ThrusterRPM, SamTopics.THRUSTER2_CMD_TOPIC)
        assert len(msgs) == 1
        assert msgs[0].rpm == 500

    def test_thrust_vector_publisher(self):
        """Check whether pose messages published"""
        self.set_view(aileron=0.01, rudder=-0.2)
        msgs = self.simple_publisher_test(ThrusterAngles, SamTopics.THRUST_VECTOR_CMD_TOPIC)
        assert len(msgs) == 1
        assert msgs[0].thruster_horizontal_radians == pytest.approx(-0.2, 0.0001)
        assert msgs[0].thruster_vertical_radians == pytest.approx(0.01, 0.0001)

    def test_state_subscriber(self):
        node = rclpy.create_node('test_sub_rl_control')
        publisher = node.create_publisher(Odometry, ControlTopics.STATES, 10)

        odometry = Odometry()
        odometry.pose.pose.position = Point(x=1.1, y=2.1, z=3.1)
        odometry.pose.pose.orientation = Quaternion(x=1.0, y=0.0, z=1.0, w=0.0)

        try:
            publisher.publish(odometry)

            #  Wait for sub to pick up the msg
            end_time = time.time() + 2
            while time.time() < end_time:
                # spin to get subscriber callback executed
                rclpy.spin_once(node, timeout_sec=0.5)
                rclpy.spin_once(self.node, timeout_sec=0.5)

            recieved_state = self.view.get_state()
            assert recieved_state.pose.pose.position.x == pytest.approx(1.1, 0.0001)
            assert recieved_state.pose.pose.position.x == pytest.approx(2.1, 0.0001)
            assert recieved_state.pose.pose.position.x == pytest.approx(3.1, 0.0001)
            # TODO: Finish properly. For now this is good enough, just need to make sure the state is saved and accessible.
        finally:
            node.destroy_publisher(publisher)

    def simple_publisher_test(self, msg_type, topic):
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
