#!/usr/bin/python

# General

# ROS
from rclpy.node import Node
import rclpy

# Transforms
from tf_transformations import euler_from_quaternion

# Messages
# from sbg_driver.msg import SbgEkfEuler ##
from sensor_msgs.msg import Imu
from std_msgs.msg import Float64

# Topics
from sam_msgs.msg import Topics as SamTopics
from dead_reckoning_msgs.msg import Topics as DRTopics


class SbGImu2Heading(Node):
    """
    This node will convert the orientation provided by the SBG imu.
    Please confirm that the SBG imu is setup to report orientations in ENU.

    Note: this node will subscribe to the default sbg topic defined in sam_msgs.
    """

    def __init__(self, namespace=None):
        super().__init__("sbg_imu_2_heading", namespace=namespace)
        self.get_logger().info("Starting node defined in sbg_imu_2_heading.py")

        self.sbg_topic = SamTopics.SBG_IMU_TOPIC

        # Output topics
        # Heading
        self.heading_topic = DRTopics.DR_HEADING_TOPIC

        # Roll and pitch
        self.roll_topic = DRTopics.DR_ROLL_TOPIC
        self.pitch_topic = DRTopics.DR_PITCH_TOPIC

        self.create_subscription(msg_type=Imu, topic=self.sbg_topic,
                                 callback=self.sbg_imu_callback, qos_profile=10)

        self.heading_pub = self.create_publisher(msg_type=Float64, topic=self.heading_topic,
                                                 qos_profile=10)

        self.roll_pub = self.create_publisher(msg_type=Float64, topic=self.roll_topic,
                                              qos_profile=10)

        self.pitch_pub = self.create_publisher(msg_type=Float64, topic=self.pitch_topic, qos_profile=10)

    def sbg_imu_callback(self, sbg_msg):
        quat = sbg_msg.orientation
        euler = euler_from_quaternion([quat.x, quat.y, quat.z, quat.w])

        roll = euler[0]
        pitch = euler[1]
        heading = euler[2]

        self.get_logger().info(f"roll: {roll} - pitch: {pitch} - heading: {heading}")

        # Construct messages and publish
        roll_msg = Float64()
        roll_msg.data = roll
        self.heading_pub.publish(roll_msg)

        pitch_msg = Float64()
        pitch_msg.data = heading
        self.heading_pub.publish(pitch_msg)

        heading_msg = Float64()
        heading_msg.data = heading
        self.heading_pub.publish(heading_msg)


def main(args=None, namespace=None):
    rclpy.init(args=args)
    heading_node = SbGImu2Heading(namespace=namespace)
    try:
        rclpy.spin(heading_node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    default_namespace = "sam0"
    main(namespace=default_namespace)
