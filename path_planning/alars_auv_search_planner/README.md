# Drone Search Planning 
## Overview
This package is responsible for the implementation of the drone search planning algorithm, *i.e*, looking for SAM. As of now, it wasn't tested with the hardware and it's not properly integrated with the full system, but one can run it on SIM independently.
For now, it contains 4 algorithms:
- Spiral: The drone moves to the GPS ping and starts a spiral movement. Its radius increases over time and its center moves according
        to SAM velocity. This planner doesn't use the **Probabilistic Grid Map (PGM)** (no informative path planning).
- Heuristic: These algorithms make use of a probabilistic grid map constructed via a Bayes Filter. The goal point of each path is the point with highest probability in the map.
    - Pure Greedy: Each path consists of a straight line to the final point
    - A* based: The grid map is randomly populated with pseudo-obstacles. Cells with lower probability will be randomly chosen to define
        line obstacles. The objective is to give priority to paths that pass through cells with higher probability. After defining the
        obstacles, the regular A* algorithm is run.
    - Artificial Potential Field: The highest probability cell exerts an attractive force on the drone whereas the remaining cells exert a 
        repulsive force, which is more intense for lower probability cells. The resultant force defines the movement direction.
## Dependencies (minimum)
- ROS2 Humble
- Python: 3.10.12
- Numpy: 2.2.3
- Scipy: 1.15.2

## Launch
The search planning can be run standalone or integrated in other procedures.  To run this package, In the simulator, go to the Quadrotor object (in Hierarchy) 
and set the parameter **Distance Error Cap** to **1** (in Inspector). Then, open two terminals:
```
ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=127.0.0.1
```
```
ros2 launch alars_auv_search_planner search_planning_launch.py
```

If the user solely wants to test the package, the parameter "mode" should be changed to "sim". This will teleport SAM to the desired position, create the GPS ping and move the drone to the initial position immediately. 

If the user wants to integrate this in a broader task, two clients have to be created. The services are as follows (check *smarc_mission_msgs*):
## **(ROS) Srv**
| Service name | Service Type | Description |
| --- | ---| ---|
| 'init_auv_search' | InitAUVSearch | It initiates the **PGM**. It should be requested when the search planning is about to initiate. It needs the search radius around the GPS ping, the GPS ping (GeoPoint msg) and the drone's initial altitude wrt to the water level. It can be called several times in a single simulation since the planner and the grid map are reinitialized when this service is requested|
| 'get_quadrotor_path' | DronePath |  It computes a path based on the **PGM** and returns it as a PoseArray |
---
Check *test_initmap_srv.py* and *test_getpath_srv.py* to see how the client can be set up.

The launch file includes all parameters that may require fine-tuning and brief explanations for each.
RVIZ2 is highly recommended to see the grid map and the planned path. 

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
source install/setup.sh
```
## Maintainer
Francisco Miranda, framir@kth.se