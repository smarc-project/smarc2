import rclpy
import math
import json

from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.action import ActionClient, ActionServer

from smarc_msgs.action import BaseAction

from shapely.geometry import Polygon, LineString, MultiPolygon
from shapely.ops import unary_union, triangulate
from shapely.affinity import affine_transform


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
                ('obstacle_buffer',  rclpy.Parameter.Type.DOUBLE),  # buffer distance in meters
            ]
        )

        self.move_path_action = self.get_parameter('move_path_action').value
        self.lane_spacing     = self.get_parameter('lane_spacing').value
        self.waypoint_tol     = self.get_parameter('waypoint_tol').value
        self.speed            = self.get_parameter('speed').value
        self.obstacle_buffer  = self.get_parameter('obstacle_buffer').value

        cbg = ReentrantCallbackGroup()

        self._move_path_client = ActionClient(
            self, BaseAction, self.move_path_action, callback_group=cbg)

        self._planner_server = ActionServer(
            self, BaseAction, 'search_area',
            self._execute_callback, callback_group=cbg)

        self.get_logger().info('SearchArea (polygon-with-holes sweep) started')

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

        area_pts      = payload.get('area', [])
        obstacles_raw = payload.get('obstacles', [])   # [[{"lat","lon"}, ...], ...]
        speed         = payload.get('speed', self.speed)
        buf_dist      = payload.get('obstacle_buffer', self.obstacle_buffer)

        if not area_pts or len(area_pts) < 3:
            self.get_logger().error('No valid area polygon (need >= 3 points)')
            goal_handle.abort()
            return BaseAction.Result()

        inside_latlon    = [(p['lat'], p['lon']) for p in area_pts]
        obstacles_latlon = [
            [(p['lat'], p['lon']) for p in obs]
            for obs in obstacles_raw
            if len(obs) >= 3
        ]

        waypoints_latlon = self._generate_coverage(
            inside_latlon, obstacles_latlon, self.lane_spacing, buf_dist)

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
    # CORE — coverage generation with obstacle holes
    # ═════════════════════════════════════════════════════════
    def _generate_coverage(self, inside_latlon, obstacles_latlon,
                           lane_spacing_m, buf_dist_m):

        # ── Project lat/lon → XY ─────────────────────────────────────────────
        origin_lat = sum(p[0] for p in inside_latlon) / len(inside_latlon)
        origin_lon = sum(p[1] for p in inside_latlon) / len(inside_latlon)

        def to_xy(latlon_list):
            return [_latlon_to_xy(lat, lon, origin_lat, origin_lon)
                    for lat, lon in latlon_list]

        area_poly = Polygon(to_xy(inside_latlon))
        if not area_poly.is_valid:
            area_poly = area_poly.buffer(0)

        # ── Buffer each obstacle and subtract from the search area ───────────
        buffered_obstacles = []
        for obs_latlon in obstacles_latlon:
            obs_poly = Polygon(to_xy(obs_latlon))
            if not obs_poly.is_valid:
                obs_poly = obs_poly.buffer(0)
            # Buffer the obstacle, then clip to the search area boundary
            clipped = obs_poly.buffer(buf_dist_m).intersection(area_poly)
            if not clipped.is_empty:
                buffered_obstacles.append(clipped)

        # Polygon with holes = area minus union of all buffered obstacles
        if buffered_obstacles:
            search_zone = area_poly.difference(unary_union(buffered_obstacles))
        else:
            search_zone = area_poly

        if search_zone.is_empty:
            self.get_logger().error('Search zone is empty after obstacle subtraction')
            return []

        self.get_logger().info(
            f'Search zone: {search_zone.geom_type} | '
            f'{len(buffered_obstacles)} hole(s) carved out'
        )

        sweep_angle = self._longest_edge_angle(to_xy(inside_latlon))

        # ── Sweep the holed polygon directly ─────────────────────────────────
        # Shapely's intersection() handles holes automatically:
        # a sweep line through a Polygon-with-holes returns only the
        # segments in the valid (non-hole) area — no extra obstacle logic needed.
        ordered_xy = self._sweep_holed_polygon(search_zone, lane_spacing_m, sweep_angle)

        if not ordered_xy:
            return []

        # ── Reproject XY → lat/lon ───────────────────────────────────────────
        return [_xy_to_latlon(x, y, origin_lat, origin_lon) for x, y in ordered_xy]

    # ─────────────────────────────────────────────────────────
    # Lawn-mower sweep — works on any Shapely geometry
    # (Polygon with or without holes, MultiPolygon)
    # ─────────────────────────────────────────────────────────
    def _sweep_holed_polygon(self, geom, lane_spacing_m: float,
                             sweep_angle: float) -> list:
        """
        Balaye la géométrie en gérant proprement les scissions d'obstacles.
        Garantit que le robot termine un côté de l'obstacle avant de passer à l'autre.
        """
        cos_a = math.cos(-sweep_angle)
        sin_a = math.sin(-sweep_angle)

        def rot_inv(x, y): 
            return cos_a*x + sin_a*y, -sin_a*x + cos_a*y

        # Rotation globale de la zone de recherche
        geom_rot = affine_transform(geom, [cos_a, -sin_a, sin_a, cos_a, 0, 0])
        minx, miny, maxx, maxy = geom_rot.bounds

        y = maxy
        reverse = False
        
        left_channel_segments = []
        right_channel_segments = []
        waypoints_final = []

        while y >= miny - lane_spacing_m * 0.5:
            line = LineString([(minx - 1.0, y), (maxx + 1.0, y)])
            inter = geom_rot.intersection(line)

            if not inter.is_empty:
                if inter.geom_type == 'LineString':
                    raw_segs = [inter]
                elif inter.geom_type in ('MultiLineString', 'GeometryCollection'):
                    raw_segs = [g for g in inter.geoms if g.geom_type == 'LineString']
                else:
                    raw_segs = []

                if raw_segs:
                    # Toujours trier de gauche à droite dans le repère local
                    raw_segs.sort(key=lambda s: (s.coords[0][0] + s.coords[-1][0]) / 2)

                    # CAS 1 : Ligne continue (Pas d'obstacle au milieu)
                    if len(raw_segs) == 1:
                        # Si on avait accumulé des segments divisés par un obstacle, on les vide d'abord
                        if left_channel_segments or right_channel_segments:
                            waypoints_final.extend(
                                self._resolve_channels(left_channel_segments, right_channel_segments, rot_inv)
                            )
                            left_channel_segments, right_channel_segments = [], []

                        seg = raw_segs[0]
                        p1, p2 = (seg.coords[-1], seg.coords[0]) if reverse else (seg.coords[0], seg.coords[-1])
                        waypoints_final.append(rot_inv(*p1))
                        waypoints_final.append(rot_inv(*p2))
                        reverse = not reverse

                    # CAS 2 : La ligne rencontre un obstacle (Scission en sous-canaux)
                    else:
                        left_channel_segments.append((raw_segs[0], reverse))
                        right_channel_segments.append((raw_segs[-1], reverse))
                        reverse = not reverse

            y -= lane_spacing_m

        # Vider les canaux restants si l'obstacle s'étendait jusqu'au bout de la zone
        if left_channel_segments or right_channel_segments:
            waypoints_final.extend(
                self._resolve_channels(left_channel_segments, right_channel_segments, rot_inv)
            )

        return waypoints_final

    def _resolve_channels(self, left_chan, right_chan, rot_inv_func):
        """
        Génère les waypoints locaux pour le contournement en appliquant
        immédiatement la transformation géométrique inverse.
        """
        local_wps = []
        
        # 1. Parcourir le premier côté de l'obstacle (Canal Gauche)
        for seg, rev in left_chan:
            p1, p2 = (seg.coords[-1], seg.coords[0]) if rev else (seg.coords[0], seg.coords[-1])
            local_wps.append(rot_inv_func(*p1))
            local_wps.append(rot_inv_func(*p2))

        # 2. Transitionner et parcourir le second côté (Canal Droit) en sens inverse
        # pour éviter que le robot ne traverse l'obstacle par le milieu
        for seg, rev in reversed(right_chan):
            p1, p2 = (seg.coords[0], seg.coords[-1]) if rev else (seg.coords[-1], seg.coords[0])
            local_wps.append(rot_inv_func(*p1))
            local_wps.append(rot_inv_func(*p2))

        return local_wps

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