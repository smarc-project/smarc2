import collections
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
import numpy as np
from cv_bridge import CvBridge
from std_msgs.msg import Float32MultiArray
from sklearn.decomposition import PCA
from drone_msgs.msg import Links as DroneLinks
from drone_msgs.msg import Topics as DroneTopics
import auv_detector.params_detector_2 as P
from scipy.interpolate import splprep, splev
from sklearn.neighbors import NearestNeighbors
from collections import deque
import heapq

from tf2_ros import TransformListener, Buffer
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformException


class KNN(Node):
    def __init__(self):
        super().__init__('k_nearest_neighbors')
        # ===== Declare parameters =====
        self.declare_node_parameters()

        # ===== Get parameters =====
        self.robot_name = self.get_parameter("robot_name").value

        self.knn_lowerbound = self.get_parameter("knn.lowerbound").value
        self.aspect_upper_bound = self.get_parameter("data_association.aspect_upper_bound").value
        self.sam_threshold = self.get_parameter("sam.threshold").value
        self.min_area_sam = self.get_parameter("sam.min_area").value
        self.sam_color = self.get_parameter("sam.color_rgb").value
        self.buoy_threshold = self.get_parameter("buoy.threshold").value
        self.buoy_color = self.get_parameter("buoy.color_rgb").value
        self.auv_name = self.get_parameter("name.auv_name").value
        self.buoy_name = self.get_parameter("name.buoy_name").value
        self.min_area_filter = self.get_parameter("vision.min_area_filter").value
        self.max_area_filter = self.get_parameter("vision.max_area_filter").value
        self.best_fit_degree = self.get_parameter("vision.best_fit_degree").value
        self.realdata_topic = self.get_parameter("realdata.topic").value
        self.realdata = self.get_parameter("realdata.enabled").value
        # self.realdata_path = self.get_parameter("realdata.path").value
        self.SHOW_DEBUG = self.get_parameter("show_debug").value

        # Initialization (in __init__ or once)
        self.rope_img_buffer = deque(maxlen=5)
        self.rope_mask_buffer = deque(maxlen=5)

        if(P.REALDATA) :
            self.subscription = self.create_subscription(
                Image,
                f"/Quadrotor/gimbal_camera/image_raw",
                self.listener_callback,            
                10)

            # self.subscription = self.create_subscription(
            #     Image,
            #     f"/{self.robot_name}/{self.realdata_topic}",
            #     self.listener_callback,            
            #     10)
        else:
            self.subscription = self.create_subscription(
                Image,
                f"/Quadrotor/gimbal_camera/image_raw",
                self.listener_callback,            
                10)
            # self.subscription = self.create_subscription(
            #     Image,
            #     f"/{self.robot_name}/{DroneTopics.CAMERA_DATA_TOPIC}",
            #     self.listener_callback,            
            #     10)
        self.subscription
        self.bridge = CvBridge()
        self.mask_publisher = self.create_publisher(Image, f"/{self.robot_name}/{DroneTopics.CAMERA_PROCESSED_TOPIC}", 10)
        # self.foreground_publisher = self.create_publisher(Image, 'Quadrotor/core/fpcamera/image_foreground', 10)
        # self.detection_publisher = self.create_publisher(Image, 'Quadrotor/core/fpcamera/image_detection', 10)
        self.buoy_pub = self.create_publisher(Float32MultiArray, f"/{self.robot_name}/{ DroneTopics.BUOY_DETECTOR_ESTIMATE_TOPIC}", 10)
        self.buoy_pub_3 = self.create_publisher(Float32MultiArray, f"alars_detection/buoy", 10)

        self.sam_lowest_pub = self.create_publisher(Float32MultiArray, f"/{self.robot_name}/{ DroneTopics.SAM_LOWEST_POINT_ESTIMATE_TOPIC}", 10)
        self.auv_pub = self.create_publisher(Float32MultiArray, f"alars_detection/auv", 10)

        self.target_pub = self.create_publisher(Float32MultiArray, f"/target", 10)  # [diving x, diving y, heading x, heading y]
        self.middle_pub = self.create_publisher(Float32MultiArray, f"alars_detection/middle", 10)

        self.knn = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=self.knn_lowerbound,detectShadows=False)
        #self.knn = cv2.createBackgroundSubtractorKNN(history=1000, dist2Threshold=10,detectShadows=False)


        # Initialize the tf buffer and listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Use a timer to periodically check for transform
        #self.timer = self.create_timer(0.1, self.timer_callback)  # 10 Hz

        # Set parent and child frame
        self.parent_frame = 'map_gt'
        #self.child_frame = 'Quadrotor/camera_gt'
        self.child_frame = 'Quadrotor/winch_link'

    # def timer_callback(self):
    #     try:
    #         now = rclpy.time.Time()
    #         trans: TransformStamped = self.tf_buffer.lookup_transform(
    #             self.parent_frame,
    #             self.child_frame,
    #             now
    #         )
    #         pos = trans.transform.translation
    #         self.get_logger().info(f"[{self.child_frame}] Position in [{self.parent_frame}]: x={pos.x:.2f}, y={pos.y:.2f}, z={pos.z:.2f}")
    #     except TransformException as e:
    #         self.get_logger().warn(f'Could not transform {self.parent_frame} -> {self.child_frame}: {str(e)}')



    def declare_node_parameters(self):
        """
        Declare the node parameters for the AUV position estimator node.
        """
        self.declare_parameter("robot_name", "Quadrotor")
        
        self.declare_parameter("knn.lowerbound", P.KNN_LOWERBOUND)
        self.declare_parameter("data_association.aspect_upper_bound", P.ASPECT_UPPER_BOUND)
        self.declare_parameter("sam.threshold", P.SAM_THRESHOLD)
        self.declare_parameter("sam.min_area", P.MIN_AREA_SAM)
        self.declare_parameter("sam.color_rgb", P.SAM_COLOR)
        self.declare_parameter("buoy.threshold", P.BUOY_THRESHOLD)
        self.declare_parameter("buoy.color_rgb", P.BUOY_COLOR)
        self.declare_parameter("name.auv_name", P.AUV_NAME)
        self.declare_parameter("name.buoy_name", P.BUOY_NAME)
        self.declare_parameter("vision.min_area_filter", P.MIN_AREA_FILTER)
        self.declare_parameter("vision.max_area_filter", P.MAX_AREA_FILTER)
        self.declare_parameter("vision.best_fit_degree", P.BEST_FIT_DEGREE)
        self.declare_parameter("realdata.topic", P.REALDATA_TOPIC)
        self.declare_parameter("realdata.enabled", P.REALDATA)
        # self.declare_parameter("realdata_path", P.REALDATA_PATH)

        self.declare_parameter("show_debug", False)  # Show debug images in separate windows


        
    def listener_callback(self, msg):
        # self.get_logger().info("Received an image!")
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        # cv_image = self.enhance_saturation(cv_image, saturation_factor=1.5) TODO : increase saturation and see if results improve
        #enhance saturation values
        sat_factor = 1
        imghsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV).astype("float32")
        (h, s, v) = cv2.split(imghsv)
        s = s*sat_factor
        s = np.clip(s,0,255)
        imghsv = cv2.merge([h,s,v])
        imgrgb = cv2.cvtColor(imghsv.astype("uint8"), cv2.COLOR_HSV2BGR)
        cv_image = imgrgb
        # Apply the MOG2 algorithm to get the foreground mask
        foreground_mask = self.knn.apply(cv_image)
        #cv2.imshow('KNN', foreground_mask)

        #########################################################################################  buoy

        # HSV filter for buoy
        lower_orange = np.array([26, 190, 0])  # manual hsv detector
        upper_orange = np.array([36, 231, 245])
        hsv_thresh_buoy = cv2.inRange(imghsv, lower_orange, upper_orange)
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
                self.buoy_pub_3.publish(buoy_position_msg)
                #self.get_logger().info(f"detect buoy")

                cv2.circle(preview_buoy, (cx, cy), 10, (0, 0, 255), 1)

                # Put area text
                cv2.putText(preview_buoy, f"Area: {int(max_area)}", (cx + 10, cy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        #cv2.imshow('HSV_buoy', preview_buoy)

        #########################################################################################  auv


        # HSV filter for sam auv
        lower_yellow = np.array([25, 0, 169])  # manual hsv detector
        upper_yellow = np.array([46, 103, 221])
        hsv_thresh_auv = cv2.inRange(imghsv, lower_yellow, upper_yellow)
        preview_auv = cv2.bitwise_and(cv_image, cv_image, mask=hsv_thresh_auv)
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
                cv2.circle(preview_auv, (cx, cy), 10, (0, 0, 255), 1)

                auv_position_msg = Float32MultiArray()
                auv_position_msg.data = [float(cx), float(cy)]  # Publish the coordinates of the AUV
                self.auv_pub.publish(auv_position_msg)

                # Put area text
                cv2.putText(preview_auv, f"AUV Area: {int(max_area)}", (cx + 10, cy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        if self.SHOW_DEBUG: cv2.imshow('HSV_auv', preview_auv)



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


        if self.SHOW_DEBUG: cv2.imshow('HSV_auv_Missle_Shape Detect', preview_auv_2)
        #########################################################################################   rope

        # HSV filter for rope
        lower_rope = np.array([6, 61, 165])  # manual hsv detector
        upper_rope = np.array([22, 120, 187])
        hsv_thresh_rope = cv2.inRange(imghsv, lower_rope, upper_rope)
        preview_rope = cv2.bitwise_and(cv_image, cv_image, mask=hsv_thresh_rope)
        preview_rope_2 = preview_rope.copy()
        preview_rope_3 = preview_rope.copy()
        if self.SHOW_DEBUG: cv2.imshow('HSV_rope', preview_rope)


        # Rope Reconstruction method 1 
        # # Step 1: Find rope points
        # ys, xs = np.where(hsv_thresh_rope > 0)
        # rope_points = np.array(list(zip(xs, ys)))
        # # Step 2: Add AUV and buoy centers
        # if center_auv is not None and center_buoy is not None and len(rope_points) > 0:
        #     full_points = np.vstack([rope_points, center_auv, center_buoy])

        #     # Optional: Sort points based on distance from AUV or along y-axis
        #     full_points = full_points[full_points[:, 1].argsort()]  # sort by y (top to bottom)

        #     # Step 3: Fit a polyline or spline through the points
        #     for i in range(len(full_points) - 1):
        #         pt1 = tuple(full_points[i])
        #         pt2 = tuple(full_points[i + 1])
        #         cv2.line(preview_rope_2, pt1, pt2, (255, 0, 255), 2)  # Draw in magenta
        # cv2.imshow("Rope_Reconstructed", preview_rope_2)

        # # Rope Reconstruction method 2  ---- Spline
        # # 1. Extract rope pixels
        # ys, xs = np.where(hsv_thresh_rope > 0)
        # rope_pixels = np.array(list(zip(xs, ys)))

        # # 2. Add AUV and buoy centers
        # if center_auv is not None and center_buoy is not None and len(rope_pixels) > 2:
        #     full_points = np.vstack([rope_pixels, center_auv, center_buoy])

        #     # 3. Sort points vertically (optional, for consistency)
        #     full_points = full_points[full_points[:, 1].argsort()]

        #     # 4. Fit spline
        #     try:
        #         tck, _ = splprep([full_points[:, 0], full_points[:, 1]], s=50)  # s controls smoothness
        #         u_fine = np.linspace(0, 1, 100)
        #         x_fine, y_fine = splev(u_fine, tck)

        #         # 5. Draw the spline
        #         for i in range(len(x_fine) - 1):
        #             pt1 = (int(x_fine[i]), int(y_fine[i]))
        #             pt2 = (int(x_fine[i + 1]), int(y_fine[i + 1]))
        #             cv2.line(preview_rope_3, pt1, pt2, (255, 0, 255), 2)  # magenta curve
        #     except Exception as e:
        #         print("Spline fitting failed:", e)
        # cv2.imshow("Rope Curve Fit", preview_rope_3)



        # # Rope Reconstruction method 3 ---- KNN

        # # 1. Get rope pixel coordinates
        # ys, xs = np.where(hsv_thresh_rope > 0)
        # rope_pixels = np.array(list(zip(xs, ys)))

        # # 2. Add buoy and AUV centers
        # if len(rope_pixels) > 2 and center_buoy is not None and center_auv is not None:
        #     full_points = np.vstack([rope_pixels, center_buoy, center_auv])

        #     # 3. Use KNN to order points starting from one end (e.g., AUV)
        #     ordered_points = self.order_points_knn(full_points, center_auv)

        #     # # 4. Fit spline curve
        #     try:
        #         tck, _ = splprep([ordered_points[:, 0], ordered_points[:, 1]], s=30)
        #         u_fine = np.linspace(0, 1, 100)
        #         x_fine, y_fine = splev(u_fine, tck)

        #         # 5. Draw the fitted rope curve
        #         for i in range(len(x_fine) - 1):
        #             pt1 = (int(x_fine[i]), int(y_fine[i]))
        #             pt2 = (int(x_fine[i + 1]), int(y_fine[i + 1]))
        #             cv2.line(preview_rope_3, pt1, pt2, (255, 0, 255), 2)
        #     except Exception as e:
        #         print("Spline fitting failed:", e)


        #     # # Step 4: Fit a polyline through the points
        #     # for i in range(len(ordered_points) - 1):
        #     #     pt1 = tuple(ordered_points[i])
        #     #     pt2 = tuple(ordered_points[i + 1])
        #     #     cv2.line(preview_rope_3, pt1, pt2, (255, 0, 255), 2)  # Draw in magenta

        # cv2.imshow("Rope Curve Fit", preview_rope_3)

        

        # Rope Reconstruction method 4 ---- multi frames
        self.rope_img_buffer.append(preview_rope_3)
        for img_tmp in self.rope_img_buffer:
            preview_rope_3 = cv2.add(preview_rope_3, img_tmp)
        #cv2.imshow("N frames rope detect", preview_rope_3)


       

        # Apply dilation to connect fragmented rope segments
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 8))  # or (3,3) if rope is thin
        rope_dilated = cv2.dilate(preview_rope_3, kernel, iterations=1)
        # Use this dilated result for binary mask and grid processing
        rope_bin = cv2.cvtColor(rope_dilated, cv2.COLOR_BGR2GRAY)
        _, rope_bin = cv2.threshold(rope_bin, 1, 255, cv2.THRESH_BINARY)
        #cv2.imshow("Dilation", rope_bin)

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
            cv2.circle(preview_rope_2, (center_x_rope, center_y_rope), 5, (0, 255, 0), 1) # rope center

            cv2.putText(preview_rope_2, "Heading Point", (center_x_rope + 10, center_y_rope - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            if self.SHOW_DEBUG: cv2.imshow("Curve Fitting", preview_rope_2)
        # grid-based search require fully connection 
        # path_px = self.grid_path_from_rope(preview_rope_3, center_buoy, center_auv, cell_size=5)

        # # Draw the path on image
        # for i in range(1, len(path_px)):
        #     cv2.line(preview_rope_3, path_px[i-1], path_px[i], (0, 255, 0), 2)
        # cv2.imshow("Grid-Based Rope Path Reconstructed", preview_rope_3)

        #########################################################################################

        # Just add the filtered images directly
        combined_preview = cv2.add(preview_buoy, preview_auv)
        combined_preview = cv2.add(combined_preview, preview_rope_3)

        if center_auv is not None and center_buoy is not None:
            center_between_auv_and_buoy = (center_auv + center_buoy) / 2

            middle_position_msg = Float32MultiArray()
            middle_position_msg.data = [float(center_between_auv_and_buoy[0]), float(center_between_auv_and_buoy[1])]  # Publish the coordinates of the middle point between auv and buoy
            self.middle_pub.publish(middle_position_msg)    
            
            direction_between_auv_and_buoy =  center_auv - center_buoy
            direction_between_auv_and_buoy = direction_between_auv_and_buoy / np.linalg.norm(direction_between_auv_and_buoy)  # Normalize

            # Compute Perpendicular Unit Vector
            perp = np.array([direction_between_auv_and_buoy[1], -direction_between_auv_and_buoy[0]])

            # Assume camera intrinsics
            fx, fy = 369.5, 415.69 # focus
            cam_x, cam_y = 320, 240 # pixels
            cam_Z = 7.0  # e.g., quadrotor height (meter)

            # Midpoint in 3D
            X_center = (center_between_auv_and_buoy[0] - cam_x) * cam_Z / fx
            Y_center = (center_between_auv_and_buoy[1] - cam_y) * cam_Z / fy

            # Convert pixel offset (perp) to metric offset at depth Z
            dx = (perp[0] * cam_Z) / fx
            dy = (perp[1] * cam_Z) / fy

            # Scale to get 0.2m offset distance
            scale = 0.2 / np.sqrt(dx**2 + dy**2)
            offset_x = dx * scale
            offset_y = dy * scale

            # Final 3D target in camera frame
            target_camera = [X_center + offset_x, Y_center + offset_y, cam_Z]
            #self.get_logger().info(f"Hook diving point-------------: {target_camera}")

            # Display into camera
            target_u = int(fx * target_camera[0] / cam_Z + cam_x)
            target_v = int(fy * target_camera[1] / cam_Z + cam_y)

            cv2.circle(combined_preview, (target_u, target_v), radius=3, color=(0, 255, 255), thickness=-1)
            cv2.putText(combined_preview, "Diving Point", (target_u + 10, target_v - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            

            # Draw heading
            arrow_start_point = (target_u, target_v)
            arrow_end_point = (center_x_rope, center_y_rope)
            cv2.arrowedLine(combined_preview, arrow_start_point, arrow_end_point, (0, 255, 0), thickness=1, tipLength=0.3)

            # Final 3D heading in camera frame
            heading_x = (center_x_rope - cam_x) * cam_Z / fx
            heading_y = (center_y_rope - cam_y) * cam_Z / fy

            # Publish Target
            target_position_msg = Float32MultiArray()
            target_position_msg.data = [float(target_camera[0]), float(target_camera[1]), float(heading_x), float(heading_y)] # diving point and heading 
            self.target_pub.publish(target_position_msg) 

        # Show the combined result
        if self.SHOW_DEBUG: cv2.imshow('Combined_HSV', combined_preview)
        #########################################################################################

        # Apply the connected component filtering
        filtered_mask = self.remove_small_blobs_connected_components(foreground_mask, min_area=self.min_area_filter, max_area=self.max_area_filter)
        masked_image = cv2.bitwise_and(cv_image, cv_image, mask=filtered_mask)
        avg_rgb = cv2.mean(masked_image, mask=filtered_mask)
        #self.get_logger().info(f"average rgb : {avg_rgb}")  #BGR
        # # Display the mask from KNN
        #cv2.imshow('Detected Foreground', filtered_mask)
        cv2.waitKey(1)
        # Apply morphological operations to remove noise and fill gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        foreground_mask = cv2.morphologyEx(filtered_mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(filtered_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        min_area = 0  # Minimum area threshold to consider a contour
        large_contours = [c for c in contours if cv2.contourArea(c) > min_area]

        debug_contour_img = cv_image.copy()
        cv2.drawContours(debug_contour_img, large_contours, -1, (0, 255, 0), 2)  # green contours
        #cv2.imshow("Large Contours", debug_contour_img)


        for cnt in large_contours:

            # Data Association
            if self.data_association(cnt, filtered_mask, cv_image) == self.auv_name:
                # Extract points from the contour
                points = cnt[:, 0, :]  # Extract (x, y) points

                # Apply PCA to align the points along the principal axes
                pca = PCA(n_components=2)
                pca.fit(points)
                rotated_points = pca.transform(points)

                # Separate the rotated x and y coordinates
                x = rotated_points[:, 0]
                y = rotated_points[:, 1]
                
                # Create a parameter t that goes from 0 to 1
                t = np.linspace(0, 1, len(points))

                # best_deg = 1
                # min_error = float('inf')
                # best_p1 = None
                # best_p2 = None
                # Fit ith degree polynomial to x(t) and y(t)
                p1 = np.poly1d(np.polyfit(t, x, self.best_fit_degree))
                p2 = np.poly1d(np.polyfit(t, y, self.best_fit_degree))
                # for i in range(1, 10):
                #     # Fit ith degree polynomial to x(t) and y(t)
                #     p1 = np.poly1d(np.polyfit(t, x, i))
                #     p2 = np.poly1d(np.polyfit(t, y, i))
                    
                #     # Calculate the fit errors
                #     x_poly = p1(t)
                #     y_poly = p2(t)
                #     error = np.linalg.norm(x_poly - x) + np.linalg.norm(y_poly - y)
                    
                #     # Update the best polynomial if error is smaller
                #     if error < min_error:
                #         min_error = error
                #         best_deg = i
                #         best_p1 = p1
                #         best_p2 = p2
                # self.get_logger().info(f"the best fit degree is {i}")
                # Generate fitted points
                t_fit = np.linspace(0, 1, 100)
                # x_fit = best_p1(t_fit)
                # y_fit = best_p2(t_fit)

                x_fit = p1(t_fit)
                y_fit = p2(t_fit)

                # # First derivatives
                # dx_dt = best_p1.deriv()(t_fit)
                # dy_dt = best_p2.deriv()(t_fit)
                # First derivatives
                dx_dt = p1.deriv()(t_fit)
                dy_dt = p2.deriv()(t_fit)

                # Magnitude of the derivative at each point
                derivative_magnitude = np.sqrt(dx_dt**2 + dy_dt**2)
                # Find the index of the maximum magnitude
                max_derivative_index = np.argmax(derivative_magnitude)
                min_derivative_index = np.argmin(derivative_magnitude)

                # max_derivative_index = np.argmax(derivative_magnitude)
                # Rotate the fitted polynomial back to the original coordinate system
                fitted_points = np.vstack((x_fit, y_fit)).T
                original_fitted_points = pca.inverse_transform(fitted_points)

                max_x = x_fit[max_derivative_index]
                max_y = y_fit[max_derivative_index] 
                min_x = x_fit[min_derivative_index]
                min_y = y_fit[min_derivative_index] 
                # Highlight the point with the highest derivative magnitude
                max_point = pca.inverse_transform([[max_x, max_y]])[0]
                min_point = pca.inverse_transform([[min_x, min_y]])[0]
                cv_image = cv2.circle(cv_image, tuple(max_point.astype(int)), 5, (0, 0, 255), -1)  # Red dot for max derivative
                cv_image = cv2.circle(cv_image, tuple(min_point.astype(int)), 5, (0, 255, 0), -1)  # Yellow dot for min derivative
                # Publish the minimum gradient point
                min_gradient_msg = Float32MultiArray()
                min_gradient_msg.data = [max_point[0], max_point[1]]
                self.sam_lowest_pub.publish(min_gradient_msg)
                

                # Draw the fitted curve on the image
                for i in range(len(original_fitted_points) - 1):
                    pt1 = tuple(original_fitted_points[i].astype(int))
                    pt2 = tuple(original_fitted_points[i + 1].astype(int))
                    cv_image = cv2.line(cv_image, pt1, pt2, (255, 255, 0), 2)   # Blue color

            elif self.data_association(cnt, filtered_mask, cv_image) == self.buoy_name:
                # Get any point from the contour (e.g., the first point)
                point = cnt[0][0]  # This is the first point in the contour, it could be any point from the contour

                # Draw a circle at the selected point (using a radius of 5 and color green for visibility)
                cv_image = cv2.circle(cv_image, (point[0], point[1]), radius=5, color=(0, 255, 0), thickness=-1)  # Green dot

                # Publish the point (as a Float32MultiArray)
                # buoy_position_msg = Float32MultiArray()
                # buoy_position_msg.data = [float(point[0]), float(point[1])]  # Publish the coordinates of the point
                # self.buoy_pub.publish(buoy_position_msg)
                # self.get_logger().info(f"buoy publishing ......!!!! ")


        # Publish the processed mask
        mask_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding="bgr8")
        self.mask_publisher.publish(mask_msg)
        
        # # Display the point where we guess the buoy is
        # # cv2.imshow('Curve and Min gradeint Lowest Point', cv_image)
        # # cv2.waitKey(1)

        # # Display the mask from KNN
        # cv2.imshow('Detected Foreground', filtered_mask)
        # cv2.waitKey(1)
    
    def data_association(self, cnt, filtered_mask, cv_image):

        # Step 1: Calculate the yellow percentage in the contour
        contour_mask = np.zeros_like(filtered_mask)
        cv2.drawContours(contour_mask, [cnt], -1, 255, thickness=cv2.FILLED)
        #cv2.imshow("data_association", contour_mask)
        #cv2.waitKey(1) 
        orange_percentage = self.get_orange_percentage(contour_mask, cv_image, np.uint8([[self.buoy_color]]))
        # yellow_percentage = self.get_yellow_percentage(contour_mask, cv_image, lower_yellow, upper_yellow)
        yellow_percentage = self.get_yellow_percentage(contour_mask, cv_image, np.uint8([[self.sam_color]]))

        # # Print the yellow percentage for tuning
        #self.get_logger().info(f'Yellow percentage: {yellow_percentage:.2f}%')
        #self.get_logger().info(f'Orange percentage: {orange_percentage:.2f}%')
        if orange_percentage > self.buoy_threshold:
            # cv2.drawContours(cv_image, [cnt], -1, (0, 255, 0), thickness=cv2.FILLED)
            return self.buoy_name
        # Step 2: Proceed only if the yellow percentage is high enough
        if yellow_percentage > self.sam_threshold:  # Liberal threshold, you can adjust this
            if cv2.contourArea(cnt) > self.min_area_sam :  # Adjust as needed
                
                # Use minAreaRect to get the smallest bounding box around the contour
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box = np.intp(box)

                # Extract width and height from the bounding box (minAreaRect)
                width = rect[1][0]
                height = rect[1][1]

                # Ensure width and height are non-zero to avoid division by zero
                if width > 0 and height > 0:
                    # Aspect ratio from the minimum area rectangle
                    aspect_ratio = min(width, height) / max(width, height)
                    # self.get_logger().info(f'Aspect ratio: {aspect_ratio:.2f}')

                    # Check the aspect ratio against the liberal threshold
                    
                    if 0 < aspect_ratio < self.aspect_upper_bound:  # Adjust as needed
                        # self.get_logger().info('Contour meets aspect ratio criteria')
                        # Visualize the contour and the minAreaRect box
                        # cv2.drawContours(cv_image, [box], -1, (0, 255, 0), 2)

                        #self.get_logger().info(f"all tests satisfied")
                        return self.auv_name
                    else :
                        # cv2.drawContours(cv_image, [cnt], -1, (0, 0, 255), thickness=cv2.FILLED)
                        #self.get_logger().info(f"aspect ratio test not satisfied : {aspect_ratio}")
                        pass
                # else :
            #         # cv2.drawContours(cv_image, [cnt], -1, (0, 0, 255), thickness=cv2.FILLED)
            #         self.get_logger().info("yellow pixel test not satisfied")
            else : 
                #self.get_logger().info(f"area test not satisfied : {cv2.contourArea(cnt)}")
                pass
        else : 
            #self.get_logger().info(f"color threshold test  not satisfied : {yellow_percentage}")
            pass
        return False


    def get_yellow_percentage(self, mask, image, rgb_color_yellow):
        # Convert RGB color to HSV
        hsv_color = cv2.cvtColor(rgb_color_yellow, cv2.COLOR_RGB2HSV)
        hsv_value = hsv_color[0][0]

        # print("Target HSV value:", hsv_value)

        # Define your lower and upper HSV bounds (widened range)
        lower_yellow = hsv_value - np.array([5, 25, 25])  # Adjust tolerances as needed
        upper_yellow = hsv_value + np.array([5, 25, 25])

        # Clip to valid HSV ranges
        lower_yellow = np.clip(lower_yellow, 0, 255)
        upper_yellow = np.clip(upper_yellow, 0, 255)

        # Apply the mask to the image
        masked_image = cv2.bitwise_and(image, image, mask=mask)

        # Convert the masked image to HSV color space
        hsv_image = cv2.cvtColor(masked_image, cv2.COLOR_BGR2HSV)

        # Create a mask for the orange color
        yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)

        # Count all non-zero values in the orange mask
        yellow_pixels = np.sum(yellow_mask > 0)  # Count all orange-like pixels

        # Calculate the total number of pixels in the original mask
        total_pixels = np.sum(mask > 0)  # Count all non-zero pixels in the mask

        # Calculate the percentage of orange pixels
        yellow_percentage = (yellow_pixels / total_pixels) * 100 if total_pixels > 0 else 0

        return yellow_percentage

    def get_orange_percentage(self, mask, image, rgb_color):
        # Convert RGB color to HSV
        hsv_color = cv2.cvtColor(rgb_color, cv2.COLOR_RGB2HSV)
        hsv_value = hsv_color[0][0]

        # print("Target HSV value:", hsv_value)

        # Define your lower and upper HSV bounds (widened range)
        lower_orange = hsv_value - np.array([15, 80, 80])  # Adjust tolerances as needed
        upper_orange = hsv_value + np.array([15, 80, 80])

        #lower_orange = np.array([16, 0, 255])  # manual hsv detector
        #upper_orange = np.array([25, 152, 255])

        # Clip to valid HSV ranges
        lower_orange = np.clip(lower_orange, 0, 255)
        upper_orange = np.clip(upper_orange, 0, 255)

        # Apply the mask to the image
        masked_image = cv2.bitwise_and(image, image, mask=mask)

        # Convert the masked image to HSV color space
        hsv_image = cv2.cvtColor(masked_image, cv2.COLOR_BGR2HSV)

        # Create a mask for the orange color
        orange_mask = cv2.inRange(hsv_image, lower_orange, upper_orange)

        # Count all non-zero values in the orange mask
        orange_pixels = np.sum(orange_mask > 0)  # Count all orange-like pixels

        # Calculate the total number of pixels in the original mask
        total_pixels = np.sum(mask > 0)  # Count all non-zero pixels in the mask

        # Calculate the percentage of orange pixels
        orange_percentage = (orange_pixels / total_pixels) * 100 if total_pixels > 0 else 0

        return orange_percentage


    # Step 2: Mask the yellow regions
    def mask_yellow_regions(self, image, lower_yellow, upper_yellow):
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
        return yellow_mask

    # Step 3: Check the aspect ratio of the contour
    def check_aspect_ratio(contour):
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h)
        return aspect_ratio        
    

    def remove_small_blobs_connected_components(self, foreground_mask, min_area= P.MIN_AREA_FILTER , max_area=P.MAX_AREA_FILTER):
            # Find all connected components in the mask
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(foreground_mask)

            # Create a blank mask
            filtered_mask = np.zeros_like(foreground_mask)
            #self.get_logger().info("_____________________________________________")
            # Loop over each connected component
            for i in range(1, num_labels):  # Start from 1 to skip the background
                area = stats[i, cv2.CC_STAT_AREA]

                # Filter based on the area
 
                if min_area < area < max_area:
                    #self.get_logger().info(f"area :{area}") 
                    filtered_mask[labels == i] = 255

            return filtered_mask    
    
    def order_points_knn(self, points, start_point, k=5):
        ordered = [start_point]
        remaining = points.copy()
        nbrs = NearestNeighbors(n_neighbors=min(k, len(points))).fit(remaining)

        current = start_point
        for _ in range(len(points)):
            distances, indices = nbrs.kneighbors([current], return_distance=True)
            for idx in indices[0]:
                candidate = remaining[idx]
                if not any(np.array_equal(candidate, o) for o in ordered):
                    ordered.append(candidate)
                    current = candidate
                    break

        return np.array(ordered)


    def astar(self, grid, start, goal):
        """A* pathfinding on binary grid."""
        rows, cols = grid.shape
        open_set = [(0 + np.linalg.norm(np.subtract(start, goal)), 0, start, [])]
        visited = set()

        while open_set:
            est_total, cost, current, path = heapq.heappop(open_set)

            if current in visited:
                continue
            visited.add(current)
            path = path + [current]

            if current == goal:
                return path

            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(1,-1),(-1,1)]:
                nx, ny = current[0] + dx, current[1] + dy
                if 0 <= nx < rows and 0 <= ny < cols and grid[nx, ny]:
                    heapq.heappush(open_set, (
                        cost + 1 + np.linalg.norm(np.subtract((nx, ny), goal)),
                        cost + 1,
                        (nx, ny),
                        path
                    ))
        return []


    def grid_path_from_rope(self, rope_img, start_px, end_px, cell_size=5):
        # 1. Threshold the rope mask
        rope_gray = cv2.cvtColor(rope_img, cv2.COLOR_BGR2GRAY)
        _, rope_bin = cv2.threshold(rope_gray, 1, 1, cv2.THRESH_BINARY)

        # 2. Downsample to grid
        h, w = rope_bin.shape
        grid_h, grid_w = h // cell_size, w // cell_size
        grid = np.zeros((grid_h, grid_w), dtype=np.uint8)

        for y in range(grid_h):
            for x in range(grid_w):
                grid[y, x] = np.any(
                    rope_bin[y*cell_size:(y+1)*cell_size, x*cell_size:(x+1)*cell_size]
                )

        # 3. Convert start/end points to grid
        start_grid = (start_px[1] // cell_size, start_px[0] // cell_size)
        end_grid = (end_px[1] // cell_size, end_px[0] // cell_size)

        # 4. Run A*
        path = self.astar(grid, start_grid, end_grid)

        # 5. Convert path back to pixel coordinates
        path_px = [(x * cell_size + cell_size//2, y * cell_size + cell_size//2) for y, x in path]
        return path_px


def main(args=None):
    rclpy.init(args=args)
    k_nearest_neighbors = KNN()
    rclpy.spin(k_nearest_neighbors)
    k_nearest_neighbors.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()