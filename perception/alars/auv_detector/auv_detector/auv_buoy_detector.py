import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float32MultiArray
from cv_bridge import CvBridge
import cv2
import numpy as np
from dji_msgs.msg import Topics
from std_srvs.srv import Trigger


class DetectionNode(Node):
    def __init__(self):
        super().__init__('detection_node')

        ################################################################################
        # Frequent Adjustments
        # Note: On Jetson, set to 0 to maintain a publish rate of ~30 Hz
        self.debug_imshow = 1     # 0: disable display, 1: show one frame, 2: show all frames  

        # Color Mask Thresholds
        # Buoy detection (orange range)
        self.buoy_color_lower_orange = np.array([8, 121, 35]) 
        self.buoy_color_upper_orange = np.array([40, 157, 247])
        self.buoy_min_area = 20   
                                                   
        # AUV detection (yellow range)
        self.auv_color_lower_yellow = np.array([25, 0, 169]) 
        self.auv_color_upper_yellow = np.array([46, 103, 221])
        self.auv_min_area = 200   # Minimum contour area for buoy detection 
                                  # Lower values = more sensitive (detects small objects)
                                  # Higher values = stricter (requires larger buoy size)   
        


        ################################################################################
        # Occasional Adjustments
        # Enable or disable specific detectors  
        self.buoy_detector = 1     # 0: off, 1: enabled
        self.auv_detector = 1      # 0: off, 1: largest contour center, 2: best rectangle center    
        self.rope_detector = 0     # 0: off, 1: spline line, 2: multi-frame, 3: both    


        ################################################################################
        # Rarely Changed
        # ROS2 publishers for detection topics
        self.buoy_pub = self.create_publisher(Float32MultiArray, Topics.ESTIMATED_BUOY_TOPIC, 10)
        self.auv_pub = self.create_publisher(Float32MultiArray, Topics.ESTIMATED_AUV_TOPIC, 10)
        self.middle_pub = self.create_publisher(Float32MultiArray, Topics.ESTIMATED_MIDDLE_TOPIC, 10)

        # Subscriber
        self.subscription = self.create_subscription(
            Image,
            Topics.CAMERA_TOPIC,
            self.image_callback,
            10
        )
        self.bridge = CvBridge()

        self.get_logger().info(f"DetectionNode initialized and subscribed to '{Topics.CAMERA_TOPIC}'")


        ################################################################################
        # Detector enabled flag (controlled via service)
        self.detector_enabled = True

        ################################################################################
        # Service to enable/disable the detector (use std_srvs/SetBool)
        # Service name also without leading slash so it will be namespaced properly.
        self.create_service(Trigger, 'alars_detector', self.handle_enable_detector)


        self.get_logger().info(f"DetectionNode initialized. Subscribed to '{Topics.CAMERA_TOPIC}'. Service 'enable_detector' ready.")

    
    
    ################################################################################
    # Service callback: SetBool request.data True -> enable, False -> disable

    def handle_enable_detector(self, request, response):
        # Toggle the detector enabled flag
        self.detector_enabled = not self.detector_enabled
        response.success = True
        response.message = 'detector enabled' if self.detector_enabled else 'detector disabled'
        self.get_logger().info(f"Service called: detector_enabled = {self.detector_enabled}")
        return response



    def image_callback(self, msg: Image):

        if not self.detector_enabled:
            # Detector disabled — do minimal processing / return quickly.
            # Could still forward camera frames or publish heartbeat if desired.
            return

        # self.get_logger().info("Received an image!")
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        cv_image_noted = cv_image.copy()


        sat_factor = 1
        imghsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV).astype("float32")
        (h, s, v) = cv2.split(imghsv)
        s = s*sat_factor
        s = np.clip(s,0,255)
        imghsv = cv2.merge([h,s,v])
        imgrgb = cv2.cvtColor(imghsv.astype("uint8"), cv2.COLOR_HSV2BGR)
        cv_image = imgrgb

        #########################################################################################  buoy

        if self.buoy_detector  == 1:

            hsv_thresh_buoy = cv2.inRange(imghsv, self.buoy_color_lower_orange , self.buoy_color_upper_orange)
            preview_buoy = cv2.bitwise_and(cv_image, cv_image, mask=hsv_thresh_buoy)
            #cv2.imshow('HSV_buoy', preview_buoy)

            # Find contours
            contours, _ = cv2.findContours(hsv_thresh_buoy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Find largest contour
            max_area = 0
            max_contour = None
            center_buoy = None

            for cnt in contours:
                area = cv2.contourArea(cnt)
                
                if area < self.buoy_min_area:
                    continue
                
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
                    self.buoy_pub.publish(buoy_position_msg)
                    #self.get_logger().info(f"detect buoy")

                    cv2.circle(preview_buoy, (cx, cy), 10, (0, 0, 255), 1)

                    # Put area text
                    cv2.putText(preview_buoy, f"Area: {int(max_area)}", (cx + 10, cy - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    

                    cv2.circle(cv_image_noted, (cx, cy), 10, (0, 0, 255), 1)

                    # Put area text
                    cv2.putText(cv_image_noted, f"Area: {int(max_area)}", (cx + 10, cy - 10),
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

                    if area < self.auv_min_area:
                        continue

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
                        cv2.circle(preview_auv, (cx, cy), 10, (0, 0, 255), 1)

                        cv2.circle(cv_image_noted, (cx, cy), 10, (0, 0, 255), 1)

                        auv_position_msg = Float32MultiArray()
                        auv_position_msg.data = [float(cx), float(cy)]  # Publish the coordinates of the AUV
                        self.auv_pub.publish(auv_position_msg)

                        # Put area text
                        cv2.putText(preview_auv, f"AUV Area: {int(max_area)}", (cx + 10, cy - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                        
                        cv2.putText(cv_image_noted, f"AUV Area: {int(max_area)}", (cx + 10, cy - 10),
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
                    auv_position_msg = Float32MultiArray()
                    auv_position_msg.data = [float(center[0]), float(center[1])]  # Publish the coordinates of the AUV
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

            middle_position_msg = Float32MultiArray()
            middle_position_msg.data = [float(center_between_auv_and_buoy[0]), float(center_between_auv_and_buoy[1])]  # Publish the coordinates of the middle point between auv and buoy
            self.middle_pub.publish(middle_position_msg) 

            cx = int(center_between_auv_and_buoy[0])  
            cy = int(center_between_auv_and_buoy[1])  
            cv2.circle(cv_image_noted, (cx, cy), 5, (0, 0, 255), -1) 
            cv2.putText(cv_image_noted, f"Middle Point", (cx + 10, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)


        # Show the combined result
        if self.debug_imshow >=2:
            cv2.imshow('Combined_HSV', combined_preview)
        if self.debug_imshow >=1:
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