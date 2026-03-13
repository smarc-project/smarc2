#!/usr/bin/python3

import os
import yaml

import rclpy, sys
from rclpy.node import Node
from ament_index_python import get_package_share_directory

from geographic_msgs.msg import GeoPoint
from smarc_mission_msgs.srv import GeoFenceChecker
from smarc_mission_msgs.msg import Topics as MissionTopics

class GeoFenceCheckerService(Node):
    def __init__(self, namespace=None):
        super().__init__('geofence_checker_service', namespace=namespace)

        self.declare_parameter('geofence_file', 'islands.yaml')
        # self.declare_parameter('geofence_file', 'obstacles_bathymetry.yaml')
        self.geofence_filename = self.get_parameter('geofence_file').value
        self.islands = self.read_geofence()

        self.declare_parameter("verbose", False)
        self.verbose = self.get_parameter("verbose").value

        self.srv = self.create_service(srv_type=GeoFenceChecker,
                                       srv_name=MissionTopics.GEOFENCE_CHECKER_SERVICE,
                                       callback=self.check_geopoint_callback)

        self.get_logger().info(f"Geofence checker service available on:{MissionTopics.GEOFENCE_CHECKER_SERVICE}")
        self.get_logger().info(f"Verbose: {self.verbose}")



    def read_geofence(self):
        """
        Read YAML file with geofence .
        Returns a dictionary with the values.
        """
        path_to_pkg = get_package_share_directory('evolo_move_path')
        yaml_path = os.path.join(path_to_pkg, "config", self.geofence_filename)
        with open(yaml_path, 'r') as file:
            loaded_yaml = yaml.safe_load(file)

        islands = []
        for name, coords in loaded_yaml.items():
            if name.startswith('island_') and coords:
            # if name.startswith('obstacle_') and coords:
                islands.append(coords)
                self.get_logger().info(f"Island '{name}' loaded with {len(coords)} points")

        return islands
    

    def is_point_inside_polygon(self, lat, lon, polygon):
        """
        Ray-casting algorithm.
        Returns True if (lat, lon) is inside the given polygon.
        """
        n = len(polygon)
        inside = False

        lat_1, lon_1 = polygon[0]
        for i in range(n + 1):
            lat_2, lon_2 = polygon[i % n]
            if lat > min(lat_1, lat_2):
                if lat <= max(lat_1, lat_2):
                    if lon <= max(lon_1, lon_2):
                        if lat_1 != lat_2:
                            lon_inters = (lat - lat_1) * (lon_2 - lon_1) / (lat_2 - lat_1) + lon_1
                        if lon_1 == lon_2 or lon <= lon_inters:
                            inside = not inside
            lat_1, lon_1 = lat_2, lon_2

        return inside

    def check_geopoint_callback(self, request: GeoFenceChecker.Request, response: GeoFenceChecker.Response):
        lat, lon = request.geopoint.latitude, request.geopoint.longitude

        if self.verbose:
            self.get_logger().info(f"Service call - lat: {lat}, lon: {lon}")
        in_island = any(self.is_point_inside_polygon(lat, lon, island) for island in self.islands)

        response.valid = not in_island 
        return response
    

def main(args=None, namespace=None):
    rclpy.init(args=args)
    node = GeoFenceCheckerService(namespace=namespace)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down")
        node.destroy_node()
        # rclpy.shutdown()


if __name__ == "__main__":
    default_namespace = "evolo"
    main(namespace=default_namespace)