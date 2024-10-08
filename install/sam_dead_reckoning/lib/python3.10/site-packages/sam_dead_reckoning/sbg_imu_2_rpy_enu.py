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


class SbGImu2rpy(Node):
    """
    This node will convert the orientation provided by the SBG imu.
    Please confirm that the SBG imu is setup to report orientations in ENU.

    Note: this node will subscribe to the default sbg topic defined in sam_msgs.
    """

    def __init__(self, namespace=None):
        super().__init__("sbg_imu_2_rpy_enu", namespace=namespace)
        self.get_logger().info("Starting node defined in sbg_imu_2_rpy_enu.py")

        self.sbg_topic = SamTopics.SBG_IMU_TOPIC

        # Output topics
        # Roll, pitch, yaw topics
        self.roll_topic = DRTopics.DR_ROLL_TOPIC
        self.pitch_topic = DRTopics.DR_PITCH_TOPIC
        self.yaw_topic = DRTopics.DR_YAW_TOPIC

        self.create_subscription(msg_type=Imu, topic=self.sbg_topic,
                                 callback=self.sbg_imu_callback, qos_profile=10)

        self.roll_pub = self.create_publisher(msg_type=Float64, topic=self.roll_topic, qos_profile=10)

        self.pitch_pub = self.create_publisher(msg_type=Float64, topic=self.pitch_topic, qos_profile=10)

        self.yaw_pub = self.create_publisher(msg_type=Float64, topic=self.yaw_topic, qos_profile=10)

    def sbg_imu_callback(self, sbg_msg):
        quat = sbg_msg.orientation
        euler = euler_from_quaternion([quat.x, quat.y, quat.z, quat.w])

        roll = euler[0]
        pitch = euler[1]
        yaw = euler[2]

        self.get_logger().info(f"(ENU) roll: {roll} - pitch: {pitch} - yaw: {yaw}")

        # Construct messages and publish
        roll_msg = Float64()
        roll_msg.data = roll
        self.roll_pub.publish(roll_msg)

        pitch_msg = Float64()
        pitch_msg.data = pitch
        self.pitch_pub.publish(pitch_msg)

        yaw_msg = Float64()
        yaw_msg.data = yaw
        self.yaw_pub.publish(yaw_msg)


def main(args=None, namespace=None):
    rclpy.init(args=args)
    rpy_node = SbGImu2rpy(namespace=namespace)
    try:
        rclpy.spin(rpy_node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    default_namespace = "sam0"
    main(namespace=default_namespace)
