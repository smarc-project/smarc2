#!/usr/bin/python3

from enum import Enum
import rclpy

from rclpy.node import Node
from rclpy.time import Time, Duration
from rclpy.executors import MultiThreadedExecutor
from builtin_interfaces.msg import Time as TimeMsg

from tf2_geometry_msgs import do_transform_point
from tf2_ros import Buffer, TransformListener


from geographic_msgs.msg import GeoPoint, GeoPath, GeoPointStamped
from geographic_msgs.srv import GetGeoPath
from geometry_msgs.msg import Point, Point32, Polygon
from visualization_msgs.msg import Marker, MarkerArray

from smarc_msgs.msg import Topics as SmarcTopics
from smarc_msgs.msg import GeofenceStatusStamped, GeofencePolygonsStamped
from smarc_action_base.gentler_action_server import GentlerActionServer
from smarc_utilities.georef_utils import convert_latlon_to_utm


class PointInPolyResults(Enum):
    INVALID = -2
    INSIDE = -1
    # matches the GeofenceStatusStamped reason for outside
    OUTSIDE_LATLON = 0 
    OUTSIDE_CEILING = 1
    OUTSIDE_FLOOR = 2
    INSIDE_ISLAND = 3

class GeofenceNode():
    def __init__(self, node: Node):
        self._node = node

        self._geopoint_sub = self._node.create_subscription(GeoPoint, SmarcTopics.POS_LATLON_TOPIC, self.pos_latlon_cb, 10)
        self._geofence_status_pub = self._node.create_publisher(GeofenceStatusStamped, SmarcTopics.GEOFENCE_STATUS_TOPIC, 10)
        self._geofence_msg = GeofenceStatusStamped()

        self._geofence_polygons_pub = self._node.create_publisher(GeofencePolygonsStamped, SmarcTopics.GEOFENCE_POLYGONS_TOPIC, 10)
        self._geofence_polygons_msg = GeofencePolygonsStamped()
        self._rviz_pub = self._node.create_publisher(MarkerArray, SmarcTopics.GEOFENCE_POLYGONS_TOPIC+'/rviz', 10)

        self._start_as = GentlerActionServer(
            node,
            "smarc_start_geofence",
            self._on_goal_received_start,
            self._on_cancel_received_start,
            lambda: None,
            lambda: True,
            lambda: "Geofence node running",
            loop_frequency = 5
        )

        self._stop_as = GentlerActionServer(
            node,
            "smarc_stop_geofence",
            self._on_goal_received_stop,
            lambda: True,
            lambda: None,
            lambda: True,
            lambda: "Geofence node stopped",
            loop_frequency = 5
        )

        self._check_fence_srv = node.create_service(GetGeoPath, SmarcTopics.CHECK_GEOFENCE_SERVICE_TOPIC, self._check_fence_srv_cb)


        self._robot_position : GeoPoint | None = None
        self._robot_position_time : Time | None = None
        self._fences : list[list[GeoPoint]] | list = []
        self._islands : list[list[GeoPoint]] | list = []

        self._fences_in_map : list[list[tuple[float, float, float]]] | list = [] 
        self._islands_in_map : list[list[tuple[float, float, float]]] | list = []

        self._ceiling_altitude : float | None = None
        self._floor_altitude : float | None = None # aka depth for underwater vehicles
        self._fence_start_time : TimeMsg | None = None

        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self._node)

        self._node.declare_parameter('map_frame', 'M350/map')
        self._map_frame : str = self._node.get_parameter('map_frame').get_parameter_value().string_value
        self._node.get_logger().info(f"Using map frame: {self._map_frame}")
        self._utm_frame : str | None = None # will be set on first position message

        self._node.declare_parameter('check_period', 0.5)
        self._check_period = self._node.get_parameter('check_period').get_parameter_value().double_value
        self._pub_timer = self._node.create_timer(self._check_period, self.publish_geofence_ok)

        self._node.declare_parameter('max_position_age', 1.0)
        self._max_position_age = self._node.get_parameter('max_position_age').get_parameter_value().double_value
        self._max_position_duration = Duration(seconds=int(self._max_position_age), nanoseconds=int((self._max_position_age - int(self._max_position_age)) * 1e9))

        self._node.declare_parameter('polygon_publish_period', 5.0)
        self._polygon_publish_period = self._node.get_parameter('polygon_publish_period').get_parameter_value().double_value
        self._polygon_pub_timer = self._node.create_timer(self._polygon_publish_period, self._publish_geofence_polygons)


    def valid_geofence_setup(self) -> bool:
        if self._fences is None or self._islands is None or (len(self._fences) < 1 and len(self._islands) < 1):
            return False
        return True

    def pos_latlon_cb(self, msg: GeoPoint):
        self._robot_position_time = self._node.get_clock().now()
        self._robot_position = msg

        if self._utm_frame is None:
            ps = convert_latlon_to_utm(msg)
            self._utm_frame = ps.header.frame_id
            self._node.get_logger().info(f"Setting UTM frame to {self._utm_frame} based on first received robot latlon position")


    def publish_geofence_ok(self):
        self._geofence_msg.time = self._node.get_clock().now().to_msg()

        if self._robot_position is None or self._robot_position_time is None: 
            self._node.get_logger().info("No robot position received yet...")
            self._geofence_msg.status = GeofenceStatusStamped.STATUS_INACTIVE
            self._geofence_status_pub.publish(self._geofence_msg)
            return
        
        if not self.valid_geofence_setup(): 
            self._node.get_logger().info("No valid geofence or island defined yet...")
            self._geofence_msg.status = GeofenceStatusStamped.STATUS_INACTIVE
            self._geofence_status_pub.publish(self._geofence_msg)
            return

        if self._robot_position_time + self._max_position_duration < self._node.get_clock().now():
            self._node.get_logger().info(f"Robot position is older than {self._max_position_age}s, not publishing geofence_ok")
            self._geofence_msg.status = GeofenceStatusStamped.STATUS_INACTIVE
            self._geofence_status_pub.publish(self._geofence_msg)
            return

        fence_status = self._point_is_safe(self._robot_position)
        t = f"{self._robot_position_time.seconds_nanoseconds()[0]:.2f}s" if self._robot_position_time is not None else "unknown time"
        if fence_status == PointInPolyResults.INSIDE:
            self._node.get_logger().info(f"Robot is INSIDE t={t}")
            self._geofence_msg.status = GeofenceStatusStamped.STATUS_INSIDE
        elif fence_status == PointInPolyResults.OUTSIDE_LATLON:
            self._node.get_logger().warn(f"Robot is OUTSIDE(latlon) t={t}")
            self._geofence_msg.status = GeofenceStatusStamped.STATUS_OUTSIDE
            self._geofence_msg.outside_reason = GeofenceStatusStamped.REASON_FENCE
        elif fence_status == PointInPolyResults.OUTSIDE_CEILING:
            self._node.get_logger().warn(f"Robot is OUTSIDE(ceiling) t={t}")
            self._geofence_msg.status = GeofenceStatusStamped.STATUS_OUTSIDE
            self._geofence_msg.outside_reason = GeofenceStatusStamped.REASON_CEILING
        elif fence_status == PointInPolyResults.OUTSIDE_FLOOR:
            self._node.get_logger().warn(f"Robot is OUTSIDE(floor) t={t}")
            self._geofence_msg.status = GeofenceStatusStamped.STATUS_OUTSIDE
            self._geofence_msg.outside_reason = GeofenceStatusStamped.REASON_FLOOR
        elif fence_status == PointInPolyResults.INSIDE_ISLAND:
            self._node.get_logger().warn(f"Robot is INSIDE ISLAND t={t}")
            self._geofence_msg.status = GeofenceStatusStamped.STATUS_OUTSIDE
            self._geofence_msg.outside_reason = GeofenceStatusStamped.REASON_ISLAND
        else:
            self._node.get_logger().error(f"Invalid geofence status for robot position t={t}")
            self._geofence_msg.status = GeofenceStatusStamped.STATUS_INACTIVE
        
        self._geofence_status_pub.publish(self._geofence_msg)


    
    def _publish_geofence_polygons(self):
        self._geofence_polygons_msg.header.stamp = self._node.get_clock().now().to_msg()
        self._geofence_polygons_msg.header.frame_id = self._map_frame

        def geopoint_poly_to_map(poly: list[GeoPoint]) -> list[tuple[float, float, float]]:
            if self._utm_frame is None:
                self._node.get_logger().error("Cannot transform geofence polygon to map frame because UTM frame is not set yet")
                return []
            
            transformed_poly = []
            utm_to_map_transform = self._tf_buffer.lookup_transform(self._map_frame, self._utm_frame, Time())
            for point in poly:
                ps = convert_latlon_to_utm(point)
                try:
                    transformed_ps = do_transform_point(ps, utm_to_map_transform)
                    transformed_poly.append((transformed_ps.point.x, transformed_ps.point.y, point.altitude))
                except Exception as e:
                    self._node.get_logger().error(f"Error transforming geofence polygon point to map frame: {e}")
                    return []
            
            return transformed_poly

        map_fences = [geopoint_poly_to_map(fence) for fence in self._fences]
        map_islands = [geopoint_poly_to_map(island) for island in self._islands]

        def map_poly_to_polygon_msg(map_poly: list[tuple[float, float, float]]) -> Polygon:
            polygon_msg = Polygon()
            if len(map_poly) < 3:
                self._node.get_logger().error("Invalid polygon, must be a list of at least 3 GeoPoints transformed to map frame")
                return polygon_msg
            polygon_msg.points = [Point32(x=point[0], y=point[1], z=point[2]) for point in map_poly]
            return polygon_msg
        
        self._geofence_polygons_msg.geofence = [map_poly_to_polygon_msg(fence) for fence in map_fences]
        self._geofence_polygons_msg.islands = [map_poly_to_polygon_msg(island) for island in map_islands]

        self._geofence_polygons_pub.publish(self._geofence_polygons_msg)

        def map_poly_to_marker_msg(poly: list[tuple[float, float, float]], marker_id: int, color: tuple[float, float, float, float]) -> Marker:
            marker = Marker()
            marker.header.stamp = self._node.get_clock().now().to_msg()
            marker.header.frame_id = self._map_frame
            marker.ns = "geofence"
            marker.id = marker_id
            marker.type = Marker.LINE_STRIP
            marker.action = Marker.MODIFY
            marker.scale.x = 0.1
            marker.color.r = float(color[0])
            marker.color.g = float(color[1])
            marker.color.b = float(color[2])
            marker.color.a = float(color[3])
            marker.points = []
            for point in poly:
                p = Point()
                p.x = float(point[0])
                p.y = float(point[1])
                p.z = float(point[2])
                marker.points.append(p)
            # close the loop
            if len(poly) > 0:
                p = Point()
                p.x = float(poly[0][0])
                p.y = float(poly[0][1])
                p.z = float(poly[0][2])
                marker.points.append(p)
            return marker
        
        fence_markers = [map_poly_to_marker_msg(fence, i, (1.0, 0.0, 0.0, 1.0)) for i, fence in enumerate(map_fences)]
        island_markers = [map_poly_to_marker_msg(island, len(map_fences)+i, (0.0, 1.0, 0.0, 1.0)) for i, island in enumerate(map_islands)]
        marker_array = MarkerArray(markers=fence_markers + island_markers)
        self._rviz_pub.publish(marker_array)

        

    def _on_goal_received_start(self, goal_request: dict) -> bool:
        try:
            wps = goal_request['waypoints']
            if len(wps) < 3:
                self._node.get_logger().error("Geofence action server requires at least 3 waypoints to define a geofence")
                return False
            
            try:
                inside = bool(goal_request['stay_inside'])
            except KeyError:
                self._node.get_logger().warn("No 'stay_inside' field in geofence goal, defaulting to stay_inside=True")
                inside = True

            poly = [(GeoPoint(latitude=float(wp['latitude']), longitude=float(wp['longitude']))) for wp in wps]
            if inside:
                self._fences.append(poly)
            else:
                self._islands.append(poly)

            ceiling = float(goal_request['ceiling_altitude'])
            floor = float(goal_request['floor_altitude'])
            if ceiling > floor:
                self._ceiling_altitude = ceiling 
                self._floor_altitude = floor
            else:
                self._node.get_logger().warn("Ceiling altitude is not greater than floor altitude, ignoring altitude limits")
                self._ceiling_altitude = None
                self._floor_altitude = None
            self._fence_start_time = self._node.get_clock().now().to_msg()
            self._node.get_logger().info(f"Geofence defined with {len(self._fences)} fences and {len(self._islands)} islands, ceiling altitude {self._ceiling_altitude}, floor altitude {self._floor_altitude}")
            self._publish_geofence_polygons()
            return True

        except Exception as e:
            self._node.get_logger().error(f"Error parsing geofence waypoints: {e}")
            return False
        
    def _on_goal_received_stop(self, goal_request: dict) -> bool:
        fence_reset = bool(goal_request['reset_geofence'])
        if fence_reset:
            self._fences = []
            self._floor_altitude = None
            self._ceiling_altitude = None
        
        island_reset = bool(goal_request['reset_islands'])
        if island_reset:
            self._islands = []

        self._fence_start_time = None
        self._node.get_logger().info(f"Geofence stopped. Fences reset: {fence_reset}, Islands reset: {island_reset}")
        self._publish_geofence_polygons()
        return True
        
    def _on_cancel_received_start(self):
        self._fences = []
        self._islands = []
        self._ceiling_altitude = None
        self._floor_altitude = None
        self._fence_start_time = None
        self._node.get_logger().info("Geofence cleared")
        self._publish_geofence_polygons()
        return True
    
    def _point_is_safe(self, point: GeoPoint) -> PointInPolyResults:
        if not self.valid_geofence_setup(): return PointInPolyResults.INVALID

        if self._ceiling_altitude is not None:
            if point.altitude > self._ceiling_altitude: return PointInPolyResults.OUTSIDE_CEILING

        if self._floor_altitude is not None:
            if point.altitude < self._floor_altitude: return PointInPolyResults.OUTSIDE_FLOOR

        inside_fences = any(is_point_inside_polygon(point, fence) for fence in self._fences)
        if not inside_fences: return PointInPolyResults.OUTSIDE_LATLON

        inside_islands = any(is_point_inside_polygon(point, island) for island in self._islands)
        if inside_islands: return PointInPolyResults.INSIDE_ISLAND
        
        return PointInPolyResults.INSIDE
    

    def _check_fence_srv_cb(self, request: GetGeoPath.Request, response: GetGeoPath.Response):
        if not self.valid_geofence_setup():
            response.success = False
            response.status = "No geofence or islands defined"
            self._node.get_logger().info(f"Get geofence request response: {response.status}")
            return response
        
        valid_start = not (request.start.altitude == 0.0 and request.start.latitude == 0.0 and request.start.longitude == 0.0)
        valid_end = not (request.goal.altitude == 0.0 and request.goal.latitude == 0.0 and request.goal.longitude == 0.0)

        if valid_start and not valid_end:
            response.success = self._point_is_safe(request.start) == PointInPolyResults.INSIDE
            response.status = "Start point is valid" if response.success else "Start point is outside geofence"
            self._node.get_logger().info(response.status)
            return response
        
        if valid_end and not valid_start:
            response.success = self._point_is_safe(request.goal) == PointInPolyResults.INSIDE
            response.status = "Goal point is valid" if response.success else "Goal point is outside geofence"
            self._node.get_logger().info(response.status)
            return response
        
        if valid_end and valid_start:
            response.success = self._point_is_safe(request.start) == PointInPolyResults.INSIDE and self._point_is_safe(request.goal) == PointInPolyResults.INSIDE
            response.status = "Start and goal points are valid" if response.success else "Start and/or goal point is outside geofence"
            self._node.get_logger().info(response.status)
            return response
        

        response.success = False
        response.status = "No valid start or goal point provided"
        self._node.get_logger().info(response.status)
        return response
        


