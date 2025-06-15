import json
import traceback

import numpy as np
import rclpy
from geodesy import utm
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import Pose, PointStamped, PoseStamped, Quaternion
from nav_msgs.msg import Odometry
from rclpy.action import CancelResponse, GoalResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node
from rclpy import logging
from rclpy.time import Duration, Time
from smarc_action_base.smarc_action_base import (
    ActionResult,
    ActionType,
    SMARCActionServer,
)
from smarc_mission_msgs.action import BaseAction
from smarc_msgs.msg import Topics
from tf2_geometry_msgs import do_transform_pose_stamped
from tf2_ros import Buffer, TransformException, TransformListener

from go_to_geopoint.action_parsing import ActionSubMsg as ActS
from go_to_geopoint.action_parsing import GeoActionParsing
from smarc_utilities.node_utils import typed_param_declare
from smarc_utilities.georef_utils import convert_latlon_to_utm

class RescuePointServer(SMARCActionServer):
    """Action point server that handles SAM recovery once it has been located.

    """

    def __init__(
        self,
        node: Node,
        action_name,
        action_type: ActionType,
    ):
        super().__init__(
            node,
            action_name,
            action_type,
            Topics.WARA_PS_ACTION_SERVER_HB_TOPIC,
        )
        self.logger = node.get_logger()
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(
            self._tf_buffer, self._node, spin_thread=True
        )
        self.declare_parameters()

        self.logger.set_level(logging.LoggingSeverity.INFO)
        self.wp_pub = self._node.create_publisher(PoseStamped, self._node.get_parameter("setpoint_topic").value, 10)
        self._json_ops: GeoActionParsing = GeoActionParsing() #TODO
        self.BASE_FRAME = self._node.get_parameter("robot_name").value + "/base_link"
        self.ODOM_FRAME = self._node.get_parameter("robot_name").value + "/odom"

        self._pub_setpoint = self._node.create_publisher(
            PoseStamped, self._node.get_parameter("setpoint_topic").value, 2
        )

        self.odom_topic = Topics.ODOM_TOPIC 

        self.sub_quad = self._node.create_subscription(
            Odometry, self.odom_topic, self.quad_cb, 10)

        self.initial_velocity                   = 5.0    # m/s for for calculating tau trajectory 
        self.tau_k                              = 0.4    # shape param k
        self.kd_alpha                           = 0.8    # α‐coupling exponent

    def declare_parameters(self):
        """Declares all of node's parameters in a single location."""
        node = self._node
        typed_param_declare(
            node,
            "robot_name",
            "Quadrotor",
            "The name of the robot being run; used for things like frame names"
        )

        typed_param_declare(
            node,
            "distance_frame",
            "base_link",
            "Frame for which the distance to target will be computed (usually base_link)",
        )

        typed_param_declare(
            node,
            "setpoint_tolerance",
            0.1,
            "Setpoint tolerance for when the goal is considered achieved (Euclidean norm).",
        )
        
        typed_param_declare(
            node,
            "setpoint_topic",
            "move_to_setpoint",
            "Topic to publish setpoint targets to. Will be prepended with 'robot_name'",
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
            "# number of tau‐law waypoints"
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

    @staticmethod
    def _str_posestamp(pose: PoseStamped):
        """Helper function to print PoseStamped Messages nicely."""
        return f"\nFrame: {pose.header.frame_id}\nPosition: {pose.pose.position}\nOrientation: {pose.pose.orientation}"
        
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

    def execution_callback(self, goal_handle: ServerGoalHandle) -> ActionResult:
        """Primary execution callback where goals are handled after acceptance.
           Sets initial values for recovery and starts timer attached to callback
           of the primary function.
        Args:
            goal_handle: handle to control server and add callbacks

        Returns:
            A populated ActionResult message
        """
        self.logger.info("Executing callback")
        self.logger.info(f"{goal_handle.request}")
        result_msg = self.action_type.Result

        self.pickup_traj_start_point    = None   # starting point of the pick up trajectory, it is in perpendicular plane to the target
        self.touchdown                  = None   # tau touchdown point
        self.reached_start              = False  # have we driven to pickup_traj_start_point?
        self.waypoints                  = []     # tau‐law trajectory waypoints
        self.step_index                 = 0      # index for tau waypoints
        self.target_index               = self._node.get_parameter("target_index_offset").value     # index for point the drone moves towards

        # --- FORWARD (flat) PHASE STATE ---
        self.forward_phase              = False  # have we switched to flat after tau?
        self.flat_direction             = None   # unit vector of horizontal motion

        # --- INCLINE PHASE STATE ---
        self.incline_phase              = False  # have we switched to incline?
        self.incline_direction          = None   # unit vector of incline motion


        self._node.rescue_timer = None
        self.incline_distance = None
        self.done = False

        self._node.rescue_timer = self._node.create_timer(self._node.get_parameter("dt").value, self.timer_callback) #TODO: Go through all get Params for string and value
        self._node.get_logger().info('Rescue Point Follower started.')

        status = self.feedback_loop(goal_handle) 
        if status == "cancelled":
            self.logger.info("Goal was cancelled by client.")
            result_msg.success = False
            goal_handle.abort()
            return result_msg

        if status == "invalid":
            self.logger.info("Goal was cancelled by client.")
            result_msg.success = False
            goal_handle.abort()
            return result_msg
        if(self._node.rescue_timer is not None):
            self._node.rescue_timer.cancel()
            self._node.rescue_timer = None
        result_msg.success = True
        goal_handle.succeed()
        return result_msg

    def goal_callback(self, goal_request: ActionType.Goal) -> GoalResponse:
        """Considers a goal validity and evaluates whether it should be accepted or not.
           A goal is refused if either the two provided points for the buoy and SAM are 
           too far apart from eachother or if SAM is too far from the drone.
        Args:
            goal_request (ActionType.Goal): Goal message

        Returns:
            response: Either GoalResponse.Accept or GoalResponse.Reject

        """
        goal_json = json.loads(goal_request.goal.data)  # Assuming goal is std_msgs/String
        self.SAM_pose_utm = None
        self.buoy_pose_utm = None
        self.SAM_pose_odom = None
        self.SAM_pose_odom_array = None
        self.buoy_pose_odom = None
        rope_points = []
        for pt in goal_json["rope_points"]:
            gp = GeoPoint(
                latitude = float(pt["latitude"]),
                longitude = float(pt["longitude"]),
                altitude = float(pt["altitude"])
            )
            rope_points.append(gp)
        # e.g. if you expect exactly two:
        geopoint_SAM, geopoint_buoy = rope_points

        # now pull the offset out of the same dict
        self.min_height_above_water = float(goal_json["min_height_above_water"])
        self.swoop_vertical = float(goal_json["swoop_vertical"])
        self.swoop_horizontal = float(goal_json["swoop_horizontal"])
        self.straight_before_rope = float(goal_json["straight_before_rope"])
        self.straight_distance = float(goal_json["straight_distance"])
        self.raise_horizontal = float(goal_json["raise_horizontal"])
        self.raise_vertical = float(goal_json["raise_vertical"])


            
        self.logger.info(f"Received geopoint at {geopoint_SAM} for SAM")
        self.logger.info(f"Received geopoint at {geopoint_buoy} for buoy")
        self.logger.info(f"Received min_height_above_water: {self.min_height_above_water}")
        self.logger.info(f"Received swoop_vertical: {self.swoop_vertical}")
        self.logger.info(f"Received swoop_horizontal: {self.swoop_horizontal}")
        self.logger.info(f"Received straight_before_rope: {self.straight_before_rope}")
        self.logger.info(f"Received straight_distance: {self.straight_distance}")
        self.logger.info(f"Received raise_horizontal: {self.raise_horizontal}")
        self.logger.info(f"Received raise_vertical: {self.raise_vertical}")


        SAM_pose_utm = convert_latlon_to_utm(geopoint_SAM)
        buoy_pose_utm = convert_latlon_to_utm(geopoint_buoy)

  


        try:
            self.SAM_pose_posestamped = self.point_to_pose(SAM_pose_utm)
            self.SAM_pose_odom = self.transform_goal(self.SAM_pose_posestamped, self.ODOM_FRAME)
            self.SAM_pose_odom_array = np.array([self.SAM_pose_odom.pose.position.x, self.SAM_pose_odom.pose.position.y, self.SAM_pose_odom.pose.position.z])
            self.buoy_pose_posestamped = self.point_to_pose(buoy_pose_utm)
            self.logger.info(
                f"Buoy in utm is {self._str_posestamp(self.buoy_pose_posestamped)}"
            )
            self.buoy_pose_odom = self.transform_goal(self.buoy_pose_posestamped, self.ODOM_FRAME)
            self.buoy_pose_odom_array = np.array([self.buoy_pose_odom.pose.position.x, self.buoy_pose_odom.pose.position.y, self.buoy_pose_odom.pose.position.z])



            self.logger.info(
                f"SAM in {self.ODOM_FRAME} is {self._str_posestamp(self.SAM_pose_odom)}"
            )
            self.logger.info(
                f"Buoy in {self.ODOM_FRAME} is {self._str_posestamp(self.buoy_pose_odom)}"
            )
            self.logger.info(
                f"Quad in {self.ODOM_FRAME} is {self._str_posestamp(self.quad_pose_stamped)}"
            )

        except TransformException as err:
            self.logger.error(
                f"Failed to transform goal target frame {self.ODOM_FRAME}.\n\t Tf2 exception error {err}"
            )
            return GoalResponse.REJECT  
        



        try:
            dist = self.compute_distance(self.SAM_pose_odom, self.buoy_pose_odom)
        except TransformException as err:
            err_str = "Could not successfully compute distance!. Rejecting goal!\n"
            exec_up = TransformException(err_str)
            exec_up.__cause__ = err
            # Adding error message to traceback for debug log.
            self.logger.info(err_str)
            self.logger.debug(traceback.format_exc())
            return GoalResponse.REJECT

        if dist >= self._node.get_parameter("width_goal_threshold").value:
            err_str = f"Rejecting goal due to violating distance threshold. Criteria: {dist:.1f} >= {self.width_goal_threshold:.1f}"
            self.logger.info(err_str)
            return GoalResponse.REJECT

        try:
            dist = self.compute_distance(self.SAM_pose_odom, self.quad_pose_stamped)
        except TransformException as err:
            err_str = "Could not successfully compute distance!. Rejecting goal!\n"
            exec_up = TransformException(err_str)
            exec_up.__cause__ = err
            # Adding error message to traceback for debug log.
            self.logger.info(err_str)
            self.logger.debug(traceback.format_exc())
            return GoalResponse.REJECT

        if dist >= self._node.get_parameter("dist_goal_threshold").value:
            err_str = f'Rejecting goal due to violating distance threshold. Criteria: {dist:.1f} >= {self._node.get_parameter("dist_goal_threshold").value:.1f}'
            self.logger.info(err_str)
            return GoalResponse.REJECT
        

        # Accepts as all criteria fulfilled
        self.logger.info("Accepting Goal")
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle: ServerGoalHandle) -> CancelResponse:
        """Handles canceling of goal requests.

        Args:
            goal_handle: handle

        Returns:
            Cancel response as ACCEPT
        """
        self.logger.info("Received Cancel Request")
        if(self._node.rescue_timer is not None):
            self._node.rescue_timer.cancel()
            self._node.rescue_timer = None
        return CancelResponse.ACCEPT

    def feedback_loop(self, goal_handle: ServerGoalHandle):
        """Abstracted feedback loop where tolerance checks are conducted.

        Args:
            pose_stamped: target location
            goal_handle: passed in to enable feedback publishing
        """
        rate = self._node.create_rate(10)
        feedback = self.action_type.Feedback

        while not self.done:
            if goal_handle.is_cancel_requested:
                self.logger.info("Goal was cancelled by client.")
                goal_handle.canceled()
                return "cancelled"
            if not self.is_valid_goal:
                return "invalid"
            rate.sleep()

        rate.destroy()
        return "done"

    def quad_cb(self, msg: Odometry):
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

    
    def compute_distance(self, pose1 : PoseStamped, pose2 : PoseStamped) -> float:
        #Computes the distance between two points given as stamepd poses 
        if(pose1.header.frame_id != pose2.header.frame_id):
            try:
                pose2 = self.transform_goal(pose2, pose1.header.frame_id)
            except Exception as e:
                self.log(f"Failed to transform pose2 from {pose2.header.frame_id} to {pose1.header.frame_id}: {e}")
                return
        dist = np.sqrt((pose1.pose.position.x - pose2.pose.position.x) ** 2 + (pose1.pose.position.y - pose2.pose.position.y) ** 2 + (pose1.pose.position.z - pose2.pose.position.z) ** 2)
        return dist

    def timer_callback(self):
        """
        Periodic function triggered by ROS timer:
        1. Waits until both SAM and quad poses are available.
        2. On first run, computes the perpendicular start and touchdown points.
        3. Phase 1: Fly to Start Point: drives the drone to pickup_traj_start_point (starting point for the tau trajectory) at fly_to_start_point_velocity.
           Once within tau_trajectory_starting_threshold, precomputes tau‐law waypoints.
        4. Phase 2: publishes tau‐law trajectory waypoints.
           If within straight_before_rope of SAM, switches to flat phase.
        5. Phase 3: Flat Phase: moves straight ahead with flat_forward_velocity, keeping height constant, until straight_distance reached.
        6. Phase 4: Incline fly out Phase: after flat, ascends at 45° in same horizontal direction with flat_forward_velocity, for incline_distance.
        7. Shuts down the node when the incline phase is completed.
        """
        # 1. Ensure both poses have been received
        if self.SAM_pose_odom_array is None:
            self._node.get_logger().warning('Waiting for both SAM odom...')
            return
        if self.quad_pose is None: 
            self._node.get_logger().warning('Waiting for Quad odom...')
            return
        
        self.logger.info(
            f"SAM in {self.ODOM_FRAME} is {self._str_posestamp(self.SAM_pose_odom)}"
        )
        self.logger.info(
            f"Buoy in {self.ODOM_FRAME} is {self._str_posestamp(self.buoy_pose_odom)}"
        )
        self.logger.info(
            f"Quad in {self.ODOM_FRAME} is {self._str_posestamp(self.quad_pose_stamped)}"
        )


        # 2. Compute pickup_traj_start_point & touchdown once
        if self.pickup_traj_start_point is None:
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

            self._node.get_logger().info(
                f'Using start pos {self.pickup_traj_start_point} → touchdown pos {self.touchdown}'
            )

        # 3. Phase 1: Fly to Start Point to move the drone to pickup_traj_start_point
        if not self.reached_start:
            vec = self.pickup_traj_start_point - self.quad_pose


            dist = np.linalg.norm(vec)
            if dist <= self._node.get_parameter("tau_trajectory_starting_threshold").value:
                # Arrived at start location
                self.reached_start = True
                # Precompute tau‐law trajectory from start to touchdown
                self.waypoints = self._generate_tau_trajectory(self.pickup_traj_start_point, self.touchdown)
                self._node.get_logger().info(
                    f'Reached start. Computed {len(self.waypoints)} tau‐law waypoints.')
            else:
                # Step toward the start point at fly_to_start_point_velocity

                pose_msg = PoseStamped()
                pose_msg.header.stamp = self._node.get_clock().now().to_msg()
                pose_msg.header.frame_id = 'odom'
                pose_msg.pose.position.x = float(self.pickup_traj_start_point[0])
                pose_msg.pose.position.y = float(self.pickup_traj_start_point[1])
                pose_msg.pose.position.z = float(self.pickup_traj_start_point[2])
                self.wp_pub.publish(pose_msg)

                self._node.get_logger().info(f'Moving to start: {dist:.2f} m remaining')
            return

        # 4. Phase 2: publish tau‐law trajectory or switch to flat phase
        if not self.forward_phase and self.step_index < len(self.waypoints):
            current_pos = self.quad_pose
            target_pos = self.waypoints[self.target_index]
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

                self._node.get_logger().info(
                    f'Within {self.straight_before_rope} m of SAM — switching to flat phase, ')
            else:
                # continue tau trajectory
                target_distance = np.linalg.norm(target_pos - current_pos)
                next_distance = np.linalg.norm(next_pos - current_pos)
                if(next_distance < self._node.get_parameter("setpoint_tolerance").value):
                    self.step_index += 1
                    self.target_index += 1
                elif(target_distance < self._node.get_parameter("setpoint_tolerance").value):
                    self.step_index += self._node.get_parameter("target_index_offset").value
                    self.target_index += self._node.get_parameter("target_index_offset").value
                

                pose_msg = PoseStamped()
                pose_msg.header.stamp = self._node.get_clock().now().to_msg()
                pose_msg.header.frame_id = 'odom'
                pose_msg.pose.position.x = float(target_pos[0])
                pose_msg.pose.position.y = float(target_pos[1])
                pose_msg.pose.position.z = float(target_pos[2])
                self.wp_pub.publish(pose_msg)

                # self._node.get_logger().info(
                #     f'Published waypoint {self.step_index+1}/{len(self.waypoints)}: {self.target_index}')
                # self._node.get_logger().info(
                #     f'target distance: {target_distance} next distance: {next_distance}')
            return

        # 5. Phase 3: Flat Phase: move straight ahead at constant flat_forward_velocity
        if self.forward_phase and not self.incline_phase and self.straight_distance > self._node.get_parameter("setpoint_tolerance").value:
            
            self.straight_distance = np.linalg.norm(self.quad_pose - self.flat_final)


            pose_msg = PoseStamped()
            pose_msg.header.stamp = self._node.get_clock().now().to_msg()
            pose_msg.header.frame_id = 'odom'
            pose_msg.pose.position.x = float(self.flat_final[0])
            pose_msg.pose.position.y = float(self.flat_final[1])
            pose_msg.pose.position.z = float(self.flat_final[2])
            self.wp_pub.publish(pose_msg)

            self._node.get_logger().info(
                f'Flat phase: Distance Remaining {self.straight_distance:.2f} m Waiting for {self._node.get_parameter("setpoint_tolerance").value:.2f} m')
            return

        # 6. Phase 4: Incline Phase: ascend at 45° with flat_forward_velocity
        if self.forward_phase and not self.incline_phase:
            # initialize incline direction once
            vec3D = np.array([self.flat_direction[0]*self.raise_horizontal, self.flat_direction[1]*self.raise_horizontal, self.raise_vertical]) 
            self.incline_final = self.quad_pose + vec3D
            self.incline_distance = np.linalg.norm(self.quad_pose - self.incline_final)
            self.incline_phase     = True
            self._node.get_logger().info('Starting incline phase at 45°')

        if self.incline_phase and self.incline_distance > self._node.get_parameter("setpoint_tolerance").value:
            self.incline_distance = np.linalg.norm(self.quad_pose - self.incline_final)

            pose_msg = PoseStamped()
            pose_msg.header.stamp = self._node.get_clock().now().to_msg()
            pose_msg.header.frame_id = 'odom'
            pose_msg.pose.position.x = float(self.incline_final[0])
            pose_msg.pose.position.y = float(self.incline_final[1])
            pose_msg.pose.position.z = float(self.incline_final[2])
            self.wp_pub.publish(pose_msg)

            self._node.get_logger().info(
                f'Incline Phase: Distance Remaining {self.incline_distance:.2f} m Waiting for {self._node.get_parameter("setpoint_tolerance").value:.2f} m')
            return

        # 7. All done
        self._node.get_logger().info('All phases completed. Shutting down node.')
        self.done = True
        
    
    def _generate_tau_trajectory(self, p0, p_td):
        """
        Generate a tau‐law curved trajectory from p0 to p_td.
        Returns an array of shape (num_steps, 3).
        """
        self.num_steps = self._node.get_parameter("num_steps").value
        delta = p0 - p_td
        d0 = np.linalg.norm(delta)
        if d0 < 1e-6:
            return np.tile(p_td, (self.num_steps,1))

        # horizontal unit direction in XY plane
        dir_xy = delta[:2] / np.linalg.norm(delta[:2])
        # initial pitch angle α₀ between vertical and d₀
        alpha0 = np.arcsin((p0[2] - p_td[2]) / d0)

        # tau‐law parameters
        tau0 = -d0 / self.initial_velocity
        t_d  = -tau0 / self.tau_k
        inv_k  = 1.0 / self.tau_k
        inv_kd = 1.0 / self.kd_alpha
        traj = np.zeros((self.num_steps,3))
        for i in range(self.num_steps):
            t = t_d * i / (self.num_steps - 1)
            d = d0 * (1.0 - t/t_d)**inv_k

            # α‐coupling
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


def main(args=None):
    try:
        rclpy.init(args=args)
        node_name = "rescue_point_server"
        node = Node(node_name)
        action_type = ActionType(BaseAction)
        setpoint = RescuePointServer(node, "alars_recover", action_type)
        executor = MultiThreadedExecutor()
        executor.add_node(node)
        executor.spin()
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == "__main__":
    main()
