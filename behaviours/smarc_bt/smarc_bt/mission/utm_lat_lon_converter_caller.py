from geographic_msgs.msg import GeoPoint
from rclpy.node import Node
from smarc_mission_msgs.msg import MissionControl, Topics as MissionTopics
from smarc_mission_msgs.srv import UTMLatLon


class UTMLatLonConverterCaller:
    def __init__(self, node: Node) -> None:
        self._node = node
        self._ll_utm_converter = self._node.create_client(UTMLatLon,
                                                          MissionTopics.UTM_LATLON_CONVERSION_SERVICE)

        self.reset()

    def _log(self, s:str):
        self._node.get_logger().info(s)

    def call(self, msg: MissionControl) -> None:
        self._converted = False
        self._mission_control_msg = msg

        request = UTMLatLon.Request()
        request.lat_lon_points = []
        for wp in msg.waypoints:
            gp = GeoPoint()
            gp.latitude = wp.lat
            gp.longitude = wp.lon
            request.lat_lon_points.append(gp)

        self._log("Calling ll-utm-converter service")
        self._future = self._ll_utm_converter.call_async(request)
        self._future.add_done_callback(self._done_cb)

    def _done_cb(self, future) -> None:
        result = future.result()

        for wp, utm_point in zip(self._mission_control_msg.waypoints, result.utm_points):
            wp.pose.pose.position.x = utm_point.point.x
            wp.pose.pose.position.y = utm_point.point.y

        self._converted = True


    def reset(self):
        self._mission_control_msg = None
        self._future = None
        self._converted = False


    @property
    def done(self) -> bool:
        return self._converted


    def get_result(self) -> MissionControl:
        if self.done:
            return self._mission_control_msg

        return None