# lifted from "utils/geofence_checker/geofence_checker/geofence_checker_node.py"
# this node should supercede that one
def is_point_inside_polygon(point: GeoPoint, vertices: list[GeoPoint]) -> bool:
    n = len(vertices)
    inside = False

    lat_1, lon_1 = vertices[0].latitude, vertices[0].longitude
    for i in range(n + 1):
        lat_2, lon_2 = vertices[i % n].latitude, vertices[i % n].longitude
        if point.latitude > min(lat_1, lat_2):
            if point.latitude <= max(lat_1, lat_2):
                if point.longitude <= max(lon_1, lon_2):
                    if lat_1 != lat_2:
                        lon_inters = (point.latitude - lat_1) * (lon_2 - lon_1) / (lat_2 - lat_1) + lon_1
                    if lon_1 == lon_2 or point.longitude <= lon_inters: # type: ignore
                        inside = not inside
        lat_1, lon_1 = lat_2, lon_2

    return inside




def main():
    rclpy.init()
    node = Node("geofence_node")
    geofence_node = GeofenceNode(node)
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down")
        node.destroy_node()


def test_action():
    import json
    from smarc_action_base.bt_action_client_action import A_ActionClient
    from py_trees.trees import BehaviourTree

    goal = {
        "waypoints": [
            {"latitude": 59.0, "longitude": 18.0, "altitude": 0},
            {"latitude": 59.0, "longitude": 18.1, "altitude": 0},
            {"latitude": 59.1, "longitude": 18.1, "altitude": 0},
            {"latitude": 59.1, "longitude": 18.0, "altitude": 0},
        ],
        "ceiling_altitude": 20.0,
        "floor_altitude": 8.0,
    }
    goal = json.dumps(goal)

    rclpy.init()
    node = Node("geofence_test_client")
    action_client = A_ActionClient(node, "start_geofence")
    action_client.setup()
    action_client.set_goal(goal)

    tree = BehaviourTree(action_client)
    node.create_timer(10, tree.tick)

    latlonpub = node.create_publisher(GeoPoint, SmarcTopics.POS_LATLON_TOPIC, 10)
    alt = 0.1
    lat = 59.05
    def publish_test_position():
        nonlocal alt, lat, node
        if alt < 19:
            alt += 1.0
        else:
            lat += 0.01
        msg = GeoPoint(latitude=lat, longitude=18.05, altitude=alt)
        node.get_logger().info(f"Publishing test position: {msg}")
        latlonpub.publish(msg)

    node.create_timer(0.5, publish_test_position)

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    rclpy.spin(node, executor=executor)
    rclpy.shutdown()

    
    
    




if __name__ == "__main__":
    main()