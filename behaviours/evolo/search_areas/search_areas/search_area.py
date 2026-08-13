import rclpy
import math
import json

from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped
from geographic_msgs.msg import GeoPoint
from smarc_msgs.msg import Topics as smarcTopics
from smarc_utilities import georef_utils
from tf2_ros import Buffer, TransformListener
from tf2_geometry_msgs import do_transform_pose_stamped
from rclpy.time import Time, Duration

from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle

from smarc_msgs.action import BaseAction
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union, triangulate
from smarc_action_base.gentler_action_server import GentlerActionServer


_R_EARTH = 6371000.0

_SPEED_MAP = {'fast': 6.0, 'slow': 4.0, 'standard': 5.0}


# ─────────────────────────────────────────────────────────────────────────
def _parse_speed(node: Node, speed_raw, default: float = 5.0) -> float:
    if isinstance(speed_raw, str):
        val = _SPEED_MAP.get(speed_raw.lower())
        if val is None:
            node.get_logger().warn(
                f"[Speed] Unrecognized speed level '{speed_raw}' "
                f"(expected one of {list(_SPEED_MAP)}) — using default {default} m/s"
            )
            return default
        return val
    try:
        return float(speed_raw)
    except (TypeError, ValueError):
        node.get_logger().warn(f"[Speed] Invalid speed value {speed_raw!r} — using default {default} m/s")
        return default


# ─────────────────────────────────────────────────────────────────────────
def _latlon_to_xy(lat, lon, origin_lat, origin_lon):
    dlat = math.radians(lat - origin_lat)
    dlon = math.radians(lon - origin_lon)
    x = dlon * _R_EARTH * math.cos(math.radians(origin_lat))
    y = dlat * _R_EARTH
    return x, y

# ─────────────────────────────────────────────────────────────────────────
def _xy_to_latlon(x, y, origin_lat, origin_lon):
    dlat = y / _R_EARTH
    dlon = x / (_R_EARTH * math.cos(math.radians(origin_lat)))
    return origin_lat + math.degrees(dlat), origin_lon + math.degrees(dlon)

