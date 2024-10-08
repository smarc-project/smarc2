#!/usr/bin/python3

import rclpy, sys, math
from rclpy.node import Node

from geometry_msgs.msg import PointStamped
from smarc_mission_msgs.msg import Topics as MissionTopics
from smarc_mission_msgs.srv import UTMLatLon

from geodesy.utm import fromMsg, UTMPoint


class GeoConverterService:
    def __init__(self,
                 node: Node):
        self._node = node
        self._converter_service = self._node.create_service(UTMLatLon,
                                                            MissionTopics.UTM_LATLON_CONVERSION_SERVICE,
                                                            self._convert)

        self._log(f"UTM <-> LAT/LON Converter running on {MissionTopics.UTM_LATLON_CONVERSION_SERVICE}")

    def _log(self, s):
        self._node.get_logger().info(s)

    def _convert(self, request: UTMLatLon.Request, response: UTMLatLon.Response):
        self._log(f"Got {len(request.lat_lon_points)} latlon->utm and {len(request.utm_points)} utm->latlon points")
        return GeoConverterService.convert(request, response)

    def convert(request: UTMLatLon.Request, response: UTMLatLon.Response):
        response.utm_points = []
        response.lat_lon_points = []

        # convert all the latlons to utm
        for ll in request.lat_lon_points:
            # each is a GeoPoint already, so we can feed directly to geodesy
            # dont crash if 1 of 100 points is bad...
            try:
                pt = fromMsg(ll)
            except:
                response.utm_points.append(None)
                continue
            ps = PointStamped()
            ps.point = pt.toPoint()
            zone, band = pt.gridZone()
            ps.header.frame_id = f"utm_{zone}_{band}"
            response.utm_points.append(ps)

        # do the same, in reverse for utm->latlon
        for utm in request.utm_points:
            utm_pt = UTMPoint()
            utm_pt.easting = utm.point.x
            utm_pt.northing = utm.point.y
            _, zone, band = utm.header.frame_id.split("_")
            utm_pt.zone = int(zone)
            utm_pt.band = band
            # don't want to crash if 1 of 100 points was bad...
            try:
                msg = utm_pt.toMsg()
                if(math.isnan(msg.altitude)):
                    msg.altitude = 0.0
            except:
                msg = None

            response.lat_lon_points.append(msg)

        return response


def main():
    # create a node and our objects in the usual manner.
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("utm_latlon_converter")

    s = GeoConverterService(node)

    rclpy.spin(node)


def test_converter():
    from geographic_msgs.msg import GeoPoint

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("utm_latlon_converter_service_tester")

    client = node.create_client(UTMLatLon,
                                MissionTopics.UTM_LATLON_CONVERSION_SERVICE)

    while not client.wait_for_service(timeout_sec=1.0):
        node.get_logger().info("Can't reach the service?!")

    latlon_utm_pairs = [
        ((59.348518, 18.071837), (333508.24, 6582521.93, 34, "V")),  # -> smarc
        ((59.348419, 18.074798), (333676.05, 6582503.51, 34, "V")),  # -> rpl
        ((58.249679, 11.445581), (643529.33, 6459113.62, 32, "V"))  # -> kristineberg
    ]

    # request
    # rate = node.create_rate(frequency=1.0)
    count = 0

    while rclpy.ok():
        node.get_logger().info(f"Request Start: {count}")

        # Constuct request
        req = UTMLatLon.Request()
        req.utm_points = []
        req.lat_lon_points = []
        for ll, utm in latlon_utm_pairs:
            ps = PointStamped()
            ps.point.x = utm[0]
            ps.point.y = utm[1]
            ps.header.frame_id = f"utm_{utm[2]}_{utm[3]}"
            req.utm_points.append(ps)

            gp = GeoPoint()
            gp.latitude = ll[0]
            gp.longitude = ll[1]
            req.lat_lon_points.append(gp)

        future = client.call_async(req)
        rclpy.spin_until_future_complete(node, future)

        res = future.result()

        for i in range(len(res.lat_lon_points)):
            # these should match the latlon in the input
            ll_in = latlon_utm_pairs[i][0]
            ll_out = res.lat_lon_points[i]
            ll_out = (ll_out.latitude, ll_out.longitude)
            diffs = (abs(ll_in[0] - ll_out[0]), abs(ll_in[1] - ll_out[1]))
            node.get_logger().info(f"in:{ll_in}, out:{ll_out}, diff: {diffs}")

            utm_in = latlon_utm_pairs[i][1]
            utm_out = res.utm_points[i]
            _, zone, band = utm_out.header.frame_id.split("_")
            utm_out = (utm_out.point.x, utm_out.point.y, zone, band)
            diffs = (abs(utm_in[0] - utm_out[0]), abs(utm_in[1] - utm_out[1]))
            node.get_logger().info(f"in: {utm_in}, out: {utm_out}, diff: {diffs}")

        node.get_logger().info(f"Request complete: {count}")

        count += 1
        if count >= 10:
            break
