# import rclpy
# from rclpy.node import Node
# import cv2
# import numpy as np
# from cv_bridge import CvBridge, CvBridgeError
# from sensor_msgs.msg import Image
# from geometry_msgs.msg import Point
# import random

# class Particle:
#     def __init__(self, x, y, weight):
#         self.x = x
#         self.y = y
#         self.weight = weight

# def initialize_particles(num_particles, frame_shape):
#     particles = []
#     height, width, _ = frame_shape
#     for _ in range(num_particles):
#         x = random.uniform(0, width)
#         y = random.uniform(0, height)
#         particles.append(Particle(x, y, 1.0 / num_particles))
#     return particles

# def predict_particles(particles, frame_shape, std_dev=5.0):
#     height, width, _ = frame_shape
#     for particle in particles:
#         particle.x += np.random.normal(0, std_dev)
#         particle.y += np.random.normal(0, std_dev)
#         particle.x = np.clip(particle.x, 0, width - 1)
#         particle.y = np.clip(particle.y, 0, height - 1)
#     return particles

# def calculate_weights(frame, particles):
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#     lower_yellow = np.array([20, 100, 100])
#     upper_yellow = np.array([30, 255, 255])
#     mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

#     total_weight = 0.0
#     for particle in particles:
#         x, y = int(particle.x), int(particle.y)
#         if x < frame.shape[1] and y < frame.shape[0] and mask[y, x] > 0:
#             particle.weight = 1.0
#         else:
#             particle.weight = 0.1  # Small weight for particles not matching the color
#         total_weight += particle.weight

#     # Normalize weights
#     for particle in particles:
#         particle.weight /= total_weight

#     return particles

# # def resample_particles(particles):
# #     cumulative_sum = np.cumsum([p.weight for p in particles])
# #     cumulative_sum[-1] = 1.0  # Ensure sum is exactly one
# #     indexes = np.searchsorted(cumulative_sum, np.random.rand(len(particles)))

# #     particles = [particles[i] for i in indexes]
# #     return particles

# def resample_particles(particles):
#     num_particles = len(particles)
#     weights = [p.weight for p in particles]

#     # Compute the cumulative sum of weights
#     cumulative_sum = np.cumsum(weights)

#     # Generate random offset for systematic resampling
#     random_offset = np.random.rand() * (1.0 / num_particles)

#     # Initialize the resampled particles
#     resampled_particles = []

#     # Resample particles
#     for i in range(num_particles):
#         sample_index = (i + random_offset) % num_particles
#         while cumulative_sum[sample_index] < (i / num_particles):
#             sample_index = (sample_index + 1) % num_particles
#         resampled_particles.append(copy.deepcopy(particles[sample_index]))

#     # Reset weights for resampled particles
#     for p in resampled_particles:
#         p.weight = 1.0 / num_particles

#     return resampled_particles


# def estimate_position(particles):
#     x_est = np.mean([p.x for p in particles])
#     y_est = np.mean([p.y for p in particles])
#     return x_est, y_est

# class AUVPositionPublisher(Node):
#     def __init__(self):
#         super().__init__('auv_position_publisher')
#         self.bridge = CvBridge()
#         self.image_sub = self.create_subscription(Image, '/Quadrotor/drone/fpcam/image_raw', self.image_callback, 10)
#         self.position_pub = self.create_publisher(Point, "/Quadrotor/drone/fpcam/position", 10)
#         self.annotated_image_pub = self.create_publisher(Image, "/Quadrotor/drone/fpcam/annotated_image", 10)
#         self.particles = []
#         self.initialized = False

#     def image_callback(self, data):
#         try:
#             cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
#         except CvBridgeError as e:
#             self.get_logger().error(f"CvBridge Error: {e}")
#             return

#         if not self.initialized:
#             self.particles = initialize_particles(100, cv_image.shape)
#             self.initialized = True

#         # Perform multiple iterations of prediction, update, and resampling
#         num_iterations = 5
#         for _ in range(num_iterations):
#             # Prediction step with Gaussian noise
#             self.particles = predict_particles(self.particles, cv_image.shape)

#             # Update step based on observed data
#             self.particles = calculate_weights(cv_image, self.particles)

