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
        obstacles, the regular A* algorithm is run (it needs some improvements, so it shouldn't be used for now)
    - Artificial Potential Field: The highest probability cell exerts an attractive force on the drone whereas the remaining cells exert a 
        repulsive force, which is more intense for lower probability cells. The resultant force defines the movement direction.
## Dependencies (minimum)
- ROS2 Humble
- Python: 3.10.12
- Numpy: 1.23.5
- Scipy: 1.8.0
- MLFlow: 3.3.1
- dotenv 

## Launch
The search planning can be run standalone or integrated in other procedures.  For that reason, 3 modes are available:
- 'sim': It performs a full search based on the parameters in the config file. Useful for testing, it incorporates a mlflow
pipeline so one can track the results. It's only available on sim as it involves teleporting sam and other sim-only procedures. Some
visualization topics are available so the user can track what's happening.
- 'srv': The search planning is triggered by a client requested and handled by a service. It only produces a path and it's not responsible for
defining the setpoint, conversely to 'sim' mode. It consists of 2 services: one to trigger and set up the search planning and another to
compute the next path. 
- 'as': The search planning is managed by an Action Server. Similar to sim (it constantly publishes the next setpoint and not the path) but the search planning
needs to be triggered by the Action Client.

Examples of service client scripts are available within the package. If one wants to use the action server, it can run via CLI:
```
 ros2 action send_goal /Quadrotor/alars_search smarc_mission_msgs/action/AlarsSearchAction "{gps: {latitude: 58.85058132601718, longitude: 17.67436659875381, altitude: 5.0}, radius: 100.0}"
```
To run the search planning standalone, open two terminals and type:
```
ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=127.0.0.1
```
```
ros2 launch alars_auv_search_planner search_planning_launch.py  mode:="'as'"
```
Note that the mode parameter is mandatory, which prevents the user from selecting the wrong mode. 

### Note: 
While in the simulator, it's highly recommended to go to the Quadrotor object (in Hierarchy) 
and set the parameter **Distance Error Cap** to **1** (in Inspector). 

## **ROS Action**
| Action name | Components | 
| --- | ---| 
| AlarsSearchAction | gps (GeoPoint), radius (float) | 
---

## **ROS Srv**
| Service name | Service Type | Description |
| --- | ---| ---|
| 'init_auv_search' | InitAUVSearch | It initiates the **PGM**. It should be requested when the search planning is about to initiate. It needs the search radius around the GPS ping, the GPS ping (GeoPoint msg) and the drone's initial altitude wrt to the water level. It can be called several times in a single simulation since the planner and the grid map are reinitialized when this service is requested|
| 'get_quadrotor_path' | DronePath |  It computes a path based on the **PGM** and returns it as a PoseArray |
---
Check *test_initmap_srv.py* and *test_getpath_srv.py* to see how the client can be set up.

The launch file includes all parameters that may require fine-tuning and brief explanations for each.
RVIZ2 is highly recommended to see the grid map and the planned path. 

## **Visualization Topics**
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

ros2 action send_goal /Quadrotor/alars_search smarc_mission_msgs/action/AlarsSearchAction "{gps: {latitude: 58.85058132601718, longitude: 17.67416659875381, altitude: 5.0}, radius: 100.0}"
