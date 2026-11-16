#!/usr/bin/env python3
"""Example of using the smarc_georef_cpp Python bindings from an rclpy node.

Once a second it runs three separate examples:
  1. Convert a hard coded GeoPoint to a PointStamped in lolo/base_link
  2. Convert a hard coded PointStamped in lolo/base_link to a GeoPoint
  3. Get the transform from lolo/base_link to lolo/odom, and apply it to a point with
     tf2_geometry_msgs

    ros2 run smarc_georef_examples georef_example_node.py
"""

import rclpy
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PointStamped
from rclpy.node import Node
from tf2_geometry_msgs import do_transform_point

from smarc_georef_cpp import GeorefUtils, TransformException


class GeorefExampleNode(Node):

    def __init__(self):
        super().__init__('georef_example_node')

        # Creates the C++ GeorefUtils with its own internal rclcpp node and tf listener
        # thread. Nothing needs to be added to the rclpy executor. Passing node=self copies
        # this node's use_sim_time to it.
        self.georef = GeorefUtils(node=self)

        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        self.geopoint_to_vehicle_frame()
        self.vehicle_frame_to_geopoint()
        self.base_link_to_odom_transform()

    def geopoint_to_vehicle_frame(self):
        """1. GeoPoint -> PointStamped in lolo/base_link."""
        geopoint = GeoPoint(latitude=59.35, longitude=18.07, altitude=0.0)

        try:
            point = self.georef.geopoint_to_point_stamped(geopoint, 'lolo/base_link')
        except TransformException as e:
            # Happens until the utm frame and lolo/base_link have been received over tf
            self.get_logger().warn(f'1. Not ready: {e}', throttle_duration_sec=5.0)
            return

        p = point.point
        self.get_logger().info(
            f'1. GeoPoint ({geopoint.latitude:.7f}, {geopoint.longitude:.7f}) -> '
            f'{point.header.frame_id} ({p.x:.2f}, {p.y:.2f}, {p.z:.2f})')

    def vehicle_frame_to_geopoint(self):
        """2. PointStamped in lolo/base_link -> GeoPoint."""
        point = PointStamped()
        point.header.frame_id = 'lolo/base_link'
        point.point.x = 10.0  # 10 m ahead of the vehicle

        try:
            geopoint = self.georef.point_stamped_to_geopoint(point)
        except TransformException as e:
            # Happens until the utm frame and lolo/base_link have been received over tf
            self.get_logger().warn(f'2. Not ready: {e}', throttle_duration_sec=5.0)
            return

        p = point.point
        self.get_logger().info(
            f'2. {point.header.frame_id} ({p.x:.2f}, {p.y:.2f}, {p.z:.2f}) -> GeoPoint '
            f'({geopoint.latitude:.7f}, {geopoint.longitude:.7f}, {geopoint.altitude:.2f})')

    def base_link_to_odom_transform(self):
        """3. Transform from lolo/base_link to lolo/odom, i.e. the vehicle pose in lolo/odom.

        The transform comes from the C++ tf listener, so this node needs no TransformListener
        of its own. It is then applied to a point with tf2_geometry_msgs.
        """
        try:
            tf = self.georef.lookup_transform('lolo/odom', 'lolo/base_link')
        except TransformException as e:
            # Happens until lolo/odom and lolo/base_link have been received over tf
            self.get_logger().warn(f'3. Not ready: {e}', throttle_duration_sec=5.0)
            return

        t = tf.transform.translation
        self.get_logger().info(
            f'3. lolo/base_link in lolo/odom: ({t.x:.2f}, {t.y:.2f}, {t.z:.2f})')

        # Apply the transform: a point 10 m ahead of the vehicle, in lolo/odom
        point = PointStamped()
        point.header.frame_id = 'lolo/base_link'
        point.point.x = 10.0
        point_odom = do_transform_point(point, tf)

        p, q = point.point, point_odom.point
        self.get_logger().info(
            f'3. {point.header.frame_id} ({p.x:.2f}, {p.y:.2f}, {p.z:.2f}) -> '
            f'{point_odom.header.frame_id} ({q.x:.2f}, {q.y:.2f}, {q.z:.2f})')

    def destroy_node(self):
        # Stop the C++ tf listener thread and destroy its internal node now, instead of
        # whenever Python garbage collects self.georef. That may be after rclpy has shut down,
        # or never if something still holds a reference to it.
        self.georef.shutdown()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = GeorefExampleNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
