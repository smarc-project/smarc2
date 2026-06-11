import rclpy
import math
import json

from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from smarc_action_base.gentler_action_server import GentlerActionServer
from geographic_msgs.msg import GeoPoint
from tf2_geometry_msgs import do_transform_pose_stamped
from tf_transformations import euler_from_quaternion
from rclpy.time import Duration, Time
from nav_msgs.msg import Path, Odometry
from geometry_msgs.msg import PoseStamped, Quaternion
from tf2_ros import Buffer, TransformListener
from smarc_utilities import georef_utils
import tf_transformations
from std_msgs.msg import String

from evolo_msgs.msg import Topics as evoloTopics
from smarc_msgs.msg import Topics as smarcTopics

from dubins_planner.dubins import Waypoint, calc_dubins_path, dubins_traj

from smarc_msgs.msg import GeofencePolygonsStamped



# ─────────────────────────────────────────────────────────────────────────────
class PurePursuitController:

    def __init__(self, Ld_base, omega_max, dubins_step,
                 cte_kp=0.0, cte_ki=0.0, cte_integral_max=10.0, heading_kp=0.0):
        self.Ld_base          = Ld_base
        self.omega_max        = omega_max
        self.dubins_step      = dubins_step
        self.cte_kp           = cte_kp
        self.cte_ki           = cte_ki
        self.cte_integral_max = cte_integral_max
        self.heading_kp       = heading_kp
        self._cte_integral    = 0.0

    # ─────────────────────────────────────────────────────────────────────────────
    def reset(self):
        self._cte_integral = 0.0

    # ─────────────────────────────────────────────────────────────────────────────
    def compute(self, robot_x, robot_y, robot_yaw, robot_v, path, cursor, dt):

        lookahead_idx = len(path) - 1
        for i in range(cursor, len(path)):
            px, py, _ = path[i]
            if math.hypot(px - robot_x, py - robot_y) >= self.Ld_base:
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
            ('min_turning_radius', rclpy.Parameter.Type.DOUBLE),
            ('dubins_step',        rclpy.Parameter.Type.DOUBLE),
            ('timeout',            rclpy.Parameter.Type.DOUBLE),
            ('frame_id',           rclpy.Parameter.Type.STRING),
            ('cte_kp',             rclpy.Parameter.Type.DOUBLE),
            ('cte_ki',             rclpy.Parameter.Type.DOUBLE),
            ('cte_integral_max',   rclpy.Parameter.Type.DOUBLE),
            ('heading_kp',         rclpy.Parameter.Type.DOUBLE),
            ('dubins_mode',        rclpy.Parameter.Type.STRING),
        ])

        self.SPEED_SLOW          = self._node.get_parameter('speed_slow').value
        self.SPEED_STANDARD      = self._node.get_parameter('speed_standard').value
        self.SPEED_FAST          = self._node.get_parameter('speed_fast').value
        self.OMEGA_MAX           = self._node.get_parameter('omega_max').value
        self.MIN_TURNING_RADIUS  = self._node.get_parameter('min_turning_radius').value
        self.DUBINS_STEP         = self._node.get_parameter('dubins_step').value
        self.DUBINS_MODE         = self._node.get_parameter('dubins_mode').value
        self.timeout             = self._node.get_parameter('timeout').value
        self.frame_id            = self._node.get_parameter('frame_id').value

        self.controller = PurePursuitController(
            Ld_base          = self._node.get_parameter('ld_base').value,
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
        self._tf_listener = TransformListener(self._tf_buffer, self._node, spin_thread=True)

        self.robot_position        = PoseStamped()
        self.robot_position_time   = None
        self.current_yaw           = None
        self.current_linear_speed  = 0.0
        self.current_angular_speed = 0.0

        self.target_list           = None
        self.speed_kn              = 10.0

        self.dubins_path           = None
        self.wp_end_indices        = None
        self.path_cursor           = 0

        self._last_calculated_path = None
        self._prev_omega           = 0.0
        self.action_started_time   = None

        self._precision_ticks_close = 0
        self._precision_ticks_total = 0
        self._distance_travelled    = 0.0
        self._last_robot_pos        = None

        pub_cbg = ReentrantCallbackGroup()
        sub_cbg = ReentrantCallbackGroup()

        self.dubins_path_pub = self._node.create_publisher(Path, "rviz/planned_path", 10, callback_group=pub_cbg)
        self.robot_sub = self._node.create_subscription(Odometry, smarcTopics.ODOM_TOPIC, self.robot_odom_callback, 10, callback_group=sub_cbg)
        self.speed_pub = self._node.create_publisher(Odometry, evoloTopics.EVOLO_CONTROL_SETPOINT, 10, callback_group=pub_cbg)
        self.polygons_sub = self._node.create_subscription(GeofencePolygonsStamped, smarcTopics.GEOFENCE_POLYGONS_TOPIC, self._geofence_polygons_callback, 10, callback_group=sub_cbg)

        self._waraps_feedback_pub = self._node.create_publisher(String, 'waraps/current_waypoint', 10, callback_group=pub_cbg)

        self._node.get_logger().info("EvoloMovePath started")

    # ─────────────────────────────────────────────────────────────────────────
    def _publish_waraps_feedback(self, payload: dict) -> None:
        try:
            msg = String()
            msg.data = json.dumps(payload)
            self._waraps_feedback_pub.publish(msg)
        except Exception as e:
            self._node.get_logger().error(f"[WARAPS] Error : {e}")

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

        geofence_just_arrived = False
        if geofence_just_arrived and self.dubins_path is not None:
            self._node.get_logger().warn('[Geofence] Path planned without avoidance — invalidating')
            self.dubins_path    = None
            self.wp_end_indices = None
            self.path_cursor    = 0
            self.controller.reset()

    # ─────────────────────────────────────────────────────────────────────────
    def _on_goal_received(self, goal_request: dict) -> bool:
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

        self.target_list        = []
        self.target_list_latlon = []
        self.dubins_path        = None
        self.wp_end_indices     = None

        for wp_params in waypoints:
            lat  = float(wp_params['latitude'])
            lon  = float(wp_params['longitude'])
            tol  = float(wp_params['tolerance'])
            pose = self.latlon_to_local_frame([lat, lon])
            if pose is None:
                return False
            self.target_list.append(self.WP(p=pose, tol=tol, speed_kn=self.speed_kn))
            self.target_list_latlon.append({'latitude': lat, 'longitude': lon})
            self._node.get_logger().info(
                f"  WP{len(self.target_list)}: "
                f"({pose.pose.position.x:.1f}, {pose.pose.position.y:.1f})"
            )

        self._waypoints_for_client = [
            {'x': wp.p.pose.position.x, 'y': wp.p.pose.position.y, 'tol': wp.tol}
            for wp in self.target_list
        ]
        return True

    # ─────────────────────────────────────────────────────────────────────────
    def _on_cancel_received(self) -> bool:
        self._send_stop()
        return True

    # ─────────────────────────────────────────────────────────────────────────
    def _prepare_loop(self) -> None:
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
    def _loop_inner(self) -> bool | None:
        time_now = int(self._node.get_clock().now().nanoseconds * 1e-9)
        if time_now - self.action_started_time > self.timeout:
            self._send_stop()
            return False

        if self.robot_position_time is None or self.current_yaw is None:
            return None

        robot_pos = self.robot_position.pose.position

        # distance
        if self._last_robot_pos is not None:
            self._distance_travelled += math.hypot(
                robot_pos.x - self._last_robot_pos[0],
                robot_pos.y - self._last_robot_pos[1],
            )
        self._last_robot_pos = (robot_pos.x, robot_pos.y)

        if self.dubins_path is None:
            if not self._plan_global_dubins():
                return None

        path = self.dubins_path

        WINDOW     = 40
        search_end = min(len(path), self.path_cursor + WINDOW)
        candidate  = self._find_closest(robot_pos, self.path_cursor, search_end)
        self.path_cursor = max(self.path_cursor, candidate)
        self.path_cursor = min(self.path_cursor, len(path) - 1)

        # WARAPS
        if self.wp_end_indices is not None:
            try:
                wp_current_idx = len(self.wp_end_indices) - 1
                for i, end_idx in enumerate(self.wp_end_indices):
                    if self.path_cursor <= end_idx:
                        wp_current_idx = i
                        break
                latlon = self.target_list_latlon[wp_current_idx]
                self._publish_waraps_feedback({
                    'index':     wp_current_idx,
                    'latitude':  latlon['latitude'],
                    'longitude': latlon['longitude'],
                })
            except Exception:
                pass

        # end 
        if self.path_cursor >= len(path) - 1:
            self._node.get_logger().info("End of Dubins path reached")
            self._send_stop()
            return True

        cx, cy, cyaw = path[self.path_cursor]
        dx = robot_pos.x - cx
        dy = robot_pos.y - cy
        dist_to_curve = abs(math.cos(cyaw) * dy - math.sin(cyaw) * dx)
        self._precision_ticks_total += 1
        if dist_to_curve < 1.0:
            self._precision_ticks_close += 1

        # speed
        v = self.speed_kn

        # control
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
        omega_smoothed = self._prev_omega + max(-MAX_DELTA, min(MAX_DELTA, omega - self._prev_omega))
        self._prev_omega = omega_smoothed

        commanded_yaw = self.current_yaw + math.radians(omega_smoothed)
        q = tf_transformations.quaternion_from_euler(0, 0, commanded_yaw)

        cmd                         = Odometry()
        cmd.header.stamp            = self._node.get_clock().now().to_msg()
        cmd.header.frame_id         = self.frame_id
        cmd.child_frame_id          = "evolo/base_link"
        cmd.pose.pose.orientation.x = q[0]
        cmd.pose.pose.orientation.y = q[1]
        cmd.pose.pose.orientation.z = q[2]
        cmd.pose.pose.orientation.w = q[3]
        cmd.twist.twist.linear.x    = v
        cmd.twist.twist.angular.z   = omega_smoothed
        self.speed_pub.publish(cmd)

        return None

    # ─────────────────────────────────────────────────────────────────────────────
    def _plan_global_dubins(self) -> bool:
        if self.current_yaw is None:
            return False

        robot_pos = self.robot_position.pose.position
        full_path, wp_ends = [], []

        positions = [(robot_pos.x, robot_pos.y)]
        for wp in self.target_list:
            positions.append((wp.p.pose.position.x, wp.p.pose.position.y))

        R = self.MIN_TURNING_RADIUS
        n = len(positions)

        states = [(positions[0][0], positions[0][1], self.current_yaw)]
        real_wp_state_indices = []

        for i in range(1, n):
            curr = positions[i]
            prev = positions[i - 1]

            if self.DUBINS_MODE == 'vwp':
                h_in = math.atan2(curr[1] - prev[1], curr[0] - prev[0])

                if i == n - 1:
                    states.append((curr[0], curr[1], h_in))
                else:
                    vwp = (curr[0] + R * math.cos(h_in),
                           curr[1] + R * math.sin(h_in))
                    nxt      = positions[i + 1]
                    h_next   = math.atan2(nxt[1] - curr[1], nxt[0] - curr[0])
                    next_vwp = (nxt[0] + R * math.cos(h_next),
                                nxt[1] + R * math.sin(h_next))
                    h_exit   = math.atan2(next_vwp[1] - curr[1], next_vwp[0] - curr[0])
                    states.append((vwp[0],  vwp[1],  h_in))
                    states.append((curr[0], curr[1], h_exit))

            else:  # smooth mode
                h = (math.atan2(positions[i+1][1] - prev[1], positions[i+1][0] - prev[0])
                     if i < n - 1
                     else math.atan2(curr[1] - prev[1], curr[0] - prev[0]))
                states.append((curr[0], curr[1], h))

            real_wp_state_indices.append(len(states) - 1)

        for i in range(len(states) - 1):
            s1, s2 = states[i], states[i + 1]
            w1 = Waypoint(s1[0], s1[1], math.degrees(s1[2]))
            w2 = Waypoint(s2[0], s2[1], math.degrees(s2[2]))
            params = calc_dubins_path(w1, w2, R)
            if params:
                seg = dubins_traj(params, self.DUBINS_STEP)
                seg = [pt.tolist() if hasattr(pt, 'tolist') else list(pt) for pt in seg]
                full_path.extend(seg if i == 0 else seg[1:])
            else:
                full_path.append(list(s2))

            if (i + 1) in real_wp_state_indices:
                wp_ends.append(len(full_path) - 1)

        self.dubins_path_pub.publish(self._path_msg(full_path))
        self.dubins_path           = full_path
        self.wp_end_indices        = wp_ends
        self.path_cursor           = 0
        self._last_calculated_path = full_path
        self._node.get_logger().info(f"Dubins path planned: {len(full_path)} points")

        try:
            waypoints_latlon = [
                {
                    'latitude':  ll['latitude'],
                    'longitude': ll['longitude'],
                    'tolerance': self.target_list[i].tol,
                }
                for i, ll in enumerate(self.target_list_latlon)
            ]
            self._publish_waraps_feedback({
                'speed':     self.speed_kn,
                'waypoints': waypoints_latlon,
            })
            self._node.get_logger().info(
                f"[WARAPS] List sent ({len(waypoints_latlon)} pts)"
            )
        except Exception as e:
            self._node.get_logger().error(f"[WARAPS] Error : {e}")

        return True

    # ─────────────────────────────────────────────────────────────────────────
    def _find_closest(self, robot_pos, start: int, end: int) -> int:
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
    def _send_stop(self):
        cmd                         = Odometry()
        cmd.header.stamp            = self._node.get_clock().now().to_msg()
        cmd.header.frame_id         = self.frame_id
        cmd.child_frame_id          = "evolo/base_link"
        cmd.pose.pose.position.x    = self.robot_position.pose.position.x
        cmd.pose.pose.position.y    = self.robot_position.pose.position.y
        cmd.pose.pose.orientation   = self.robot_position.pose.orientation
        cmd.twist.twist.linear.x    = 0.0
        cmd.twist.twist.angular.z   = 0.0
        self.speed_pub.publish(cmd)

    # ─────────────────────────────────────────────────────────────────────────
    def _path_msg(self, configurations) -> Path:
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

    # ─────────────────────────────────────────────────────────────────────────
    def _give_feedback(self) -> str:
        time_now = int(self._node.get_clock().now().nanoseconds * 1e-9)
        runtime  = time_now - self.action_started_time
        pct = (round(100.0 * self._precision_ticks_close / self._precision_ticks_total, 2)
               if self._precision_ticks_total > 0 else 0.0)

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

        self._node.get_logger().info(
            f"precision={pct}% | dist={self._distance_travelled:.1f}m"
            f" | cursor={self.path_cursor}/{len(self.dubins_path) if self.dubins_path else '?'}"
        )

        fb = {
            "runtime":            runtime,
            "precision_pct":      pct,
            "precision_close":    self._precision_ticks_close,
            "precision_total":    self._precision_ticks_total,
            "distance_travelled": round(self._distance_travelled, 2),
            "total_progress_pct": total_progress_pct,
            "wp_progress_pct":    wp_progress_pct,
            "wp_current_idx":     wp_current_idx,
        }

        if hasattr(self, '_waypoints_for_client') and self._waypoints_for_client:
            fb['wps'] = self._waypoints_for_client
            self._waypoints_for_client = None

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
                timeout=Duration(seconds=1),
            )
            return do_transform_pose_stamped(ps, t)
        except Exception as e:
            self._node.get_logger().error(f"TF failed: {e}")
            return None

    # ─────────────────────────────────────────────────────────────────────────
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
                    timeout=Duration(seconds=1),
                )
                self.robot_position = do_transform_pose_stamped(raw, t)
            except Exception as e:
                self._node.get_logger().error(f"Odom TF failed: {e}")
                return

        self.robot_position_time = int(self._node.get_clock().now().nanoseconds * 1e-9)
        oq = self.robot_position.pose.orientation
        (_, _, self.current_yaw) = euler_from_quaternion([oq.x, oq.y, oq.z, oq.w])
        self.current_linear_speed  = msg.twist.twist.linear.x
        self.current_angular_speed = msg.twist.twist.angular.z


# ─────────────────────────────────────────────────────────────────────────────
def main():
    rclpy.init()
    node = Node("evolo_move_path_action_server")
    server_instance = EvoloMovePath(node, "move_path")
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down")
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()