#             # Resampling step to focus on high-probability areas
#             self.particles = resample_particles(self.particles)
#         x_est, y_est = estimate_position(self.particles)

#         # Publish estimated position
#         position_msg = Point()
#         position_msg.x = float(x_est)
#         position_msg.y = float(y_est)
#         position_msg.z = 0.0  # Ensure z is a float
#         self.position_pub.publish(position_msg)

#         # Annotate the image with the estimated position
#         annotated_image = cv_image.copy()
#         cv2.circle(annotated_image, (int(x_est), int(y_est)), 5, (0, 255, 0), -1)  # Draw a green dot at the estimated position
#         try:
#             annotated_image_msg = self.bridge.cv2_to_imgmsg(annotated_image, "bgr8")
#             self.annotated_image_pub.publish(annotated_image_msg)
#         except CvBridgeError as e:
#             self.get_logger().error(f"CvBridge Error: {e}")

# def main(args=None):
#     rclpy.init(args=args)
#     node = AUVPositionPublisher()
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         pass
#     node.destroy_node()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()


# import rclpy
# from rclpy.node import Node
# import cv2
# import numpy as np
# from cv_bridge import CvBridge, CvBridgeError
# from sensor_msgs.msg import Image
# from std_msgs.msg import Float32
# from random import uniform

# class Particle:
#     def __init__(self, x, y, weight):
#         self.x = x
#         self.y = y
#         self.weight = weight

# def initialize_particles(num_particles, img_shape):
#     particles = []
#     for _ in range(num_particles):
#         x = uniform(0, img_shape[1])  # width
#         y = uniform(0, img_shape[0])  # height
#         particles.append(Particle(x, y, 1.0 / num_particles))
#     return particles

# def predict_particles(particles, img_shape, sigma=1):
#     for p in particles:
#         p.x += np.random.normal(0, sigma)
#         p.y += np.random.normal(0, sigma)
#         p.x = np.clip(p.x, 0, img_shape[1] - 1)
#         p.y = np.clip(p.y, 0, img_shape[0] - 1)
#     return particles

# # def calculate_weights(image, particles, lower_yellow, upper_yellow):
# #     hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
# #     for p in particles:
# #         color = hsv[int(p.y), int(p.x)]
# #         if lower_yellow[0] <= color[0] <= upper_yellow[0] and lower_yellow[1] <= color[1] <= upper_yellow[1] and lower_yellow[2] <= color[2] <= upper_yellow[2]:
# #             p.weight = 1.0
# #         else:
# #             p.weight = 1/(len(particles)+1)

# #     # Normalize weights
# #     total_weight = sum([p.weight for p in particles])
# #     for p in particles:
# #         p.weight /= total_weight
# #     return particles
# def calculate_weights(image, particles, lower_yellow, upper_yellow):
#     hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
#     mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
#     # Get coordinates of yellow points
#     yellow_points = set(tuple(p) for p in np.argwhere(mask > 0))
    
#     for p in particles:
#         if (int(p.y), int(p.x)) in yellow_points:
#             p.weight = 1.0
#         else:
#             p.weight = 1 / (len(particles) + 1)

#     # Normalize weights
#     total_weight = sum([p.weight for p in particles])
#     for p in particles:
#         p.weight /= total_weight
        
#     return particles

# def estimate_position(particles):
#     x_est = sum([p.x * p.weight for p in particles])
#     y_est = sum([p.y * p.weight for p in particles])
#     return x_est, y_est

# def stratified_resampling(particles):
#     num_particles = len(particles)
#     weights = [p.weight for p in particles]

#     cumulative_sum = np.cumsum(weights)
#     cumulative_sum[-1] = 1.0  # Ensure sum is exactly one

#     step = 1.0 / num_particles
#     positions = (np.arange(num_particles) + np.random.uniform(0, step)) * step

#     indexes = np.zeros(num_particles, 'i')
#     i, j = 0, 0
#     while i < num_particles:
#         if positions[i] < cumulative_sum[j]:
#             indexes[i] = j
#             i += 1
#         else:
#             j += 1

#     resampled_particles = [particles[i] for i in indexes]
#     for p in resampled_particles:
#         p.weight = 1.0 / num_particles  # Reset weights after resampling

#     return resampled_particles

