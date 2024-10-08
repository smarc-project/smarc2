#!/usr/bin/python

# General
import math

# ROS
import rclpy
from rclpy.node import Node
from rclpy import time

# Transforms
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from tf2_ros import LookupException, ConnectivityException, ExtrapolationException

from tf2_geometry_msgs import do_transform_pose
from tf_transformations import euler_from_quaternion  # quaternion_from_euler

# Messages
# from sbg_driver.msg import SbgEkfEuler ##
# from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose
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

    Note II: this node will use the raw odometry message until the odom listener does the proper conversions to the map
    frame from the odometry frame
    """

    def __init__(self, namespace=None):
        super().__init__("yaw_enu_2_compass_heading", namespace=namespace)
        self.get_logger().info("Starting node defined in yaw_enu_2_compass_heading.py")

        self.robot_name = namespace
        # Subscription topics
        self.odom_topic = DRTopics.DR_ODOM_TOPIC  # New
        self.yaw_topic = DRTopics.DR_YAW_TOPIC
        # Publisher topics
        # compass heading
        self.compass_heading_topic = DRTopics.DR_COMPASS_HEADING_TOPIC

        # Frame names
        self.map_frame = 'map'
        self.odom_frame = 'odom'

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.create_subscription(msg_type=Odometry, topic=self.odom_topic,
                                 callback=self.odom_callback, qos_profile=10)

        # self.create_subscription(msg_type=Float64, topic=self.yaw_topic,
        #                          callback=self.yaw_callback, qos_profile=10)

        self.compass_heading_pub = self.create_publisher(msg_type=Float64, topic=self.compass_heading_topic,
                                                         qos_profile=10)

    def yaw_callback(self, yaw_msg):
        yaw_enu = yaw_msg.data

        # Convert to
        compass_heading = yaw_enu_2_compass_heading(yaw_enu)

        # self.get_logger().info(f"Compass heading (deg): {compass_heading}")

        # Construct messages and publish
        compass_heading_msg = Float64()
        compass_heading_msg.data = compass_heading
        self.compass_heading_pub.publish(compass_heading_msg)

    def odom_callback(self, odom_msg):

        try:
            map_transform = self.tf_buffer.lookup_transform(target_frame=self.map_frame,
                                                            source_frame=odom_msg.header.frame_id,
                                                            time=rclpy.time.Time())

            odom_map_pose = self.transformed_odometry_to_pose(odom_msg, map_transform, self.map_frame)

            odom_map_rot = odom_map_pose.orientation

            rpy_map = euler_from_quaternion([odom_map_rot.x, odom_map_rot.y, odom_map_rot.z, odom_map_rot.w])

            compass_heading = yaw_enu_2_compass_heading(rpy_map[2])

            # Construct messages and publish
            compass_heading_msg = Float64()
            compass_heading_msg.data = compass_heading
            self.compass_heading_pub.publish(compass_heading_msg)

        except (LookupException, ConnectivityException, ExtrapolationException) as e:
            self.get_logger().error(f'Failed to transform odometry: {e}')

    def transformed_odometry_to_pose(self, odom_msg, transform, target_frame) -> Pose:
        # Create a new odometry message for the transformed odometry
        transformed_odom = Odometry()

        # Copy the header and twist information
        transformed_odom.header.stamp = self.get_clock().now().to_msg()
        transformed_odom.header.frame_id = target_frame
        transformed_odom.child_frame_id = odom_msg.child_frame_id
        transformed_odom.twist = odom_msg.twist

        # Transform the pose
        transformed_pose = do_transform_pose(odom_msg.pose.pose, transform)

        return transformed_pose


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
