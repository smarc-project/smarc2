#!/usr/bin/python
import sys
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from math import dist
from smarc_mission_msgs.srv import DronePath, InitAUVSearch
from geometry_msgs.msg import PoseArray, Pose, PointStamped
from .prob_grid_map import ProbabilisticGridMap 
from .path_planners import InitializeActions, SpiralPathModel, GreedyPathModel, AStarPathModel, APFPathModel
from smarc_utilities.georef_utils import convert_latlon_to_utm

##############################################################################
# TODO
##############################################################################
"""
Different path planners should be triggered by the behavior tree or by a more robust function.
""" 

##############################################################################
##############################################################################

class SearchPlannerController(Node):
    """ 
    This node creates instances of grid_map and path planner classes and controls them via timer. 

    Attributes (the relevant ones):
        countsToInitialize<...>: the count attributes (grid map and path planner) impose a time delay in the initialization of the corresponding procedure.

    """
    def __init__(self):
        super().__init__(
            'SearchPlanner_Controller',
            allow_undeclared_parameters=True,
            automatically_declare_parameters_from_overrides=True
        )
        self.get_params() 
        self.sim_commands = InitializeActions(params = self.model_params)

        # services initialization
        self.init_search_srv = self.create_service(srv_type = InitAUVSearch,
                                       srv_name = 'init_auv_search',
                                       callback = self.init_search_srv_callback)
        self.get_path = self.create_service(srv_type = DronePath,
                                       srv_name = 'get_quadrotor_path',
                                       callback = self.get_path_srv_callback)

        # initialize flags and counters to manage path planner and grid map timers
        self.path_node_time_count = 0
        self.gridmap_node_time_count = 0

        self.init_done = False
        self.path_initiated = False
        self.callback_running = False
        self.simulation_finished = False
        

        # calculate necessary timer calls (counts) to perform a task. Planner will only start when the update in the grid map is
        # ready to be applied (otherwise the drone will start moving but the cells' probabilities won't be updated)
        self.path_update_dt = 0.2 # it's not that relevant, therefore there isn't need to be in the launch file
        self.grid_update_dt = self.model_params['grid_map.update.rate']
        self.countsToInitializeMap =  int(self.model_params['initialization.time_delay']/self.grid_update_dt) + 1
        self.countsToUpdateMap = self.countsToInitializeMap + int(self.model_params["grid_map.update.time_margin"]/self.grid_update_dt)
        self.countsToInitializePlanner =  int(self.model_params['initialization.time_delay']/self.path_update_dt) + 1 + int(self.model_params["grid_map.update.time_margin"]/self.path_update_dt)
        
        # teleport SAM (sim) and initialize GPS ping and drone position
        self.drone_init_pos = None
        self.GPS_ping = None
        if self.model_params['mode'] == 'sim':
            self.sim_commands.teleport_sam()

        # initialize planner and grid map but without GPS ping and drone position; move drone to flight height (solely vertically)
        self.grid_map = ProbabilisticGridMap(params = self.model_params)
        planner_dict = {'spiral': SpiralPathModel,
                        'greedy': GreedyPathModel,
                        'astar': AStarPathModel,
                        'apf': APFPathModel}
        try:
            self.planner = planner_dict[self.model_params['path_planner']](params = self.model_params, grid_map = self.grid_map)
        except:
            self.get_logger().error('Incorrect path planner label! Check launch and README files')

    def init_search_srv_callback(self, request, response):
        """ 
        Stores the GPS_ping (after transforming it to map) and desired quadrotor initial position, 
        which will trigger path generation in respective timer.
        """
        # if activated by client, quadrotor doesn't perform initial movement (assigning purposes only)
        self.drone_init_pos = PointStamped()
        self.drone_init_pos.header.frame_id = self.model_params['frames.id.quadrotor_odom']      

        # get search radius (range) convert GPS ping to correct coordinates
        self.grid_map.w = self.grid_map.h = 2*request.radius
        self.GPS_ping_utm = convert_latlon_to_utm(request.gps)
        self.GPS_ping = self.planner.transform_point(self.GPS_ping_utm, self.model_params['frames.id.map'])
        response.success = True

        # (re)initialize planner (including grid map)
        self.grid_map.GPS_ping = self.GPS_ping
        self.planner.reinitialize_planner()
        return response

    def get_path_srv_callback(self, request, response):
        """ Generates path and converts to PoseArray"""
        if request.data:
            _ , path = self.planner.generate_path() 
            path_msg = PoseArray()
            pose_list = []
            for i, position in enumerate(path):
                pose = Pose()
                pose.position.x = position[0]
                pose.position.y = position[1]
                pose.position.z = self.model_params["drone.flight_height"]
                pose_list.append(pose)
            path_msg.poses = pose_list
            path_msg.header.frame_id = self.model_params['frames.id.quadrotor_odom']
            path_msg.header.stamp = self.get_clock().now().to_msg()
            response.path = path_msg 
            return response
        else: return None


    """ --- Management of drone initial position and GPS ping retrievals """

    def get_initial_info(self):
        """ timer to continously try to get GPS ping and initial quadrotor's position """
        self.get_logger().info("Waiting for quadrotor's initial position and GPS ping ...")
        self.initial_info = self.create_timer(0.1, self.attemp_retrieval)

    def attemp_retrieval(self):
        """ 
        Attempts to retrieve the GPS ping and the quadrotor's position in map_gt until both are != None. The
        planner will only be executed when these variables are retrieved, which is triggered by the flag init_done.

        If initial drone position is defined, the search planner will wait for the drone until it's sufficiently close
        to that position. Otherwise (position.<coordinate> == None), the search planner won't wait.
        """
        if not self.initial_info.is_canceled():
            if self.model_params['mode'] == 'sim':
                if self.drone_init_pos is None:
                    self.drone_init_pos = self.sim_commands.get_init_quadrotor_position()

                if self.GPS_ping is None:
                    self.GPS_ping = self.sim_commands.get_GPSxy_ping()

            if self.drone_init_pos is not None and self.GPS_ping is not None:
                self.initial_info.cancel()
                self.grid_map.GPS_ping = self.GPS_ping
                self.get_logger().info(f'Received GPS ping (x,y) = {round(float(self.GPS_ping.point.x),2), round(float(self.GPS_ping.point.y),2)}')
                if None in (self.drone_init_pos.point.x, self.drone_init_pos.point.y,  self.drone_init_pos.point.z):
                    self.init_done = True
                else: # create timer to relocate drone (valid only in mode = sim)
                    if self.model_params['mode'] == 'sim':
                        self.relocate_timer = self.create_timer(0.5, self.check_drone_position)
                    else:
                        self.init_done = True

    def check_drone_position(self):
        """ Continously publish initial waypoint and checking distance"""
        x_odom, y_odom = self.planner.generate_waypoint(self.drone_init_pos.point.x,
                                        self.drone_init_pos.point.y,
                                        self.drone_init_pos.point.z)
        if dist([x_odom, y_odom], [self.drone_init_pos.point.x, self.drone_init_pos.point.y]) < 0.5:
            self.relocate_timer.cancel()
            self.init_done = True



    """ --- Management of path planner """

    def run_path_planner(self):
        """ timer to continously produce and check path """
        self.path_timer = self.create_timer(self.path_update_dt, self.update_path)

    
    def update_path(self):
        """ Path planner timer callback. It will continously see if a new path needs to be produced or if a new waypoint
        needs to be published, which is done in the generate_path method """

        if self.init_done:
            if self.path_node_time_count <= self.countsToInitializePlanner: 
                self.path_node_time_count += 1
            else:
                self.path_initiated = True
                if self.callback_running:
                    self.get_logger().warn("Callback still running, skipping this tick.")
                    return
                self.callback_running = True
                try:
                    safe_path, _ = self.planner.generate_path()
                    if not safe_path:
                        self.path_timer.cancel()
                        self.return_to_base()

                finally:
                    self.callback_running = False

    """ --- Management of grid map """

    def run_grid_map(self):
        """ timer to continously update grid map """
        self.create_timer(self.grid_update_dt, self.update_grid_map)

    def update_grid_map(self):
        """ Grid map timer callback. It will update the map with Bayes Filtering over and over"""
        if self.init_done:
            if self.gridmap_node_time_count == self.countsToInitializeMap:
                self.planner.grid_map.initiate_grid_map()
            elif self.gridmap_node_time_count >= self.countsToUpdateMap and self.path_initiated:
                self.planner.grid_map.apply_bayes_filter()
                if self.gridmap_node_time_count > self.countsToUpdateMap:
                    return  
            elif self.gridmap_node_time_count == self.countsToUpdateMap and not self.path_initiated:
                return

            self.gridmap_node_time_count += 1

    
    """ --- Management of returning motion """

    def return_to_base(self):
        """ This method will be called by the main function when the generate_path method return False. This will happen when
        the battery is considered too low to finish the motion, ie, finishing the current path and returning to base """

        self.get_logger().info('Simulation will end (low battery or SAM was found), returning to base.')
        self.return_timer = self.create_timer(0.5, self.return_timer_callback)

    def return_timer_callback(self):
        """ Timer that continously checks when the drone is sufficiently close to the base (origin of odom frame)"""
        odom_x, odom_y = self.planner.return_to_base()
        thresh = 0.5
        if abs(odom_x) < thresh and abs(odom_y) < thresh:
            self.return_timer.cancel()
            self.simulation_finished = True


    """ --- Parameters declaration """

    def get_params(self):
        # Retrieve parameters
        self.model_params = {
            "mode": self.get_parameter("mode").value,
            "path_planner": self.get_parameter("path_planner").value,
            'initialization.time_delay': self.get_parameter("initialization.time_delay").value,

            "drone.init_pos": self.get_parameter("drone.init_pos").value,
            "drone.flight_height": self.get_parameter("drone.flight_height").value,
            "drone.camera_fov": self.get_parameter("drone.camera_fov").value,
            "drone.look_ahead_time": self.get_parameter("drone.look_ahead_time").value,
            "drone.intermediate_dt": self.get_parameter("drone.intermediate_dt").value,

            "spiral.vel_factor": self.get_parameter("spiral.vel_factor").value,
            "spiral.dtheta": self.get_parameter("spiral.dtheta").value,

            'greedy.horizon_radius': self.get_parameter("greedy.horizon_radius").value,

            "astar.obstacles.max_length": self.get_parameter("astar.obstacles.max_length").value,
            "astar.obstacles.quantile_per": self.get_parameter("astar.obstacles.quantile_per").value,
            "astar.obstacles.obstacles_per": self.get_parameter("astar.obstacles.obstacles_per").value,
            'astar.horizon_radius': self.get_parameter("astar.horizon_radius").value,

            'arf.k_attractive': self.get_parameter("arf.k_attractive").value,
            'arf.k_repulsive': self.get_parameter("arf.k_repulsive").value,
            'arf.goal_distance_factor': self.get_parameter("arf.goal_distance_factor").value,
            'arf.d_min': self.get_parameter("arf.d_min").value,
            'arf.d_max': self.get_parameter("arf.d_max").value,
            'arf.horizon_radius': self.get_parameter("arf.horizon_radius").value,
            
            "sam.init_pos": self.get_parameter("sam.init_pos").value,
            "sam.init_pos_variance": self.get_parameter("sam.init_pos_variance").value,
            'sam.vel_variance': self.get_parameter('sam.vel_variance').value,
            'sam.max_floating_vel': self.get_parameter('sam.max_floating_vel').value, 

            "grid_map.workspace.width": self.get_parameter("grid_map.workspace.width").value,
            "grid_map.workspace.height": self.get_parameter("grid_map.workspace.height").value,
            "grid_map.workspace.resol": self.get_parameter("grid_map.workspace.resol").value,
            "grid_map.sam_variance": self.get_parameter("grid_map.workspace.variance").value,
            'grid_map.update.rate': self.get_parameter('grid_map.update.rate').value,
            "grid_map.update.true_detection_rate": self.get_parameter("grid_map.update.true_detection_rate").value,
            "grid_map.update.time_margin": self.get_parameter("grid_map.update.time_margin").value,

            "battery.discharge_rate": self.get_parameter("battery.discharge_rate").value,
            "battery.threshold": self.get_parameter("battery.threshold").value,
            "battery.equivalent_drone_vel": self.get_parameter("battery.equivalent_drone_vel").value,

            'frames.id.map': self.get_parameter('frames.id.map').value,
            'frames.id.quadrotor_odom': self.get_parameter('frames.id.quadrotor_odom').value,
            'frames.id.sam_odom': self.get_parameter('frames.id.sam_odom').value


        }
        

