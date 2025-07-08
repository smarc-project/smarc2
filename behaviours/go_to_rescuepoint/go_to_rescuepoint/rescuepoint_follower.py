#!/usr/bin/env python3
import rclpy
import numpy as np
import math 
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry


class WaypointFollower(Node):
    def __init__(self):
        """
        Node initialization:
        - Sets up parameters for waypoint generation and publishing rate.
        - Initializes state variables for SAM, Buoy and quad poses, trajectory waypoints, and step counters.
        - Creates ROS subscriptions for SAM and quad odometry.
        - Creates a publisher for sending waypoint setpoints.
        - Starts a timer to trigger waypoint publishing at fixed intervals.
        """
        super().__init__('waypoint_follower')
        
        ###  PARAMETERS "NEEDED" TO BE CHANGED WHILE DEPLOYING IN THE REAL DRONE  ###
        self.target_pos_A                       = None  # REPLACE WITH SAM Head POSITION 
        self.target_pos_B                       = None  # REPLACE WITH BUOY POSITION
        self.num_steps                          = 400   # number of tau‐law waypoints (less waypoints between drone and target-> more speed)
        self.dt                                 = 0.05  # time interval [s] between waypoint publishes (higher dt -> less speed)
        self.fly_to_start_point_velocity        = 15.0  # m/s to go from drone's current position to the starting point of the approach trajectory 
        self.vertical_height_offset             = 0.3   # CHANGE WHILE GROUND TESTING, final vertical offset [m] above the water surface, clearance height, 
        self.rope_proximity_threshold           = 1.0   # m to consider “close to rope" to start the FLAT APPROACH
        self.flat_forward_distance              = 4.0   # m to go forward horizontally to catch the rope
        self.flat_forward_velocity              = 1.0   # m/s horizontal constant flat-forward velocity
        self.horizontal_distance_from_target    = -10.0 # m horizontally how far from the  rope you want to start the pick up approach 
        self.vertical_distance_from_target      = 7.0   # m vertically how far from the  rope you want to start the pick up approach 
        self.incline_distance                   = 10.0  # m to ascend along incline direction after picking up the sam
        self.incline_angle_degree               = 30    # deg to ascend along incline direction after picking up the sam


        ###  PARAMETERS "MIGHT NEEDED" TO BE CHANGED WHILE DEPLOYING IN THE REAL DRONE  ###
        self.tau_trajectory_starting_threshold  = 0.2   # m to consider “arrived” at starting point of tau-trajectory
        
        ###  PARAMETERS "NOT NEEDED" TO BE CHANGED WHILE DEPLOYING IN THE REAL DRONE  ###
        self.initial_velocity                   = 5.0    # m/s for for calculating tau trajectory 
        self.tau_k                              = 0.4    # shape param k
        self.kd_alpha                           = 0.8    # α‐coupling exponent
        self.flat_base_point                    = None   # anchor point for flat phase start

        
        # PARAMETERS FOR INCLINE PHASE
        
        
        # STATE
        self.sam_pose                   = None   # latest SAM position [x,y,z]
        self.quad_pose                  = None   # latest quadrotor position [x,y,z]
        self.pickup_traj_start_point    = None   # starting point of the pick up trajectory, it is in perpendicular plane to the target
        self.touchdown                  = None   # tau touchdown point
        self.reached_start              = False  # have we driven to pickup_traj_start_point?
        self.waypoints                  = []     # tau‐law trajectory waypoints
        self.step_index                 = 0      # index for tau waypoints

        # --- FORWARD (flat) PHASE STATE ---
        self.forward_phase              = False  # have we switched to flat after tau?
        self.flat_direction             = None   # unit vector of horizontal motion
        self.flat_traveled              = 0.0    # distance traveled in flat phase

        # --- INCLINE PHASE STATE ---
        self.incline_phase              = False  # have we switched to incline?
        self.incline_direction          = None   # unit vector of incline motion
        self.incline_traveled           = 0.0    # distance traveled along incline

        # Subscribers for SAM and quad odometry
        self.sub_sam  = self.create_subscription(
            Odometry, '/sam_auv_v1/core/odom_gt', self.sam_cb, 10)
        self.sub_quad = self.create_subscription(
            Odometry, '/Quadrotor/odom_gt',    self.quad_cb, 10)

        # Publisher for waypoint setpoints
        self.wp_pub = self.create_publisher(PoseStamped, '/setpoint_position', 10)
        
        # Timer to call timer_callback at rate 1/dt
        self.timer = self.create_timer(self.dt, self.timer_callback)
        self.get_logger().info('WaypointFollower started.')


    def _generate_tau_trajectory(self, p0, p_td):
        """
        Generate a tau‐law curved trajectory from p0 to p_td.
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

    def sam_cb(self, msg: Odometry):
        """
        Callback for SAM odometry updates:
        - Extracts position from Odometry message.
        - Stores as numpy array in self.sam_pose.
        """
        p = msg.pose.pose.position
        self.sam_pose = np.array([p.x, p.y, p.z])
        self.get_logger().debug(f'Received SAM pose: {self.sam_pose}')

    def quad_cb(self, msg: Odometry):
        """
        Callback for quadrotor odometry updates:
        - Extracts position from Odometry message.
        - Stores as numpy array in self.quad_pose.
        """
        p = msg.pose.pose.position
        self.quad_pose = np.array([p.x, p.y, p.z])
        self.get_logger().debug(f'Received quad pose: {self.quad_pose}')

    def timer_callback(self):
        """
        Periodic function triggered by ROS timer:
        1. Waits until both SAM and quad poses are available.
        2. On first run, computes the perpendicular start and touchdown points.
        3. Phase 1: Fly to Start Point: drives the drone to pickup_traj_start_point (starting point for the tau trajectory) at fly_to_start_point_velocity.
           Once within tau_trajectory_starting_threshold, precomputes tau‐law waypoints.
        4. Phase 2: publishes tau‐law trajectory waypoints.
           If within rope_proximity_threshold of SAM, switches to flat phase.
        5. Phase 3: Flat Phase: moves straight ahead with flat_forward_velocity, keeping height constant, until flat_forward_distance reached.
        6. Phase 4: Incline fly out Phase: after flat, ascends at 45° in same horizontal direction with flat_forward_velocity, for incline_distance.
        7. Shuts down the node when the incline phase is completed.
        """
        # 1. Ensure both poses have been received
        if self.sam_pose is None or self.quad_pose is None:
            self.get_logger().warning('Waiting for both SAM and quad odometry...')
            return

        # 2. Compute pickup_traj_start_point & touchdown once
        if self.pickup_traj_start_point is None:

            # Initialize target positions if not given by the user
            if self.target_pos_A is None or self.target_pos_B is None:
                self.target_pos_A = self.sam_pose
                self.target_pos_B = self.target_pos_A + np.array([0.0, 1.6, 0.0])
                self.get_logger().warning('SAM head and Buoy Position not given. Using predefined SAM head and Buoy Position...')

            # 1) Midpoint of target A (sam head) and target B (buoy) in 3D
            mid3D = (self.target_pos_A + self.target_pos_B) / 2.0

            # 2) Compute 2D perp direction (on x–y plane)
            delta = self.target_pos_B[:2] - self.target_pos_A[:2]
            perp = np.array([-delta[1], delta[0]])
            perp /= np.linalg.norm(perp)

            # 3) Offset midpoint by horizontal_distance_from_target & vertical_distance_from_target
            start2D = mid3D[:2] + perp * self.horizontal_distance_from_target
            self.pickup_traj_start_point   = np.array([start2D[0], start2D[1], mid3D[2] + self.vertical_distance_from_target]) # starting point of the tau trajectory 
            self.touchdown = mid3D + np.array([0.0, 0.0, self.vertical_height_offset])

            self.get_logger().info(
                f'Using start pos {self.pickup_traj_start_point} → touchdown pos {self.touchdown}'
            )

        # 3. Phase 1: Fly to Start Point to move the drone to pickup_traj_start_point
        if not self.reached_start:
            vec = self.pickup_traj_start_point - self.quad_pose
            dist = np.linalg.norm(vec)
            if dist <= self.tau_trajectory_starting_threshold:
                # Arrived at start location
                self.reached_start = True
                # Precompute tau‐law trajectory from start to touchdown
                self.waypoints = self._generate_tau_trajectory(self.pickup_traj_start_point, self.touchdown)
                self.get_logger().info(
                    f'Reached start. Computed {len(self.waypoints)} tau‐law waypoints.')
            else:
                # Step toward the start point at fly_to_start_point_velocity
                step_len = self.fly_to_start_point_velocity * self.dt
                direction = vec / dist
                next_pt = self.quad_pose + direction * min(step_len, dist)

                pose_msg = PoseStamped()
                pose_msg.header.stamp = self.get_clock().now().to_msg()
                pose_msg.header.frame_id = 'map'
                pose_msg.pose.position.x = float(next_pt[0])
                pose_msg.pose.position.y = float(next_pt[1])
                pose_msg.pose.position.z = float(next_pt[2])
                self.wp_pub.publish(pose_msg)

                self.get_logger().info(f'Moving to start: {dist:.2f} m remaining')
            return

        # 4. Phase 2: publish tau‐law trajectory or switch to flat phase
        if not self.forward_phase and self.step_index < len(self.waypoints):
            current_pos = self.waypoints[self.step_index]
            final_pos   = self.waypoints[-1]
            dist_to_sam = np.linalg.norm(current_pos - final_pos)
            if dist_to_sam <= self.rope_proximity_threshold:
                # switch to flat phase
                self.forward_phase = True
                prev = self.waypoints[max(0, self.step_index-1)]
                flat_vec = current_pos - prev
                flat_vec[2] = 0.0
                self.flat_direction = flat_vec / np.linalg.norm(flat_vec)
                self.flat_traveled  = 0.0
                self.flat_base_point = current_pos.copy()  # <- anchor for flat & incline phase


                self.get_logger().info(
                    f'Within {self.rope_proximity_threshold} m of SAM — switching to flat phase, '
                    f'flat_forward_velocity={self.flat_forward_velocity} m/s')
            else:
                # continue tau trajectory
                pose_msg = PoseStamped()
                pose_msg.header.stamp = self.get_clock().now().to_msg()
                pose_msg.header.frame_id = 'map'
                pose_msg.pose.position.x = float(current_pos[0])
                pose_msg.pose.position.y = float(current_pos[1])
                pose_msg.pose.position.z = float(current_pos[2])
                self.wp_pub.publish(pose_msg)

                self.get_logger().info(
                    f'Published waypoint {self.step_index+1}/{len(self.waypoints)}: {current_pos}')
                self.step_index += 1
            return

        # 5. Phase 3: Flat Phase: move straight ahead at constant flat_forward_velocity
        if self.forward_phase and not self.incline_phase and self.flat_traveled < self.flat_forward_distance:
            step_len = self.flat_forward_velocity * self.dt
            next_pt = self.flat_base_point + self.flat_direction * self.flat_traveled
            self.flat_traveled += step_len


            pose_msg = PoseStamped()
            pose_msg.header.stamp = self.get_clock().now().to_msg()
            pose_msg.header.frame_id = 'map'
            pose_msg.pose.position.x = float(next_pt[0])
            pose_msg.pose.position.y = float(next_pt[1])
            pose_msg.pose.position.z = float(next_pt[2])
            self.wp_pub.publish(pose_msg)

            self.get_logger().info(
                f'Flat phase: traveled {self.flat_traveled:.2f}/{self.flat_forward_distance} m')
            return

        # 6. Phase 4: Incline Phase: ascend at 45° with flat_forward_velocity
        if self.forward_phase and not self.incline_phase:
            # initialize incline direction once
            incline_angle_rad = math.radians(self.incline_angle_degree) 
            h = math.cos(incline_angle_rad)
            v = math.sin(incline_angle_rad)
            vec3D = np.array([self.flat_direction[0]*h, self.flat_direction[1]*h, v]) 
            self.incline_direction = vec3D / np.linalg.norm(vec3D)
            self.incline_traveled  = 0.0
            self.incline_phase     = True
            self.get_logger().info('Starting incline phase at 45°')

        if self.incline_phase and self.incline_traveled < self.incline_distance:
            step_len = self.flat_forward_velocity * self.dt
            start_point = self.flat_base_point + self.flat_direction * self.flat_forward_distance
            next_pt = start_point + self.incline_direction * self.incline_traveled
            self.incline_traveled += step_len

            pose_msg = PoseStamped()
            pose_msg.header.stamp = self.get_clock().now().to_msg()
            pose_msg.header.frame_id = 'map'
            pose_msg.pose.position.x = float(next_pt[0])
            pose_msg.pose.position.y = float(next_pt[1])
            pose_msg.pose.position.z = float(next_pt[2])
            self.wp_pub.publish(pose_msg)

            self.get_logger().info(
                f'Incline Phase: travelled {self.incline_traveled:.2f}/{self.incline_distance} m')
            return

        # 7. All done
        self.get_logger().info('All phases completed. Shutting down node.')
        rclpy.shutdown()


def main(args=None):
    """
    Entry point for the waypoint follower node:
    - Initializes the ROS client library.
    - Creates the WaypointFollower node instance.
    - Spins to process callbacks until shutdown.
    """
    rclpy.init(args=args)
    node = WaypointFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()


if __name__ == '__main__':
    main()