# ─────────────────────────────────────────────────────────────────────────
class SearchArea(Node):
    """
    Single-zone boustrophedon coverage planner.

    Goal payload (flat WARAPS behavior-tree convention, no "task" wrapper):
        {
          "speed": "low" | "medium" | "high" | "standard" | <float>,
          "area": [{"latitude":.., "longitude":..}, ...],   # single polygon
          "obstacle": [
              [{"latitude":.., "longitude":..}, ...], ...   # optional, unused here yet
          ]
        }

    Can be called directly (single zone) or as a sub-goal fanned out by
    'search_areas' (multi-zone orchestrator) — the payload shape is
    identical either way.
    """

    def __init__(self):
        super().__init__('search_area')

        self.declare_parameters(
            namespace='',
            parameters=[
                ('move_path_action', rclpy.Parameter.Type.STRING),
                ('spacing',     rclpy.Parameter.Type.DOUBLE),
                ('waypoint_tol',     rclpy.Parameter.Type.DOUBLE),
                ('speed',            rclpy.Parameter.Type.DOUBLE),
            ]
        )

        self.move_path_action = self.get_parameter('move_path_action').value
        self.spacing     = self.get_parameter('spacing').value
        self.waypoint_tol     = self.get_parameter('waypoint_tol').value
        self.speed            = self.get_parameter('speed').value

        cbg = ReentrantCallbackGroup()

        self._move_path_client = ActionClient(
            self, BaseAction, self.move_path_action, callback_group=cbg)

        self._pending_payload: dict = {}
        self._waypoints_latlon: list = []
        self._speed_mission: float = self.speed

        self._mp_goal_future   = None
        self._mp_result_future = None
        self._mp_goal_handle: ClientGoalHandle | None = None
        self._last_feedback: dict = {}

        self._server = GentlerActionServer(
            node=self,
            action_name='search_area',
            on_goal_received=self._on_goal_received,
            on_cancel_received=self._on_cancel_received,
            prepare_loop=self._prepare_loop,
            loop_inner=self._loop_inner,
            give_feedback=self._give_feedback,
            loop_frequency=5.0,
        )

        self._tf_buffer   = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self)
        self._robot_pose_raw: PoseStamped | None = None

        self.robot_sub = self.create_subscription(
            Odometry, smarcTopics.ODOM_TOPIC, self._robot_odom_callback, 10,
            callback_group=cbg)

        self.get_logger().info('SearchArea started')


    # ─────────────────────────────────────────────────────────────────────────
    def _on_goal_received(self, payload: dict) -> bool:
        area_pts = payload.get('area', [])
        if not area_pts or len(area_pts) < 3:
            self.get_logger().error('[Goal] Need >= 3 area points')
            return False
        self._pending_payload = payload
        return True


    # ─────────────────────────────────────────────────────────────────────────
    def _on_cancel_received(self) -> bool:
        self.get_logger().info('[SearchArea] Cancel requested')
        if self._mp_goal_handle is not None:
            self.get_logger().info('[SearchArea] Cancelling active move_path sub-goal')
            self._mp_goal_handle.cancel_goal_async()
        return True

    # ─────────────────────────────────────────────────────────────────────────
    def _robot_odom_callback(self, msg: Odometry):
        ps = PoseStamped()
        ps.header = msg.header
        ps.pose   = msg.pose.pose
        self._robot_pose_raw = ps


    # ─────────────────────────────────────────────────────────────────────────
    def _prepare_loop(self) -> None:
        payload   = self._pending_payload
        area_pts  = payload.get('area', [])
        speed_raw = payload.get('speed', self.speed)
        self._speed_mission = _parse_speed(self, speed_raw, default=self.speed)

        self._mp_goal_future   = None
        self._mp_result_future = None
        self._mp_goal_handle   = None
        self._last_feedback    = {}

        spacing = float(payload.get('spacing', self.spacing)) 

        inside_latlon = [(p['latitude'], p['longitude']) for p in area_pts]
        self._waypoints_latlon = self._generate_coverage(inside_latlon, spacing)  

        if self._waypoints_latlon:
            self.get_logger().info(f'[SearchArea] Generated {len(self._waypoints_latlon)} waypoints')
        else:
            self.get_logger().error('[SearchArea] No waypoints generated')

        if not self._move_path_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error(f'move_path action server unavailable: {self.move_path_action}')
            self._server_unavailable = True
        else:
            self._server_unavailable = False


    # ─────────────────────────────────────────────────────────────────────────
    def _loop_inner(self) -> bool | None:
        if getattr(self, '_server_unavailable', False):
            return False

        if not self._waypoints_latlon:
            return False

        # ── Phase 1: send goal ────────────────────────────────────────────────
        if self._mp_goal_future is None and self._mp_result_future is None:
            goal_msg = BaseAction.Goal()
            goal_msg.goal.data = json.dumps({
                'speed': self._speed_mission,
                'waypoints': [
                    {'latitude': lat, 'longitude': lon, 'tolerance': self.waypoint_tol}
                    for lat, lon in self._waypoints_latlon
                ],
            })
            self.get_logger().info(f'[SearchArea] Sending {len(self._waypoints_latlon)} waypoints to move_path')
            self._mp_goal_future = self._move_path_client.send_goal_async(
                goal_msg,
                feedback_callback=self._feedback_cb,
            )
            return None

        # ── Phase 2: wait for acceptance ──────────────────────────────────────
        if self._mp_goal_future is not None and self._mp_result_future is None:
            if not self._mp_goal_future.done():
                return None

            self._mp_goal_handle = self._mp_goal_future.result()
            self._mp_goal_future = None

            if not self._mp_goal_handle.accepted:
                self.get_logger().error('[SearchArea] move_path rejected goal')
                return False

            self.get_logger().info('[SearchArea] move_path accepted goal — waiting for result…')
            self._mp_result_future = self._mp_goal_handle.get_result_async()
            return None

        # ── Phase 3: wait for result ──────────────────────────────────────────
        if self._mp_result_future is not None:
            if not self._mp_result_future.done():
                return None

            result = self._mp_result_future.result()
            self._mp_result_future = None
            self._mp_goal_handle   = None

            if result.status == 4:   
                self.get_logger().info('[SearchArea] move_path completed successfully')
                return True

            self.get_logger().error(f'[SearchArea] move_path ended with status={result.status}')
            return False

        return None


    # ─────────────────────────────────────────────────────────────────────────
    def _give_feedback(self) -> str:
        return json.dumps({
            'waypoints_total': len(self._waypoints_latlon),
            'sub_feedback':    self._last_feedback,
        })


    # ─────────────────────────────────────────────────────────────────────────
    def _feedback_cb(self, feedback_msg):
        try:
            data = json.loads(feedback_msg.feedback.feedback.data)
            self._last_feedback = data
            self.get_logger().info(
                f'[move_path] '
                f'total={data.get("total_progress_pct", "?")}% | '
                f'wp[{data.get("wp_current_idx", "?")}]={data.get("wp_progress_pct", "?")}% | '
                f'precision={data.get("precision_pct", "?")}% | '
                f'distance={data.get("distance_travelled", "?")}m'
            )
        except Exception:
            pass


    # ─────────────────────────────────────────────────────────────────────────
    def _generate_coverage(self, inside_latlon, spacing_m):
        origin_lat = sum(p[0] for p in inside_latlon) / len(inside_latlon)
        origin_lon = sum(p[1] for p in inside_latlon) / len(inside_latlon)

        inside_xy = [
            _latlon_to_xy(lat, lon, origin_lat, origin_lon)
            for lat, lon in inside_latlon
        ]

        poly = Polygon(inside_xy)
        if poly.is_empty or not poly.is_valid:
            poly = poly.buffer(0)
        if poly.is_empty:
            return []

        sweep_angle = self._longest_edge_angle(inside_xy)

        if self._is_convex(poly):
            self.get_logger().info('Zone is convex — direct sweep')
            ordered_xy = self._sweep_polygon(poly, spacing_m, sweep_angle)
        else:
            self.get_logger().info('Zone is non-convex — triangular decomposition')
            cells = self._decompose_convex(poly)
            self.get_logger().info(f'Decomposed into {len(cells)} convex cell(s)')

            cell_paths, valid_cells = [], []
            for cell in cells:
                cell_angle = self._longest_edge_angle(list(cell.exterior.coords)[:-1])
                wps = self._sweep_polygon(cell, spacing_m, cell_angle)
                if wps:
                    cell_paths.append(wps)
                    valid_cells.append(cell)

            if not cell_paths:
                return []
            ordered_xy = self._chain_paths(valid_cells, cell_paths)

        robot_xy = self._get_robot_xy(origin_lat, origin_lon)
        if robot_xy is not None and ordered_xy:
            nearest_idx = min(
                range(len(ordered_xy)),
                key=lambda i: math.hypot(ordered_xy[i][0] - robot_xy[0],
                                        ordered_xy[i][1] - robot_xy[1])
            )
            ordered_xy = ordered_xy[nearest_idx:] + list(reversed(ordered_xy[:nearest_idx]))

        return [_xy_to_latlon(x, y, origin_lat, origin_lon) for x, y in ordered_xy]


    def _get_robot_xy(self, origin_lat, origin_lon):
        if self._robot_pose_raw is None:
            return None
        try:
            gp = GeoPoint()
            gp.latitude, gp.longitude, gp.altitude = origin_lat, origin_lon, 0.0
            utm_ref = georef_utils.convert_latlon_to_utm(gp)

            t = self._tf_buffer.lookup_transform(
                target_frame=utm_ref.header.frame_id,
                source_frame=self._robot_pose_raw.header.frame_id,
                time=Time(seconds=0),
                timeout=Duration(seconds=1))
            robot_pose_utm = do_transform_pose_stamped(self._robot_pose_raw, t)

            geo = georef_utils.convert_utm_to_latlon(robot_pose_utm)
            return _latlon_to_xy(geo.latitude, geo.longitude, origin_lat, origin_lon)
        except Exception as e:
            self.get_logger().warn(f'[Coverage] Position of the robot is not available: {e}')
            return None
        

    # ─────────────────────────────────────────────────────────────────────────
    def _is_convex(self, poly: Polygon) -> bool:
        return self._polygon_is_convex(poly)

    # ─────────────────────────────────────────────────────────────────────────
    def _polygon_is_convex(self, poly: Polygon, tol: float = 1e-7) -> bool:
        coords = list(poly.exterior.coords)[:-1]
        n = len(coords)
        if n < 3:
            return True
        sign = 0
        for i in range(n):
            a = coords[i]
            b = coords[(i + 1) % n]
            c = coords[(i + 2) % n]
            cross = (b[0]-a[0])*(c[1]-b[1]) - (b[1]-a[1])*(c[0]-b[0])
            if abs(cross) < tol:
                continue 
            s = 1 if cross > 0 else -1
            if sign == 0:
                sign = s
            elif s != sign:
                return False
        return True

    def _ear_clip_triangulate(self, ring_coords) -> list:
        pts = list(ring_coords)
        if len(pts) >= 2 and pts[0] == pts[-1]:
            pts = pts[:-1]
        n = len(pts)
        if n < 3:
            return []

        area2 = sum(pts[i][0]*pts[(i+1) % n][1] - pts[(i+1) % n][0]*pts[i][1] for i in range(n))
        if area2 < 0:
            pts = pts[::-1]

        def is_convex_vertex(a, b, c):
            return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0]) > 1e-12

        def point_in_triangle(p, a, b, c):
            def sign(p1, p2, p3):
                return (p1[0]-p3[0])*(p2[1]-p3[1]) - (p2[0]-p3[0])*(p1[1]-p3[1])
            d1, d2, d3 = sign(p, a, b), sign(p, b, c), sign(p, c, a)
            neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
            pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
            return not (neg and pos)

        indices = list(range(len(pts)))
        triangles = []
        guard = 0
        while len(indices) > 3 and guard < 10000:
            guard += 1
            ear_found = False
            m = len(indices)
            for k in range(m):
                i_prev, i_curr, i_next = indices[(k-1) % m], indices[k], indices[(k+1) % m]
                a, b, c = pts[i_prev], pts[i_curr], pts[i_next]
                if not is_convex_vertex(a, b, c):
                    continue
                if any(point_in_triangle(pts[idx], a, b, c)
                    for idx in indices if idx not in (i_prev, i_curr, i_next)):
                    continue
                triangles.append(Polygon([a, b, c]))
                indices.pop(k)
                ear_found = True
                break
            if not ear_found:
                self.get_logger().warn('[EarClip] Stop, weird polygon')
                break

        if len(indices) == 3:
            triangles.append(Polygon([pts[i] for i in indices]))

        return triangles

    # ─────────────────────────────────────────────────────────────────────────
    def _decompose_convex(self, poly: Polygon) -> list:
        tris = self._ear_clip_triangulate(list(poly.exterior.coords))
        if not tris:
            return [poly]

        self.get_logger().info(f'  Triangulated into {len(tris)} triangle(s)')

        def shares_edge(p1: Polygon, p2: Polygon) -> bool:
            inter = p1.intersection(p2)
            return inter.geom_type in ('LineString', 'MultiLineString') and inter.length > 1e-9

        cells = list(tris)
        merged = True
        while merged:
            merged = False
            n = len(cells)
            used = set()
            new_cells = []
            for i in range(n):
                if i in used:
                    continue
                current = cells[i]
                for j in range(i + 1, n):
                    if j in used or not shares_edge(current, cells[j]):
                        continue
                    candidate = unary_union([current, cells[j]])
                    if candidate.geom_type == 'Polygon' and self._polygon_is_convex(candidate):
                        current = candidate
                        used.add(j)
                        merged = True
                used.add(i)
                new_cells.append(current)
            cells = new_cells

        return cells


    # ─────────────────────────────────────────────────────────────────────────
    def _sweep_polygon(self, poly: Polygon, spacing_m: float,
                   sweep_angle: float) -> list:
        cos_a = math.cos(-sweep_angle)
        sin_a = math.sin(-sweep_angle)

        def rot(x, y):     return  cos_a*x - sin_a*y,  sin_a*x + cos_a*y
        def rot_inv(x, y): return  cos_a*x + sin_a*y, -sin_a*x + cos_a*y

        poly_rot = Polygon([rot(x, y) for x, y in poly.exterior.coords])
        minx, miny, maxx, maxy = poly_rot.bounds

        y       = maxy
        reverse = False
        waypoints_rot = []

        while y >= miny - spacing_m * 0.5:
            line  = LineString([(minx - 1.0, y), (maxx + 1.0, y)])
            inter = poly_rot.intersection(line)

            if not inter.is_empty:
                if inter.geom_type == 'LineString':
                    raw_segs = [inter]
                elif hasattr(inter, 'geoms'):
                    raw_segs = [g for g in inter.geoms if g.geom_type == 'LineString']
                else:
                    raw_segs = []

                if reverse:
                    raw_segs = list(reversed(raw_segs))

                for seg in raw_segs:
                    coords = list(seg.coords)
                    if len(coords) < 2:
                        continue
                    p1, p2 = coords[0], coords[-1]
                    if reverse:
                        p1, p2 = p2, p1
                    waypoints_rot.append(rot_inv(*p1))
                    waypoints_rot.append(rot_inv(*p2))

                reverse = not reverse

            y -= spacing_m

        return waypoints_rot

    # ─────────────────────────────────────────────────────────────────────────
    def _chain_paths(self, cells: list, cell_paths: list, start_xy=None) -> list:
        n = len(cells)

        def shares_edge(p1, p2):
            inter = p1.intersection(p2)
            return inter.geom_type in ('LineString', 'MultiLineString') and inter.length > 1e-9

        adj = {i: set() for i in range(n)}
        for i in range(n):
            for j in range(i + 1, n):
                if shares_edge(cells[i], cells[j]):
                    adj[i].add(j)
                    adj[j].add(i)

        if start_xy is not None:
            start_pt = Point(start_xy)
            start_idx = min(range(n), key=lambda i: cells[i].centroid.distance(start_pt))
        else:
            start_idx = 0

        visited, order, stack = set(), [], [start_idx]
        while stack:
            cur = stack.pop()
            if cur in visited:
                continue
            visited.add(cur)
            order.append(cur)
            neighbors = sorted(adj[cur] - visited,
                                key=lambda j: cells[cur].centroid.distance(cells[j].centroid))
            stack.extend(reversed(neighbors))

        for i in range(n):
            if i not in visited:
                order.append(i)
                visited.add(i)

        result = list(cell_paths[order[0]])
        for idx in order[1:]:
            path = cell_paths[idx]
            last = result[-1]
            d_s = math.hypot(path[0][0] - last[0], path[0][1] - last[1])
            d_e = math.hypot(path[-1][0] - last[0], path[-1][1] - last[1])
            result.extend(reversed(path) if d_e < d_s else path)

        return result


    # ─────────────────────────────────────────────────────────────────────────
    def _longest_edge_angle(self, pts: list) -> float:
        best_len, best_angle = -1.0, 0.0
        n = len(pts)
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            l = math.hypot(x2 - x1, y2 - y1)
            if l > best_len:
                best_len   = l
                best_angle = math.atan2(y2 - y1, x2 - x1)
        return best_angle


# ─────────────────────────────────────────────────────────────────────────────
def main(args=None):
    rclpy.init(args=args)
    node = SearchArea()

    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard interrupt')
    finally:
        executor.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
