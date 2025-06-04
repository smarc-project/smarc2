#!/usr/bin/python
##############################################################################
# Overview
##############################################################################

"""
This script contains three path planners classes and the SearchPlanner class, which manages the initial drone movement and the 
actual search planner algorithm). The initial drone movement is to be done if one wants to test the search planner and it just moves
the drone away from the initial position, which is very close from SAM.

Path planners:
    Spiral: the drone moves to the GPS ping and starts a spiral movement. Its radius increases over time and its center moves according
            to SAM position. This planner doesn't use the probabilistic grid map.
    AStar: "pseudo-obstacles" are created based on the probabilistic grid map: cells with small probability will be randomly chosen to define
            line obstacles. The objective is to give priority to paths that pass through cells with higher probability. After defining the
            obstacles, the regular astar algorithm is run
    Greedy: it defines the waypoint as the cell with highest probability.
    Artificial Potential Field: cells exert repulsive and attractive forces and the displacement vector is aligned with this force.
"""
##############################################################################
##############################################################################


import sys
import rclpy
from rclpy.node import Node
from abc import ABC, abstractmethod
from geometry_msgs.msg import PointStamped, Pose, PoseStamped
from nav_msgs.msg import Odometry, Path
from sensor_msgs.msg import BatteryState
from geographic_msgs.msg import GeoPoint
import tf2_ros
import tf2_geometry_msgs
from tf2_ros import Buffer, TransformListener
import numpy as np
from math import cos, sin, pi, sqrt, tan, factorial, dist
from .Astar import AStar

class InitializeActions(Node):
    """
    This class is instatiated in SIM to teleport SAM and create a pseudo GPS ping (SAM postion + noise)
     Args: 
        name: ros node name
        params: dictionary with all relevant parameters for search planning. They can be changed in the launch file

    Attributes (the relevant ones):
        sam_pos: position (x,y) from odometry
        gps_ping: GeoPoint msg from the GPS. #TODO: use this instead of adding noise directly to sam_pos


    Notes:
        This class should only be useful in SIM. In real life, the GPS measurement needs to be passed as argument to different objects in the 
        SearchPlannerController class (search_planner_controller.py).

    """
    def __init__(self, name = 'init_actions', params = None):
        super().__init__(name)

        self.sam_pos = None
        self.drone_position = None
        self.gps_ping = None

        if params:
            self.drone_init_pos = np.array(params["drone.init_pos"]) 
            self.sam_init_pos = params["sam.init_pos"]
            self.sam_pos_var= params["sam.initial_state.pos_variance"]
            self.flight_height= params["flight_height"]
        else:
            self.get_logger().error("No valid parameters received in SearchPlanner node")

        self.teleport_sam_publisher = self.create_publisher(
            msg_type = PoseStamped,
            topic = '/sam_auv_v1/teleport',
            qos_profile= 10)
        
        self.sam_odom_callback = self.create_subscription(
            msg_type = Odometry,
            callback= self.sam_odom_callback,
            topic = '/sam_auv_v1/smarc/odom',
            qos_profile= 10)
        self.gps_ping_geo = self.create_subscription(
            msg_type = GeoPoint,
            callback= self.gps_ping_geo_callback,
            topic = '/sam_auv_v1/smarc/latlon',
            qos_profile= 10)
        self.drone_pos_sub = self.create_subscription(
            msg_type = Odometry,
            topic = '/Quadrotor/odom_gt',
            callback = self.drone_odom_callback,
            qos_profile= 10)
        

        
    def teleport_sam(self):
        """
        Method to teleport SAM at the beginning of the simulation. The goal position is defined in the launch file and it's
        in SAM's odom frame.
        """
        msg = PoseStamped()
        msg.header.frame_id = 'sam_auv_v1/odom_gt'
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.pose.position.x =  self.sam_init_pos[0]
        msg.pose.position.y =  self.sam_init_pos[1]
        self.get_logger().info('Teleporting SAM ...')
        self.teleport_sam_publisher.publish(msg)

    def get_quadrotor_position(self):
        """ Returns initial quadrotor position in map_gt"""
        # if self.drone_position is not None:
        #     self.drone_pos_sub.destroy()
        return self.drone_position
        

    def get_GPSxy_ping(self) -> np.array :
        """ 
        Method that adds Gaussian noise to SAM's initial position, therefore it's in odom_gt frame.
        It's not a real GPS measurement.
        """
        if self.sam_pos is not None:
            cov = [[self.sam_pos_var, 0], [0, self.sam_pos_var]]
            X = np.random.multivariate_normal(self.sam_init_pos[0:2], cov)
            #self.get_logger().info(f"SAM's position + noise: {round(float(X[0]), 2), round(float(X[1]),2)}")
            return X
        else: return None
        
        
    def sam_odom_callback(self, msg):
        """ Retrieves SAM position (in map_gt frame)"""
        self.sam_pos = np.array([msg.pose.pose.position.x, msg.pose.pose.position.y])

    def gps_ping_geo_callback(self, msg):
        """ Retrieves SAM GPS coordinates """
        self.gps_ping = msg

    def drone_odom_callback(self, msg):
        """ Retrieve drone position (map_gt)"""
        self.drone_position = np.array([msg.pose.pose.position.x, msg.pose.pose.position.y, msg.pose.pose.position.z])

