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

class KNN(Node):
    def __init__(self):
        super().__init__('k_nearest_neighbors')
        # ===== Declare parameters =====
        self.declare_node_parameters()

        # ===== Get parameters =====
        self.robot_name = self.get_parameter("robot_name").value


        self.subscription = self.create_subscription(
            Image,
            f"/{self.robot_name}/{DroneTopics.CAMERA_DATA_TOPIC}",
            self.listener_callback,            
            10)
        self.subscription
        self.bridge = CvBridge()
        self.mask_publisher = self.create_publisher(Image, 'Quadrotor/core/fpcamera/image_processed', 10)
        # self.foreground_publisher = self.create_publisher(Image, 'Quadrotor/core/fpcamera/image_foreground', 10)
        # self.detection_publisher = self.create_publisher(Image, 'Quadrotor/core/fpcamera/image_detection', 10)
        self.buoy_pub = self.create_publisher(Float32MultiArray, f"/{self.robot_name}/{ DroneTopics.BUOY_DETECTOR_ESTIMATE_TOPIC}", 10)
        
        
        self.knn = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=1000,detectShadows=False)

    def declare_node_parameters(self):
        """
        Declare the node parameters for the AUV position estimator node.
        """
        self.declare_parameter("robot_name", "Quadrotor")
        
    def listener_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

        # Apply the MOG2 algorithm to get the foreground mask
        foreground_mask = self.knn.apply(cv_image)

        # Apply the connected component filtering
        filtered_mask = self.remove_small_blobs_connected_components(foreground_mask, min_area=700, max_area=4000)

        # Apply morphological operations to remove noise and fill gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        foreground_mask = cv2.morphologyEx(filtered_mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(filtered_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        min_area = 130  # Minimum area threshold to consider a contour
        large_contours = [c for c in contours if cv2.contourArea(c) > min_area]

        for cnt in large_contours:

            # Data Association
            if self.data_association(cnt, filtered_mask, cv_image):
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

                best_deg = 1
                min_error = float('inf')
                best_p1 = None
                best_p2 = None

                for i in range(1, 10):
                    # Fit ith degree polynomial to x(t) and y(t)
                    p1 = np.poly1d(np.polyfit(t, x, i))
                    p2 = np.poly1d(np.polyfit(t, y, i))
                    
                    # Calculate the fit errors
                    x_poly = p1(t)
                    y_poly = p2(t)
                    error = np.linalg.norm(x_poly - x) + np.linalg.norm(y_poly - y)
                    
                    # Update the best polynomial if error is smaller
                    if error < min_error:
                        min_error = error
                        best_deg = i
                        best_p1 = p1
                        best_p2 = p2

                # Generate fitted points
                t_fit = np.linspace(0, 1, 100)
                x_fit = best_p1(t_fit)
                y_fit = best_p2(t_fit)

                # First derivatives
                dx_dt = best_p1.deriv()(t_fit)
                dy_dt = best_p2.deriv()(t_fit)

                # Magnitude of the derivative at each point
                derivative_magnitude = np.sqrt(dx_dt**2 + dy_dt**2)

                # Find the index of the maximum magnitude
                max_derivative_index = np.argmin(derivative_magnitude)
                # max_derivative_index = np.argmax(derivative_magnitude)

                max_x = x_fit[max_derivative_index]
                max_y = y_fit[max_derivative_index]

                # Rotate the fitted polynomial back to the original coordinate system
                fitted_points = np.vstack((x_fit, y_fit)).T
                original_fitted_points = pca.inverse_transform(fitted_points)

                # Highlight the point with the highest derivative magnitude
                max_point = pca.inverse_transform([[max_x, max_y]])[0]
                cv_image = cv2.circle(cv_image, tuple(max_point.astype(int)), 5, (0, 255, 0), -1)  # Green dot for max derivative
                # Publish the minimum gradient point
                min_gradient_msg = Float32MultiArray()
                min_gradient_msg.data = [max_point[0], max_point[1]]
                self.buoy_pub.publish(min_gradient_msg)    

                # Draw the fitted curve on the image
                for i in range(len(original_fitted_points) - 1):
                    pt1 = tuple(original_fitted_points[i].astype(int))
                    pt2 = tuple(original_fitted_points[i + 1].astype(int))
                    cv_image = cv2.line(cv_image, pt1, pt2, (255, 0, 0), 2)

        # Publish the processed mask
        mask_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding="bgr8")
        self.mask_publisher.publish(mask_msg)
        
        # Display the point where we guess the buoy is
        cv2.imshow('Curve and Min gradeint Lowest Point', cv_image)
        cv2.waitKey(1)

        # Display the mask from KNN
        cv2.imshow('Detected Foreground', filtered_mask)
        cv2.waitKey(1)


    def data_association(self, cnt, filtered_mask, cv_image):
        # Define the yellow range in HSV (adjust these as needed)
        lower_yellow = np.array([23, 125, 125], dtype=np.uint8)
        upper_yellow = np.array([30, 255, 255], dtype=np.uint8)

        # lower_yellow1 = np.array([20, 100, 100], dtype=np.uint8)  # Even higher S & V to exclude dull colors
        # upper_yellow1 = np.array([27, 180, 180], dtype=np.uint8)

        lower_yellow1 = np.array([25, 150, 150], dtype=np.uint8)  # Even higher S & V to exclude dull colors
        upper_yellow1 = np.array([30, 255, 255], dtype=np.uint8)

        # Step 1: Calculate the yellow percentage in the contour
        contour_mask = np.zeros_like(filtered_mask)
        cv2.drawContours(contour_mask, [cnt], -1, 255, thickness=cv2.FILLED)
        yellow_percentage = self.get_yellow_percentage(contour_mask, cv_image, lower_yellow, upper_yellow)

        # # Print the yellow percentage for tuning
        self.get_logger().info(f'Yellow percentage: {yellow_percentage:.2f}%')

        # Step 2: Proceed only if the yellow percentage is high enough
        if yellow_percentage > 10:  # Liberal threshold, you can adjust this
            
            # Apply the yellow mask to the contour
            yellow_mask = self.mask_yellow_regions(cv_image, lower_yellow1, upper_yellow1)

            # Combine the contour mask with the yellow mask (logical AND)
            contour_yellow_mask = cv2.bitwise_and(yellow_mask, contour_mask)

            # Check if there are any yellow pixels in the contour
            if np.sum(contour_yellow_mask) > 0:  # Ensure there are yellow pixels to proceed
               
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
                    if 0 < aspect_ratio < 0.3:  # Adjust as needed
                        # self.get_logger().info('Contour meets aspect ratio criteria')
                        # Visualize the contour and the minAreaRect box
                        cv2.drawContours(cv_image, [box], -1, (0, 255, 0), 2)

                        # Display the contour yellow mask REDUNDANT
                        # cv2.imshow('Yellow Contour Mask', contour_yellow_mask)
                        # cv2.waitKey(1)
                        return True
                    else :
                        self.get_logger().info(f"aspect ratio test not satisfied : {aspect_ratio}")
            else :
                self.get_logger().info("yellow pixel test not satisfied")
        else : 
            self.get_logger().info(f"color threshold test  not satisfied : {yellow_percentage}")
        return False

    
    # Step 1: yellow regions percentage
    def get_yellow_percentage(self, mask, image, lower_yellow, upper_yellow):
        # Apply mask to the image
        masked_image = cv2.bitwise_and(image, image, mask=mask)

        # Convert the image to HSV color space
        hsv_image = cv2.cvtColor(masked_image, cv2.COLOR_BGR2HSV)

        # Create a mask for the yellow color
        yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)

        # Calculate the number of yellow pixels
        yellow_pixels = np.sum(yellow_mask == 255)

        # Calculate the total number of pixels in the contour
        total_pixels = np.sum(mask == 255)

        # Calculate the percentage of yellow pixels
        yellow_percentage = (yellow_pixels / total_pixels) * 100 if total_pixels > 0 else 0

        return yellow_percentage

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
    

    def remove_small_blobs_connected_components(self, foreground_mask, min_area=50, max_area=3000):
            # Find all connected components in the mask
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(foreground_mask)

            # Create a blank mask
            filtered_mask = np.zeros_like(foreground_mask)
            self.get_logger().info("_____________________________________________")
            # Loop over each connected component
            for i in range(1, num_labels):  # Start from 1 to skip the background
                area = stats[i, cv2.CC_STAT_AREA]

                # Filter based on the area
                # print(area) 
                if min_area < area < max_area:
                    self.get_logger().info(f"area :{area}") 
                    filtered_mask[labels == i] = 255

            return filtered_mask    

def main(args=None):
    rclpy.init(args=args)
    k_nearest_neighbors = KNN()
    rclpy.spin(k_nearest_neighbors)
    k_nearest_neighbors.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()