#!/usr/bin/env -S venv/bin/python
import rclpy
from ultralytics import YOLO
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
from image_geometry import PinholeCameraModel
from pathlib import Path
import numpy as np
from geometry_msgs.msg import PointStamped, Pose, PoseStamped
from nav_msgs.msg import Odometry
from tf2_ros import Buffer, TransformListener
import cv2
import tf2_geometry_msgs


class YOLODetector(Node):
    def __init__(self, name = 'auv_yolo_detector',
                 allow_undeclared_parameters=True,
                automatically_declare_parameters_from_overrides=True):
        super().__init__(name)
        self.get_params()

        # camera calibration matrix
        self.K = np.array([[369.5, 0, 320],
                           [0, 415.69, 240],
                           [0, 0, 1]])
        self.invK = np.linalg.inv(self.K)

        # detection filtering params
        self.sam_dim = [self.model_params['real_dimensions.sam.width'], self.model_params['real_dimensions.sam.height']]
        self.cam_fov = self.model_params['camera.fov']
        self.max_horizontal_vel = 1
        self.max_vertical_vel = 1
        self.prev_detections = None
 
        
        # pubs, subs and tf2
        self.create_subscription(msg_type=Image, 
                                topic=self.model_params['topics.sub.raw_image'], 
                                callback=self.image_callback,
                                qos_profile=10)
        self.create_subscription(msg_type=CameraInfo, 
                        topic=self.model_params['topics.sub.camera_info'], 
                        callback=self.camera_info_callback,
                        qos_profile=10)
        self.create_subscription(
            msg_type = Odometry,
            topic = self.model_params["topics.sub.drone_position"],
            callback = self.drone_position_callback,
            qos_profile= 10)
        self.annotated_img_pub = self.create_publisher(msg_type=Image,
                                            topic=self.model_params['topics.pub.annotated_image'],
                                            qos_profile=10)
        self.sam_position_pub = self.create_publisher(msg_type=PointStamped,
                                                      topic = self.model_params['topics.pub.predicted_position.sam'],
                                                      qos_profile=10)
        self.buoy_position_pub = self.create_publisher(msg_type=PointStamped,
                                                      topic = self.model_params['topics.pub.predicted_position.buoy'],
                                                      qos_profile=10)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.drone_position = PointStamped()
        
        # models (yolo and camera) 
        self.yolo_model = YOLO(self.model_params['model_path']+'/best_'+self.model_params['mode']+'2.pt')
        self.yolo_model.info()
        self.camera_model = PinholeCameraModel()
        self.bridge = CvBridge()

        # timer to simulate tracking
        self.image = None
        self.classify_timer = self.create_timer(self.model_params['inference_frequency'], self.classify_callback)


    def classify_callback(self):
        """ Infers with yolo model and publishes objects positions """
        if self.image is not None:
            cv_image = self.bridge.imgmsg_to_cv2(self.image, desired_encoding='bgr8')
            results = self.yolo_model.predict(source = cv_image, 
                            conf = self.model_params['confidence_threshold'],    
                            save = False,
                            verbose = False)
            
            # publish bounding box
            num_detections = results[0].obb.xywhr.shape[0]
            self.get_logger().info(f'{num_detections} objects were detected')
            for i in range(num_detections): #xywhr (torch.Tensor | numpy.ndarray): Boxes in [x_center, y_center, width, height, rotation] format.
                if results[0].obb.cls[i] == 0:
                    self.sam_position_pub.publish(self.pixels2frame(results[0].obb.xywhr[i][0],
                                                                    results[0].obb.xywhr[i][1],
                                                                    self.drone_position.point.z,
                                                                    self.model_params["frames.map"]))
            self.get_logger().info('\n')
     
            # publish annotated image as ros msg
            im = results[0].plot()
            ros_img = self.bridge.cv2_to_imgmsg(im, encoding = 'bgr8')
            self.annotated_img_pub.publish(ros_img)

    def pixels2frame(self, u:float, v:float, Z:float, frame: str) -> PointStamped:
        """
        Apllies camera matrix to obtain object position in camera frame and transforms it to specified frame"""
        camera_coord_norm = np.matmul(self.invK,np.array([u,v,1]))
        camera_coord = camera_coord_norm*Z

        pos = PointStamped()
        pos.header.frame_id = self.model_params["frames.camera"]
        pos.header.stamp = self.get_clock().now().to_msg()
        pos.point.x = camera_coord[2] # x axis in camera frame is depth
        pos.point.y = - camera_coord[0]
        pos.point.z = camera_coord[1]

        t = self.tf_buffer.lookup_transform(
            target_frame = frame,  
            source_frame = pos.header.frame_id,                 
            time = rclpy.time.Time())
        #self.get_logger().info(f'In desired frame, position = {tf2_geometry_msgs.do_transform_point(pos, t).point.x,tf2_geometry_msgs.do_transform_point(pos, t).point.y}')

        return tf2_geometry_msgs.do_transform_point(pos, t)
    
    def remove_outliers(self) -> bool:
        """
        TODO: implement simple outlier removel or kalman filter
        """
        if len(self.prev_detections) < 5:
            return True
        else:
            return False
        
    def drone_position_callback(self, msg: Odometry):
        """ Retrieve drone position (currently odometry gives in map_gt)"""
        self.drone_position.point =  msg.pose.pose.position 
        self.drone_position.header.stamp = self.get_clock().now().to_msg()
        self.drone_position.header.frame_id = msg.header.frame_id 

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

        self.declare_parameter('camera.fov', rclpy.Parameter.Type.DOUBLE)

        self.declare_parameter('real_dimensions.sam.width', rclpy.Parameter.Type.DOUBLE)
        self.declare_parameter('real_dimensions.sam.height', rclpy.Parameter.Type.DOUBLE)

        for mode in ['real', 'sim']:
            self.declare_parameter(f'frames.{mode}.map', rclpy.Parameter.Type.STRING)
            self.declare_parameter(f'frames.{mode}.quadrotor_odom', rclpy.Parameter.Type.STRING)
            self.declare_parameter(f'frames.{mode}.sam_odom', rclpy.Parameter.Type.STRING)
            self.declare_parameter(f'frames.{mode}.camera', rclpy.Parameter.Type.STRING)

            self.declare_parameter(f'topics.sub.{mode}.raw_image', rclpy.Parameter.Type.STRING)
            self.declare_parameter(f'topics.sub.{mode}.camera_info', rclpy.Parameter.Type.STRING)
            self.declare_parameter(f'topics.sub.{mode}.drone_position', rclpy.Parameter.Type.STRING)

        self.declare_parameter('topics.pub.annotated_image', rclpy.Parameter.Type.STRING)
        self.declare_parameter('topics.pub.predicted_position.sam', rclpy.Parameter.Type.STRING)
        self.declare_parameter('topics.pub.predicted_position.buoy', rclpy.Parameter.Type.STRING)

        mode = self.get_parameter("mode").value
        if mode not in ['real', 'sim']:
            self.get_logger().warn(f"Invalid mode '{mode}' specified. Defaulting to 'sim'.")
            mode = 'sim'

        # retrieve params
        self.model_params = {
            "mode": self.get_parameter("mode").value,
            "inference_frequency": self.get_parameter("inference_frequency").value,
            "confidence_threshold": self.get_parameter("confidence_threshold").value,
            "model_path": self.get_parameter("model_path").value,

            "camera.fov": self.get_parameter("camera.fov").value,
            "real_dimensions.sam.width": self.get_parameter("real_dimensions.sam.width").value,
            "real_dimensions.sam.height": self.get_parameter("real_dimensions.sam.height").value,

            "frames.map": self.get_parameter(f"frames.{mode}.map").value,
            "frames.quadrotor_odom": self.get_parameter(f"frames.{mode}.quadrotor_odom").value,
            "frames.sam_odom": self.get_parameter(f"frames.{mode}.sam_odom").value,
            "frames.camera": self.get_parameter(f"frames.{mode}.camera").value,

            "topics.sub.raw_image": self.get_parameter(f"topics.sub.{mode}.raw_image").value,
            "topics.sub.camera_info": self.get_parameter(f"topics.sub.{mode}.camera_info").value,
            "topics.sub.drone_position": self.get_parameter(f"topics.sub.{mode}.drone_position").value,

            "topics.pub.annotated_image": self.get_parameter("topics.pub.annotated_image").value,
            "topics.pub.predicted_position.sam": self.get_parameter("topics.pub.predicted_position.sam").value,
            "topics.pub.predicted_position.buoy": self.get_parameter("topics.pub.predicted_position.buoy").value,
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
