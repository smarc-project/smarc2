# import rclpy
# from rclpy.node import Node
# import cv2
# import numpy as np
# from cv_bridge import CvBridge, CvBridgeError
# from sensor_msgs.msg import Image
# from std_msgs.msg import Float32

# # Function to detect the yellow object and compute its distance from the drone
# def detect_yellow_object(frame):
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#     lower_yellow = np.array([20, 100, 100])
#     upper_yellow = np.array([30, 255, 255])
#     mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
#     contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

#     for contour in contours:
#         # area = cv2.contourArea(contour)
#         # if area > 500:  # Filter out small contours
#         x, y, w, h = cv2.boundingRect(contour)
#         # Calculate the centroid of the contour
#         M = cv2.moments(contour)
#         if M['m00'] != 0:
#             cx = int(M['m10'] / M['m00'])
#             cy = int(M['m01'] / M['m00'])
#             # Assume a known height of the AUV to calculate distance (e.g., height in meters)
#             known_height = 1.318  # meters, capsule collider height for now
#             focal_length = 554  # Example focal length in pixels
#             distance = (known_height * focal_length) / h
#             return float(h)
#     return None

# class AUVDistancePublisher(Node):
#     def __init__(self):
#         super().__init__('auv_distance_publisher')
#         self.bridge = CvBridge()
#         self.image_sub = self.create_subscription(
#             Image,
#             '/Quadrotor/drone/fpcam/image_raw',
#             self.image_callback,
#             10)
#         self.distance_pub = self.create_publisher(Float32, '/Quadrotor/drone/fpcam/distance', 10)

#     def image_callback(self, data):
#         try:
#             cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
#         except CvBridgeError as e:
#             self.get_logger().error(f"CvBridge Error: {e}")
#             return

#         distance = detect_yellow_object(cv_image)
#         if distance is not None:
#             self.get_logger().info(f"Distance to AUV: {distance:.2f} meters")
#             self.distance_pub.publish(Float32(data=distance))
#         else:
#             self.get_logger().info("AUV not detected")

# def main(args=None):
#     rclpy.init(args=args)
#     node = AUVDistancePublisher()
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         node.get_logger().info("Shutting down")
#     finally:
#         node.destroy_node()
#         rclpy.shutdown()

# if __name__ == '__main__':
#     main()
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
from std_msgs.msg import Float32
from visualization_msgs.msg import Marker

# Function to detect the yellow object and compute its distance from the drone
def detect_yellow_object(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # area = cv2.contourArea(contour)
        # if area > 500:  # Filter out small contours
        x, y, w, h = cv2.boundingRect(contour)
        # Assume a known height of the AUV to calculate distance (e.g., height in meters)
        known_height = 1.318  # meters, capsule collider height for now
        focal_length = 554  # Example focal length in pixels
        distance = (known_height * focal_length) / h
        return distance, (x, y, w, h)
    return None, None

class AUVDistancePublisher(Node):
    def __init__(self):
        super().__init__('auv_distance_publisher')
        self.bridge = CvBridge()
        self.image_sub = self.create_subscription(
            Image,
            '/Quadrotor/drone/fpcam/image_raw',
            self.image_callback,
            10)
        self.distance_pub = self.create_publisher(Float32, '/Quadrotor/drone/fpcam/distance', 10)
        self.marker_pub = self.create_publisher(Marker, '/Quadrotor/drone/fpcam/bounding_box', 10)

    def image_callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            self.get_logger().error(f"CvBridge Error: {e}")
            return

        distance, bbox = detect_yellow_object(cv_image)
        if distance is not None:
            self.get_logger().info(f"Distance to AUV: {distance:.2f} meters")
            self.distance_pub.publish(Float32(data=distance))
            self.publish_bounding_box_marker(bbox)
        else:
            self.get_logger().info("AUV not detected")

    def publish_bounding_box_marker(self, bbox):
        x, y, w, h = bbox
        marker = Marker()
        marker.header.frame_id = "camera_frame"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "auv"
        marker.id = 0
        marker.type = Marker.CUBE
        marker.action = Marker.ADD

        # Define the position and size of the bounding box
        marker.pose.position.x = float(x + w / 2)
        marker.pose.position.y = float(y + h / 2)
        marker.pose.position.z = 0.0
        marker.pose.orientation.x = 0.0
        marker.pose.orientation.y = 0.0
        marker.pose.orientation.z = 0.0
        marker.pose.orientation.w = 1.0
        marker.scale.x = float(w)
        marker.scale.y = float(h)
        marker.scale.z = 1.0  # Assuming a flat 2D bounding box

        marker.color.a = 1.0  # Alpha
        marker.color.r = 1.0  # Red
        marker.color.g = 1.0  # Green
        marker.color.b = 0.0  # Blue
        self.get_logger().info("publishing bounding box")
        self.marker_pub.publish(marker)

def main(args=None):
    rclpy.init(args=args)
    node = AUVDistancePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
