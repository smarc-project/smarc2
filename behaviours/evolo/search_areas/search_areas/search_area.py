import rclpy
import math
import json

from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.action import ActionClient, ActionServer

from smarc_msgs.action import BaseAction

from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union, triangulate


_R_EARTH = 6371000.0


def _latlon_to_xy(lat, lon, origin_lat, origin_lon):
    dlat = math.radians(lat - origin_lat)
    dlon = math.radians(lon - origin_lon)
    x = dlon * _R_EARTH * math.cos(math.radians(origin_lat))
    y = dlat * _R_EARTH
    return x, y


def _xy_to_latlon(x, y, origin_lat, origin_lon):
    dlat = y / _R_EARTH
    dlon = x / (_R_EARTH * math.cos(math.radians(origin_lat)))
    return origin_lat + math.degrees(dlat), origin_lon + math.degrees(dlon)


class SearchArea(Node):
    def __init__(self):
        super().__init__('search_area')

        self.declare_parameters(
            namespace='',
            parameters=[
                ('move_path_action', rclpy.Parameter.Type.STRING),
                ('lane_spacing',     rclpy.Parameter.Type.DOUBLE),
                ('waypoint_tol',     rclpy.Parameter.Type.DOUBLE),
                ('speed',            rclpy.Parameter.Type.DOUBLE),
            ]
        )

        self.move_path_action = self.get_parameter('move_path_action').value
        self.lane_spacing     = self.get_parameter('lane_spacing').value
        self.waypoint_tol     = self.get_parameter('waypoint_tol').value
        self.speed            = self.get_parameter('speed').value

        cbg = ReentrantCallbackGroup()

        self._move_path_client = ActionClient(
            self, BaseAction, self.move_path_action, callback_group=cbg)

        self._planner_server = ActionServer(
            self, BaseAction, 'search_area',
            self._execute_callback, callback_group=cbg)

        self.get_logger().info('SearchArea (no obstacles, convex decomposition) started')

    # ─────────────────────────────────────────────────────────
    # Action callback
    # ─────────────────────────────────────────────────────────
    async def _execute_callback(self, goal_handle):
        self.get_logger().info('[SearchArea] Received planning request')

        try:
            payload = json.loads(goal_handle.request.goal.data)
        except Exception as e:
            self.get_logger().error(f'Invalid JSON: {e}')
            goal_handle.abort()
            return BaseAction.Result()

        area_pts = payload.get('area', [])
        speed    = payload.get('speed', self.speed)

        if not area_pts or len(area_pts) < 3:
            self.get_logger().error('No valid area polygon (need >= 3 points)')
            goal_handle.abort()
            return BaseAction.Result()

        inside_latlon = [(p['lat'], p['lon']) for p in area_pts]

        waypoints_latlon = self._generate_coverage(inside_latlon, self.lane_spacing)

        if not waypoints_latlon:
            self.get_logger().error('No waypoints generated')
            goal_handle.abort()
            return BaseAction.Result()

        self.get_logger().info(f'Generated {len(waypoints_latlon)} waypoints')

        success = await self._send_to_move_path(waypoints_latlon, speed)

        if not success:
            goal_handle.abort()
        else:
            goal_handle.succeed()

        return BaseAction.Result()

    # ═════════════════════════════════════════════════════════
    # CORE — coverage generation
    # ═════════════════════════════════════════════════════════
    def _generate_coverage(self, inside_latlon, lane_spacing_m):

        # ── Project lat/lon → XY ─────────────────────────────────────────────
        origin_lat = sum(p[0] for p in inside_latlon) / len(inside_latlon)
        origin_lon = sum(p[1] for p in inside_latlon) / len(inside_latlon)

        inside_xy = [
            _latlon_to_xy(lat, lon, origin_lat, origin_lon)
            for lat, lon in inside_latlon
        ]

        poly = Polygon(inside_xy)
        if poly.is_empty or not poly.is_valid:
            poly = poly.buffer(0)   # repair if necessary

        if poly.is_empty:
            return []

        sweep_angle = self._longest_edge_angle(inside_xy)

        # ── Convex → direct sweep ────────────────────────────────────────────
        if self._is_convex(poly):
            self.get_logger().info('Zone is convex — direct sweep')
            ordered_xy = self._sweep_polygon(poly, lane_spacing_m, sweep_angle)

        # ── Non-convex → triangular decomposition + merge + sweep ────────────
        else:
            self.get_logger().info('Zone is non-convex — triangular decomposition')
            cells = self._decompose_convex(poly)
            self.get_logger().info(f'Decomposed into {len(cells)} convex cell(s)')

            cell_paths = []
            for cell in cells:
                wps = self._sweep_polygon(cell, lane_spacing_m, sweep_angle)
                if wps:
                    cell_paths.append(wps)

            if not cell_paths:
                return []

            ordered_xy = self._chain_paths(cell_paths)

        # ── Reproject XY → lat/lon ───────────────────────────────────────────
        return [_xy_to_latlon(x, y, origin_lat, origin_lon) for x, y in ordered_xy]

    # ─────────────────────────────────────────────────────────
    # Convexity test
    # ─────────────────────────────────────────────────────────
    def _is_convex(self, poly: Polygon) -> bool:
        """
        A polygon is convex if its area equals the area of its
        convex hull (within a 1% tolerance).
        """
        hull = poly.convex_hull
        if hull.area < 1e-9:
            return True
        return abs(poly.area - hull.area) / hull.area < 0.01

    # ─────────────────────────────────────────────────────────
    # Convex decomposition: Shapely triangulation + greedy merge
    # ─────────────────────────────────────────────────────────
    def _decompose_convex(self, poly: Polygon) -> list:
        """
        1. Triangulates the polygon using shapely.ops.triangulate.
        2. Keeps only triangles contained within the polygon.
        3. Greedy-merges adjacent triangles into convex cells
           (union is valid only if the result remains convex within 1%).
        Returns a list of convex Polygons covering poly.
        """
        # ── Triangulation ────────────────────────────────────────────────────
        all_tris = triangulate(poly)
        tris = [t for t in all_tris if poly.contains(t) or poly.covers(t)]

        if not tris:
            # Fallback: return the polygon itself
            return [poly]

        self.get_logger().info(f'  Triangulated into {len(tris)} triangle(s)')

        # ── Greedy merge ─────────────────────────────────────────────────────
        cells  = list(tris)
        merged = True

        while merged:
            merged    = False
            used      = [False] * len(cells)
            new_cells = []

            for i in range(len(cells)):
                if used[i]:
                    continue

                current = cells[i]

                for j in range(i + 1, len(cells)):
                    if used[j]:
                        continue
                    if not current.touches(cells[j]):
                        continue

                    candidate = unary_union([current, cells[j]])

                    # Accept the merge only if the result is convex
                    if (candidate.geom_type == 'Polygon'
                            and abs(candidate.area - candidate.convex_hull.area)
                            / (candidate.convex_hull.area + 1e-9) < 0.01):
                        current    = candidate
                        used[j]    = True
                        merged     = True

                used[i] = True
                new_cells.append(current)

            cells = new_cells

        return cells

    # ─────────────────────────────────────────────────────────
    # Lawn-mower sweep over a convex polygon
    # ─────────────────────────────────────────────────────────
    def _sweep_polygon(self, poly: Polygon, lane_spacing_m: float,
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

        while y >= miny - lane_spacing_m * 0.5:
            line  = LineString([(minx - 1.0, y), (maxx + 1.0, y)])
            inter = poly_rot.intersection(line)

            if not inter.is_empty:
                if inter.geom_type == 'LineString':
                    raw_segs = [inter]
                elif hasattr(inter, 'geoms'):
                    raw_segs = [g for g in inter.geoms
                                if g.geom_type == 'LineString']
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

            y -= lane_spacing_m

        return waypoints_rot

    # ─────────────────────────────────────────────────────────
    # Greedy cell path chaining (approximate TSP)
    # ─────────────────────────────────────────────────────────
    def _chain_paths(self, cell_paths: list) -> list:
        remaining = list(cell_paths)
        result    = list(remaining.pop(0))

        while remaining:
            last      = result[-1]
            best_idx  = -1
            best_dist = float('inf')
            best_flip = False

            for i, path in enumerate(remaining):
                d_s = math.hypot(path[0][0]  - last[0], path[0][1]  - last[1])
                d_e = math.hypot(path[-1][0] - last[0], path[-1][1] - last[1])
                if d_s < best_dist:
                    best_dist, best_idx, best_flip = d_s, i, False
                if d_e < best_dist:
                    best_dist, best_idx, best_flip = d_e, i, True

            chosen = remaining.pop(best_idx)
            result.extend(reversed(chosen) if best_flip else chosen)

        return result

    # ─────────────────────────────────────────────────────────
    # Longest edge angle (sweep orientation)
    # ─────────────────────────────────────────────────────────
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

    # ─────────────────────────────────────────────────────────
    # Send waypoints to move_path
    # ─────────────────────────────────────────────────────────
    async def _send_to_move_path(self, waypoints_latlon, speed):
        self.get_logger().info(f'Waiting for action server: {self.move_path_action}')

        if not self._move_path_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('move_path action server unavailable')
            return False

        goal_msg = BaseAction.Goal()
        goal_msg.goal.data = json.dumps({
            'speed': speed,
            'mode':  'vwp',
            'waypoints': [
                {'latitude': lat, 'longitude': lon, 'tolerance': self.waypoint_tol}
                for lat, lon in waypoints_latlon
            ],
        })

        self.get_logger().info(f'Sending {len(waypoints_latlon)} waypoints to move_path')

        goal_handle = await self._move_path_client.send_goal_async(
            goal_msg, feedback_callback=self._feedback_cb)

        if not goal_handle.accepted:
            self.get_logger().error('move_path rejected goal')
            return False

        self.get_logger().info('move_path accepted goal — waiting for completion…')
        result = await goal_handle.get_result_async()

        if result.status == 4:
            self.get_logger().info('move_path completed successfully')
            return True

        self.get_logger().error(f'move_path ended with status={result.status}')
        return False

    def _feedback_cb(self, feedback_msg):
        try:
            data = json.loads(feedback_msg.feedback.feedback.data)
            self.get_logger().info(
                f'precision={data.get("precision_pct", "?")}% | '
                f'distance={data.get("distance_travelled", "?")}m'
            )
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
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