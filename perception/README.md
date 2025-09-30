# Perception
Detecting things from sensors. 
Usually compute-intensive and doesn't need to run all the time. So a service to toggle on/off is nice to have!

## AUV Detector

### Running the Detector

Navigate to the detector folder and run the Python script:
Modify _ns:="/Quadrotor" to change the namespace

```bash
ros2 run auv_detector auv_buoy_detector --ros-args -r __ns:=/Quadrotor
```
or 

```bash
cd /colcon_ws/src/smarc2/perception/alars/auv_detector/auv_detector
python3 auv_buoy_detector.py
```

[Tutorial Video](https://youtu.be/dcXlofACp_I)



Tip: On Jetson devices, set `self.debug_imshow = 0` in the script to save computational resources and maintain a publishing rate of ~30 Hz.


To enable the AUV detector via ROS 2 service:
```bash
ros2 service call /enable_alars_detector std_srvs/srv/Trigger
```

To disable the AUV detector via ROS 2 service:
```bash
ros2 service call /disable_alars_detector std_srvs/srv/Trigger
```


To test using a recorded ROS 2 bag:
```bash
ros2 bag play rosbag2_2025_06_18-09_20_40_20.db3 --loop
```