""" --------------------- Parent path planner --------------------------------------"""
class SearchPlanner(Node, ABC):
    """ 
    Parent class containing several methods and attributes needed for any path planner algorithm. The different path planners
    classes will inherit from this class. It's never instantiated "standalone"

    Args: 
        name: ros node name
        params: dictionary with all relevant parameters for search planning. They can me changed in the launch file
        grid_map: object from ProbabilisticGridMap class 
        drone_init_pos: quadrotor's initial position (currently given by odometry in map frame)
        
    Attributes (the relevant ones):
        path: list of points from which the next waypoint will be published
        battery_state: current battery status in %
        distance_thresh: minimum distance to publish next waypoint. If the distance of the drone to the current waypoint if smaller
                        than this threshold, the next waypoint will be published regardless of drone's velocity
        drone_position, drone_vel, sam_vel: 1*2 arrays with x,y elements (position or velocity)

    Notes:

    """
    def __init__(self, name="pathplanner_parent", params = None, grid_map = None, drone_init_pos = None):
        super().__init__(node_name = name)
        self.get_logger().info('Parent search planner initialized')

        self.params = params
        self.grid_map = grid_map
        self.drone_init_pos = drone_init_pos

        self.path = None
        self.battery_state = None
        self.drone_position = None,
        self.drone_vel = None
        self.sam_vel = None
        self.distance_thresh = 0.1

        # flags to avoid blocking operations
        self.path_needed = True
        self.path_completed = False
        self.wait_finished = True

        if params:        
            self.planner_type = params["path_planner"]
            self.camera_fov = params["camera_fov"]
            self.flight_height = params["flight_height"]
            self.lat = params["look_ahead_time"]
            self.intermediate_dt = params["intermediate_dt"]

            self.battery_discharge_rate = params['battery.discharge_rate']
            self.battery_threshold = params['battery.threshold']
            self.equivalent_drone_vel = params['battery.equivalent_drone_vel'] 

            self.drone_map_frame_id = params['frames.id.quadrotor_map'] 
            self.drone_odom_frame_id = params['frames.id.quadrotor_odom'] 
        else:
            self.get_logger().error("No valid parameters received in Path Model")

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.create_subscription(
            msg_type = Odometry,
            topic = '/Quadrotor/odom_gt',
            callback = self.drone_odom_callback,
            qos_profile= 10)
        self.create_subscription(
            msg_type = Odometry,
            topic = '/sam_auv_v1/smarc/odom',
            callback = self.sam_odom_callback,
            qos_profile= 10)
        self.create_subscription(
            msg_type= BatteryState,
            topic = '/Quadrotor/core/battery',
            callback=self.drone_battery_callback,
            qos_profile= 10)     
        
        self.point_publisher = self.create_publisher(
            msg_type = PoseStamped,
            topic = '/Quadrotor/go_to_setpoint',
            qos_profile= 10)
        self.path_publisher = self.create_publisher( # visualization purposes only
            msg_type = Path,
            topic = '/Quadrotor/path',
            qos_profile= 10)
        

    @abstractmethod     
    def generate_path(self) -> bool:
        """ Common method to all children classes that generates a path and publishes the next waypoint. It returns false
        if the battery's low (return to base) and true if everything's good"""
        pass

    def generate_waypoint(self, x, y, z):
        """ Method to publish a single waypoint for the drone"""
        pose_msg = PoseStamped()
        pose_msg.header.stamp = self.get_clock().now().to_msg()
        pose_msg.header.frame_id = self.drone_odom_frame_id
        pose_msg.pose.position.x = x
        pose_msg.pose.position.y = y
        pose_msg.pose.position.z = z - self.drone_init_pos[2] 
        self.point_publisher.publish(pose_msg)
        
    def transform_pose(self, x_goal, y_goal) -> Pose:
        # transform desired position (relative position) to odom frame
        t = self.tf_buffer.lookup_transform(
            target_frame=self.drone_odom_frame_id,  
            source_frame=self.drone_map_frame_id,                 
            time=rclpy.time.Time() )
        goal = PointStamped()
        goal.header.stamp = t.header.stamp
        goal.header.frame_id = self.drone_map_frame_id
        goal.point.x = x_goal
        goal.point.y = y_goal
        goal.point.z = self.flight_height 
        new_goal = tf2_geometry_msgs.do_transform_point(goal, t)

        # send initial msg already transformed
        msg = Pose()
        msg.position.x =  new_goal.point.x 
        msg.position.y =  new_goal.point.y 
        msg.position.z = self.flight_height 

        return msg
    
    def find_cell(self, x_coord, y_coord):
        """ Maps (x,y) coordinates to cell coordinates """
        x_cell = int((x_coord - self.grid_map.X_min) / self.grid_map.resol) 
        y_cell = int((self.grid_map.Y_max - y_coord) / self.grid_map.resol) 
        x_cell = max(0, min(x_cell, self.grid_map.Ncells_x - 1))
        y_cell = max(0, min(y_cell, self.grid_map.Ncells_y - 1))
        return x_cell, y_cell
    
    def battery_ok(self, path) -> bool: 
        """ 
        Prediction of the total battery consumption while traversing  the path + return trip to origin.
        It's a very simple estimation assuming battery consumption varies linearly over time  
        """
        vel = max(self.equivalent_drone_vel, np.linalg.norm(self.drone_vel)) # when drone is hovering for example, vel = 0 but there's still battery consumption
        time = 0

        # outbound trip
        N = len(path)
        for i in range(1, N):
            time += dist(path[i-1], path[i])/vel
        # return trip
        time += dist([0,0], path[N-1])/vel

        # check percentage threshold
        percentage_var = (time/60)*self.battery_discharge_rate
        self.get_logger().info(f'Current battery = {round(self.battery_state,2)} % and estimated consumed battery in new path is {round(percentage_var,2)} % ')
        if self.battery_state - percentage_var <= self.battery_threshold:
            self.get_logger().info('Low battery ...')
            return False
        else:
            return True
        

    def publish_path(self) -> None:
        """ Publish path for visualization in rviz """

        path_msg = Path()
        path_msg.header.stamp = self.get_clock().now().to_msg()
        path_msg.header.frame_id = self.drone_odom_frame_id
        path_msg.poses = []
        for i, position in enumerate(self.path):
            pose_msg = PoseStamped()
            pose_msg.header.stamp = path_msg.header.stamp
            pose_msg.header.frame_id = self.drone_odom_frame_id
            pose_msg.pose.position.x = position[0]
            pose_msg.pose.position.y = position[1]
            path_msg.poses.append(pose_msg)
        self.path_publisher.publish(path_msg)

    def publish_waypoint(self, min_threshold: float, pose_odom: Pose) -> None:
        """ 
        It checks if drone is too close to the next waypoint and in that case, publishes next point. The distance threshold is linearly 
        dependent on velocity: the greater the velocity, the sooner the next waypoint will be published. This calculation is based on
        the defined "look ahead time" -> check launch file
        Args: 
            min_threshold: distance up to which next waypoint is always published. Chech class documentation (distance_thresh attribute)
            pose_odom: current drone's pose
        """

        lad = np.linalg.norm(self.drone_vel)*self.lat # "look ahead distance"
        distance2goal = sqrt((self.path[0][0]-pose_odom.position.x)**2 + (self.path[0][1]-pose_odom.position.y)**2)
        if ((distance2goal < min_threshold or distance2goal < lad or len(self.path) == self.path_num_points)
            and self.wait_finished): 
            dt = 0.01 if distance2goal > min_threshold else self.intermediate_dt # if we're far from goal, we want to publish the next goal asap.
            self.wait2publish_goal_timer = self.create_timer(dt, self.publish_waypoint_timer)
            self.wait_finished = False 

    def publish_waypoint_timer(self) -> None:
        """ Waypoint publication timer callback. It publishes the next point of the path"""
        pose_msg = PoseStamped()
        self.path.pop(0)
        if len(self.path) != 0:
            pose_msg.header.frame_id = self.drone_odom_frame_id
            pose_msg.header.stamp = self.get_clock().now().to_msg()
            pose_msg.pose.position.x = self.path[0][0]
            pose_msg.pose.position.y = self.path[0][1]
            pose_msg.pose.position.z = self.flight_height - self.drone_init_pos[2] 
            self.point_publisher.publish(pose_msg)
        self.wait_finished = True
        self.wait2publish_goal_timer.cancel()  


    def return_to_base(self):
        """ Method called when the drone is running low on battery. It will go to odom frame's origin"""
        pose_msg = PoseStamped()
        pose_msg.header.frame_id = self.drone_odom_frame_id
        pose_msg.header.stamp = self.get_clock().now().to_msg()
        pose_msg.pose.position.z = self.flight_height - self.drone_init_pos[2]
        self.point_publisher.publish(pose_msg)
        odom_msg = self.transform_pose(self.drone_position[0], self.drone_position[1])
        return odom_msg.position.x, odom_msg.position.y

        
    def drone_odom_callback(self, msg):
        """ Retrieve drone position (map_gt)"""
        self.drone_position = np.array([msg.pose.pose.position.x, msg.pose.pose.position.y])
        self.drone_vel = np.array([msg.twist.twist.linear.x, msg.twist.twist.linear.y])

    def sam_odom_callback(self, msg):
        """ Retrieve SAM's velocity from odometry"""
        self.sam_vel = np.array([msg.twist.twist.linear.x, msg.twist.twist.linear.y])

    def drone_battery_callback(self, msg):
        """ Retrieve current battery percentage"""
        self.battery_state = msg.percentage
        
