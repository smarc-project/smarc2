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

        self.declare_parameter('geofence_file', 'asko.yaml')
        self.geofence_filename = self.get_parameter('geofence_file').value
        self.geofence = self.read_geofence()

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
        path_to_pkg = get_package_share_directory('geofence_checker')

        yaml_path = os.path.join(path_to_pkg, "config", self.geofence_filename)
        with open(yaml_path, 'r') as file:
            loaded_yaml = yaml.safe_load(file)

        geofence = loaded_yaml['geofence']

        self.get_logger().info(f"Geofence configured with filename {self.geofence_filename}")

        [self.get_logger().info(f"{i}: ({lat}, {lon})") for i, (lat, lon) in enumerate(geofence)]

        return geofence

    def is_point_inside_polygon(self, lat, lon):
        """
        lat, lon
        geofence is a list of (lat, lon) tuples
        """
        n = len(self.geofence)
        inside = False

        lat_1, lon_1 = self.geofence[0]
        for i in range(n + 1):
            lat_2, lon_2 = self.geofence[i % n]
            if lat > min(lat_1, lat_2):
                if lat <= max(lat_1, lat_2):
                    if lon <= max(lon_1, lon_2):
                        if lat_1 != lat_2:
                            lon_inters = (lat - lat_1) * (lon_2 - lon_1) / (lat_2 - lat_1) + lon_1
                            print(lon_inters)
                        if lon_1 == lon_2 or lon <= lon_inters:
                            inside = not inside
            lat_1, lon_1 = lat_2, lon_2

        return inside

    def check_geopoint_callback(self, request: GeoFenceChecker.Request, response: GeoFenceChecker.Response):
        lat, lon = request.geopoint.latitude, request.geopoint.longitude

        if self.verbose:
            self.get_logger().info(f"Service call - lat: {lat}, lon: {lon}")

        valid = self.is_point_inside_polygon(lat=lat,
                                             lon=lon)

        response.valid = valid
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
    default_namespace = "lolo"
    main(namespace=default_namespace)
