import rclpy
import math
import json

from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.time import Duration, Time
from smarc_msgs.action import BaseAction
from nav_msgs.msg import Path, Odometry
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point, PoseStamped, Quaternion
from geographic_msgs.msg import GeoPoint
from tf2_ros import Buffer, TransformListener
from tf2_geometry_msgs import do_transform_pose_stamped, do_transform_point
from geometry_msgs.msg import PointStamped
from smarc_utilities import georef_utils
import tf_transformations

from smarc_msgs.msg import GeofencePolygonsStamped
from sensor_msgs.msg import NavSatFix
from smarc_msgs.msg import Topics as SmarcTopics
from rclpy.action import ActionClient as RosActionClient


class EvoloMovePathClient(Node):

    def __init__(self):
        super().__init__('evolo_move_path_client')
        self._action_client = ActionClient(self, BaseAction, 'move_path')

        self._tf_buffer   = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self, spin_thread=True)

        self.frame_id    = 'evolo/odom'
        self.target_list = []

        # ── Publishers ────────────────────────────────────────────────────────
        self.marker_pub      = self.create_publisher(MarkerArray, 'waypoints_viz',    10)
        self.path_pub        = self.create_publisher(Path,        'visual_path',      10)
        self.viz_pub         = self.create_publisher(MarkerArray, 'visualisation',    10)
        self.dubins_path_pub = self.create_publisher(Path,        'dubins_path',      10)
        self.attractor_pub   = self.create_publisher(Marker,      'attractor_marker', 10)
        self.geofence_inside_pub  = self.create_publisher(MarkerArray, 'rviz/geofence_inside',  10)
        self.geofence_outside_pub = self.create_publisher(MarkerArray, 'rviz/geofence_outside', 10)
        self.geopoint_pub    = self.create_publisher(GeoPoint, SmarcTopics.POS_LATLON_TOPIC, 10)

        # ── Island buffer publishers ──────────────────────────────────────────
        # Soft buffer (white) — traversable, used as Dijkstra node source
        self.island_soft_pub = self.create_publisher(
            MarkerArray, 'rviz/island_buffer_soft', 10)
        # Hard buffer (orange) — absolute exclusion zone
        self.island_hard_pub = self.create_publisher(
            MarkerArray, 'rviz/island_buffer_hard', 10)

        # ── Subscribers ───────────────────────────────────────────────────────
        self.gps_sub      = self.create_subscription(
            NavSatFix, '/evolo/Lidar/gps', self._gps_callback, 10)
        self.polygons_sub = self.create_subscription(
            GeofencePolygonsStamped, '/smarc/geofence_polygons',
            self._geofence_polygons_callback, 10)
        self.odom_sub     = self.create_subscription(
            Odometry, 'evolo/smarc/odom', self._odom_callback, 10)

        self._geofence_start_client = RosActionClient(
            self, BaseAction, 'smarc_start_geofence')

        self.robot_path_msg = Path()
        self.robot_path_msg.header.frame_id = self.frame_id

    # ─────────────────────────────────────────────────────────────────────────
    # TF helper
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
            self.get_logger().error(f'TF failed: {e}')
            return None

    # ─────────────────────────────────────────────────────────────────────────
    # Odometry → robot trail
    # ─────────────────────────────────────────────────────────────────────────
    def _odom_callback(self, msg: Odometry):
        ps = PoseStamped()
        ps.header.frame_id = self.frame_id
        ps.header.stamp    = msg.header.stamp
        ps.pose            = msg.pose.pose

        if msg.header.frame_id != self.frame_id:
            try:
                t = self._tf_buffer.lookup_transform(
                    target_frame=self.frame_id,
                    source_frame=msg.header.frame_id,
                    time=Time(seconds=0),
                    timeout=Duration(seconds=1),
                )
                raw = PoseStamped()
                raw.header = msg.header
                raw.pose   = msg.pose.pose
                ps = do_transform_pose_stamped(raw, t)
            except Exception as e:
                self.get_logger().error(f'Odom TF failed: {e}')
                return

        self.robot_path_msg.poses.append(ps)
        self.robot_path_msg.header.stamp = self.get_clock().now().to_msg()
        self.path_pub.publish(self.robot_path_msg)

    # ─────────────────────────────────────────────────────────────────────────
    # Geofence polygons → RViz (raw island and safe-zone outlines)
    # ─────────────────────────────────────────────────────────────────────────
    def _geofence_polygons_callback(self, msg: GeofencePolygonsStamped):
        stamp    = msg.header.stamp
        frame_id = self.frame_id

        try:
            t = self._tf_buffer.lookup_transform(
                self.frame_id, msg.header.frame_id,
                Time(seconds=0), timeout=Duration(seconds=1))
        except Exception as e:
            self.get_logger().error(f'TF geofence failed: {e}')
            return

        def _poly_to_marker(polygon, marker_id, r, g, b) -> Marker:
            m = Marker()
            m.header.stamp    = stamp
            m.header.frame_id = frame_id
            m.ns     = 'geofence'
            m.id     = marker_id
            m.type   = Marker.LINE_STRIP
            m.action = Marker.ADD
            m.scale.x = 2.0
            m.color.r, m.color.g, m.color.b = r, g, b
            m.color.a = 0.9
            for pt in polygon.points:
                ps_in = PointStamped()
                ps_in.header = msg.header
                ps_in.point  = Point(x=pt.x, y=pt.y, z=pt.z)
                m.points.append(do_transform_point(ps_in, t).point)
            if polygon.points:
                ps_in = PointStamped()
                ps_in.header = msg.header
                ps_in.point  = Point(x=polygon.points[0].x,
                                     y=polygon.points[0].y,
                                     z=polygon.points[0].z)
                m.points.append(do_transform_point(ps_in, t).point)
            return m

        inside_array = MarkerArray()
        for i, poly in enumerate(msg.geofence):
            inside_array.markers.append(_poly_to_marker(poly, i, 0.0, 1.0, 0.0))
        self.geofence_inside_pub.publish(inside_array)

        outside_array = MarkerArray()
        for i, poly in enumerate(msg.islands):
            outside_array.markers.append(_poly_to_marker(poly, i, 1.0, 0.0, 0.0))
        self.geofence_outside_pub.publish(outside_array)

        self.get_logger().info(
            f'Geofence: {len(msg.geofence)} inside (green), '
            f'{len(msg.islands)} outside (red)'
        )

    # ─────────────────────────────────────────────────────────────────────────
    # GPS → GeoPoint relay
    # ─────────────────────────────────────────────────────────────────────────
    def _gps_callback(self, msg: NavSatFix):
        gp = GeoPoint()
        gp.latitude  = msg.latitude
        gp.longitude = msg.longitude
        gp.altitude  = msg.altitude
        self.geopoint_pub.publish(gp)

    # ─────────────────────────────────────────────────────────────────────────
    # Goal dispatch
    # ─────────────────────────────────────────────────────────────────────────
    def _send_polygons_to_geofence(self, polygons: list):
        if not self._geofence_start_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().warn('smarc_start_geofence not available, skipping')
            return
        for poly_def in polygons:
            goal_msg = BaseAction.Goal()
            payload = {
                'stay_inside': poly_def['stay_inside'],
                'ceiling_altitude': 1000.0,
                'floor_altitude':   0.0,
                'waypoints': [
                    {'latitude': pt['lat'], 'longitude': pt['lon'], 'altitude': 0.0}
                    for pt in poly_def['points']
                ],
            }
            goal_msg.goal.data = json.dumps(payload)
            self.get_logger().info(
                f"Sending polygon '{poly_def['name']}' to geofence "
                f"(stay_inside={poly_def['stay_inside']})"
            )
            self._geofence_start_client.send_goal_async(goal_msg)

    def send_goal(self):
        self.get_logger().info('Wait for Action Server…')
        if not self._action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('No server')
            return
        while not self._tf_buffer.can_transform(
                self.frame_id, 'utm', Time(seconds=0)):
            self.get_logger().info('Waiting for TF…')
            rclpy.spin_once(self, timeout_sec=0.5)

        goal_msg = BaseAction.Goal()
        payload = {
            'speed': 'high',
            'waypoints': [
                {'latitude': 58.8389422670, 'longitude': 17.6534623045, 'tolerance': 3.0},
                {'latitude': 58.8400922670, 'longitude': 17.6540122932, 'tolerance': 3.0},
                {'latitude': 58.8403922670, 'longitude': 17.6533123075, 'tolerance': 3.0},
                {'latitude': 58.8398922670, 'longitude': 17.6518123177, 'tolerance': 3.0},
                {'latitude': 58.8397922670, 'longitude': 17.6543122871, 'tolerance': 3.0},
            ],
            'polygons': [
                {
                    'name': 'Big Area',
                    'stay_inside': True,
                    'points': [
                        {'lat': 58.8380, 'lon': 17.6500},
                        {'lat': 58.8420, 'lon': 17.6500},
                        {'lat': 58.8420, 'lon': 17.6570},
                        {'lat': 58.8380, 'lon': 17.6570},
                    ],
                },
                {
                    'name': 'Island 1',
                    'stay_inside': False,
                    'points': [
                        {'lat': 58.8395, 'lon': 17.6530},
                        {'lat': 58.8400, 'lon': 17.6530},
                        {'lat': 58.8400, 'lon': 17.6532},
                        {'lat': 58.8395, 'lon': 17.6535},
                    ],
                },
                {
                    'name': 'Island 2',
                    'stay_inside': False,
                    'points': [
                        {'lat': 58.8405, 'lon': 17.6540},
                        {'lat': 58.8407, 'lon': 17.6540},
                        {'lat': 58.8407, 'lon': 17.6542},
                        {'lat': 58.8405, 'lon': 17.6542},
                    ],
                },
                {
                    'name': 'Island 3',
                    'stay_inside': False,
                    'points': [
                        {'lat': 58.8410, 'lon': 17.6510},
                        {'lat': 58.8415, 'lon': 17.6510},
                        {'lat': 58.8415, 'lon': 17.6515},
                        {'lat': 58.8410, 'lon': 17.6515},
                    ],
                },
                {
                    'name': 'Island 4',
                    'stay_inside': False,
                    'points': [
                        {'lat': 58.8385, 'lon': 17.6550},
                        {'lat': 58.8390, 'lon': 17.6550},
                        {'lat': 58.8390, 'lon': 17.6555},
                        {'lat': 58.8385, 'lon': 17.6555},
                    ],
                },
                {
                    'name': 'Island 5',
                    'stay_inside': False,
                    'points': [
                        {'lat': 58.8412, 'lon': 17.6560},
                        {'lat': 58.8416, 'lon': 17.6560},
                        {'lat': 58.8416, 'lon': 17.6565},
                        {'lat': 58.8412, 'lon': 17.6565},
                    ],
                },
            ],
        }

        goal_msg.goal.data = json.dumps(payload)
        if 'polygons' in payload:
            self._send_polygons_to_geofence(payload['polygons'])

        self.get_logger().info('Send mission…')
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Mission rejected')
            return
        self.get_logger().info('Mission accepted')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        future.result().result
        self.get_logger().info('Final Result')
        rclpy.shutdown()

    # ─────────────────────────────────────────────────────────────────────────
    # Feedback — dispatch all server data to RViz
    # ─────────────────────────────────────────────────────────────────────────
    def feedback_callback(self, feedback_msg):
        try:
            data = json.loads(feedback_msg.feedback.feedback.data)

            if 'wps' in data:
                self.target_list = data['wps']
                self.publish_waypoints_markers()

            if 'ax' in data and 'ay' in data:
                self._publish_attractor(data['ax'], data['ay'])

            if 'full_path' in data:
                self.dubins_path_pub.publish(
                    self._convert_list_to_path(data['full_path']))

            # ── Island buffers received once after planning ────────────────────
            if 'visibility_graph' in data:
                vg = data['visibility_graph']
                if 'island_contours_soft' in vg:
                    self._publish_buffer_contours(
                        vg['island_contours_soft'],
                        publisher   = self.island_soft_pub,
                        ns          = 'island_soft',
                        r=1.0, g=1.0, b=1.0,   # white
                        line_width  = 0.25,
                        dot_scale   = 0.8,
                    )
                if 'island_contours_hard' in vg:
                    self._publish_buffer_contours(
                        vg['island_contours_hard'],
                        publisher   = self.island_hard_pub,
                        ns          = 'island_hard',
                        r=1.0, g=0.5, b=0.0,   # orange
                        line_width  = 0.35,
                        dot_scale   = 0.6,
                    )

        except Exception as e:
            self.get_logger().error(f'Feedback error: {e}')

    # ─────────────────────────────────────────────────────────────────────────
    # Island buffer visualisation
    # ─────────────────────────────────────────────────────────────────────────
    def _publish_buffer_contours(
            self,
            contours:   list,
            publisher,
            ns:         str,
            r: float, g: float, b: float,
            line_width: float,
            dot_scale:  float,
    ):
        """
        Publishes a MarkerArray for a list of (x, y) contours.

        For each contour two markers are emitted:
          • LINE_STRIP  — closed polygon outline
          • SPHERE_LIST — one sphere per vertex (the "waypoints" of the buffer)

        Parameters
        ----------
        contours    : list[list[(x, y)]]  received from server JSON
        publisher   : ROS publisher (MarkerArray)
        ns          : marker namespace prefix
        r, g, b     : RGB colour [0-1]
        line_width  : LINE_STRIP scale.x in metres
        dot_scale   : SPHERE_LIST sphere diameter in metres
        """
        if not contours:
            return

        ma    = MarkerArray()
        stamp = self.get_clock().now().to_msg()
        mid   = 0

        for contour in contours:
            if len(contour) < 2:
                continue

            pts = [Point(x=float(c[0]), y=float(c[1]), z=0.0) for c in contour]

            # ── Closed polygon outline ────────────────────────────────────────
            line = Marker()
            line.header.frame_id = self.frame_id
            line.header.stamp    = stamp
            line.ns, line.id     = f'{ns}_line', mid;  mid += 1
            line.type            = Marker.LINE_STRIP
            line.action          = Marker.ADD
            line.scale.x         = line_width
            line.color.r         = r
            line.color.g         = g
            line.color.b         = b
            line.color.a         = 0.85
            line.points          = pts + [pts[0]]   # close the loop
            ma.markers.append(line)

            # ── Vertex spheres ("waypoints" of the buffer contour) ────────────
            dots = Marker()
            dots.header.frame_id = self.frame_id
            dots.header.stamp    = stamp
            dots.ns, dots.id     = f'{ns}_dots', mid;  mid += 1
            dots.type            = Marker.SPHERE_LIST
            dots.action          = Marker.ADD
            dots.scale.x = dots.scale.y = dots.scale.z = dot_scale
            dots.color.r         = r
            dots.color.g         = g
            dots.color.b         = b
            dots.color.a         = 1.0
            dots.points          = pts
            ma.markers.append(dots)

            # ── Vertex index labels ───────────────────────────────────────────
            for k, pt in enumerate(pts):
                label = Marker()
                label.header.frame_id = self.frame_id
                label.header.stamp    = stamp
                label.ns, label.id    = f'{ns}_labels', mid;  mid += 1
                label.type            = Marker.TEXT_VIEW_FACING
                label.action          = Marker.ADD
                label.pose.position.x = pt.x
                label.pose.position.y = pt.y
                label.pose.position.z = 1.5
                label.scale.z         = 0.8
                label.color.r         = r
                label.color.g         = g
                label.color.b         = b
                label.color.a         = 1.0
                label.text            = str(k)
                ma.markers.append(label)

        publisher.publish(ma)
        self.get_logger().info(
            f'[{ns}] {len(contours)} contour(s) | '
            f'{sum(len(c) for c in contours)} vertex markers published'
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Attractor marker
    # ─────────────────────────────────────────────────────────────────────────
    def _publish_attractor(self, ax, ay):
        m = Marker()
        m.header.frame_id = self.frame_id
        m.header.stamp    = self.get_clock().now().to_msg()
        m.ns = 'attractor'; m.id = 0
        m.type = Marker.SPHERE; m.action = Marker.ADD
        m.pose.position.x = ax
        m.pose.position.y = ay
        m.pose.position.z = 1.0
        m.scale.x = 3.0; m.scale.y = 3.0; m.scale.z = 3.0
        m.color.r = 1.0; m.color.g = 1.0; m.color.b = 0.0; m.color.a = 0.9
        self.attractor_pub.publish(m)

    # ─────────────────────────────────────────────────────────────────────────
    # Waypoint markers
    # ─────────────────────────────────────────────────────────────────────────
    def publish_waypoints_markers(self):
        if not self.target_list:
            return
        ma = MarkerArray()
        for i, wp in enumerate(self.target_list):
            # Tolerance sphere
            m = Marker()
            m.header.frame_id = self.frame_id
            m.header.stamp    = self.get_clock().now().to_msg()
            m.ns = 'waypoints'; m.id = i
            m.type = Marker.SPHERE; m.action = Marker.ADD
            m.pose.position.x = float(wp['x'])
            m.pose.position.y = float(wp['y'])
            m.pose.position.z = 0.5
            m.scale.x = float(wp['tol']) * 2
            m.scale.y = float(wp['tol']) * 2
            m.scale.z = 1.0
            m.color.g = 1.0; m.color.a = 0.3
            ma.markers.append(m)

            # Label
            t = Marker()
            t.header = m.header
            t.ns = 'waypoint_labels'; t.id = i + 1000
            t.type = Marker.TEXT_VIEW_FACING; t.action = Marker.ADD
            t.pose.position.x = m.pose.position.x
            t.pose.position.y = m.pose.position.y
            t.pose.position.z = 2.0
            t.scale.z = 1.5
            t.color.r = t.color.g = t.color.b = t.color.a = 1.0
            t.text = f'WP{i + 1}'
            ma.markers.append(t)

        self.viz_pub.publish(ma)

    # ─────────────────────────────────────────────────────────────────────────
    # Dubins path helper
    # ─────────────────────────────────────────────────────────────────────────
    def _convert_list_to_path(self, points) -> Path:
        path_msg = Path()
        path_msg.header.frame_id = self.frame_id
        path_msg.header.stamp    = self.get_clock().now().to_msg()
        for pt in points:
            ps = PoseStamped()
            ps.header          = path_msg.header
            ps.pose.position.x = pt[0]
            ps.pose.position.y = pt[1]
            path_msg.poses.append(ps)
        return path_msg


# ─────────────────────────────────────────────────────────────────────────────
def main(args=None):
    rclpy.init(args=args)
    client = EvoloMovePathClient()
    client.send_goal()
    rclpy.spin(client)


if __name__ == '__main__':
    main()