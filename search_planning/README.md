# Drone Search Planning 
## Overview
This package is responsible for the implementation of the drone search planning algorithm, *i.e*, looking for SAM. As of now, it wasn't tested with the hardware and it's not properly integrated with the full system, but one can run it on SIM independently.
For now, it contains two types of algorithms:
- Spiral: The drone moves to the GPS ping and starts a spiral movement. Its radius increases over time and its center moves according
        to SAM velocity. This planner doesn't use the probabilistic grid map (no informative path planning).
- Heuristic: These algorithms make use of a probabilistic grid map constructed via a Bayes Filter. The final point of each path is the point with highest probability in the map.
    - Pure Greedy: Each path consists of a straight line to the final point
    -  A* based: The grid map is randomly populated with pseudo-obstacles. Cells with lower probability will be randomly chosen to define
        line obstacles. The objective is to give priority to paths that pass through cells with higher probability. After defining the
        obstacles, the regular A* algorithm is run.
## Dependencies (minimum)
- ROS2 Humble
- Python: 3.10.12
- Numpy: 2.2.3
- Scipy: 1.15.2

## Launch
To run this package in standalone mode, open two terminals:
```
ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=127.0.0.1
```
```
ros2 launch search_planning search_planning_launch.py 
```
The launch file includes all parameters that may require fine-tuning, along with brief explanations for each.
RVIZ2 is highly recommended in order to see the grid map and the planned path. 

In the simulator, go to the Quadrotor object (in Hierarchy) and set the parameter **Distance Error Cap** to **1** (in Inspector).

## **(ROS) Nodes**
| Node Name | File | Description |
| --- | ---| ---|
| sim_actions_node | path_planners.py | Responsible for teleporting SAM and creating a pseudo measurement of its coordinates|
| Quadrotorsmarcpathplanner_RosPublisher | path_planners.py |  Parent class from which all path planners inherit. Contains main attributes and methods for a seach planner class. |
| Quadrotorsmarcpathplanner_spiral_RosPublisher | path_planners.py | Spiral class implementation |
| Quadrotorsmarcpathplanner_heuristic_RosPublisher | path_planners.py | Greedy and A* implementations|
| Quadrotorsmarcpathplanner_gridmap_RosPublisher | prob_grid_map.py | Probabilistic grid map that feeds the heuristic planners. It's independent of the path planner though as it's always running |
---

## **New Topics**
| Topic | Type | Description |
| --- | ---| --- |
| /Quadrotor/path | RVIZ2 visualization | Path computed by any of the existing algorithms|
| /Quadrotor/grid_map | RVIZ2 visualization | Occupancy grid map computed via Bayes Filtering.  |
| /Quadrotor/max_prob_cell | RVIZ2 visualization| PointStamped corresponding to the cell with highest probability |
---

## Outro
Don't forget to
```
colcon build --symlink-install --packages-select search_planning 
source install/setup.bash
```
## Maintainer
Francisco Miranda, framir@kth.se
