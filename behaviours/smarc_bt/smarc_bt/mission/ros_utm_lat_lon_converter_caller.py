from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PointStamped

from rclpy.node import Node

from smarc_mission_msgs.msg import Topics as MissionTopics, GotoWaypoint
from smarc_mission_msgs.srv import UTMLatLon


class ROSLatLonUTMConverterCaller:
    def __init__(self, node: Node) -> None:
        self._node = node
        self._ll_utm_converter = self._node.create_client(UTMLatLon,
                                                          MissionTopics.UTM_LATLON_CONVERSION_SERVICE)

        self.reset()

    def _log(self, s:str):
        self._node.get_logger().info(s)

    def call_latlon_to_utm(self, goto_wps: list[GotoWaypoint]) -> None:
        self._converted = False
        self._goto_wps = goto_wps

        request = UTMLatLon.Request()
        request.lat_lon_points = []
        for wp in self._goto_wps:
            gp = GeoPoint()
            gp.latitude = wp.lat
            gp.longitude = wp.lon
            request.lat_lon_points.append(gp)

        self._log("Calling ll-utm-converter service")
        self._future = self._ll_utm_converter.call_async(request)
        self._future.add_done_callback(self._latlon_to_utm_done_cb)

    def _latlon_to_utm_done_cb(self, future) -> None:
        result = future.result()

        for wp, utm_point in zip(self._goto_wps, result.utm_points):
            wp.pose.pose.position.x = utm_point.point.x
            wp.pose.pose.position.y = utm_point.point.y

        self._converted = True


    def reset(self):
        self._goto_wps = None
        self._future = None
        self._converted = False


    @property
    def done(self) -> bool:
        return self._converted


    def get_result(self) -> list[GotoWaypoint]:
        if self.done:
            return self._goto_wps

        return None