""" --------------------- Spiral based path planner --------------------------------------"""

class SpiralPathModel(SearchPlanner):
    """ 
    Simple path generator that consists of a straight line up to the estimated SAM's and then a moving 
    spiral path along the estimatated SAM velocity direction, whose radius increase over time.

    Args: 
        name: ros node name
        params: dictionary with all relevant parameters for search planning. They can be changed in the launch file
        grid_map: an object from the ProbabilisticGridMap class. See prob_grid_map.py

    Attributes (the relevant ones):
        drone_position:

    Notes:

    """
    def __init__(self, name="pathplanner_spiral", params = None, grid_map = None, drone_init_pos = None):
        super().__init__(name = name, params = params, grid_map = grid_map, drone_init_pos = drone_init_pos)
        self.get_logger().info('Spiral initialized')
      
        # get parameters 
        try:
            self.sam_max_vel = params["sam.max_floating_vel"]
            self.vel_factor = params["spiral.vel_factor"]
            self.delta_theta = params["spiral.dtheta"]
        except:
            self.get_logger().error("No valid parameters received in Spiral Path Model")
        
        # parameterizations for the spiral
        self.theta, self.spiral_center = 0.0, np.array([0.0,0.0]) 
        self.r = self.flight_height*tan(pi*self.camera_fov/(2*180)) # "projected" radius
        self.R = self.r
        self.phase = 'line' 
        self.i = None
        self.previous_spiral_displacement = np.array([0,0])


    def generate_path(self) -> bool:
        """ 
        The spiral planner consists of three movements: a straight line to the GPS ping, an initial circle around that point and
        consecutive spirals after that. The spiral radius increases consecutively and the spiral center moves according to 
        SAM's estimated velocity
        """
        pose_odom = self.transform_pose(self.drone_position[0], self.drone_position[1])
        if self.path_needed:
            if self.phase == 'line':
                self.path = [[pose_odom.position.x, pose_odom.position.y], self.grid_map.GPS_ping_odom]
                self.phase = 'circle'
                self.path_needed = False
            elif self.phase == 'circle':
                # check velocity direction to produce points smoothly
                signs = [1,-1]
                vec1 = np.array([self.r*np.cos(signs[0]*self.delta_theta)  - self.r*np.cos(0), self.r*np.sin(signs[0]*self.delta_theta)  - self.r*np.sinc(0)])
                vec2 = np.array([self.r*np.cos(signs[1]*self.delta_theta)  - self.r*np.cos(0), self.r*np.sin(signs[1]*self.delta_theta)  - self.r*np.sinc(0)])
                self.i = signs[np.argmax(np.matmul(np.array([vec1, vec2]), self.drone_vel))]
                # generate circle points
                theta = np.arange(0,self.i*(2*pi+self.delta_theta), self.i*self.delta_theta)
                x = self.r*np.cos(theta) + self.grid_map.GPS_ping_odom[0]
                y = self.r*np.sin(theta) + self.grid_map.GPS_ping_odom[1]
                self.path = list(zip(x,y))
                self.path_needed = False
                self.phase = 'spiral'

            elif self.phase == 'spiral': 
                # NOTE: if sam odom and quadrotor ain't aligned, this needs to be changed
                sam_vel = self.sam_vel

                # generate moving spiral with increasing radius -> estimate period with current drone velocity
                predicted_T = 2*pi*self.R/np.linalg.norm(self.drone_vel)
                spiral_displacement = self.vel_factor*sam_vel*predicted_T
                theta = np.arange(0,self.i*(2*pi+self.delta_theta),self.i*self.delta_theta)
                delta_r = self.r*(1-sqrt(np.linalg.norm(sam_vel)/self.sam_max_vel)) # radius increment accounting for sam velocity
                r = np.linspace(self.R, self.R + delta_r, theta.shape[0])
                self.R  += delta_r 
                x = self.grid_map.GPS_ping_odom[0] + np.multiply(r, np.cos(theta)) + np.linspace(0, spiral_displacement[0], theta.shape[0]) + self.previous_spiral_displacement[0] 
                y = self.grid_map.GPS_ping_odom[1] + np.multiply(r, np.sin(theta)) + np.linspace(0, spiral_displacement[1], theta.shape[0]) + self.previous_spiral_displacement[1] 
                self.path = list(zip(x,y))
                self.path_needed = False
                self.previous_spiral_displacement = spiral_displacement
                
            self.path_num_points = len(self.path)
            
            # publish path for visualization in rviz
            self.publish_path()

            #check battery
            if not self.battery_ok(self.path): 
                return False
            return True

        elif not self.path_needed and not self.path_completed:
            if len(self.path) == 0:
                self.path_completed = True 
            else:
                self.publish_waypoint(self.distance_thresh, pose_odom)
               
        else:
            self.path_needed = True
            self.path_completed = False
            self.phase == 'line'
 
        return True



