import rclpy

from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from smarc_action_base.gentler_action_server import GentlerActionServer
from geodesy import utm
from geographic_msgs.msg import GeoPoint
from tf2_geometry_msgs import do_transform_pose_stamped
from tf_transformations import euler_from_quaternion
from rclpy.time import Duration, Time
from nav_msgs.srv import SetMap
from nav_msgs.msg import OccupancyGrid
from nav_msgs.msg import MapMetaData
from nav_msgs.srv import GetPlan
from nav_msgs.msg import Path
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose
from geometry_msgs.msg import Twist, TwistStamped
from geometry_msgs.msg import Point
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32, Empty
from std_msgs.msg import String
from evolo_msgs.msg import Topics as evoloTopics
from smarc_msgs.msg import Topics as smarcTopics
from smarc_control_msgs.msg import Topics as controlTopics
from tf2_ros import Buffer, TransformException, TransformListener
import numpy as np
import time
import math
import json
from geometry_msgs.msg import Quaternion
from smarc_utilities import georef_utils

import tf_transformations

from enum import Enum

from dubins_planner.dubins import Waypoint, calc_dubins_path, dubins_traj



class PurePursuitController:
    """
    Parameters:
        Ld_base   : Base lookahead distance (m)
        Ld_gain   : Lookahead velocity gain (Ld = Ld_base + Ld_gain * v)
        omega_max : Angular velocity saturation (deg/s)
        ff_gain   : Dubins curvature feedforward gain (0 = disabled)
    """

    def __init__(self,
                 Ld_base, 
                 Ld_gain,
                 omega_max,
                 ff_gain,
                 dubins_step):
        self.Ld_base   = Ld_base
        self.Ld_gain   = Ld_gain
        self.omega_max = omega_max
        self.ff_gain   = ff_gain
        self.dubins_step = dubins_step

    def compute(self,
                robot_x:   float,
                robot_y:   float,
                robot_yaw: float,   
                robot_v:   float,  
                path:      list,
                cursor:    int,
                ) -> tuple[float, float, int]:

        Ld = self.Ld_base + self.Ld_gain * robot_v

        lookahead_idx = cursor
        for i in range(cursor, len(path)):
            px, py, _ = path[i]
            if math.hypot(px - robot_x, py - robot_y) >= Ld:
                lookahead_idx = i
                break
        else:
            lookahead_idx = len(path) - 1

        lx, ly, lyaw = path[lookahead_idx]

        angle_to_target = math.atan2(ly - robot_y, lx - robot_x)
        alpha = math.atan2(
            math.sin(angle_to_target - robot_yaw),
            math.cos(angle_to_target - robot_yaw),
        )

        dist_to_target = math.hypot(lx - robot_x, ly - robot_y)
        if dist_to_target < 0.1:
            kappa = 0.0
        else:
            kappa = 2.0 * math.sin(alpha) / dist_to_target

        ff_omega_rad = 0.0
        if self.ff_gain > 0.0 and lookahead_idx + 1 < len(path):
            _, _, yaw_next = path[min(lookahead_idx + 1, len(path) - 1)]
            _, _, yaw_cur  = path[lookahead_idx]
            dyaw = math.atan2(math.sin(yaw_next - yaw_cur),
                              math.cos(yaw_next - yaw_cur))
            kappa_local = dyaw / self.dubins_step
            ff_omega_rad = self.ff_gain * robot_v * kappa_local

        omega_rad = robot_v * kappa + ff_omega_rad
        omega_deg = math.degrees(omega_rad)

        omega_deg = max(-self.omega_max, min(self.omega_max, omega_deg))

        return omega_deg, lookahead_idx