# class AUVPositionPublisher(Node):
#     def __init__(self):
#         super().__init__('auv_position_publisher')
#         self.bridge = CvBridge()
#         self.image_sub = self.create_subscription(Image, '/Quadrotor/drone/fpcam/image_raw', self.image_callback, 10)
#         self.position_pub = self.create_publisher(Float32, "/Quadrotor/drone/fpcam/position", 10)
#         self.annotated_image_pub = self.create_publisher(Image, "/Quadrotor/drone/fpcam/annotated_image", 10)
#         self.num_particles = 500
#         self.particles = initialize_particles(self.num_particles, (480, 640))  # Assuming image size 640x480

#     def image_callback(self, data):
#         try:
#             cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
#         except CvBridgeError as e:
#             self.get_logger().error(f"CvBridge Error: {e}")
#             return

#         # Perform particle filter iterations
#         for _ in range(5):  # Number of iterations
#             self.particles = predict_particles(self.particles, cv_image.shape)
#             self.particles = calculate_weights(cv_image, self.particles, np.array([20, 100, 100]), np.array([30, 255, 255]))
#             self.particles = stratified_resampling(self.particles)
        
#         x_est, y_est = estimate_position(self.particles)
#         self.get_logger().info(f"Estimated Position of AUV: x={x_est}, y={y_est}")
#         self.position_pub.publish(Float32(data=x_est))  # Publish only x or both x and y as needed

#         # Annotate and publish the image
#         annotated_image = cv_image.copy()
#         for p in self.particles:
#             cv2.circle(annotated_image, (int(p.x), int(p.y)), 1, (0, 255, 0), -1)
#         cv2.circle(annotated_image, (int(x_est), int(y_est)), 5, (0, 0, 255), -1)

#         try:
#             annotated_image_msg = self.bridge.cv2_to_imgmsg(annotated_image, "bgr8")
#             self.annotated_image_pub.publish(annotated_image_msg)
#         except CvBridgeError as e:
#             self.get_logger().error(f"CvBridge Error: {e}")

# def main(args=None):
#     rclpy.init(args=args)
#     node = AUVPositionPublisher()
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         node.get_logger().info("Shutting down")
#     finally:
#         node.destroy_node()
#         rclpy.shutdown()

# if __name__ == '__main__':
#     main()


# import rclpy
# import cv2
# import numpy as np
# from rclpy.node import Node
# from cv_bridge import CvBridge, CvBridgeError
# from sensor_msgs.msg import Image
# from std_msgs.msg import Float32

# class AUVDistancePublisher(Node):
#     def __init__(self):
#         super().__init__('auv_position_publisher')
#         self.bridge = CvBridge()
#         self.image_sub = self.create_subscription(Image, '/Quadrotor/drone/fpcam/image_raw', self.image_callback, 10)
#         self.annotated_image_pub = self.create_publisher(Image, '/Quadrotor/drone/fpcam/annotated_image', 10)
#         self.position_pub = self.create_publisher(Float32, '/Quadrotor/drone/fpcam/position', 10)

#     def image_callback(self, data):
#         try:
#             cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
#         except CvBridgeError as e:
#             self.get_logger().error(f"CvBridge Error: {e}")
#             return

#         hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
#         lower_yellow = np.array([20, 100, 100])
#         upper_yellow = np.array([30, 255, 255])
#         mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        
#         yellow_points = np.argwhere(mask > 0)
#         np.random.shuffle(yellow_points)
#         selected_points = yellow_points[:5]

#         annotated_image = cv_image.copy()
#         for point in selected_points:
#             y, x = point
#             cv2.circle(annotated_image, (x, y), 5, (0, 0, 255), -1)  # Red dot for detected yellow points

#         try:
#             annotated_image_msg = self.bridge.cv2_to_imgmsg(annotated_image, "bgr8")
#             self.annotated_image_pub.publish(annotated_image_msg)
#         except CvBridgeError as e:
#             self.get_logger().error(f"CvBridge Error: {e}")

# def main(args=None):
#     rclpy.init(args=args)
#     node = AUVDistancePublisher()
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         node.get_logger().info("Shutting down")
#     finally:
#         node.destroy_node()
#         rclpy.shutdown()

# if __name__ == '__main__':
#     main()

