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

class DetectionNode(Node):
    def __init__(self):
        super().__init__('detection_node')

        self.declare_parameter('debug_imshow', 2)
        self.declare_parameter('enable_buoy_detector', 1)
        self.declare_parameter('enable_auv_detector', 1)
        self.declare_parameter('enable_rope_detector', 0)
        self.declare_parameter('enable_on_start', 1)

        self.declare_parameter('buoy_color_lower_orange', [8, 121, 35])
        self.declare_parameter('buoy_color_upper_orange', [40, 157, 247])

        self.declare_parameter('auv_color_lower_yellow', [25, 0, 169])
        self.declare_parameter('auv_color_upper_yellow', [46, 103, 221])

        # default values from field test rosbag
        self.declare_parameter('calibration_altitude', 8.7)
        self.declare_parameter('buoy_area_percent_at_calibration_altitude', 0.007)
        self.declare_parameter('auv_area_percent_at_calibration_altitude', 0.149)
        self.declare_parameter('sensitivity_area_percent', 0.10)
        self.declare_parameter('least_area_pixels', 10)

        self._CAMERA_PIXELS_FRAME = "camera_pixels_normalized"  # Frame for publishing detected points

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

        
        # Minimum and maximum area thresholds at 8 meters, so you can intuitively estimate
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

        # Here, I set the area thresholds based on AUV height. 
        # If the AUV height is less than 10 meters, buoy_min_area_by_height[0] is used. 
        # If it is greater than 10 meters, buoy_min_area_by_height[1] is used. 
        # Using the same logic, you can extend the thresholds to [10, 25, ...] 
        # and define corresponding areas as self.buoy_min_area_by_height = [20, 10, 1, ...]

        # self.auv_height = [10, 25]  # meters  
        # self.buoy_min_area_by_height = [20, 10, 1]
        # self.buoy_max_area_by_height = [800, 180, 150]

        # self.auv_min_area_by_height = [180, 10, 1]
        # self.auv_max_area_by_height = [1500, 800, 700]


        ################################################################################
        # Occasional Adjustments
        # Enable or disable specific detectors  
        self.buoy_detector = int(self.get_parameter('enable_buoy_detector').value)     # 0: off, 1: enabled
        self.auv_detector = int(self.get_parameter('enable_auv_detector').value)       # 0: off, 1: largest contour center, 2: best rectangle center    
        self.rope_detector = int(self.get_parameter('enable_rope_detector').value)     # 0: off, 1: spline line, 2: multi-frame, 3: both


        ################################################################################
        # Rarely Changed
        # ROS2 publishers for detection topics
        self.buoy_pub = self.create_publisher(PointStamped, Topics.ESTIMATED_BUOY_TOPIC, 10)
        self.auv_pub = self.create_publisher(PointStamped, Topics.ESTIMATED_AUV_TOPIC, 10)
        self.middle_pub = self.create_publisher(PointStamped, Topics.ESTIMATED_MIDDLE_TOPIC, 10)

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
        self.current_altitude = msg.data
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
            
            # Find contours
            contours, _ = cv2.findContours(hsv_thresh_auv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            center_auv = None
            
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

                    if self.auv_min_area <= max_area <= self.auv_max_area:
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

        #########################################################################################

        # Just add the filtered images directly
        combined_preview = cv2.add(preview_buoy, preview_auv)

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