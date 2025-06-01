#!/usr/bin/python
import sys
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor, SingleThreadedExecutor
from .prob_grid_map import ProbabilisticGridMap 
from .path_planners import SimActions, SpiralPathModel, GreedyPathModel, AStarPathModel, APFPathModel


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
        self.sim_commands = SimActions(params = self.model_params) 
        self.sim_commands.teleport_sam()
        GPS_ping = self.sim_commands.create_GPS_ping()
        self.grid_map = ProbabilisticGridMap(params = self.model_params, GPS_ping_odom = GPS_ping)

        # instantiate path planner and move drone to flight height (solely vertically)
        if self.model_params['path_planner'] == 'spiral':
            self.planner = SpiralPathModel(params = self.model_params, GPS_ping = GPS_ping, grid_map = self.grid_map)
        elif self.model_params['path_planner'] == 'greedy':
            self.planner = GreedyPathModel(params = self.model_params, GPS_ping = GPS_ping, grid_map = self.grid_map)
        elif self.model_params['path_planner'] == 'astar':
            self.planner = AStarPathModel(params = self.model_params, GPS_ping = GPS_ping, grid_map = self.grid_map)
        elif self.model_params['path_planner'] == 'apf':
            self.planner = APFPathModel(params = self.model_params, GPS_ping = GPS_ping, grid_map = self.grid_map)
        else:
            self.get_logger().error('Incorrect path planner label! Check launch file')
        self.planner.generate_point(0.0, 0.0, self.planner.flight_height)
        
        # initialize flags and counters to manage path planner and grid map timers
        self.path_node_time_count = 0
        self.gridmap_node_time_count = 0

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
        
    """ --- Management of path planner """

    def run_path_planner(self):
        """ timer to continously produce and check path """
        self.path_timer = self.create_timer(self.path_update_dt, self.update_path)

    
    def update_path(self):
        """ Path planner timer callback. It will continously see if a new path needs to be produced or if a new waypoint
        needs to be published, which is done in the generate_path method """

        if self.path_node_time_count <= self.countsToInitializePlanner: 
            self.path_node_time_count += 1
        else:
            self.path_initiated = True
            if self.callback_running:
                self.get_logger().warn("Callback still running, skipping this tick.")
                return
            self.callback_running = True
            try:
                if not self.planner.generate_path():
                    self.path_timer.cancel()
                    self.return_to_base()

            finally:
                self.callback_running = False
        return

    """ --- Management of grid map """

    def run_grid_map(self):
        """ timer to continously update grid map """
        self.create_timer(self.grid_update_dt, self.update_grid_map)

    def update_grid_map(self):
        """ Grid map timer callback. It will update the map with Bayes Filtering over and over"""
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
            "path_planner": self.get_parameter("path_planner").value,
            'initialization.time_delay': self.get_parameter("initialization.time_delay").value,
            "flight_height": self.get_parameter("flight_height").value,
            "camera_fov": self.get_parameter("camera_fov").value,
            "look_ahead_time": self.get_parameter("look_ahead_time").value,
            "intermediate_dt": self.get_parameter("intermediate_dt").value,

            "spiral.vel_factor": self.get_parameter("spiral.vel_factor").value,
            "spiral.dtheta": self.get_parameter("spiral.dtheta").value,

            'greedy.horizon_radius': self.get_parameter("greedy.horizon_radius").value,

            "astar.obstacles.max_length": self.get_parameter("astar.obstacles.max_length").value,
            "astar.obstacles.quantile_per": self.get_parameter("astar.obstacles.quantile_per").value,
            "astar.obstacles.obstacles_per": self.get_parameter("astar.obstacles.obstacles_per").value,
            'astar.horizon_radius': self.get_parameter("astar.horizon_radius").value,

            #'arf.look_ahead_time': self.get_parameter("arf.look_ahead_time").value,
            'arf.k_attractive': self.get_parameter("arf.k_attractive").value,
            'arf.k_repulsive': self.get_parameter("arf.k_repulsive").value,
            'arf.goal_distance_factor': self.get_parameter("arf.goal_distance_factor").value,
            'arf.d_min': self.get_parameter("arf.d_min").value,
            'arf.d_max': self.get_parameter("arf.d_max").value,
            'arf.horizon_radius': self.get_parameter("arf.horizon_radius").value,

            "sam.initial_state.position": self.get_parameter("sam.initial_state.position").value,
            "sam.initial_state.pos_variance": self.get_parameter("sam.initial_state.pos_variance").value,
            'sam.vel_variance': self.get_parameter('sam_.vel_variance').value,
            'sam.max_floating_vel': self.get_parameter('sam.max_floating_vel').value, 

            "grid_map.workspace.center": self.get_parameter("grid_map.workspace.center").value,
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

            "drone_initial_state.position": self.get_parameter("drone_initial_state.position").value,
            "drone_initial_state.orientation": self.get_parameter("drone_initial_state.orientation").value,

        }
        

def main():
    rclpy.init(args=sys.argv)
    controller = SearchPlannerController()
    executor = MultiThreadedExecutor()
    executor.add_node(controller)
    executor.add_node(controller.planner)
    executor.add_node(controller.planner.grid_map)
    controller.run_path_planner()
    controller.run_grid_map()
    try:
        while True and rclpy.ok() and not controller.simulation_finished:
            executor.spin_once()
    except KeyboardInterrupt:
        return
    pass


if __name__ == '__main__':
    main()