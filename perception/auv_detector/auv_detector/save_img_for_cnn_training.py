#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import argparse
from datetime import datetime


# HSV  buoy [16 0 255]  ~ [25 152 255]  orange color
# HSV  auv  [0 55 153] ~ [195 97 254]  yellow color

def setup_trackbars(range_filter):
    cv2.namedWindow("Trackbars", 0)
    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255
        for j in range_filter:
            cv2.createTrackbar(f"{j}_{i}", "Trackbars", v, 255, lambda x: None)
    # Add a "Save Image" button-like trackbar
    cv2.createTrackbar("Save_Image", "Trackbars", 0, 1, lambda x: None)

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

        self.last_preview = None  # <-- NEW

        # Setup mouse callback for clicking "save" area
        cv2.namedWindow("Preview")
        #cv2.setMouseCallback("Preview", self.mouse_callback)
        
        self.save_dir = "processed_img_for_cnn_training"
        os.makedirs(self.save_dir, exist_ok=True)  # Create folder if it doesn't exist

        setup_trackbars(self.range_filter)

        if not self.image_path:
            self.subscription = self.create_subscription(
                Image,
                '/Quadrotor/core/fpcamera/image',
                self.image_callback,
                10
            )
            self.get_logger().info("Subscribed to /Quadrotor/core/fpcamera/image")

    # def mouse_callback(self, event, x, y, flags, param=None):
    #     # Click inside the green box to save image
    #     if event == cv2.EVENT_LBUTTONDOWN:
    #         if 10 <= x <= 110 and 10 <= y <= 50:
    #             if self.last_preview is not None:
    #                 cv2.imwrite("saved_image.jpg", self.last_preview)
    #                 self.get_logger().info("Image saved by mouse click!")


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

        # # Draw fake "Save" button
        # cv2.rectangle(preview, (10, 10), (110, 50), (0, 255, 0), -1)
        # cv2.putText(preview, "Save", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        self.last_preview = preview.copy()

        if cv2.getTrackbarPos("Save_Image", "Trackbars") == 1:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            #filename = f"saved_{timestamp}.jpg"
            filename = os.path.join(self.save_dir, f"saved_{timestamp}.jpg")
            cv2.imwrite(filename, self.last_preview)
            self.get_logger().info(f"Image saved as {filename}")
            cv2.setTrackbarPos("Save_Image", "Trackbars", 0)  # Reset

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
                elif cv2.waitKey(1) & 0xFF == ord('s'):
                    if node.last_preview is not None:
                        cv2.imwrite("saved_image.jpg", node.last_preview)
                        node.get_logger().info("Image saved by keypress!")

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
