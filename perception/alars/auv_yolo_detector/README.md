# YOLO Detection 
## Overview
This package uses YOLO to independently detect SAM and buoy. It includes two trained models: one for simulation and another for real-world scenarios (*.pt* files).
Two different datasets were used, with ~450 labelled images in total. Access them [here](https://kth-my.sharepoint.com/:f:/g/personal/framir_ug_kth_se/EpHV7UF6nQVIsYwrSBDlYWkBR-Yv08Lia9hxuD-aqrMTJQ?e=cpmczE).
### Training
The sim model was trained with the sim dataset, which was later used to train the real model with the real dataset.

## Dependencies (dev versions)
- ROS2 Humble
- Ultralytics: 8.3.160
  
When installing *Ultralytics*, corresponding dependencies (*eg*: torch, opencv, etc) will be installed (check [here](https://docs.ultralytics.com/quickstart/) for more info)

## Launch yolo detector
``
ros2 launch auv_yolo_detector yolo_detector_launch.py
``
## **New Topics**
| Topic | Msg | Description |
| --- | ---| --- |
| /Quadrotor/image_annotated | Image | Image from camera with YOLO annotations (bounding boxes + probabilities)|
| /Quadrotor/pred_position/sam | PointStamped | Predicted sam position in map frame|
| /Quadrotor/pred_position/buoy | PointStamped | Predicted buoy position in map frame|
---

## Future work
- Convert bounding boxes+orientation to pose (not position)
- Estimate pose/position correctly in real scenario (not only sim)
- Implement some kind of filter or atleast outlier removal.

## Outro
Don't forget to
```
colcon build --symlink-install --packages-select auv_yolo_detector
source install/setup.sh
```
## Maintainer
Francisco Miranda, framir@kth.se