""" --------------------- A* and Greedy path planners --------------------------------------"""
class GreedyPathModel(SearchPlanner):
    """ 
    Args: 
        name: ros node name
        params: dictionary with all relevant parameters for search planning. They can me changed in the launch file
        grid_map: an object from the ProbabilisticGridMap class. See prob_grid_map.py

    Attributes (the relevant ones):

    Notes:
    """
    def __init__(self, name="pathplanner_greedy", params = None,  grid_map = None, drone_init_pos = None):
        super().__init__(name = name, params = params, grid_map = grid_map, drone_init_pos = drone_init_pos)
        self.get_logger().info('Greedy initialized')

        try:
            self.horizon = params['greedy.horizon_radius']
        except:
            self.get_logger().error("No valid parameters received in Greedy Path Model")


    def generate_path(self) -> bool:
        """ It makes use of the grid map to generate a striaght line between current position and cell
        with highest probability. This cell can be retrieved using the full map or using a region around
        the drone's current position. In the latter case, the radius has to be specified -> horizon
        """
        if self.path_needed:
            self.get_logger().info(f'Path is needed, running {self.params["path_planner"]}) path planner')
            self.path_needed = False

            # get current position in odom and cell with highets prob in a given radius
            pose_odom = self.transform_pose(self.drone_position[0], self.drone_position[1])
            start = [pose_odom.position.x, pose_odom.position.y]
            if self.horizon == -1:
                idx = np.unravel_index(np.argmax(self.grid_map.prior, axis=None), self.grid_map.prior.shape) #  idx = [column index, row index]
            else: 
                try:
                    xc_cell, yc_cell = self.find_cell(x_coord = start[0], y_coord = start[1])
                    encirclements = int(self.horizon/(sqrt(2)*self.grid_map.resol))+1
                    base_mask = np.ix_(np.arange(yc_cell-encirclements,yc_cell+encirclements+1,1), np.arange(xc_cell-encirclements,xc_cell+encirclements+1,1))
                    horizon_prior = self.grid_map.prior[base_mask]
                    idx_horizon = np.unravel_index(np.argmax(horizon_prior, axis=None), horizon_prior.shape)
                    idx = np.array([yc_cell-encirclements, xc_cell-encirclements], dtype=int) + idx_horizon
                except IndexError:
                    idx = np.unravel_index(np.argmax(self.grid_map.prior, axis=None), self.grid_map.prior.shape)

            # generate pseudo obstacles and plan path 
            goal = [self.grid_map.X[idx[0]][idx[1]], self.grid_map.Y[idx[0]][idx[1]]]
            self.path = [start, goal]
            self.path_num_points = len(self.path)

            # publish path for visualization in rviz
            self.publish_path()

            #check battery
            if not self.battery_ok(self.path): 
                return False
            return True


        elif not self.path_needed and not self.path_completed:
            if len(self.path) == 0:
                self.path_completed = True 
            else:
                pose_odom = self.transform_pose(self.drone_position[0], self.drone_position[1])
                self.publish_waypoint(self.distance_thresh, pose_odom)            
        
        else:
            self.path_needed = True
            self.path_completed = False
            
        return True
    
