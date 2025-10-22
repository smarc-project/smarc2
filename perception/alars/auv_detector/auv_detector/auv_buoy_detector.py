import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import PointStamped
from cv_bridge import CvBridge
import cv2
import numpy as np
from dji_msgs.msg import Topics
from std_srvs.srv import Trigger
from std_msgs.msg import Float32
from smarc_msgs.msg import Topics as SMARCTopics
from collections import deque


import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image as PILImage
from collections import deque
import os

from ament_index_python.packages import get_package_share_directory
import yaml


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



class DetectionNode(Node):
    def __init__(self):
        super().__init__('detection_node')

        self.declare_parameter('debug_imshow', 2)
        self.declare_parameter('enable_buoy_detector', 1)
        self.declare_parameter('enable_auv_detector', 1)
        self.declare_parameter('enable_rope_detector', 1)
        self.declare_parameter('enable_cnn_detector', 1)
        self.declare_parameter('enable_on_start', 1)

        self.declare_parameter('buoy_color_lower_orange', [8, 121, 35])
        self.declare_parameter('buoy_color_upper_orange', [40, 157, 247])

        self.declare_parameter('auv_color_lower_yellow', [25, 0, 169])
        self.declare_parameter('auv_color_upper_yellow', [46, 103, 221])

        self.declare_parameter('rope_color_lower', [0, 92, 242])
        self.declare_parameter('rope_color_upper', [86, 255, 255])     
        self.declare_parameter('rope_img_buffer', 8)   
        self.declare_parameter('rope_erosion_scale', 0)
        self.declare_parameter('rope_dilation_scale', 8)
        self.declare_parameter('rope_hough_circle_min', 10)
        self.declare_parameter('rope_hough_circle_max', 100)
        self.declare_parameter('dist_threshold_between_auv_and_buoy',80)

        # default values from field test rosbag
        self.declare_parameter('calibration_altitude', 8.7)
        self.declare_parameter('buoy_area_percent_at_calibration_altitude', 0.007)
        self.declare_parameter('auv_area_percent_at_calibration_altitude', 0.149)
        self.declare_parameter('sensitivity_area_percent', 0.10)
        self.declare_parameter('least_area_pixels', 10)

        self._CAMERA_PIXELS_FRAME = "camera_pixels_normalized"  # Frame for publishing detected points

        self.declare_parameter('model_path', '/home/lifan/colcon_ws/src/smarc2/perception/alars/auv_detector/auv_detector/anchor_point_cnn_dynamic_roi_validate_20251007_163547.pth')

        ################################################################################
        # Frequent Adjustments
        # Note: On Jetson, set to 0 to maintain a publish rate of ~30 Hz
        self.debug_imshow = int(self.get_parameter('debug_imshow').value)  # 0: disable display, 1: show one frame, 2: show all frames

        # Color Mask Thresholds
        # Buoy detection (orange range)

        self.buoy_color_lower_orange = np.array(
            self.get_parameter('buoy_color_lower_orange').value, dtype=np.uint8
        )
        self.buoy_color_upper_orange = np.array(
            self.get_parameter('buoy_color_upper_orange').value, dtype=np.uint8
        )

        

        # AUV detection (yellow range)
        self.auv_color_lower_yellow = np.array(
            self.get_parameter('auv_color_lower_yellow').value, dtype=np.uint8
        )
        self.auv_color_upper_yellow = np.array(
            self.get_parameter('auv_color_upper_yellow').value, dtype=np.uint8
        )


        # Rope detection 
        self.rope_color_lower = np.array(
            self.get_parameter('rope_color_lower').value, dtype=np.uint8
        )
        self.rope_color_upper = np.array(
            self.get_parameter('rope_color_upper').value, dtype=np.uint8
        )

        
        # Minimum and maximum area thresholds at 8.7 meters, so you can intuitively estimate
        # what percentage of the image the buoy and AUV will occupy.
        # unit: meter
        self.initial_altitude = self.get_parameter('calibration_altitude').get_parameter_value().double_value  
        # unit: percentage
        self.buoy_area_percent_at_initial_altitude = 0.01 * self.get_parameter('buoy_area_percent_at_calibration_altitude').get_parameter_value().double_value
        self.auv_area_percent_at_initial_altitude = 0.01 * self.get_parameter('auv_area_percent_at_calibration_altitude').get_parameter_value().double_value
        self.sensitivity_area_percent = 0.01 * self.get_parameter('sensitivity_area_percent').get_parameter_value().double_value


        # The lower bound of the detection is usually set to 10 to remove environmental noise. 
        # unit: Pixel
        self.least_area_pixels = self.get_parameter('least_area_pixels').get_parameter_value().integer_value
    
        self.get_logger().info(f"Buoy HSV Lower: {self.buoy_color_lower_orange}, Upper: {self.buoy_color_upper_orange}")
        self.get_logger().info(f"AUV HSV Lower: {self.auv_color_lower_yellow}, Upper: {self.auv_color_upper_yellow}")
        self.get_logger().info(f"Initial Altitude: {self.initial_altitude} m")
        self.get_logger().info(f"Buoy Area at Initial Altitude: {self.buoy_area_percent_at_initial_altitude*100:.2f} %")
        self.get_logger().info(f"AUV Area at Initial Altitude: {self.auv_area_percent_at_initial_altitude*100:.2f} %")
        self.get_logger().info(f"Sensitivity Area Percent: {self.sensitivity_area_percent*100:.2f} %")
        self.get_logger().info(f"Least Area Pixels: {self.least_area_pixels} pixels")

        ################################################################################
        # Occasional Adjustments
        # Enable or disable specific detectors  
        self.buoy_detector = int(self.get_parameter('enable_buoy_detector').value)     # 0: off, 1: enabled
        self.auv_detector = int(self.get_parameter('enable_auv_detector').value)       # 0: off, 1: largest contour center, 2: best rectangle center    
        self.rope_detector = int(self.get_parameter('enable_rope_detector').value)     # 0: off, 1: enabled 
        self.rope_img_buffer = deque(maxlen=self.get_parameter('rope_img_buffer').value)#        5: Stores the last N frames to merge for more robust rope detection'
        self.rope_erosion_scale = int(self.get_parameter('rope_erosion_scale').value)  # 0: off,    higher values apply stronger erosion to the rope mask for noise reduction
        self.rope_dilation_scale = int(self.get_parameter('rope_dilation_scale').value)# 0: off,    higher values apply stronger dilation to the rope mask for connecting the rope  
        self.rope_hough_circle_min = int(self.get_parameter('rope_hough_circle_min').value) # Decide the expected radius of rope circle
        self.rope_hough_circle_max = int(self.get_parameter('rope_hough_circle_max').value)
        self.cnn_detector = int(self.get_parameter('enable_cnn_detector').value)       # 0: off, 1: enabled 
                                                                                       # cnn_detector requires buoy, auv, rope detectors are enabled
        self.dist_threshold_between_auv_and_buoy = int(self.get_parameter('dist_threshold_between_auv_and_buoy').value)  # CNN publisher threshold, determined by the distance between the AUV and the buoy
        ################################################################################
        # Rarely Changed
        # ROS2 publishers for detection topics
        self.buoy_pub = self.create_publisher(PointStamped, Topics.ESTIMATED_BUOY_TOPIC, 10)
        self.auv_pub = self.create_publisher(PointStamped, Topics.ESTIMATED_AUV_TOPIC, 10)
        self.middle_pub = self.create_publisher(PointStamped, Topics.ESTIMATED_MIDDLE_TOPIC, 10)

        # Before Catching, anchor point [P1x, P1y]
        # After Catching, uav flys vector [P2x, P2y]
        self.cnn_pub = self.create_publisher(PointStamped, Topics.ESTIMATED_CNN_HOOK_ANCHOR_TOPIC, 10)       # [P1x, P1y] 
        self.cnn_vec_pub = self.create_publisher(PointStamped, Topics.ESTIMATED_CNN_AFTER_CATCH_FLY_DIRECTION_TOPIC, 10)   # [P2x, P2y]


        # Subscriber
        self.subscription = self.create_subscription(
            Image,
            Topics.GIMBAL_CAMERA_RAW_TOPIC,
            self.image_callback,
            10
        )

        # Subscribe to quadrotor altitude
        self.altitude_sub = self.create_subscription(
            Float32,                     # or the actual type of the altitude topic
            SMARCTopics.ALTITUDE_TOPIC,
            self.altitude_callback,
            10
        )

        self.bridge = CvBridge()

        self.get_logger().info(f"DetectionNode initialized and subscribed to '{Topics.GIMBAL_CAMERA_RAW_TOPIC}'")


        ################################################################################
        # Detector enabled flag (controlled via service)
        self.detector_enabled = bool(self.get_parameter('enable_on_start').value)  # Start enabled or disabled based on parameter

        ################################################################################
        # Service to enable/disable the detector (use std_srvs/SetBool)
        # Service name also without leading slash so it will be namespaced properly.
        self.create_service(Trigger, Topics.ENABLE_ALARS_DETECTOR_SERVICE_TOPIC , self.handle_enable_detector)
        self.create_service(Trigger, Topics.DISABLE_ALARS_DETECTOR_SERVICE_TOPIC , self.handle_disable_detector)

        self.get_logger().info(f"DetectionNode initialized. Subscribed to '{Topics.GIMBAL_CAMERA_RAW_TOPIC}'. Service 'enable_detector' ready.")
        self.get_logger().info(f"DetectionNode initialized. Subscribed to '{Topics.GIMBAL_CAMERA_RAW_TOPIC}'. Service 'disable_detector' ready.")
        self.current_altitude = 0.0

        # The area values will be real-time adjusted according to UAV's alititude, so we do not need to change the values
        self.buoy_min_area = 20   # Minimum contour area for buoy detection     
                                  # Lower values = more sensitive (detects small objects)
                                  # Higher values = stricter (requires larger buoy size)  
        self.buoy_max_area = 800 
        self.auv_min_area = 200                     
        self.auv_max_area = 1500
        self.camera_height = 480
        self.camera_width = 640
        self.auv_area_no_bound = 0
        self.buoy_area_no_bound = 0
        ################################################################################ 
        # CNN Initialization

        self.model = AnchorPointCNN()
        # model_path = '/home/lifan/colcon_ws/src/smarc2/perception/alars/auv_detector/auv_detector/anchor_point_cnn_dynamic_roi_validate_20251007_163547.pth'
        model_path = str(self.get_parameter('model_path').value)

        # To Download the CNN-trained file, please follow the github readme (Handling Complex Rope Pattern Scenarios)
        # https://github.com/AlexWUrobot/smarc2/tree/humble/perception/alars/auv_detector
        # https://purdue0-my.sharepoint.com/:f:/g/personal/wu1714_purdue_edu/EipFkxfwAChCs9_pB7qYX7oBZJphrxCcef63-rTvEa2O2g?e=liMWBs
        
        try:
            # package_name = 'smarc2'  # <-- change this to your actual package name
            # package_share = get_package_share_directory(package_name)

            # # Relative path inside your package share directory
            # model_relative_path = os.path.join(
            #     'perception', 'alars', 'auv_detector', 'auv_detector',
            #     'anchor_point_cnn_dynamic_roi_validate_20251007_163547.pth'
            # )

            # model_path = os.path.join(package_share, model_relative_path)


            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found at: {model_path}")
            
            self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
            self.model.eval()
            self.get_logger().info(f"AnchorPointCNN model loaded successfully from {model_path}")

        except FileNotFoundError as e:
            self.get_logger().error(f"ERROR: {e}")
        except Exception as e:
            self.get_logger().error(f"Unexpected error while loading CNN model: {e}")
        
        self.model.eval()

        self.input_size = (224, 224)
        self.orig_size = (640, 480)
        self.transform = transforms.Compose([
            transforms.Resize(self.input_size),
            transforms.ToTensor()
        ])

    ################################################################################
    # Service callback: SetBool request.data True -> enable, False -> disable

    def handle_enable_detector(self, request, response):
        # Toggle the detector enabled flag
        self.detector_enabled = True
        response.success = True
        response.message = 'detector enabled' if self.detector_enabled else 'detector disabled'
        self.get_logger().info(f"Service called: detector_enabled = {self.detector_enabled}")
        return response

    def handle_disable_detector(self, request, response):
        # Toggle the detector enabled flag
        self.detector_enabled = False
        response.success = True
        response.message = 'detector enabled' if self.detector_enabled else 'detector disabled'
        self.get_logger().info(f"Service called: detector_enabled = {self.detector_enabled}")
        return response


    def altitude_callback(self, msg: Float32):
        self.current_altitude = msg.data  + 6.0  # rosbag2_2025_10_10-13_28_21_22.db3
        # Scale minimum detection areas with altitude

        total_pixel = self.camera_height*self.camera_width

        buoy_area_percent = self.buoy_area_percent_at_initial_altitude * (self.initial_altitude/self.current_altitude )**2
        self.buoy_min_area = (buoy_area_percent - self.sensitivity_area_percent) * total_pixel
        self.buoy_max_area = (buoy_area_percent + self.sensitivity_area_percent) * total_pixel

        auv_area_percent = self.auv_area_percent_at_initial_altitude * (self.initial_altitude/self.current_altitude )**2
        self.auv_min_area = (auv_area_percent - self.sensitivity_area_percent) * total_pixel
        self.auv_max_area = (auv_area_percent + self.sensitivity_area_percent) * total_pixel


        # The lower bound of the detection is usually set to 10 to remove environmental noise. 
        if self.buoy_min_area < self.least_area_pixels:
            self.buoy_min_area = self.least_area_pixels
        if self.auv_min_area < self.least_area_pixels:
            self.auv_min_area = self.least_area_pixels


        # # Default to the last area values
        # self.buoy_min_area = self.buoy_min_area_by_height[-1]
        # self.buoy_max_area = self.buoy_max_area_by_height[-1]
        # self.auv_min_area = self.auv_min_area_by_height[-1]
        # self.auv_max_area = self.auv_max_area_by_height[-1]

        # # Loop through heights
        # for i, height in enumerate(self.auv_height):
        #     if self.current_altitude < height:
        #         self.buoy_min_area = self.buoy_min_area_by_height[i]
        #         self.buoy_max_area = self.buoy_max_area_by_height[i]
        #         self.auv_min_area = self.auv_min_area_by_height[i]
        #         self.auv_max_area = self.auv_max_area_by_height[i]
        #         break

    def image_callback(self, msg: Image):

        center_buoy = None  # Ensure center_buoy is always defined

        if self.cnn_detector > 0:
            HoughCircle_x, HoughCircle_y, HoughCircle_r = None, None, None

        if not self.detector_enabled:
            # Detector disabled — do minimal processing / return quickly.
            # Could still forward camera frames or publish heartbeat if desired.
            return

        # Refresh HSV thresholds live of Buoy
        self.buoy_color_lower_orange = np.array(
            self.get_parameter('buoy_color_lower_orange').value, dtype=np.uint8
        )
        self.buoy_color_upper_orange = np.array(
            self.get_parameter('buoy_color_upper_orange').value, dtype=np.uint8
        )
                                                   

        # Refresh HSV thresholds live of AUV
        self.auv_color_lower_yellow = np.array(
            self.get_parameter('auv_color_lower_yellow').value, dtype=np.uint8
        )
        self.auv_color_upper_yellow = np.array(
            self.get_parameter('auv_color_upper_yellow').value, dtype=np.uint8
        )

        # self.get_logger().info("Received an image!")
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        cv_image_noted = cv_image.copy()

        # Get image size
        self.camera_height, self.camera_width = cv_image.shape[:2]
        total_pixels = self.camera_height*self.camera_width

        # Uncomment the code, If you need saturation changes
        # sat_factor = 1
        imghsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV).astype("float32")
        # (h, s, v) = cv2.split(imghsv)
        # s = s*sat_factor
        # s = np.clip(s,0,255)
        # imghsv = cv2.merge([h,s,v])
        # imgrgb = cv2.cvtColor(imghsv.astype("uint8"), cv2.COLOR_HSV2BGR)
        # cv_image = imgrgb

        #########################################################################################  buoy

        if self.buoy_detector  == 1:

            hsv_thresh_buoy = cv2.inRange(imghsv, self.buoy_color_lower_orange , self.buoy_color_upper_orange)
            preview_buoy = cv2.bitwise_and(cv_image, cv_image, mask=hsv_thresh_buoy)
            #cv2.imshow('HSV_buoy', preview_buoy)

            if self.cnn_detector > 0:
                preview_buoy_initial = preview_buoy.copy()

            # Find contours
            contours, _ = cv2.findContours(hsv_thresh_buoy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Find largest contour
            max_area = 0
            self.buoy_area_no_bound = 0
            max_contour = None
            center_buoy = None

            for cnt in contours:
                area = cv2.contourArea(cnt)
                # if area < self.buoy_min_area:
                #     continue
                # # Skip contours that are too large
                # if area > self.buoy_max_area:
                #     continue
                
                if area > max_area:
                    max_area = area
                    max_contour = cnt

            # Draw largest contour and show area
            if max_contour is not None:
                # Draw the contour
                # cv2.drawContours(preview_buoy, [max_contour], -1, (0, 255, 0), 1)
                self.buoy_area_no_bound = int(max_area)
                if self.debug_imshow >= 2:
                    cv2.drawContours(preview_buoy, [max_contour], -1, (0, 255, 0), 1)  
                    cv2.putText(
                        preview_buoy,
                        f"Buoy Max Area: {self.buoy_area_no_bound}",
                        (10, 100),     # top-left corner
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,          # font scale
                        (255, 255, 255),  # color (green)
                        1             # thickness
                    )               
                # Use only the largest contour region from the RGB image as input to the CNN
                if self.cnn_detector > 0:
                    mask = np.zeros_like(hsv_thresh_buoy)
                    # Apply mask to RGB image — keep only max contour region
                    cv2.drawContours(mask, [max_contour], -1, 255, thickness=cv2.FILLED)
                    preview_buoy_initial = cv2.bitwise_and(cv_image, cv_image, mask=mask)
                    #cv2.imshow('Test largest buoy region', preview_buoy_initial)


                if self.buoy_min_area <= max_area <= self.buoy_max_area:
                    # Get center
                    M = cv2.moments(max_contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        center_buoy = (cx, cy)
                        # Normalize coordinates between -1 and 1, with 0 at the image center
                        img_h, img_w = cv_image.shape[:2]
                        norm_cx = 2 * (cx / img_w) - 1
                        norm_cy = 2 * (cy / img_h) - 1

                        buoy_position_msg = PointStamped()
                        buoy_position_msg.header.frame_id = self._CAMERA_PIXELS_FRAME
                        buoy_position_msg.header.stamp = self.get_clock().now().to_msg()
                        buoy_position_msg.point.x = float(norm_cx)
                        buoy_position_msg.point.y = float(norm_cy)
                        self.buoy_pub.publish(buoy_position_msg)
                        #self.get_logger().info(f"detect buoy")

                        # --- calculate percentage of image covered by the contour ---
                        buoy_area = max_area / total_pixels  # value between 0 and 1

                        cv2.circle(preview_buoy, (cx, cy), 10, (0, 0, 255), 1)
                        # Put area text
                        cv2.putText(preview_buoy, f"Area: {int(max_area)} ({buoy_area:.3%})", (cx + 10, cy - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                        # cv2.drawContours(preview_buoy, [max_contour], -1, (0, 255, 0), 1)                    

                        cv2.circle(cv_image_noted, (cx, cy), 10, (0, 0, 255), 1)

                        # Put area text
                        cv2.putText(cv_image_noted, f"Area: {int(max_area)} ({buoy_area:.3%})", (cx + 10, cy - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            if self.debug_imshow >= 2:
                cv2.imshow('HSV_buoy', preview_buoy)
        
        #########################################################################################  auv

        if self.auv_detector > 0: 
            # HSV filter for sam auv
            hsv_thresh_auv = cv2.inRange(imghsv, self.auv_color_lower_yellow, self.auv_color_upper_yellow)
            preview_auv = cv2.bitwise_and(cv_image, cv_image, mask=hsv_thresh_auv)
            #cv2.imshow('HSV_auv', preview_auv)
            
            if self.cnn_detector > 0:
                preview_auv_initial = preview_auv.copy()

            # Find contours
            contours, _ = cv2.findContours(hsv_thresh_auv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            center_auv = None
            if self.rope_detector > 0:
                auv_image_with_correct_size = None
            
            if self.auv_detector == 1:
                # Find largest contour
                max_area = 0
                max_contour = None
                

                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    # if area < self.auv_min_area:
                    #     continue
                    # # Skip contours that are too large
                    # if area > self.auv_max_area:
                    #     continue

                    if area > max_area:
                        max_area = area
                        max_contour = cnt

                # Draw largest contour and show area
                if max_contour is not None:
                    # Draw the contour
                    # cv2.drawContours(preview_auv, [max_contour], -1, (0, 255, 0), 1)
                    self.auv_area_no_bound = int(max_area)
                    if self.debug_imshow >= 2:
                        cv2.drawContours(preview_auv, [max_contour], -1, (0, 255, 0), 1)  
                        cv2.putText(
                            preview_auv,
                            f"AUV Max Area: {int(self.auv_area_no_bound)}",
                            (10, 120),     # top-left corner
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,          # font scale
                            (255, 255, 255),  # color (green)
                            1             # thickness
                        )     

                    # Use only the largest contour region from the RGB image as input to the CNN
                    if self.cnn_detector > 0:
                        mask = np.zeros_like(hsv_thresh_auv)
                        # Apply mask to RGB image — keep only max contour region
                        cv2.drawContours(mask, [max_contour], -1, 255, thickness=cv2.FILLED)
                        preview_auv_initial = cv2.bitwise_and(cv_image, cv_image, mask=mask)
                        #cv2.imshow('Test largest auv region', preview_auv_initial)

                    if self.auv_min_area <= max_area <= self.auv_max_area:

                        if self.rope_detector > 0:
                            auv_image_with_correct_size = preview_auv_initial.copy()

                        # Now, pick the edge center closer to buoy
                        if center_buoy is None:
                            # No buoy, just use contour centroid
                            M = cv2.moments(max_contour)
                            if M["m00"] != 0:
                                cx = int(M["m10"] / M["m00"])
                                cy = int(M["m01"] / M["m00"])
                            else:
                                return  # Avoid division by zero
                        else:
                            # Buoy detected, recovery needs to know the
                            # AUV tip position not its center, so fit
                            # a rectangle on the contour and pick
                            # the short edge closer to the buoy
                            # This assumes the AUV is longer than it is wide
                            # This assumes the buoy is not inside the AUV contour
                            # This assumes the rope is relatively straight and doesnt curve
                            # behind the back of the auv... and so on
                            # Need a better detection method for the complicated cases

                            # Fit a rotated rectangle to the contour
                            rect = cv2.minAreaRect(max_contour)
                            box = cv2.boxPoints(rect)
                            box = np.int0(box)
                            # Get the four corners
                            corners = box
                            # Find the two short edges (pairs of corners)
                            dists = [np.linalg.norm(corners[i] - corners[(i+1)%4]) for i in range(4)]
                            # Indices of the two short edges
                            short_edges = sorted(range(4), key=lambda i: dists[i])[:2]
                            # Each short edge is (corners[i], corners[(i+1)%4])
                            edge_centers = []
                            for i in short_edges:
                                pt1 = corners[i]
                                pt2 = corners[(i+1)%4]
                                center = (pt1 + pt2) / 2.0
                                edge_centers.append(center)
                            buoy_point = np.array(center_buoy)
                            distances = [np.linalg.norm(center - buoy_point) for center in edge_centers]
                            min_idx = np.argmin(distances)
                            cx, cy = edge_centers[min_idx]
                            cx = int(cx)
                            cy = int(cy)
                            

                        # Normalize coordinates between -1 and 1, with 0 at the image center
                        img_h, img_w = cv_image.shape[:2]
                        norm_cx = 2 * (cx / img_w) - 1
                        norm_cy = 2 * (cy / img_h) - 1
                        auv_position_msg = PointStamped()
                        auv_position_msg.header.frame_id = self._CAMERA_PIXELS_FRAME
                        auv_position_msg.header.stamp = self.get_clock().now().to_msg()
                        auv_position_msg.point.x = float(norm_cx)
                        auv_position_msg.point.y = float(norm_cy)
                        self.auv_pub.publish(auv_position_msg)

                        # --- calculate percentage of image covered by the contour ---
                        auv_area = max_area / total_pixels  # value between 0 and 1

                        #center_auv = (cx,cy)
                        center_auv = np.array([cx, cy])
                        cv2.circle(preview_auv, (cx, cy), 10, (0, 0, 255), 1)

                        cv2.circle(cv_image_noted, (cx, cy), 10, (0, 0, 255), 1)


                        # Put area text
                        cv2.putText(preview_auv, f"AUV Area: {int(max_area)} ({auv_area:.3%})", (cx + 10, cy - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                        #cv2.drawContours(preview_auv, [max_contour], -1, (0, 255, 0), 1) 

                        cv2.putText(cv_image_noted, f"AUV Area: {int(max_area)} ({auv_area:.3%})", (cx + 10, cy - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                if self.debug_imshow >= 2:
                    cv2.imshow('HSV_auv', preview_auv)

            if self.auv_detector == 2:
                # Missle-Shape detector Parameters
                min_aspect_ratio = 2.5  # Tune this: 2.5 means at least 2.5x longer than wide
                best_contour = None
                best_ratio = 0

                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    if area < self.auv_min_area:
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
                    

                    # Get center from rect
                    center = tuple(map(int, rect[0]))
                    # Normalize coordinates between -1 and 1, with 0 at the image center
                    img_h, img_w = cv_image.shape[:2]
                    norm_cx = 2 * (center[0] / img_w) - 1
                    norm_cy = 2 * (center[1] / img_h) - 1
                    auv_position_msg = PointStamped()
                    auv_position_msg.header.frame_id = self._CAMERA_PIXELS_FRAME
                    auv_position_msg.header.stamp = self.get_clock().now().to_msg()
                    auv_position_msg.point.x = float(norm_cx)
                    auv_position_msg.point.y = float(norm_cy)
                    self.auv_pub.publish(auv_position_msg)

                    center_auv = np.array([center[0], center[1]]) # update for middle point
        
                    if self.debug_imshow >= 2:
                        cv2.circle(preview_auv, center, 3, (0, 0, 255), -1)
                        cv2.drawContours(preview_auv, [box], 0, (0, 255, 0), 1)
                        cv2.putText(preview_auv, f"AUV W/H: {best_ratio:.2f}", (center[0] + 10, center[1] - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

                    cv2.circle(cv_image_noted, center, 3, (0, 0, 255), -1)
                    cv2.drawContours(cv_image_noted, [box], 0, (0, 255, 0), 1)
                    cv2.putText(cv_image_noted, f"AUV W/H: {best_ratio:.2f}", (center[0] + 10, center[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)


                if self.debug_imshow >= 2:
                    cv2.imshow('HSV_auv_Missle_Shape Detect', preview_auv)
        #########################################################################################  rope
        if self.auv_detector > 0: 
            # HSV filter for sam auv
            hsv_thresh_rope = cv2.inRange(imghsv, self.rope_color_lower, self.rope_color_upper)
            preview_rope = cv2.bitwise_and(cv_image, cv_image, mask=hsv_thresh_rope)
            #cv2.imshow('preview_rope', preview_rope)
            preview_rope_multi = preview_rope.copy()

            # Only Procee Rope for For CNN
            self.rope_img_buffer.append(preview_rope_multi)
            for img_tmp in self.rope_img_buffer:
                preview_rope_multi = cv2.add(preview_rope_multi, img_tmp)
            #cv2.imshow("N frames rope detect", preview_rope_multi)

            # Only Procee Rope for HoughCircle Not for CNN
            rope_multi_H = preview_rope_multi.copy()
            # Process Rope for HoughCircle and CNN
            # rope_multi_H = preview_rope_multi

            if self.rope_erosion_scale > 0:
                # Apply erosion to remove noise
                kernel_size = self.rope_erosion_scale
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
                rope_multi_H = cv2.erode(rope_multi_H, kernel, iterations=1)
                if self.debug_imshow >= 2:
                    cv2.imshow("Erosion", rope_multi_H)

            if self.rope_dilation_scale > 0:
                # Apply dilation to connect fragmented rope segments
                kernel_size = self.rope_dilation_scale
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))  #  3 is small dilated, 8 is large dilated
                rope_multi_H = cv2.dilate(rope_multi_H, kernel, iterations=1)
                if self.debug_imshow >= 2:
                    cv2.imshow("Dilation", rope_multi_H)
                # # Use this dilated result for binary mask and grid processing
                # rope_bin = cv2.cvtColor(rope_dilated, cv2.COLOR_BGR2GRAY)
                # _, rope_bin = cv2.threshold(rope_bin, 1, 255, cv2.THRESH_BINARY)
                # if self.debug_imshow >= 2:
                #     cv2.imshow("Dilation", rope_bin)

            #rope_annotated = preview_rope_multi.copy()
            # Hough Circle consider AUV, so combine rope and AUV
            if auv_image_with_correct_size is not None:  # find correct AUV size, use both rope and AUV to draw HoughCircle
                rope_and_auv_annotated =  cv2.add(rope_multi_H, preview_auv_initial)
                rope_multi_H = rope_and_auv_annotated.copy()
            else: # cannot find correct AUV, just use rope to draw HoughCircle
                rope_and_auv_annotated = rope_multi_H.copy()

            # Use this dilated result for binary mask and grid processing
            rope_bin = cv2.cvtColor(rope_multi_H, cv2.COLOR_BGR2GRAY)
            _, rope_bin = cv2.threshold(rope_bin, 1, 255, cv2.THRESH_BINARY)
            if self.debug_imshow >= 2:
                cv2.imshow("Rope with Erosion Dilation and Binary mask", rope_bin)

            # Detect Hough circles
            # circles = cv2.HoughCircles(rope_bin, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
            #                         param1=70, param2=25, minRadius=10, maxRadius=100)
            circles = cv2.HoughCircles(rope_bin, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                                    param1=70, param2=25, minRadius=self.rope_hough_circle_min, maxRadius=self.rope_hough_circle_max)
    
            if circles is not None:
                circles = np.uint16(np.around(circles[0]))  # Flatten to shape (N, 3)

                # Find the biggest circle (with max radius)
                biggest_circle = max(circles, key=lambda c: c[2])  # c = (cx, cy, radius)
                cx, cy, r = biggest_circle

                # Optional: Draw the biggest circle for visualization
                cv2.circle(rope_and_auv_annotated, (cx, cy), r, (0, 255, 0), 2)   # Draw the circle
                cv2.circle(rope_and_auv_annotated, (cx, cy), 2, (0, 0, 255), 3)   # Draw the center

                if self.cnn_detector > 0:
                    HoughCircle_x, HoughCircle_y, HoughCircle_r = biggest_circle

            if self.debug_imshow >= 2:
                cv2.imshow("Rope and AUV with Hough Circle", rope_and_auv_annotated)

        ######################################################################################### CNN 

        if self.cnn_detector > 0:
            # --- Procee CNN input data --- (Consider AUV, Buoy largest contour,  Still need to consider Rope's largest contour and overexposure)
            preview_buoy_auv = cv2.add(preview_buoy_initial, preview_auv_initial)   # no text 
            #buoy_auv_rope_preview = cv2.add(preview_buoy_auv, preview_rope_multi)
            
            
            # Create a mask where buoy_auv image has non-black pixels
            mask = cv2.cvtColor(preview_buoy_auv, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)
            # Invert mask for background
            mask_inv = cv2.bitwise_not(mask)
            # Keep rope where buoy_auv is black
            background = cv2.bitwise_and(preview_rope_multi, preview_rope_multi, mask=mask_inv)
            # Keep buoy_auv where it has content
            foreground = cv2.bitwise_and(preview_buoy_auv, preview_buoy_auv, mask=mask)
            # Combine both — buoy_auv on top
            buoy_auv_rope_preview = cv2.add(background, foreground)
            if self.debug_imshow >=2:
                cv2.imshow('The input image of CNN: Buoy, AUV and Rope', buoy_auv_rope_preview)
            # --- ---------------------------------- ---



            original_image = cv_image.copy()

            # --- Convert to numpy for ROI detection ---
            np_img = buoy_auv_rope_preview.copy()
            gray = np_img.mean(axis=2)  # average intensity
            mask = gray > 30  # brightness threshold

            if not mask.any():
                # fallback to full image if object not found
                left, top, right, bottom = 0, 0, np_img.shape[1], np_img.shape[0]
            else:
                ys, xs = np.where(mask)
                top, bottom = ys.min(), ys.max()
                left, right = xs.min(), xs.max()
                pad = 10  # optional padding
                left = max(0, left - pad)
                top = max(0, top - pad)
                right = min(np_img.shape[1], right + pad)
                bottom = min(np_img.shape[0], bottom + pad)

            if self.debug_imshow >=2:
                # --- Draw ROI box ---
                roi_preview = np_img.copy()
                cv2.rectangle(
                    roi_preview,
                    (left, top), (right, bottom),
                    (0, 255, 0), 2  # Green box, thickness=2
                )

                # --- Show the ROI visualization ---
                cv2.imshow('ROI Visualization', roi_preview)


            # --- Crop the image to ROI ---
            roi_img = np_img[top:bottom, left:right, :]

            # --- Save top-left pixel coordinates ---
            x0, y0 = left, top

            # Preprocess for CNN
            #pil_image = PILImage.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
            #pil_image = PILImage.fromarray(cv2.cvtColor(combined_preview, cv2.COLOR_BGR2RGB))
            # --- Prepare ROI image for CNN ---
            #cv2.imshow("roi_img", roi_img)
            pil_image = PILImage.fromarray(cv2.cvtColor(roi_img, cv2.COLOR_BGR2RGB))
            input_tensor = self.transform(pil_image).unsqueeze(0)

            # Inference
            with torch.no_grad():
                output = self.model(input_tensor).squeeze().numpy()

            # --- Rescale prediction to ROI size ---
            roi_width, roi_height = right - left, bottom - top


            # --- Rescale prediction to ROI size ---
            x1_norm, y1_norm, x2_norm, y2_norm = output  # normalized [0,1]

            x1 = int(x1_norm * roi_width)
            y1 = int(y1_norm * roi_height)
            x2 = int(x2_norm * roi_width)
            y2 = int(y2_norm * roi_height)

            # --- Add top-left pixel offset to restore to original image ---
            x1 += x0
            y1 += y0
            x2 += x0
            y2 += y0

            # Clamp to original image
            x1 = int(np.clip(x1, 0, cv_image.shape[1]-1))
            y1 = int(np.clip(y1, 0, cv_image.shape[0]-1))
            x2 = int(np.clip(x2, 0, cv_image.shape[1]-1))
            y2 = int(np.clip(y2, 0, cv_image.shape[0]-1))

            # Draw predicted points
            cv2.circle(original_image, (x1, y1), 6, (0, 255, 0), -1)  # P1: Green
            cv2.circle(original_image, (x2, y2), 6, (0, 0, 255), -1)  # P2: Red
            cv2.putText(original_image, f"P1", (x1+5, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(original_image, f"P2", (x2+5, y2-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            # Show image with overlay
            if self.debug_imshow >= 2:
                cv2.imshow("Anchor Points Prediction", original_image)
            #cv2.waitKey(1)


            # CNN Publisher Threshold Logic:
            # Threshold 1: Both buoy and AUV must be detected.
            # Threshold 2: Distance between the AUV and buoy must be within a predefined limit. This ensures that the rope is not too complex.
            # Threshold 3: A Hough Circle must exist, meaning the curve of the rope has been detected.
            # Threshold 4: The CNN prediction must lie within the Hough Circle radius, ensuring a reasonable prediction.

            # Threshold 1: Check that both AUV and buoy centers are detected
            if center_auv is not None and center_buoy is not None:
                distance_between_auv_and_buoy = np.linalg.norm(center_buoy - center_auv) # Compute Euclidean distance (in pixels)

                # Threshold 2: Verify distance between AUV and buoy
                if distance_between_auv_and_buoy <= self.dist_threshold_between_auv_and_buoy:

                    # Threshold 4: Ensure CNN prediction is within Hough Circle radius
                    if HoughCircle_r is not None: 
                        center_HoughCircle  = np.array([HoughCircle_x,HoughCircle_y])
                        cnn_P1 = np.array([x1,y1])
                        distance_between_P1_and_HoughCircle = np.linalg.norm(cnn_P1 - center_HoughCircle)
                        
                        # CNN publisher threshold 4
                        if distance_between_P1_and_HoughCircle <= HoughCircle_r:

                            # Publish center_HoughCircle as P1 and CNN prediction as P2
                            # Draw the radius and center_HoughCircle and P2 vector
                            # cv2.circle(cv_image_noted, (HoughCircle_x, HoughCircle_y), HoughCircle_r, (0, 255, 255), 1)   # Draw the circle
                            cv2.circle(cv_image_noted, (HoughCircle_x, HoughCircle_y), 2, (0, 255, 255), 2)     # Draw the center        

                            # Compute and draw directional vector from Hough Circle center to P2
                            direction_vector = np.array([x2 - HoughCircle_x, y2 - HoughCircle_y])
                            norm = np.linalg.norm(direction_vector)
                            # Prevent divide-by-zero and scale vector
                            if norm > 1e-5:
                                direction_vector = direction_vector / norm 
                            else:
                                direction_vector = np.array([0, 0], dtype=np.float32)
                            #direction_vector = direction_vector / np.linalg.norm(direction_vector) 
                            arrow_tip = np.array([HoughCircle_x, HoughCircle_y]) + direction_vector* 20  # scale to 20 pixels
                            cv2.arrowedLine(
                                cv_image_noted,
                                (int(HoughCircle_x), int(HoughCircle_y)),
                                (int(arrow_tip[0]), int(arrow_tip[1])),
                                (0, 255, 255), 2, tipLength=0.3
                            )
                            cv2.putText(cv_image_noted, f"CNN", (HoughCircle_x + 10, HoughCircle_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255), 1)


                            # Normalize coordinates between -1 and 1, with 0 at the image center
                            img_h, img_w = cv_image.shape[:2]
                            norm_cx = 2 * (HoughCircle_x / img_w) - 1
                            norm_cy = 2 * (HoughCircle_y / img_h) - 1
                            cnn_position_msg = PointStamped()
                            cnn_position_msg.header.frame_id = self._CAMERA_PIXELS_FRAME
                            cnn_position_msg.header.stamp = self.get_clock().now().to_msg()
                            cnn_position_msg.point.x = float(norm_cx)
                            cnn_position_msg.point.y = float(norm_cy)
                            self.cnn_pub.publish(cnn_position_msg)


                            cnn_vec_msg = PointStamped()
                            cnn_vec_msg.header.frame_id = self._CAMERA_PIXELS_FRAME
                            cnn_vec_msg.header.stamp = self.get_clock().now().to_msg()
                            cnn_vec_msg.point.x = float(direction_vector[0])
                            cnn_vec_msg.point.y = float(direction_vector[1])
                            self.cnn_vec_pub.publish(cnn_vec_msg)

            else:
                distance_between_auv_and_buoy = None

        #########################################################################################

        # Just add the filtered images directly
        combined_preview = cv2.add(preview_buoy, preview_auv)   # with text and circle

        #########################################################################################
        if center_auv is not None and center_buoy is not None:
            center_between_auv_and_buoy = (center_auv + center_buoy) / 2

            img_h, img_w = cv_image.shape[:2]
            norm_cx = 2 * (center_between_auv_and_buoy[0] / img_w) - 1
            norm_cy = 2 * (center_between_auv_and_buoy[1] / img_h) - 1
            middle_position_msg = PointStamped()
            middle_position_msg.header.frame_id = self._CAMERA_PIXELS_FRAME
            middle_position_msg.header.stamp = self.get_clock().now().to_msg()
            middle_position_msg.point.x = float(norm_cx)
            middle_position_msg.point.y = float(norm_cy)
            self.middle_pub.publish(middle_position_msg)

            cx = int(center_between_auv_and_buoy[0])  
            cy = int(center_between_auv_and_buoy[1])  
            cv2.circle(cv_image_noted, (cx, cy), 5, (0, 0, 255), -1) 
            cv2.putText(cv_image_noted, f"Middle Point", (cx + 10, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)


        # Show the combined result
        if self.debug_imshow >=2:
            cv2.imshow('Combined_HSV', combined_preview)
        if self.debug_imshow >=1:
            if hasattr(self, 'current_altitude'):
                cv2.putText(
                    cv_image_noted,
                    f"Altitude: {self.current_altitude:.2f} m",
                    (10, 30),     # top-left corner
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,          # font scale
                    (0, 255, 0),  # color (green)
                    2             # thickness
                )


            if hasattr(self, 'buoy_min_area'):
                cv2.putText(
                    cv_image_noted,
                    f"Buoy Threshold: {int(self.buoy_min_area)}~{int(self.buoy_max_area)}",
                    (10, 60),     # top-left corner
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,          # font scale
                    (255, 255, 255),  # color (white)
                    1             # thickness
                )


            if hasattr(self, 'auv_min_area'):
                cv2.putText(
                    cv_image_noted,
                    f"AUV Threshold: {int(self.auv_min_area)}~{int(self.auv_max_area)}",
                    (10, 80),     # top-left corner
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,          # font scale
                    (255, 255, 255),  # color (white)
                    1             # thickness
                )


            if hasattr(self, 'buoy_area_no_bound'):
                cv2.putText(
                    cv_image_noted,
                    f"Buoy Max Area: {self.buoy_area_no_bound}",
                    (10, 100),     # top-left corner
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,          # font scale
                    (255, 255, 255),  # color (white)
                    1             # thickness
                )


            if hasattr(self, 'auv_area_no_bound'):
                cv2.putText(
                    cv_image_noted,
                    f"AUV Max Area: {self.auv_area_no_bound}",
                    (10, 120),     # top-left corner
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,          # font scale
                    (255, 255, 255),  # color (white)
                    1             # thickness
                )

            if self.cnn_detector > 0:

                cv2.putText(
                    cv_image_noted,
                    f"Buoy-AUV Distance Threshold: {self.dist_threshold_between_auv_and_buoy}",
                    (10, 430),     # top-left corner
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,          # font scale
                    (0, 255, 255),  # color (yellow)
                    1             # thickness
                )

                distance_text = f"Buoy-AUV Distance: {distance_between_auv_and_buoy:.2f}" if distance_between_auv_and_buoy is not None else "Buoy-AUV Distance: None"
                cv2.putText(
                    cv_image_noted,
                    distance_text,
                    (10, 450),  # top-left corner, adjust as needed
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,        # font scale
                    (0, 255, 255),  # color (yellow)
                    1           # thickness
                )

                cv2.imshow("CNN Detecting AUV and Buoy and Rope", cv_image_noted)
            else:
                cv2.imshow("Detecting AUV and Buoy", cv_image_noted)

        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = DetectionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()