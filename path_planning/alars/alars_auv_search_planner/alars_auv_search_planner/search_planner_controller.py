#!/usr/bin/python
import sys
import os
from math import tan, dist, pi
import time
import numpy as np
from dotenv import load_dotenv
import mlflow

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from math import dist
from smarc_mission_msgs.srv import DronePath, InitAUVSearch
from geometry_msgs.msg import PoseArray, Pose, PointStamped
from .prob_grid_map import ProbabilisticGridMap 
from .path_planners import InitializeActions, SpiralPathModel, GreedyPathModel, AStarPathModel, APFPathModel
from smarc_utilities.georef_utils import convert_latlon_to_utm

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
        
        # set up depending on mode
        if self.model_params["mode"] == 'srv':
            self.init_search_srv = self.create_service(srv_type = InitAUVSearch,
                                        srv_name = 'init_auv_search',
                                        callback = self.init_search_srv_callback)
            self.get_path = self.create_service(srv_type = DronePath,
                                        srv_name = 'get_quadrotor_path',
                                        callback = self.get_path_srv_callback)
        elif self.model_params["mode"] == 'sim':
            self.sim_commands = InitializeActions(params = self.model_params)

        # initialize flags and counters to manage path planner and grid map timers
        self.path_node_time_count = 0
        self.gridmap_node_time_count = 0

        self.init_done = False if self.model_params["mode"] != 'as' else True
        self.path_initiated = False
        self.callback_running = False
        self.simulation_finished = False
        

        # calculate necessary timer calls (counts) to perform a task. Planner will only start when the update in the grid map is
        # ready to be applied (otherwise the drone will start moving but the cells' probabilities won't be updated)

        self.path_update_dt = 0.2 # it's not that relevant, therefore there isn't need to be in the launch file
        self.grid_update_dt = self.model_params['grid_map.update.rate']
        if self.model_params["mode"] == "sim": # in sim we have to "manually" ensure the grid map and path are set up before we start
            self.countsToInitializeMap =  int(self.model_params['initialization.time_delay']/self.grid_update_dt) + 1
            self.countsToUpdateMap = self.countsToInitializeMap + int(self.model_params["grid_map.update.time_margin"]/self.grid_update_dt)
        else:
            self.countsToInitializeMap = 0
            self.countsToUpdateMap = 1
        self.countsToInitializePlanner = self.countsToUpdateMap + int(self.model_params["grid_map.update.time_margin"]/self.grid_update_dt)


        
        # teleport SAM  and initialize testing procedures (sim)
        self.drone_init_pos = None
        self.GPS_ping = None
        if self.model_params['mode'] == 'sim':
            self.sim_commands.teleport_sam()
            self.PATH_DISTANCE, self.PATH_TIME = [], []
            try:
                load_dotenv()
                uri = os.getenv('URI')
                mlflow.set_tracking_uri(uri=uri) #NOTE set the tracking server's uri for experiment puporses 
            except:
                self.get_logger().warn("Couldn't connect to mlflow tracking server, proceding without result tracking ...")

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
            assert False, "path planner param only accepts 'spiral', 'greedy', 'astar' or 'apf'"


    def init_search_srv_callback(self, request, response):
        """ 
        Stores the GPS_ping (after transforming it to map) and desired quadrotor initial position, 
        which will trigger path generation in respective timer.
        """
        # if activated by client, quadrotor doesn't perform initial movement (assigning purposes only)
        self.drone_init_pos = PointStamped()
        self.drone_init_pos.header.frame_id = self.model_params['frames.id.quadrotor_odom']      

        # get search radius (range) and altitude 
        self.grid_map.w = self.grid_map.h = 2*request.radius
        self.planner.flight_height = self.planner.grid_map.flight_height = request.initial_altitude + request.gps.altitude
        GPS_ping_utm = convert_latlon_to_utm(request.gps)
        self.GPS_ping = self.planner.transform_point(GPS_ping_utm, self.model_params['frames.id.map'])
        response.success = True

        # (re)initialize planner (including grid map)
        self.grid_map.GPS_ping = self.GPS_ping
        self.reinitialize_search()
        return response

    def get_path_srv_callback(self, request, response):
        """ Generates path and converts to PoseArray"""
        if request.data:
            _ , path, _ , _ = self.planner.generate_path() 
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

    def reinitialize_search(self):
        """ 
        Reinitializes grid map and planner state (called when client makes requests a new service and 
        the search planning has to be reinitiated without destroying the node)
        """
        if self.model_params['path_planner'] == 'spiral': self.planner.phase = 'line'
        if self.model_params['mode'] == 'as': self.init_done = True 
        self.planner.path_needed = True
        self.planner.path_completed = False
        self.planner.grid_map.initiate_grid_map()


    """ --- Management of drone initial position and GPS ping retrievals """

    def get_initial_info(self):
        """ timer to continously try to get GPS ping and initial quadrotor's position """
        self.get_logger().info("Waiting for quadrotor's initial position and GPS ping ...")
        self.initial_info = self.create_timer(0.1, self.attemp_retrieval)

    def attemp_retrieval(self):
        """ 
        Ensures the planner has GPS ping and the quadrotor's position in map_gt before initiating searching. The
        planner will only be executed when these variables are retrieved, which indicated by the flag init_done.

        In 'sim' mode, if initial drone position is defined, the search planner will wait for the drone until it's 
        sufficiently close to that position. Otherwise (position.<coordinate> == None), the search planner won't wait.
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
                if self.model_params["mode"] == 'sim':
                    if self.finish_experiment():
                        self.path_timer.cancel()
                        self.return_to_base()
                try:
                    safe_path, _, distance, time = self.planner.generate_path()
                    if distance != 0 and self.model_params["mode"] == 'sim': 
                        self.PATH_DISTANCE.append(distance)
                        self.PATH_TIME.append(time)
                    if not safe_path:
                        self.path_timer.cancel()
                        self.return_to_base()

                finally:
                    self.callback_running = False

    """ --- Management of grid map """

    def run_grid_map(self):
        """ timer to continously update grid map """
        self.START = time.time()
        self.create_timer(self.grid_update_dt, self.update_grid_map)

    def update_grid_map(self):
        """ Grid map timer callback. It will update the map with Bayes Filtering over and over"""
        map_seen = 0
        if self.init_done:
            if self.gridmap_node_time_count == self.countsToInitializeMap:
                self.planner.grid_map.initiate_grid_map()
            elif self.gridmap_node_time_count >= self.countsToUpdateMap and self.path_initiated:
                map_seen = self.planner.grid_map.apply_bayes_filter()
                if self.gridmap_node_time_count > self.countsToUpdateMap:
                    return map_seen
            elif self.gridmap_node_time_count == self.countsToUpdateMap and not self.path_initiated:
                return map_seen

            self.gridmap_node_time_count += 1
            return map_seen
        return map_seen

    
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
            'frames.id.sam_odom': self.get_parameter('frames.id.sam_odom').value,

            'topics.move_drone': self.get_parameter('topics.move_drone').value,
            'topics.teleport_sam': self.get_parameter('topics.teleport_sam').value,
            'topics.drone_odom': self.get_parameter('topics.drone_odom').value,
            'topics.sam_odom': self.get_parameter('topics.sam_odom').value,
            'topics.sam_detection': self.get_parameter('topics.sam_detection').value,

            'topics.pub_path': self.get_parameter('topics.pub_path').value,
            'topics.pub_grid_map': self.get_parameter('topics.pub_grid_map').value,
            'topics.pub_likely_sam_location': self.get_parameter('topics.pub_likely_sam_location').value
            
        }
    
    def finish_experiment(self):
        """ 
        Experiment purposes only: checks when drone reaches AUV and logs parameters and metrics
        into a mlflow server, as long as uri is properly set up
        """
        TEST_SCHEDULE = "1"
        RUN_COUNTER = "4"
        INDEP_VAR = str(self.model_params["grid_map.sam_variance"])

        drone_pos = self.planner.drone_position.point.x, self.planner.drone_position.point.y
        sam_pos = self.planner.sam_position.point.x, self.planner.sam_position.point.y
        if dist(drone_pos, sam_pos) <= tan((pi/180)*self.model_params["drone.camera_fov"]/2)*self.planner.drone_position.point.z:
            self.get_logger().info("Experiment ended, logging information ...")
            self.END = time.time()
            prior = "UniPeakGaussian" # UniPeakGaussian, BiPeakGaussian, AsynGaussian

            params = {
                "PlannerType": self.model_params["path_planner"],
                "SAM_Variance": self.model_params["sam.init_pos_variance"],
                "GPS_Variance": self.model_params["grid_map.sam_variance"],
                "Dist2AUV": self.calc_init_distance(),
                "PriorType": prior, 
                "Height": self.model_params["drone.flight_height"],
                "Resol": self.model_params["grid_map.workspace.resol"],
                "AUV_Vel": 0
            }
            metrics = {
                "TimeOfFlight": self.END - self.START,
            }
            dist_time_rows = np.array(list(zip(self.PATH_DISTANCE, self.PATH_TIME)))
            np.savetxt('results.csv', dist_time_rows, delimiter=",", fmt='%s')

            mlflow.set_experiment(experiment_name = self.model_params["path_planner"] + "_" + TEST_SCHEDULE) # `spiral`, `greedy`, `astar`, or `apf`)
            with mlflow.start_run(run_name = prior + INDEP_VAR + "_run_"+RUN_COUNTER, 
                                  description= self.model_params["path_planner"] + " planner experiment"):
                mlflow.log_params(params)
                mlflow.log_metrics(metrics)
                mlflow.log_artifact("results.csv")
                
            return True
        return False

    def calc_init_distance(self)-> float:
        drone_pos_odom, sam_pos = PointStamped(), PointStamped()
        drone_pos_odom.point.x = self.model_params["drone.init_pos"][0]
        drone_pos_odom.point.y = self.model_params["drone.init_pos"][1]
        sam_pos.point.x = self.model_params["sam.init_pos"][0]
        sam_pos.point.y = self.model_params["sam.init_pos"][1]

        drone_pos_odom.header.frame_id = self.model_params['frames.id.quadrotor_odom']
        sam_pos.header.frame_id = self.model_params['frames.id.map']
        drone_pos_odom.header.stamp = sam_pos.header.stamp = self.get_clock().now().to_msg()

        drone_pos = self.planner.transform_point(point = drone_pos_odom, frame = self.model_params['frames.id.map']) 

        return dist((drone_pos.point.x, drone_pos.point.y), ((sam_pos.point.x, sam_pos.point.y)))


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
    executor.add_node(controller.planner)
    executor.add_node(controller.planner.grid_map)
    if controller.model_params["mode"] == "sim": executor.add_node(controller.sim_commands)

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