""" --------------------- A*  path planners --------------------------------------"""

class AStarPathModel(SearchPlanner):
    """ 
    Args: 
        name: ros node name
        params: dictionary with all relevant parameters for search planning. They can me changed in the launch file
        grid_map: an object from the ProbabilisticGridMap class. See prob_grid_map.py

    Attributes (the relevant ones):

    Notes:
    """
    def __init__(self, name="pathplanner_astar", params = None, grid_map = None, drone_init_pos = None):
        super().__init__(name = name, params = params, grid_map = grid_map, drone_init_pos = drone_init_pos)
        self.get_logger().info('A* initialized')

        # different initialization between astar and greedy (greedy inherits from astar class)
        try:
            self.max_length = params["astar.obstacles.max_length"]
            self.quantile_percentage = params["astar.obstacles.quantile_per"]
            self.obstacles_percentage = params["astar.obstacles.obstacles_per"]
            self.horizon = params['astar.horizon_radius']
        except:
            self.get_logger().error("No valid parameters received in AStar Path Model")
        self.astar = AStar(resolution=self.grid_map.resol, rr=self.grid_map.resol) # drone radius and map resolution are equal


    def generate_path(self):
        """ Similar to greedy but obstacles are generated using cells with small probability. Therefore, instead of generating
        a straight line, a graph-based planner is used. #NOTE: It can take a considerable amount of time, depending on the workspace number of cells
        and the number of cells considered to generate obstacles"""
        
        if self.path_needed:
            self.get_logger().info(f'Path is needed, running A* path planner')
            self.path_needed = False

            # get current position in odom and cell with highets prob in a given radius
            pose_odom = self.transform_pose(self.drone_position[0], self.drone_position[1])
            start = [pose_odom.position.x, pose_odom.position.y]
            if self.horizon == -1:
                idx = np.unravel_index(np.argmax(self.grid_map.prior, axis=None), self.grid_map.prior.shape) #  idx = [column index, row index]
            else: 
                try:
                    xc_cell, yc_cell = self.find_cell(x_coord = start[0], y_coord = start[1])
                    encirclements = int(self.horizon/(sqrt(2)*self.grid_map.resol))+1
                    base_mask = np.ix_(np.arange(yc_cell-encirclements,yc_cell+encirclements+1,1), np.arange(xc_cell-encirclements,xc_cell+encirclements+1,1))
                    horizon_prior = self.grid_map.prior[base_mask]
                    idx_horizon = np.unravel_index(np.argmax(horizon_prior, axis=None), horizon_prior.shape)
                    idx = np.array([yc_cell-encirclements, xc_cell-encirclements], dtype=int) + idx_horizon
                except IndexError:
                    idx = np.unravel_index(np.argmax(self.grid_map.prior, axis=None), self.grid_map.prior.shape)

            # generate pseudo obstacles and plan path 
            goal = [self.grid_map.X[idx[0]][idx[1]], self.grid_map.Y[idx[0]][idx[1]]]

            ox, oy = self.create_pseudo_obstacles(prior = self.grid_map.prior, X = self.grid_map.X, Y = self.grid_map.Y, res = self.grid_map.resol,
                    corner_1 = [self.grid_map.X_min, self.grid_map.Y_min] , corner_2 = [self.grid_map.X_max, self.grid_map.Y_max], 
                    R = self.grid_map.resol, start = start, goal = goal)
            self.astar.set_obstacles(ox, oy)
            rx, ry = self.astar.planning(start[0], start[1], goal[0], goal[1]) # rx and ry are positions in odom (not cell indexes)
            if rx is None or ry is None:
                self.path_needed = True
                self.get_logger().error('No path found with AStar! (this is not supposed to happen)')
                return True
            else:
                rx.reverse()
                ry.reverse()
                self.path = list(zip(rx, ry))
                #self.get_logger().info(f'Path: {self.path}')
            
            self.path_num_points = len(self.path)

            # publish path for visualization in rviz
            self.publish_path()

            #check battery
            if not self.battery_ok(self.path): 
                return False
            return True


        elif not self.path_needed and not self.path_completed:
            #self.get_logger().info('Moving')
            if len(self.path) == 0:
                self.path_completed = True 
            else:
                pose_odom = self.transform_pose(self.drone_position[0], self.drone_position[1])
                self.publish_waypoint(self.distance_thresh, pose_odom)            
        
        else:
            self.path_needed = True
            self.path_completed = False
            
        return True
    

    
    def create_pseudo_obstacles(self, prior, X, Y, res, corner_1, corner_2, R, start, goal):
        """ Create pseudo obstacles based on the prior probability map.
        From the quantile_percentage % cells with smallest probabilities, we choose obs_percentage % of them randomly as obstacles"""

        # choose cells with smallest probabilities to define obstacles
        quantile_percentage = self.quantile_percentage
        obs_percentage = self.obstacles_percentage
        ind = np.argsort(prior, axis=None)
        ind = ind[:int(len(ind) * quantile_percentage / 100)]
        np.random.shuffle(ind) #TODO: not returning correctly
        ind = ind[:int(len(ind) * obs_percentage / 100)]
        reference_cells = [[int(ind[i] % prior.shape[0]), int(ind[i] // prior.shape[0])] for i in range(len(ind))]
        N = len(reference_cells)

        # set workspace boundary as obstacles (lower base, right wall, upper base, left wall)
        min_length = min(abs(np.array(corner_2)- np.array(corner_1)))
        x1 = np.arange(corner_1[0], corner_2[0]+self.grid_map.resol/2, self.grid_map.resol/2)
        y1 = np.linspace(corner_1[1], corner_1[1], x1.shape[0])

        y2 = np.arange(corner_1[1], corner_2[1]+self.grid_map.resol/2, self.grid_map.resol/2)
        x2 = np.linspace(corner_2[0], corner_2[0], y2.shape[0])

        x3 = x1
        y3 = y1 + self.grid_map.h

        y4 = y2
        x4 = x2 - self.grid_map.w

        ox = list(np.concatenate((x1,x2,x3,x4)))
        oy = list(np.concatenate((y1,y2,y3,y4)))

        # pair reference cells
        idx2 = 1
        count = 0
        pairs = []
        lines_parameters = []
        while True:
            idx1 = 0
            if len(reference_cells) <= 1 or count > factorial(N):
                break
            if idx2 >= len(reference_cells):
                reference_cells.pop(idx1)
                idx2 = 1
                continue
            valid_cells_pair = self.check_cells(min_length, corner_1, corner_2, R,
                                X[reference_cells[idx1][0]][reference_cells[idx1][1]], Y[reference_cells[idx1][0]][reference_cells[idx1][1]], 
                                X[reference_cells[idx2][0]][reference_cells[idx2][1]], Y[reference_cells[idx2][0]][reference_cells[idx2][1]],
                                start, goal)
            if not valid_cells_pair:
                idx2 += 1
            else:
                pairs.append((float(X[reference_cells[idx1][0]][reference_cells[idx1][1]]), float(X[reference_cells[idx2][0]][reference_cells[idx2][1]]), 
                              float(Y[reference_cells[idx1][0]][reference_cells[idx1][1]]), float(Y[reference_cells[idx2][0]][reference_cells[idx2][1]])))
                reference_cells.pop(max([idx1, idx2]))
                reference_cells.pop(min([idx1, idx2]))
                idx2 = 1
            count += 1

        # create obstacles. pairs[i] = (x1, x2, y1, y2)
        for n in range(len(pairs)):
            idx_min = np.argmin([pairs[n][0], pairs[n][1]])
            point_A = [pairs[n][idx_min], pairs[n][idx_min+2]] # point to the left
            point_B = [pairs[n][-idx_min+1], pairs[n][-idx_min+3]] # point to the right
            try:
                slope = (point_B[1]-point_A[1])/(point_B[0]-point_A[0]) 
            except:
                slope = 0
            is_intersection, HC_params = self.check_intersections(slope, point_A, point_B, lines_parameters, R)
            if is_intersection:
                continue
            else:
                lines_parameters.append([HC_params, point_A, point_B]) # lines params = [[slope,b],(x_A, y_A),(x_B, y_B)] 
                n_int_points = int(max(abs((point_B[0]-point_A[0]))/R+1,abs((point_B[1]-point_A[1]))/R+1)) 
                x = np.linspace(point_A[0], point_B[0], num = n_int_points)
                y = np.linspace(point_A[1], point_B[1], num = n_int_points)
                for i in range(n_int_points):
                    ox.append(x[i])
                    oy.append(y[i])
        return ox, oy
    
    def check_cells(self, min_length, corner_1, corner_2, R, x1, y1, x2, y2, start, goal):
        """ Check if two cells can consist of an obstacle. They need to satisfy some distance
        requirements. """
        w = self.max_length #threshold for maximum length of an obstacle
        dist_thresh = 3*R
        X1 = np.array([x1,y1])
        X2 = np.array([x2,y2])

        for i, position in enumerate([start, goal]):
            # s or g = X1 +t(X2-X1)
            t = np.dot(position-X1, X2-X1)/np.linalg.norm(X2-X1)**2
            t = min(max(t,0),1)
            distance = np.linalg.norm((X1+t*(X2-X1)) - position)
            if distance <= dist_thresh:
                return False
        if (
            dist(X1, X2) > w * min_length
            or any((np.array([x1, x2]) - corner_1[0]) <= dist_thresh)  # far from workspace boundaries 
            or any((corner_2[0] - np.array([x1, x2])) <= dist_thresh)
            or any((np.array([y1, y2]) - corner_1[1]) <= dist_thresh)  
            or any((corner_2[1] - np.array([y1, y2])) <= dist_thresh)
            or dist(start, X1) <= dist_thresh # far from start/goal 
            or dist(start, X2) <= dist_thresh
            or dist(goal, X1) <= dist_thresh
            or dist(goal, X2) <= dist_thresh 
        ):
            return False 
        else:
            return True
    
    def check_intersections(self, slope, point_A, point_B, lines_parameters, R):
        """ 
        Receives points and slope of the line segment and sees if there's an intersection with other line segments
        Point_A is the point with minimum x coordinate. Intersection is computed using cross product in Homo. Coord 
        """
        params_line = np.array([slope, -1, point_A[1] - slope * point_A[0]])
        dist_thresh = 2*R
        for i, params_others in enumerate(lines_parameters):
            intersection_point = np.cross(params_line, params_others[0])
            try:
                intersection_point = intersection_point[:2]/intersection_point[2]
            except ZeroDivisionError as e:
                continue # lines are parallel
            if (
                (point_A[0] - dist_thresh <= intersection_point[0] <= point_B[0] + dist_thresh) and
                (params_others[1][0] - dist_thresh <= intersection_point[0] <= params_others[2][0] + dist_thresh)
            ):  
                return True, None
        return False, params_line
    

""" --------------------- Artificial Potential Field --------------------------------------"""

from numpy import multiply as m
class APFPathModel(SearchPlanner):

    """ 
    Args: 
        name: ros node name
        params: dictionary with all relevant parameters for search planning. They can me changed in the launch file
        grid_map: an object from the ProbabilisticGridMap class. See prob_grid_map.py

    Attributes (the relevant ones):

    Notes:
    """
    def __init__(self, name="pathplanner_apf", params = None, grid_map = None, drone_init_pos = None):
        
        super().__init__(name = name, params = params, grid_map = grid_map, drone_init_pos = drone_init_pos)
        self.get_logger().info('APF initialized')

        try:
            self.ka = params['arf.k_attractive']
            self.kr = params['arf.k_repulsive']
            self.mass = params['arf.goal_distance_factor'] # we'll call it mass for simplicity but this factor doesn't have mass units
            self.d_min= params['arf.d_min']
            self.d_max = params['arf.d_max']
            self.horizon = params['arf.horizon_radius']
        except:
            self.get_logger().error("No valid parameters received in ARF Path Model")


    def generate_path(self) -> bool:
        """ 
        We consider the goal cell to exert an attractive force and the remaining cells to exert a repulsive force.
        Similar to regular artifical potential field algorithms but we use probability as well: cells with lower probability will
        exert more repulsive force.
        
        The resultant of forces is then convert to a displacement vector, which is proportional to the force.
        """
        if self.path_needed:
            self.path_needed = False
            # get current position in odom and cell with highets prob in a given radius
            pose_odom = self.transform_pose(self.drone_position[0], self.drone_position[1])
            start = np.array([pose_odom.position.x, pose_odom.position.y])
            if self.horizon == -1:
                X, Y, prior = self.grid_map.X, self.grid_map.Y, self.grid_map.prior
            else: 
                try:
                    xGlobal_idx, yGlobal_idx = self.find_cell(x_coord = start[0], y_coord = start[1])
                    encirclements = int(self.horizon/(sqrt(2)*self.grid_map.resol))+1
                    base_mask = np.ix_(np.arange(yGlobal_idx-encirclements,yGlobal_idx+encirclements+1,1), np.arange(xGlobal_idx-encirclements,xGlobal_idx+encirclements+1,1))
                    X, Y, prior = self.grid_map.X[base_mask], self.grid_map.Y[base_mask],  self.grid_map.prior[base_mask]
                except IndexError:
                    X, Y, prior = self.grid_map.X, self.grid_map.Y, self.grid_map.prior       

            # compute resultant of forces, goal position and corresponding path
            Fr, goal_distance = self.create_forces(X, Y, prior, start)
            goal = self.create_goal(Fr, self.drone_vel, goal_distance)
            self.path = [start, start+goal]
            self.path_num_points = len(self.path)

            # publish path for visualization in rviz
            self.publish_path()
            
            #check battery
            if not self.battery_ok(self.path): 
                return False
            return True
        

        elif not self.path_needed and not self.path_completed:
            if len(self.path) == 0:
                self.path_completed = True 
            else:
                pose_odom = self.transform_pose(self.drone_position[0], self.drone_position[1])
                self.publish_waypoint(self.distance_thresh, pose_odom)            
        
        else:
            self.path_needed = True
            self.path_completed = False
            
        return True
    

    def create_forces(self, X, Y, prior, start:np.array):
        """ Each cell will exert a repulsive force that depends on distance and corresponding probability. The goal cell
        on its turn exerts an attractive force. The repulsive force is limited to avoid local minima (contexts where resultant force = 0)

        Besides, some distance thresholds are imposed. This means not every cell will exert forces, only those withing a specific region.
        """
        # define goal and choose between conical potential (dist < d0) or quadratic potential (dist > d0)
        goal_idx = np.unravel_index(np.argmax(prior, axis=None), prior.shape)
        goal = np.array([X[goal_idx[0]][goal_idx[1]], Y[goal_idx[0]][goal_idx[1]]])
        goal_dist = dist(goal, start) + sys.float_info.min
        exp = 2 if goal_dist > self.d_min else 3

        # initialize vector field (3D array) and compute scaled probability array
        force_field = np.zeros((2,X.shape[0], X.shape[1]), dtype = float)
        scaled_prior = self.map_probabilities(prior)

        # compute attractive and repulsive forces and assign latter
        F_att = self.ka*(goal-start)/goal_dist**(exp-2)
        dists = np.sqrt((X-start[0])**2, (Y-start[1])**2) + 1e-6
        K = self.kr * m(scaled_prior, m(1/dists - 1/self.d_min, 1/dists**exp))
        force_field = -np.multiply(K, [start[0] - X, start[1] - Y])

        # limit force to avoid null resultant force (TODO: improve this to avoid local minima); distance threshold
        F_max = np.linalg.norm(F_att/(X.shape[0]*X.shape[1]))
        mask = np.sqrt(force_field[0]**2 + force_field[1]**2) < F_max
        force_field = np.where(mask, force_field, force_field / F_max)
        force_field = np.where((self.d_min < dists) & (dists < self.d_max), force_field, 0)

        # assign attractive force and compute resultant force
        force_field[0][goal_idx[0]][goal_idx[1]] = F_att[0]
        force_field[1][goal_idx[0]][goal_idx[1]] = F_att[1]
        Fr = np.sum(force_field, axis=(1,2))
        return Fr, dists[goal_idx[0]][goal_idx[1]]
    
    def create_goal(self, Fr: np.array, vel:np.array, goal_distance: float) -> np.array:
        """ Computes goal in the direction of the resultant force. The displacement is proportional to the
        resultant of forces."""
        vel = max(self.equivalent_drone_vel, np.linalg.norm(vel))
        goal = (1/self.mass)* Fr
        return goal


    def map_probabilities(self, prior:np.array) -> np.array:
        """ It maps the local prior to the interval [0,1], where the maximum probability will correspond to 0 and the minimum to 1"""
        log_prob = -np.log(prior+sys.float_info.min)
        min = np.min(log_prob) 
        max = np.max(log_prob) 
        return (log_prob - min) /(max - min)
        
if __name__ == "__main__":
    # TODO: define model while running standalone
    pass
