#!/usr/bin/env -S venv/bin/python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import pathlib
from pathlib import PurePath
import os

class RecordData(Node):
    """
    Convert ROS image to jpeg and save it. Useful to create datasets
    """
    def __init__(self, name = 'record_data_node'):
        super().__init__(name)
        img_subs = self.create_subscription(msg_type=Image, 
                                            topic='/M350/gimbal_camera/image_raw', #'/Quadrotor/gimbal_camera/image_raw' OR '/Quadrotor/core/fpcamera/image'
                                            callback=self.image_callback,
                                            qos_profile=10)
        self.image: Image = None
        self.last_stamp = None
        self.end_flag = False

        # PARAMETERS: time interval between frames, initial frame index and initial run number
        self.period = 1.0
        self.frame_index = 1
        self.run = 1

        self.bridge = CvBridge()
        self.get_logger().info('Waiting for image')
        self.save_img_timer = self.create_timer(self.period, self.save_image_callback)

        # get/create directory to store images (should be within this pkg)
        self.path = os.path.join(pathlib.Path().resolve(), 
                                'perception/alars/auv_yolo_detector/images/real_images_djuro/run_'+str(self.run))
        p = pathlib.Path(self.path)
        p.mkdir(parents=True, exist_ok=True)
        self.get_logger().info(f'Saving image in {self.path}')


    def save_image_callback(self):

        if self.image is not None and not self.save_img_timer.is_canceled():
            current_image = self.image
            try:
                if False: 
                    self.save_img_timer.cancel()
                    self.get_logger().info('Frame extraction had ended.')
                    self.end_flag = True
                    return
            except:
                pass

            cv_image = self.bridge.imgmsg_to_cv2(self.image, desired_encoding='bgr8')
            cv2.imwrite(os.path.join(self.path, f'run{str(self.run)}_frame_{self.frame_index}.jpg'), cv_image)
            self.get_logger().info(f'Saving image {self.frame_index} ...')
            self.frame_index += 1
            self.last_stamp = current_image.header.stamp.sec

    def image_callback(self, msg):
        self.image = msg


def main():
    rclpy.init()
    node = RecordData()
    try:
        while True and rclpy.ok() and not node.end_flag:
            rclpy.spin_once(node)            
    except KeyboardInterrupt:
        return
    pass
    


if __name__ == '__main__':
    main()
