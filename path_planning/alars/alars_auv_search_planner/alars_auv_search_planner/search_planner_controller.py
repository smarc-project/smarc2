#!/usr/bin/python
import sys
import os
from math import tan, dist, pi
import time
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from dji_msgs.srv import DronePath, InitAUVSearch
from geometry_msgs.msg import PoseArray, Pose, PointStamped, PoseStamped
from .prob_grid_map import ProbabilisticGridMap 
from .path_planners import InitializeActions, SpiralPathModel, GreedyPathModel, AStarPathModel, APFPathModel, SearchPlanner
from smarc_utilities.georef_utils import convert_latlon_to_utm
from dji_msgs.msg import Topics as Topics_dji
from dji_msgs.msg import Links as Links_dji
from smarc_msgs.msg import Topics as Topics_smarc
from sam_msgs.msg import Links as Links_sam

class SearchPlannerController(Node):
    """ 
    This node creates instances of grid_map and path planner classes and controls them via timer. 

    Attributes (the relevant ones):
        countsToInitialize<...>: the count attributes (grid map and path planner) impose a time delay in the initialization of the corresponding procedure.

    """
    def __init__(self):
        super().__init__(
            'search_planner_controller',
            allow_undeclared_parameters=True,
            automatically_declare_parameters_from_overrides=True
        )
        # get names of topics and links from messages package
        self.dji_topics = Topics_dji()
        self.dji_links = Links_dji()
        self.smarc_topics = Topics_smarc()
        self.sam_links = Links_sam()

        # declare parameters and store in self.model_params; 
        self.get_params() 

        # check if params values are expected
        planner_dict = {'spiral': SpiralPathModel,
                        'greedy': GreedyPathModel,
                        'astar': AStarPathModel,
                        'apf': APFPathModel}
        assert self.model_params['path_planner'] in planner_dict, 'Wrong "path_planner" param: it should be "spiral", "greedy", "astar" or "apf" '
        assert self.model_params['mode'] in ('sim', 'srv', 'as'), 'Wrong "mode" param: it should be "sim", "srv" or "as"'

        # initialize planner and grid map but without GPS ping and drone position; move drone to flight height (solely vertically)
        self.grid_map = ProbabilisticGridMap(params = self.model_params)
        self.planner: SearchPlanner = planner_dict[self.model_params['path_planner']](params = self.model_params, grid_map = self.grid_map)

        # important attributes -> have to be defined to trigger search. sam_init_pos corresponds to
        # 1st position on odom topic; drone_init_pos is "hardcoded" since the drone might not start 
        # from the desired initial position but will move to that position before starting search (in 'sim')
        self.sam_init_pos: PointStamped = None
        self.drone_init_pos: PointStamped = None
        self.GPS_ping: PointStamped = None
        
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
            self.get_sam_init_position()


        # initialize flags and counters to manage path planner and grid map timers
        self.path_node_time_count = 0
        self.gridmap_node_time_count = 0

        self.init_done = False if self.model_params["mode"] != 'as' else True
        self.map_initiated = False
        self.path_initiated = False
        self.callback_running = False
        self.simulation_finished = False
        

        # calculate necessary timer calls (counts) to perform a task. Planner will only start when the update in the grid map is
        # ready to be applied (otherwise the drone will start moving but the cells' probabilities won't be updated)
        self.path_update_dt = self.model_params['path_update_rate']
        self.grid_update_dt = self.model_params['grid_map.update.rate']

        self.countsToInitializeMap = 0
        self.countsToUpdateMap = 1
        self.countsToInitializePlanner = 2


        if self.model_params['mode'] == 'sim':
            self.PATH_DISTANCE, self.PATH_TIME = [], []
            # try:
            #     #HACK horrible, horrible thing to do... but this is what happens when 
            #     # you dont separate your research from your software development properly
            #     from dotenv import load_dotenv
            #     import mlflow
            #     load_dotenv()
            #     uri = os.getenv('URI')
            #     mlflow.set_tracking_uri(uri=uri) #NOTE set the tracking server's uri for experiment puporses 
            # except:
            #     self.get_logger().warn("Couldn't connect to mlflow tracking server, proceding without result tracking ...")




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
        """ timer to continously try to get GPS ping and initial quadrotor's position (in sim mode) """
        self.get_logger().info("Waiting for initial information ...")
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
                    self.GPS_ping: PointStamped = self.sim_commands.get_GPSxy_ping(self.planner)

            if self.GPS_ping is not None:
                self.initial_info.cancel()
                self.grid_map.GPS_ping = self.GPS_ping
                if None in (self.drone_init_pos.point.x, self.drone_init_pos.point.y,  self.drone_init_pos.point.z): #not sim, don't need initial drone's position
                    self.init_done = True
                    self.get_logger().info(f'Ready to start search')
                else: # create timer to relocate drone (valid only in mode = sim)
                    if self.model_params['mode'] == 'sim':
                        self.get_logger().info(f'Moving drone to initial position ...')
                        self.relocate_timer = self.create_timer(0.5, self.check_drone_position)
                    else:
                        self.init_done = True
                        self.get_logger().info(f'Ready to start search')

    def check_drone_position(self):
        """ 
        Continously publish initial waypoint and checking distance; only useful in sim and it allows 
        detecting when we're close to SAM without detection node (distance-based only)
        """
        x_odom, y_odom = self.planner.generate_waypoint(self.drone_init_pos.point.x,
                                        self.drone_init_pos.point.y,
                                        self.drone_init_pos.point.z)
        if None in (x_odom, y_odom): return
        
        if dist([x_odom, y_odom], [self.drone_init_pos.point.x, self.drone_init_pos.point.y]) < self.model_params["distance_threshold"]:
            self.relocate_timer.cancel()
            self.START = time.time()
            self.get_logger().info(f'Ready to start search!')
            self.init_done = True


    """ --- Management of path planner """

    def run_path_planner(self):
        """ timer to continously produce and check path """
        self.path_timer = self.create_timer(self.path_update_dt, self.update_path)

    
    def update_path(self) -> PoseStamped:
        """ 
        Path planner timer callback. It will continously see if a new path needs to be produced or if a new waypoint
        needs to be published, which is done in the generate_path method
         
        pose2pub (planner attribute) is returned as is (it might be None in the beginning of the movement) 
        and in mode = 'as', the action server is responsible for publishing it"""
        if self.init_done and self.map_initiated:
            if self.path_node_time_count <= self.countsToInitializePlanner: 
                self.path_node_time_count += 1
            else:
                self.path_initiated = True
                if self.callback_running:
                    self.get_logger().warn("Callback still running, skipping this tick.")
                    return None
                self.callback_running = True

                if self.model_params["mode"] == 'sim':
                    if self.finish_experiment():
                        self.path_timer.cancel()
                        self.return_to_base()

                try:
                    _, distance, time = self.planner.generate_path()
                    if distance != 0 and self.model_params["mode"] == 'sim': 
                        self.PATH_DISTANCE.append(distance)
                        self.PATH_TIME.append(time)
                except Exception as e:
                    self.get_logger().warn('Path generation failed; search planner could not publish waypoint')
                    self.get_logger().warn(str(e))
                    return None
                finally:
                    self.callback_running = False

        return self.planner.pose2pub

    """ --- Management of grid map """

    def run_grid_map(self):
        """ timer to continously update grid map """
        self.create_timer(self.grid_update_dt, self.update_grid_map)

    def update_grid_map(self):
        """ Grid map timer callback. It will update the map with Bayes Filtering over and over"""
        map_seen = 0
        if self.init_done:
            if self.gridmap_node_time_count == self.countsToInitializeMap: # time to initialize grid map
                try:
                    self.planner.grid_map.initiate_grid_map()
                    self.map_initiated = True
                except Exception as e:
                    self.get_logger().warn("Grid map initialization failed (most likely tf failure)")
                    self.get_logger().warn(str(e))
                    return map_seen
                
            elif self.gridmap_node_time_count >= self.countsToUpdateMap and self.path_initiated: # time to update grid map - planner has started
                map_seen = self.planner.grid_map.apply_bayes_filter()
                if self.gridmap_node_time_count > self.countsToUpdateMap: #counter var doesn't need to be incremented anymore
                    return map_seen
                
            elif self.gridmap_node_time_count == self.countsToUpdateMap and not self.path_initiated: # don't update map since search hasn't started yet
                return map_seen

            self.gridmap_node_time_count += 1

        return map_seen

    
    """ --- Management of returning motion """

    def return_to_base(self):
        """ 
        This method will be called by the main function when the generate_path method return False. 
        It's called only on sim mode, when drone has found sam """

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
        """ 
        Check parameters type and update dictionary when needed:
            - sim mode has more parameters (sam stuff that's not accessible in real life)
            - some parameters depend on others and require operations
        """
        self.sam_namespace = '/HollowSam'
        expected_types = {
            "mode": str,
            "path_planner": str,
            "path_update_rate": (int, float),
            "distance_threshold": (int, float),
            "namespace": str,

            "drone.init_pos": list,
            "drone.flight_height": (int, float),
            "drone.camera_fov": (int, float),
            "drone.look_ahead_time": (int, float),
            "drone.intermediate_dt": (int, float),

            "spiral.vel_factor": (int, float),
            "spiral.dtheta": (int, float),

            "greedy.horizon_radius": (int, float),

            "astar.obstacles.max_length": (int, float),
            "astar.obstacles.quantile_per": (int, float),
            "astar.obstacles.obstacles_per": (int, float),
            "astar.horizon_radius": (int, float),

            "arf.k_attractive": (int, float),
            "arf.k_repulsive": (int, float),
            "arf.goal_distance_factor": (int, float),
            "arf.d_min": (int, float),
            "arf.d_max": (int, float),
            "arf.horizon_radius": (int, float),

            "sam.init_pos_variance": (int, float),
            "sam.max_floating_vel": (int, float),

            "grid_map.workspace.width": (int, float),
            "grid_map.workspace.height": (int, float),
            "grid_map.workspace.resol": (int, float),
            "grid_map.workspace.variance": (int, float),
            "grid_map.update.rate": (int, float),
            "grid_map.update.true_detection_rate": (int, float),
            "grid_map.update.time_margin": (int, float),

            "frames.id.map": str,
            "frames.id.quadrotor_odom": str,

            "topics.move_drone": str,
            "topics.drone_odom": str,
            "topics.sam_detection": str,
            "topics.pub_path": str,
            "topics.pub_grid_map": str,
            "topics.pub_likely_sam_location": str,
        }

        # get dictionary with values that not correspond to frame or link names
        self.model_params = {
            k: self.get_parameter(k).value for k in expected_types
            if not k.startswith("frames") and not k.startswith("topics")
        }

        # check if link and topics names from message packages are valid
        external_constants = [
            self.dji_links.MAP,
            self.dji_links.ODOM,
            self.dji_topics.MOVE_TO_SETPOINT_TOPIC,
            self.dji_topics.ESTIMATED_AUV_TOPIC,
            self.smarc_topics.ODOM_TOPIC,
            self.sam_links.ODOM_LINK,
        ]  
        for _, name in enumerate(external_constants):
            if not isinstance(name, str):
                raise TypeError(f"One of the links/frames name should be str, got {type(name).__name__}; check import from one of the messages packages")   
                
        # include frames and links names
        self.model_params.update({
            "frames.id.map": self.model_params['namespace'].removeprefix("/") + '/' + self.dji_links.MAP,
            "frames.id.quadrotor_odom": self.model_params['namespace'].removeprefix("/") + "/" + self.dji_links.ODOM,

            "topics.move_drone": self.dji_topics.MOVE_TO_SETPOINT_TOPIC,
            "topics.drone_odom": self.smarc_topics.ODOM_TOPIC,
            "topics.sam_detection": self.dji_topics.ESTIMATED_AUV_TOPIC,
            "topics.pub_path": self.get_parameter('topics.pub_path').value,
            "topics.pub_grid_map": self.get_parameter('topics.pub_grid_map').value,
            "topics.pub_likely_sam_location": self.get_parameter('topics.pub_likely_sam_location').value,
        })

        # check their types
        for key, expected in expected_types.items():
            value = self.model_params[key]
            if not isinstance(value, expected):
                raise TypeError(f"{key} should be {expected}, got {type(value).__name__}")
            
        # If we use sim, there are additional topics/links/parameters we need to declare
        if self.model_params["mode"] != "as":
            sim_parameters = {
                "frames.id.sam_odom": self.sam_namespace.removeprefix("/") + "/" + self.sam_links.ODOM_LINK,
                "topics.sam_odom": self.sam_namespace + "/" + self.smarc_topics.ODOM_TOPIC,
            }
            self.model_params.update(sim_parameters)

        
    def finish_experiment(self):
        """ 
        Experiment purposes only: checks when drone reaches AUV and logs parameters and metrics
        into a mlflow server, as long as uri is properly set up
        """
        TEST_SCHEDULE = "1"
        RUN_COUNTER = "10"
        INDEP_VAR = str(self.model_params["grid_map.workspace.variance"])

        try:
            distance = self.planner.calculate_distance(self.planner.drone_position, self.planner.sam_position)
        except:
            self.get_logger().error(f"Couldn't compute distance to SAM: tf issue; continuing search")
            return False

        if distance <= tan((pi/180)*self.model_params["drone.camera_fov"]/2)*self.planner.drone_position.point.z:
            self.get_logger().info("Experiment ended, logging information ...")
            self.END = time.time()
            prior = "UniPeakGaussian" # UniPeakGaussian, BiPeakGaussian, AsynGaussian

            params = {
                "PlannerType": self.model_params["path_planner"],
                "SAM_Variance": self.model_params["sam.init_pos_variance"],
                "GPS_Variance": self.model_params["grid_map.workspace.variance"],
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

            # try:
            #     mlflow.set_experiment(experiment_name = self.model_params["path_planner"] + "_" + TEST_SCHEDULE) # `spiral`, `greedy`, `astar`, or `apf`)
            #     with mlflow.start_run(run_name = prior + INDEP_VAR + "_run_"+RUN_COUNTER, 
            #                         description= self.model_params["path_planner"] + " planner experiment"):
            #         mlflow.log_params(params)
            #         mlflow.log_metrics(metrics)
            #         mlflow.log_artifact("results.csv")
            # except:
            #     self.get_logger().info('Could not log experiment data!')
                
            return True
        return False

            

    def calc_init_distance(self)-> float:
        """ Calculates distance between stored sam's initial position and predefined drone's initial position"""
        return self.planner.calculate_distance(self.sam_init_pos, self.drone_init_pos)

    def get_sam_init_position(self):
        self.sam_pos_timer = self.create_timer(0.5, self.get_sam_init_position_callback)

    def get_sam_init_position_callback(self):
        if not self.sam_pos_timer.is_canceled() and self.sam_init_pos is None:
            self.sam_init_pos = self.planner.sam_position
            if self.sam_init_pos is not None:
                self.sam_pos_timer.cancel()


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