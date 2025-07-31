# YOLO Detection 
This package uses YOLO to independently detect SAM and buoy. It includes two trained models: one for simulation and another for real-world scenarios (*.pt* files).
Two different datasets were used, with ~200 labelled images each. Access them [here](https://kth-my.sharepoint.com/:f:/g/personal/framir_ug_kth_se/EpHV7UF6nQVIsYwrSBDlYWkBR-Yv08Lia9hxuD-aqrMTJQ?e=cpmczE).

## Dependencies (dev versions)
- ROS2 Humble
- Ultralytics: 8.3.160
  
When installing *Ultralytics*, corresponding dependencies (*eg*: torch, opencv, etc) will be installed (check [here](https://docs.ultralytics.com/quickstart/))

## Launch yolo detector
``
ros2 launch auv_yolo_detector yolo_detector_launch.py
``
## **New Topics**
| Topic | Type | Description |
| --- | ---| --- |
| /Quadrotor/path | RVIZ2 visualization | Path computed by any of the existing algorithms|
---

## Future work
