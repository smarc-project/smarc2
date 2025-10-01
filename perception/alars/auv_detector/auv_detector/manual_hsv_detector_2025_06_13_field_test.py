#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import argparse


# HSV  buoy [16 0 255]  ~ [25 152 255]  orange color
# HSV  auv  [0 55 153] ~ [195 97 254]  yellow color

def setup_trackbars(range_filter):
    cv2.namedWindow("Trackbars", 0)
    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255
        for j in range_filter:
            cv2.createTrackbar(f"{j}_{i}", "Trackbars", v, 255, lambda x: None)


def get_trackbar_values(range_filter):
    values = []
    for i in ["MIN", "MAX"]:
        for j in range_filter:
            v = cv2.getTrackbarPos(f"{j}_{i}", "Trackbars")
            values.append(v)
    return values


class HSVDetectorNode(Node):
    def __init__(self, image_path=None):
        super().__init__('hsv_detector')
        self.bridge = CvBridge()
        self.image_path = image_path
        self.cv2_img = None
        self.range_filter = "HSV"

        setup_trackbars(self.range_filter)

        if not self.image_path:
            self.subscription = self.create_subscription(
                Image,
                '/M350/gimbal_camera/image_raw',
                self.image_callback,
                10
            )
            self.get_logger().info("Subscribed to /M350/gimbal_camera/image_raw")

    def image_callback(self, msg):
        try:
            self.cv2_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except CvBridgeError as e:
            self.get_logger().error(f"CvBridge Error: {e}")

    def process_image(self, image):
        frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values(self.range_filter)
        thresh = cv2.inRange(frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))
        preview = cv2.bitwise_and(image, image, mask=thresh)
        return preview


def main(args=None):
    parser = argparse.ArgumentParser(description="HSV Detector for ROS 2")
    parser.add_argument("-i", "--image", required=False, help="Path to input static image")
    parsed_args, unknown = parser.parse_known_args()

    rclpy.init(args=unknown)
    node = HSVDetectorNode(image_path=parsed_args.image)

    try:
        if parsed_args.image:
            image = cv2.imread(parsed_args.image)
            if image is None:
                node.get_logger().error(f"Failed to load image from {parsed_args.image}")
                return
            while True:
                preview = node.process_image(image)
                cv2.imshow("Preview", preview)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        else:
            while rclpy.ok():
                rclpy.spin_once(node, timeout_sec=0.1)
                if node.cv2_img is not None:
                    preview = node.process_image(node.cv2_img)
                    cv2.imshow("Preview", preview)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