import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
from std_msgs.msg import Float32
from random import uniform

class Particle:
    def __init__(self, x, y, weight):
        self.x = x
        self.y = y
        self.weight = weight

def initialize_particles(num_particles, img_shape):
    particles = []
    for _ in range(num_particles):
        x = uniform(0, img_shape[1])  # width
        y = uniform(0, img_shape[0])  # height
        particles.append(Particle(x, y, 1.0 / num_particles))
    return particles

def predict_particles(particles, img_shape, sigma=5):
    for p in particles:
        p.x += np.random.normal(0, sigma)
        p.y += np.random.normal(0, sigma)
        p.x = np.clip(p.x, 0, img_shape[1] - 1)
        p.y = np.clip(p.y, 0, img_shape[0] - 1)
    return particles

# def calculate_weights(image, particles, lower_yellow, upper_yellow):
#     hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
#     mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
#     # Get coordinates of yellow points
#     yellow_points = set(tuple(p) for p in np.argwhere(mask > 0))
    
#     for p in particles:
#         if (int(p.y), int(p.x)) in yellow_points:
#             p.weight = 1.0
#             self.get_logger().info(f"assigned weight 1")
#         else:
#             p.weight = 1 / (len(particles) + 1)

#     # Normalize weights
#     total_weight = sum([p.weight for p in particles])
#     if total_weight > 0:
#         for p in particles:
#             p.weight /= total_weight
        
#     return particles

def calculate_weights(image, particles, lower_yellow, upper_yellow, node_logger):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # Get coordinates of yellow points
    yellow_points = set(tuple(p) for p in np.argwhere(mask > 0))
    
    for p in particles:
        if (int(p.y), int(p.x)) in yellow_points:
            p.weight = 1.0
            node_logger.info(f"Particle at ({p.x}, {p.y}) assigned weight 1.0")
        else:
            p.weight = 1 / (len(particles) + 1)

    # Normalize weights
    total_weight = sum([p.weight for p in particles])
    if total_weight > 0:
        for p in particles:
            p.weight /= total_weight
        
    return particles


def estimate_position(particles):
    x_est = sum([p.x * p.weight for p in particles])
    y_est = sum([p.y * p.weight for p in particles])
    return x_est, y_est

# def stratified_resampling(particles):
#     num_particles = len(particles)
#     weights = [p.weight for p in particles]

#     cumulative_sum = np.cumsum(weights)
#     cumulative_sum[-1] = 1.0  # Ensure sum is exactly one

#     step = 1.0 / num_particles
#     positions = (np.arange(num_particles) + np.random.uniform(0, step)) * step

#     indexes = np.zeros(num_particles, 'i')
#     i, j = 0, 0
#     while i < num_particles:
#         if positions[i] < cumulative_sum[j]:
#             indexes[i] = j
#             i += 1
#         else:
#             j += 1

#     resampled_particles = [particles[i] for i in indexes]
#     # for p in resampled_particles:
#     #     p.weight = 1.0 / num_particles  # Reset weights after resampling
        # return resampled_particles

def systematic_resampling(particles):
    num_particles = len(particles)
    weights = [p.weight for p in particles]
    cumulative_sum = np.cumsum(weights)
    cumulative_sum[-1] = 1.0  # Ensure sum is exactly one

    positions = (np.arange(num_particles) + np.random.uniform(0, 1)) / num_particles

    indexes = np.zeros(num_particles, 'i')
    i, j = 0, 0
    while i < num_particles:
        if positions[i] < cumulative_sum[j]:
            indexes[i] = j
            i += 1
        else:
            j += 1

    resampled_particles = [particles[i] for i in indexes]
    for p in resampled_particles:
        p.weight = 1.0 / num_particles  # Reset weights after resampling

    return resampled_particles


def calculate_yellow_centroid(mask):
    yellow_points = np.argwhere(mask > 0)
    if len(yellow_points) == 0:
        return None, None

    centroid = np.mean(yellow_points, axis=0)
    return int(centroid[1]), int(centroid[0])  # x, y order

