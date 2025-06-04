from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os
from math import pi

def generate_launch_description():
    robot_name = LaunchConfiguration('robot_name')

    # All configurable parameters (sorted by relevance)
    params = {

    # --- choose path planner and vehicles' initial positions
    'mode': 'sim', # 'sim', 'real'
    'path_planner': 'apf', # 'spiral', 'greedy', 'astar', 'apf'
    'sam.init_pos': [float(1277.0), float(1146.0)], # position to which sam will teleport (in map). User-defined, only useful in simulation
    'drone.init_pos': [float(1297.0), float(1160.0),float(3)], # position to which drone will teleport (in odom). User-defined, only useful in simulation

    # --- common parameters to all path planners
    'initialization.time_delay': float(4),
    'flight_height': 6.0,
    'camera_fov': 82.0,
    'intermediate_dt': float(2.0), # dt between path points in case drones gets too unstable.
    # lat [s] × velocity sets the waypoint distance threshold. Recommended values for distance cap = 1: 
    # Spiral = 0.6, Greedy = 3, A* = 2.
    'look_ahead_time': float(2), 

    # --- Spiral planner parameters
    'spiral.vel_factor': 1.0, # the spiral center will move x times faster than AUV. Turn it to 0 to make a static spiral
    'spiral.dtheta': float(pi/6), #increments in angle between spiral points (smaller value -> more points per spiral)

    # --- Greedy parameters (greedy)
    'greedy.horizon_radius': float(-1), # Heuristic planners pick the highest-probability cell within radius x; -1 uses full workspace

    # --- AStar planner parameters
    'astar.obstacles.max_length' : 0.8, #threshold on obstacle dimension wrt the minimum dimension of the workspace (rectangle)
    'astar.obstacles.quantile_per': 70, # quantile of cells from which we'll try to define obstacles (x % of cells with lowest probability)
    'astar.obstacles.obstacles_per': 5, # from cells chosen above, we'll chose a fraction randomly to define obstacles
    'astar.horizon_radius': float(-1), # Heuristic planners pick the highest-probability cell within radius x; -1 uses full workspace

    # --- Artificial Potential Field (ARF) parameters
    #'arf.look_ahead_time': 5, # different from regular lat: it will say how far the waypoint is from current position, not a distance threshold!
    'arf.k_attractive': 100, # k constant for attractive potential field (bigger -> goal will attract more)
    'arf.k_repulsive': 85, # k constant for repulsive potential field (bigger -> neighbouring cells will repulse more)
    'arf.goal_distance_factor': 90, # factor to determine how far is the goal (bigger factor -> smaller acceleration by resultant of forces -> closer goal). Think of it as mass
    'arf.d_min': 2, # (minimum) distance threshold to define which cells will exert repulsive force
    'arf.d_max': 25, # (maximum) distance threshold to define which cells will exert repulsive force
    'arf.horizon_radius': float(50), # arf planner picks the highest-probability cell within radius x; -1 uses full workspace

    # --- + SAM configs
    'sam.initial_state.pos_variance': 10, # variance considered when sampling the pseudo GPS ping (sam position + noise)
    'sam.vel_variance': 4.0, # variance considered when getting SAM velocity with noise (simulating real conditions, noise is Gaussian). Not used for now
    'sam.max_floating_vel': 2.0, # maximum SAM velocity on water due to wind + waves. It's used in spiral to define a correct spiral

    # --- Grid Map workspace and update parameters
    'grid_map.workspace.width': float(120.0),
    'grid_map.workspace.height': float(120.0),
    'grid_map.workspace.resol': float(2), 
    'grid_map.workspace.variance': 10.0, # gaussian variance considered in the prior distribution (initial grid map)
    'grid_map.update.rate': 0.5, # frequency of Bayes Filter runs (prediction + update)
    'grid_map.update.true_detection_rate': 1.0 - 1e-10, # parameter used in Bayes filter -> probability of having a true positive
    'grid_map.update.time_margin': 10.0, # parameter to avoid updating repeated cells -> don't update cells that were updated x or less seconds ago

    # --- Battery parameters
    'battery.discharge_rate': 1.0, # % per min
    'battery.threshold': 20, # after planning a path, if the final estimated battery % is below this threshold, the drone will return to base instead

    # [m/s] -> (constant) velocity used in the time duration estimation of each path. This value is only used if velocity = 0 at the the time of the 
    # calculation, otherwise the current drone velocity will be used. Set it to a small value
    'battery.equivalent_drone_vel': 1.0, 

    # # --- Drone initial state (in map_gt), don't change unless there was a change in frames
    # 'drone_initial_state.position': [1297.0, 1156.0, 1.1628761291503906], # (x, y, z)
    # 'drone_initial_state.orientation': [-3.285610546299722e-06, -2.3353104552370496e-06, -0.3826446831226349, -0.923895537853241], #x,y,z,w

    # --- Frame's names
    'frames.id.quadrotor_map': 'map_gt_gt',
    'frames.id.quadrotor_odom': 'Quadrotor/odom_gt',
    'frames.id.auv_map': 'map_gt_gt',
    'frames.id.auv_odom': 'Quadrotor/odom_gt',

    }

    return LaunchDescription([
        DeclareLaunchArgument(
            'robot_name',
            default_value='Quadrotor'
        ),
        Node(
            package='alars_auv_search_planner',
            executable='search_planner_controller',
            namespace=robot_name,
            output='screen',
            parameters=[params]
        )
    ])
