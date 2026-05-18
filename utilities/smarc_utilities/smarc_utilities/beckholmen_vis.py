#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker

class MeshMarker(Node):
    def __init__(self):
        super().__init__('mesh_marker_pub')
        self.pub = self.create_publisher(Marker, '/mesh_marker', 10)

        self.tick()
        # self.timer = self.create_timer(0.5, self.tick)

    def tick(self):
        m = Marker()
        m.header.frame_id = 'beckholmen_map'
        m.header.stamp = self.get_clock().now().to_msg()

        m.ns = 'mesh'
        m.id = 0
        m.type = Marker.MESH_RESOURCE
        m.action = Marker.ADD
        # The current mesh resource is a file path to a .obj
        # To use a package resource, you can use a path like 'package://smarc_utilities/meshes/your_mesh.obj'
        # NOTE: I found there to be a weird offset when using dae files, the rviz origin of the mesh is not the same as the origin of the mesh in Cloudcompare. 
        # This caused issues with the computed transform.
        m.mesh_resource = 'file:///root/dufomap_data/models/obj_scaled_no_boat/12_09_2025.obj'  # Working
        m.mesh_resource = 'package://watertank_description/mesh/beckholmen.dae'  # Alternative
        # Original
        # m.mesh_use_embedded_materials = True

        # Attempt to lighten the model
        # m.mesh_use_embedded_materials = False
        m.color.r = 0.8
        m.color.g = 0.8
        m.color.b = 0.8
        m.color.a = 0.5

        m.pose.orientation.w = 1.0
        m.scale.x = m.scale.y = m.scale.z = 1.0
        self.pub.publish(m)

def main():
    rclpy.init()
    node = MeshMarker()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()