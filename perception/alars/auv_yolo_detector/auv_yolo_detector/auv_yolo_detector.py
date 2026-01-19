#!/usr/bin/env -S venv/bin/python
from typing import Tuple, Union
import traceback

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.duration import Duration

from math import pi
import numpy as np
import cv2
import torch
from cv_bridge import CvBridge

from ultralytics import YOLO
from ultralytics.engine.results import OBB, Results

from sensor_msgs.msg import Image
from geometry_msgs.msg import PointStamped
from tf2_ros import Buffer, TransformListener
from std_srvs.srv import Trigger

from dji_msgs.msg import Topics
from dji_msgs.msg import Links



class YOLODetector(Node):
    def __init__(self, name = 'auv_yolo_detector'):
        super().__init__(name,
                allow_undeclared_parameters=True,
                automatically_declare_parameters_from_overrides=True)
        self.get_params()

        # detection filtering params
        lw_ratio_margin = 4.0
        self.filt_params = {
            "sam_dim": [self.model_params['sam.width'], self.model_params['sam.length']],
            "lw_ratio_lb": self.model_params['sam.length']/self.model_params['sam.width'] - lw_ratio_margin, # requires fine-tuning
            "lw_ratio_ub": self.model_params['sam.length']/self.model_params['sam.width'] + lw_ratio_margin, # requires fine-tuning
        }
        self.dircount = []
        self.horizon = 10
 
        
        # pubs, subs and tf2
        self.create_subscription(Image, self.model_params["topics.raw_image"], self.image_callback, 10) 
        self.annotated_img_pub = self.create_publisher(Image,
                                            self.model_params["topics.rviz.annotated_image"], 10)
        self.blurred_channel_pub = self.create_publisher(Image,
                                    self.model_params["topics.rviz.bw_blurred_sam"], 10)
        self.head_detection_view_pub = self.create_publisher(Image,
                                    self.model_params["topics.rviz.edges"],10)
        self.sam_position_pub =  self.create_publisher(PointStamped, 
                                self.model_params["topics.predicted_position.sam"], 10)
        self.buoy_position_pub = self.create_publisher(PointStamped, 
                                self.model_params["topics.predicted_position.buoy"], 10)

        
        # models 
        try:
            self.yolo_model = YOLO(self.model_params['model_path'])
            self.yolo_model.info()
        except Exception as e:
            self.get_logger().warn(f'\n\nYOLO model import failed; check if the model_path rosparam is pointing to a valid model file! Readme has more details.\nGiven path:{self.model_params["model_path"]}\n\n')
            self.get_logger().warn(str(e))
            self.get_logger().warn(traceback.format_exc())
        self.bridge = CvBridge()

        # timer to simulate tracking
        self.detector_enabled = True
        self.image: Image = None
        self.classify_timer = self.create_timer(self.model_params['detection.inference_period'], self.classify_callback)

        # create detector services
        self.create_service(Trigger, Topics.ENABLE_ALARS_DETECTOR_SERVICE_TOPIC , self.handle_enable_detector)
        self.create_service(Trigger, Topics.DISABLE_ALARS_DETECTOR_SERVICE_TOPIC , self.handle_disable_detector)

    
    def classify_callback(self):
        """ 
        Callback that's running continuoysly at specified frequency. It only classified image if we
        have an image and if detector is enabled.
        Infers with yolo model and canny edge deetctor and publishes objects positions
        """
        
        if self.image is not None and self.detector_enabled:
            cv_image = self.bridge.imgmsg_to_cv2(self.image, desired_encoding='bgr8')
            results = self.yolo_model.predict(source = cv_image, 
                            conf = self.model_params['detection.confidence_threshold'],    
                            save = False,
                            verbose = False,
                            device = self.model_params['device'])
            result: Results = results[0]
            
            # filter detections and get head position
            result.obb, _ , sam_pixels, buoy_pixels = self.filter_detections(result.obb)
            head = self.identify_head(result.obb, cv_image)

            # publish positions (head and buoy)
            if sam_pixels is not None:
                self.published_normalized_position(head, (self.image.width,self.image.height), "sam")
            if buoy_pixels is not None:
                self.published_normalized_position(buoy_pixels, (self.image.width,self.image.height), "buoy")
     
            # publish filtered annotated image as ros msg
            im = result.plot()
            if head is not None:
                cv2.circle(im, center=(head[0], head[1]), radius=5, color=(0, 255, 0), thickness=2)
            ros_img = self.bridge.cv2_to_imgmsg(im, encoding = 'bgr8')
            self.annotated_img_pub.publish(ros_img)

            self.get_logger().info(f"Detections:\nSAM Head: {head}\nSAM: {sam_pixels}\nBuoy: {buoy_pixels}")



    def identify_head(self, result: OBB, im: np.ndarray) -> tuple:
        """
        Head detection with Canny edge detector. It takes bounding box, slices and rotates window 
        (bounding box + some slack to include the rope) and apply edge detector to see which side has 
        the rope. To be robust against outliers, the argmax of last N detections is selected

        Args:
            - result: OBB instance, contains result from YOLO inference (bounding box, classifications, etc)
            - im: raw image as numpy array instance

        Return:
            - tuple with head position (in pixels)

        Vars:
            - c4: list with the coordinates of the 4 corners of the bounding box
            - thresh: threshold/slack given to define the window. 0 means window = box, 
                      1 means = window = 2*box (roughly, check slice_image code for +info)
        """
        
        cls : torch.Tensor = result.cls
        xywhr: list = result.xywhr # [x_center, y_center, width, height, rotation]
        c4: list = result.xyxyxyxy
        head = None
        sam_index = np.nonzero(cls == 0).flatten()
        thresh = 0.8

        if sam_index.numel() == 1:
            xywhr: torch.Tensor = xywhr[sam_index[0]]
            c4: np.ndarray = c4[sam_index[0]].cpu().numpy() # 4 corners of bounding box, shape = (4,2)
            original_c4 = c4.copy()
            length = max(xywhr[2:4])*0.5

            # slice image to get bounding box region (with a margin) 
            sliced_im, c4 = self.slice_image(im, c4, thresh, length)

            # rotate image and slice again
            rgb_sliced_im = cv2.cvtColor(sliced_im, cv2.COLOR_BGR2RGB)
            canny_im, corners_rot = self.rotate_image(rgb_sliced_im[:,:,0], c4.T, (180/pi)*float(xywhr[4]))
            canny_im, c4 = self.slice_image(canny_im, corners_rot.T, thresh, length, 'uneven')

            # Implement canny edge detector           
            blur = cv2.GaussianBlur(canny_im, (5, 5), self.model_params["detection.blur_variance"]) 
            median = np.median(blur)
            lower_threshold = int(max(0, 0.5 * median))
            upper_threshold = int(min(255, 1.5 * median))
            edges = cv2.Canny(blur, threshold1=lower_threshold, threshold2=upper_threshold)

            # Use edges to decide head position (NOTE use past xyxyxyx (ie, index correctly) to get point on the correct side)
            # if left side has more edges, than we choose a corner with xmin and i = 0;
            # otherwise, we choose a corner with xmax and i = 1;

            fdim = {0: np.min, 1: np.max}
            axis = int((float(xywhr[2]) < float(xywhr[3])))
            coord_min, coord_max = int(np.min(c4, axis = 0)[axis]), int(np.max(c4, axis = 0)[axis])
            if axis == 0: # bounding box is aligned with horizontal axis
                sums = (np.sum(edges[:, 0:coord_min]), np.sum(edges[:, coord_max:])) 
            else:
                sums = (np.sum(edges[0:coord_min, :]), np.sum(edges[coord_max:, :]))
   
            # determine where are more edges and update cumulative variable to get chosen side (left/bottom - 0; right/top - 1)
            argsum = np.argmax(np.array(sums))
            if len(self.dircount) >= self.horizon:
                self.dircount.pop(0)
            self.dircount.append(argsum)
            idx_headc = 0 if len(list(np.flatnonzero(np.array(self.dircount) == 0))) > len(self.dircount) // 2 else 1 #count left detections
                    
            # map the obtained side (left or right) to the two corresponding corners of the original image
            # and get head position as middle point
            i = np.nonzero(c4[:,axis].astype(int) == int(fdim[idx_headc](c4, axis = 0)[axis]))[0]
            head = np.mean(original_c4[i,:], axis = 0).astype(int)
            
            # publish images
            self.head_detection_view_pub.publish(self.bridge.cv2_to_imgmsg(edges, encoding = 'passthrough'))
            self.blurred_channel_pub.publish(self.bridge.cv2_to_imgmsg(blur, encoding = 'passthrough'))   


        return head
    
    def rotate_image(self, im: np.ndarray, points: np.ndarray, angle: float)-> Tuple[np.ndarray, np.ndarray]: 
        """
        Rotate image and individual pixels
        """

        assert points.shape[0] == 2, "points array should be shape (2, n) "
        try: n = points.shape[1] 
        except: 
            points = points.reshape(-1, 1)
            n = 1 
        w, h = im.shape[1], im.shape[0]
        rotation_matrix = cv2.getRotationMatrix2D(center = (w//2,h//2), #1 = width, 0 = height
                                                      angle = angle, 
                                                      scale = 1.0)
        corners_rot = rotation_matrix @ np.concatenate((points, np.ones((1,n))), axis = 0)
        canny_im = cv2.warpAffine(im, rotation_matrix, (w, h))
    
        return canny_im, corners_rot
    
    
    def slice_image(self, im: np.ndarray, c4: np.ndarray, thresh: float, 
                    length: float, mode: str = 'even') -> Tuple[np.ndarray, np.ndarray]: 
        """ 
        Slice image by taking the max and min (x,y) coordinates (corners) and return
        the c4' new position
        Args:
            im: image as a numpy array
            c4: (4,2) array where each row is a corner of the box
            thresh: how much bigger will the window be than the box. 0 means window = box, 1 means = window = 2*box
            length: maximum dimension of box
            slice_mode: str
        Note:
            c4: the corners of the bounding box, thus 4 positions
            corners: two points, corresponding to (xmax, ymax), (xmin, ymin), and that define the sliced image size.
                 Each corners may correspond to one of the c4 or not, depending on the orientation of the box 
                
        """
        assert c4.shape == (4,2), 'shape of corners array is not (4,2)'

        slack = np.ones((1,4)).flatten()*thresh
        # get two corners (xmax, ymax, xmin, ymin); add slack unevenly (bigger slack to longer dimension)
        corners = (*np.max(c4, axis = 0), *np.min(c4, axis = 0)) 
        if mode != 'even':
            argmax_dim = np.argmax([corners[0]-corners[2], corners[1]-corners[3]])
            slack[[not argmax_dim, (not argmax_dim)+2]] = thresh/4
        corners = np.array(corners) + np.array([1,1,-1,-1])*float(length)*slack

        # apply limits on each coordinate
        f = lambda x, t: min(max(round(x), 0), t)
        corners = np.array(list(map(f, corners, (*im.shape[1: :-1], *im.shape[1: :-1])))) #xmax, ymax, xmin, ymin

        return im[corners[3]:corners[1], corners[2]:corners[0]], c4 - corners[2:]

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
                   
    
    def published_normalized_position(self, p: tuple, wh: tuple, label: str) -> tuple:
        """
        Normalize pixels coordinates so the origin is the center of the image, the x axis is horizontal
        from left to right and y axis is vertical from bottom to top
        Publishes normalized pixel position in corresponding topics, depending on label
        Args:
            p: (horizontal position, vertical position)  (both in pixels)
            wh: (width, height)
            label: "sam" or "buoy"
        """
        #if wh != (640, 480): self.get_logger().warn(f'640*480 resolution was expected (width, height).')
        point = PointStamped()
        point.header.stamp = self.get_clock().now().to_msg()
        point.header.frame_id = self.model_params["frames.camera"]
        point.point.x = float((p[0]-wh[0]/2)/(wh[0]/2))
        point.point.y = float(-(p[1]-wh[1]/2)/(wh[1]/2))
        if label == 'sam': self.sam_position_pub.publish(point)
        elif label == 'buoy': self.buoy_position_pub.publish(point)
        else: self.get_logger().error('Position not published, label argument should be "sam" or "buoy"')

    
    def handle_enable_detector(self, request, response):
        # Toggle the detector enabled flag
        self.detector_enabled = True
        response.success = True
        response.message = 'detector enabled' if self.detector_enabled else 'detector disabled'
        self.get_logger().info(f"Service called: detector_enabled = {self.detector_enabled}")
        return response

    def handle_disable_detector(self, request, response):
        # Toggle the detector enabled flag
        self.detector_enabled = False
        response.success = True
        response.message = 'detector enabled' if self.detector_enabled else 'detector disabled'
        self.get_logger().info(f"Service called: detector_enabled = {self.detector_enabled}")
        return response
    

    def image_callback(self, msg):
        self.image = msg

    def get_params(self):
 
        # expected types of parameters and create parameters dictionary 
        namespace = "/"+self.get_parameter("namespace").value
        expected_types = {
            "device": (str, int),
            "model_path": str,

            "detection.inference_period": float,
            "detection.confidence_threshold": float,
            "detection.blur_variance": (float, int),         

            "sam.width": (float, int),
            "sam.length": (float, int),

            "topics.rviz.annotated_image": str,
            "topics.rviz.bw_blurred_sam": str,
            "topics.rviz.edges": str,

            "topics.predicted_position.sam": str,
            "topics.predicted_position.buoy": str,
            "topics.raw_image": str,

            "frames.map": str,
            "frames.quadrotor_odom": str,
            "frames.camera": str,
        }
        frames_topics = {
            "topics.rviz.annotated_image": namespace + "/"  + self.get_parameter("topics.rviz.annotated_image").value,
            "topics.rviz.bw_blurred_sam": namespace + "/"  + self.get_parameter("topics.rviz.bw_blurred_sam").value,
            "topics.rviz.edges": namespace + "/"  + self.get_parameter("topics.rviz.edges").value,

            "topics.predicted_position.sam": namespace + "/" + Topics.ESTIMATED_AUV_TOPIC,
            "topics.predicted_position.buoy": namespace + "/" + Topics.ESTIMATED_BUOY_TOPIC,
            "topics.raw_image": namespace + "/" + Topics.GIMBAL_CAMERA_RAW_TOPIC,

            "frames.map": namespace.removeprefix("/") + "/" + Links.MAP,
            "frames.quadrotor_odom": namespace.removeprefix("/") + "/" + Links.ODOM,
            "frames.camera": namespace.removeprefix("/") + "/" + Links.GIMBAL_CAMERA_LINK,

        }
        self.model_params = {
            k: self.get_parameter(k).value if not k.startswith("frames") and not k.startswith("topics")
            else frames_topics[k]
            for k in expected_types
        }
        self.model_params.update({"frame.camera_pixels": "camera_pixels_normalized"})

        # check parameter types
        for key, expected in expected_types.items():
            if not isinstance(self.model_params[key], expected):
                raise TypeError(f"{key} should be {expected}, got {type(self.model_params[key]).__name__}")
           
            
            

def main():
    rclpy.init()
    node = YOLODetector()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    rclpy.spin(node, executor=executor)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
