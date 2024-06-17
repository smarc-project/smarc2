# import rclpy
# from rclpy.node import Node
# from sensor_msgs.msg import Image
# import cv2
# from cv_bridge import CvBridge

# class ColorDetector(Node):

#     def __init__(self):
#         super().__init__('color_detector')
#         self.subscription = self.create_subscription(
#             Image,
#             '/Quadrotor/drone/fpcam/image_raw',  # replace with your actual camera topic name
#             self.listener_callback,
#             10)
#         self.subscription  # prevent unused variable warning
#         self.bridge = CvBridge()

#     def listener_callback(self, msg):
#         cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
#         hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
#         lower_yellow = (20, 100, 100)
#         upper_yellow = (30, 255, 255)
#         mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
#         result = cv2.bitwise_and(cv_image, cv_image, mask=mask)
        
#         # Visualization
#         cv2.imshow("Yellow Detection", result)
#         cv2.waitKey(1)

# def main(args=None):
#     rclpy.init(args=args)
#     color_detector = ColorDetector()
#     rclpy.spin(color_detector)
#     color_detector.destroy_node()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge

class ColorDetector(Node):

    def __init__(self):
        super().__init__('color_detector')
        self.subscription = self.create_subscription(
            Image,
            '/Quadrotor/drone/fpcam/image_raw',  # replace with your actual camera topic name
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        self.bridge = CvBridge()
        self.mask_publisher = self.create_publisher(Image, '/Quadrotor/drone/fpcam/image_processed', 10)

    def listener_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        lower_yellow = (20, 100, 100)
        upper_yellow = (30, 255, 255)
        mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
        result = cv2.bitwise_and(cv_image, cv_image, mask=mask)

        # Publish the mask
        mask_msg = self.bridge.cv2_to_imgmsg(mask, encoding="mono8")
        self.mask_publisher.publish(mask_msg)

        # Visualization
        cv2.imshow("Yellow Detection", result)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    color_detector = ColorDetector()
    rclpy.spin(color_detector)
    color_detector.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
