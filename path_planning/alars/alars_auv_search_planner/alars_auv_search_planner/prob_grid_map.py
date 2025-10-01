#!/usr/bin/python
import sys
import rclpy
from rclpy.node import Node
import numpy as np
import scipy.signal as sc
from math import sin, pi, sqrt, tan, log
from rclpy.duration import Duration
from nav_msgs.msg import OccupancyGrid, Odometry
from geometry_msgs.msg import Pose, PoseStamped, PointStamped, Vector3Stamped
import tf2_geometry_msgs
from tf2_ros import Buffer, TransformListener


class ProbabilisticGridMap(Node):
    """ 
    Node that creates and updates probabilistic grid map using Bayes Filtering. We'll update using meshgrids but will publish ROS 
    msg to facilitate integration with other nodes. The grid map is constructed in drone's odom frame

    Args: 
        name: ros node name
        params: dictionary with all relevant parameters for search planning. They can me changed in the launch file
        GPS_ping: PointStamped with GPS coordinates in any frame (as long as it's connected to Quadrotor/odom_gt) 

    Attributes (the relevant ones):
        GPS_ping_odom: estimated SAM coordinates [x,y] in odom frame. It's also used by spiral path planner (as attribute of this class)
        drone_pos_odom_gt: current drone's position in odom frame
        prior: 2D array in which each element corresponds to the estimatec probability of the corresponding cell of having SAM there

    Notes:

    """

    def __init__(self, name = "SearchPlanner_gridmap", params:dict = None, GPS_ping:PointStamped = None):
        super().__init__(name)
        self.get_logger().info('Grid map initialized')

        if params:

            self.w = params["grid_map.workspace.width"]
            self.h = params["grid_map.workspace.height"]
            self.resol = params["grid_map.workspace.resol"]
            self.variance = params["grid_map.workspace.variance"]

            self.dt = params['grid_map.update.rate']
            self.beta = params["grid_map.update.true_detection_rate"]
            self.time_margin = params["grid_map.update.time_margin"]*1e9 #nanoseconds

            self.camera_fov = (pi/180)*params["drone.camera_fov"]
            self.flight_height = params["drone.flight_height"]

            self.drone_odom_frame_id = params['frames.id.quadrotor_odom'] 

        else:
            self.get_logger().error("No parameters received")

        # initialize grid map vars. 
        self.GPS_ping = GPS_ping
        self.GPS_ping_odom = None
        self.drone_pos_odom_gt = None
        self.prior = None

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.drone_position = PointStamped()
        self.sam_vel = Vector3Stamped()

        # initiate pubs and subs
        self.create_subscription(
            msg_type = Odometry,
            topic = params["topics.drone_odom"],
            callback = self.drone_odom_callback,
            qos_profile= 10)

        self.grid_map_pub = self.create_publisher(msg_type=OccupancyGrid, topic = params["topics.pub_grid_map"], qos_profile = 10)
        self.cell_pub = self.create_publisher(msg_type=PointStamped, topic = params["topics.pub_likely_sam_location"], qos_profile = 10)

        # If mode = as, sam vel is not accessible -> assume zero
        if params["mode"] == "as":
            self.sam_vel.vector.x = .0
            self.sam_vel.vector.y = .0
            self.sam_vel.vector.z = .0
            self.sam_vel.header.frame_id = self.drone_odom_frame_id
            self.sam_vel.header.stamp = self.get_clock().now().to_msg()

        else:
            self.create_subscription(
                msg_type= Odometry,
                topic = params["topics.sam_odom"],
                callback=self.sam_odom_callback,
                qos_profile= 10)  


    def initiate_grid_map(self) -> None: 
        """ 
        Initializes grid map , ie, initializes the grid map coordinates and the timestamp of each cell. 
        It's then published for rviz visualization.
        If transformation fails, controller will try again in next loop cycle
        """

        # create grid map without probabilities (just its dimensions) as class attributes and ros msg.
        self.GPS_ping_odom, _ = self.transform_point(self.GPS_ping)
        self.createMap(self.GPS_ping_odom) 

        # gaussian prior, scale probabilities to fit int -> viewing purposes only
        self.prior = self.initiatePrior(self.GPS_ping_odom)
        self.prior2grid_msg()        
        self.grid_map_pub.publish(self.map)
        

    def apply_bayes_filter(self) -> bool:
        """ 
        Bayesian filter that predicts and updates prior and publishes grid map msg. The update step is performed as usual but the predict step
        tries to account for SAM's estimated velocity and drag the probabilities along that direction. That's accomplished by a convolution with
        an appropriate kernel
        """

        ## (modified) Predict Step 
        kernel = self.kernel()
        self.prior = sc.convolve2d(self.prior, kernel, mode = 'same')
        self.prior /= np.sum(self.prior)

        ## Update Step
        self.map.header.stamp = self.drone_position.header.stamp #self.get_clock().now().to_msg() 
        rows, columns = self.find_cells2update()
        
        # #TODO: do update properly (subscribe from detection node)
        self.map_Time[rows, columns] = self.get_clock().now().nanoseconds
        detection = False
        likelihood = 1 - self.beta if not detection else self.beta
        self.prior[rows, columns] = likelihood * self.prior[rows, columns]
        self.prior /= np.sum(self.prior)

        self.prior2grid_msg()
        self.grid_map_pub.publish(self.map)

        # publishing cell with highest probability for visualization purposes
        self.pub_max_prob_cell()

        return self.map_seen()
    
    
    def kernel(self):
        """
        Using SAM's estimated velocity in the correct frame, the kernel is estimated. 
        The kernel is a 3*3 matrix with bigger values on the elements that are aligned with SAM's velocity direction.
        Eg: if SAM's velocity = (0,1), then the top-central element of the kernel will be significantly high
        """

        sam_vel_odom = self.transform_vector(self.sam_vel)

        # Compute weights by mapping SAM's velocity to closest base vector and retrieving most appropriate kernel
        (q, Q) = self.compute_kernel_coeff(sam_vel=np.linalg.norm(sam_vel_odom), 
                                           update_period=self.dt,
                                           resol=self.resol,
                                           function_string='piecewise')
        
        base_vectors = [(0,1), (1/sqrt(2),1/sqrt(2)), (1,0), (1/sqrt(2),-1/sqrt(2)), 
                        (0,-1), (-1/sqrt(2),-1/sqrt(2)), (-1,0), (-1/sqrt(2),1/sqrt(2))]
        dot_products = [np.dot(sam_vel_odom, base_vector) for base_vector in base_vectors]
        mapped_direction = base_vectors[np.argmax(dot_products)]
        blur_factor = 10 # the neighbouring cells will also have an impact. Higher the blur factor, smaller the impact (should be called unblur factor maybe)
        direction_dict = {
            (0,1):                      np.array([[q/blur_factor,q,q/blur_factor],
                                                    [0,Q,0],
                                                    [0,0,0]]),

            (1/sqrt(2),1/sqrt(2)):      np.array([[0,q/blur_factor,q],
                                                    [0,Q,q/blur_factor],
                                                    [0,0,0]]),

            (1,0):                      np.array([[0,0,q/blur_factor],
                                                    [0,Q,q],
                                                    [0,0,q/blur_factor]]),

            (1/sqrt(2),-1/sqrt(2)):     np.array([[0,0,0],
                                                    [0,Q,q/blur_factor],
                                                    [0,q/blur_factor,q]]),

            (0,-1):                     np.array([[0,0,0],
                                                    [0,Q,0],
                                                    [q/blur_factor,q,q/blur_factor]]),

            (-1/sqrt(2),-1/sqrt(2)):    np.array([[0,0,0],
                                                    [q/blur_factor,Q,0],
                                                    [q,q/blur_factor,0]]),

            (-1,0):                     np.array([[q/blur_factor,0,0],
                                                    [q,Q,0],
                                                    [q/blur_factor,0,0]]),

            (-1/sqrt(2), 1/sqrt(2)):    np.array([[q,q/blur_factor,0],
                                                    [q/blur_factor,Q,0],
                                                    [0,0,0]])
        }
        normalized_kernel = direction_dict[mapped_direction]/np.sum(direction_dict[mapped_direction]) 

        return normalized_kernel
    
    def compute_kernel_coeff(self, sam_vel:float, update_period:float, resol:float, function_string:str) -> tuple[float, float]:
        """ 
        Computes weights q and Q based on the function type provided. This is done by computing the distance SAM ha travelled between
        consecutive Bayes Filter updates. The bigger the distance, the bigger the outer elements of the kernel.

        Notes: 
            Q is the central weight whilst q is the outer weight. So if SAM's has travelled a bigger distance, q/Q will increase, ie,
            we rely more in outer cells than the central cell

            The weight calculation is made with math functions and some parameters. There's little science underneath these values, it's 
            mostly based on empirical results (good old trial & error) -> TODO: find the science of this

            The piecewise consists of two linear functions, one for small velocities and one for considerable velocities. This difference
            relies on the need of filtering meaningless velocities that don't reflect SAM's movement

            piecewise ratio = q/Q. The smaller, the faster SAM's moving
        """
        d_max = sqrt(2)*resol
        d = min(sam_vel*update_period, d_max)
        d_ratio_lb = 1e-3 # value from which steeper linear function is applied
        weight_ratio_lb = 1e-8 # slope value for smaller velocities
        weight_ratio_ub = 0.1 # slope value for bigger velocities. Decrease if predict step is "convolving too fast".
        #TODO: define a function that receives resol, bayes update dt and outputs the best weight
        
        piecewise_ratio = lambda d_ratio: d_ratio*weight_ratio_lb if d_ratio < d_ratio_lb else max(weight_ratio_lb, weight_ratio_ub*d_ratio)

        piecewise = lambda d: (1, min(1/max(piecewise_ratio(d/d_max), sys.float_info.min), sys.float_info.max))
        linear = lambda d:  (d*(sys.float_info.max-1)/d_max +1, -d*(sys.float_info.max-1)/d_max + sys.float_info.max)
        rational = lambda d: ( d_max/(d_max-d), (d_max-d)/d)
        logarithmic = lambda d: ( log(d_max/(d_max-d))+1, log((d_max-d)/d)+1 )

        fcn_dict = {
            'piecewise': piecewise,
            'linear': linear,
            'rational': rational,
            'logarithmic': logarithmic }

        return fcn_dict[function_string](d)

    

    def find_cells2update(self):
        """ 
        Function that determines the cells that need to be updated based on flight height, camera FOV and time constraint.
        Here, as in the majority of functions of this node, consider the private grid map (self.X and self.Y) indexes, 
        not the ROS grid map indexes

        To avoid heavy computations, we don't apply the distance and time criteria on the full grid map. A mask is computed based on
        the "projected radius" (which depends on height of flight and camer FOV).
        
        """
        
        x_cells, y_cells = [], []
        drone_pos_odom, height = self.transform_point(self.drone_position)
        x, y = drone_pos_odom[0], drone_pos_odom[1]
        detection_radius = tan(self.camera_fov/2)*height
        xc_cell, yc_cell = self.find_cell(x_coord = x, y_coord = y) # drone's current cell

        # create a mask around current cell to avoid iterate over full workspace
        encirclements = int(detection_radius/self.resol)+1
        base_mask = np.ix_(np.arange(yc_cell-encirclements,yc_cell+encirclements+1,1), np.arange(xc_cell-encirclements,xc_cell+encirclements+1,1))

        # remove cells that lie outside the workspace
        base_mask_y_filtered = np.extract((0 <= base_mask[0]) & (base_mask[0] <= self.Ncells_y -1), base_mask[0])
        base_mask_x_filtered = np.extract((0 <= base_mask[1]) & (base_mask[1] <= self.Ncells_x -1), base_mask[1])
        base_mask_filtered = (base_mask_y_filtered.reshape(base_mask_y_filtered.shape[0],1), base_mask_x_filtered )
        
        # apply distance and time criteria
        sub_X, sub_Y, sub_Time = self.X[base_mask_filtered], self.Y[base_mask_filtered], self.map_Time[base_mask_filtered]
        condition_mask = (
            ((np.power(sub_X - x, 2) + np.power(sub_Y - y, 2)) < detection_radius ** 2)
            & (((self.get_clock().now().nanoseconds) - sub_Time > self.time_margin) | (sub_Time == self.init_timestamp))
        )
        condition_rows, condition_cols = np.where(condition_mask)
        rows = condition_rows + yc_cell-encirclements
        columns = condition_cols + xc_cell-encirclements

        # remove negative elements from rows and columns -> we don't want to wrap around the grid map
        mask = (0 <= rows) & (rows < self.Ncells_y) & (0 <= columns) & (columns < self.Ncells_x)
        rows = rows[mask]
        columns = columns[mask]

        return rows, columns

    def find_cell(self, x_coord, y_coord):
        """ Maps (x,y) coordinates to cell coordinates """
        x_cell = int((x_coord - self.X_min) / self.resol) 
        y_cell = int((self.Y_max - y_coord) / self.resol)  
        x_cell = max(0, min(x_cell, self.Ncells_x - 1))
        y_cell = max(0, min(y_cell, self.Ncells_y - 1))
        return x_cell, y_cell
       
    def pub_max_prob_cell(self):
        """Publishes cell with highest probability for visualization purposes (rviz)"""
        idx = np.unravel_index(np.argmax(self.prior, axis=None), self.prior.shape)
        cell_coord = PointStamped()
        cell_coord.header.frame_id = self.drone_odom_frame_id
        cell_coord.header.stamp = self.get_clock().now().to_msg()
        cell_coord.point.x = self.X[idx[0]][idx[1]]
        cell_coord.point.y = self.Y[idx[0]][idx[1]]
        self.cell_pub.publish(cell_coord)


    def prior2grid_msg(self):
        """ Convert 2D array to a row-major order list in order to publish as a ros message"""
        data = self.prior[::-1].reshape(self.prior.shape[0]*self.prior.shape[1], 1).flatten().tolist() #[::-1] or not in prior
        data = self.map_probabilities(np.log10(np.array(data)+sys.float_info.min))
        self.map.data = [int(d) for d in data]
    
    def transform_point(self, point:PointStamped) -> np.array:
        """Convert points in map frame to odom frame"""
        t = self.tf_buffer.lookup_transform(
            target_frame = self.drone_odom_frame_id,  
            source_frame = point.header.frame_id,                 
            time=rclpy.time.Time() )
        new_point = tf2_geometry_msgs.do_transform_point(point, t)
        return np.array([new_point.point.x, new_point.point.y]), new_point.point.z
    
    def transform_vector(self, vector:Vector3Stamped) -> np.array:
        """Convert points in map frame to odom frame"""
        t = self.tf_buffer.lookup_transform(
            target_frame = self.drone_odom_frame_id,  
            source_frame = vector.header.frame_id,                 
            time=rclpy.time.Time() )
        new_vector = tf2_geometry_msgs.do_transform_vector3(vector, t)
        sam_vel_odom = [new_vector.vector.x, new_vector.vector.y]
        return np.array(sam_vel_odom) 
    
    def initiatePrior(self, GPS_ping_odom:np.array):
        """ Initiate Gaussian prior in the odom_gt frame"""
        prior = np.exp(-((self.X - GPS_ping_odom[0]) ** 2 + (self.Y - GPS_ping_odom[1]) ** 2) / self.variance  ** 2)
        prior /= np.sum(prior)
        return prior
    
    
    def createMap(self, gps_ping_odom:np.array) -> None: 
        """Function that creates the grid map which the calculations are based in. """

        # create grid map as attributes (position and time wise)
        dim = np.array([self.w, self.h])
        corner_1 = gps_ping_odom - dim/2 
        corner_2 = gps_ping_odom + dim/2 
        x = np.arange(corner_1[0], corner_2[0] + self.resol, self.resol)
        y = np.arange(corner_1[1], corner_2[1] + self.resol, self.resol)
        self.X, self.Y = np.meshgrid(x[:-1] + self.resol / 2, y[:-1] + self.resol / 2)
        self.Y = self.Y[::-1]
        self.Ncells_x, self.Ncells_y = self.X.shape[1], self.X.shape[0]
        self.map_Time = np.empty([self.Ncells_x, self.Ncells_y])
        self.init_timestamp = self.get_clock().now().nanoseconds
        self.map_Time[:,:] = self.init_timestamp  

        # create grid map as ros msg
        self.grid_map_translation = [int((self.w/2)/self.resol), int((self.h/2)/self.resol)]
        self.X_min, self.X_max = np.min(self.X) -self.resol/2, np.max(self.X) +self.resol/2
        self.Y_min, self.Y_max = np.min(self.Y) -self.resol/2, np.max(self.Y) +self.resol/2
        self.origin = Pose() # in /Quadrotor/odom_gt frame
        self.origin.position.x = gps_ping_odom[0] - self.w/2 
        self.origin.position.y = gps_ping_odom[1] - self.h/2 
        # TODO: give correct orientation
        self.origin.orientation.x = 0.0
        self.origin.orientation.y = 0.0
        self.origin.orientation.z = 0.0
        self.origin.orientation.w = 1.0

        self.map = OccupancyGrid()
        self.map.header.frame_id = self.drone_odom_frame_id
        self.map.header.stamp = self.get_clock().now().to_msg() 
        self.initial_map_time =  self.get_clock().now().nanoseconds
        self.map.info.width = self.Ncells_x
        self.map.info.height = self.Ncells_y
        self.map.info.resolution = self.resol
        self.map.info.origin = self.origin  

    def map_seen(self):
        """ Compute the ratio of the map area already seen by the search planner """
        mask  = self.map_Time !=  self.init_timestamp
        return np.sum(mask,axis = None) / (mask.shape[0]*mask.shape[1])


    def map_probabilities(self, data):
        """ Map probabilities to values between 0 and 100, as required by OccupancyGrid message in ros"""
        min = np.min(data) # or sys.float_info.min ?
        max = 1    
        new_min = 0
        new_max = 100
        slope = (new_max - new_min)/(max - min)
        return np.int8(slope*(data - max) + new_max)

 
    def sam_odom_callback(self, msg:Odometry):
        """ Retrieve SAM position (map_gt)"""
        self.sam_vel.vector.x = msg.twist.twist.linear.x 
        self.sam_vel.vector.y = msg.twist.twist.linear.y
        self.sam_vel.vector.z = msg.twist.twist.linear.z 
        self.sam_vel.header = msg.header #np.array([msg.twist.twist.linear.x, msg.twist.twist.linear.y])

    def drone_odom_callback(self, msg: Odometry):
        """ Retrieve drone position (map_gt)"""
        self.drone_position.point = msg.pose.pose.position
        self.drone_position.header = msg.header

