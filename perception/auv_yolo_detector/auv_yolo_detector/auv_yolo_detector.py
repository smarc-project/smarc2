#!/usr/bin/env -S venv/bin/python
import rclpy
from ultralytics import YOLO
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
from image_geometry import PinholeCameraModel
from pathlib import Path
import os


class YOLODetector(Node):
    def __init__(self, name = 'auv_yolo_detector',
                 allow_undeclared_parameters=True,
                automatically_declare_parameters_from_overrides=True):
        super().__init__(name)
        self.get_params()
        
        # pubs and subs
        self.annotated_img_pub = self.create_publisher(msg_type=Image,
                                                       topic=self.model_params['topics.annotated_image'],
                                                       qos_profile=10)
        self.create_subscription(msg_type=Image, 
                                topic=self.model_params['topics.raw_image'], 
                                callback=self.image_callback,
                                qos_profile=10)
        self.create_subscription(msg_type=CameraInfo, 
                        topic=self.model_params['topics.camera_info'], 
                        callback=self.camera_info_callback,
                        qos_profile=10)
        
        # models (yolo and camera) 
        self.yolo_model = YOLO(self.model_params['model_path']+'/best_'+self.model_params['mode']+'.pt')
        self.yolo_model.info()
        self.camera_model = PinholeCameraModel()
        self.bridge = CvBridge()

        # timer to simulate tracking
        self.image = None
        self.classify_timer = self.create_timer(self.model_params['inference_frequency'], self.classify_callback)


    def classify_callback(self):
        if self.image is not None:
            cv_image = self.bridge.imgmsg_to_cv2(self.image, desired_encoding='bgr8')
            results = self.yolo_model.predict(source = cv_image, 
                            conf = self.model_params['confidence_threshold'],    
                            save = False,
                            verbose = False)
            # publish bounding box
            num_detections = results[0].obb.xywhr.shape[0]
            print(f'{num_detections} objects were detected')
            for i in range(num_detections): #xywhr (torch.Tensor | numpy.ndarray): Boxes in [x_center, y_center, width, height, rotation] format.
                print(f'Box {i+1}: {results[0].obb.xywhr[i]}')
                print(f'Inference time ({i+1}): {results[0].speed}')
            print()
     
            # publish annotated image as ros msg
            im = results[0].plot()
            ros_img = self.bridge.cv2_to_imgmsg(im, encoding = 'bgr8')
            self.annotated_img_pub.publish(ros_img)
    
    def image_callback(self, msg):
        self.image = msg

    def camera_info_callback(self, msg):
        self.camera_model.fromCameraInfo(msg)

    def get_params(self):
        # Declare parameters
        self.declare_parameter('mode', rclpy.Parameter.Type.STRING)
        self.declare_parameter('inference_frequency', rclpy.Parameter.Type.DOUBLE)
        self.declare_parameter('confidence_threshold', rclpy.Parameter.Type.DOUBLE)
        self.declare_parameter('model_path', rclpy.Parameter.Type.STRING)

        self.declare_parameter('frames.id.map', rclpy.Parameter.Type.STRING)
        self.declare_parameter('frames.id.quadrotor_odom', rclpy.Parameter.Type.STRING)
        self.declare_parameter('frames.id.sam_odom', rclpy.Parameter.Type.STRING)

        self.declare_parameter('topics.raw_image', rclpy.Parameter.Type.STRING)
        self.declare_parameter('topics.camera_info', rclpy.Parameter.Type.STRING)
        self.declare_parameter('topics.annotated_image', rclpy.Parameter.Type.STRING)

        # Retrieve parameters
        self.model_params = {
            "mode": self.get_parameter("mode").value,
            "inference_frequency": self.get_parameter("inference_frequency").value, 
            "confidence_threshold": self.get_parameter("confidence_threshold").value,
            'model_path': self.get_parameter("model_path").value,

            'frames.id.map': self.get_parameter('frames.id.map').value,
            'frames.id.quadrotor_odom': self.get_parameter('frames.id.quadrotor_odom').value,
            'frames.id.sam_odom': self.get_parameter('frames.id.sam_odom').value,

            'topics.raw_image': self.get_parameter('topics.raw_image').value,
            'topics.camera_info': self.get_parameter('topics.camera_info').value,
            'topics.annotated_image': self.get_parameter('topics.annotated_image').value
        }

def main():
    rclpy.init()
    node = YOLODetector()
    try:
        while True and rclpy.ok():
            rclpy.spin_once(node)            
    except KeyboardInterrupt:
        return
    pass
    


if __name__ == '__main__':
    main()
