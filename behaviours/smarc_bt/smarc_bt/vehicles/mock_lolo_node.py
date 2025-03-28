#!/usr/bin/python3

import rclpy
from rclpy.node import Node
from smarc_msgs.msg import Leak, ThrusterFeedback, ThrusterRPM, ThrusterDC, Topics
from std_msgs.msg import String, Header
import json

class MockLoloData(Node):
    def __init__(self):
        super().__init__('mock_lolo_node')

        # Publishers for Lolo-specific topics
        self.leak_pub = self.create_publisher(Leak, 'leak', 10)
        self.thruster1_pub = self.create_publisher(ThrusterFeedback, 'thruster1_fb', 10)
        self.thruster2_pub = self.create_publisher(ThrusterFeedback, 'thruster2_fb', 10)

        # Publishers for additional topics
        self.battery_pub = self.create_publisher(String, Topics.BATTERY_TOPIC, 10)
        self.gps_pub = self.create_publisher(String, Topics.GPS_TOPIC, 10)
        self.heading_pub = self.create_publisher(String, Topics.HEADING_TOPIC, 10)
        self.heartbeat_pub = self.create_publisher(String, Topics.HEARTBEAT_TOPIC, 10)

        # Timers to publish mock data
        self.create_timer(1.0, self.publish_leak)
        self.create_timer(1.0, self.publish_thruster_feedback)
        self.create_timer(1.0, self.publish_battery)
        self.create_timer(1.0, self.publish_gps)
        self.create_timer(1.0, self.publish_heading)
        # self.create_timer(1.0, self.publish_heartbeat)

    def publish_leak(self):
        msg = Leak()
        msg.value = False  # Mock value for no leak
        self.leak_pub.publish(msg)
        self.get_logger().info('Published mock Leak data')

    def publish_thruster_feedback(self):
        # Mock ThrusterFeedback for thruster 1
        msg1 = ThrusterFeedback()
        msg1.header = Header()
        msg1.header.stamp = self.get_clock().now().to_msg()
        msg1.rpm = ThrusterRPM(rpm=1500)  # Mock RPM
        msg1.dc = ThrusterDC(dc=0.75)  # Mock duty cycle
        msg1.current = 10.5  # Mock current in amps
        msg1.torque = 5.2  # Mock torque in Nm
        self.thruster1_pub.publish(msg1)
        self.get_logger().info('Published mock Thruster1 Feedback')

        # Mock ThrusterFeedback for thruster 2
        msg2 = ThrusterFeedback()
        msg2.header = Header()
        msg2.header.stamp = self.get_clock().now().to_msg()
        msg2.rpm = ThrusterRPM(rpm=1600)  # Mock RPM
        msg2.dc = ThrusterDC(dc=0.80)  # Mock duty cycle
        msg2.current = 11.0  # Mock current in amps
        msg2.torque = 5.5  # Mock torque in Nm
        self.thruster2_pub.publish(msg2)
        self.get_logger().info('Published mock Thruster2 Feedback')

    def publish_battery(self):
        msg = String()
        msg.data = json.dumps({"voltage": 48.5, "current": 12.3, "percentage": 85.0})  # Mock battery data
        self.battery_pub.publish(msg)
        self.get_logger().info('Published mock Battery data')

    def publish_gps(self):
        msg = String()
        msg.data = json.dumps({"latitude": 59.3293, "longitude": 18.0686, "altitude": 15.0})  # Mock GPS data
        self.gps_pub.publish(msg)
        self.get_logger().info('Published mock GPS data')

    def publish_heading(self):
        msg = String()
        msg.data = json.dumps({"heading": 120.5})  # Mock heading data
        self.heading_pub.publish(msg)
        self.get_logger().info('Published mock Heading data')

    def publish_heartbeat(self):
        msg = String()
        msg.data = "LOLO_HEARTBEAT"  # Mock heartbeat data
        self.heartbeat_pub.publish(msg)
        self.get_logger().info('Published mock Heartbeat data')


def main(args=None):
    rclpy.init(args=args)
    node = MockLoloData()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
