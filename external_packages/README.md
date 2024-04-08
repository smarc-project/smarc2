# External
Place any packages that a smarc-package requires, but for reasons it can not be acquired from `apt` or `pip` here. 
**They should be git submodules.**

Listing them here with an explanation is heavily encouraged!

**Please also include a link to the primary source of whatever it is you put in here.**


## mqtt_bridge
**[Source](https://github.com/groove-x/mqtt_bridge/tree/ros2)**

Needed to speak to the SMaRC GUI over mqtt. Not availble any other way... There are some possible improvements to be made to this later.


## ROS-TCP-Endpoint
**[Main Source](https://github.com/Unity-Technologies/ROS-TCP-Endpoint)**

**[Source with fixed warnings](https://github.com/KKalem/ROS-TCP-Endpoint)**

This is the node Unity needs to communicate with ROS(2). Run with `ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=127.0.0.1`. It can keep running and works with Unity restarts.

