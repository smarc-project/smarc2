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
        # Topic principal pour la visualisation des waypoints de mission
        self.viz_pub         = self.create_publisher(MarkerArray, 'mission_visualisation',    10)
        
        # Autres topics de visualisation
        self.path_pub        = self.create_publisher(Path,        'visual_path',      10)
        self.dubins_path_pub = self.create_publisher(Path,        'dubins_path',      10)
        self.attractor_pub   = self.create_publisher(Marker,      'attractor_marker', 10)
        self.geofence_inside_pub  = self.create_publisher(MarkerArray, 'rviz/geofence_inside',  10)
        self.geofence_outside_pub = self.create_publisher(MarkerArray, 'rviz/geofence_outside', 10)
        self.allowed_soft_pub = self.create_publisher(MarkerArray, 'rviz/allowed_buffer_soft', 10)
        self.allowed_hard_pub = self.create_publisher(MarkerArray, 'rviz/allowed_buffer_hard', 10)
        # Dans __init__, ajouter :
        self.islands_raw_pub = self.create_publisher(MarkerArray, 'rviz/islands_raw', 10)
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

        def _poly_to_marker(polygon, marker_id, r, g, b, ns_name) -> Marker:
            m = Marker()
            m.header.stamp    = stamp
            m.header.frame_id = frame_id
            m.ns     = ns_name
            m.id     = marker_id
            m.type   = Marker.LINE_STRIP
            m.action = Marker.ADD
            m.scale.x = 2.0  # Épaisseur de trait identique à ton rendu initial
            m.color.r, m.color.g, m.color.b = r, g, b
            m.color.a = 0.95
            
            # --- CORRECTION VISIBILITÉ : Forçage de l'altitude entre le sol et les buffers ---
            m.pose.position.z = 0.5 

            for pt in polygon.points:
                ps_in = PointStamped()
                ps_in.header = msg.header
                ps_in.point  = Point(x=pt.x, y=pt.y, z=pt.z)
                
                pt_trans = do_transform_point(ps_in, t).point
                pt_trans.z = 0.5  # Assure l'altitude constante sur chaque sommet
                m.points.append(pt_trans)
                
            if polygon.points:
                ps_in = PointStamped()
                ps_in.header = msg.header
                ps_in.point  = Point(x=polygon.points[0].x,
                                     y=polygon.points[0].y,
                                     z=polygon.points[0].z)
                pt_trans = do_transform_point(ps_in, t).point
                pt_trans.z = 0.5
                m.points.append(pt_trans)  # Ferme la boucle du polygone
            return m

        # ── 2. PUBLICATION ZONE GLOBALE (Vert clair) ──
        inside_contours = []

        for poly in msg.geofence:
            contour = []

            for pt in poly.points:
                ps_in = PointStamped()
                ps_in.header = msg.header
                ps_in.point = Point(
                    x=pt.x,
                    y=pt.y,
                    z=pt.z
                )

                p = do_transform_point(ps_in, t).point

                contour.append([
                    float(p.x),
                    float(p.y)
                ])

            if len(contour) >= 2:
                inside_contours.append(contour)

        self._publish_buffer_contours(
            contours=inside_contours,
            publisher=self.geofence_inside_pub,
            ns='geofence',
            r=0.0,
            g=1.0,
            b=0.5,
            line_width=2.0,
            dot_scale=2.0
        )
        # ── 3. PUBLICATION DES ÎLES (Rouge) ──
        # ── 3. PUBLICATION DES ÎLES AVEC LE MÊME RENDU QUE LES BUFFERS ──

        island_contours = []

        for poly in msg.islands:
            contour = []

            for pt in poly.points:
                ps_in = PointStamped()
                ps_in.header = msg.header
                ps_in.point = Point(
                    x=pt.x,
                    y=pt.y,
                    z=pt.z
                )

                p = do_transform_point(ps_in, t).point

                contour.append([
                    float(p.x),
                    float(p.y)
                ])

            if len(contour) >= 2:
                island_contours.append(contour)

        self._publish_buffer_contours(
            contours=island_contours,
            publisher=self.islands_raw_pub,         # ← publisher dédié
            ns='islands_raw',
            r=1.0, g=0.0, b=0.0,                   # rouge
            line_width=2.0, dot_scale=2.0,
        )


        self.get_logger().info(
            f'Geofence raw: {len(msg.geofence)} zones vertes (inside), '
            f'{len(msg.islands)} îles rouges (outside) à Z=0.5m'
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


    def _publish_payload_polygons(self, polygons):

        ma = MarkerArray()
        stamp = self.get_clock().now().to_msg()
        mid = 0

        for poly in polygons:

            color = (0.0, 1.0, 0.5) if poly['stay_inside'] else (1.0, 0.0, 0.0)

            pts = []

            for p in poly['points']:

                pose = self.latlon_to_local_frame(
                    [p['lat'], p['lon'], 0.0]
                )

                if pose is None:
                    continue

                pts.append(
                    Point(
                        x=pose.pose.position.x,
                        y=pose.pose.position.y,
                        z=1.0
                    )
                )

            if len(pts) < 3:
                continue

            line = Marker()
            line.header.frame_id = self.frame_id
            line.header.stamp = stamp
            line.ns = 'payload_polygons'
            line.id = mid
            mid += 1

            line.type = Marker.LINE_STRIP
            line.action = Marker.ADD

            line.scale.x = 2.0

            line.color.r = color[0]
            line.color.g = color[1]
            line.color.b = color[2]
            line.color.a = 1.0

            line.points = pts + [pts[0]]

            ma.markers.append(line)

            dots = Marker()
            dots.header.frame_id = self.frame_id
            dots.header.stamp = stamp
            dots.ns = 'payload_polygons_pts'
            dots.id = mid
            mid += 1

            dots.type = Marker.SPHERE_LIST
            dots.action = Marker.ADD

            dots.scale.x = 3.0
            dots.scale.y = 3.0
            dots.scale.z = 3.0

            dots.color.r = color[0]
            dots.color.g = color[1]
            dots.color.b = color[2]
            dots.color.a = 1.0

            dots.points = pts

            ma.markers.append(dots)

        self.viz_pub.publish(ma)

    def send_goal(self):

        """
        self.get_logger().info('Wait for Action Server…')
        if not self._action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('No server')
            return
        
        # avant la boucle d'attente
        probe = GeoPoint()
        probe.latitude, probe.longitude, probe.altitude = 58.8389422670, 17.6534623045, 0.0
        zone_frame = georef_utils.convert_latlon_to_utm(probe).header.frame_id  # ex: "utm_33_V"

        self.get_logger().info(f'Waiting for TF frame: {zone_frame}')
        while not self._tf_buffer.can_transform(
                self.frame_id, zone_frame, Time(seconds=0)):
            self.get_logger().info('Waiting for TF…')
            rclpy.spin_once(self, timeout_sec=0.5)
        
        while not self._tf_buffer.can_transform(
                self.frame_id, 'utm', Time(seconds=0)):
            self.get_logger().info('Waiting for TF…')
            rclpy.spin_once(self, timeout_sec=0.5)
        
        goal_msg = BaseAction.Goal()
        """

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
            'speed': 'fast',
            'waypoints': [
                {'latitude': 58.8389422670, 'longitude': 17.6534623045, 'tolerance': 3.0},
                {'latitude': 58.8400922670, 'longitude': 17.6540122932, 'tolerance': 3.0},
                {'latitude': 58.8403922670, 'longitude': 17.6533123075, 'tolerance': 3.0},
                {'latitude': 58.8398922670, 'longitude': 17.6518123177, 'tolerance': 3.0},
                # {'latitude': 58.8397922670, 'longitude': 17.6543122871, 'tolerance': 3.0},
                ## {'latitude': 58.8427922670, 'longitude': 17.6593122871, 'tolerance': 3.0},
                # {'latitude': 58.8410922670, 'longitude': 17.6569522871, 'tolerance': 3.0},
                # {'latitude': 58.8407922670, 'longitude': 17.6569522871, 'tolerance': 3.0},
                # {'latitude': 58.8417922670, 'longitude': 17.6563122871, 'tolerance': 3.0},
                {'latitude': 58.8407922670, 'longitude': 17.6553122871, 'tolerance': 3.0},
                {'latitude': 58.84135, 'longitude': 17.6523, 'tolerance': 3.0}
            ],
            'polygons': [
                {
                    'name': 'Big Area',
                    'stay_inside': True,
                    'points': [
                        {'lat': 58.8360, 'lon': 17.6490},
                        {'lat': 58.8430, 'lon': 17.6490},
                        {'lat': 58.8430, 'lon': 17.6573},
                        {'lat': 58.8360, 'lon': 17.6573},
                    ],
                },
                {
                    'name': 'Mini Island V',
                    'stay_inside': False,  # C'est un obstacle
                    'points': [
                        {'lat': 58.8415, 'lon': 17.6520},  # Pointe Haut-Gauche
                        {'lat': 58.8411, 'lon': 17.6523},  # Le creux du V (Piège externe)
                        {'lat': 58.8415, 'lon': 17.6526},  # Pointe Haut-Droite
                        {'lat': 58.8413, 'lon': 17.6528},  # Épaisseur Haut-Droite
                        {'lat': 58.8407, 'lon': 17.6523},  # Pointe Basse du V
                        {'lat': 58.8413, 'lon': 17.6518},  # Épaisseur Haut-Gauche
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
                        {'lat': 58.8414, 'lon': 17.6560},
                        {'lat': 58.8419, 'lon': 17.6560},
                        {'lat': 58.8419, 'lon': 17.6565},
                        {'lat': 58.8414, 'lon': 17.6565},
                    ],
                },
            ],
            
        }
        """
        payload = {
            'speed': 'standard',
            'waypoints': [
                # Points de déplacement (partie 2) recalibrés à 58.84 / 17.65
                {'latitude': 58.840056, 'longitude': 17.654263, 'tolerance': 10.0},
                {'latitude': 58.839186, 'longitude': 17.653867, 'tolerance': 10.0},
                {'latitude': 58.839342, 'longitude': 17.654398, 'tolerance': 10.0},
                {'latitude': 58.840202, 'longitude': 17.654747, 'tolerance': 10.0},
                {'latitude': 58.840520, 'longitude': 17.656450, 'tolerance': 10.0},
                {'latitude': 58.840920, 'longitude': 17.657450, 'tolerance': 10.0},
            ],
            'polygons': [
                {
                    'name': 'Big Area',
                    'stay_inside': True,
                    'points': [
                        # Points de la zone (partie 1) translatés à 58.84 / 17.65
                        {'lat': 58.840395, 'lon': 17.656560},
                        {'lat': 58.840464, 'lon': 17.656764},
                        {'lat': 58.840658, 'lon': 17.656717},
                        {'lat': 58.840665, 'lon': 17.656114},
                        {'lat': 58.840660, 'lon': 17.655725},
                        {'lat': 58.840609, 'lon': 17.654923},
                        {'lat': 58.840417, 'lon': 17.654179},
                        {'lat': 58.840076, 'lon': 17.653697},
                        {'lat': 58.839617, 'lon': 17.653721},
                        {'lat': 58.839361, 'lon': 17.653365},
                        {'lat': 58.838913, 'lon': 17.653362},
                        {'lat': 58.838738, 'lon': 17.653927},
                        {'lat': 58.838719, 'lon': 17.654487},
                        {'lat': 58.838845, 'lon': 17.655115},
                        {'lat': 58.839277, 'lon': 17.654723},
                        {'lat': 58.839688, 'lon': 17.654627},
                        {'lat': 58.840102, 'lon': 17.654820},
                        {'lat': 58.840341, 'lon': 17.655387},
                        {'lat': 58.840423, 'lon': 17.655841},
                    ],
                },
            ],
        }
        """



        goal_msg.goal.data = json.dumps(payload)
        self._publish_payload_polygons(payload['polygons'])
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
                        publisher=self.island_soft_pub,
                        ns='island_soft',
                        r=1.0, g=1.0, b=1.0,
                        line_width=1.0, dot_scale=1.5,
                    )
                if 'island_contours_hard' in vg:
                    self._publish_buffer_contours(
                        vg['island_contours_hard'],
                        publisher=self.island_hard_pub,
                        ns='island_hard',
                        r=1.0, g=0.5, b=0.0,
                        line_width=1.2, dot_scale=1.8,
                    )
                if 'allowed_contours_raw' in vg:
                    self._publish_buffer_contours(
                        vg['allowed_contours_raw'],
                        publisher=self.geofence_inside_pub,   # réutilise le pub existant
                        ns='allowed_raw',
                        r=0.0, g=1.0, b=0.5,   # vert clair = zone brute
                        line_width=2.0, dot_scale=2.0,
                    )
                if 'allowed_contours_soft' in vg:
                    self._publish_buffer_contours(
                        vg['allowed_contours_soft'],
                        publisher=self.allowed_soft_pub,
                        ns='allowed_soft',
                        r=0.0, g=0.8, b=1.0,   # cyan = limite soft intérieure
                        line_width=1.0, dot_scale=1.5,
                    )
                if 'allowed_contours_hard' in vg:
                    self._publish_buffer_contours(
                        vg['allowed_contours_hard'],
                        publisher=self.allowed_hard_pub,
                        ns='allowed_hard',
                        r=1.0, g=0.8, b=0.0,   # jaune = limite hard (zone de planning)
                        line_width=1.2, dot_scale=1.8,
                    )
        except Exception as e:
            self.get_logger().error(f'Feedback error: {e}')

    # ─────────────────────────────────────────────────────────────────────────
    # Island buffer visualisation
    # ─────────────────────────────────────────────────────────────────────────
    # ─────────────────────────────────────────────────────────────────────────
    # Island buffer visualisation
    # ─────────────────────────────────────────────────────────────────────────
    def _publish_buffer_contours(self, contours, publisher, ns, r, g, b, line_width, dot_scale):
        if not contours:
            return

        stamp = self.get_clock().now().to_msg()
        
        # ── 1. Clear pass — separate publish ─────────────────────────────────
        clear_ma = MarkerArray()
        for clear_ns in [f'{ns}_line', f'{ns}_dots']:
            m = Marker()
            m.header.frame_id = self.frame_id
            m.header.stamp    = stamp
            m.ns              = clear_ns
            m.id              = 0
            #m.action          = Marker.DELETEALL
            clear_ma.markers.append(m)
        publisher.publish(clear_ma)

        # ── 2. Draw pass ──────────────────────────────────────────────────────
        ma  = MarkerArray()
        mid = 0

        for contour in contours:
            if len(contour) < 2:
                continue

            pts = [Point(x=float(c[0]), y=float(c[1]), z=1.0) for c in contour]

            line = Marker()
            line.header.frame_id = self.frame_id
            line.header.stamp    = stamp
            line.ns, line.id     = f'{ns}_line', mid;  mid += 1
            line.type            = Marker.LINE_STRIP
            line.action          = Marker.ADD
            line.scale.x         = line_width
            line.color.r, line.color.g, line.color.b, line.color.a = r, g, b, 1.0
            line.points          = pts + [pts[0]]
            ma.markers.append(line)

            dots = Marker()
            dots.header.frame_id = self.frame_id
            dots.header.stamp    = stamp
            dots.ns, dots.id     = f'{ns}_dots', mid;  mid += 1
            dots.type            = Marker.SPHERE_LIST
            dots.action          = Marker.ADD
            dots.scale.x = dots.scale.y = dots.scale.z = dot_scale
            dots.color.r, dots.color.g, dots.color.b, dots.color.a = r, g, b, 1.0
            dots.points          = pts
            ma.markers.append(dots)

        publisher.publish(ma)
        self.get_logger().info(
            f'[{ns}] {len(contours)} contour(s) | '
            f'{sum(len(c) for c in contours)} pts at Z=1.0m'
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
        m.pose.position.z = 2.0 # Flotte bien haut
        m.scale.x = 4.0; m.scale.y = 4.0; m.scale.z = 4.0
        m.color.r = 1.0; m.color.g = 1.0; m.color.b = 0.0; m.color.a = 0.9 # Jaune fluo
        self.attractor_pub.publish(m)

    # ─────────────────────────────────────────────────────────────────────────
    # Waypoint markers (LA PARTIE AMÉLIORÉE POUR LA VISIBILITÉ)
    # ─────────────────────────────────────────────────────────────────────────
    def publish_waypoints_markers(self):
        ma = MarkerArray()
        stamp = self.get_clock().now().to_msg()
        mid = 0

        if not self.target_list:
            self.viz_pub.publish(ma)
            return

        # Extraction des coordonnées et calage de l'altitude Z
        pts = []
        for wp in self.target_list:
            pt = Point()
            pt.x = float(wp['x'])
            pt.y = float(wp['y'])
            pt.z = 2.0  # Placé à 2.0m pour flotter juste au-dessus des lignes de carte
            pts.append(pt)

        # ── 1. LE CONTOUR INTER-WAYPOINTS (Optionnel, changé en blanc discret) ──
        if len(pts) >= 2:
            line = Marker()
            line.header.frame_id = self.frame_id
            line.header.stamp    = stamp
            line.ns              = 'waypoints_contour'
            line.id              = mid; mid += 1
            line.type            = Marker.LINE_STRIP
            line.action          = Marker.ADD
            line.scale.x         = 1.0  
            line.color.r, line.color.g, line.color.b, line.color.a = 1.0, 1.0, 1.0, 0.6 # Blanc transparent
            line.points          = pts 
            ma.markers.append(line) 

        # ── 2. LES SPHÈRES ROUGES ──
        for i, pt in enumerate(pts):
            dot = Marker()
            dot.header.frame_id = self.frame_id
            dot.header.stamp    = stamp
            dot.ns              = 'waypoints_spheres'
            dot.id              = mid; mid += 1
            
            # --- CORRECTION : Type repassé en SPHERE ---
            dot.type            = Marker.SPHERE
            dot.action          = Marker.ADD
            
            # Taille des sphères (diamètre de 3 mètres)
            dot.scale.x         = 3.0  
            dot.scale.y         = 3.0
            dot.scale.z         = 3.0
            
            dot.pose.position   = pt
            
            # --- CORRECTION : Couleur Rouge Pure Opaque ---
            dot.color.r         = 1.0
            dot.color.g         = 0.0
            dot.color.b         = 0.0
            dot.color.a         = 1.0  
            ma.markers.append(dot)

            # Index du waypoint au-dessus de la sphère
            text = Marker()
            text.header.frame_id = self.frame_id
            text.header.stamp    = stamp
            text.ns              = 'waypoints_labels'
            text.id              = mid; mid += 1
            text.type            = Marker.TEXT_VIEW_FACING
            text.action          = Marker.ADD
            text.pose.position.x = pt.x
            text.pose.position.y = pt.y
            text.pose.position.z = pt.z + 2.5 
            text.scale.z         = 3.0 
            text.color.r, text.color.g, text.color.b, text.color.a = 1.0, 1.0, 1.0, 1.0
            text.text            = str(i)
            ma.markers.append(text)

        # Publication sur le topic 'mission_visualisation'
        self.viz_pub.publish(ma)
        self.get_logger().info(f"Publication de {len(pts)} sphères rouges sur RViz.")











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
            ps.pose.position.z = 0.5 # Légèrement au dessus du sol pour être visible
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