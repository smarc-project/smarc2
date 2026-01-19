#!/usr/bin/env -S venv/bin/python

import os
from pathlib import Path
from typing import Tuple, Union
import traceback

import cv2
import numpy as np
import torch
import yaml
from ament_index_python.packages import get_package_share_directory
from dji_msgs.msg import Topics

from cv_bridge import CvBridge
from ultralytics import YOLO
from ultralytics.engine.results import OBB, Results

from rosbags.highlevel import AnyReader
from rosbags.interfaces import Connection
from rosbags.typesys import Stores, get_typestore


class LabelFrame():
    """
        Performs inference on current frame every x seconds. Inferences are divided into:
            1) Good result and useful frame: detection (label + bounding box) is correct and the user
            wants to use that frame to train the model
            2) Bad result and useful frame: detection is incorrect but the user wants to use that frame
            to train the model, thus he will later on label it manually
            3) Useless frame: regardless of accuracy, the user finds the frame redundant/not important, hence
            it is not saved

        These cases map to keyboard keys, namely ENTER, SPACE and DEL, respectively.
            
    """
    def __init__(self):

        # get params (also from auv_yolo_detector node)
        with open(get_package_share_directory('auv_yolo_detector') + "/config/automatic_label_params.yaml", "r") as f:
            data = yaml.safe_load(f)
            params = data["/**/auv_yolo_detector"]
        with open(get_package_share_directory('auv_yolo_detector') + "/config/params.yaml", "r") as f:
            data = yaml.safe_load(f)
            self.model_params = data["/**/auv_yolo_detector"]["ros__parameters"]

        # define necessary paths
        model_local_path = params["paths"]["yolo_model"]
        bags_path = Path(params["paths"]["bags"])
        self.annotations_path = bags_path / "annotations"
        self.annotations_path.mkdir(parents=True, exist_ok=True)
        self.tolabel_path = self.annotations_path / "tolabel" 
        self.tolabel_path.mkdir(parents=True, exist_ok=True)

        # rosbag params
        self.dt = params["rosbag"]["frame_period"] 
        self.rosbag_duration = params["rosbag"]["duration"]  
        self.stored_frame_count = params["rosbag"]["initial_frame_index"]
        self.annotation_topic = "/M350/"  + self.model_params["topics"]["rviz"]["annotated_image"]
        self.rawim_topic = "/M350/" + Topics.GIMBAL_CAMERA_RAW_TOPIC
        self.rosbag_count = 0
        
        # yolo model
        model_path = get_package_share_directory('auv_yolo_detector') + model_local_path
        try:
            self.yolo_model = YOLO(model_path)
            self.yolo_model.info()
        except Exception as e:
            self.get_logger().warn(f'\n\nYOLO model import failed; check if the model_path rosparam is pointing to a valid model file! Readme has more details.\nGiven path:{model_path}\n\n')
            self.get_logger().warn(str(e))
            self.get_logger().warn(traceback.format_exc())
        self.bridge = CvBridge()

        lw_ratio_margin = 4.0
        self.filt_params = {
            "sam_dim": [self.model_params['sam']["width"], self.model_params['sam']['length']],
            "lw_ratio_lb": self.model_params['sam']['length']/self.model_params['sam']["width"] - lw_ratio_margin, # requires fine-tuning
            "lw_ratio_ub": self.model_params['sam']['length']/self.model_params['sam']["width"] + lw_ratio_margin, # requires fine-tuning
        }

        # create iterable objects os rosbags filenames, according to provided path
        self.bags = list(bags_path.glob('**/*.db3'))
        self.typestore = get_typestore(Stores.ROS2_HUMBLE) # Create a type store to use if the bag has no message definitions.

        self.window_name = "Current Frame  | ENTER to save image and non-empty label | SPACE to save image only | TAB to save image and an empty label | DEL to continue | ESC to finish process"

        
    def automatic_classifier(self): 
        """
        Creates a window and show two images: raw image and annotated image. Depending on the user
        action, the image/label are stored or not.
        Iterates on rosbags directory and stores images and labels within it.
        """
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        for path in self.bags:
            msg_count = 0
            print(f'ROSBAG NR {self.rosbag_count} | Current bag filename: \n {path.parts[-1]}')
            with AnyReader([path], default_typestore=self.typestore) as reader:
                connections = [x for x in reader.connections if x.topic == self.rawim_topic]
                connection: Connection = connections[0]
                step = int(self.dt*connection.msgcount/self.rosbag_duration)
                print(f'Nr of messages: {connection.msgcount} | Frame to label: {connection.msgcount // step} | Message Topic: {connection.topic} \n ')  
                for _, timestamp, rawdata in reader.messages(connections=connections):
                    msg = reader.deserialize(rawdata, connection.msgtype)         
                    if msg_count % step == 0:
                        # apply inference to frame, show raw and annotated images
                        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
                        results = self.yolo_model.predict(source = cv_image, 
                                        conf = 0.4, save = False, verbose = False, device = 'cpu')
                        result: Results = results[0]
                        result.obb, _, _, _ = self.filter_detections(result.obb)
                        im = np.hstack((cv_image, result.plot()))
                        cv2.resizeWindow(self.window_name, im.shape[1], im.shape[0])
                        cv2.imshow(self.window_name, im)

                        # loop: wait for user action to do smth with frame
                        while True:
                            key = cv2.waitKey(1)
                            match key:
                                case 27: 
                                    print("ESCAPE pressed, finishing labelling")
                                    return
                                case 13: 
                                    print("ENTER pressed, frame label accepted and saved")
                                    filename = f'aut_djuroNov_{self.stored_frame_count}'
                                    cv2.imwrite(os.path.join(self.annotations_path, filename + '.jpg'), cv_image)
                                    self.create_label(result.obb, filename)
                                    self.stored_frame_count += 1
                                    break
                                case 32: 
                                    print("SPACE pressed, frame stored to be labelled")
                                    filename = f'aut_djuroNov_{self.stored_frame_count}'
                                    cv2.imwrite(os.path.join(self.tolabel_path, filename + '.jpg'), cv_image)
                                    self.stored_frame_count += 1
                                    break 
                                case 255: 
                                    print("DELETE pressed, frame not stored")
                                    break
                                case 9: 
                                    print("TAB pressed, false detection, storing frame and empty label")
                                    filename = f'aut_djuroNov_{self.stored_frame_count}'
                                    cv2.imwrite(os.path.join(self.annotations_path, filename + '.jpg'), cv_image)
                                    self.create_label(None, filename)
                                    self.stored_frame_count += 1
                                    break
                    msg_count += 1
            self.rosbag_count += 1

    def create_label(self, obb: OBB, filename: str):
        """
        Creates .txt file that follows the YOLO OBB format (https://docs.ultralytics.com/datasets/obb/#yolo-obb-format)
        """
        try:
            for j in range(obb.xyxyxyxyn.numpy().shape[0]):
                points = obb.xyxyxyxyn.numpy()[j,:,:].reshape(1,8).flatten()
                cls = obb.cls.numpy()[j]
                x = list(np.concatenate((cls, points), None))
                x[0] = int(x[0])
                s = ""
                with open(os.path.join(self.annotations_path, filename + ".txt"), 'a') as f:
                    for i in x:
                        s = s + str(i)+ " "
                    s = s[:-1]
                    f.write(s+'\n')
        except (TypeError, ValueError, AttributeError) as e:
            print("WARN: empty label")
            with open(os.path.join(self.annotations_path, filename + ".txt"), 'w') as f:
                pass
        


    def filter_detections(self, obb: OBB) -> Tuple[Results, torch.Tensor, Union[list, None], Union[list, None]]:
        """
        Filter detections by choosing most likely detection for each class and filter according to 
        box ratio and temporal/velocity constraints
        """

        cls : torch.Tensor = obb.cls
        conf: torch.Tensor = obb.conf
        sam_index, buoy_index = None, None  
        
        # Keep most likely sam/buoy (sam = 0, buoy = 1)
        sam_mask = cls.cpu().numpy() == 0 # cls.numpy() detach().cpu().numpy
        if len(cls.cpu().numpy() ) != 0:
            sam_index = np.argmax(np.multiply(conf.cpu().numpy(), sam_mask))
            sam_index = None if cls.cpu().numpy()[sam_index] != 0  else sam_index

            buoy_index = np.argmax(np.multiply(conf.cpu().numpy(), ~sam_mask))
            buoy_index = None if cls.cpu().numpy()[buoy_index] != 1  else buoy_index

        # Check length/width ratio of sam bounding box
        if sam_index is not None:
            lw_ratio = max(obb.xywhr[sam_index][2],obb.xywhr[sam_index][3])/min(obb.xywhr[sam_index][2],obb.xywhr[sam_index][3]) 
            if lw_ratio < self.filt_params["lw_ratio_lb"] or lw_ratio > self.filt_params["lw_ratio_ub"]: 
                sam_index = None

        # return objects posiitons as lists
        sam_pos = obb.xywhr[sam_index][0:2] if sam_index is not None else None
        buoy_pos = obb.xywhr[buoy_index][0:2] if buoy_index is not None else None

        # Create valid detections mask and return new result.obb object
        final_mask = np.full(cls.cpu().numpy().size, False)
        if sam_index is not None: final_mask[sam_index] = True 
        if buoy_index is not None: final_mask[buoy_index] = True 

        return obb[torch.from_numpy(final_mask)], torch.from_numpy(final_mask), sam_pos, buoy_pos 
    
def main():
    node = LabelFrame()
    node.automatic_classifier() 

if __name__ == '__main__':
    main()
