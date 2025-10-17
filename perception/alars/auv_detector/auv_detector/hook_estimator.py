# Standard library imports
import os
import csv
from collections import deque
from itertools import groupby
from operator import itemgetter
from datetime import datetime

# Third-party imports
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

from scipy.spatial.transform import Rotation
from filterpy.kalman import ExtendedKalmanFilter

# ROS 2 imports
import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32MultiArray, Header
from std_srvs.srv import Trigger

from sensor_msgs.msg import Image, Imu
from geometry_msgs.msg import PoseStamped, AccelStamped, Vector3Stamped, TransformStamped, PointStamped
from nav_msgs.msg import Odometry

from tf2_ros import TransformListener, Buffer, TransformException

from cv_bridge import CvBridge

# Custom message imports
from dji_msgs.msg import Topics as DjiTopics, Links
from smarc_msgs.msg import Topics as SmarcTopics



class hook_estimator(Node):
    def __init__(self):
        super().__init__('hook_estimator')

        # Declare parameters and get their values
        self.declare_parameter('enabled', True)
        self.declare_parameter('robot_name', 'Quadrotor')
        self.declare_parameter('enable_visualization', True)
        self.declare_parameter('current_length', 5.0) 

        self.enabled = self.get_parameter('enabled').value
        self.robot_name = self.get_parameter('robot_name').value
        self.enable_visualization = self.get_parameter('enable_visualization').value
        self.current_length = self.get_parameter('current_length').value

        self.get_logger().info(f'Node enabled: {self.enabled}')
        self.get_logger().info(f'Robot name: {self.robot_name}')
        self.get_logger().info(f'Visualization enabled: {self.enable_visualization}')
        self.get_logger().info(f'Current rope length: {self.current_length} meters')

        # Subscriptions
        self.subscription_camera = self.create_subscription(
            Image,
            DjiTopics.GIMBAL_CAMERA_RAW_TOPIC,
            self.listener_callback,
            10
        )
        self.subscription_camera  # prevent unused variable warning

        self.bridge = CvBridge()

        # Internal variables
        self.cv_image = None
        self.stamp = None
        self.debug_imshow = False
        self.gb_cv_image_hough = None

        self.hook_timer = self.create_timer(0.1, self.process_hook_estimation)

        self.subscription_odom = self.create_subscription(
            Odometry,
            SmarcTopics.ODOM_TOPIC,
            self.odom_callback,
            10)

        # Estimated positions and history
        self.est_Hook_pos_in_winch_frame = np.array([np.nan, np.nan, np.nan])
        self.est_Hook_pos_in_base_link_frame = np.array([np.nan, np.nan, np.nan])
        self.ekf_Hook_pos_in_winch_frame = np.array([np.nan, np.nan, np.nan])
        self.ekf_Hook_pos_in_base_link_frame = np.array([np.nan, np.nan, np.nan])
        self.est_Hook_pos_in_winch_frame_ekf = np.array([np.nan, np.nan, np.nan])
        self.Hook_pos_in_base_link_frame_to_plot = deque(maxlen=2000)
        self.est_Hook_pos_in_base_link_frame_to_plot = deque(maxlen=2000)
        self.ekf_Hook_pos_in_base_link_frame_to_plot = deque(maxlen=2000)
        self.est_hook_timestamps = deque(maxlen=2000)  # Store timestamps of hook detections
        self.camera_sees_hook = deque(maxlen=2000)

        self.plot_initialized = False
        self.ekf_est_hook_map_pos_to_save = deque(maxlen=2000)  # Store EKF hook estimated pos
        self.ekf_initialized = False
        self.last_ekf_time = None

        # EKF setup
        self.ekf = ExtendedKalmanFilter(dim_x=6, dim_z=3)  # State: [p, v]; Measured: [r]
        self.ekf.x = np.zeros(6)
        self.ekf.P *= 1e-1
        self.ekf.R = np.eye(3) * 1e-1                       # Measurement noise (camera)
        self.ekf.Q = np.eye(6) * 1e-2                       # Process noise
        self.g_vec = np.array([0, 0, 0])  # Gravity vector

        # Initialize IMU values
        self.a_drone = None
        self.smoothed_accel = None
        self.a_drone_odom = None

        # Frame names with namespace from robot_name param
        self.base_link_frame = f'{self.robot_name}/{Links.BASE_LINK}'
        #self.odom_frame = f'{self.robot_name}/{Links.ODOM}' useless?
        self.camera_frame = f'{self.robot_name}/{Links.GIMBAL_CAMERA_LINK}'
        self.winch_frame = f'{self.robot_name}/{Links.WINCH_LINK}'
        self.hook_frame = f'{self.robot_name}/{Links.HOOK_LINK}'

        #self.odom_frame = f'{self.robot_name}/{Links.ODOM}' useless?
        # TF listener and buffer
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.static_tf_timer = self.create_timer(2.0, self.init_static_transforms_once)

        # Publishers
        self.est_hook_pub = self.create_publisher(PointStamped, DjiTopics.ESTIMATED_HOOK_TOPIC, 10)
        self.ekf_hook_pub = self.create_publisher(PointStamped, DjiTopics.ESTIMATED_EKF_HOOK_TOPIC, 10)

        # Enable/disable services
        self.enable_service = self.create_service(Trigger, DjiTopics.ENABLE_HOOK_ESTIMATOR_SERVICE_TOPIC, self.enable_callback)
        self.disable_service = self.create_service(Trigger, DjiTopics.DISABLE_HOOK_ESTIMATOR_SERVICE_TOPIC, self.disable_callback)


    def init_static_transforms_once(self):
        success = self.init_static_transforms(max_retries=20, retry_delay=0.5)
        if success and hasattr(self, 'static_tf_timer'):
            self.static_tf_timer.cancel()
            self.get_logger().info("Static TF timer destroyed after successful initialization.")


    def listener_callback(self, msg):
        if not self.enabled:
            return
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        self.cv_image = self.adjust_saturation(cv_image)
        self.stamp = msg.header.stamp

    def adjust_saturation(self, image, sat_factor=1.0):
        imghsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype("float32")
        h, s, v = cv2.split(imghsv)
        s *= sat_factor
        s = np.clip(s, 0, 255)
        imghsv = cv2.merge([h, s, v])
        return cv2.cvtColor(imghsv.astype("uint8"), cv2.COLOR_HSV2BGR)

    def filter_similar_lines_by_position_and_angle(self, lines, position_thresh=20, angle_thresh=5):
        """
        Filters out lines that are spatially close and have similar orientation.

        Args:
            lines (np.ndarray): Output from cv2.HoughLinesP, shape (N, 1, 4)
            position_thresh (float): Maximum distance between start/end points to consider lines similar
            angle_thresh (float): Maximum angle difference in degrees to consider lines similar

        Returns:
            List of filtered lines, each as [x1, y1, x2, y2]
        """
        if lines is None:
            return []

        lines = [line[0] for line in lines]  # unpack
        accepted = []

        def compute_angle(x1, y1, x2, y2):
            return np.degrees(np.arctan2(y2 - y1, x2 - x1))

        for i, line_i in enumerate(lines):
            x1_i, y1_i, x2_i, y2_i = line_i
            angle_i = compute_angle(x1_i, y1_i, x2_i, y2_i)
            keep = True

            for line_j in accepted:
                x1_j, y1_j, x2_j, y2_j = line_j
                angle_j = compute_angle(x1_j, y1_j, x2_j, y2_j)

                # Distance between corresponding points
                d_start = np.hypot(x1_i - x1_j, y1_i - y1_j)
                d_end   = np.hypot(x2_i - x2_j, y2_i - y2_j)

                if d_start < position_thresh and d_end < position_thresh and abs(angle_i - angle_j) < angle_thresh:
                    keep = False
                    break

            if keep:
                accepted.append(line_i)

        return accepted

    def get_triangle_vertex(self, mask):
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        # Find the largest contour (assumed to be the triangle)
        largest = max(contours, key=cv2.contourArea)
        # Approximate contour to polygon
        epsilon = 0.02 * cv2.arcLength(largest, True)
        approx = cv2.approxPolyDP(largest, epsilon, True)

        # If it's a triangle, approx should have 3 points
        if len(approx) == 3:
            # Extract vertices
            vertices = [tuple(pt[0]) for pt in approx]
            # Example: pick the vertex with the largest Y (lowest point in image)
            tip = max(vertices, key=lambda v: v[1])
            return tip
        else:
            # If not a triangle, return None
            return None

    def estimate_hook_pixel_position(self, cv_image):
        """
        Estimates the hook's pixel position from the camera image using HSV color filtering and contour analysis.

        Args:
            cv_image (np.ndarray): The input image (in BGR format).

        Returns:
            tuple or None: (x, y) pixel coordinates of the hook tip, or None if not detected.
        """

        result = None

        # Convert to HSV
        cv_image_original = cv_image.copy()
        imghsv = cv2.cvtColor(cv_image_original, cv2.COLOR_BGR2HSV)

        cv2.imshow("HSV imghsv original", cv_image_original)

        # HSV range for hook detection (adjust as needed)
        lower_red = np.array([0, 180, 100])
        upper_red = np.array([220, 255, 225])

        hsv_thresh_hook = cv2.inRange(imghsv, lower_red, upper_red)

        preview_hook = cv2.bitwise_and(cv_image, cv_image, mask=hsv_thresh_hook)

        # Inflate the binary mask using dilation
        kernel = np.ones((5, 3), np.uint8)  # You can adjust the kernel size   # (height, width)
        inflated_mask = cv2.dilate(hsv_thresh_hook, kernel, iterations=3)

        # Use the inflated mask for preview
        hsv_thresh_hook_after_dilation = cv2.bitwise_and(cv_image, cv_image, mask=inflated_mask)

        # Find contours
        contours, _ = cv2.findContours(hsv_thresh_hook, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find the biggest area (assumed to be the rope/hook)
        max_area = 0
        biggest_area = None
        cv_image_biggest_area = cv_image.copy()
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > max_area:
                max_area = area
                biggest_area = cnt

        # Convert in greyscale for contour detection
        hsv_thresh_hook_gray = cv2.cvtColor(hsv_thresh_hook, cv2.COLOR_GRAY2BGR)

        # Create mask from the biggest contour
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        mask = np.zeros_like(gray)

        cv_image_hough = None
        
        if biggest_area is not None and max_area > 50:  # Ensure the area is significant
            cv2.drawContours(mask, [biggest_area], -1, 255, thickness=cv2.FILLED)

            # Edge detection on the mask
            edges = cv2.Canny(mask, 50, 150, apertureSize=3)

            # Triangle fitting
            vertex = self.get_triangle_vertex(edges)
            if vertex is not None:
                # Use this as the hook tip
                result = vertex
            else:
                # Hough Transform
                lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=10, maxLineGap=100)
                self.get_logger().info(f"Detected lines: {len(lines) if lines is not None else 0}")
                #filtered_line = self.filter_similar_lines_by_position_and_angle(lines, position_thresh=20, angle_thresh=5)

                # Compute line lengths if lines are detected
                if lines is not None and len(lines) > 0:
                    line_lengths = [np.linalg.norm(np.array([l[0], l[1]]) - np.array([l[2], l[3]])) for l in lines.reshape(-1, 4)]
                    self.get_logger().info(f"Line lengths: {line_lengths}")
                    # Get index of the single longest line
                    longest_index = int(np.argmax(line_lengths))
                    longest_line = [lines[longest_index]]
                else:
                    longest_line = []

                if len(longest_line) == 1:
                    cv_image_hough = cv_image.copy()
                    line = longest_line[0]
                    if line.shape == (1, 4):
                        x1, y1, x2, y2 = line[0]
                    elif line.shape == (4,):
                        x1, y1, x2, y2 = line
                    cv2.line(cv_image_hough, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green line, thickness 2

                    self.gb_cv_image_hough = cv_image_hough.copy()

                    # Compute image center
                    img_h, img_w = cv_image.shape[:2]
                    center_x, center_y = img_w // 2, img_h // 2

                    # Compute distances from endpoints to center
                    dist1 = np.hypot(x1 - center_x, y1 - center_y)
                    dist2 = np.hypot(x2 - center_x, y2 - center_y)

                    # Choose the endpoint closest to the center
                    if dist1 < dist2:
                        nearest_point = (int(x1), int(y1))
                    else:
                        nearest_point = (int(x2), int(y2))

                    result = nearest_point
        
            top10_by_x = sorted(biggest_area, key=lambda p: p[0][0], reverse=True)[:10]
            top10_by_y = sorted(top10_by_x, key=lambda p: p[0][1], reverse=True)[:10]

            vertex = tuple(top10_by_y[0][0])

            output = result if result is not None else vertex

            height, width = cv_image.shape[:2]
            edge_margin = 2

            # Check if on edge
            on_edge = any([
                output[0] <= edge_margin, output[0] >= width - edge_margin,
                output[1] <= edge_margin, output[1] >= height - edge_margin,
            ])

            if self.debug_imshow:
                cv2.imshow("HSV Threshold Hook camera", hsv_thresh_hook)
                cv2.imshow("HSV preview_hook", preview_hook)
                cv2.imshow("HSV Threshold Hook camera after dilation", hsv_thresh_hook_after_dilation)
                cv2.drawContours(cv_image_biggest_area, [biggest_area], -1, (0, 255, 0), 2)
                cv2.imshow("Biggest Area Contour", cv_image_biggest_area)
                cv2.imshow("Grey Threshold Hook", hsv_thresh_hook_gray)
                cv2.imshow("Canny Edges", edges)
                if cv_image_hough is not None:
                    cv2.imshow("Detected Lines", cv_image_hough)
                cv2.waitKey(1)

            if on_edge:
                return None
            else:
                return output
            
        else:
            self.get_logger().warn("No contours found for hook detection.")
            return None

    def init_static_transforms(self, max_retries=10, retry_delay=0.5):
        """
        Initializes and stores static transforms from predefined frame pairs that do not change over time.
        Repeatedly tries to fetch until all are available or max_retries is reached.
        Results are stored as self.A_pos_in_B_frame and self.A_rot_in_B_frame.
        """
        import time
        static_pairs = [
            (self.camera_frame, self.winch_frame),
            (self.winch_frame, self.base_link_frame),
        ]

        now = rclpy.time.Time()
        missing = set(static_pairs)
        attempts = 0

        while missing and attempts < max_retries:
            for A_frame, B_frame in list(missing):
                try:
                    tf = self.tf_buffer.lookup_transform(
                        target_frame=B_frame,
                        source_frame=A_frame,
                        time=now
                    )
                    pos = np.array([
                        tf.transform.translation.x,
                        tf.transform.translation.y,
                        tf.transform.translation.z
                    ])
                    quat = [
                        tf.transform.rotation.x,
                        tf.transform.rotation.y,
                        tf.transform.rotation.z,
                        tf.transform.rotation.w
                    ]
                    rot = Rotation.from_quat(quat).as_matrix()

                    # Extract frame names without robot_name prefix for attribute naming
                    A_name = A_frame.split('/')[-1]
                    B_name = B_frame.split('/')[-1]

                    pos_attr = f"{A_name}_pos_in_{B_name}_frame"
                    rot_attr = f"{A_name}_rot_in_{B_name}_frame"
                    setattr(self, pos_attr, pos)
                    setattr(self, rot_attr, rot)
                    missing.remove((A_frame, B_frame))
                except Exception as e:
                    self.get_logger().warn(f"TF lookup failed for {A_frame} -> {B_frame}: {e}")
            attempts += 1
            if missing:
                time.sleep(retry_delay)

        # Set None for any still missing after retries
        for A_frame, B_frame in missing:
            A_name = A_frame.split('/')[-1]
            B_name = B_frame.split('/')[-1]
            pos_attr = f"{A_name}_pos_in_{B_name}_frame"
            rot_attr = f"{A_name}_rot_in_{B_name}_frame"
            setattr(self, pos_attr, None)
            setattr(self, rot_attr, None)

        if not missing:
            self.get_logger().info("Successfully initialized all static transforms!")
            return True
        else:
            self.get_logger().warn(f"Some static transforms could not be initialized: {missing}")
            return False

    def update_camera_link_winch_link_rotations(self):
        """
        Computes and stores the rotation matrix from camera_link to winch_link frame and vice versa.
        These transforms may change over time and should be updated regularly.
        Results are stored as self.camera_link_rot_in_winch_link_frame and self.winch_link_rot_in_camera_link_frame.
        """
        try:
            now = rclpy.time.Time()
            # Get transform from camera_link to winch_link
            tf = self.tf_buffer.lookup_transform(
                target_frame=self.winch_frame,
                source_frame=self.camera_frame,
                time=now
            )
            quat = [
                tf.transform.rotation.x,
                tf.transform.rotation.y,
                tf.transform.rotation.z,
                tf.transform.rotation.w
            ]
            rot_camera_to_winch = Rotation.from_quat(quat).as_matrix()
            self.camera_link_rot_in_winch_link_frame = rot_camera_to_winch
            # The inverse rotation matrix gives camera to base_link
            self.winch_link_rot_in_camera_link_frame = rot_camera_to_winch.T
        except Exception as e:
            self.get_logger().warn(f"TF lookup failed for camera_link <-> winch_link: {e}")
            self.camera_link_rot_in_winch_link_frame = None
            self.winch_link_rot_in_camera_link_frame = None

    def update_Hook_base_link_positions(self):
        """
        Computes and stores the position vector from Hook to base_link frame.
        This transform may change over time and should be updated regularly.
        Result is stored as self.base_link_rot_in_map_frame and self.map_rot_in_base_link_frame.
        """
        try:
            now = rclpy.time.Time()
            # Get transform from base_link to map
            tf = self.tf_buffer.lookup_transform(
                target_frame=self.base_link_frame,
                source_frame=self.hook_frame,
                time=now
            )
            pos = np.array([
                tf.transform.translation.x,
                tf.transform.translation.y,
                tf.transform.translation.z
            ])
            self.Hook_pos_in_base_link_frame = pos
        except Exception as e:
            self.get_logger().warn(f"TF lookup failed for Hook <-> base_link: {e}")
            self.Hook_pos_in_base_link_frame = None

    def is_in_frame(self, pt, img_w, img_h):
        if pt is None or not (isinstance(pt, (list, tuple, np.ndarray)) and len(pt) == 2):
            return False
        x, y = pt
        return 0 <= x < img_w and 0 <= y < img_h

    def estimate_hook_position(self, tip_cam):
        """
        Estimate the 3D position of the hook in winch frame coordinates using one camera view.
        Stores result in self.est_Hook_pos_in_winch_frame.
        """

        K = np.array([
                    [369.5, 0, 320],
                    [0, 415.69, 240],
                    [0, 0, 1]
                ])
        img_w = int(K[0, 2] * 2)
        img_h = int(K[1, 2] * 2)

        hook_position = []

        if tip_cam is not None and self.is_in_frame(tip_cam, img_w, img_h):
            self.camera_sees_hook.append(True)
            try:
                p_img = np.array(tip_cam)
                R = self.camera_link_rot_in_winch_link_frame
                T = self.camera_link_pos_in_winch_link_frame
                pos = self.reconstruct_hook_position(p_img, K, R, T, self.current_length)
                hook_position.append(pos)
            except Exception as e:
                self.get_logger().warn(f"[Camera] Hook reconstruction failed: {e}")
        else:
            self.camera_sees_hook.append(False)

        # === DECIDE FINAL POSITION ===
        if len(hook_position) == 0:
            self.get_logger().warn("No valid hook detections from camera.")
            self.est_Hook_pos_in_winch_frame = None
        elif len(hook_position) == 1:
            self.est_Hook_pos_in_winch_frame = hook_position[0]
            self.get_logger().info("Hook estimated from a single camera.")

    def draw_hook_info(self, image, tip_rope, window_name='Hook Detection'):
        """
        Draws the hook tip and estimated 3D position (in base_link frame) on the image.

        Args:
            image (np.ndarray): BGR image where to draw.
            tip_rope (tuple or None): (x, y) pixel coordinates of the detected hook tip or None.
        """
        if image is None:
            return

        preview_hook = image.copy()


        if tip_rope is not None:
            # Draw the hook tip as a red filled circle
            cv2.circle(preview_hook, tuple(map(int, tip_rope)), 10, (0, 255, 255), 3)
            text_pos = (int(tip_rope[0] + 10), int(tip_rope[1]))
        else:
            # Default text position if no tip detected
            text_pos = (10, 30)

        # Prepare the position text based on estimated 3D hook position in base_link frame
        if hasattr(self, 'est_Hook_pos_in_base_link_frame') and \
        isinstance(self.est_Hook_pos_in_base_link_frame, np.ndarray) and \
        self.est_Hook_pos_in_base_link_frame.shape == (3,):
            pos = self.est_Hook_pos_in_base_link_frame
            pos_text = f"Position (base_link): ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})"
        else:
            pos_text = "Position (base_link): N/A"

        # Put the position text on the image
        cv2.putText(preview_hook, pos_text, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Show the image window
        cv2.imshow(window_name, preview_hook)
        cv2.waitKey(1)

    def reconstruct_hook_position(self, p_img, K, R, T, L):
        """ Reconstructs the 3D position of the hook from a 2D image point.
        Parameters:
        - p_img: 2D image point (2,)
        - K: Camera intrinsic matrix (3x3)
        - R: Camera rotation matrix (3x3)
        - T: Camera translation vector (3,)
        - L: Rope length (scalar)

        Returns:
        - pos_3d: Reconstructed 3D position(s) of the hook in winch coordinates (up to 2 points)
        """
        # Convert image point to homogeneous coordinates
        p_img_hom = np.array([p_img[0], p_img[1], 1.0])

        # Compute direction of the ray in camera coordinates
        ray_dir_cam = np.linalg.inv(K) @ p_img_hom
        ray_dir_cam = np.array([
                [0, 0, 1],
                [0, 1, 0],
                [1, 0, 0]
            ]) @ ray_dir_cam  # Assuming the camera is rotated to align with winch coordinates

        # Convert ray direction to winch coordinates
        ray_dir_world = R @ ray_dir_cam

        # Camera center in winch coordinates
        C = T

        # The ray: P(s) = C + s * ray_dir_world
        # Intersect with sphere centered at origin (0, 0, 0) with radius L

        a = np.dot(ray_dir_world, ray_dir_world)
        b = 2 * np.dot(ray_dir_world, C)
        c = np.dot(C, C) - L**2

        # Solve quadratic: a*s^2 + b*s + c = 0
        discriminant = b**2 - 4*a*c
        if discriminant < 0:
            raise ValueError("No intersection with the pendulum sphere.")

        sqrt_disc = np.sqrt(discriminant)
        s = (-b + sqrt_disc) / (2*a)

        P = C + s * ray_dir_world
        self.get_logger().info(f"Reconstructed hook position: {P}")

        return P

    def get_actual_frequency_and_dt(self):
        if len(self.est_hook_timestamps) < 2:
            return None, None
        intervals = np.diff(self.est_hook_timestamps)
        avg_dt = np.mean(intervals)
        freq = 1.0 / avg_dt if avg_dt > 0 else 0
        return freq, avg_dt

    def process_hook_estimation(self, msg=None):
        """
        Main hook estimation loop. Must be called repeatedly via timer or update event.
        Requires that self.cv_image is already populated.
        """

        if not self.enabled:
            return

        if self.cv_image is None:
            self.get_logger().warn("No camera images received yet.")
            return

        # Step 1: Estimate hook tip pixel positions
        tip_cam = self.estimate_hook_pixel_position(self.cv_image) if self.cv_image is not None else None

        # Step 2: Update TF transforms
        self.update_camera_link_winch_link_rotations()
        self.update_Hook_base_link_positions()

        # Step 3: Estimate 3D hook position using one or both camera tips
        self.estimate_hook_position(tip_cam)

        self.get_logger().info(f"Estimated hook position in winch frame: {self.est_Hook_pos_in_winch_frame}")

        # Step 4: Initialize EKF if needed
        if self.est_Hook_pos_in_winch_frame is not None:
            self.est_Hook_pos_in_winch_frame_ekf = np.array([
                                                    [0, 1, 0],
                                                    [-1, 0, 0],
                                                    [0, 0, 1]
                                                ]) @ self.est_Hook_pos_in_winch_frame
            try:
                # ======= EKF Initialization (once) =======
                if not self.ekf_initialized:
                    try:
                        pos = np.array(self.est_Hook_pos_in_winch_frame_ekf, dtype=float)
                        if pos.shape == (3,):
                            self.ekf.x[0:3] = pos.flatten()
                            self.ekf.x[3:6] = np.zeros(3)
                            # angles = self.cartesian_to_spherical(pos)
                            # self.ekf.x = np.array([angles[0], angles[1], 0.0, 0.0])
                            self.ekf_initialized = True
                            self.get_logger().info("EKF initialized with first hook position.")
                            self.get_logger().info(f"EKF initial value: {self.ekf.x}")
                        else:
                            self.get_logger().warn(f"Invalid hook position shape during EKF init: {pos.shape}")
                    except Exception as e:
                        self.get_logger().warn(f"EKF initialization failed: {e}")
            except Exception as e:
                self.get_logger().warn(f"Error during EKF initialization: {e}")
                self.ekf_initialized = False

        
        # Step 5: EKF prediction/update
        now = self.get_clock().now()

        if self.last_ekf_time is None:
            self.last_ekf_time = now
            self.est_hook_timestamps.append(now.nanoseconds * 1e-9)
            dt = now.nanoseconds * 1e-9

        dt = (now - self.last_ekf_time).nanoseconds * 1e-9
        self.last_ekf_time = now

        # Always append timestamp for plotting
        self.est_hook_timestamps.append(now.nanoseconds * 1e-9)

        meas = (
                np.array(self.est_Hook_pos_in_winch_frame_ekf).reshape(3, 1)
                if self.est_Hook_pos_in_winch_frame_ekf is not None and not np.isnan(self.est_Hook_pos_in_winch_frame_ekf).any()
                else None
                )

        try:
            if meas is not None:
                self.update_ekf_constrained(dt, self.a_world, meas)
            else:
                self.predict_ekf_constrained(dt, self.a_world)
        except Exception as e:
            self.get_logger().warn(f"EKF update failed: {e}")


        self.get_logger().info(f"self.ekf_Hook_pos_in_winch_frame: {self.ekf_Hook_pos_in_winch_frame}")

        # Step 6: Transform hook position to base_link frame
        try:
            pos_winch = self.est_Hook_pos_in_winch_frame  # shape (3,)
            rot_winch_in_base = getattr(self, "winch_link_rot_in_base_link_frame", None)
            pos_winch_in_base = getattr(self, "winch_link_pos_in_base_link_frame", None)
        except Exception as e:
            self.get_logger().warn(f"Error transforming hook position to base_link: {e}")
            self.est_Hook_pos_in_base_link_frame = np.array([np.nan, np.nan, np.nan])
            self.ekf_Hook_pos_in_base_link_frame = np.array([np.nan, np.nan, np.nan])

        if self.est_Hook_pos_in_winch_frame is not None and not np.isnan(self.est_Hook_pos_in_winch_frame).any() and rot_winch_in_base is not None and pos_winch_in_base is not None:
            self.est_Hook_pos_in_base_link_frame = rot_winch_in_base @ pos_winch + pos_winch_in_base
            self.est_Hook_pos_in_base_link_frame = np.array([
                                                            [0, 1, 0],
                                                            [-1, 0, 0],
                                                            [0, 0, 1]
                                                        ]) @ self.est_Hook_pos_in_base_link_frame
        else:
            self.est_Hook_pos_in_base_link_frame = np.array([np.nan, np.nan, np.nan])

                
        if not np.isnan(self.ekf_Hook_pos_in_winch_frame).any() and rot_winch_in_base is not None and pos_winch_in_base is not None:
            self.ekf_Hook_pos_in_base_link_frame = rot_winch_in_base @ self.ekf_Hook_pos_in_winch_frame + pos_winch_in_base
        else:
            self.ekf_Hook_pos_in_base_link_frame = np.array([np.nan, np.nan, np.nan])

        # Step 5: Save positions for plotting
        if self.Hook_pos_in_base_link_frame is None:
            self.Hook_pos_in_base_link_frame = np.array([np.nan, np.nan, np.nan])
        self.Hook_pos_in_base_link_frame_to_plot.append(list(self.Hook_pos_in_base_link_frame))
        self.est_Hook_pos_in_base_link_frame_to_plot.append(list(self.est_Hook_pos_in_base_link_frame))
        self.ekf_Hook_pos_in_base_link_frame_to_plot.append(list(self.ekf_Hook_pos_in_base_link_frame))

        # Step 6: Draw hook info on images if available
        if self.enable_visualization and self.cv_image is not None:
            self.draw_hook_info(self.cv_image, tip_cam, 'Camera Hook Detection')

        # Step 7: Publish hook positions
        self.publish_hook_positions()


    def odom_callback(self, msg: Odometry):
        # Extract linear velocity in body frame
        linear_vel = msg.twist.twist.linear
        current_vel = np.array([linear_vel.x, linear_vel.y, linear_vel.z])

        # Calculate acceleration as difference in velocity over time
        current_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

        if not hasattr(self, 'prev_vel'):
            self.prev_vel = current_vel
            self.prev_time = current_time
            self.a_base_link = np.zeros(3)
        else:
            dt = current_time - self.prev_time if current_time > self.prev_time else 1e-3
            self.a_base_link = (current_vel - self.prev_vel) / dt
            self.prev_vel = current_vel
            self.prev_time = current_time

        # Smooth acceleration with simple moving average
        if not hasattr(self, 'smoothed_accel') or self.smoothed_accel is None:
            self.smoothed_accel = self.a_base_link.copy()
        else:
            alpha = 0.2
            self.smoothed_accel = alpha * self.a_base_link + (1 - alpha) * self.smoothed_accel

        # Extract quaternion (x, y, z, w)
        q = msg.pose.pose.orientation
        quat = [q.x, q.y, q.z, q.w]

        # Create rotation from quaternion (body -> world)
        r = Rotation.from_quat(quat)

        # Rotate smoothed acceleration from body frame to world frame
        self.a_world = r.apply(self.smoothed_accel)

        # Now self.a_world holds acceleration in the world frame

    def fx(self, x, dt, a_drone):
        x = np.asarray(x).flatten()
        p = x[0:3]
        v = x[3:6]
        a_eff = self.g_vec - a_drone

        # Remove radial component of acceleration to stay on sphere
        acc = a_eff - np.dot(a_eff, p) / (np.linalg.norm(p)**2 + 1e-6) * p

        new_v = v + acc * dt
        new_p = p + new_v * dt
        return np.concatenate((new_p, new_v))

    def jacobian_F(self, x, dt, a_drone):
        F = np.eye(6)
        F[0:3, 3:6] = np.eye(3) * dt
        return F

    def hx(self, x):
        return x[0:3]

    def project_to_sphere(self, x, L):
        p = x[0:3].flatten()
        v = x[3:6].flatten()

        norm_p = np.linalg.norm(p)
        if norm_p > 1e-3:
            p_proj = p / norm_p * L
            v_proj = v - (np.dot(v, p_proj) / (L ** 2)) * p_proj
        else:
            p_proj = p
            v_proj = v

        return np.concatenate((p_proj, v_proj)).flatten()

    def project_covariance(self, P, x, L):
        p = x[0:3].flatten()
        norm_p = np.linalg.norm(p)
        if norm_p < 1e-3:
            return P

        p_unit = p / norm_p
        T = np.eye(3) - np.outer(p_unit, p_unit)

        P_proj = P.copy()
        P_proj[0:3, 0:3] = T @ P[0:3, 0:3] @ T.T
        P_proj[0:3, 3:6] = T @ P[0:3, 3:6]
        P_proj[3:6, 0:3] = P_proj[0:3, 3:6].T
        return P_proj

    # Prediction Only
    def predict_ekf(self, dt, a_drone):
        self.ekf.F = self.jacobian_F(self.ekf.x, dt, a_drone)
        self.ekf.x = self.fx(self.ekf.x, dt, a_drone)
        self.ekf.P = self.ekf.F @ self.ekf.P @ self.ekf.F.T + self.ekf.Q

        self.ekf_Hook_pos_in_winch_frame = self.ekf.x[0:3].copy()

    def predict_ekf_constrained(self, dt, a_drone):
        self.predict_ekf(dt, a_drone)
        self.ekf.x = self.project_to_sphere(self.ekf.x, self.current_length)
        self.ekf.P = self.project_covariance(self.ekf.P, self.ekf.x, self.current_length)

        self.ekf_Hook_pos_in_winch_frame = self.ekf.x[0:3].copy()
        self.get_logger().info(f"self.ekf_Hook_pos_in_winch_frame: {self.ekf_Hook_pos_in_winch_frame}")

    # Predict + Update (with measurement)
    def update_ekf(self, dt, a_drone, measurement):
        self.predict_ekf(dt, a_drone)

        H = np.hstack((np.eye(3), np.zeros((3, 3))))
        z = measurement.flatten()
        hx = self.hx(self.ekf.x).flatten()
        y = z - hx
        S = H @ self.ekf.P @ H.T + self.ekf.R
        K = self.ekf.P @ H.T @ np.linalg.inv(S)
        self.ekf.x = self.ekf.x + K @ y
        self.ekf.P = (np.eye(6) - K @ H) @ self.ekf.P

        self.ekf_Hook_pos_in_winch_frame = self.ekf.x[0:3].copy()

    def update_ekf_constrained(self, dt, a_drone, measurement):
        self.predict_ekf_constrained(dt, a_drone)

        H = np.hstack((np.eye(3), np.zeros((3, 3))))
        z = measurement.flatten()
        hx = self.hx(self.ekf.x).flatten()
        y = z - hx
        S = H @ self.ekf.P @ H.T + self.ekf.R
        K = self.ekf.P @ H.T @ np.linalg.inv(S)
        self.ekf.x = self.ekf.x + K @ y
        self.ekf.P = (np.eye(6) - K @ H) @ self.ekf.P

        self.ekf.x = self.project_to_sphere(self.ekf.x, self.current_length)
        self.ekf.P = self.project_covariance(self.ekf.P, self.ekf.x, self.current_length)

        self.ekf_Hook_pos_in_winch_frame = self.ekf.x[0:3].copy()

    
    def publish_hook_positions(self):
        now = self.get_clock().now().to_msg()
        # Estimated position
        est_msg = PointStamped()
        est_msg.header.stamp = now
        est_msg.header.frame_id = self.base_link_frame
        est = self.est_Hook_pos_in_base_link_frame
        if est is not None and not np.isnan(est).any():
            est_msg.point.x = float(est[0])
            est_msg.point.y = float(est[1])
            est_msg.point.z = float(est[2])
            self.est_hook_pub.publish(est_msg)
        # EKF position
        ekf_msg = PointStamped()
        ekf_msg.header.stamp = now
        ekf_msg.header.frame_id = self.base_link_frame
        ekf = self.ekf_Hook_pos_in_base_link_frame
        if ekf is not None and not np.isnan(ekf).any():
            ekf_msg.point.x = float(ekf[0])
            ekf_msg.point.y = float(ekf[1])
            ekf_msg.point.z = float(ekf[2])
            self.ekf_hook_pub.publish(ekf_msg)



    def enable_callback(self, request, response):
        self.enabled = True
        response.success = True
        response.message = "Hook estimator enabled."
        self.get_logger().info(response.message)
        return response

    def disable_callback(self, request, response):
        self.enabled = False
        response.success = True
        response.message = "Hook estimator disabled."
        self.get_logger().info(response.message)
        return response




    def _align_arrays(self, *arrays):
        """
        Aligns arrays (3D vectors or scalars) to the same length by padding with NaNs.
        Handles empty arrays safely.
        """
        cleaned = []
        is_vector = []

        for arr in arrays:
            valid_rows = []
            for item in arr:
                if isinstance(item, (list, tuple, np.ndarray)) and len(item) == 3:
                    try:
                        valid_rows.append([float(x) for x in item])
                    except (ValueError, TypeError):
                        continue
                elif isinstance(item, (int, float, np.float64)):
                    valid_rows.append(float(item))
            cleaned.append(valid_rows)
            is_vector.append(len(valid_rows) > 0 and isinstance(valid_rows[0], list))

        max_len = max(len(arr) for arr in cleaned)
        padded = []

        for arr, vec in zip(cleaned, is_vector):
            pad_value = [np.nan, np.nan, np.nan] if vec else np.nan
            padded_arr = arr + [pad_value] * (max_len - len(arr))
            padded.append(padded_arr)

        return tuple(np.array(arr) for arr in padded)

    def plot_base_link_hook_trajectory(self, save_dir='plots'):
        if not self.enable_visualization:
            self.get_logger().info("Visualization disabled, skipping plotting.")
            return

        self.get_logger().info("Called plot_base_link_hook_trajectory")
        
        # Log lengths of plot data
        self.get_logger().info(
            f"Timestamps: {len(self.est_hook_timestamps)}, "
            f"Hook: {len(self.Hook_pos_in_base_link_frame_to_plot)}, "
            f"Est Hook: {len(self.est_Hook_pos_in_base_link_frame_to_plot)}, "
            f"EKF Hook: {len(self.ekf_Hook_pos_in_base_link_frame_to_plot)}"
        )

        try:
            aligned = self._align_arrays(
                self.est_hook_timestamps,
                self.Hook_pos_in_base_link_frame_to_plot,
                self.est_Hook_pos_in_base_link_frame_to_plot,
                self.ekf_Hook_pos_in_base_link_frame_to_plot
            )
            t, gt, est, ekf = aligned

            self.get_logger().info(
                f"Aligned arrays - Time: {len(t)}, GT: {len(gt)}, Est: {len(est)}, EKF: {len(ekf)}"
            )

            os.makedirs(save_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(save_dir, f'base_link_trajectory_{timestamp}.png')
            self.get_logger().info(f"Saving base_link plot to: {filename}")

            plt.figure(figsize=(12, 6))
            for i, label in enumerate(['X', 'Y', 'Z']):
                plt.subplot(3, 1, i + 1)
                plt.plot(t, gt[:, i], 'b-', label='Ground Truth' if i == 0 else "")
                plt.plot(t, est[:, i], 'r--', label='Estimated' if i == 0 else "")
                plt.plot(t, ekf[:, i], 'g-.', label='EKF' if i == 0 else "")
                plt.ylabel(f'{label} [m]')
                plt.grid(True)
                if i == 0:
                    plt.legend()

            plt.xlabel('Time [s]')
            plt.suptitle('Hook Position in Base Link Frame')
            plt.tight_layout()
            plt.savefig(filename)
            self.get_logger().info(f"Saved base_link plot to: {filename}")
            plt.close()

        except Exception as e:
            self.get_logger().error(f"Failed to plot base_link trajectory: {e}")


    def compute_base_link_rmse(self):
        """
        Computes the mean squared error (MSE) between ground truth and estimated,
        and ground truth and EKF hook positions in base_link frame, for each axis (x, y, z).
        Uses the _to_plot arrays.
        Returns:
            mse_est (np.ndarray): MSE between gt and est for each axis [x, y, z]
            mse_ekf (np.ndarray): MSE between gt and ekf for each axis [x, y, z]
        """
        # Align arrays and convert to numpy
        aligned = self._align_arrays(
            self.est_hook_timestamps,
            self.Hook_pos_in_base_link_frame_to_plot,
            self.est_Hook_pos_in_base_link_frame_to_plot,
            self.ekf_Hook_pos_in_base_link_frame_to_plot
        )
        t, gt, est, ekf = aligned

        # Only use valid (non-nan) rows for error computation
        valid_mask = ~np.isnan(gt).any(axis=1) & ~np.isnan(est).any(axis=1) & ~np.isnan(ekf).any(axis=1)
        gt_valid = gt[valid_mask]
        est_valid = est[valid_mask]
        ekf_valid = ekf[valid_mask]

        if len(gt_valid) == 0:
            self.get_logger().warn("No valid odom data for MSE computation.")
            return None, None

        # Compute per-axis MSE
        mse_est = np.mean((gt_valid - est_valid) ** 2, axis=0)  # Shape: (3,) for x, y, z
        mse_ekf = np.mean((gt_valid - ekf_valid) ** 2, axis=0)  # Shape: (3,) for x, y, z

        # Square root to get RMSE
        rmse_est = np.sqrt(mse_est)
        rmse_ekf = np.sqrt(mse_ekf)

        self.get_logger().info(
            f"Base_link RMSE (GT vs EST) [x, y, z]: {rmse_est}, Base_link RMSE (GT vs EKF) [x, y, z]: {rmse_ekf}"
        )

        return rmse_est, rmse_ekf


    def destroy_node(self):
        if self.enable_visualization:
            # Log MSE results at shutdown
            rmse_est, rmse_ekf = self.compute_base_link_rmse()
            self.get_logger().info("\n=== Final Results ===")
            self.get_logger().info(f"Base_link RMSE (GT vs EST): {rmse_est}")
            self.get_logger().info(f"Base_link RMSE (GT vs EKF): {rmse_ekf}")
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = hook_estimator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down node (Ctrl+C detected)")
    finally:
        if node.enable_visualization:
            node.plot_base_link_hook_trajectory()
        node.get_logger().info("Cleaning up...")
        node.destroy_node()
        rclpy.shutdown()



if __name__ == '__main__':
    main()
