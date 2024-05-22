#!/usr/bin/python

# General
import math

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


def yaw_enu_2_compass_heading(yaw: float) -> float:
    """
    Calculates the compass heading from the yaw.

    :param yaw: yaw in radians w.r.t. to the ENU frame
    :return: compass_heading in degrees, 0-360
    """

    # Convert input yaw to degrees
    yaw_deg = yaw * (180 / math.pi)

    # Convert yaw (ENU) to heading (NED)
    heading = 90. - yaw_deg

    # Bound to 0 - 360
    compass_heading = heading % 360.

    return compass_heading


class YawEnu2CompassHeading(Node):
    """
    This node will convert the yaw (enu) to compass heading in degrees

    Note: this node will subscribe to the default yaw topic defined in dead_reckoning_msgs.
    """

    def __init__(self, namespace=None):
        super().__init__("yaw_enu_2_compass_heading", namespace=namespace)
        self.get_logger().info("Starting node defined in yaw_enu_2_compass_heading.py")

        self.yaw_topic = DRTopics.DR_YAW_TOPIC

        # Output topics
        # compass heading
        self.compass_heading_topic = DRTopics.DR_COMPASS_HEADING_TOPIC

        self.create_subscription(msg_type=Float64, topic=self.yaw_topic,
                                 callback=self.yaw_callback, qos_profile=10)

        self.compass_heading_pub = self.create_publisher(msg_type=Float64, topic=self.compass_heading_topic,
                                                         qos_profile=10)

    def yaw_callback(self, yaw_msg):
        yaw_enu = yaw_msg.data

        # Convert to
        compass_heading = yaw_enu_2_compass_heading(yaw_enu)

        #self.get_logger().info(f"Compass heading (deg): {compass_heading}")

        # Construct messages and publish
        compass_heading_msg = Float64()
        compass_heading_msg.data = compass_heading
        self.compass_heading_pub.publish(compass_heading_msg)


def main(args=None, namespace=None):
    rclpy.init(args=args)
    compass_heading_node = YawEnu2CompassHeading(namespace=namespace)
    try:
        rclpy.spin(compass_heading_node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    default_namespace = "sam0"
    main(namespace=default_namespace)
