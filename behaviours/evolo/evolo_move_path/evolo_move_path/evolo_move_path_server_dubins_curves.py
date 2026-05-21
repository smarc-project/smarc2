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
from geometry_msgs.msg import TwistStamped, PoseStamped, Quaternion, Point
from tf2_ros import Buffer, TransformListener
from smarc_utilities import georef_utils
import tf_transformations
from evolo_msgs.msg import Topics as evoloTopics
from smarc_msgs.msg import Topics as SmarcTopics
from dubins_planner.dubins import Waypoint, calc_dubins_path, dubins_traj

from smarc_msgs.msg import GeofencePolygonsStamped
from visualization_msgs.msg import Marker, MarkerArray

from shapely.geometry import Polygon, MultiPolygon, LineString, Point as SPoint
from shapely.ops import unary_union


# ─────────────────────────────────────────────────────────────────────────────
# Pure Pursuit Controller
# ─────────────────────────────────────────────────────────────────────────────
class PurePursuitController:
    def __init__(self, Ld_base, Ld_gain, omega_max, dubins_step,
                 cte_kp=0.0, cte_ki=0.0, cte_integral_max=10.0, heading_kp=0.0):
        self.Ld_base          = Ld_base
        self.Ld_gain          = Ld_gain
        self.omega_max        = omega_max
        self.dubins_step      = dubins_step
        self.cte_kp           = cte_kp
        self.cte_ki           = cte_ki
        self.cte_integral_max = cte_integral_max
        self.heading_kp       = heading_kp
        self._cte_integral    = 0.0

    def reset(self):
        self._cte_integral = 0.0

    def compute(self, robot_x, robot_y, robot_yaw, robot_v, path, cursor, dt):
        Ld = self.Ld_base + self.Ld_gain * robot_v

        lookahead_idx = len(path) - 1
        for i in range(cursor, len(path)):
            px, py, _ = path[i]
            if math.hypot(px - robot_x, py - robot_y) >= Ld:
                lookahead_idx = i
                break

        lx, ly, _ = path[lookahead_idx]
        angle_to_target = math.atan2(ly - robot_y, lx - robot_x)
        alpha = math.atan2(
            math.sin(angle_to_target - robot_yaw),
            math.cos(angle_to_target - robot_yaw),
        )
        dist_to_target = math.hypot(lx - robot_x, ly - robot_y)
        kappa = 0.0 if dist_to_target < 0.1 else 2.0 * math.sin(alpha) / dist_to_target

        omega_pp = robot_v * kappa

        x1, y1, _ = path[cursor]
        x2, y2, _ = path[min(cursor + 1, len(path) - 1)]
        dx, dy    = x2 - x1, y2 - y1
        seg_len   = math.hypot(dx, dy)
        cross_error = 0.0
        if seg_len > 1e-3:
            t = ((robot_x - x1) * dx + (robot_y - y1) * dy) / seg_len ** 2
            t = max(0.0, min(1.0, t))
            foot_x = x1 + t * dx
            foot_y = y1 + t * dy
            nx = -dy / seg_len
            ny =  dx / seg_len
            cross_error = (robot_x - foot_x) * nx + (robot_y - foot_y) * ny

        self._cte_integral = max(
            -self.cte_integral_max,
            min(self.cte_integral_max, self._cte_integral + cross_error * dt)
        )
        omega_cte_deg = -(self.cte_kp * cross_error + self.cte_ki * self._cte_integral)

        _, _, path_yaw = path[cursor]
        heading_error = math.atan2(math.sin(path_yaw - robot_yaw),
                                   math.cos(path_yaw - robot_yaw))
        omega_heading_deg = self.heading_kp * heading_error

        omega_deg = math.degrees(omega_pp) + omega_cte_deg + omega_heading_deg
        omega_deg = max(-self.omega_max, min(self.omega_max, omega_deg))

        return omega_deg, lookahead_idx


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
            ('v_min',              rclpy.Parameter.Type.DOUBLE),
            ('v_max',              rclpy.Parameter.Type.DOUBLE),
            ('omega_max',          rclpy.Parameter.Type.DOUBLE),
            ('ld_base',            rclpy.Parameter.Type.DOUBLE),
            ('ld_gain',            rclpy.Parameter.Type.DOUBLE),
            ('min_turning_radius', rclpy.Parameter.Type.DOUBLE),
            ('dubins_step',        rclpy.Parameter.Type.DOUBLE),
            ('timeout',            rclpy.Parameter.Type.DOUBLE),
            ('frame_id',           rclpy.Parameter.Type.STRING),
            ('cte_kp',             rclpy.Parameter.Type.DOUBLE),
            ('cte_ki',             rclpy.Parameter.Type.DOUBLE),
            ('cte_integral_max',   rclpy.Parameter.Type.DOUBLE),
            ('heading_kp',         rclpy.Parameter.Type.DOUBLE),
            ('dubins_mode',        rclpy.Parameter.Type.STRING),
            ('hard_buffer',        rclpy.Parameter.Type.DOUBLE),
            ('soft_buffer',        rclpy.Parameter.Type.DOUBLE),
            ('geofence_timeout',   rclpy.Parameter.Type.DOUBLE),
            ('speed_slow',         rclpy.Parameter.Type.DOUBLE),
            ('speed_standard',     rclpy.Parameter.Type.DOUBLE),
            ('speed_high',         rclpy.Parameter.Type.DOUBLE),
        ])

        self.V_MIN              = self._node.get_parameter('v_min').value
        self.V_MAX              = self._node.get_parameter('v_max').value
        self.OMEGA_MAX          = self._node.get_parameter('omega_max').value
        self.MIN_TURNING_RADIUS = self._node.get_parameter('min_turning_radius').value
        self.DUBINS_STEP        = self._node.get_parameter('dubins_step').value
        self.DUBINS_MODE        = self._node.get_parameter('dubins_mode').value
        self.timeout            = self._node.get_parameter('timeout').value
        self.frame_id           = self._node.get_parameter('frame_id').value
        self.HARD_BUFFER        = self._node.get_parameter('hard_buffer').value
        self.SOFT_BUFFER        = self._node.get_parameter('soft_buffer').value
        self.GEOFENCE_TIMEOUT   = self._node.get_parameter('geofence_timeout').value
        self.SPEED_SLOW         = self._node.get_parameter('speed_slow').value
        self.SPEED_STANDARD     = self._node.get_parameter('speed_standard').value
        self.SPEED_HIGH         = self._node.get_parameter('speed_high').value

        self.controller = PurePursuitController(
            Ld_base          = self._node.get_parameter('ld_base').value,
            Ld_gain          = self._node.get_parameter('ld_gain').value,
            omega_max        = self.OMEGA_MAX,
            dubins_step      = self.DUBINS_STEP,
            cte_kp           = self._node.get_parameter('cte_kp').value,
            cte_ki           = self._node.get_parameter('cte_ki').value,
            cte_integral_max = self._node.get_parameter('cte_integral_max').value,
            heading_kp       = self._node.get_parameter('heading_kp').value,
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
        self.speed_kn       = 10.0
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

        self._islands_lock           = threading.Lock()
        self._shapely_hard_zones     = None
        self._shapely_soft_zones     = None
        # Unions fusionnées — un seul polygone Shapely pour les checks rapides
        self._hard_union_single      = None
        self._soft_union_single      = None
        self._contours_hard          = []
        self._contours_soft          = []
        self._geofence_received_time = None

        self._visibility_graph_data = None

        pub_cbg = ReentrantCallbackGroup()
        sub_cbg = ReentrantCallbackGroup()

        self.dubins_path_pub = self._node.create_publisher(Path, 'rviz/planned_path', 10, callback_group=pub_cbg)
        # self.speed_pub = self._node.create_publisher(TwistStamped, 'evolo/evolo_cmd', 10, callback_group=pub_cbg)
        self.viz_island_pub = self._node.create_publisher(MarkerArray, 'rviz/island_contours', 10, callback_group=pub_cbg)

        self.robot_sub = self._node.create_subscription(Odometry, SmarcTopics.ODOM_TOPIC, self.robot_odom_callback, 10, callback_group=sub_cbg)     
        self.speed_pub = self._node.create_publisher(TwistStamped, evoloTopics.EVOLO_TWIST_PLANNED,    10, callback_group=pub_cbg)

        # self.robot_sub = self._node.create_subscription(Odometry, 'evolo/smarc/odom', self.robot_odom_callback, 10, callback_group=sub_cbg)
        # self.polygons_sub = self._node.create_subscription(GeofencePolygonsStamped, '/smarc/geofence_polygons', self._geofence_polygons_callback, 10, callback_group=sub_cbg)
        self.polygons_sub = self._node.create_subscription(GeofencePolygonsStamped, SmarcTopics.GEOFENCE_POLYGONS_TOPIC, self._geofence_polygons_callback, 10, callback_group=sub_cbg)
        
        self._node.create_timer(2.0, self._publish_island_visuals)
        self._node.get_logger().info('EvoloMovePath started')

    # ─────────────────────────────────────────────────────────────────────────
    # Geofence callback
    # ─────────────────────────────────────────────────────────────────────────
    def _geofence_polygons_callback(self, msg: GeofencePolygonsStamped):
        if not msg.islands:
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

        islands_local = []
        for polygon in msg.islands:
            pts = [_tr(p) for p in polygon.points]
            pts = [p for p in pts if p is not None]
            if len(pts) >= 3:
                islands_local.append(pts)

        if not islands_local:
            self._node.get_logger().warn('[Geofence] No valid polygons after TF')
            return

        try:
            raw_union  = unary_union([Polygon(isl).buffer(0) for isl in islands_local])
            hard_union = raw_union.buffer(self.HARD_BUFFER)
            soft_union = raw_union.buffer(self.SOFT_BUFFER)
        except Exception as e:
            self._node.get_logger().error(f'[Geofence] Shapely buffer: {e}')
            return

        def _zones(union):
            return list(union.geoms) if union.geom_type == 'MultiPolygon' else [union]

        def _contours(union, tol=1.0):
            result = []
            for poly in _zones(union):
                coords = list(
                    poly.simplify(tol, preserve_topology=True).exterior.coords[:-1])
                result.append([(c[0], c[1]) for c in coords])
            return result

        geofence_just_arrived = False
        with self._islands_lock:
            had_zones                    = self._shapely_hard_zones is not None
            self._shapely_hard_zones     = _zones(hard_union)
            self._shapely_soft_zones     = _zones(soft_union)
            # Unions fusionnées précalculées — évite de boucler sur les zones à chaque check
            self._hard_union_single      = hard_union
            self._soft_union_single      = soft_union
            self._contours_hard          = _contours(hard_union)
            self._contours_soft          = _contours(soft_union)
            self._geofence_received_time = int(
                self._node.get_clock().now().nanoseconds * 1e-9)
            if not had_zones:
                geofence_just_arrived = True

        self._node.get_logger().info(
            f'[Geofence] {len(islands_local)} island(s) | '
            f'hard={self.HARD_BUFFER}m ({len(self._shapely_hard_zones)} poly) | '
            f'soft={self.SOFT_BUFFER}m ({len(self._shapely_soft_zones)} poly)'
        )

        if geofence_just_arrived and self.dubins_path is not None:
            self._node.get_logger().warn(
                '[Geofence] Path planned without avoidance — invalidating')
            self.dubins_path    = None
            self.wp_end_indices = None
            self.path_cursor    = 0
            self.controller.reset()

    # ─────────────────────────────────────────────────────────────────────────
    # Shapely helpers — toujours sur l'union fusionnée (plus rapide)
    # ─────────────────────────────────────────────────────────────────────────
    def _point_in_hard(self, x, y):
        with self._islands_lock:
            u = self._hard_union_single
        return u is not None and u.contains(SPoint(x, y))

    def _point_in_soft(self, x, y):
        with self._islands_lock:
            u = self._soft_union_single
        return u is not None and u.contains(SPoint(x, y))

    def _line_of_sight_hard(self, ax, ay, bx, by):
        """True quand le segment ne pénètre pas la HARD zone."""
        with self._islands_lock:
            u = self._hard_union_single
        if u is None:
            return True
        seg = LineString([(ax, ay), (bx, by)])
        return not u.intersects(seg)

    def _segment_collides_soft(self, ax, ay, bx, by):
        """True quand le segment touche la SOFT zone (déclencheur bypass)."""
        with self._islands_lock:
            u = self._soft_union_single
        if u is None:
            return False
        seg = LineString([(ax, ay), (bx, by)])
        return u.intersects(seg)

    # ─────────────────────────────────────────────────────────────────────────
    # RViz visualisation
    # ─────────────────────────────────────────────────────────────────────────
    def _publish_island_visuals(self):
        with self._islands_lock:
            contours_soft = list(self._contours_soft)
            contours_hard = list(self._contours_hard)
        if not contours_soft and not contours_hard:
            return

        ma    = MarkerArray()
        stamp = self._node.get_clock().now().to_msg()
        mid   = 0

        def _add(contour, ns_dots, ns_line, r, g, b, dot_sz, line_sz):
            nonlocal mid
            if len(contour) < 2:
                return
            pts = [Point(x=float(c[0]), y=float(c[1]), z=0.0) for c in contour]
            sphere = Marker()
            sphere.header.frame_id = self.frame_id
            sphere.header.stamp    = stamp
            sphere.ns, sphere.id   = ns_dots, mid;  mid += 1
            sphere.type            = Marker.SPHERE_LIST
            sphere.action          = Marker.ADD
            sphere.scale.x = sphere.scale.y = sphere.scale.z = dot_sz
            sphere.color.r, sphere.color.g, sphere.color.b, sphere.color.a = r, g, b, 1.0
            sphere.points = pts
            ma.markers.append(sphere)
            line = Marker()
            line.header.frame_id = self.frame_id
            line.header.stamp    = stamp
            line.ns, line.id     = ns_line, mid;  mid += 1
            line.type            = Marker.LINE_STRIP
            line.action          = Marker.ADD
            line.scale.x         = line_sz
            line.color.r, line.color.g, line.color.b, line.color.a = r, g, b, 0.85
            line.points = pts + [pts[0]]
            ma.markers.append(line)

        for c in contours_soft:
            _add(c, 'soft_dots', 'soft_lines', 1.0, 1.0, 1.0, 0.8, 0.25)
        for c in contours_hard:
            _add(c, 'hard_dots', 'hard_lines', 1.0, 0.5, 0.0, 0.6, 0.30)
        self.viz_island_pub.publish(ma)

    # ─────────────────────────────────────────────────────────────────────────
    # Dijkstra
    # ─────────────────────────────────────────────────────────────────────────
    def _dijkstra(self, graph, start, end):
        queue   = [(0.0, start, [start])]
        visited = set()
        while queue:
            cost, u, path = heapq.heappop(queue)
            if u in visited:
                continue
            visited.add(u)
            if u == end:
                return path
            for w, v in graph.get(u, []):
                if v not in visited:
                    heapq.heappush(queue, (cost + w, v, path + [v]))
        return None

    def _project_outside_soft(self, xy, soft_zones):
        p = SPoint(xy[0], xy[1])
        for zone in soft_zones:
            if zone.contains(p):
                nearest = zone.exterior.interpolate(zone.exterior.project(p))
                cx, cy = zone.centroid.x, zone.centroid.y
                dx, dy = nearest.x - cx, nearest.y - cy
                d = math.hypot(dx, dy) or 1.0
                return (nearest.x + (dx / d) * 0.5,
                        nearest.y + (dy / d) * 0.5)
        return xy

    # ─────────────────────────────────────────────────────────────────────────
    # Bypass Dijkstra — graphe de visibilité optimisé
    # ─────────────────────────────────────────────────────────────────────────
    def _bypass_segment(self, start_xy, end_xy):
        """
        Graphe de visibilité Dijkstra sur les vertices du contour soft.
        Arêtes vérifiées contre la HARD zone uniquement.
        Filtrage spatial : ne considère que les nœuds proches du segment.
        Retourne une liste de (x,y) se terminant par end_xy.
        """
        with self._islands_lock:
            hard_union = self._hard_union_single
            soft_zones = list(self._shapely_soft_zones) if self._shapely_soft_zones else []

        if not soft_zones:
            return [end_xy]

        safe_start = self._project_outside_soft(start_xy, soft_zones)
        safe_end   = self._project_outside_soft(end_xy,   soft_zones)

        # ── Candidats : vertices du contour soft poussés vers l'extérieur ────
        push_dist        = 1.0
        edge_subdivisions = 3
        candidate_pts    = []

        for zone in soft_zones:
            cx, cy   = zone.centroid.x, zone.centroid.y
            coords   = list(
                zone.simplify(0.5, preserve_topology=True).exterior.coords[:-1])
            n_coords = len(coords)

            for idx in range(n_coords):
                vx0, vy0 = coords[idx]
                vx1, vy1 = coords[(idx + 1) % n_coords]

                for k in range(edge_subdivisions + 1):
                    t  = k / edge_subdivisions
                    vx = vx0 + t * (vx1 - vx0)
                    vy = vy0 + t * (vy1 - vy0)
                    ddx, ddy = vx - cx, vy - cy
                    d = math.hypot(ddx, ddy)
                    if d < 1e-6:
                        continue
                    nx_u, ny_u = ddx / d, ddy / d
                    px = vx + nx_u * push_dist
                    py = vy + ny_u * push_dist
                    if hard_union is None or not hard_union.contains(SPoint(px, py)):
                        candidate_pts.append((px, py))

        all_nodes = [(float(safe_start[0]), float(safe_start[1])),
                     (float(safe_end[0]),   float(safe_end[1]))] + candidate_pts

        # ── Filtrage spatial : ne garder que les nœuds proches du segment ────
        sx, sy    = safe_start
        ex, ey    = safe_end
        seg_len   = math.hypot(ex - sx, ey - sy)
        margin    = max(self.SOFT_BUFFER * 2.0, seg_len * 0.3)
        mid_x     = (sx + ex) / 2
        mid_y     = (sy + ey) / 2
        half_diag = seg_len / 2 + margin

        filtered = [0, 1]   # start et end toujours inclus
        for i, (nx_c, ny_c) in enumerate(all_nodes[2:], 2):
            if math.hypot(nx_c - mid_x, ny_c - mid_y) <= half_diag:
                filtered.append(i)

        self._node.get_logger().info(
            f'  Dijkstra: {len(filtered) - 2}/{len(all_nodes) - 2} candidates '
            f'(spatial filter margin={margin:.1f}m)')

        # ── Construction du graphe sur les nœuds filtrés uniquement ──────────
        graph = {i: [] for i in filtered}
        for ii, i in enumerate(filtered):
            ax, ay = all_nodes[i]
            for j in filtered[ii + 1:]:
                bx, by = all_nodes[j]
                seg = LineString([(ax, ay), (bx, by)])
                if hard_union is None or not hard_union.intersects(seg):
                    dist = math.hypot(bx - ax, by - ay)
                    graph[i].append((dist, j))
                    graph[j].append((dist, i))

        route = self._dijkstra(graph, 0, 1)
        if not route or len(route) < 2:
            self._node.get_logger().warn('  Dijkstra: no path found')
            return [end_xy]

        self._node.get_logger().info(
            f'  Dijkstra: route has {len(route) - 1} segment(s)')

        result = []
        for k, node_id in enumerate(route[1:], 1):
            is_last = (k == len(route) - 1)
            result.append(end_xy if is_last else all_nodes[node_id])
        return result

    # ─────────────────────────────────────────────────────────────────────────
    # Segment-level avoidance
    # ─────────────────────────────────────────────────────────────────────────
    def _extend_positions_for_avoidance(self, positions):
        with self._islands_lock:
            has_zones = self._soft_union_single is not None
        if not has_zones:
            self._node.get_logger().warn(
                'Avoidance: no geofence data — planning without avoidance')
            return positions

        extended = [positions[0]]
        for i in range(len(positions) - 1):
            ax, ay = positions[i]
            bx, by = positions[i + 1]
            if self._segment_collides_soft(ax, ay, bx, by):
                self._node.get_logger().warn(
                    f'  Segment {i}→{i+1} crosses soft buffer '
                    f'({ax:.1f},{ay:.1f})→({bx:.1f},{by:.1f}) — running Dijkstra')
                bypass = self._bypass_segment((ax, ay), (bx, by))
                extended.extend(bypass)
            else:
                extended.append((bx, by))
        return extended

    # ─────────────────────────────────────────────────────────────────────────
    # Arc validation — lock pris une seule fois, pas dans la boucle
    # ─────────────────────────────────────────────────────────────────────────
    def _validate_dubins_arc(self, arc, check_step=5):
        """True si aucun point échantillonné de l'arc n'est dans la HARD zone."""
        with self._islands_lock:
            u = self._hard_union_single
        if u is None:
            return True
        indices = list(range(0, len(arc), check_step))
        if indices[-1] != len(arc) - 1:
            indices.append(len(arc) - 1)
        for i in indices:
            if u.contains(SPoint(arc[i][0], arc[i][1])):
                return False
        return True

    # ─────────────────────────────────────────────────────────────────────────
    # Arc Dubins direct — sans récursion (utilisé par contour walk)
    # ─────────────────────────────────────────────────────────────────────────
    def _build_arc_direct(self, s1, s2, radius):
        """
        Arc Dubins sans aucun fallback récursif.
        Retourne une ligne droite uniquement si le Dubins échoue complètement.
        Jamais appelé avec depth — ne peut pas boucler.
        """
        w1     = Waypoint(s1[0], s1[1], math.degrees(s1[2]))
        w2     = Waypoint(s2[0], s2[1], math.degrees(s2[2]))
        params = calc_dubins_path(w1, w2, radius)
        if params:
            seg = dubins_traj(params, self.DUBINS_STEP)
            seg = [pt.tolist() if hasattr(pt, 'tolist') else list(pt) for pt in seg]
            if self._validate_dubins_arc(seg):
                return seg
        # Ligne droite uniquement ici — jamais depuis _build_arc principal
        n = max(2, int(math.hypot(s2[0] - s1[0], s2[1] - s1[1]) / self.DUBINS_STEP))
        return [
            [s1[0] + k / (n - 1) * (s2[0] - s1[0]),
             s1[1] + k / (n - 1) * (s2[1] - s1[1]),
             math.atan2(s2[1] - s1[1], s2[0] - s1[0])]
            for k in range(n)
        ]

    # ─────────────────────────────────────────────────────────────────────────
    # Contour walk — dernier recours avant ligne droite forcée
    # ─────────────────────────────────────────────────────────────────────────
    def _contour_walk_fallback(self, s1, s2, radius):
        """
        Identifie la zone soft bloquant s1→s2.
        Marche le contour dans les deux sens (CW et CCW) depuis le vertex
        le plus proche de s1, jusqu'à trouver une ligne de vue vers s2.
        Chaîne ensuite des arcs Dubins smooth via _build_arc_direct.
        Retourne la liste de points ou None si aucune direction ne fonctionne.
        """
        with self._islands_lock:
            soft_zones = list(self._shapely_soft_zones) if self._shapely_soft_zones else []
            hard_union = self._hard_union_single

        if not soft_zones:
            return None

        # Trouver la zone qui bloque le segment s1→s2
        seg_line     = LineString([(s1[0], s1[1]), (s2[0], s2[1])])
        blocking_zone = None
        for zone in soft_zones:
            if zone.intersects(seg_line) or zone.contains(SPoint(s1[0], s1[1])):
                blocking_zone = zone
                break
        if blocking_zone is None:
            blocking_zone = min(soft_zones, key=lambda z: z.distance(seg_line))

        # Vertices du contour poussés vers l'extérieur
        push_dist = 1.0
        cx, cy    = blocking_zone.centroid.x, blocking_zone.centroid.y
        coords    = list(
            blocking_zone.simplify(0.5, preserve_topology=True).exterior.coords[:-1])

        vertices = []
        for vx, vy in coords:
            ddx, ddy = vx - cx, vy - cy
            d = math.hypot(ddx, ddy)
            if d < 1e-6:
                continue
            px = vx + (ddx / d) * push_dist
            py = vy + (ddy / d) * push_dist
            if hard_union is None or not hard_union.contains(SPoint(px, py)):
                vertices.append((px, py))

        if not vertices:
            self._node.get_logger().warn(
                '  Contour walk: no valid vertices on blocking zone')
            return None

        n = len(vertices)

        # Vertex le plus proche de s1
        start_idx = min(range(n),
            key=lambda i: math.hypot(vertices[i][0] - s1[0],
                                     vertices[i][1] - s1[1]))

        # Marcher dans les deux sens jusqu'à avoir LoS vers s2
        def walk(direction):
            pts = []
            for step in range(1, n + 1):
                idx  = (start_idx + direction * step) % n
                vx, vy = vertices[idx]
                pts.append((vx, vy))
                seg = LineString([(vx, vy), (s2[0], s2[1])])
                if hard_union is None or not hard_union.intersects(seg):
                    return pts
            return None

        cw  = walk(+1)
        ccw = walk(-1)

        if cw is None and ccw is None:
            self._node.get_logger().warn(
                "  Contour walk: aucune direction n'atteint la LoS vers s2")
            return None

        if cw is None:
            chosen = ccw
        elif ccw is None:
            chosen = cw
        else:
            chosen = cw if len(cw) <= len(ccw) else ccw

        self._node.get_logger().info(
            f'  Contour walk: {len(chosen)} vertex(es) pour atteindre la LoS')

        # Construire les états Dubins : s1 → vertices → s2
        all_states = [s1]
        prev_xy    = (s1[0], s1[1])
        for wx, wy in chosen:
            h = math.atan2(wy - prev_xy[1], wx - prev_xy[0])
            all_states.append((wx, wy, h))
            prev_xy = (wx, wy)
        all_states.append(s2)   # heading original de s2 conservé

        # Chaîner les arcs Dubins smooth sans récursion
        result = []
        for i in range(len(all_states) - 1):
            seg = self._build_arc_direct(all_states[i], all_states[i + 1], radius)
            result.extend(seg if i == 0 else seg[1:])
        return result

    # ─────────────────────────────────────────────────────────────────────────
    # Arc principal avec fallback en cascade
    # ─────────────────────────────────────────────────────────────────────────
    def _build_arc(self, s1, s2, radius, depth=0):
        """
        Construit un arc Dubins de s1=(x,y,yaw_rad) vers s2.

        Cascade :
          depth 0 → arc OK ?  retourne
                 → KO        → Dijkstra midpoint (depth 1)
          depth 1 → arc OK ?  retourne
                 → KO        → Dijkstra midpoint (depth 2)
          depth 2 → arc OK ?  retourne
                 → KO        → contour walk (arcs Dubins sur vertices contour)
                              → si contour walk échoue : ligne droite forcée (ERROR)
        """
        w1     = Waypoint(s1[0], s1[1], math.degrees(s1[2]))
        w2     = Waypoint(s2[0], s2[1], math.degrees(s2[2]))
        params = calc_dubins_path(w1, w2, radius)

        if params:
            seg = dubins_traj(params, self.DUBINS_STEP)
            seg = [pt.tolist() if hasattr(pt, 'tolist') else list(pt) for pt in seg]
            if self._validate_dubins_arc(seg):
                return seg  # ✓ arc propre

        # ── Fallback Dijkstra (jusqu'à depth < 3) ────────────────────────────
        if depth < 3:
            self._node.get_logger().warn(
                f'  Arc ({s1[0]:.1f},{s1[1]:.1f})→({s2[0]:.1f},{s2[1]:.1f}): '
                f'hard collision at R={radius:.1f} — '
                f'inserting bypass midpoint (depth={depth})')
            bypass = self._bypass_segment((s1[0], s1[1]), (s2[0], s2[1]))

            if len(bypass) > 1:
                mid_xy   = bypass[0]
                h_to_mid = math.atan2(mid_xy[1] - s1[1], mid_xy[0] - s1[0])
                s_mid    = (mid_xy[0], mid_xy[1], h_to_mid)

                seg_a = self._build_arc(s1,    s_mid, radius, depth=depth + 1)
                seg_b = self._build_arc(s_mid, s2,    radius, depth=depth + 1)
                return seg_a + seg_b[1:]

        # ── Last resort : contour walk smooth ────────────────────────────────
        self._node.get_logger().warn(
            f'  Arc ({s1[0]:.1f},{s1[1]:.1f})→({s2[0]:.1f},{s2[1]:.1f}): '
            f'Dijkstra exhausted — contour walk fallback')
        result = self._contour_walk_fallback(s1, s2, radius)
        if result:
            return result

        # Absolument dernier recours — ne devrait jamais arriver
        self._node.get_logger().error(
            f'  Arc ({s1[0]:.1f},{s1[1]:.1f})→({s2[0]:.1f},{s2[1]:.1f}): '
            f'contour walk failed — forced straight line')
        n_interp = max(2, int(
            math.hypot(s2[0] - s1[0], s2[1] - s1[1]) / self.DUBINS_STEP))
        return [
            [s1[0] + k / (n_interp - 1) * (s2[0] - s1[0]),
             s1[1] + k / (n_interp - 1) * (s2[1] - s1[1]),
             math.atan2(s2[1] - s1[1], s2[0] - s1[0])]
            for k in range(n_interp)
        ]

    # ─────────────────────────────────────────────────────────────────────────
    # Goal / Cancel / Prepare
    # ─────────────────────────────────────────────────────────────────────────
    def _on_goal_received(self, goal_request):
        try:
            self.speed_kn = float(goal_request['speed'])
        except (ValueError, TypeError):
            self.speed_kn = 10.0

        waypoints = goal_request.get('waypoints', [])
        if not waypoints:
            return False

        self.target_list    = []
        self.dubins_path    = None
        self.wp_end_indices = None

        for wp_params in waypoints:
            lat  = float(wp_params['latitude'])
            lon  = float(wp_params['longitude'])
            tol  = float(wp_params['tolerance'])
            pose = self.latlon_to_local_frame([lat, lon])
            if pose is None:
                return False
            self.target_list.append(self.WP(p=pose, tol=tol, speed_kn=self.speed_kn))
            self._node.get_logger().info(
                f'  WP{len(self.target_list)}: '
                f'({pose.pose.position.x:.1f}, {pose.pose.position.y:.1f})')

        self._waypoints_for_client = [
            {'x': wp.p.pose.position.x, 'y': wp.p.pose.position.y, 'tol': wp.tol}
            for wp in self.target_list
        ]
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
        self.controller.reset()

    # ─────────────────────────────────────────────────────────────────────────
    # Main control loop
    # ─────────────────────────────────────────────────────────────────────────
    def _loop_inner(self):
        time_now = int(self._node.get_clock().now().nanoseconds * 1e-9)
        if time_now - self.action_started_time > self.timeout:
            self._send_stop()
            return False

        if self.robot_position_time is None or self.current_yaw is None:
            return None

        if self.dubins_path is None:
            with self._islands_lock:
                has_geofence = self._soft_union_single is not None

            if not has_geofence:
                elapsed = time_now - self.action_started_time
                if elapsed < self.GEOFENCE_TIMEOUT:
                    if int(elapsed) % 2 == 0:
                        self._node.get_logger().info(
                            f'Waiting for geofence… ({elapsed:.1f}s / '
                            f'{self.GEOFENCE_TIMEOUT}s timeout)')
                    return None
                else:
                    self._node.get_logger().warn(
                        f'Geofence timeout ({self.GEOFENCE_TIMEOUT}s) — '
                        'planning without avoidance')

            if not self._plan_global_dubins():
                return None

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

        if self.path_cursor >= len(path) - 1:
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

        v = max(self.V_MIN, min(self.V_MAX, self.speed_kn))

        omega, _ = self.controller.compute(
            robot_x   = float(robot_pos.x),
            robot_y   = float(robot_pos.y),
            robot_yaw = float(self.current_yaw),
            robot_v   = float(self.current_linear_speed) if self.current_linear_speed > 0.5 else v,
            path      = path,
            cursor    = self.path_cursor,
            dt        = 0.1,
        )

        MAX_DELTA      = 4.0
        omega_smoothed = (self._prev_omega
                          + max(-MAX_DELTA, min(MAX_DELTA, omega - self._prev_omega)))
        self._prev_omega = omega_smoothed

        cmd                 = TwistStamped()
        cmd.header.stamp    = self._node.get_clock().now().to_msg()
        cmd.header.frame_id = self.frame_id
        cmd.twist.linear.x  = v
        cmd.twist.angular.z = omega_smoothed
        self.speed_pub.publish(cmd)

        return None

    # ─────────────────────────────────────────────────────────────────────────
    # Global Dubins planner
    # ─────────────────────────────────────────────────────────────────────────
    def _plan_global_dubins(self):
        if self.current_yaw is None:
            return False

        robot_pos = self.robot_position.pose.position

        # Step 1: positions brutes
        raw_positions = [(robot_pos.x, robot_pos.y)]
        for wp in self.target_list:
            raw_positions.append(
                (wp.p.pose.position.x, wp.p.pose.position.y))

        self._node.get_logger().info(
            f'Planning | start=({robot_pos.x:.1f},{robot_pos.y:.1f},'
            f'{math.degrees(self.current_yaw):.0f}°) | '
            f'{len(self.target_list)} WP(s)')


        # Step 2: insertion des bypass waypoints Dijkstra
        # On mémorise quels indices dans `positions` sont des WP réels
        with self._islands_lock:
            has_geofence = self._soft_union_single is not None

        if has_geofence:
            positions = self._extend_positions_for_avoidance(raw_positions)
        else:
            self._node.get_logger().warn('Planning without avoidance (geofence timeout)')
            positions = raw_positions

        # Indices dans `positions` qui correspondent à un vrai WP utilisateur
        # raw_positions[0] = robot, raw_positions[1..] = WPs réels
        # _extend_positions_for_avoidance conserve les points originaux en dernier
        # de chaque segment, donc on les retrouve en reconstruisant le mapping
        real_wp_positions = set()
        raw_idx = 0
        pos_idx = 0
        while pos_idx < len(positions) and raw_idx < len(raw_positions):
            if (abs(positions[pos_idx][0] - raw_positions[raw_idx][0]) < 1e-3 and
                    abs(positions[pos_idx][1] - raw_positions[raw_idx][1]) < 1e-3):
                if raw_idx > 0:  # ne pas marquer le robot lui-même
                    real_wp_positions.add(pos_idx)
                raw_idx  += 1
                pos_idx  += 1
            else:
                pos_idx += 1   # bypass waypoint, on saute

        n_bypass = len(positions) - len(raw_positions)
        if n_bypass:
            self._node.get_logger().info(
                f'  Avoidance: {n_bypass} bypass waypoint(s) inserted')

        # Step 3: construction des états Dubins depuis les positions
        n      = len(positions)
        R      = self.MIN_TURNING_RADIUS
        states = [(positions[0][0], positions[0][1], self.current_yaw)]
        real_wp_state_indices = []

        for i in range(1, n):
            curr       = positions[i]
            prev       = positions[i - 1]
            is_real_wp = i in real_wp_positions
            is_last    = (i == n - 1)

            if self.DUBINS_MODE == 'vwp' and is_real_wp and not is_last:
                # VWP uniquement sur les vrais waypoints intermédiaires
                h_in = math.atan2(curr[1] - prev[1], curr[0] - prev[0])
                vwp  = (curr[0] + R * math.cos(h_in),
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
                # Bypass waypoints et dernier WP : cap interpolé simple
                h = (math.atan2(positions[i + 1][1] - prev[1],
                                positions[i + 1][0] - prev[0])
                    if not is_last
                    else math.atan2(curr[1] - prev[1], curr[0] - prev[0]))
                states.append((curr[0], curr[1], h))

            real_wp_state_indices.append(len(states) - 1)





        # Step 4: chaîner les arcs avec _build_arc (cascade de fallbacks)
        full_path, wp_ends = [], []

        for i in range(len(states) - 1):
            seg = self._build_arc(states[i], states[i + 1], R)
            full_path.extend(seg if i == 0 else seg[1:])
            if (i + 1) in real_wp_state_indices:
                wp_ends.append(len(full_path) - 1)

        # Step 5: publication et stockage
        self.dubins_path_pub.publish(self._path_msg(full_path))
        self.dubins_path           = full_path
        self.wp_end_indices        = wp_ends
        self.path_cursor           = 0
        self._last_calculated_path = full_path

        with self._islands_lock:
            self._visibility_graph_data = {
                'island_contours_soft': list(self._contours_soft),
                'island_contours_hard': list(self._contours_hard),
            }

        self._node.get_logger().info(
            f'✓ Dubins path: {len(full_path)} pts | '
            f'{len(wp_ends)} WP end(s) | '
            f'{n_bypass} bypass pt(s)')
        return True

    # ─────────────────────────────────────────────────────────────────────────
    # Cursor helper
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

    # ─────────────────────────────────────────────────────────────────────────
    # Utilities
    # ─────────────────────────────────────────────────────────────────────────
    def _send_stop(self):
        cmd = TwistStamped()
        cmd.header.stamp    = self._node.get_clock().now().to_msg()
        cmd.twist.linear.x  = 0.0
        cmd.twist.angular.z = 0.0
        self.speed_pub.publish(cmd)

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
        fb = {
            'runtime':            runtime,
            'precision_pct':      pct,
            'precision_close':    self._precision_ticks_close,
            'precision_total':    self._precision_ticks_total,
            'distance_travelled': round(self._distance_travelled, 2),
        }
        if self._last_calculated_path is not None:
            fb['full_path'] = self._last_calculated_path
            self._last_calculated_path = None
        if hasattr(self, '_waypoints_for_client') and self._waypoints_for_client:
            fb['wps'] = self._waypoints_for_client
            self._waypoints_for_client = None
        if self._visibility_graph_data is not None:
            fb['visibility_graph'] = self._visibility_graph_data
            self._visibility_graph_data = None
        return json.dumps(fb)

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