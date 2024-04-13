Work on porting smarc-project/smarc_navigation/sam_dead_reckoning to smarc-project/smarc2

# Scripts
- algae_map.py	
- dr_node.py
  - Ported 
- gps_node.py
  - Ported
- press_to_depth.py
  - Ported		
- publish_gps_path.py	
- publish_gps_pose.py
- republish_yost_odom.py
- sam_mm.py
- sbg_to_ros.py
- spoof_gps_imu.py
- wp_vis_node.py
- yaw_2_heading.py

# Other things to do
- package.xml: 
  - goedesy
- setup.py
  Entry point:
  - gps_node
  - depth_node
  - dr_node
- launch files: sam_dr_launch.py will launch depth, gps, and dr nodes
- config files: No config files are used yet, all parameters are set in the launch

# Install
gps_node.py requires geodesy -> added to package.xml
To install manually: apt install ros-humble-geodesy

# Things to check
## In general
- Which scripts should be ported?
- Are the pressures being reported by sam correct? see note in press_to_depth
- Am I declaring parameters correctly?
- Topic names should be looked up from somewhere...
## dr_node
- frame names
- Transforms: The order of args such as source and target frames can differ between ROS1 and ROS2
- How should DR behave in the simulation: I added a parameter to indicate that the node was being run with simulated data

## press_to_depth
- The pressure to depth calculation was reporting incorrect depths. Added a parameter to indicate simulation and a separate function for calculating depth with unity pressure values?
- The Depth calculation looked off to me, un explained offset. Maybe the publisher of the depth should apply any offset so that pressure is reported in 'true' Pascals.

## Launch file
- The current launch file is written in python, which is kind of a pain for some things... but it works for now.