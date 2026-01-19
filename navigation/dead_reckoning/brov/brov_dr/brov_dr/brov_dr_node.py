#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import numpy as np
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import TransformStamped
from tf2_ros import StaticTransformBroadcaster
from tf2_ros import TransformBroadcaster
from nav_msgs.msg import Odometry
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from geodesy import utm

from tf_transformations import (
    quaternion_inverse,
    quaternion_multiply,
    quaternion_matrix,
)

from geometry_msgs.msg import Quaternion
import math

# Brov Dead Reckoning Node: only for Saamarine with DVL
# It just gets /mavros/local_position/odom and initializes the origin with a GPS fix
class BrovDR(Node):
    
    def __init__(self):
        super().__init__('BrovDR')

        # Static TF broadcaster
        self.static_broadcaster = StaticTransformBroadcaster(self)

        self._transform_sent = False
        self.get_logger().info('Waiting for /fix to publish static TF world -> map')

        # Parameters
        self.declare_parameter('odom_topic', '/mavros/local_position/odom')
        self.declare_parameter('map_frame', 'map')        # source frame
        self.declare_parameter('base_frame', 'saabmarine/base_link')   # target frame
        self.declare_parameter('output_odom_topic', '/saabmarine/dr/odom')
        self.declare_parameter('odom_frame', 'saabmarine/odom')

        odom_topic = self.get_parameter('odom_topic').get_parameter_value().string_value
        self.map_frame = self.get_parameter('map_frame').get_parameter_value().string_value
        self.base_frame = self.get_parameter('base_frame').get_parameter_value().string_value
        self.odom_frame = self.get_parameter('odom_frame').get_parameter_value().string_value
        output_topic = self.get_parameter('output_odom_topic').value

        self.odom_pub = self.create_publisher(Odometry, output_topic, 10)

        # Internal state: pose starts at zero
        # Pose inicial
        self.initial_position = None      
        self.initial_orientation = None   
        self.initial_quat_inv = None      
        self.initial_rot_matrix = None

        self.last_time = None

        # TF broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        # Odom subscriber
        self.subscription = self.create_subscription(
            Odometry,
            odom_topic,
            self.odom_callback,
            qos_profile
        )

        # Subscribe to /fix
        self.subscription = self.create_subscription(
            NavSatFix,
            '/fix',
            self.gps_callback,
            10, 
        )


    def gps_callback(self, msg: NavSatFix):
        # Only use the first NavSatFix to define the static transform
        if self._transform_sent:
            return

        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = self.map_frame

        utm_coord = utm.fromLatLong(msg.latitude, msg.longitude)
        t.transform.translation.x = utm_coord.easting
        t.transform.translation.y = utm_coord.northing
        t.transform.translation.z = 0.

        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        # Publish as static transform
        self.static_broadcaster.sendTransform(t)
        self._transform_sent = True

        self.get_logger().info(
            f'Published static TF world -> map with '
            f'lat={msg.latitude}, lon={msg.longitude}, alt={msg.altitude}'
        )

    def odom_callback(self, msg: Odometry):
        # Pose actual
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        current_position = (p.x, p.y, p.z)
        current_orientation = (q.x, q.y, q.z, q.w)

        # Save origin from first received odom
        if self.initial_position is None:
            self.initial_position = current_position
            self.initial_orientation = current_orientation

            self.initial_quat_inv = quaternion_inverse(self.initial_orientation)
            self.initial_rot_matrix = quaternion_matrix(self.initial_quat_inv)
            self.get_logger().info("Initial odom pose captured as new origin.")

            t = TransformStamped()
            t.header.stamp = self.get_clock().now().to_msg()
            t.header.frame_id = self.map_frame
            t.child_frame_id = self.odom_frame

            t.transform.translation.x = 0.
            t.transform.translation.y = 0.
            t.transform.translation.z = 0.
            t.transform.rotation.x = msg.pose.pose.orientation.x
            t.transform.rotation.y = msg.pose.pose.orientation.y
            t.transform.rotation.z = msg.pose.pose.orientation.z
            t.transform.rotation.w = msg.pose.pose.orientation.w

            # Publish as static transform
            self.static_broadcaster.sendTransform(t)

            self.get_logger().info(
                f'Published static TF map -> odom with '
            )

        # p_rel = R(q0^-1) * (p - p0)
        dx = current_position[0] - self.initial_position[0]
        dy = current_position[1] - self.initial_position[1]
        dz = current_position[2] - self.initial_position[2]

        v = [dx, dy, dz, 1.0]
        p_rel_h = self.initial_rot_matrix.dot(v)
        p_rel = (p_rel_h[0], p_rel_h[1], p_rel_h[2])
        q_rel = quaternion_multiply(self.initial_quat_inv, current_orientation)

        new_msg = Odometry()
        new_msg.header = msg.header  
        new_msg.header.frame_id = self.odom_frame   
        new_msg.child_frame_id = self.base_frame

        new_msg.pose = msg.pose
        new_msg.pose.pose.position.x = p_rel[0]
        new_msg.pose.pose.position.y = p_rel[1]
        new_msg.pose.pose.position.z = p_rel[2]
        new_msg.pose.pose.orientation.x = q_rel[0]
        new_msg.pose.pose.orientation.y = q_rel[1]
        new_msg.pose.pose.orientation.z = q_rel[2]
        new_msg.pose.pose.orientation.w = q_rel[3]
        new_msg.twist = msg.twist

        self.publish_tf_odom(new_msg)


    @staticmethod
    def quaternion_to_msg(q_tuple) -> Quaternion:
        """Convert (x, y, z, w) tuple to geometry_msgs/Quaternion."""
        qx, qy, qz, qw = q_tuple
        q = Quaternion()
        q.x = qx
        q.y = qy
        q.z = qz
        q.w = qw
        return q

    @staticmethod
    def normalize_quaternion(q_tuple):
        """Normalize a quaternion (x, y, z, w)."""
        x, y, z, w = q_tuple
        norm = math.sqrt(x * x + y * y + z * z + w * w)
        if norm < 1e-12:
            return (0.0, 0.0, 0.0, 1.0)
        return (x / norm, y / norm, z / norm, w / norm)


    def publish_tf_odom(self, msg: Odometry):

        t = TransformStamped()
        # Use timestamp from the odometry message
        t.header.stamp = msg.header.stamp
        t.header.frame_id = self.odom_frame
        t.child_frame_id = self.base_frame

        # Copy position
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z

        # Flit to FRD frame
        q_enu_to_frd = np.array([1.0, 0.0, 0.0, 0.0])
        q_odom = np.array([
            msg.pose.pose.orientation.x,
            msg.pose.pose.orientation.y,
            msg.pose.pose.orientation.z,
            msg.pose.pose.orientation.w
        ])
        q_out = quaternion_multiply(q_odom, q_enu_to_frd)
        msg.pose.pose.orientation = self.quaternion_to_msg(q_out)#
        t.transform.rotation = self.quaternion_to_msg(q_out)#

        self.tf_broadcaster.sendTransform(t)
        self.odom_pub.publish(msg)



def main(args=None):
    rclpy.init(args=args)
    node = BrovDR()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
