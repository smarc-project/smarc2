import rclpy
import math
import json
import threading
import heapq

from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from smarc_action_base.gentler_action_server import GentlerActionServer
from geographic_msgs.msg import GeoPoint
from tf2_geometry_msgs import do_transform_pose_stamped
from tf_transformations import euler_from_quaternion
from rclpy.time import Duration, Time
from nav_msgs.msg import Path, Odometry
from geometry_msgs.msg import TwistStamped, PoseStamped, Quaternion, Point, PointStamped
from tf2_ros import Buffer, TransformListener
from smarc_utilities import georef_utils
import tf_transformations
from evolo_msgs.msg import Topics as evoloTopics
from smarc_msgs.msg import Topics as smarcTopics
from dubins_planner.dubins import Waypoint, calc_dubins_path, dubins_traj
from std_msgs.msg import String

from smarc_msgs.msg import GeofencePolygonsStamped
from visualization_msgs.msg import Marker, MarkerArray

from shapely.geometry import Polygon, MultiPolygon, LineString, Point as SPoint
from shapely.ops import unary_union


# ─────────────────────────────────────────────────────────────────────────────
# Mission abort exception
# ─────────────────────────────────────────────────────────────────────────────
class MissionAbortError(Exception):
    pass


# ─────────────────────────────────────────────────────────────────────────────
# Pure Pursuit Controller
# ─────────────────────────────────────────────────────────────────────────────
class PurePursuitController:
    def __init__(self, Ld_base, Ld_min, omega_max, dubins_step, min_turning_radius):
        self.Ld_base     = Ld_base
        self.Ld_min      = Ld_min
        self.omega_max   = omega_max
        self.dubins_step = dubins_step
        arc_len = min_turning_radius * math.pi / 2
        self.lookahead_pts = max(3, int(arc_len / dubins_step))

    def _path_curvature_ahead(self, path, cursor):
        end = min(len(path), cursor + self.lookahead_pts)
        if end - cursor < 3:
            return 0.0

        yaws = [path[i][2] for i in range(cursor, end)]
        total_turn = sum(
            abs(math.atan2(math.sin(yaws[i+1] - yaws[i]),
                            math.cos(yaws[i+1] - yaws[i])))
            for i in range(len(yaws) - 1)
        )

        return min(1.0, total_turn / (math.pi / 2))

    def compute(self, robot_x, robot_y, robot_yaw, robot_v, path, cursor, dt):
        curvature_factor = self._path_curvature_ahead(path, cursor)
        Ld = self.Ld_base - curvature_factor * (self.Ld_base - self.Ld_min)

        lookahead_idx = len(path) - 1
        for i in range(cursor, len(path)):
            px, py, _ = path[i]
            if math.hypot(px - robot_x, py - robot_y) >= Ld:
                lookahead_idx = i
                break

        lx, ly, _ = path[lookahead_idx]
        return lx, ly, lookahead_idx

