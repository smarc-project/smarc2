import time
import numpy as np
import signal
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from floatsam_controllers.floatsam_common import FloatSam


import py_trees
import py_trees_ros
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped, TransformStamped
from geographic_msgs.msg import GeoPoint
from smarc_msgs.msg import FloatStamped
from tf2_geometry_msgs import do_transform_pose_stamped
from .behaviours import (
    HaveGoal,
    HungarianAssignment,
    ArrivalCheck,
    MoveToClient,
    AllArrivalCheck,
    LoiterWithHeadingClient
)
from smarc_action_base.gentler_action_server import GentlerActionServer

class BTActionServer(Node):
    def __init__(self):
        super().__init__('go_to_formation_rvo_bt_action_server')

        self.declare_parameter('robot_name', 'floatsam_usv_0')
        self.this_robot_name = self.get_parameter('robot_name').value
        self.robot_base_name = '_'.join(self.this_robot_name.split('_')[:-1])

        self.declare_parameter('use_sim', True)
        self.use_sim = self.get_parameter('use_sim').value
        self._floatsam = FloatSam(self, self.this_robot_name, use_sim=self.use_sim)

        self.declare_parameter('num_robots', 3)
        num_robots = self.get_parameter('num_robots').value
        self.robot_ids = list(range(num_robots))

        self.declare_parameter('max_velocity', 2.0)  
        self.max_velocity = self.get_parameter('max_velocity').value

        self.declare_parameter('last_point_tolerance_move_path', 0.5)
        self.last_point_tolerance_move_path = self.get_parameter('last_point_tolerance_move_path').value
        
        self.get_logger().info(f'Robot "{self.this_robot_name}" managing {len(self.robot_ids)} robots (base: "{self.robot_base_name}", IDs: {self.robot_ids})')
        
        self._setup_blackboard()
        
        self._odom_subscribers = {}
        self._loiter_subscribers = {}
        self._setup_odometry_subscriptions()
        self._setup_loiter_subscriptions()

        self._as = GentlerActionServer(
            self,
            "go_to_formation_rvo",
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency=10  
        )

        self.tree = None

    def _setup_loiter_subscriptions(self):
        """Subscribe to loiter heading feedback topic for each robot."""
        for robot_id in self.robot_ids:
            loiter_topic = f'/{self.robot_base_name}_{robot_id}/loiter_heading_fb'
            
            subscriber = self.create_subscription(
                FloatStamped,
                loiter_topic,
                lambda msg, rid=robot_id: self._loiter_callback(msg, rid),
                10
            )
            
            self._loiter_subscribers[robot_id] = subscriber
            self.get_logger().info(f'Subscribed to {loiter_topic}')
    
    def _loiter_callback(self, msg: FloatStamped, robot_id: int):
        """Update loiter heading feedback in blackboard when received.
        
        The loiter_heading_fb value is either 1.0 (heading to loiter point)
        or 0.0 (not heading to loiter point). This is stored in the blackboard
        keyed by robot name, similar to robot positions.
        """
        blackboard = py_trees.blackboard.Client(name="Server")
        blackboard.register_key(key="loiter_heading_fb", access=py_trees.common.Access.WRITE)
        
        loiter_fb = blackboard.loiter_heading_fb
        loiter_fb[f'{self.robot_base_name}_{robot_id}'] = msg.data
        blackboard.loiter_heading_fb = loiter_fb


    def _setup_blackboard(self):
        """Initialize blackboard with robot positions and assignments dictionaries."""
        blackboard = py_trees.blackboard.Client(name="Server")
        blackboard.register_key(key="robot_positions", access=py_trees.common.Access.WRITE)
        blackboard.register_key(key="robot_assignments", access=py_trees.common.Access.WRITE)
        blackboard.register_key(key="this_robot_name", access=py_trees.common.Access.WRITE)
        blackboard.register_key(key="formation_points", access=py_trees.common.Access.WRITE)
        blackboard.register_key(key="formation_points_latlon", access=py_trees.common.Access.WRITE)
        blackboard.register_key(key="last_point_tolerance_move_path", access=py_trees.common.Access.WRITE)
        blackboard.register_key(key="loiter_heading_fb", access=py_trees.common.Access.WRITE)
        blackboard.register_key(key="max_velocity", access=py_trees.common.Access.WRITE)
        
        blackboard.robot_positions = {}
        blackboard.robot_assignments = {}
        blackboard.formation_points={}
        blackboard.this_robot_name = self.this_robot_name  
        blackboard.formation_points_latlon = {}
        blackboard.last_point_tolerance_move_path = self.last_point_tolerance_move_path
        blackboard.loiter_heading_fb = {}
        blackboard.max_velocity = self.max_velocity
        
        for robot_id in self.robot_ids:
            blackboard.robot_positions[f'{self.robot_base_name}_{robot_id}'] = None
            blackboard.loiter_heading_fb[f'{self.robot_base_name}_{robot_id}'] = None
        
        self.get_logger().info('Blackboard initialized with robot_positions and robot_assignments')

    def _setup_odometry_subscriptions(self):
        """Subscribe to odometry topic for each robot."""
        for robot_id in self.robot_ids:
            odom_topic = f'/{self.robot_base_name}_{robot_id}/smarc/odom'
            
            subscriber = self.create_subscription(
                Odometry,
                odom_topic,
                lambda msg, rid=robot_id: self._odom_callback(msg, rid),
                10
            )
            
            self._odom_subscribers[robot_id] = subscriber
            self.get_logger().info(f'Subscribed to {odom_topic}')

    def _odom_callback(self, msg: Odometry, robot_id: int):
        """Update robot position in blackboard, explicitly casting to the GLOBAL shared map."""
        robot_name = f'{self.robot_base_name}_{robot_id}'
        
        pose_in_odom = PoseStamped()
        pose_in_odom.header = msg.header
        pose_in_odom.pose = msg.pose.pose

        try:
            # 100% LIVE LOOKUP to the GLOBAL Map. No caches.
            # Sim: unity_origin -> unity_origin (Identity TF, resolves instantly)
            # Real: robot_X/odom -> map (Traverses the Master/Slave TF tree)
            odom_to_global_tf = self._floatsam._tf_buffer.lookup_transform(
                self._floatsam.GLOBAL_MAP_FRAME,  
                msg.header.frame_id,       
                rclpy.time.Time()          
            )
        except Exception as e:
            # If TF fails, the tree isn't ready (e.g. waiting for RTK lock). 
            # We safely return and try again next tick.
            self.get_logger().warn(
                f"[{robot_name}] Waiting for TF: {msg.header.frame_id} -> {self._floatsam.GLOBAL_MAP_FRAME}",
                throttle_duration_sec=2.0
            )
            return

        # Apply the transform
        try:
            pose_in_global = do_transform_pose_stamped(pose_in_odom, odom_to_global_tf)
        except Exception as e:
            self.get_logger().error(f"Error transforming odom for robot {robot_id}: {e}")
            return

        # Update the Blackboard
        blackboard = py_trees.blackboard.Client(name="Server")
        blackboard.register_key(key="robot_positions", access=py_trees.common.Access.WRITE)
        
        positions = blackboard.robot_positions
        positions[robot_name] = pose_in_global
        blackboard.robot_positions = positions


    def create_behavior_tree(self):
        root = py_trees.composites.Sequence(name="MainTree", memory=False)

        selector_1 = py_trees.composites.Selector(name="FirstSelector", memory=False)
        have_goal_check = HaveGoal(name="HaveGoal")
        hungarian_assignment = HungarianAssignment(name="HungarianAssignment")  
        selector_1.add_children([have_goal_check, hungarian_assignment])
        
        sequence_3 = py_trees.composites.Sequence(name="SecondSequence", memory=False)
        selector_3_1_1 = py_trees.composites.Selector(name="FifthSelector", memory=False)
        arrival_check = ArrivalCheck(name="ArrivalCheck")
        move_to_client = MoveToClient(name="MoveToClient")
        selector_3_1_1.add_children([arrival_check, move_to_client])
        selector_3_1_2 = py_trees.composites.Selector(name="SixthSelector", memory=False)
        all_arrival_check = AllArrivalCheck(name="AllArrivalCheck")
        loiter_with_heading_client = LoiterWithHeadingClient(name="LoiterWithHeadingClient")
        selector_3_1_2.add_children([all_arrival_check, loiter_with_heading_client])
        sequence_3.add_children([selector_3_1_1, selector_3_1_2])

        root.add_children([selector_1, sequence_3])

        tree = py_trees_ros.trees.BehaviourTree(root)
        
        _original_signal = signal.signal
        def _safe_signal(signum, handler):
            try:
                return _original_signal(signum, handler)
            except ValueError:
                pass  
        signal.signal = _safe_signal
        try:
            tree.setup(node=self, timeout=15.0)
        finally:
            signal.signal = _original_signal
        return tree

    def _on_goal_received(self, goal_request: dict) -> bool:
        """
        Parse and validate the formation goal.
        
        Expected format:
        {
            'formation_points': [
                {'latitude': float, 'longitude': float, 'heading': float},
                {'latitude': float, 'longitude': float, 'heading': float},
                ...
            ]
        }
        
        heading: orientation in degrees (0-360)
        """
        self.get_logger().info(f'Goal received: {goal_request}')
    

        try:
            formation_points = goal_request.get('formation_points', None)
            
            
            if formation_points is None:
                self.get_logger().error("Missing 'formation_points' in goal request")
                return False
            
            if not isinstance(formation_points, list):
                self.get_logger().error("'formation_points' must be a list")
                return False
            
            if len(formation_points) == 0:
                self.get_logger().error("'formation_points' list is empty")
                return False
            
            for i, point in enumerate(formation_points):
                if not isinstance(point, dict):
                    self.get_logger().error(f"Point {i} is not a dictionary")
                    return False
                
                required_fields = ['latitude', 'longitude', 'heading']
                for field in required_fields:
                    if field not in point:
                        self.get_logger().error(f"Point {i} missing required field: '{field}'")
                        return False
                
                lat = float(point['latitude'])
                if lat < -90 or lat > 90:
                    self.get_logger().error(f"Point {i}: Invalid latitude {lat} (must be -90 to 90)")
                    return False
                
                lon = float(point['longitude'])
                if lon < -180 or lon > 180:
                    self.get_logger().error(f"Point {i}: Invalid longitude {lon} (must be -180 to 180)")
                    return False
                
                heading = float(point['heading'])
                if heading < 0 or heading > 360:
                    self.get_logger().error(f"Point {i}: Invalid heading {heading} (must be 0 to 360 degrees)")
                    return False
            
            self.get_logger().info(f"Validated {len(formation_points)} formation points")
            
            blackboard = py_trees.blackboard.Client(name="ActionServer")
            blackboard.register_key(key="formation_points", access=py_trees.common.Access.WRITE)
            blackboard.register_key(key="formation_points_latlon", access=py_trees.common.Access.WRITE)
            new_formation_points = {}
            new_formation_points_latlon = {}
            for i, pt in enumerate(formation_points):
                gp = GeoPoint(latitude=float(pt['latitude']), longitude=float(pt['longitude']), altitude=0.0)
                pose = self._floatsam.convert_geopoint_to_map_pose_stamped(gp)
                pt = [pose.pose.position.x, pose.pose.position.y]
                new_formation_points[f'goal_{i}'] = pt
                new_formation_points_latlon[f'goal_{i}'] = {
                    'latitude': float(formation_points[i]['latitude']),
                    'longitude': float(formation_points[i]['longitude']),
                    'heading': float(formation_points[i]['heading'])
                }

            blackboard.formation_points = new_formation_points
            blackboard.formation_points_latlon = new_formation_points_latlon

            return True  
            
        except Exception as e:
            self.get_logger().error(f"Failed to parse goal: {e}")
            return False

    def _on_cancel_received(self) -> bool:
        """Handle cancellation."""
        self.get_logger().info('Goal canceled')
        return True

    def _check_all_robots_have_positions(self, timeout_seconds=5.0) -> bool:
        """
        Check if all robots have valid position data.
        Waits up to timeout_seconds for positions to arrive.
        
        Returns:
            True if all robots have positions, False otherwise
        """
        blackboard = py_trees.blackboard.Client(name="Server")
        blackboard.register_key(key="robot_positions", access=py_trees.common.Access.READ)
        
        start_time = time.time()
        
        while (time.time() - start_time) < timeout_seconds:
            robot_positions = blackboard.robot_positions
            
            missing_robots = [rid for rid, pos in robot_positions.items() if pos is None]
            
            if len(missing_robots) == 0:
                self.get_logger().info(f'All {len(robot_positions)} robots have valid positions')
                return True
            
            self.get_logger().info(
                f'Waiting for positions from robots: {missing_robots} '
                f'({len(missing_robots)}/{len(robot_positions)} missing)'
            )
            time.sleep(0.5)
        
        robot_positions = blackboard.robot_positions
        missing_robots = [rid for rid, pos in robot_positions.items() if pos is None]
        
        if len(missing_robots) > 0:
            self.get_logger().error(
                f'Timeout: Missing position data for robots: {missing_robots}. '
                f'Cannot proceed with formation goal.'
            )
            return False
        
        return True

    def _prepare_loop(self) -> None:
        """Create the tree once before loop starts."""
        self.get_logger().info('Building behavior tree...')
        
        if not self._check_all_robots_have_positions():
            self.get_logger().error('Cannot build behavior tree: missing robot positions')
            self.tree = None  
            return
        
        self.tree = self.create_behavior_tree()
        self.get_logger().info('Behavior tree created successfully')

    def _loop_inner(self) -> bool | None:
        """
        Called at loop_frequency.
        Tick tree once per call.

        Returns:
            True = SUCCESS (goal completed)
            False = FAILURE (goal failed)
            None = RUNNING (keep going)
        """
        if self.tree is None:
            self.get_logger().error('Behavior tree was not created - aborting goal')
            return False  
        
        self.tree.tick()

        if self.tree.root.status == py_trees.common.Status.SUCCESS:
            self.get_logger().info('Go To Formation Behavior tree SUCCEDED!')
            return True  
        elif self.tree.root.status == py_trees.common.Status.FAILURE:
            self.get_logger().warning('Go To Formation Behavior tree FAILED!')
            return False  
        else:
            return None

    def _give_feedback(self) -> str:
        """Return feedback string for the action client."""
        if self.tree:
            return f"Tree status: {self.tree.root.status}"
        return "Tree not initialized"


def main(args=None):
    rclpy.init(args=args)
    action_server = BTActionServer()
    executor = MultiThreadedExecutor()
    rclpy.spin(action_server, executor=executor)
    action_server.destroy()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

