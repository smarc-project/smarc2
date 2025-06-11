#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
import numpy as np
import cv2
from PIL import Image as PILImage
from std_msgs.msg import Float32MultiArray
from collections import deque

# ==== CNN Definition (same as in training file) ====
class AnchorPointCNN(nn.Module):
    def __init__(self):
        super(AnchorPointCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.conv3 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 28 * 28, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 4)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

# ==== ROS Node ====
class AnchorPointPredictor(Node):
    def __init__(self):
        super().__init__('anchor_point_predictor')
        self.subscription = self.create_subscription(
            Image,
            '/Quadrotor/core/fpcamera/image',
            self.listener_callback,
            10
        )
        self.bridge = CvBridge()
        self.model = AnchorPointCNN()
        self.model.load_state_dict(torch.load('anchor_point_cnn.pth', map_location=torch.device('cpu')))
        self.model.eval()

        self.input_size = (224, 224)
        self.orig_size = (640, 480)
        self.transform = transforms.Compose([
            transforms.Resize(self.input_size),
            transforms.ToTensor()
        ])
        self.rope_img_buffer = deque(maxlen=10)

    def listener_callback(self, msg):
        try:
            # Convert ROS image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # cv2.imshow("cv_image", cv_image)
        
            image = cv_image.copy()

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

                    cx_buoy = cx
                    cy_buoy = cy
                    #cv2.circle(preview_buoy, (cx, cy), 10, (0, 0, 255), 1)

                    # Put area text
                    #cv2.putText(preview_buoy, f"Area: {int(max_area)}", (cx + 10, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow('HSV_buoy', preview_buoy)  

            #########################################################################################  auv

            # HSV filter for sam auv
            lower_yellow = np.array([0, 55, 153])  # manual hsv detector
            upper_yellow = np.array([195, 97, 254])
            hsv_thresh_auv = cv2.inRange(imghsv, lower_yellow, upper_yellow)
            preview_auv = cv2.bitwise_and(image, image, mask=hsv_thresh_auv)
            preview_auv_2 = preview_auv.copy()
            #cv2.imshow('HSV_auv', preview_auv)
            
            # Find contours
            contours, _ = cv2.findContours(hsv_thresh_auv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Find largest contour
            max_area = 0
            max_contour = None
            center_auv = None

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > max_area:
                    max_area = area
                    max_contour = cnt

            # Draw largest contour and show area
            if max_contour is not None:
                # Draw the contour
                # cv2.drawContours(preview_auv, [max_contour], -1, (0, 255, 0), 1)

                # Get center
                M = cv2.moments(max_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    #center_auv = (cx,cy)
                    center_auv = np.array([cx, cy])
                    #cv2.circle(preview_auv, (cx, cy), 10, (0, 0, 255), 1)

                    cx_auv = cx
                    cy_auv = cy

                    # Put area text
                    #cv2.putText(preview_auv, f"AUV Area: {int(max_area)}", (cx + 10, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            cv2.imshow('HSV_auv', preview_auv)



            # Missle-Shape detector Parameters
            min_area = 300
            min_aspect_ratio = 2.5  # Tune this: 2.5 means at least 2.5x longer than wide
            best_contour = None
            best_ratio = 0

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < min_area:
                    continue

                # Fit rotated rectangle to get aspect ratio
                rect = cv2.minAreaRect(cnt)
                width, height = rect[1]

                if width == 0 or height == 0:
                    continue

                aspect_ratio = max(width, height) / min(width, height)

                if aspect_ratio > min_aspect_ratio and aspect_ratio > best_ratio:
                    best_ratio = aspect_ratio
                    best_contour = cnt

            # Draw best contour if found
            if best_contour is not None:
                rect = cv2.minAreaRect(best_contour)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(preview_auv_2, [box], 0, (0, 255, 0), 2)

                # Get center from rect
                center = tuple(map(int, rect[0]))
                cv2.circle(preview_auv_2, center, 3, (0, 0, 255), -1)
                cv2.putText(preview_auv_2, f"AUV W/H: {best_ratio:.2f}", (center[0] + 10, center[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


            #cv2.imshow('HSV_auv_Missle_Shape Detect', preview_auv_2)


            #########################################################################################   rope

            # HSV filter for rope
            lower_rope = np.array([3, 146, 82])  # manual hsv detector
            upper_rope = np.array([13, 255, 245])
            hsv_thresh_rope = cv2.inRange(imghsv, lower_rope, upper_rope)
            preview_rope = cv2.bitwise_and(image, image, mask=hsv_thresh_rope)
            preview_rope_2 = preview_rope.copy()
            preview_rope_3 = preview_rope.copy()
            #cv2.imshow('HSV_rope', preview_rope)

            # Rope Reconstruction method 4 ---- multi frames
            self.rope_img_buffer.append(preview_rope_3)
            for img_tmp in self.rope_img_buffer:
                preview_rope_3 = cv2.add(preview_rope_3, img_tmp)
            cv2.imshow("N frames rope detect", preview_rope_3)


        

            # Apply dilation to connect fragmented rope segments
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 8))  # or (3,3) if rope is thin
            rope_dilated = cv2.dilate(preview_rope_3, kernel, iterations=1)
            # Use this dilated result for binary mask and grid processing
            rope_bin = cv2.cvtColor(rope_dilated, cv2.COLOR_BGR2GRAY)
            _, rope_bin = cv2.threshold(rope_bin, 1, 255, cv2.THRESH_BINARY)
            #cv2.imshow("Dilation", rope_bin)

            #contours, _ = cv2.findContours(rope_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            #cv2.drawContours(preview_rope_2, contours, -1, (0,255,0), 2)

            # Curve fitting 

            # Get coordinates of white pixels (rope)
            ys, xs = np.where(rope_bin == 255)
            if len(xs) >= 3:   # if rope exist
                # Fit a 2nd or 3rd degree polynomial (x = f(y) or y = f(x))
                coeffs = np.polyfit(xs, ys, deg=3)  # Try deg=2 or 3   # can be changed by distance
                poly_func = np.poly1d(coeffs)
                # Generate smoothed rope line
                x_fit_rope = np.linspace(min(xs), max(xs), 100)
                y_fit_rope = poly_func(x_fit_rope)
                
                for x, y in zip(x_fit_rope.astype(int), y_fit_rope.astype(int)):
                    cv2.circle(preview_rope_2, (x, y), 1, (0, 255, 0), -1)
                
                #center_x_rope = int(np.mean(x_fit_rope))
                #center_y_rope = int(np.mean(y_fit_rope))

                center_x_rope = int(x_fit_rope[50])
                center_y_rope = int(y_fit_rope[50])
                #cv2.circle(preview_rope_2, (center_x_rope, center_y_rope), 5, (0, 255, 0), 1) # rope center

                # cv2.putText(preview_rope_2, "Heading Point", (center_x_rope + 10, center_y_rope - 10),
                #                     cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                cv2.imshow("Curve Fitting", preview_rope_2)


            ######################################################################################### 

            # Just add the filtered images directly
            combined_preview = cv2.add(preview_buoy, preview_auv)
            combined_preview = cv2.add(combined_preview, preview_rope_3)

            # Show the combined result
            cv2.imshow('Combined_HSV', combined_preview)



            ######################################################################################### 
            original_image = cv_image.copy()

            # Preprocess for CNN
            #pil_image = PILImage.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
            pil_image = PILImage.fromarray(cv2.cvtColor(combined_preview, cv2.COLOR_BGR2RGB))
            input_tensor = self.transform(pil_image).unsqueeze(0)

            # Inference
            with torch.no_grad():
                output = self.model(input_tensor).squeeze().numpy()

            # Rescale to original image size
            x_scale = self.orig_size[0] / self.input_size[0]
            y_scale = self.orig_size[1] / self.input_size[1]
            x1, y1, x2, y2 = output
            x1, y1 = int(x1 * x_scale), int(y1 * y_scale)
            x2, y2 = int(x2 * x_scale), int(y2 * y_scale)

            # Draw predicted points
            cv2.circle(original_image, (x1, y1), 6, (0, 255, 0), -1)  # P1: Green
            cv2.circle(original_image, (x2, y2), 6, (0, 0, 255), -1)  # P2: Red
            cv2.putText(original_image, f"P1", (x1+5, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(original_image, f"P2", (x2+5, y2-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # Show image with overlay
            cv2.imshow("Anchor Points Prediction", original_image)
            cv2.waitKey(1)

            self.get_logger().info(f"Predicted Points: ({x1}, {y1}), ({x2}, {y2})")

        except Exception as e:
            self.get_logger().error(f"Error processing image: {e}")

# ==== Main ====
def main(args=None):
    rclpy.init(args=args)
    predictor = AnchorPointPredictor()
    rclpy.spin(predictor)
    predictor.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()