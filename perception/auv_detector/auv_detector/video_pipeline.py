import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import auv_detector.params_detector as P

class VideoPublisher(Node):
    def __init__(self):
        super().__init__('video_publisher')
        self.publisher_ = self.create_publisher(Image, P.REALDATA_TOPIC, 10)  # Topic name: camera/image
        self.br = CvBridge()
        self.timer = None
        
        # Load video file
        self.video_path = P.REALDATA_PATH  # Replace with your video path
        self.cap = cv2.VideoCapture(self.video_path)
        
        if not self.cap.isOpened():
            self.get_logger().error("Could not open video file!")
            return

        # Get video FPS to control publishing rate
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.timer = self.create_timer(1.0 / self.fps, self.timer_callback)

    def timer_callback(self):
        ret, frame = self.cap.read()
        
        if not ret:
            self.get_logger().info("Video playback finished.")
            self.cap.release()
            self.destroy_timer(self.timer)
            return
        
        # Preprocess the frame to match Unity camera settings
        frame = self.preprocess_frame(frame)

        # Convert frame (OpenCV format) to ROS Image message
        img_msg = self.br.cv2_to_imgmsg(frame, encoding="bgr8")
        self.publisher_.publish(img_msg)
        # self.get_logger().info("Published a frame.")

    def preprocess_frame(self, frame):
        # Resize the frame to 640x480 (Unity camera resolution)
        frame = cv2.resize(frame, (640, 480))
        
        # Rotate the frame 180 degrees (Unity camera orientation)
        frame = cv2.flip(frame, -1)  # Flip both axes

        return frame

def main(args=None):
    rclpy.init(args=args)
    video_publisher = VideoPublisher()
    rclpy.spin(video_publisher)
    video_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()