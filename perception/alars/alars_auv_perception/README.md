# ALARS AUV Perception

## Overview
This package uses YOLO to detect **sam**, **buoy**, and other classes such as **Lolo**, **Catamaran**, and **boats**. The YOLO models with real and sim data can be found in detail in the following repository [alars_labeling_training](https://github.com/moyucrazy12/alars_labeling_training.git), where can be found as well the annotation and training pipeline followed to obtain the models.

Additionally, the package detects the SAM's head using a Canny edge detector, which assumes the presence of a rope attached to Sam.

---

## Dependencies
- ROS 2 Humble
- Ultralytics `8.3.160`
- NumPy `1.23.5`
- OpenCV `4.11.0`
- PyTorch `2.6.0`

When installing **Ultralytics**, some dependencies such as **PyTorch** and **OpenCV** will usually be installed automatically. See the official documentation for more details:  
[Ultralytics Quickstart](https://docs.ultralytics.com/quickstart/)

> **Note**  
> Running `pip3 install ultralytics` may also install `numpy 2.2.6` (observed as of November 2025). This can cause compatibility issues with the `tf_transformations` library. If that happens, remove the incompatible NumPy version and install the required one manually.

---
Before using this package, ensure that the trained models are available through the [training repository](https://github.com/moyucrazy12/alars_labeling_training).

---

### Training Package (Submodule)

The training repository contains all the currently available trained models and is intended to be added as a **git submodule**:

alars_labeling_training

Once included and built, the models are exposed through the ROS 2 package system, so this allows the perception package to resolve model paths automatically (via FindPackageShare).

---

### Detection Configuration

The detection behavior (e.g., classes and confidence thresholds) can be configured in:

config/detection_parameters.yaml

Make sure that:
- the configured classes match the selected model  
- per-class thresholds are consistent with your use case  

---

### Important ⚠️

Ensure the submodule is properly initialized. If the submodule is missing or not built, the perception package will not be able to locate the trained models.

### Build Workspace

After adding the submodule, build both packages:

cd [ws_path]
colcon build --symlink-install --packages-select alars_auv_perception alars_labeling_training
source install/setup.bash

---

## Package Setup

Before using the package, make sure to check the trained models from the submodule: [alars_labeling_training](https://github.com/moyucrazy12/alars_labeling_training.git)

#### Training package
You can use the training package which has already all the current trained models:
```bash
alars_labeling_training
```

Models will be resolved automatically via ROS packages.

### Detection Configuration
As well, the classes to detect, with their corresponding confidence thresholds, can be configured in:

```yaml
config/detection_parameters.yaml
```

Then, remember to build the workspace with this new package and the submodule:

```bash
cd [ws_path]
colcon build --symlink-install --packages-select alars_auv_perception alars_labeling_training
source install/setup.sh
```

So, make sure you have the submodule as well

---

## Launch YOLO Detector

### 1. Launch only the YOLO detector

```bash
ros2 launch alars_auv_perception alars_yolo_detector.launch.py namespace:=M350 device:=cpu use_sim_time:=true model_package:=alars_labeling_training model_file:=<model_name>
```

If CPU inference is too slow, consider using a GPU instead by setting:

```bash
device:=0
```

or another available GPU device (consider this step for all the following examples).

To open the RViz configuration file:

```bash
rviz2 -d <absolute_path>/perception/alars/alars_auv_perception/config/rviz/M350_perception.rviz
```

By default, the detector subscribes to the raw image topic defined internally in the Python node, which corresponds to the gimbal camera (`dji_msgs`). To override this topic from the launch file, use:

```bash
raw_image_topic:=<image_raw_topic>
```

---

### 2. Launch the YOLO detector with a video

```bash
ros2 launch alars_auv_perception alars_video_yolo_detector.launch.py namespace:=M350 device:=cpu use_sim_time:=false model_package:=alars_labeling_training model_file:=<model_name>
```

For video playback, it is recommended to use:

```bash
use_sim_time:=false
```

To change the input video, edit the path in:

```bash
config/video_publisher_parameters.yaml
```

---

### 3. Launch the YOLO detector with a rosbag

```bash
ros2 launch alars_auv_perception alars_rosbag_yolo_detector.launch.py namespace:=M350 device:=cpu use_sim_time:=false model_package:=alars_labeling_training model_file:=<model_name>
```

---

### 4. Play only a rosbag
Useful for frame collection or testing:

```bash
ros2 bag play --read-ahead-queue-size 1000 -r 1.0 --clock 100 --start-paused <rosbag_path>
```

It is recommended to create a `datasets/` folder to store videos and rosbags.

---

## Visualization Topics

| Topic | Message Type | Description |
|---|---|---|
| `/namespace/rviz/annotated_image` | `Image` | Camera image with YOLO annotations (bounding boxes and confidence scores). |
| `/namespace/rviz/blurred_sam` | `Image` | Sliced and rotated SAM window in grayscale, blurred before Canny edge detection. |
| `/namespace/rviz/edges` | `Image` | Output of the Canny edge detector. |

The last two topics are especially useful for debugging. In particular, the filter parameter:

```yaml
detection.blur_variance
```

may need adjustment depending on the scene. Ideally, waves should not generate edges, so the variance should be set to the smallest value that still suppresses them.

---

## Published Topics

| Topic | Message Type | Description |
|---|---|---|
| `/namespace/alars_detection/auv` | `PointStamped` | Estimated position of the detected SAM/AUV. |
| `/namespace/alars_detection/auv_obb` | `PolygonStamped` | Oriented bounding box of the detected SAM/AUV. |
| `/namespace/alars_detection/auv_head` | `PolygonStamped` | Estimated head/front region of the detected SAM/AUV. |
| `/namespace/alars_detection/buoy` | `PointStamped` | Estimated position of the detected buoy. |
| `/namespace/alars_detection/buoy_obb` | `PolygonStamped` | Oriented bounding box of the detected buoy. |
| `/namespace/estimated_other_obbs` | `PolygonStamped` | Oriented bounding boxes for other detected classes. |

---

## Labeling and Training Pipeline

If you also want to use the labeling and training pipeline, see: [alars_labeling_training](https://github.com/moyucrazy12/alars_labeling_training.git). This pipeline is kept separate from the ROS 2 perception pipeline and is intended only for annotation and training tasks.

Therefore it is separated because it depends on **Segment Anything Model 2 and 3**, and typically requires two different Conda environments to avoid dependency conflicts with the main perception pipeline. You can find its installation instructions in the corresponding repository, but it is suggested to be included in the add-ons folder.

---

## Maintainer
**Cristhian Mallqui Castro**  
ckmc@kth.se