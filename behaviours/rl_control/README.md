
```
colcon test --packages-select rl_control  --event-handlers console_cohesion+
```

Had to run 
```
pip install "numpy<1.24"
```


```
ros2 launch watertank_utils sim_tank_mocap.launch.py

netsh interface portproxy add v4tov4 listenport=10000 listenaddress=0.0.0.0 connectport=10000 connectaddress=(wsl hostname -I)

ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=127.0.0.1 -p ROS_TCP_PORT:=10000
```