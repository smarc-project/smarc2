# Search planning parameters
A brief explanation of each parameter:

## Launch arguments (params that are changed regularly and mau be defined via CLI)

| **Parameter**    | **Description**                                                                                                                |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `mode`           | If `sim`, it's assumed the user wants to test the package standalone. If `srv`, appropriate service requests have to be made. If 'as', it works via Action Server / goal request (check main readme) |
| `namespace`      | Robot namespace - important to get correct links names                                                                         |
| `path_planner`   | `spiral`, `greedy`, `astar`, or `apf` → Path planner type. See code documentation for details.                                 |


## Drone params
| **Parameter**               | **Description**                                                                                                        |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `drone.init_pos` | Position to which the drone will move (in `odom`) at the beginning. User-defined, only useful in `sim`.                        |
| `drone.flight_height`       | \[m] Constant flight height of the drone.                                                                              |
| `drone.camera_fov`          | \[degrees] Horizontal camera field of view.                                                                            |
| `drone.intermediate_dt`     | Time step between path points if the drone becomes unstable.                                                           |
| `drone.look_ahead_time`     | Look-ahead time \[s] × velocity sets the waypoint distance threshold. Spiral = 0.6, Greedy = 3, A\* = 2 (recommended). |

## Movement params
| **Parameter**               | **Description**                                                                                                        |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `distance_threshold` | Threshold distance to waypoint that triggers next waypoint publication                        |
| `path_update_rate` | Frequency of waypoint publication; In 'as' mode, it's useless as it's the grid_map.update.rate that defines that                        |


## Spiral params
| **Parameter**       | **Description**                                                                                |
| ------------------- | ---------------------------------------------------------------------------------------------- |
| `spiral.vel_factor` | The spiral center will move `x` times faster than the AUV. Set to `0` for a static spiral center.     |
| `spiral.dtheta`     | Angle increment between spiral points in radians. Smaller values = denser spiral. (e.g., π/6). |

## Greedy params
| **Parameter**           | **Description**                                                                                 |
| ----------------------- | ----------------------------------------------------------------------------------------------- |
| `greedy.horizon_radius` | Radius within which the planner chooses the highest-probability cell. `-1` uses full workspace. |

## A* params
| **Parameter**                   | **Description**                                                                 |
| ------------------------------- | ------------------------------------------------------------------------------- |
| `astar.obstacles.max_length`    | Max obstacle size relative to the smallest workspace dimension.                 |
| `astar.obstacles.quantile_per`  | Percentile of lowest-probability cells considered for obstacle generation.      |
| `astar.obstacles.obstacles_per` | Fraction of above-selected cells that will become obstacles (randomly sampled). |
| `astar.horizon_radius`          | Radius within which the planner selects goals. `-1` uses full workspace.        |

## ARF (Artificial Potential Field) params
| **Parameter**              | **Description**                                                                              |
| -------------------------- | -------------------------------------------------------------------------------------------- |
| `arf.k_attractive`         | Attractive potential coefficient. Higher = stronger pull toward goal.                        |
| `arf.k_repulsive`          | Repulsive potential coefficient. Higher = stronger repulsion from nearby cells.              |
| `arf.goal_distance_factor` | Factor controlling how "massive" the goal feels. Higher = slower acceleration toward it.     |
| `arf.d_min`                | Minimum distance at which cells start exerting repulsive force.                              |
| `arf.d_max`                | Maximum range within which cells can exert repulsive force.                                  |
| `arf.horizon_radius`       | Radius within which the planner selects the highest-probability goal. `-1` = full workspace. |

## SAM params
| **Parameter**           | **Description**                                                            |
| ----------------------- | -------------------------------------------------------------------------- |
| `sam.init_pos_variance` | Variance used when simulating the GPS ping (adds noise to position).       |
| `sam.max_floating_vel`  | Max SAM velocity due to wind/water. Used to adapt spiral motion correctly. |

## Grid map params
| **Parameter**                         | **Description**                                                      |
| ------------------------------------- | -------------------------------------------------------------------- |
| `grid_map.workspace.width`            | Width of the grid map (in meters). Only useful in `sim`.                                      |
| `grid_map.workspace.height`           | Height of the grid map (in meters). Only useful in `sim`.                                  |
| `grid_map.workspace.resol`            | Grid cell resolution (in meters per cell).                           |
| `grid_map.workspace.variance`         | Gaussian variance used in the initial grid distribution.             |
| `grid_map.update.rate`                | Bayes Filter update period (s).                                  |
| `grid_map.update.true_detection_rate` | Probability of a true positive in the Bayes Filter.                  |
| `grid_map.update.time_margin`         | Prevents re-updating of recently updated cells (within `x` seconds). |


## TF params
| **Parameter**              | **Description**                   |
| -------------------------- | --------------------------------- |
| `frames.id.map`            | Frame ID of the global map.       |
| `frames.id.quadrotor_odom` | Frame ID of the drone's odometry. |
| `frames.id.sam_odom`       | Frame ID of SAM’s odometry.       |







