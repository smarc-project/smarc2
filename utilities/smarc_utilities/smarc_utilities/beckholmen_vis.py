#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker

class DaeMarker(Node):
    def __init__(self):
        super().__init__('dae_marker_pub')
        self.pub = self.create_publisher(Marker, '/dae_marker', 10)
        self.tick()
        # self.timer = self.create_timer(0.5, self.tick)

    def tick(self):
        m = Marker()
        m.header.frame_id = 'beckholmen_map'
        m.header.stamp = self.get_clock().now().to_msg()
        m.ns = 'dae'
        m.id = 0
        m.type = Marker.MESH_RESOURCE
        m.action = Marker.ADD
        m.mesh_resource = 'package://watertank_description/mesh/beckholmen.dae'
        m.mesh_use_embedded_materials = True

        m.pose.orientation.w = 1.0
        m.scale.x = m.scale.y = m.scale.z = 1.0
        self.pub.publish(m)

def main():
    rclpy.init()
    node = DaeMarker()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()