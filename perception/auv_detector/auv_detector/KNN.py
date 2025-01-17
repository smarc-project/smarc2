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
import auv_detector.params_detector as P

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

        if(P.REALDATA) :
            self.subscription = self.create_subscription(
                Image,
                f"/{self.robot_name}/{self.realdata_topic}",
                self.listener_callback,            
                10)
        else:
            self.subscription = self.create_subscription(
                Image,
                f"/{self.robot_name}/{DroneTopics.CAMERA_DATA_TOPIC}",
                self.listener_callback,            
                10)
        self.subscription
        self.bridge = CvBridge()
        self.mask_publisher = self.create_publisher(Image, f"/{self.robot_name}/{DroneTopics.CAMERA_PROCESSED_TOPIC}", 10)
        # self.foreground_publisher = self.create_publisher(Image, 'Quadrotor/core/fpcamera/image_foreground', 10)
        # self.detection_publisher = self.create_publisher(Image, 'Quadrotor/core/fpcamera/image_detection', 10)
        self.buoy_pub = self.create_publisher(Float32MultiArray, f"/{self.robot_name}/{ DroneTopics.BUOY_DETECTOR_ESTIMATE_TOPIC}", 10)
        self.sam_lowest_pub = self.create_publisher(Float32MultiArray, f"/{self.robot_name}/{ DroneTopics.SAM_LOWEST_POINT_ESTIMATE_TOPIC}", 10)
        
        self.knn = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=self.knn_lowerbound,detectShadows=False)

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
        

        # Apply the connected component filtering
        filtered_mask = self.remove_small_blobs_connected_components(foreground_mask, min_area=self.min_area_filter, max_area=self.max_area_filter)
        masked_image = cv2.bitwise_and(cv_image, cv_image, mask=filtered_mask)
        avg_rgb = cv2.mean(masked_image, mask=filtered_mask)
        self.get_logger().info(f"average rgb : {avg_rgb}")  #BGR
        # # Display the mask from KNN
        cv2.imshow('Detected Foreground', filtered_mask)
        cv2.waitKey(1)
        # Apply morphological operations to remove noise and fill gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        foreground_mask = cv2.morphologyEx(filtered_mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(filtered_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        min_area = 0  # Minimum area threshold to consider a contour
        large_contours = [c for c in contours if cv2.contourArea(c) > min_area]

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
                    cv_image = cv2.line(cv_image, pt1, pt2, (255, 0, 0), 2)

            elif self.data_association(cnt, filtered_mask, cv_image) == self.buoy_name:
                # Get any point from the contour (e.g., the first point)
                point = cnt[0][0]  # This is the first point in the contour, it could be any point from the contour

                # Draw a circle at the selected point (using a radius of 5 and color green for visibility)
                cv_image = cv2.circle(cv_image, (point[0], point[1]), radius=5, color=(0, 255, 0), thickness=-1)  # Green dot

                # Publish the point (as a Float32MultiArray)
                buoy_position_msg = Float32MultiArray()
                buoy_position_msg.data = [float(point[0]), float(point[1])]  # Publish the coordinates of the point
                self.buoy_pub.publish(buoy_position_msg)


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
        orange_percentage = self.get_orange_percentage(contour_mask, cv_image, np.uint8([[self.buoy_color]]))
        # yellow_percentage = self.get_yellow_percentage(contour_mask, cv_image, lower_yellow, upper_yellow)
        yellow_percentage = self.get_yellow_percentage(contour_mask, cv_image, np.uint8([[self.sam_color]]))

        # # Print the yellow percentage for tuning
        self.get_logger().info(f'Yellow percentage: {yellow_percentage:.2f}%')
        self.get_logger().info(f'Orange percentage: {orange_percentage:.2f}%')
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

                        self.get_logger().info(f"all tests satisfied")
                        return self.auv_name
                    else :
                        # cv2.drawContours(cv_image, [cnt], -1, (0, 0, 255), thickness=cv2.FILLED)
                        self.get_logger().info(f"aspect ratio test not satisfied : {aspect_ratio}")
                # else :
            #         # cv2.drawContours(cv_image, [cnt], -1, (0, 0, 255), thickness=cv2.FILLED)
            #         self.get_logger().info("yellow pixel test not satisfied")
            else : 
                self.get_logger().info(f"area test not satisfied : {cv2.contourArea(cnt)}")
        else : 
            self.get_logger().info(f"color threshold test  not satisfied : {yellow_percentage}")
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
            self.get_logger().info("_____________________________________________")
            # Loop over each connected component
            for i in range(1, num_labels):  # Start from 1 to skip the background
                area = stats[i, cv2.CC_STAT_AREA]

                # Filter based on the area
 
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