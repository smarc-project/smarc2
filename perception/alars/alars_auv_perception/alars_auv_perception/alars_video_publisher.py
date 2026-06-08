#!/usr/bin/env python3

import os
import cv2
import rclpy

from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class VideoImagePublisher(Node):
    """ROS 2 node for publishing video frames as ROS Image messages.

    This node reads a video file and publishes its frames as ROS Image messages
    at a specified rate, with options for looping, resizing, and pausing.
    """

    def __init__(self):
        super().__init__(
            'alars_video_publisher',
            allow_undeclared_parameters=True,
            automatically_declare_parameters_from_overrides=True
        )

        self.video_path = self._require_param('video_path')
        raw_image_topic = self._require_param('image_topic')
        raw_frame_id = self._require_param('frame_id')

        self.loop_video = bool(self._require_param('loop_video'))
        self.publish_fps = float(self._require_param('publish_fps'))
        self.resize_width = int(self._require_param('resize_width'))
        self.resize_height = int(self._require_param('resize_height'))
        self.paused = bool(self._require_param('start_paused'))

        self.image_topic = self._resolve_topic(raw_image_topic)
        self.frame_id = str(raw_frame_id).strip('/')

        if not self.frame_id:
            raise ValueError("Parameter 'frame_id' cannot be empty.")

        if not self.video_path:
            raise ValueError("Parameter 'video_path' is empty.")

        if not os.path.isfile(self.video_path):
            raise FileNotFoundError(f"Video file does not exist: {self.video_path}")

        self.bridge = CvBridge()
        self.pub = self.create_publisher(Image, self.image_topic, 10)

        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open video: {self.video_path}")

        video_fps = self.cap.get(cv2.CAP_PROP_FPS)
        if video_fps is None or video_fps <= 0:
            video_fps = 30.0

        self.effective_fps = self.publish_fps if self.publish_fps > 0.0 else float(video_fps)
        if self.effective_fps <= 0.0:
            self.effective_fps = 30.0

        self.timer_period = 1.0 / self.effective_fps
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        self.get_logger().info(f"ROS namespace: {self.get_namespace()}")
        self.get_logger().info(f"Video path: {self.video_path}")
        self.get_logger().info(f"Publishing topic: {self.image_topic}")
        self.get_logger().info(f"Frame id: {self.frame_id}")
        self.get_logger().info(f"Loop video: {self.loop_video}")
        self.get_logger().info(f"Paused at start: {self.paused}")
        self.get_logger().info(f"Effective FPS: {self.effective_fps:.2f}")

    def _require_param(self, name):
        value = self.get_parameter(name).value
        if value is None:
            raise ValueError(f"Required parameter '{name}' is missing.")
        return value

    def _resolve_topic(self, topic_name: str) -> str:
        topic = str(topic_name).strip()
        if not topic:
            raise ValueError("Parameter 'image_topic' cannot be empty.")

        if topic.startswith('/'):
            return topic

        ns = self.get_namespace().rstrip('/')
        if ns:
            return f"{ns}/{topic.lstrip('/')}"
        return f"/{topic.lstrip('/')}"

    def reopen_video(self) -> bool:
        self.cap.release()
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            self.get_logger().error(f"Failed to reopen video: {self.video_path}")
            return False
        return True

    def timer_callback(self):
        if self.paused:
            return

        ret, frame = self.cap.read()

        if not ret:
            if self.loop_video:
                self.get_logger().info("Reached end of video. Looping.")
                if not self.reopen_video():
                    return
                ret, frame = self.cap.read()
                if not ret:
                    self.get_logger().error("Could not read first frame after reopening video.")
                    return
            else:
                self.get_logger().info("Reached end of video. Stopping publisher timer.")
                self.timer.cancel()
                return

        if self.resize_width > 0 and self.resize_height > 0:
            frame = cv2.resize(frame, (self.resize_width, self.resize_height))

        msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id

        self.pub.publish(msg)

    def destroy_node(self):
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = VideoImagePublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()