def main():
    """ 
    Function that initiates the appropriate timers (grid map, path generation). The difference between 'mode' = 'real'
    and 'mode' = 'sim' resides on the triggering flag and sam teleportation. 
    
    In 'sim', it's assumed the user wants to test the pkg standalone. Hence, as soon this file is launched, 
    SAM is teleported and the search planning initiates. 
    
    In 'real', the user has to request the initialization and the path generation via service. Check readme for + info
    """

    rclpy.init(args=sys.argv)
    controller = SearchPlannerController()
    executor = MultiThreadedExecutor()
    executor.add_node(controller)
    executor.add_node(controller.sim_commands)
    executor.add_node(controller.planner)
    executor.add_node(controller.planner.grid_map)

    # timer that continously checks if we have the GPS ping and in that case corresponding flag (init_done) is set to true
    controller.get_initial_info() 

    # if flag is true, these timers trigger search planning, otherwise nothing happens. In 'sim', the path is automatically
    # generated over and over again. In 'real', it's the service request that triggers path generation
    controller.run_grid_map()
    if controller.model_params['mode'] == 'sim':
        controller.run_path_planner()

    try:
        while True and rclpy.ok() and not controller.simulation_finished:
            executor.spin_once()
    except KeyboardInterrupt:
        return
    pass
    


if __name__ == '__main__':
    main()