# ─────────────────────────────────────────────────────────────────────────────
# Action 
# ─────────────────────────────────────────────────────────────────────────────
class EvoloMovePath():

    class WP:
        def __init__(self, p, tol, speed_kn):
            self.p        = p
            self.tol      = tol
            self.speed_kn = speed_kn

    def __init__(self, node: Node, action_name: str):
        self._node = node

        self._node.declare_parameters(
            namespace='',
            parameters=[
                ('v_min', rclpy.Parameter.Type.DOUBLE),
                ('v_max', rclpy.Parameter.Type.DOUBLE),
                ('omega_max', rclpy.Parameter.Type.DOUBLE),
                ('err_large_deg', rclpy.Parameter.Type.DOUBLE),
                ('ld_base', rclpy.Parameter.Type.DOUBLE),
                ('ld_gain', rclpy.Parameter.Type.DOUBLE),
                ('ff_gain', rclpy.Parameter.Type.DOUBLE),
                ('min_turning_radius', rclpy.Parameter.Type.DOUBLE),
                ('dubins_step', rclpy.Parameter.Type.DOUBLE),
                ('timeout', rclpy.Parameter.Type.DOUBLE),
                ('speed_map_slow', rclpy.Parameter.Type.DOUBLE),
                ('speed_map_medium', rclpy.Parameter.Type.DOUBLE),
                ('speed_map_high', rclpy.Parameter.Type.DOUBLE),
                ('frame_id', rclpy.Parameter.Type.STRING)
            ]
        )
        self.V_MIN = self._node.get_parameter('v_min').value
        self.V_MAX = self._node.get_parameter('v_max').value
        self.OMEGA_MAX = self._node.get_parameter('omega_max').value
        self.ERR_LARGE_DEG = self._node.get_parameter('err_large_deg').value
        self.MIN_TURNING_RADIUS = self._node.get_parameter('min_turning_radius').value
        self.DUBINS_STEP = self._node.get_parameter('dubins_step').value
        self.timeout = self._node.get_parameter('timeout').value
        self.frame_id = self._node.get_parameter('frame_id').value
        self.SPEED_MAP = {
            "slow": self._node.get_parameter('speed_map_slow').value,
            "medium": self._node.get_parameter('speed_map_medium').value,
            "high": self._node.get_parameter('speed_map_high').value
        }
        self.controller = PurePursuitController(
            Ld_base   = self._node.get_parameter('ld_base').value,
            Ld_gain   = self._node.get_parameter('ld_gain').value,
            omega_max = self.OMEGA_MAX,
            ff_gain   = self._node.get_parameter('ff_gain').value,
            dubins_step = self.DUBINS_STEP
        )

        self._as = GentlerActionServer(
            node, action_name,
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency=50,
        )

        self._tf_buffer   = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self._node,
                                              spin_thread=True)

        self.robot_position      = PoseStamped()
        self.robot_position_time = None
        self.current_yaw         = None
        self.distance_to_target  = None
        self.current_linear_speed  = 0.0
        self.current_angular_speed = 0.0

        self.target_index  = None
        self.target_list   = None
        self.poses_history = []

        self.dubins_path    = None
        self.wp_end_indices = None
        self.path_cursor    = 0

        self.action_started_time = None

        self.publisher_callback_group  = ReentrantCallbackGroup()
        self.subscriber_callback_group = ReentrantCallbackGroup()

        self.evolo_pub       = self._node.create_publisher(Float32,      controlTopics.CONTROL_YAW_TOPIC, 10, callback_group=self.publisher_callback_group)
        self.speed_pub       = self._node.create_publisher(TwistStamped, evoloTopics.EVOLO_TWIST_PLANNED,    10, callback_group=self.publisher_callback_group)
        # self.speed_pub       = self._node.create_publisher(TwistStamped, 'evolo/ctrl/twist_setpoint',    10, callback_group=self.publisher_callback_group)
        self.path_pub        = self._node.create_publisher(Path,         'visual_path',                   10, callback_group=self.publisher_callback_group)
        self.viz_pub         = self._node.create_publisher(MarkerArray,  'visualisation',                 10, callback_group=self.publisher_callback_group)
        self.dubins_path_pub = self._node.create_publisher(Path,         'dubins_path',                   10, callback_group=self.publisher_callback_group)
        self.attractor_pub   = self._node.create_publisher(Marker,       'attractor_marker',              10, callback_group=self.publisher_callback_group)

        self.robot_sub = self._node.create_subscription(Odometry, smarcTopics.ODOM_TOPIC, self.robot_odom_callback, 10,callback_group=self.subscriber_callback_group)
        # self.robot_sub = self._node.create_subscription(Odometry, 'evolo/smarc/odom', self.robot_odom_callback, 10,callback_group=self.subscriber_callback_group)


        self._node.get_logger().info("EvoloMovePath started")

    # ─────────────────────────────────────────────────────────────────────────
    def _on_goal_received(self, goal_request: dict) -> bool:
        raw_speed = goal_request['speed']
        if isinstance(raw_speed, str) and raw_speed.lower() in self.SPEED_MAP:
            speed_kn = self.SPEED_MAP[raw_speed.lower()]
        else:
            try:    speed_kn = float(raw_speed)
            except: speed_kn = self.SPEED_MAP['medium']

        waypoints = goal_request.get('waypoints', [])
        if not waypoints:
            return False

        self.target_index   = 0
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
            self.target_list.append(self.WP(p=pose, tol=tol, speed_kn=speed_kn))
            self._node.get_logger().info(
                f"  WP{len(self.target_list)}: "
                f"({pose.pose.position.x:.1f}, {pose.pose.position.y:.1f}) tol={tol}m"
            )

        self.publish_waypoints_markers()
        return True

    def _on_cancel_received(self) -> bool:
        self._send_stop()
        return True

    def _prepare_loop(self) -> None:
        self.action_started_time = int(self._node.get_clock().now().nanoseconds * 1e-9)
        self.dubins_path    = None
        self.wp_end_indices = None
        self.path_cursor    = 0
        self.target_index   = 0


    def _get_local_curvature(self, path: list, cursor: int) -> float:

        if cursor + 2 >= len(path):
            return 0.0
        
        x1, y1, yaw1 = path[cursor]
        x2, y2, yaw2 = path[cursor + 1]
        x3, y3, yaw3 = path[cursor + 2]

        dyaw1 = math.atan2(math.sin(yaw2 - yaw1), math.cos(yaw2 - yaw1))
        dyaw2 = math.atan2(math.sin(yaw3 - yaw2), math.cos(yaw3 - yaw2))
        
        avg_dyaw = (dyaw1 + dyaw2) / 2.0
        kappa = avg_dyaw / self.DUBINS_STEP  

        return kappa



    # ─────────────────────────────────────────────────────────────────────────
    def _loop_inner(self) -> bool | None:
        time_now = int(self._node.get_clock().now().nanoseconds * 1e-9)
        runtime  = time_now - self.action_started_time

        if runtime > self.timeout:
            self._send_stop()
            return False

        if self.robot_position_time is None or self.current_yaw is None:
            return None

        if not self.target_list or self.target_index >= len(self.target_list):
            return True

        robot_pos = self.robot_position.pose.position

        # Planification
        if self.dubins_path is None:
            if not self._plan_global_dubins():
                return None

        path = self.dubins_path

        search_end       = min(len(path), self.path_cursor + 400)
        candidate        = self._find_closest(robot_pos, self.path_cursor, search_end)
        self.path_cursor = max(self.path_cursor, candidate)
        self.path_cursor = min(self.path_cursor, len(path) - 1)

        current_wp = self.target_list[self.target_index]
        dist_to_wp = math.hypot(
            current_wp.p.pose.position.x - robot_pos.x,
            current_wp.p.pose.position.y - robot_pos.y,
        )
        self.distance_to_target = dist_to_wp

        wp_end_idx   = self.wp_end_indices[self.target_index]
        wp_start_idx = self.wp_end_indices[self.target_index - 1] if self.target_index > 0 else 0
        wp_arc_len   = max(1, wp_end_idx - wp_start_idx)
        arc_done     = (self.path_cursor - wp_start_idx) / wp_arc_len >= 0.90

        if dist_to_wp < current_wp.tol and arc_done:
            self._node.get_logger().info(
                f"✓ WP{self.target_index + 1} atteint (dist={dist_to_wp:.1f}m)")
            self.target_index += 1
            if self.target_index >= len(self.target_list):
                self._send_stop()
                return True
            self.path_cursor = self.wp_end_indices[self.target_index - 1]
            return None

        attr_idx  = min(self.path_cursor + 40, len(path) - 1)
        ax, ay, _ = path[attr_idx]
        self._publish_attractor(ax, ay)

        desired_angle = math.atan2(ay - robot_pos.y, ax - robot_pos.x)
        angle_error   = math.atan2(
            math.sin(desired_angle - self.current_yaw),
            math.cos(desired_angle - self.current_yaw),
        )
        abs_err_deg = abs(math.degrees(angle_error))

        # Control
        v = current_wp.speed_kn

        omega, lookahead_idx = self.controller.compute(
            robot_x   = float(robot_pos.x),
            robot_y   = float(robot_pos.y),
            robot_yaw = float(self.current_yaw),
            robot_v   = float(self.current_linear_speed) or v,
            path      = path,
            cursor    = self.path_cursor,
        )
        slow_factor = max(0.0, 1.0 - abs_err_deg / self.ERR_LARGE_DEG)
        v = self.V_MIN + slow_factor * (v - self.V_MIN)
        mode = "PP"

        # Publication
        cmd = TwistStamped()
        cmd.header.stamp    = self._node.get_clock().now().to_msg()
        cmd.header.frame_id = self.frame_id
        cmd.twist.linear.x  = v
        cmd.twist.angular.z = omega
        self.speed_pub.publish(cmd)

        yaw_msg      = Float32()
        yaw_msg.data = float(desired_angle)
        self.evolo_pub.publish(yaw_msg)

        if not hasattr(self, '_log_counter'):
            self._log_counter = 0
        self._log_counter += 1
        if self._log_counter % 50 == 0:
            self._node.get_logger().info(
                f"[{mode}] err={abs_err_deg:.1f}° v={v:.2f} ω={omega:.2f}°/s | "
                f"cursor={self.path_cursor}/{len(path)} DTT={dist_to_wp:.1f}m"
            )

        return None

    # ─────────────────────────────────────────────────────────────────────────
    def _plan_global_dubins(self) -> bool:
        if self.current_yaw is None:
            return False

        robot_pos = self.robot_position.pose.position
        full_path, wp_ends = [], []
        q_prev = (robot_pos.x, robot_pos.y, self.current_yaw)

        self._node.get_logger().info(
            f"Planning Dubins | start=({q_prev[0]:.1f},{q_prev[1]:.1f},"
            f"{math.degrees(q_prev[2]):.0f}°) | {len(self.target_list)} WPs"
        )

        for i, wp in enumerate(self.target_list):
            wp_pos = wp.p.pose.position
            wp_ori = wp.p.pose.orientation
            is_identity = (abs(wp_ori.w - 1.0) < 0.01 and
                           abs(wp_ori.x) < 0.01 and abs(wp_ori.y) < 0.01 and
                           abs(wp_ori.z) < 0.01)
            target_yaw = (math.atan2(wp_pos.y - q_prev[1], wp_pos.x - q_prev[0])
                          if is_identity
                          else euler_from_quaternion([wp_ori.x, wp_ori.y,
                                                      wp_ori.z, wp_ori.w])[2])
            q_next = (wp_pos.x, wp_pos.y, target_yaw)
            try:
                w1 = Waypoint(q_prev[0], q_prev[1], math.degrees(q_prev[2]))
                w2 = Waypoint(q_next[0], q_next[1], math.degrees(q_next[2]))
                param = calc_dubins_path(w1, w2, self.MIN_TURNING_RADIUS)
                seg_array = dubins_traj(param, self.DUBINS_STEP)
                
                seg = [(p[0], p[1], math.radians(p[2])) for p in seg_array]
                
                full_path.extend(seg)
                wp_ends.append(len(full_path) - 1)
                
            except Exception as e:
                self._node.get_logger().error(f"Dubins failed: {e}")
                return False
            q_prev = q_next

        self.dubins_path    = full_path
        self.wp_end_indices = wp_ends
        self.path_cursor    = 0
        self._node.get_logger().info(
            f"✓ Dubins: {len(full_path)} pts | boundaries={wp_ends}")
        self.dubins_path_pub.publish(self._path_msg(full_path))
        return True

    # ─────────────────────────────────────────────────────────────────────────
    def _find_closest(self, robot_pos, start: int, end: int) -> int:
        path     = self.dubins_path
        path_len = len(path)
        yaw      = self.current_yaw or 0.0
        best_idx, best_score = start, float('inf')
        for i in range(start, end):
            x, y, curve_yaw = path[i]
            dist         = math.hypot(x - robot_pos.x, y - robot_pos.y)
            heading_diff = math.atan2(math.sin(curve_yaw - yaw),
                                      math.cos(curve_yaw - yaw))
            score = dist + 8.0 * (1.0 - math.cos(heading_diff)) \
                         + 3.0 * (1.0 - i / path_len)
            if score < best_score:
                best_score = score
                best_idx   = i
        return best_idx

    def _send_stop(self):
        cmd = TwistStamped()
        cmd.header.stamp    = self._node.get_clock().now().to_msg()
        cmd.twist.linear.x  = 0.0
        cmd.twist.angular.z = 0.0
        self.speed_pub.publish(cmd)

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

    def _publish_attractor(self, ax, ay):
        m = Marker()
        m.header.frame_id = self.frame_id
        m.header.stamp    = self._node.get_clock().now().to_msg()
        m.ns = "attractor"; m.id = 0
        m.type = Marker.SPHERE; m.action = Marker.ADD
        m.pose.position.x = ax; m.pose.position.y = ay; m.pose.position.z = 1.0
        m.scale.x = 3.0; m.scale.y = 3.0; m.scale.z = 3.0
        m.color.r = 1.0; m.color.g = 1.0; m.color.b = 0.0; m.color.a = 0.9
        self.attractor_pub.publish(m)

    def _give_feedback(self) -> str:
        time_now = int(self._node.get_clock().now().nanoseconds * 1e-9)
        runtime  = time_now - self.action_started_time
        n   = len(self.target_list) if self.target_list else '?'
        dtt = f"{self.distance_to_target:.1f}" if self.distance_to_target is not None else "?"
        return f"Runtime: {runtime}s | WP: {self.target_index}/{n} | DTT: {dtt}m"

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

    def robot_odom_callback(self, msg: Odometry):
        if self.frame_id is None:
            self.frame_id = msg.header.frame_id

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

        if not hasattr(self, '_odom_log_counter'):
            self._odom_log_counter = 0
        self._odom_log_counter += 1
        if self._odom_log_counter % 50 == 0:
            self._node.get_logger().info(
                f"Odom: ({self.robot_position.pose.position.x:.2f}, "
                f"{self.robot_position.pose.position.y:.2f}), "
                f"yaw={math.degrees(self.current_yaw):.1f}°"
            )

        path_msg = Path()
        path_msg.header.frame_id = self.frame_id
        path_msg.header.stamp    = self._node.get_clock().now().to_msg()
        self.poses_history.append(self.robot_position)
        path_msg.poses = self.poses_history
        self.path_pub.publish(path_msg)

    def publish_waypoints_markers(self):
        ma = MarkerArray()
        for i, wp in enumerate(self.target_list):
            m = Marker()
            m.header.frame_id = self.frame_id
            m.header.stamp    = self._node.get_clock().now().to_msg()
            m.ns = "waypoints"; m.id = i
            m.type = Marker.SPHERE; m.action = Marker.ADD
            m.pose.position.x = wp.p.pose.position.x
            m.pose.position.y = wp.p.pose.position.y
            m.pose.position.z = 0.5
            m.scale.x = wp.tol * 2; m.scale.y = wp.tol * 2; m.scale.z = 1.0
            m.color.g = 1.0; m.color.a = 0.3
            ma.markers.append(m)
            t = Marker()
            t.header = m.header
            t.ns = "waypoint_labels"; t.id = i + 1000
            t.type = Marker.TEXT_VIEW_FACING; t.action = Marker.ADD
            t.pose.position.x = wp.p.pose.position.x
            t.pose.position.y = wp.p.pose.position.y
            t.pose.position.z = 2.0
            t.scale.z = 2.0
            t.color.r = 1.0; t.color.g = 1.0; t.color.b = 1.0; t.color.a = 1.0
            t.text = f"WP{i+1}"
            ma.markers.append(t)
        self.viz_pub.publish(ma)


# ─────────────────────────────────────────────────────────────────────────────
def main():
    rclpy.init()
    node = Node("evolo_move_path_action_server")
    EvoloMovePath(node, "move_path")
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