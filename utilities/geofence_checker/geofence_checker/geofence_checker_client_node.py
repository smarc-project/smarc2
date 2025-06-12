#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np

import rclpy
from rclpy.node import Node

from geographic_msgs.msg import GeoPoint
from smarc_mission_msgs.srv import GeoFenceChecker
from smarc_mission_msgs.msg import Topics as MissionTopics

class GeoFenceCheckerClient(Node):
    def __init__(self):
        super().__init__('geofence_checker_client')

        self.declare_parameter("verbose", False)
        self.verbose = self.get_parameter("verbose").value

        self.cli = self.create_client(srv_type=GeoFenceChecker,
                                      srv_name=MissionTopics.GEOFENCE_CHECKER_SERVICE)

        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for service geofence_checker...')

        self.req = GeoFenceChecker.Request()

        # Testing
        self.geofence = self.set_goefence_asko()
        self.test_points = []
        self.test_point_results = []
        self.step_count = 25


    def send_request(self, latitude, longitude):
        geopoint = GeoPoint()
        geopoint.latitude = latitude
        geopoint.longitude = longitude
        geopoint.altitude = 0.0
        self.req.geopoint = geopoint

        future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            valid = future.result().valid
            if self.verbose:
                self.get_logger().info(f"Result: {valid}")
            return valid
        else:
            self.get_logger().error(f'Service call failed: {future.exception()}')
            return None

    def set_goefence_asko(self):
        """
        Set geofence to asko
        """
        geofence = [(58.82340843380697, 17.63504927730432),
                    (58.82339234537327, 17.63333247097488),
                    (58.82313658210533, 17.63282176946456),
                    (58.82274289249682, 17.63300822776146),
                    (58.82233929757847, 17.63303259019619),
                    (58.82204921353041, 17.63271587944806),
                    (58.82154618191932, 17.63280916342387),
                    (58.821285285239, 17.63358102518024),
                    (58.82111275289891, 17.63420663339427),
                    (58.82114994251493, 17.63499700075815),
                    (58.82149845972899, 17.63494094670145),
                    (58.82174650200419, 17.63502216759974),
                    (58.82207021809655, 17.63505466876092),
                    (58.82232665647457, 17.63477821663079),
                    (58.82262912026778, 17.63446904208885),
                    (58.82294346132444, 17.63458097904721),
                    (58.82317133139508, 17.63507686273834),
                    (58.82317911826976, 17.63573905491145),
                    (58.82328740805892, 17.63572925868223),
                    (58.82327540403292, 17.63507536930186),
                    (58.82340843380697, 17.63504927730432)]

        return geofence

    def generate_test_points(self):
        if len(self.geofence) == 0:
            return
        lat_min = min([point[0] for point in self.geofence])
        lat_max = max([point[0] for point in self.geofence])

        lon_min = min([point[1] for point in self.geofence])
        lon_max = max([point[1] for point in self.geofence])

        y_vals = np.linspace(lat_min, lat_max, int(self.step_count))
        x_vals = np.linspace(lon_min, lon_max, int(self.step_count))

        grid = [(round(y, 10), round(x, 10)) for y in y_vals for x in x_vals]

        return grid

    def plot_polygon_with_point(self, lat, lon, result):
        """
        polygon: list of (y, x) tuples -- (lat, lon)
        point: (y, x) tuple -- (lat,lon)
        """
        y, x = lat, lon

        # Extract X and Y coordinates
        poly_y = [p[0] for p in self.geofence] + [self.geofence[0][0]]
        poly_x = [p[1] for p in self.geofence] + [self.geofence[0][1]]

        # Setup plot
        plt.figure(figsize=(6, 6))
        plt.plot(poly_x, poly_y, 'k-', linewidth=2, label='Polygon')
        plt.fill(poly_x, poly_y, 'lightgray', alpha=0.5)

        color = 'green' if result else 'red'
        plt.plot(x, y, 'o', color=color, markersize=10, label='Point')

        plt.title(f'Point is {"Inside" if result else "Outside"} the Polygon')
        plt.axis('equal')
        plt.grid(True)
        plt.legend()
        plt.show()

    def plot_polygon_with_test_points(self):
        """
        polygon: list of (y, x) tuples -- (lat, lon)
        point: (y, x) tuple -- (lat,lon)
        """
        if len(self.geofence) == 0:
            self.get_logger().info(f"Geofence not initialized!")
            return

        if len(self.test_points) != len(self.test_point_results):
            self.get_logger().info(f"Plotting size mismatch!")
            self.get_logger().info(f"{len(self.test_points)} - {len(self.test_point_results)}")
            return

        # Separate coordinates by flag
        x_true = [x for (y, x), f in zip(self.test_points, self.test_point_results) if f]
        y_true = [y for (y, x), f in zip(self.test_points, self.test_point_results) if f]

        x_false = [x for (y, x), f in zip(self.test_points, self.test_point_results) if not f]
        y_false = [y for (y, x), f in zip(self.test_points, self.test_point_results) if not f]

        # Extract X and Y coordinates
        poly_y = [p[0] for p in self.geofence] + [self.geofence[0][0]]
        poly_x = [p[1] for p in self.geofence] + [self.geofence[0][1]]

        # Setup plot
        plt.figure(figsize=(6, 6))

        plt.plot(poly_x, poly_y, 'k-', linewidth=2, label='Polygon')
        plt.fill(poly_x, poly_y, 'lightgray', alpha=0.5)

        # color = 'green' if result else 'red'
        # plt.plot(x, y, 'o', color=color, markersize=10, label='Point')
        plt.scatter(x_true, y_true, color='green', label='True')
        plt.scatter(x_false, y_false, color='red', label='False')

        plt.title(f"Test points in geofence")
        plt.axis('equal')
        plt.grid(True)
        plt.legend()
        plt.show()

    def perform_grid_testing(self):
        """
        Perform grid testing
        """

        self.test_points = self.generate_test_points()
        self.test_point_results = []

        self.get_logger().info(f"Grid testing: {len(self.test_points)}")

        for test_point in self.test_points:
            result = self.send_request(test_point[0], test_point[1])

            if result is not None:
                self.test_point_results.append(result)
            else:
                self.test_point_results.append(False)

        self.plot_polygon_with_test_points()

def main():
    rclpy.init()
    client = GeoFenceCheckerClient()

    single_point_test = False


    if single_point_test:
        """
        Perform single point testing
        """
        lat = 58.8231
        lon = 17.634
        count = 20
        result = False

        for _ in range(count):
            result = client.send_request(lat, lon)
            if result is not None:
                print(f"Service response: {result}")

        client.plot_polygon_with_point(lat=lat, lon=lon, result=result)
    else:
        """
        Perform a grid test over the bounds of the geofence
        """
        client.perform_grid_testing()

    client.destroy_node()
    # rclpy.shutdown()


if __name__ == '__main__':
    main()