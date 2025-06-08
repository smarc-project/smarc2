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
from std_msgs.msg import Float32MultiArray


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
        self.points = []  # <-- NEW: store clicked points
        self.clear_points = 0

        # Setup mouse callback for clicking "save" area
        cv2.namedWindow("Preview")
        cv2.setMouseCallback("Preview", self.mouse_callback)
        
        self.save_dir_processed = "for_cnn_training_processed_img"
        self.save_dir_original = "for_cnn_training_original_img"
        self.save_dir_points = "for_cnn_training_points"
        # buoy 
        # rope 
        # auv
        # buoy-rope-auv
        os.makedirs(self.save_dir_processed, exist_ok=True)  # Create folder if it doesn't exist
        os.makedirs(self.save_dir_original, exist_ok=True)
        os.makedirs(self.save_dir_points, exist_ok=True)


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

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.points) >= 2:
                self.points = []  # Reset after two clicks
            self.points.append((x, y))
            self.get_logger().info(f"Clicked point: ({x}, {y})")  # <-- NEW

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

        # Draw clicked points
        # Draw clicked points with different colors
        for idx, point in enumerate(self.points):
            if idx == 0:
                color = (0, 255, 255)  # yellow for first click (BGR format)
                label = "P1"
            elif idx == 1:
                color = (0, 255, 0)  # Green for second click
                label = "P2"
            else:
                color = (0, 255, 255)  # fallback, shouldn't happen
                label = f"P{idx+1}"

            cv2.circle(preview, point, 5, color, -1)
            cv2.putText(preview, f"{label}: ({point[0]}, {point[1]})",
                        (point[0] + 5, point[1] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        self.last_preview = preview.copy()


        #########################################################################################  buoy
        imghsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype("float32")
        # HSV filter for buoy
        lower_orange = np.array([16, 0, 255])  # manual hsv detector
        upper_orange = np.array([25, 152, 255])
        hsv_thresh_buoy = cv2.inRange(imghsv, lower_orange, upper_orange)
        preview_buoy = cv2.bitwise_and(image, image, mask=hsv_thresh_buoy)
        #cv2.imshow('HSV_buoy', preview_buoy)

        # Find contours
        contours, _ = cv2.findContours(hsv_thresh_buoy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find largest contour
        max_area = 0
        max_contour = None
        center_buoy = None

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > max_area:
                max_area = area
                max_contour = cnt

        # Draw largest contour and show area
        if max_contour is not None:
            # Draw the contour
            # cv2.drawContours(preview_buoy, [max_contour], -1, (0, 255, 0), 1)

            # Get center
            M = cv2.moments(max_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                #center_buoy = (cx, cy)
                center_buoy = np.array([cx, cy])

                buoy_position_msg = Float32MultiArray()
                buoy_position_msg.data = [float(cx), float(cy)]  # Publish the coordinates of the point
                #self.get_logger().info(f"detect buoy")

                cv2.circle(preview_buoy, (cx, cy), 10, (0, 0, 255), 1)

                # Put area text
                cv2.putText(preview_buoy, f"Area: {int(max_area)}", (cx + 10, cy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        #cv2.imshow('HSV_buoy', preview_buoy) ok 
        #########################################################################################


        # save images 

        if cv2.getTrackbarPos("Save_Image", "Trackbars") == 1:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            #filename = f"saved_{timestamp}.jpg"
            filename = os.path.join(self.save_dir_processed, f"processed_{timestamp}.jpg")
            cv2.imwrite(filename, self.last_preview)

            filename_original = os.path.join(self.save_dir_original, f"original_{timestamp}.jpg")
            cv2.imwrite(filename_original, self.cv2_img)

            # Save each point in separate file
            for idx, point in enumerate(self.points):
                label = f"P{idx+1}"
                txt_filename = os.path.join(self.save_dir_points, f"{label}_{timestamp}.txt")
                with open(txt_filename, 'w') as f:
                    # Save as: x y
                    f.write(f"{point[0]} {point[1]}\n")

                self.get_logger().info(f"Point {label} saved as {txt_filename}")

            self.get_logger().info(f"Image saved as {filename}")
            cv2.setTrackbarPos("Save_Image", "Trackbars", 0)  # Reset
            self.points = []  # Reset after two clicks
            # print(f"Image size: {self.cv2_img.shape}")  # Outputs (height, width, channels)  (480, 640, 3)

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

                    # too slow 
                    # elif cv2.waitKey(1) & 0xFF == ord('s'):
                    #     node.get_logger().info("click ssssss ")
                    #     if node.last_preview is not None:
                    #         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    #         filename = os.path.join(node.save_dir, f"saved_{timestamp}.jpg")
                    #         cv2.imwrite(filename, node.last_preview)
                    #         node.get_logger().info(f"Image saved by keypress as {filename}")
        
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
