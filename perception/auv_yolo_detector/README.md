# YOLO Detection pckg

## Run image recording (in sim)
``
ros2 run ros_tcp_endpoint default_server_endpoint --ros-args -p ROS_IP:=127.0.0.1
``
``
ros2 run auv_yolo_detector yolo_detector
``

## Run rosbag
``
ros2 bag play --read-ahead-queue-size 100 -l -r 1.0 --clock 100 --start-paused ~/KTH_Courses/ResearchProject/RProj_GitRepoFork/colcon_ws/src/smarc2/perception/auv_yolo_detector/bags/alars_search_and_recover/rosbag2_2025_06_13-19_49_25_4.db3
``

## Datasetd
Click [https://kth-my.sharepoint.com/:f:/g/personal/framir_ug_kth_se/EpHV7UF6nQVIsYwrSBDlYWkBR-Yv08Lia9hxuD-aqrMTJQ?e=cpmczE]