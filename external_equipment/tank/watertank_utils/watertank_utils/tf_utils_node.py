#!/usr/bin/python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
import tf2_ros
import math
from tf_transformations import quaternion_from_euler
from geodesy import utm
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy
from sensor_msgs.msg import NavSatFix

class MocapToEnuBroadcaster(Node):
    def __init__(self):
        super().__init__('mocap_to_enu_tf_broadcaster')

        # Latched QoS profile
        qos_profile = QoSProfile(
            depth=1,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.SYSTEM_DEFAULT
        )

        self.publisher = self.create_publisher(NavSatFix, '/mocap/tank/gps', qos_profile)
        self.timer = self.create_timer(0.02, self.timer_cb)  # 50Hz

        # TF broadcaster
        self.br_mocap_tank = tf2_ros.StaticTransformBroadcaster(self)
        self.br_utm_tank = tf2_ros.StaticTransformBroadcaster(self)
        self.br_local_tank = tf2_ros.StaticTransformBroadcaster(self)
        self.br_mocap_sonar = tf2_ros.StaticTransformBroadcaster(self)
        self.br_mocap_mocap_enu = tf2_ros.StaticTransformBroadcaster(self)

        t_utm = TransformStamped()
        t_utm.header.stamp = self.get_clock().now().to_msg()
        t_utm.header.frame_id = 'utm_34_V'
        t_utm.child_frame_id = 'tank_local'
        
        utm_tank = utm.fromLatLong(59.3508558333, 18.0681783333)
        t_utm.transform.translation.x = utm_tank.easting
        t_utm.transform.translation.y = utm_tank.northing
        t_utm.transform.translation.z = 0.0

        q_utm = quaternion_from_euler(0, 0, 0)
        t_utm.transform.rotation.x = q_utm[0]
        t_utm.transform.rotation.y = q_utm[1]
        t_utm.transform.rotation.z = q_utm[2]
        t_utm.transform.rotation.w = q_utm[3]

        self.br_utm_tank.sendTransform(t_utm)
        self.get_logger().info('Broadcasted utm - tank_base transform')

        t_local = TransformStamped()
        t_local.header.stamp = self.get_clock().now().to_msg()
        t_local.header.frame_id = 'tank_local'
        t_local.child_frame_id = 'tank_base'
        
        t_local.transform.translation.x = 0.0
        t_local.transform.translation.y = 0.0
        t_local.transform.translation.z = 0.0

        q_local = quaternion_from_euler(0, 0, math.radians(212))
        t_local.transform.rotation.x = q_local[0]
        t_local.transform.rotation.y = q_local[1]
        t_local.transform.rotation.z = q_local[2]
        t_local.transform.rotation.w = q_local[3]

        self.br_local_tank.sendTransform(t_local)
        self.get_logger().info('Broadcasted utm - tank_base transform')

        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'tank_base'
        t.child_frame_id = 'mocap'

        # No translation offset
        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 3.0

        # 180 deg yaw + 90 deg roll = rotation from NED to ENU
        q = quaternion_from_euler(math.radians(180), 0, 0)
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]

        self.br_mocap_tank.sendTransform(t)
        self.get_logger().info('Broadcasted mocap - tank_base transform')

        t_sonar = TransformStamped()
        t_sonar.header.stamp = self.get_clock().now().to_msg()
        t_sonar.header.frame_id = 'mocap'
        t_sonar.child_frame_id = 'sonar'
        t_sonar.transform.translation.x = 0.276
        t_sonar.transform.translation.y = 0.164
        t_sonar.transform.translation.z = 0.231

        q_local = quaternion_from_euler(0.09259, -0.332, -0.027)
        t_sonar.transform.rotation.x = q_local[0]
        t_sonar.transform.rotation.y = q_local[1]
        t_sonar.transform.rotation.z = q_local[2]
        t_sonar.transform.rotation.w = q_local[3]

        self.br_mocap_sonar.sendTransform(t_sonar)
        self.get_logger().info('Broadcasted utm - tank_base transform')

        t_enu = TransformStamped()
        t_enu.header.stamp = self.get_clock().now().to_msg()
        t_enu.header.frame_id = 'mocap'
        t_enu.child_frame_id = 'mocap_enu'
        t_enu.transform.translation.x = 0.0
        t_enu.transform.translation.y = 0.0
        t_enu.transform.translation.z = 0.0

        q_local = quaternion_from_euler(math.radians(180), 0, 0)
        t_enu.transform.rotation.x = q_local[0]
        t_enu.transform.rotation.y = q_local[1]
        t_enu.transform.rotation.z = q_local[2]
        t_enu.transform.rotation.w = q_local[3]

        self.br_mocap_mocap_enu.sendTransform(t_enu)
        self.get_logger().info('Broadcasted mocap -- mocap_enu transform')

        # Timer for broadcasting at 10 Hz
        # self.timer = self.create_timer(0.1, self.broadcast_transform)

    def timer_cb(self):

        # Create and publish one GPS message
        gps_msg = NavSatFix()
        gps_msg.header.stamp = self.get_clock().now().to_msg()
        gps_msg.header.frame_id = 'tank_base'
        gps_msg.latitude = 59.350925
        gps_msg.longitude = 18.068231
        gps_msg.altitude = 0.0

        self.publisher.publish(gps_msg)
        # self.get_logger().info('Latched GPS message published.')

        


def main(args=None):
    rclpy.init(args=args)
    node = MocapToEnuBroadcaster()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()