# YOLO Detection 
## Overview
This package uses YOLO to independently detect SAM and buoy. It includes two trained models: one for simulation and another for real-world scenarios (*.pt* files). The models can be accessed [here](https://kth-my.sharepoint.com/:f:/g/personal/framir_ug_kth_se/IgD4flS-1Nx9SoAHoldjgDS8AULieuNh-fLqTrC9wWTSeBY?e=PAd1AX). Download the models you want and change the path parameter in the *.yaml* file in config. The training datasets can be acessed [here](https://kth-my.sharepoint.com/:f:/g/personal/framir_ug_kth_se/EpHV7UF6nQVIsYwrSBDlYWkBR-Yv08Lia9hxuD-aqrMTJQ?e=cpmczE).

> Rename the model file to `yolo_model.pt` and place it inside the config directory of this package.

 The detection of SAM's head is done with a Canny edge detector, which relies on the existence of a rope attached to it. 
 
## Training 

There are three folders in OneDrive:

- **sim_data_obb**: Frames extracted from simulation only. Environment parameters (lighting, wave conditions, etc.) were varied across runs.
- **real_data_obb**: Frames extracted from rosbags. Files with the suffix `aut` were automatically labeled using a YOLO model (with human supervision).
- **mixed_data_obb**: Combination of the two datasets above.

These folders allow flexibility if one wants, for instance, train a pre-trained model with sim images on real images only or to train a model with the full dataset.
> When adding new data, follow the [YOLO OBB label format](https://docs.ultralytics.com/datasets/obb/). Tools like CVAT can be used for annotation.
> 
> Place images and labels in the correct folder (`sim` or `real`) and update the `mixed` folder accordingly.
> 
> Update the `dataset_readme.txt` with the latest frame index so other people don't override files.

> When adding new models, fill in the `yolo-model-stats.odt` file as well, very important to keep track of model performance!

## Dependencies
- ROS2 Humble
- Ultralytics: 8.3.160
- Numpy: 1.23.5
- OpenCV: 4.11.0
- Torch: 2.6.0
  
When installing *Ultralytics*, corresponding dependencies (*eg*: torch, opencv, etc) will be installed (check [here](https://docs.ultralytics.com/quickstart/) for more info)


> It is likely that if you run `pip3 install ultralytics` it will also install `numpy 2.2.6` (as of 2025 Nov). This is very likely to cause issues with the `tf_transformations` library (that everyone is using...). So remove numpy with `pip` if this is the case.

## Launch yolo detector (example)
Launch yolo detector:
```
ros2 launch auv_yolo_detector yolo_detector_launch.py namespace:=M350 device:=cpu use_sim_time:=true
```

Launch rviz file (needs absolute path):
```
rviz2 -d <your path>/perception/alars/auv_yolo_detector/config/M350_yolo.rviz 
```

Launch rosbag (for frame collection or testing purposes):
```
ros2 bag play --read-ahead-queue-size 1000 -r 1.0 --clock 100 --start-paused <rosbag path>
```

## **Visualization Topics**
| Topic | Msg | Description |
| --- | ---| --- |
| /namespace/rviz/annotated_image | Image | Image from camera with YOLO annotations (bounding boxes + probabilities)|
| /namespace/rviz/blurred_sam | Image | Sliced and rotated window with sam. It's in grayscale and it's blurred, since it's the input to the Canny edge detector. |
| /namespace/rviz/edges  | Image | Output from Canny edge detector|
---
The last two topics may help in debugging, since the variance parameter (detection.blur_variance) in the filter definition might have to be changed. The waves shouldn't yield any edges, so one should choose the smallest variance that makes this possible.


## Auxiliary scripts
### **automatic_label.py**
Using the model inference as training label allows us to decrease the dependency on labelling tools. To properly use this, start by installing the 'robags' library, that offers great flexibility when reading a rosbag
```
pip install rosbags
```
Then create a folder and add the rosbags to it. Run the script (as a regular python script, no need for `ros2 run`) and use the following keys to categorize you current frame.
1) [**ENTER**] Good result and useful frame: detection (label + bounding box) is correct and the user wants to use that frame to train the model
2) [**SPACE**] Bad result and useful frame: detection is incorrect but the user wants to use that frame to train the model, thus he will later on label it manually
3) [**DEL**] Useless frame: regardless of accuracy, the user finds the frame redundant/not important, hence it is not saved
4) [**TAB**] Same as 2 but when there's a false detection. In that case, the label *.txt* file will be empty and we can create it right away

Pressing [**TAB**] or [**ENTER**] will save the image and the label within your rosbags' folder. Pressing [**SPACE**] will save the image in a another folder within the same directory so you can label it later on. Pressing [**DEL**] won't save anything.

**Script params (automatic_label_params.yaml)**
| **Parameter**               | **Description**                                                                                                        |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `paths.yolo_model` | Relative path of the yolo model (assuming it's within auv_yolo_detector package)                       |
| `paths.bags`       | Absolute path of your rosbags' directory.                                                                             |
| `rosbag.duration`          | Duration of the rosbag in [s]. See note below.                                                                         |
| `rosbag.dt`     | Approximated time period between frames (lower value means you will evaluate more frames).                                                           |
| `rosbag.initial_frame_index`     | Starting index when naming image/label. If you already have frames within your directory, you may want to change this accordingly so you don't replace already existing images/labels. |

**Note**: In some rosbags, message stamp was always 0. This could be due to the use of `use_sim_time` parameter, check [this](https://stackoverflow.com/questions/69084148/the-effect-of-use-sim-time-in-ros) for more info. Thus, to skip to the next frame, we use the total number of frames in the rosbag and the rosbag duration to determine the next frame to evaluate.
### **record_data.py**
It extracts frames from a played rosbag (check launch command above). It's not as user friendly in the sense it does not have a parameter file, so you may want to change the class attributes
- self.path
- self.period 
- self.frame_index
- self.run

### **train.py**
Use this to train your yolo model. You may need to use a virtual environment, so you can do this outside of the smarc workspace. If you use a virtual environment and name it `yolovenv`:
```
source yolovenv/bin/activate
python3 ./train.py 
```
Your dataset should be within the directory and its path should be defined in a config.yaml (see example below)
```
path: /home/smarc/aa_francisco_ws/scripts/mixed_data_obb
train: images/train
val: images/val
names:
  0: sam
  1: buoy
```
Thus, the dataset folder, the `config.yaml` and the `train.py` should be in the same directory.

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