class AUVDistancePublisher(Node):
    def __init__(self):
        super().__init__('auv_position_publisher')
        self.bridge = CvBridge()
        self.image_sub = self.create_subscription(Image, '/Quadrotor/drone/fpcam/image_raw', self.image_callback, 10)
        self.annotated_image_pub = self.create_publisher(Image, '/Quadrotor/drone/fpcam/annotated_image', 10)
        self.position_pub = self.create_publisher(Float32, '/Quadrotor/drone/fpcam/position', 10)
        self.num_particles = 500
        self.particles = initialize_particles(self.num_particles, (480, 640))  # Assuming image size 640x480

    # def image_callback(self, data):
    #     try:
    #         cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
    #     except CvBridgeError as e:
    #         self.get_logger().error(f"CvBridge Error: {e}")
    #         return

    #     # Convert to HSV and create mask
    #     hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
    #     mask = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([30, 255, 255]))
        
    #     # Calculate the centroid of yellow points
    #     yellow_centroid_x, yellow_centroid_y = calculate_yellow_centroid(mask)

    #     for _ in range(5):  # Number of iterations
    #         self.particles = predict_particles(self.particles, cv_image.shape)
    #         self.particles = calculate_weights(cv_image, self.particles, np.array([20, 100, 100]), np.array([30, 255, 255]))
    #         self.particles = stratified_resampling(self.particles)

    #     x_est, y_est = estimate_position(self.particles)
    #     self.get_logger().info(f"Estimated Position of AUV: x={x_est}, y={y_est}")
    #     self.position_pub.publish(Float32(data=x_est))  # Publish only x or both x and y as needed

    #     annotated_image = cv_image.copy()
    #     for p in self.particles:
    #         cv2.circle(annotated_image, (int(p.x), int(p.y)), 2, (0, 255, 0), -1)  # Green dot for particles
    #     cv2.circle(annotated_image, (int(x_est), int(y_est)), 5, (0, 0, 255), -1)  # Red dot for estimated position
        
    #     if yellow_centroid_x is not None and yellow_centroid_y is not None:
    #         cv2.circle(annotated_image, (yellow_centroid_x, yellow_centroid_y), 5, (255, 0, 0), -1)  # Blue dot for yellow centroid

    #     try:
    #         annotated_image_msg = self.bridge.cv2_to_imgmsg(annotated_image, "bgr8")
    #         self.annotated_image_pub.publish(annotated_image_msg)
    #     except CvBridgeError as e:
    #         self.get_logger().error(f"CvBridge Error: {e}")

    def image_callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            self.get_logger().error(f"CvBridge Error: {e}")
            return

        # Convert to HSV and create mask
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([30, 255, 255]))

        # Calculate the centroid of yellow points
        yellow_centroid_x, yellow_centroid_y = calculate_yellow_centroid(mask)

        for _ in range(5):  # Number of iterations
            self.particles = predict_particles(self.particles, cv_image.shape)
            self.particles = calculate_weights(cv_image, self.particles, np.array([20, 100, 100]), np.array([30, 255, 255]),self.get_logger())
            self.particles = systematic_resampling(self.particles)

        x_est, y_est = estimate_position(self.particles)
        self.get_logger().info(f"Estimated Position of AUV: x={x_est}, y={y_est}")
        self.position_pub.publish(Float32(data=x_est))  # Publish only x or both x and y as needed

        annotated_image = cv_image.copy()
        for p in self.particles:
            if p.weight == 1.0:  # Particles that were in the yellow list
                cv2.circle(annotated_image, (int(p.x), int(p.y)), 2, (0, 255, 0), -1)  # Green dot
            else:
                cv2.circle(annotated_image, (int(p.x), int(p.y)), 2, (0, 0, 255), -1)  # Red dot for other particles
        cv2.circle(annotated_image, (int(x_est), int(y_est)), 5, (0, 0, 255), -1)  # Red dot for estimated position

        if yellow_centroid_x is not None and yellow_centroid_y is not None:
            cv2.circle(annotated_image, (yellow_centroid_x, yellow_centroid_y), 5, (255, 0, 0), -1)  # Blue dot for yellow centroid

        try:
            annotated_image_msg = self.bridge.cv2_to_imgmsg(annotated_image, "bgr8")
            self.annotated_image_pub.publish(annotated_image_msg)
        except CvBridgeError as e:
            self.get_logger().error(f"CvBridge Error: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = AUVDistancePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()