# ─────────────────────────────────────────────────────────────────────────────
# Action
# ─────────────────────────────────────────────────────────────────────────────
class EvoloMovePath:

    class WP:
        def __init__(self, p, tol, speed_kn):
            self.p        = p
            self.tol      = tol
            self.speed_kn = speed_kn

    def __init__(self, node: Node, action_name: str):
        self._node = node

        self._node.declare_parameters(namespace='', parameters=[
            ('speed_slow',         rclpy.Parameter.Type.DOUBLE),
            ('speed_standard',     rclpy.Parameter.Type.DOUBLE),
            ('speed_fast',         rclpy.Parameter.Type.DOUBLE),
            ('omega_max',          rclpy.Parameter.Type.DOUBLE),
            ('ld_base',            rclpy.Parameter.Type.DOUBLE),
            ('ld_min',            rclpy.Parameter.Type.DOUBLE),
            ('min_turning_radius', rclpy.Parameter.Type.DOUBLE),
            ('dubins_step',        rclpy.Parameter.Type.DOUBLE),
            ('timeout',            rclpy.Parameter.Type.DOUBLE),
            ('frame_id',           rclpy.Parameter.Type.STRING),
            ('dubins_mode',        rclpy.Parameter.Type.STRING),
            ('hard_buffer',        rclpy.Parameter.Type.DOUBLE),
            ('soft_buffer',        rclpy.Parameter.Type.DOUBLE),
        ])

        self.SPEED_SLOW         = self._node.get_parameter('speed_slow').value
        self.SPEED_STANDARD     = self._node.get_parameter('speed_standard').value
        self.SPEED_FAST         = self._node.get_parameter('speed_fast').value
        self.OMEGA_MAX          = math.radians(self._node.get_parameter('omega_max').value)
        self.MIN_TURNING_RADIUS = self._node.get_parameter('min_turning_radius').value
        self.DUBINS_STEP        = self._node.get_parameter('dubins_step').value
        self.DUBINS_MODE        = self._node.get_parameter('dubins_mode').value
        self.timeout            = self._node.get_parameter('timeout').value
        self.frame_id           = self._node.get_parameter('frame_id').value
        self.HARD_BUFFER        = self._node.get_parameter('hard_buffer').value
        self.SOFT_BUFFER        = self._node.get_parameter('soft_buffer').value

        self.controller = PurePursuitController(
            Ld_base     = self._node.get_parameter('ld_base').value,
            Ld_min      = self._node.get_parameter('ld_min').value,
            omega_max   = self.OMEGA_MAX,
            dubins_step = self.DUBINS_STEP,
            min_turning_radius = self.MIN_TURNING_RADIUS
        )

        self._as = GentlerActionServer(
            node, action_name,
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency=10,
        )

        self._tf_buffer   = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self._node,
                                              spin_thread=True)

        self.robot_position        = PoseStamped()
        self.robot_position_time   = None
        self.current_yaw           = None
        self.current_linear_speed  = 0.0
        self.current_angular_speed = 0.0

        self.target_list    = None
        self.speed_kn       = self.SPEED_STANDARD
        self.dubins_path    = None
        self.wp_end_indices = None
        self.path_cursor    = 0

        self._last_calculated_path  = None
        self._prev_omega            = 0.0
        self.action_started_time    = None
        self._precision_ticks_close = 0
        self._precision_ticks_total = 0
        self._distance_travelled    = 0.0
        self._last_robot_pos        = None

        # ── Geofence state ────────────────────────────────────────────────────
        self._islands_lock           = threading.Lock()
        self._island_polys_raw       = []
        self._hard_union             = None
        self._soft_union             = None
        self._shapely_hard_zones     = []
        self._shapely_soft_zones     = []
        self._allowed_zone           = None   
        self._allowed_zone_raw       = None   
        self._contours_hard          = []
        self._contours_soft          = []
        self._contours_allowed       = []     
        self._contours_allowed_raw   = []     
        self._contours_allowed_hard = []   
        self._contours_allowed_soft = []   
        self._geofence_received_time = None
        self._visibility_graph_data  = None

        pub_cbg = ReentrantCallbackGroup()
        sub_cbg = ReentrantCallbackGroup()

        self.dubins_path_pub = self._node.create_publisher(Path, 'rviz/planned_path', 10, callback_group=pub_cbg)
        self.speed_pub = self._node.create_publisher(Odometry, evoloTopics.EVOLO_CONTROL_PLANNED, 10, callback_group=pub_cbg)
        self.robot_sub    = self._node.create_subscription(Odometry, smarcTopics.ODOM_TOPIC, self.robot_odom_callback, 10, callback_group=sub_cbg)
        self.polygons_sub = self._node.create_subscription(GeofencePolygonsStamped, smarcTopics.GEOFENCE_POLYGONS_TOPIC, self._geofence_polygons_callback, 10, callback_group=sub_cbg)
        self.target_pub = self._node.create_publisher(PointStamped, evoloTopics.EVOLO_CURRENT_WP, 10, callback_group=self.publisher_callback_group)
        self._node.get_logger().info("EvoloMovePath started")


    # ─────────────────────────────────────────────────────────────────────────
    # Geofence callback
    # ─────────────────────────────────────────────────────────────────────────
    def _geofence_polygons_callback(self, msg: GeofencePolygonsStamped):
        if not msg.islands and not msg.geofence:
            return

        try:
            if not self._tf_buffer.can_transform(
                    self.frame_id, msg.header.frame_id, Time(seconds=0),
                    timeout=Duration(seconds=0, nanoseconds=100_000_000)):
                return
            tf = self._tf_buffer.lookup_transform(
                self.frame_id, msg.header.frame_id,
                Time(seconds=0), timeout=Duration(seconds=1))
        except Exception as e:
            self._node.get_logger().warn(f'[Geofence] TF: {e}')
            return

        from tf2_geometry_msgs import do_transform_point
        from geometry_msgs.msg import PointStamped

        def _tr(pt):
            ps = PointStamped()
            ps.header = msg.header
            ps.point.x, ps.point.y, ps.point.z = pt.x, pt.y, pt.z
            try:
                out = do_transform_point(ps, tf)
                return (out.point.x, out.point.y)
            except Exception:
                return None

        obstacle_polys = []
        allowed_polys  = []

        for polygon in msg.geofence:        # stay_inside=True
            pts = [_tr(p) for p in polygon.points]
            pts = [p for p in pts if p is not None]
            if len(pts) >= 3:
                allowed_polys.append(pts)

        for polygon in msg.islands:         # stay_inside=False
            pts = [_tr(p) for p in polygon.points]
            pts = [p for p in pts if p is not None]
            if len(pts) >= 3:
                obstacle_polys.append(pts)

        geofence_just_arrived = False

        with self._islands_lock:
            had_zones = self._hard_union is not None or self._allowed_zone is not None

            # ── Obstacles ─────────────────────────────────────────────────────
            if obstacle_polys:
                try:
                    raw_shapely      = [Polygon(p).buffer(0) for p in obstacle_polys]
                    self._hard_union = unary_union(
                        [p.buffer(self.HARD_BUFFER) for p in raw_shapely])
                    self._soft_union = unary_union(
                        [p.buffer(self.SOFT_BUFFER) for p in raw_shapely])
                    self._shapely_hard_zones = (
                        list(self._hard_union.geoms)
                        if self._hard_union.geom_type == 'MultiPolygon'
                        else [self._hard_union])
                    self._shapely_soft_zones = (
                        list(self._soft_union.geoms)
                        if self._soft_union.geom_type == 'MultiPolygon'
                        else [self._soft_union])
                    self._island_polys_raw = [
                        list(p.exterior.coords) for p in raw_shapely]
                    self._contours_hard = self._contour_simple(self._hard_union)
                    self._contours_soft = self._contour_simple(self._soft_union)
                    self._node.get_logger().info(
                        f'[Geofence] {len(obstacle_polys)} obstacle(s) loaded')
                except Exception as e:
                    self._node.get_logger().error(f'[Geofence] Obstacle: {e}')
            else:
                self._hard_union         = None
                self._soft_union         = None
                self._shapely_hard_zones = []
                self._shapely_soft_zones = []
                self._island_polys_raw   = []
                self._contours_hard      = []
                self._contours_soft      = []
                self._contours_allowed_soft = []   
                self._contours_allowed_hard = []   

            # ── Allowed zone ──────────────────────────────────────────────────
            if allowed_polys:
                try:
                    # Raw polygon — for visualization only
                    raw_allowed = unary_union(
                        [Polygon(p).buffer(0) for p in allowed_polys])
                    self._allowed_zone_raw     = raw_allowed
                    self._contours_allowed_raw = self._contour_simple(raw_allowed)

                    # Eroded zone — used for planning and collision checks
                    eroded = raw_allowed.buffer(-self.HARD_BUFFER)
                    if eroded.is_empty:
                        self._node.get_logger().error(
                            f'[Geofence] Allowed zone empty after erosion '
                            f'(buffer={self.HARD_BUFFER}m) — keeping raw zone')
                        self._allowed_zone = raw_allowed
                    else:
                        self._allowed_zone = eroded
                    # Soft erosion (inner soft boundary)
                    soft_eroded = raw_allowed.buffer(-self.SOFT_BUFFER)
                    if not soft_eroded.is_empty:
                        self._contours_allowed_soft = self._contour_simple(soft_eroded)
                    else:
                        self._contours_allowed_soft = []
                        self._contours_allowed_soft = []
                        self._contours_allowed_hard = []

                    # Hard erosion (inner hard boundary) — already computed as _allowed_zone
                    self._contours_allowed_hard = self._contour_simple(
                        eroded if not eroded.is_empty else raw_allowed
                    )

                    self._contours_allowed = self._contour_simple(self._allowed_zone)
                    self._node.get_logger().info(
                        f'[Geofence] allowed zone loaded | '
                        f'raw bounds={raw_allowed.bounds} | '
                        f'eroded bounds={self._allowed_zone.bounds}')
                except Exception as e:
                    self._node.get_logger().error(f'[Geofence] Allowed: {e}')
            else:
                self._allowed_zone         = None
                self._allowed_zone_raw     = None
                self._contours_allowed     = []
                self._contours_allowed_raw = []

            self._geofence_received_time = int(
                self._node.get_clock().now().nanoseconds * 1e-9)
            if not had_zones:
                geofence_just_arrived = True

        if geofence_just_arrived and self.dubins_path is not None:
            self._node.get_logger().warn(
                '[Geofence] Path planned without avoidance — invalidating')
            self.dubins_path    = None
            self.wp_end_indices = None
            self.path_cursor    = 0

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _contour_simple(union, tol=1.0):
        result = []
        polys  = list(union.geoms) if union.geom_type == 'MultiPolygon' else [union]
        for poly in polys:
            coords = list(
                poly.simplify(tol, preserve_topology=True).exterior.coords[:-1])
            result.append([(c[0], c[1]) for c in coords])
        return result

    # ─────────────────────────────────────────────────────────────────────────
    # Geometry checks
    # ─────────────────────────────────────────────────────────────────────────
    def _pt_in_hard(self, x, y):
        with self._islands_lock:
            zones = list(self._shapely_hard_zones)
        p = SPoint(x, y)
        return any(z.contains(p) for z in zones)

    def _seg_crosses_hard(self, ax, ay, bx, by):
        with self._islands_lock:
            zones = list(self._shapely_hard_zones)
        if not zones:
            return False
        seg = LineString([(ax, ay), (bx, by)])
        return any(z.intersects(seg) for z in zones)

    def _seg_crosses_soft(self, ax, ay, bx, by):
        with self._islands_lock:
            zones = list(self._shapely_soft_zones)
        if not zones:
            return False
        seg = LineString([(ax, ay), (bx, by)])
        return any(z.intersects(seg) for z in zones)

    def _seg_exits_allowed(self, ax, ay, bx, by):
        with self._islands_lock:
            z = self._allowed_zone
        if z is None:
            return False
        return not z.contains(LineString([(ax, ay), (bx, by)]))

    def _los_clear(self, ax, ay, bx, by):
        with self._islands_lock:
            hard_zones = list(self._shapely_hard_zones)
            allowed    = self._allowed_zone
        if self._pt_in_hard(ax, ay) or self._pt_in_hard(bx, by):
            return False
        seg = LineString([(ax, ay), (bx, by)])
        if any(z.intersects(seg) for z in hard_zones):
            return False
        if allowed is not None and not allowed.contains(seg):
            return False
        return True

    # ─────────────────────────────────────────────────────────────────────────
    # Dijkstra
    # ─────────────────────────────────────────────────────────────────────────
    def _dijkstra(self, graph, start_node, end_node):
        queue   = [(0.0, start_node, [start_node])]
        visited = set()
        while queue:
            cost, u, path = heapq.heappop(queue)
            if u in visited:
                continue
            visited.add(u)
            if u == end_node:
                return path
            for weight, v in graph.get(u, []):
                if v not in visited:
                    heapq.heappush(queue, (cost + weight, v, path + [v]))
        return None

    def _plan_bypass_dijkstra(self, start_xy, end_xy):
        with self._islands_lock:
            hard_zones    = list(self._shapely_hard_zones)
            soft_union    = self._soft_union
            contours_soft = list(self._contours_soft)
            allowed       = self._allowed_zone

        if not hard_zones and allowed is None:
            return [end_xy]

        def los(ax, ay, bx, by):
            p_a = SPoint(ax, ay)
            p_b = SPoint(bx, by)
            if any(z.contains(p_a) for z in hard_zones):
                return False
            if any(z.contains(p_b) for z in hard_zones):
                return False
            seg = LineString([(ax, ay), (bx, by)])
            if any(z.intersects(seg) for z in hard_zones):
                return False
            if allowed is not None and not allowed.contains(seg):
                return False
            return True

        candidate_pts = []

        # Vertices of soft contours (obstacles)
        for contour in contours_soft:
            valid = [
                (float(pt[0]), float(pt[1])) for pt in contour
                if not any(z.contains(SPoint(float(pt[0]), float(pt[1])))
                           for z in hard_zones)
            ]
            if not valid:
                continue
            step = max(1, len(valid) // 20)
            candidate_pts.extend(valid[::step])

        # Vertices along the inner edge of the allowed zone (already eroded),
        # with an additional small SOFT_BUFFER inset to avoid hugging the boundary
        if allowed is not None:
            eroded = allowed.buffer(-self.SOFT_BUFFER)
            if not eroded.is_empty:
                polys = (list(eroded.geoms)
                         if eroded.geom_type == 'MultiPolygon' else [eroded])
                for poly in polys:
                    coords = list(poly.exterior.coords)
                    step   = max(1, len(coords) // 20)
                    for pt in coords[::step]:
                        p = (float(pt[0]), float(pt[1]))
                        if not any(z.contains(SPoint(*p)) for z in hard_zones):
                            candidate_pts.append(p)

        # Sampled points along the direct line
        dx = end_xy[0] - start_xy[0]
        dy = end_xy[1] - start_xy[1]
        direct_dist = math.hypot(dx, dy)
        n_samples   = max(3, int(direct_dist / 20))
        for k in range(1, n_samples):
            t  = k / n_samples
            px = start_xy[0] + t * dx
            py = start_xy[1] + t * dy
            if not any(z.contains(SPoint(px, py)) for z in hard_zones):
                if allowed is None or allowed.contains(SPoint(px, py)):
                    candidate_pts.append((px, py))

        self._node.get_logger().info(
            f'[Dijkstra] {len(candidate_pts)} candidate nodes')

        all_nodes = [
            (float(start_xy[0]), float(start_xy[1])),
            (float(end_xy[0]),   float(end_xy[1])),
        ] + candidate_pts

        n     = len(all_nodes)
        graph = {i: [] for i in range(n)}

        for i in range(n):
            ax, ay = all_nodes[i]
            for j in range(i + 1, n):
                bx, by = all_nodes[j]
                if los(ax, ay, bx, by):
                    dist    = math.hypot(bx - ax, by - ay)
                    seg     = LineString([(ax, ay), (bx, by)])
                    penalty = 1.0
                    if soft_union is not None:
                        d_soft = seg.distance(soft_union)
                        if d_soft < self.HARD_BUFFER:
                            penalty += (self.HARD_BUFFER - d_soft) / self.HARD_BUFFER * 2.0
                    graph[i].append((dist * penalty, j))
                    graph[j].append((dist * penalty, i))

        route = self._dijkstra(graph, 0, 1)
        if not route or len(route) < 2:
            raise MissionAbortError(
                f'Dijkstra: no path found '
                f'({start_xy[0]:.1f},{start_xy[1]:.1f}) et '
                f'({end_xy[0]:.1f},{end_xy[1]:.1f})')

        self._node.get_logger().info(
            f'[Dijkstra] Path: {len(route)-1} length')
        return [all_nodes[nid] for nid in route[1:]]

    # ─────────────────────────────────────────────────────────────────────────
    # Path expansion
    # ─────────────────────────────────────────────────────────────────────────
    def _expand_positions(self, raw_positions):
        extended = [raw_positions[0]]
        for i in range(len(raw_positions) - 1):
            ax, ay = raw_positions[i]
            bx, by = raw_positions[i + 1]
            crosses_hard  = self._seg_crosses_hard(ax, ay, bx, by)
            exits_allowed = self._seg_exits_allowed(ax, ay, bx, by)
            if crosses_hard or exits_allowed:
                via = self._plan_bypass_dijkstra((ax, ay), (bx, by))
                extended.extend(via)
                self._node.get_logger().info(
                    f'  Segment {i}→{i+1}: Dijkstra {len(via)-1} via-point(s)')
            else:
                extended.append((bx, by))
        return extended

    # ─────────────────────────────────────────────────────────────────────────
    # Arc validation
    # ─────────────────────────────────────────────────────────────────────────
    def _validate_arc(self, arc, check_step=5):
        with self._islands_lock:
            hard_zones = list(self._shapely_hard_zones)
            allowed    = self._allowed_zone

        indices = list(range(0, len(arc), check_step))
        if indices and indices[-1] != len(arc) - 1:
            indices.append(len(arc) - 1)

        for i in indices:
            px, py = arc[i][0], arc[i][1]
            p = SPoint(px, py)
            if any(z.contains(p) for z in hard_zones):
                return False
            if allowed is not None and not allowed.contains(p):
                return False
        return True

    # ─────────────────────────────────────────────────────────────────────────
    # Dubins arc
    # ─────────────────────────────────────────────────────────────────────────
    def _build_arc(self, s1, s2, radius):
        w1     = Waypoint(s1[0], s1[1], math.degrees(s1[2]))
        w2     = Waypoint(s2[0], s2[1], math.degrees(s2[2]))
        params = calc_dubins_path(w1, w2, radius)

        if params:
            seg = dubins_traj(params, self.DUBINS_STEP)
            seg = [pt.tolist() if hasattr(pt, 'tolist') else list(pt) for pt in seg]
            if self._validate_arc(seg):
                return seg
            raise MissionAbortError(
                f'Arc Dubins ({s1[0]:.1f},{s1[1]:.1f})→({s2[0]:.1f},{s2[1]:.1f}) '
                f'not possible with geofence')

        raise MissionAbortError(
            f'No solution ({s1[0]:.1f},{s1[1]:.1f}) et '
            f'({s2[0]:.1f},{s2[1]:.1f})')

    # ─────────────────────────────────────────────────────────────────────────
    # Global Dubins planning
    # ─────────────────────────────────────────────────────────────────────────
    def _plan_global_dubins(self):
        if self.current_yaw is None:
            return False

        robot_pos     = self.robot_position.pose.position
        raw_positions = [(robot_pos.x, robot_pos.y)]
        for wp in self.target_list:
            raw_positions.append((wp.p.pose.position.x, wp.p.pose.position.y))

        self._node.get_logger().info(
            f'Planning | start=({robot_pos.x:.1f},{robot_pos.y:.1f},'
            f'{math.degrees(self.current_yaw):.0f}°) | '
            f'{len(self.target_list)} WP(s)')

        with self._islands_lock:
            has_geofence = (self._hard_union is not None
                            or self._allowed_zone is not None)

        if has_geofence:
            positions = self._expand_positions(raw_positions)
        else:
            self._node.get_logger().warn('Planning without avoidance (no geofence yet)')
            positions = raw_positions

        real_wp_pos_indices = set()
        raw_idx = 0
        pos_idx = 0
        while pos_idx < len(positions) and raw_idx < len(raw_positions):
            if (abs(positions[pos_idx][0] - raw_positions[raw_idx][0]) < 1e-3 and
                    abs(positions[pos_idx][1] - raw_positions[raw_idx][1]) < 1e-3):
                if raw_idx > 0:
                    real_wp_pos_indices.add(pos_idx)
                raw_idx += 1
                pos_idx += 1
            else:
                pos_idx += 1

        n_via = len(positions) - len(raw_positions)
        if n_via:
            self._node.get_logger().info(f'  {n_via} via-point(s) inserted')

        n      = len(positions)
        R      = self.MIN_TURNING_RADIUS
        states = [(positions[0][0], positions[0][1], self.current_yaw)]
        real_wp_state_idx = []

        for i in range(1, n):
            curr       = positions[i]
            prev       = positions[i - 1]
            is_real_wp = i in real_wp_pos_indices
            is_last    = (i == n - 1)

            if self.DUBINS_MODE == 'vwp' and is_real_wp and not is_last:
                h_in  = math.atan2(curr[1] - prev[1], curr[0] - prev[0])
                vwp   = (curr[0] + R * math.cos(h_in),
                         curr[1] + R * math.sin(h_in))
                nxt      = positions[i + 1]
                h_next   = math.atan2(nxt[1] - curr[1], nxt[0] - curr[0])
                next_vwp = (nxt[0] + R * math.cos(h_next),
                            nxt[1] + R * math.sin(h_next))
                h_exit   = math.atan2(next_vwp[1] - curr[1],
                                      next_vwp[0] - curr[0])
                states.append((vwp[0],  vwp[1],  h_in))
                states.append((curr[0], curr[1], h_exit))
            else:
                h = (math.atan2(positions[i+1][1] - prev[1],
                                positions[i+1][0] - prev[0])
                     if not is_last
                     else math.atan2(curr[1] - prev[1], curr[0] - prev[0]))
                states.append((curr[0], curr[1], h))

            real_wp_state_idx.append(len(states) - 1)

        full_path, wp_ends = [], []
        for i in range(len(states) - 1):
            seg = self._build_arc(states[i], states[i + 1], R)
            full_path.extend(seg if i == 0 else seg[1:])
            if (i + 1) in real_wp_state_idx:
                wp_ends.append(len(full_path) - 1)

        self.dubins_path_pub.publish(self._path_msg(full_path))
        self.dubins_path           = full_path

        self.wp_end_indices        = wp_ends
        self.path_cursor           = 0
        self._last_calculated_path = full_path

        with self._islands_lock:
            self._visibility_graph_data = {
                'island_contours_soft':     list(self._contours_soft),
                'island_contours_hard':     list(self._contours_hard),
                'island_contours_allowed':  list(self._contours_allowed),
                'allowed_contours_raw':     list(self._contours_allowed_raw),
                'allowed_contours_soft':    list(self._contours_allowed_soft),
                'allowed_contours_hard':    list(self._contours_allowed_hard),
            }

        self._node.get_logger().info(
            f'✓ Dubins path: {len(full_path)} pts | '
            f'{len(wp_ends)} WP end(s) | {n_via} via-pt(s)')

        return True

    # ─────────────────────────────────────────────────────────────────────────
    # Action callbacks
    # ─────────────────────────────────────────────────────────────────────────
    def _on_goal_received(self, goal_request):
        raw_speed = goal_request.get('speed', 'standard')
        if isinstance(raw_speed, (int, float)):
            self.speed_kn = float(raw_speed)
        elif raw_speed == 'slow':
            self.speed_kn = self.SPEED_SLOW
        elif raw_speed == 'fast':
            self.speed_kn = self.SPEED_FAST
        else:
            self.speed_kn = self.SPEED_STANDARD

        waypoints = goal_request.get('waypoints', [])
        if not waypoints:
            return False

        self.target_list    = []
        self.target_list_latlon = []
        self.dubins_path    = None
        self.wp_end_indices = None

        for wp_params in waypoints:
            lat  = float(wp_params['latitude'])
            lon  = float(wp_params['longitude'])
            alt  = float(wp_params.get('altitude', 0.0))
            tol  = float(wp_params['tolerance'])
            pose = self.latlon_to_local_frame([lat, lon])
            if pose is None:
                self._node.get_logger().error(
                    f'[GoalReceived] TF failed for ({lat:.6f},{lon:.6f}) — skipping')
                continue
            self.target_list.append(self.WP(p=pose, tol=tol, speed_kn=self.speed_kn))
            self.target_list_latlon.append({'latitude': lat, 'longitude': lon, 'altitude': alt})
            self._node.get_logger().info(
                f'[GoalReceived] WP{len(self.target_list)}: '
                f'({pose.pose.position.x:.1f}, {pose.pose.position.y:.1f}) queued')

        if not self.target_list:
            self._node.get_logger().error(
                '[GoalReceived] No valid waypoints — goal rejected')
            return False

        self._node.get_logger().info(
            f'[GoalReceived] {len(self.target_list)} waypoint(s) queued — '
            'filtering deferred to prepare_loop')
        return True

    def _on_cancel_received(self):
        self._send_stop()
        return True

    def _prepare_loop(self):
        self.action_started_time    = int(self._node.get_clock().now().nanoseconds * 1e-9)
        self.dubins_path            = None
        self.wp_end_indices         = None
        self.path_cursor            = 0
        self._precision_ticks_close = 0
        self._precision_ticks_total = 0
        self._distance_travelled    = 0.0
        self._last_robot_pos        = None
        self._prev_omega            = 0.0
        self._waypoints_filtered    = False

    def _filter_waypoints(self):
        with self._islands_lock:
            allowed   = self._allowed_zone
            hard_zone = self._hard_union

        if allowed is None and hard_zone is None:
            self._node.get_logger().warn(
                '[Filter] No geofence yet — all waypoints kept')
            self._waypoints_for_client = [
                {'x': wp.p.pose.position.x, 'y': wp.p.pose.position.y, 'tol': wp.tol}
                for wp in self.target_list
            ]
            return

        if allowed is not None:
            self._node.get_logger().info(
                f'[Filter] allowed_zone bounds={allowed.bounds}')

        filtered        = []
        filtered_latlon = []   

        for i, wp in enumerate(self.target_list):
            wp_pt = SPoint(wp.p.pose.position.x, wp.p.pose.position.y)

            if allowed is not None and not allowed.contains(wp_pt):
                raise MissionAbortError(
                    f'WP ({wp.p.pose.position.x:.1f}, {wp.p.pose.position.y:.1f}) '
                    f'outside stay_inside')

            if hard_zone is not None and hard_zone.contains(wp_pt):
                raise MissionAbortError(
                    f'WP ({wp.p.pose.position.x:.1f}, {wp.p.pose.position.y:.1f}) '
                    f' inside obstacle')

            filtered.append(wp)
            filtered_latlon.append(self.target_list_latlon[i])   # ← sync
            self._node.get_logger().info(
                f'[Filter] WP ({wp.p.pose.position.x:.1f}, '
                f'{wp.p.pose.position.y:.1f}) accepted')

        self._node.get_logger().info(
            f'[Filter] {len(filtered)}/{len(self.target_list)} waypoint(s) kept')

        self.target_list        = filtered
        self.target_list_latlon = filtered_latlon   

        self._waypoints_for_client = [
            {'x': wp.p.pose.position.x, 'y': wp.p.pose.position.y, 'tol': wp.tol}
            for wp in self.target_list
        ]


    def _loop_inner(self):
        time_now = int(self._node.get_clock().now().nanoseconds * 1e-9)
        if time_now - self.action_started_time > self.timeout:
            self._send_stop()
            return False

        if self.robot_position_time is None or self.current_yaw is None:
            return None

        if self.dubins_path is None:
            try:
                with self._islands_lock:
                    has_geofence = (self._hard_union is not None
                                    or self._allowed_zone is not None)

                if not has_geofence:
                    self._node.get_logger().warn(
                        'No geofence yet — planning without avoidance')
                else:
                    if not getattr(self, '_waypoints_filtered', False):
                        self._filter_waypoints()
                        self._waypoints_filtered = True
                        if not self.target_list:
                            raise MissionAbortError(
                                'No point after filter')

                if not self._plan_global_dubins():
                    return None

            except MissionAbortError as e:
                self._node.get_logger().error(f'[MissionAbort] {e}')
                self._send_stop()
                return False

        robot_pos = self.robot_position.pose.position

        if self._last_robot_pos is not None:
            self._distance_travelled += math.hypot(
                robot_pos.x - self._last_robot_pos[0],
                robot_pos.y - self._last_robot_pos[1])
        self._last_robot_pos = (robot_pos.x, robot_pos.y)

        path = self.dubins_path

        WINDOW     = 40
        search_end = min(len(path), self.path_cursor + WINDOW)
        candidate  = self._find_closest(robot_pos, self.path_cursor, search_end)
        self.path_cursor = max(self.path_cursor, candidate)
        self.path_cursor = min(self.path_cursor, len(path) - 1)

        # ── Point courant ───────
        if self.wp_end_indices is not None:
            try:
                wp_current_idx = len(self.wp_end_indices) - 1
                for i, end_idx in enumerate(self.wp_end_indices):
                    if self.path_cursor <= end_idx:
                        wp_current_idx = i
                        break

                latlon = self.target_list_latlon[wp_current_idx]
                pt_msg = PointStamped()
                pt_msg.header.stamp    = self._node.get_clock().now().to_msg()
                pt_msg.header.frame_id = self.frame_id
                pt_msg.point.x = latlon['longitude']
                pt_msg.point.y = latlon['latitude']
                pt_msg.point.z = latlon.get('altitude', 0.0)
                self.target_pub.publish(pt_msg)
            except Exception:
                pass

        dist_to_goal = math.hypot(robot_pos.x - path[-1][0], robot_pos.y - path[-1][1])
        tolerance = 5
        if self.path_cursor >= len(path) - 1 and dist_to_goal < tolerance:
            self._node.get_logger().info('End of Dubins path reached')
            self._send_stop()
            return True

        cx, cy, cyaw = path[self.path_cursor]
        dist_to_curve = abs(
            math.cos(cyaw) * (robot_pos.y - cy) -
            math.sin(cyaw) * (robot_pos.x - cx))
        self._precision_ticks_total += 1
        if dist_to_curve < 1.0:
            self._precision_ticks_close += 1



        v = self.speed_kn

        lx, ly, _ = self.controller.compute(
            robot_x   = float(robot_pos.x),
            robot_y   = float(robot_pos.y),
            robot_yaw = float(self.current_yaw),
            robot_v   = float(self.current_linear_speed) if self.current_linear_speed > 0.5 else v,
            path      = path,
            cursor    = self.path_cursor,
            dt        = 0.1,
        )

        commanded_yaw = math.atan2(ly - robot_pos.y, lx - robot_pos.x)
        q = tf_transformations.quaternion_from_euler(0, 0, commanded_yaw)

        yaw_diff = math.atan2(math.sin(commanded_yaw - self.current_yaw),
                               math.cos(commanded_yaw - self.current_yaw))

        cmd                         = Odometry()
        cmd.header.stamp            = self._node.get_clock().now().to_msg()
        cmd.header.frame_id         = self.frame_id
        cmd.child_frame_id          = "evolo/base_link"
        cmd.pose.pose.orientation.x = q[0]
        cmd.pose.pose.orientation.y = q[1]
        cmd.pose.pose.orientation.z = q[2]
        cmd.pose.pose.orientation.w = q[3]
        cmd.twist.twist.linear.x    = v
        cmd.twist.twist.angular.z   = yaw_diff  #
        self.speed_pub.publish(cmd)

        return None

    # ─────────────────────────────────────────────────────────────────────────
    def _find_closest(self, robot_pos, start, end):
        path       = self.dubins_path
        yaw        = self.current_yaw or 0.0
        best_idx   = start
        best_score = float('inf')
        for i in range(start, end):
            x, y, curve_yaw = path[i]
            dist         = math.hypot(x - robot_pos.x, y - robot_pos.y)
            heading_diff = math.atan2(math.sin(curve_yaw - yaw),
                                      math.cos(curve_yaw - yaw))
            score = dist + 4.0 * (1.0 - math.cos(heading_diff))
            if score < best_score:
                best_score = score
                best_idx   = i
        return best_idx

    def _send_stop(self):
        cmd = Odometry()
        cmd.header.stamp    = self._node.get_clock().now().to_msg()
        cmd.header.frame_id = self.frame_id
        cmd.child_frame_id  = "evolo/base_link"
        cmd.pose.pose.orientation.w = 1.0  
        cmd.twist.twist.linear.x  = 0.0
        cmd.twist.twist.angular.z = 0.0
        self.speed_pub.publish(cmd)

    def _smooth_path_bezier_safe(self, path, n_out=None):
        """Smoothing via CubicSpline with geofence revalidation."""
        if len(path) < 4:
            return path

        try:
            from scipy.interpolate import CubicSpline
        except ImportError:
            self._node.get_logger().warn('[Smooth] scipy not available — skipping')
            return path

        n_out = n_out or len(path)

        xs    = [p[0] for p in path]
        ys    = [p[1] for p in path]
        t_in  = [i / (len(path) - 1) for i in range(len(path))]
        t_out = [i / (n_out - 1)     for i in range(n_out)]

        try:
            cs_x    = CubicSpline(t_in, xs, bc_type='natural')
            cs_y    = CubicSpline(t_in, ys, bc_type='natural')
            xs_out  = cs_x(t_out)
            ys_out  = cs_y(t_out)
        except Exception as e:
            self._node.get_logger().warn(f'[Smooth] CubicSpline failed: {e} — keeping original')
            return path

        smoothed = []
        for i in range(n_out):
            if i < n_out - 1:
                yaw = math.atan2(ys_out[i+1] - ys_out[i],
                                xs_out[i+1] - xs_out[i])
            else:
                yaw = smoothed[-1][2] if smoothed else path[-1][2]
            smoothed.append([float(xs_out[i]), float(ys_out[i]), yaw])

        with self._islands_lock:
            hard_zones = list(self._shapely_hard_zones)
            allowed    = self._allowed_zone

        for pt in smoothed:
            p = SPoint(pt[0], pt[1])
            if any(z.contains(p) for z in hard_zones):
                self._node.get_logger().warn(
                    '[Smooth] Spline enters obstacle — keeping original')
                return path
            if allowed is not None and not allowed.contains(p):
                self._node.get_logger().warn(
                    '[Smooth] Spline exits allowed zone — keeping original')
                return path

        self._node.get_logger().info(
            f'[Smooth] Spline smoothed: {len(path)} → {len(smoothed)} pts')
        return smoothed

    def _path_msg(self, configurations):
        msg = Path()
        msg.header.frame_id = self.frame_id
        msg.header.stamp    = self._node.get_clock().now().to_msg()
        for x, y, yaw in configurations:
            ps = PoseStamped()
            ps.header = msg.header
            ps.pose.position.x = x
            ps.pose.position.y = y
            q = tf_transformations.quaternion_from_euler(0, 0, yaw)
            ps.pose.orientation.x = q[0]
            ps.pose.orientation.y = q[1]
            ps.pose.orientation.z = q[2]
            ps.pose.orientation.w = q[3]
            msg.poses.append(ps)
        return msg

    def _give_feedback(self):
        time_now = int(self._node.get_clock().now().nanoseconds * 1e-9)
        runtime  = time_now - self.action_started_time
        pct = (round(100.0 * self._precision_ticks_close / self._precision_ticks_total, 2)
            if self._precision_ticks_total > 0 else 0.0)
        self._node.get_logger().info(
            f'precision={pct}% | dist={self._distance_travelled:.1f}m'
            f' | cursor={self.path_cursor}/'
            f'{len(self.dubins_path) if self.dubins_path else "?"}')

        # ── Progress computation ──────────────────────────────────────────────
        total_progress_pct = 0.0
        wp_progress_pct    = 0.0
        wp_current_idx     = 0

        if self.dubins_path and self.wp_end_indices:
            path_len = len(self.dubins_path)
            cursor   = self.path_cursor

            total_progress_pct = round(100.0 * cursor / max(path_len - 1, 1), 2)

            wp_start_idx = 0
            wp_end_idx   = self.wp_end_indices[0]

            for i, end_idx in enumerate(self.wp_end_indices):
                if cursor <= end_idx:
                    wp_current_idx = i
                    wp_start_idx   = self.wp_end_indices[i - 1] + 1 if i > 0 else 0
                    wp_end_idx     = end_idx
                    break
            else:
                wp_current_idx = len(self.wp_end_indices) - 1
                wp_start_idx   = self.wp_end_indices[-2] + 1 if len(self.wp_end_indices) > 1 else 0
                wp_end_idx     = self.wp_end_indices[-1]

            seg_len = max(wp_end_idx - wp_start_idx, 1)
            wp_progress_pct = round(
                100.0 * (cursor - wp_start_idx) / seg_len, 2
            )
            wp_progress_pct = max(0.0, min(100.0, wp_progress_pct))

        fb = {
            'runtime':            runtime,
            'precision_pct':      pct,
            'precision_close':    self._precision_ticks_close,
            'precision_total':    self._precision_ticks_total,
            'distance_travelled': round(self._distance_travelled, 2),
            'total_progress_pct': total_progress_pct,
            'wp_progress_pct':    wp_progress_pct,
            'wp_current_idx':     wp_current_idx,
        }

        if hasattr(self, '_waypoints_for_client') and self._waypoints_for_client:
            fb['wps'] = self._waypoints_for_client
            self._waypoints_for_client = None
        if self._visibility_graph_data is not None:
            fb['visibility_graph'] = self._visibility_graph_data
            self._visibility_graph_data = None

        return json.dumps(fb)

    # ─────────────────────────────────────────────────────────────────────────
    def latlon_to_local_frame(self, point_list):
        geopoint           = GeoPoint()
        geopoint.latitude  = point_list[0]
        geopoint.longitude = point_list[1]
        geopoint.altitude  = 0.0
        utm_pt = georef_utils.convert_latlon_to_utm(geopoint)
        ps = PoseStamped()
        ps.header        = utm_pt.header
        ps.pose.position = utm_pt.point
        yaw = math.radians(point_list[2]) if len(point_list) > 2 else 0.0
        q   = tf_transformations.quaternion_from_euler(0, 0, yaw)
        ps.pose.orientation = Quaternion(x=q[0], y=q[1], z=q[2], w=q[3])
        try:
            t = self._tf_buffer.lookup_transform(
                target_frame=self.frame_id,
                source_frame=ps.header.frame_id,
                time=Time(seconds=0),
                timeout=Duration(seconds=1))
            return do_transform_pose_stamped(ps, t)
        except Exception as e:
            self._node.get_logger().error(f'TF failed: {e}')
            return None

    def robot_odom_callback(self, msg: Odometry):
        if msg.header.frame_id == self.frame_id:
            self.robot_position        = PoseStamped()
            self.robot_position.header = msg.header
            self.robot_position.pose   = msg.pose.pose
        else:
            raw = PoseStamped()
            raw.header = msg.header
            raw.pose   = msg.pose.pose
            try:
                t = self._tf_buffer.lookup_transform(
                    target_frame=self.frame_id,
                    source_frame=msg.header.frame_id,
                    time=Time(seconds=0),
                    timeout=Duration(seconds=1))
                self.robot_position = do_transform_pose_stamped(raw, t)
            except Exception as e:
                self._node.get_logger().error(f'Odom TF failed: {e}')
                return

        self.robot_position_time   = int(self._node.get_clock().now().nanoseconds * 1e-9)
        oq = self.robot_position.pose.orientation
        (_, _, self.current_yaw)   = euler_from_quaternion([oq.x, oq.y, oq.z, oq.w])
        self.current_linear_speed  = msg.twist.twist.linear.x
        self.current_angular_speed = msg.twist.twist.angular.z


# ─────────────────────────────────────────────────────────────────────────────
def main():
    rclpy.init()
    node = Node('evolo_move_path_action_server')
    EvoloMovePath(node, 'move_path')
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down')
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()