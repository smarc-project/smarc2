import rclpy
import math
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.time import Duration, Time
from smarc_msgs.action import BaseAction
import json
from nav_msgs.msg import Path, Odometry
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point, PoseStamped, Quaternion
from geographic_msgs.msg import GeoPoint
from std_msgs.msg import String
from tf2_ros import Buffer, TransformListener
from tf2_geometry_msgs import do_transform_pose_stamped
from smarc_utilities import georef_utils
from geofence_checker import geofence_checker_node, geofence_checker_client_node
import tf_transformations
import numpy as np
import re
import yaml


ISLANDS_FILE = '/home/baptiste/colcon_ws/src/smarc2/behaviours/evolo/evolo_move_path/config/islands.yaml'
DEPTH_FILE = '/home/baptiste/colcon_ws/src/smarc2/behaviours/evolo/evolo_move_path/obstacles_bathymetry.yaml'

class EvoloMovePathClient(Node):

    def __init__(self):
        super().__init__('evolo_move_path_client')
        self._action_client = ActionClient(self, BaseAction, 'move_path')

        # TF buffer
        self._tf_buffer   = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self, spin_thread=True)

        # ── Publishers de visualisation ───────────────────────────────────────
        self.marker_pub      = self.create_publisher(MarkerArray, 'waypoints_viz',    10)
        self.path_pub        = self.create_publisher(Path,        'visual_path',      10)
        self.viz_pub         = self.create_publisher(MarkerArray, 'visualisation',    10)
        self.dubins_path_pub = self.create_publisher(Path,        'dubins_path',      10)
        self.boundary_pub    = self.create_publisher(MarkerArray, 'path_boundaries',  10)
        self.obstacle_pub    = self.create_publisher(MarkerArray, 'obstacles',        10)
        self.avoidance_pub   = self.create_publisher(MarkerArray, 'avoidance_waypoints', 10)
        self.visibility_graph_pub = self.create_publisher(MarkerArray, 'evolo/visibility_graph', 10)

        # ── RRT-Dubins : 3 topics dédiés ─────────────────────────────────────
        # 1. Chemin Dubins final (nav_msgs/Path)  — courbe lisse bleue
        self.rrt_dubins_path_pub  = self.create_publisher(Path,        'rrt_dubins/path',  10)
        # 2. Branches de l'arbre RRT  (MarkerArray LINE_STRIPs verts)
        self.rrt_dubins_tree_pub  = self.create_publisher(MarkerArray, 'rrt_dubins/tree',  10)
        # 3. Nœuds de l'arbre RRT    (MarkerArray SPHEREs jaunes)
        self.rrt_dubins_nodes_pub = self.create_publisher(MarkerArray, 'rrt_dubins/nodes', 10)

        # Subscription odométrie
        self.odom_sub = self.create_subscription(
            Odometry, 'evolo/smarc/odom', self._odom_callback, 10)

        # Timer pour republier les obstacles périodiquement (RViz les perd sinon)
        self.obstacle_timer = self.create_timer(2.0, self._obstacle_timer_callback)

        self.poses_history  = []
        self.frame_id       = 'evolo/odom'
        self.target_list    = []

        self.robot_path_msg = Path()
        self.robot_path_msg.header.frame_id = self.frame_id

    # ─────────────────────────────────────────────────────────────────────────
    # Timer callback : republier les obstacles pour qu'ils restent visibles
    # ─────────────────────────────────────────────────────────────────────────
    # ── MODIFICATION : Timer callback pour inclure la profondeur ──────────────
    def _obstacle_timer_callback(self):
        self.publish_obstacles(ISLANDS_FILE)
        self.publish_depth_obstacles(DEPTH_FILE) # Appel pour la bathymétrie

    # ─────────────────────────────────────────────────────────────────────────
    # NOUVEAU : Charger les obstacles depuis le fichier YAML de profondeur
    # ─────────────────────────────────────────────────────────────────────────
    def load_depth_obstacles(self, filepath: str) -> dict:
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            self.get_logger().info(f"Loaded {len(data)} depth obstacles from YAML")
            return data
        except Exception as e:
            self.get_logger().error(f"Cannot open depth file '{filepath}': {e}")
            return {}

    # ─────────────────────────────────────────────────────────────────────────
    # NOUVEAU : Publier les obstacles de profondeur (ORANGE)
    # ─────────────────────────────────────────────────────────────────────────
    def publish_depth_obstacles(self, filepath: str = DEPTH_FILE):
        depth_data = self.load_depth_obstacles(filepath)
        if not depth_data:
            return

        ma = MarkerArray()
        stamp = self.get_clock().now().to_msg()

        for obs_id, (key, coords) in enumerate(depth_data.items()):
            local_pts = []
            for pt in coords:
                # pt est [lat, lon]
                ps = self.latlon_to_local_frame([pt[0], pt[1]])
                if ps is None:
                    continue
                local_pts.append((ps.pose.position.x, ps.pose.position.y))

            if len(local_pts) < 3:
                continue

            # Marker Orange pour la profondeur
            m = Marker()
            m.header.frame_id = self.frame_id
            m.header.stamp    = stamp
            m.ns              = "depth_obstacles"
            m.id              = obs_id
            m.type            = Marker.LINE_STRIP
            m.action          = Marker.ADD
            m.scale.x         = 2.0          # Un peu plus fin que les îles
            
            # Couleur Orange (R:1.0, G:0.5, B:0.0)
            m.color.r         = 1.0
            m.color.g         = 0.5
            m.color.b         = 0.0
            m.color.a         = 1.0   
            
            m.pose.orientation.w = 1.0
            for x, y in local_pts:
                p = Point(); p.x = x; p.y = y; p.z = -0.5 # Légèrement sous les îles
                m.points.append(p)
            m.points.append(m.points[0]) # Fermer le polygone
            ma.markers.append(m)

        self.obstacle_pub.publish(ma)

    # ─────────────────────────────────────────────────────────────────────────
    # Conversion lat/lon → repère local
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
                time=rclpy.time.Time(),
                timeout=Duration(seconds=1),
            )
            return do_transform_pose_stamped(ps, t)
        except Exception as e:
            self.get_logger().error(f"TF failed: {e}")
            return None

    # ─────────────────────────────────────────────────────────────────────────
    # Parse islands
    # ─────────────────────────────────────────────────────────────────────────
    def load_obstacles_from_file(self, filepath: str) -> list:
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            self.get_logger().info(f"Loaded {len(data)} islands from YAML")
            return list(data.values())  # Supposons que le YAML est une map {id: [(lat, lon), ...]}
        except Exception as e:
            self.get_logger().error(f"Cannot open islands file '{filepath}': {e}")
            return []

    # ─────────────────────────────────────────────────────────────────────────
    # Obstacles (rouge, rempli)
    # ─────────────────────────────────────────────────────────────────────────
    def publish_obstacles(self, filepath: str = ISLANDS_FILE):
        islands = self.load_obstacles_from_file(filepath)
        if not islands:
            self.get_logger().warn("No obstacles to publish.")
            return

        ma    = MarkerArray()
        stamp = self.get_clock().now().to_msg()

        for island_id, coords in enumerate(islands):
            local_pts = []
            for lat, lon in coords:
                ps = self.latlon_to_local_frame([lat, lon])
                if ps is None:
                    continue
                local_pts.append((ps.pose.position.x, ps.pose.position.y))

            if len(local_pts) < 3:
                continue

            # Contour LINE_STRIP
            outline = Marker()
            outline.header.frame_id = self.frame_id
            outline.header.stamp    = stamp
            outline.ns              = "obstacles_outline"
            outline.id              = island_id
            outline.type            = Marker.LINE_STRIP
            outline.action          = Marker.ADD
            outline.scale.x         = 5.0
            outline.color.r         = 1.0
            outline.color.g         = 0.0
            outline.color.b         = 0.0
            outline.color.a         = 1.0   
            outline.pose.orientation.w = 1.0
            for x, y in local_pts:
                p = Point(); p.x = x; p.y = y; p.z = 0.0
                outline.points.append(p)
            outline.points.append(outline.points[0])   # fermer
            ma.markers.append(outline)

        self.obstacle_pub.publish(ma)

    # ─────────────────────────────────────────────────────────────────────────
    # Avoidance WPs (orange, sphères)
    # ─────────────────────────────────────────────────────────────────────────
    def _publish_avoidance_markers(self, avoidance_wps: list):
        ma = MarkerArray()
        for i, wp in enumerate(avoidance_wps):
            m = Marker()
            m.header.frame_id = self.frame_id
            m.header.stamp    = self.get_clock().now().to_msg()
            m.ns = "avoidance_wps"
            m.id = i
            m.type = Marker.SPHERE
            m.action = Marker.ADD
            m.pose.position.x = float(wp['x'])
            m.pose.position.y = float(wp['y'])
            m.pose.position.z = 0.5
            m.scale.x = 3.0
            m.scale.y = 3.0
            m.scale.z = 1.0
            m.color.r = 1.0  # blanc
            m.color.g = 1.0
            m.color.b = 1.0
            m.color.a = 1.0

            t = Marker()
            t.header = m.header
            t.ns = "avoidance_labels"
            t.id = i + 1000
            t.type = Marker.TEXT_VIEW_FACING
            t.action = Marker.ADD
            t.pose.position.x = float(wp['x'])
            t.pose.position.y = float(wp['y'])
            t.pose.position.z = 2.0
            t.scale.z = 1.5
            t.color.r = 1.0
            t.color.g = 1.0
            t.color.b = 1.0
            t.color.a = 1.0
            t.text = f"AV{i+1}"
            ma.markers.append(m)
            ma.markers.append(t)

        self.viz_pub.publish(ma)

    # ─────────────────────────────────────────────────────────────────────────
    # RRT-Dubins : arbre (branches vertes + noeuds jaunes)
    # ─────────────────────────────────────────────────────────────────────────
    def _publish_rrt_tree(self, edges: list, nodes: list):
        """
        edges : list[list[[x,y]]]   — chaque élément = une branche Dubins
        nodes : list[[x, y, yaw]]   — chaque élément = un noeud de l'arbre
        """
        stamp = self.get_clock().now().to_msg()

        # ── 1. Branches (LINE_STRIPs verts) ───────────────────────────────────
        tree_ma = MarkerArray()
        # Supprime les anciens
        clear = Marker()
        clear.header.frame_id = self.frame_id
        clear.header.stamp    = stamp
        clear.ns              = "rrt_tree"
        clear.action          = Marker.DELETEALL
        tree_ma.markers.append(clear)
        self.rrt_dubins_tree_pub.publish(tree_ma)

        tree_ma2 = MarkerArray()
        for i, edge in enumerate(edges):
            if len(edge) < 2:
                continue
            m = Marker()
            m.header.frame_id = self.frame_id
            m.header.stamp    = stamp
            m.ns              = "rrt_tree"
            m.id              = i
            m.type            = Marker.LINE_STRIP
            m.action          = Marker.ADD
            m.scale.x         = 0.5          # épaisseur (m)
            m.color.r         = 0.0
            m.color.g         = 0.8
            m.color.b         = 0.0
            m.color.a         = 0.6
            m.pose.orientation.w = 1.0
            for pt in edge:
                p = Point()
                p.x = float(pt[0])
                p.y = float(pt[1])
                p.z = 0.0
                m.points.append(p)
            tree_ma2.markers.append(m)
        self.rrt_dubins_tree_pub.publish(tree_ma2)

        # ── 2. Nœuds (SPHEREs jaunes) ─────────────────────────────────────────
        nodes_ma = MarkerArray()
        clear_n = Marker()
        clear_n.header.frame_id = self.frame_id
        clear_n.header.stamp    = stamp
        clear_n.ns              = "rrt_nodes"
        clear_n.action          = Marker.DELETEALL
        nodes_ma.markers.append(clear_n)
        self.rrt_dubins_nodes_pub.publish(nodes_ma)

        nodes_ma2 = MarkerArray()
        for i, node in enumerate(nodes):
            m = Marker()
            m.header.frame_id = self.frame_id
            m.header.stamp    = stamp
            m.ns              = "rrt_nodes"
            m.id              = i
            m.type            = Marker.SPHERE
            m.action          = Marker.ADD
            m.scale.x         = 3.0
            m.scale.y         = 3.0
            m.scale.z         = 1.0
            m.color.r         = 1.0
            m.color.g         = 0.9
            m.color.b         = 0.0
            m.color.a         = 0.8
            m.pose.position.x  = float(node[0])
            m.pose.position.y  = float(node[1])
            m.pose.position.z  = 0.0
            m.pose.orientation.w = 1.0
            nodes_ma2.markers.append(m)
        self.rrt_dubins_nodes_pub.publish(nodes_ma2)

        self.get_logger().info(
            f"RViz Waypoints-Dubins: {len(edges)} branches, {len(nodes)} nodes published"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # RRT-Dubins : chemin final (nav_msgs/Path bleu)
    # ─────────────────────────────────────────────────────────────────────────
    def _publish_rrt_dubins_path(self, points: list):
        """
        points : list[[x, y, yaw]]  — chemin Dubins dense
        """
        path_msg = Path()
        path_msg.header.frame_id = self.frame_id
        path_msg.header.stamp    = self.get_clock().now().to_msg()
        for pt in points:
            ps = PoseStamped()
            ps.header          = path_msg.header
            ps.pose.position.x = float(pt[0])
            ps.pose.position.y = float(pt[1])
            ps.pose.position.z = 0.5   # légèrement au-dessus pour la visibilité
            if len(pt) >= 3:
                q = tf_transformations.quaternion_from_euler(0.0, 0.0, float(pt[2]))
                ps.pose.orientation.x = q[0]
                ps.pose.orientation.y = q[1]
                ps.pose.orientation.z = q[2]
                ps.pose.orientation.w = q[3]
            else:
                ps.pose.orientation.w = 1.0
            path_msg.poses.append(ps)
        self.rrt_dubins_path_pub.publish(path_msg)
        self.get_logger().info(
            f"RViz RRT-Dubins path: {len(points)} points publiés"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Odométrie → historique robot
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
                raw        = PoseStamped()
                raw.header = msg.header
                raw.pose   = msg.pose.pose
                ps         = do_transform_pose_stamped(raw, t)
            except Exception as e:
                self.get_logger().error(f"Odom TF failed: {e}")
                return

        self.robot_path_msg.poses.append(ps)
        self.robot_path_msg.header.stamp = self.get_clock().now().to_msg()
        self.path_pub.publish(self.robot_path_msg)

    # ─────────────────────────────────────────────────────────────────────────
    def publish_waypoints(self, waypoint_list):
        marker_array = MarkerArray()
        for i, pt in enumerate(waypoint_list):
            marker = Marker()
            marker.header.frame_id = self.frame_id
            marker.type   = Marker.SPHERE
            marker.action = Marker.ADD
            marker.id     = i
            marker.pose.position.x = pt[0]
            marker.pose.position.y = pt[1]
            marker.scale.x = 0.2
            marker.scale.y = 0.2
            marker.scale.z = 0.2
            marker.color.a = 1.0
            marker.color.r = 1.0
            marker.pose.orientation.w = 1.0
            marker_array.markers.append(marker)
        self.marker_pub.publish(marker_array)

    # ─────────────────────────────────────────────────────────────────────────
    # send_goal
    # ─────────────────────────────────────────────────────────────────────────
    def send_goal(self):
        self.get_logger().info("Wait for Action Server...")
        if not self._action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error("No server")
            return

        while not self._tf_buffer.can_transform(self.frame_id, 'utm', Time(seconds=0)):
            self.get_logger().info("Waiting for TF...")
            rclpy.spin_once(self, timeout_sec=0.5)
            
        self.publish_depth_obstacles(DEPTH_FILE) # AJOUT ICI
        self.publish_obstacles(ISLANDS_FILE)
        self.obstacle_timer.cancel()

        goal_msg = BaseAction.Goal()
        payload = {
            'speed': 'high',
            'waypoints': [
                {'latitude': 58.847663, 'longitude': 17.644616, 'tolerance': 7.0},
                {'latitude': 58.851386, 'longitude': 17.647441, 'tolerance': 7.0},
            ]
        }
        goal_msg.goal.data = json.dumps(payload)

        self.get_logger().info("Send mission...")
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback,
        )
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Mission rejected')
            return
        self.get_logger().info('Mission accepted')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    # ─────────────────────────────────────────────────────────────────────────
    # Feedback callback  ← point central des nouveautés
    # ─────────────────────────────────────────────────────────────────────────
    def feedback_callback(self, feedback_msg):
        try:
            data = json.loads(feedback_msg.feedback.feedback.data)

            # ── Waypoints goal (sphères vertes + labels) ──────────────────────
            if 'wps' in data:
                self.target_list = data['wps']
                self.publish_waypoints_markers()

            # ── Chemin Dubins final dense (nav_msgs/Path) ─────────────────────
            # Envoyé une seule fois juste après la planification
            if 'full_path' in data:
                self._publish_rrt_dubins_path(data['full_path'])
                # On republie aussi sur l'ancien topic pour compatibilité RViz
                path_msg = self._convert_list_to_path(data['full_path'])
                self.dubins_path_pub.publish(path_msg)

            # ── Arbre RRT-Dubins : branches vertes ────────────────────────────
            # Envoyé une seule fois juste après la planification
            if 'rrt_tree_edges' in data:
                edges = data['rrt_tree_edges']   # list[list[[x,y]]]
                nodes = data.get('rrt_tree_nodes', [])  # list[[x,y,yaw]]
                self._publish_rrt_tree(edges, nodes)
                self.get_logger().info(
                    f"Received RRT tree: {len(edges)} branches, {len(nodes)} nodes"
                )

            # ── Avoidance WPs legacy (sphères oranges) ────────────────────────
            if 'avoidance_wps' in data:
                self._publish_avoidance_markers(data['avoidance_wps'])
            
            if 'visibility_graph' in data:
                vg = data['visibility_graph']
                self._publish_visibility_graph(
                    vg.get('nodes', []),
                    vg.get('edges', []),
                    vg.get('island_contours', []),
                )

        except Exception as e:
            self.get_logger().error(f"Erreur feedback: {e}")

    # ─────────────────────────────────────────────────────────────────────────


    def _publish_visibility_graph(self, nodes: list, edges: list, island_contours: list = None):
        ma = MarkerArray()
        stamp = self.get_clock().now().to_msg()

        # ── Arêtes du graphe (très transparentes) ─────────────────────────
        edges_marker = Marker()
        edges_marker.header.frame_id    = self.frame_id
        edges_marker.header.stamp       = stamp
        edges_marker.ns                 = "visibility_edges"
        edges_marker.id                 = 0
        edges_marker.type               = Marker.LINE_LIST
        edges_marker.action             = Marker.ADD
        edges_marker.scale.x            = 0.3
        edges_marker.color.r            = 1.0
        edges_marker.color.g            = 1.0
        edges_marker.color.b            = 1.0
        edges_marker.color.a            = 0.12
        edges_marker.pose.orientation.w = 1.0
        for i, j in edges:
            ax, ay = nodes[i]
            bx, by = nodes[j]
            pa = Point(); pa.x = float(ax); pa.y = float(ay); pa.z = 0.0
            pb = Point(); pb.x = float(bx); pb.y = float(by); pb.z = 0.0
            edges_marker.points.append(pa)
            edges_marker.points.append(pb)
        ma.markers.append(edges_marker)

        # ── Contours offset par île ────────────────────────────────────────
        if island_contours:
            for isl_id, contour in enumerate(island_contours):
                if len(contour) < 2:
                    continue

                # Segments entre sommets (LINE_STRIP blanc)
                strip = Marker()
                strip.header.frame_id    = self.frame_id
                strip.header.stamp       = stamp
                strip.ns                 = "island_offsets"
                strip.id                 = 100 + isl_id
                strip.type               = Marker.LINE_STRIP
                strip.action             = Marker.ADD
                strip.scale.x            = 1.0
                strip.color.r            = 1.0
                strip.color.g            = 1.0
                strip.color.b            = 1.0
                strip.color.a            = 1.0
                strip.pose.orientation.w = 1.0
                for pt in contour:
                    p = Point(); p.x = float(pt[0]); p.y = float(pt[1]); p.z = 0.0
                    strip.points.append(p)
                strip.points.append(strip.points[0])  # fermer
                ma.markers.append(strip)

                # Sphères aux sommets (grosses, blanches)
                spheres = Marker()
                spheres.header.frame_id    = self.frame_id
                spheres.header.stamp       = stamp
                spheres.ns                 = "island_offset_nodes"
                spheres.id                 = 200 + isl_id
                spheres.type               = Marker.SPHERE_LIST
                spheres.action             = Marker.ADD
                spheres.scale.x            = 6.0
                spheres.scale.y            = 6.0
                spheres.scale.z            = 2.0
                spheres.color.r            = 1.0
                spheres.color.g            = 1.0
                spheres.color.b            = 1.0
                spheres.color.a            = 1.0
                spheres.pose.orientation.w = 1.0
                for pt in contour:
                    p = Point(); p.x = float(pt[0]); p.y = float(pt[1]); p.z = 0.0
                    spheres.points.append(p)
                ma.markers.append(spheres)

        self.visibility_graph_pub.publish(ma)
        self.get_logger().info(
            f"Visibility graph publié : {len(edges)} arêtes, "
            f"{len(island_contours) if island_contours else 0} contours île"
        )



    def publish_waypoints_markers(self):
        if not self.target_list:
            return

        ma = MarkerArray()
        for i, wp in enumerate(self.target_list):
            m = Marker()
            m.header.frame_id = self.frame_id
            m.header.stamp    = self.get_clock().now().to_msg()
            m.ns = "waypoints"; m.id = i
            m.type = Marker.SPHERE; m.action = Marker.ADD
            m.pose.position.x = float(wp['x'])
            m.pose.position.y = float(wp['y'])
            m.pose.position.z = 0.5
            m.scale.x = float(wp['tol']) * 2
            m.scale.y = float(wp['tol']) * 2
            m.scale.z = 1.0
            m.color.g = 1.0; m.color.a = 1.0
            m.pose.orientation.w = 1.0
            ma.markers.append(m)

            t = Marker()
            t.header = m.header
            t.ns = "waypoint_labels"; t.id = i + 1000
            t.type = Marker.TEXT_VIEW_FACING; t.action = Marker.ADD
            t.pose.position.x = m.pose.position.x
            t.pose.position.y = m.pose.position.y
            t.pose.position.z = 2.0
            t.scale.z = 1.5
            t.color.r = 1.0; t.color.g = 1.0; t.color.b = 1.0; t.color.a = 1.0
            t.text = f"WP{i + 1}"
            t.pose.orientation.w = 1.0
            ma.markers.append(t)

        self.viz_pub.publish(ma)

    # ─────────────────────────────────────────────────────────────────────────
    def _convert_list_to_path(self, points):
        """Transforme une liste [[x, y, yaw], ...] en nav_msgs/Path."""
        path_msg = Path()
        path_msg.header.frame_id = self.frame_id
        path_msg.header.stamp    = self.get_clock().now().to_msg()
        for pt in points:
            ps = PoseStamped()
            ps.header          = path_msg.header
            ps.pose.position.x = float(pt[0])
            ps.pose.position.y = float(pt[1])
            ps.pose.orientation.w = 1.0
            path_msg.poses.append(ps)
        return path_msg

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info("Final Result")
        rclpy.shutdown()


# ─────────────────────────────────────────────────────────────────────────────
def main(args=None):
    rclpy.init(args=args)
    client = EvoloMovePathClient()
    client.send_goal()
    rclpy.spin(client)


if __name__ == '__main__':
    main()