#!/usr/bin/python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
import tf2_ros
import math
from tf_transformations import quaternion_from_euler


class MocapToEnuBroadcaster(Node):
    def __init__(self):
        super().__init__('mocap_to_enu_tf_broadcaster')

        # TF broadcaster
        self.broadcaster = tf2_ros.StaticTransformBroadcaster(self)

        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'mocap'
        t.child_frame_id = 'tank_base'

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

        self.broadcaster.sendTransform(t)
        self.get_logger().debug('Broadcasted mocap - tank_base transform')

        # Timer for broadcasting at 10 Hz
        # self.timer = self.create_timer(0.1, self.broadcast_transform)

    # def broadcast_transform(self):
        


def main(args=None):
    rclpy.init(args=args)
    node = MocapToEnuBroadcaster()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()