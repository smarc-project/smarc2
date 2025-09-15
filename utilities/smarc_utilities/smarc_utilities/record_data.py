#!/usr/bin/env -S venv/bin/python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import pathlib
import os

class RecordData(Node):
    """
    Convert ROS image to jpeg and save it. Useful to create datasets
    """
    def __init__(self, name = 'record_data_node'):
        super().__init__(name)
        img_subs = self.create_subscription(msg_type=Image, 
                                            topic='/Quadrotor/gimbal_camera/image_raw', #'/Quadrotor/gimbal_camera/image_raw' OR '/Quadrotor/core/fpcamera/image'
                                            callback=self.image_callback,
                                            qos_profile=10)
        self.image = None
        self.frame_index = 1

        self.bridge = CvBridge()
        self.get_logger().info('yeah')
        self.save_img_timer = self.create_timer(0.25, self.save_image_callback)
        self.path = os.path.join(pathlib.Path().resolve(), 'real_images/run17')


    def save_image_callback(self):
        if self.image is not None:
            cv_image = self.bridge.imgmsg_to_cv2(self.image, desired_encoding='bgr8')
            cv2.imwrite(os.path.join(self.path, f'run1_frame_{self.frame_index}.jpg'), cv_image)
            self.get_logger().info('Saving image (hopefully) ...')
            self.frame_index += 1

    def image_callback(self, msg):
        self.image = msg


def main():
    rclpy.init()
    node = RecordData()
    try:
        while True and rclpy.ok():
            rclpy.spin_once(node)            
    except KeyboardInterrupt:
        return
    pass
    


if __name__ == '__main__':
    main()
