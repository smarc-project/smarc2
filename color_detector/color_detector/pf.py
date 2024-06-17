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

def calculate_weights(image, particles, lower_yellow, upper_yellow):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # Get coordinates of yellow points
    yellow_points = set(tuple(p) for p in np.argwhere(mask > 0))
    
    has_weight_one = False
    for p in particles:
        if (int(p.y), int(p.x)) in yellow_points:
            p.weight = 1.0
            has_weight_one = True
            print(f"Particle at ({p.x}, {p.y}) assigned weight 1")
        else:
            p.weight = 1.0 / (len(particles) + 1)

    if not has_weight_one:
        return False  # Indicate that no particle got a weight of 1

    # Normalize weights
    total_weight = sum([p.weight for p in particles])
    if total_weight > 0:
        for p in particles:
            p.weight /= total_weight
        
    return True

def estimate_position(particles):
    x_est = sum([p.x * p.weight for p in particles])
    y_est = sum([p.y * p.weight for p in particles])
    return x_est, y_est

def systematic_resampling(particles, weight_threshold=0.001):
    num_particles = len(particles)
    weights = np.array([p.weight for p in particles])

    # Apply weight threshold
    weights[weights < weight_threshold] = 0
    weights /= np.sum(weights)  # Normalize again after thresholding

    cumulative_sum = np.cumsum(weights)
    cumulative_sum[-1] = 1.0  # Ensure sum is exactly one

    step = 1.0 / num_particles
    positions = (np.arange(num_particles) + np.random.uniform(0, step)) * step

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
        self.num_particles = 5000
        self.particles = initialize_particles(self.num_particles, (480, 640))  # Assuming image size 640x480

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
            got_weight_one = calculate_weights(cv_image, self.particles, np.array([20, 100, 100]), np.array([30, 255, 255]))
            if not got_weight_one:
                self.particles = initialize_particles(self.num_particles, cv_image.shape)
                self.get_logger().info("No particle got weight 1. Reinitializing particles.")
                continue
            self.particles = systematic_resampling(self.particles, weight_threshold=0.01)

        x_est, y_est = estimate_position(self.particles)
        self.get_logger().info(f"Estimated Position of AUV: x={x_est}, y={y_est}")
        self.position_pub.publish(Float32(data=x_est))  # Publish only x or both x and y as needed

        annotated_image = cv_image.copy()
        for p in self.particles:
            if p.weight == 1.0:
                cv2.circle(annotated_image, (int(p.x), int(p.y)), 2, (0, 255, 0), -1)  # Green dot for particles with weight 1
            else:
                cv2.circle(annotated_image, (int(p.x), int(p.y)), 2, (0, 0, 255), -1)  # Red dot for particles with other weights

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
