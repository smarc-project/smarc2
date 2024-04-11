Work on porting smarc-project/smarc_navigation/sam_dead_reckoning to smarc-project/smarc2

# Scripts
- algae_map.py	
- dr_node.py
  - Ported but not tested
- gps_node.py
  - Need to do
- press_to_depth.py
  - Need to do		
- publish_gps_path.py	
- publish_gps_pose.py
- republish_yost_odom.py
- sam_mm.py
- sbg_to_ros.py
- spoof_gps_imu.py
- wp_vis_node.py
- yaw_2_heading.py

# Other things to do
- package.xml
- setup.py
- launch files
- config files

# Install
gps_node.py requires geodesy which must be installed through pip: pip install geodesy