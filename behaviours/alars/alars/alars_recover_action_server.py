#!/usr/bin/python

import rclpy
from rclpy.node import Node
from rclpy.time import Duration, Time
from rclpy.executors import MultiThreadedExecutor

import traceback
import numpy as np

from geometry_msgs.msg import PointStamped, PoseStamped, Quaternion
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PointStamped
from std_msgs.msg import Float32
from nav_msgs.msg import Odometry


from tf2_geometry_msgs import do_transform_pose_stamped
from tf2_ros import Buffer, TransformListener

from smarc_action_base.gentler_action_server import GentlerActionServer

from smarc_utilities.georef_utils import convert_latlon_to_utm
from smarc_utilities.node_utils import typed_param_declare

from dji_msgs.msg import Topics as DJITopics
from dji_msgs.msg import Links as DJILinks
from smarc_msgs.msg import Topics as SmarcTopics

class RecoverAction():
    def __init__(self,
                 node: Node):
        self._node : Node = node

        self._declare_parameters()
        self._read_parameters()
        self._robot_name : str = self._node.get_parameter('robot_name').get_parameter_value().string_value

        self.wp_pub = self._node.create_publisher(PoseStamped, DJITopics.MOVE_TO_SETPOINT_TOPIC, 10)

        self.BASE_FRAME = self._robot_name + '/' + DJILinks.BASE_LINK
        self.ODOM_FRAME = self._robot_name + '/' + DJILinks.ODOM

        self._node.create_subscription(Odometry, SmarcTopics.ODOM_TOPIC, self._odom_cb, 10)

        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self._node, spin_thread=True)

        self._as = GentlerActionServer(
            node,
            "alars_recover",
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency = 10
        )

        self.initial_velocity: float = 5.0      # m/s for calculating tau trajectory
        self.tau_k: float = 0.4                 # shape param k
        self.kd_alpha: float = 0.8              # α-coupling exponent

    def _loginfo(self, msg: str):
        self._node.get_logger().info(f"[RecoverAction] {msg}")

    def _on_goal_received(self, goal_request: dict) -> bool:
        try:
            geopoint_SAM = GeoPoint()
            geopoint_SAM.latitude = goal_request['object_position']['latitude']
            geopoint_SAM.longitude = goal_request['object_position']['longitude']
            geopoint_SAM.altitude = goal_request['object_position']['altitude']

            geopoint_buoy = GeoPoint()
            geopoint_buoy.latitude = goal_request['buoy_position']['latitude']
            geopoint_buoy.longitude = goal_request['buoy_position']['longitude']
            geopoint_buoy.altitude = goal_request['buoy_position']['altitude']

            self.min_height_above_water = float(goal_request["min_height_above_water"])
            self.swoop_vertical = float(goal_request["swoop_vertical"])
            self.swoop_horizontal = float(goal_request["swoop_horizontal"])
            self.straight_before_rope = float(goal_request["straight_before_rope"])
            self.straight_distance = float(goal_request["straight_distance"])
            self.raise_horizontal = float(goal_request["raise_horizontal"])
            self.raise_vertical = float(goal_request["raise_vertical"])
        except KeyError:
            self._loginfo(f"Goal request is missing a required field, received:\n {goal_request}")
            return False

        try:
            SAM_pose_utm = convert_latlon_to_utm(geopoint_SAM)
            buoy_pose_utm = convert_latlon_to_utm(geopoint_buoy)
        except:
            self._loginfo(f"Failed to convert geopoint to UTM, received:\n SAM: {geopoint_SAM}\n Buoy: {geopoint_buoy}")
            return False
        
        try:
            self.SAM_pose_posestamped = self.point_to_pose(SAM_pose_utm)
            self.SAM_pose_odom = self.transform_goal(self.SAM_pose_posestamped, self.ODOM_FRAME)
            self.SAM_pose_odom_array = np.array([self.SAM_pose_odom.pose.position.x, self.SAM_pose_odom.pose.position.y, self.SAM_pose_odom.pose.position.z])
            self.buoy_pose_posestamped = self.point_to_pose(buoy_pose_utm)
            self._loginfo(f"Buoy in utm is {self._str_posestamp(self.buoy_pose_posestamped)}")
            self.buoy_pose_odom = self.transform_goal(self.buoy_pose_posestamped, self.ODOM_FRAME)
            self.buoy_pose_odom_array = np.array([self.buoy_pose_odom.pose.position.x, self.buoy_pose_odom.pose.position.y, self.buoy_pose_odom.pose.position.z])
            self._loginfo(f"SAM in {self.ODOM_FRAME} is {self._str_posestamp(self.SAM_pose_odom)}")
            self._loginfo(f"Buoy in {self.ODOM_FRAME} is {self._str_posestamp(self.buoy_pose_odom)}")
            self._loginfo(f"Quad in {self.ODOM_FRAME} is {self._str_posestamp(self.quad_pose_stamped)}")
        except:
            self._loginfo(f"Failed to transform goal target frame {self.ODOM_FRAME}. Check TF tree.")
            return False

        try:
            dist = self.compute_distance(self.SAM_pose_odom, self.buoy_pose_odom)
        except:
            self._loginfo("Could not successfully compute distance between sam and buoy in odom frame. Rejecting goal!\n")
            return False
                
        if dist >= self.width_goal_threshold:
            self._loginfo(f"Rejecting goal due to violating distance threshold. Criteria: {dist:.1f} >= {self.width_goal_threshold:.1f}")
            return False

        try:
            dist = self.compute_distance(self.SAM_pose_odom, self.quad_pose_stamped)
            if dist >= self.dist_goal_threshold:
                err_str = f'Rejecting goal due to violating distance threshold. Criteria: {dist:.1f} >= {self.dist_goal_threshold:.1f}'
                self._loginfo(err_str)
                return False
        except:
            self._loginfo("Could not successfully compute distance between sam and quad in odom frame. Rejecting goal!\n")
            return False
        
        # Accepts as all criteria fulfilled
        self._loginfo(f"Accepting Goal: {goal_request}")
        return True


    def _on_cancel_received(self) -> bool:
        self._loginfo("Cancelled!")
        return True


    def _prepare_loop(self) -> None:
        self._read_parameters()

        self.pickup_traj_start_point    = None   # starting point of the pick up trajectory, it is in perpendicular plane to the target
        self.touchdown                  = None   # tau touchdown point
        self.reached_start              = False  # have we driven to pickup_traj_start_point?
        self.waypoints                  = []     # tau-law trajectory waypoints
        self.step_index                 = 0      # index for tau waypoints
        self.target_index               = self.target_index_offset # index for point the drone moves towards

        # --- FORWARD (flat) PHASE STATE ---
        self.forward_phase              = False  # have we switched to flat after tau?
        self.flat_direction             = None   # unit vector of horizontal motion

        # --- INCLINE PHASE STATE ---
        self.incline_phase              = False  # have we switched to incline?
        self.incline_direction          = None   # unit vector of incline motion
        self.incline_distance           = None

        # Initialize target positions if not given by the user
        self.target_pos_A = self.SAM_pose_odom_array
        self.target_pos_B = self.buoy_pose_odom_array

        # 1) Midpoint of target A (sam head) and target B (buoy) in 3D
        mid3D = (self.target_pos_A + self.target_pos_B) / 2.0
        mid3D[2] = 0 #TODO? This is a little messy, but is a way to potentially avoid embaressing failures

        # 2) Compute 2D perp direction (on x–y plane)
        delta = self.target_pos_B[:2] - self.target_pos_A[:2]
        perp = np.array([-delta[1], delta[0]])
        perp /= np.linalg.norm(perp)

        # 3) Offset midpoint by horizontal_distance_from_target & swoop_vertical
        start2D = mid3D[:2] + perp * self.swoop_horizontal
        self.pickup_traj_start_point = np.array([
            start2D[0],
            start2D[1],
            mid3D[2] + self.swoop_vertical
        ])

        self.touchdown = mid3D + np.array([0.0, 0.0, self.min_height_above_water])

        self._loginfo(f'Using start pos {self.pickup_traj_start_point} → touchdown pos {self.touchdown}')


    def _loop_inner(self) -> bool|None:
        """
        Periodic function triggered by ROS timer:
        1. Waits until both SAM and quad poses are available.
        2. On first run, computes the perpendicular start and touchdown points.
        3. Phase 1: Fly to Start Point: drives the drone to pickup_traj_start_point (starting point for the tau trajectory) at fly_to_start_point_velocity.
           Once within tau_trajectory_starting_threshold, precomputes tau-law waypoints.
        4. Phase 2: publishes tau-law trajectory waypoints.
           If within straight_before_rope of SAM, switches to flat phase.
        5. Phase 3: Flat Phase: moves straight ahead with flat_forward_velocity, keeping height constant, until straight_distance reached.
        6. Phase 4: Incline fly out Phase: after flat, ascends at 45° in same horizontal direction with flat_forward_velocity, for incline_distance.
        7. Shuts down the node when the incline phase is completed.
        """
        # 1. Ensure both poses have been received
        if self.SAM_pose_odom_array is None:
            self._loginfo('Waiting for both SAM odom...')
            return None
        if self.quad_pose is None: 
            self._loginfo('Waiting for Quad odom...')
            return None
        
        s = "\nRunning...:"
        s += f"\n  SAM: {self._str_posestamp(self.SAM_pose_odom)}"
        s += f"\n  Buoy: {self._str_posestamp(self.buoy_pose_odom)}"
        s += f"\n  Quad: {self._str_posestamp(self.quad_pose_stamped)}"
        s += f"\n  State: {self._give_feedback()}"

        # 2 is in _prepare_loop

        # 3. Phase 1: Fly to Start Point to move the drone to pickup_traj_start_point
        if not self.reached_start:
            vec = self.pickup_traj_start_point - self.quad_pose

            dist = np.linalg.norm(vec)
            if dist <= self._node.get_parameter("tau_trajectory_starting_threshold").value:
                # Arrived at start location
                self.reached_start = True
                # Precompute tau-law trajectory from start to touchdown
                self.waypoints = self._generate_tau_trajectory(self.pickup_traj_start_point, self.touchdown)
                s += f'\n >> Reached start. Computed {len(self.waypoints)} tau-law waypoints.'
            else:
                # Step toward the start point at fly_to_start_point_velocity
                if self.pickup_traj_start_point is None:
                    self._loginfo(f'pickup_traj_start_point is {self.pickup_traj_start_point}, Failing')
                    return False
                pose_msg = PoseStamped()
                pose_msg.header.stamp = self._node.get_clock().now().to_msg()
                pose_msg.header.frame_id = self.ODOM_FRAME;
                pose_msg.pose.position.x = float(self.pickup_traj_start_point[0])
                pose_msg.pose.position.y = float(self.pickup_traj_start_point[1])
                pose_msg.pose.position.z = float(self.pickup_traj_start_point[2])
                self.wp_pub.publish(pose_msg)

                s += f'\n >> Moving to start: {dist:.2f} m remaining'

            self._loginfo(s)
            return None

        # 4. Phase 2: publish tau-law trajectory or switch to flat phase
        if not self.forward_phase and self.step_index < len(self.waypoints):
            current_pos = self.quad_pose
            target_pos = self.waypoints[self.target_index_offset]
            next_pos = self.waypoints[self.step_index + 1]
            final_pos   = self.waypoints[-1]
            dist_to_sam = np.linalg.norm(current_pos - final_pos)
            if dist_to_sam <= self.straight_before_rope:
                # switch to flat phase
                self.forward_phase = True
                flat_vec = self.waypoints[-1] - self.waypoints[-2]
                flat_vec[2] = 0.0
                self.flat_direction = flat_vec / np.linalg.norm(flat_vec)
                self.flat_final = current_pos + self.flat_direction * self.straight_distance

                s += f'\n >> Within {self.straight_before_rope} m of SAM — switching to flat phase'
            else:
                # continue tau trajectory
                target_distance = np.linalg.norm(target_pos - current_pos)
                next_distance = np.linalg.norm(next_pos - current_pos)
                if next_distance < self.setpoint_tolerance:
                    self.step_index += 1
                    self.target_index += 1
                elif target_distance < self.setpoint_tolerance:
                    self.step_index += self.target_index_offset
                    self.target_index += self.target_index_offset

                pose_msg = PoseStamped()
                pose_msg.header.stamp = self._node.get_clock().now().to_msg()
                pose_msg.header.frame_id = self.ODOM_FRAME
                pose_msg.pose.position.x = float(target_pos[0])
                pose_msg.pose.position.y = float(target_pos[1])
                pose_msg.pose.position.z = float(target_pos[2])
                self.wp_pub.publish(pose_msg)
                s += f'\n >> Tau phase: Distance to target {target_distance:.2f} m step_index: {self.step_index}, target_index: {self.target_index}'
            
            self._loginfo(s)
            return None

        # 5. Phase 3: Flat Phase: move straight ahead at constant flat_forward_velocity
        if self.forward_phase and not self.incline_phase and self.straight_distance > self.setpoint_tolerance:
            
            self.straight_distance = np.linalg.norm(self.quad_pose - self.flat_final)


            pose_msg = PoseStamped()
            pose_msg.header.stamp = self._node.get_clock().now().to_msg()
            pose_msg.header.frame_id = self.ODOM_FRAME
            pose_msg.pose.position.x = float(self.flat_final[0])
            pose_msg.pose.position.y = float(self.flat_final[1])
            pose_msg.pose.position.z = float(self.flat_final[2])
            self.wp_pub.publish(pose_msg)

            s += f'\n >> Flat phase: Distance Remaining {self.straight_distance:.2f} m Waiting for {self.setpoint_tolerance:.2f} m'
            self._loginfo(s)
            return None

        # 6. Phase 4: Incline Phase: ascend at 45° with flat_forward_velocity
        if self.forward_phase and not self.incline_phase:
            if self.flat_direction is None:
                self._loginfo('flat_direction is None, failing')
                return False
            
            # initialize incline direction once
            vec3D = np.array([self.flat_direction[0]*self.raise_horizontal, self.flat_direction[1]*self.raise_horizontal, self.raise_vertical]) 
            self.incline_final = self.quad_pose + vec3D
            self.incline_distance = np.linalg.norm(self.quad_pose - self.incline_final)
            self.incline_phase     = True
            self._loginfo('Starting incline phase at 45°')
        
        if self.incline_distance is None:
            self._loginfo('incline_distance is None, failing')
            return False
        
        if self.incline_phase and self.incline_distance > self.setpoint_tolerance:
            self.incline_distance = np.linalg.norm(self.quad_pose - self.incline_final)

            pose_msg = PoseStamped()
            pose_msg.header.stamp = self._node.get_clock().now().to_msg()
            pose_msg.header.frame_id = self.ODOM_FRAME
            pose_msg.pose.position.x = float(self.incline_final[0])
            pose_msg.pose.position.y = float(self.incline_final[1])
            pose_msg.pose.position.z = float(self.incline_final[2])
            self.wp_pub.publish(pose_msg)

            s += f'\n >> Incline Phase: Distance Remaining {self.incline_distance:.2f} m Waiting for {self.setpoint_tolerance:.2f} m'
            self._loginfo(s)
            return None

        # 7. All done
        self._loginfo('All phases completed. Action success.')
        return True


    def _give_feedback(self) -> str:
        s = f"Reached start:{self.reached_start}, forward phase:{self.forward_phase}, incline phase:{self.incline_phase}"
        return s

    @staticmethod
    def _str_posestamp(pose: PoseStamped):
        """Helper function to print PoseStamped Messages nicely."""
        pos = pose.pose.position
        return (f"Pos:[{pos.x:.2f},{pos.y:.2f},{pos.z:.2f}] in {pose.header.frame_id}")
        

    def _odom_cb(self, msg: Odometry):
        """
        Callback for quadrotor odometry updates:
        - Extracts position from Odometry message.
        - Stores as numpy array in self.quad_pose.
        """
        
        self.quad_pose_stamped = PoseStamped()
        self.quad_pose_stamped.header = msg.header
        self.quad_pose_stamped.pose = msg.pose.pose
        self.quad_pose_stamped = self.transform_goal(self.quad_pose_stamped, self.ODOM_FRAME)
        p = self.quad_pose_stamped.pose.position
        self.quad_pose = np.array([p.x, p.y, p.z])
        self._node.get_logger().debug(f'Received quad pose: {self.quad_pose}')

    def point_to_pose(self, ps_in: PointStamped) -> PoseStamped:
        ps = PoseStamped()
        ps.header = ps_in.header
        ps.pose.position = ps_in.point
        ps.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
        return ps

    def transform_goal(
        self,
        pose_stamped: PoseStamped,
        target: str,
    ) -> PoseStamped:
        """Provides transformed point from pose_stamped.header.frame_id to target.

        Raises:
            TransformException when transformation fails allowing for caller to handle exception

        Returns:
            PoseStamped in specified frame
        """
        t = self._tf_buffer.lookup_transform(
            target_frame=target,
            source_frame=pose_stamped.header.frame_id,
            time=Time(seconds=0),
            timeout=Duration(seconds=1),
        )
        return do_transform_pose_stamped(pose_stamped, t)

    
    def compute_distance(self, pose1 : PoseStamped, pose2 : PoseStamped) -> float:
        #Computes the distance between two points given as stamepd poses 
        if(pose1.header.frame_id != pose2.header.frame_id):
            try:
                pose2 = self.transform_goal(pose2, pose1.header.frame_id)
            except Exception as e:
                self._loginfo(f"Failed to transform pose2 from {pose2.header.frame_id} to {pose1.header.frame_id}: {e}")
                return -1
        dist = np.sqrt((pose1.pose.position.x - pose2.pose.position.x) ** 2 + (pose1.pose.position.y - pose2.pose.position.y) ** 2 + (pose1.pose.position.z - pose2.pose.position.z) ** 2)
        return dist


    def _generate_tau_trajectory(self, p0, p_td):
        """
        Generate a tau-law curved trajectory from p0 to p_td.
        Returns an array of shape (num_steps, 3).
        """
        delta = p0 - p_td
        d0 = np.linalg.norm(delta)
        if d0 < 1e-6:
            return np.tile(p_td, (self.num_steps,1))

        # horizontal unit direction in XY plane
        dir_xy = delta[:2] / np.linalg.norm(delta[:2])
        # initial pitch angle α₀ between vertical and d₀
        alpha0 = np.arcsin((p0[2] - p_td[2]) / d0)

        # tau-law parameters
        tau0 = -d0 / self.initial_velocity
        t_d  = -tau0 / self.tau_k
        inv_k  = 1.0 / self.tau_k
        inv_kd = 1.0 / self.kd_alpha
        traj = np.zeros((self.num_steps,3))
        for i in range(self.num_steps):
            t = t_d * i / (self.num_steps - 1)
            d = d0 * (1.0 - t/t_d)**inv_k

            # α-coupling
            alpha = alpha0 * (d / d0)**inv_kd
            cosA, sinA = np.cos(alpha), np.sin(alpha)

            # horizontal reach & vertical rise
            h = d * cosA
            z = d * sinA

            # build curved point
            traj[i,0] = p_td[0] + dir_xy[0] * h
            traj[i,1] = p_td[1] + dir_xy[1] * h
            traj[i,2] = p_td[2] + z
 
        return traj

    def _declare_parameters(self):
        """Declares all of node's parameters in a single location."""
        node = self._node
        typed_param_declare(
            node,
            "robot_name",
            "M350",
            "The name of the robot being run; used for things like frame names"
        )

        typed_param_declare(
            node,
            "setpoint_tolerance",
            0.1,
            "Setpoint tolerance for when the goal is considered achieved (Euclidean norm).",
        )
        

        typed_param_declare(
            node,
            "dt",
            .05,
            "# time interval [s] between waypoint publishes",
        )

        typed_param_declare(
            node,
            "num_steps",
            400,
            "# number of tau-law waypoints"
        )

        typed_param_declare(
            node,
            "width_goal_threshold",
            10.0,
            "Distance threshold in meters where a goal should be rejected if the given points are too far apart. (Euclidean Norm)",
        )

        typed_param_declare(
            node,
            "dist_goal_threshold",
            1000.0,
            "Distance threshold in meters where a goal should be rejected if the SAM is too far from the drone. (Euclidean Norm)",
        )


        typed_param_declare( #TODO: Make goal, and make a height
            node,
            "incline_angle_degrees",
            30,
            "Angle (in degrees) that the drone ascends along during recovery",
        )

        typed_param_declare(
            node,
            "target_index_offset",
            5,
            "Number of steps in t by which the drone tracking leads the current position",
        )

        typed_param_declare( #TODO: Not urgent, combine with general threshold
            node,
            "tau_trajectory_starting_threshold",
            .2,
            "m to consider “arrived” at starting point of tau-trajectory",
        )


    def _read_parameters(self):
        self.setpoint_tolerance = self._node.get_parameter("setpoint_tolerance").get_parameter_value().double_value
        self.dt = self._node.get_parameter("dt").get_parameter_value().double_value
        self.num_steps = self._node.get_parameter("num_steps").get_parameter_value().integer_value
        self.width_goal_threshold = self._node.get_parameter("width_goal_threshold").get_parameter_value().double_value
        self.dist_goal_threshold = self._node.get_parameter("dist_goal_threshold").get_parameter_value().double_value
        self.incline_angle_degrees = self._node.get_parameter("incline_angle_degrees").get_parameter_value().double_value
        self.target_index_offset = self._node.get_parameter("target_index_offset").get_parameter_value().integer_value
        self.tau_trajectory_starting_threshold = self._node.get_parameter("tau_trajectory_starting_threshold").get_parameter_value().double_value


def main(args=None):
    rclpy.init(args=args)
    node = Node("alars_recover_action_server")
    RecoverAction(node)
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()
    node.destroy_node()
    rclpy.shutdown()

