import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray, Float32
import numpy as np
from state_estimation.model_ekf import EKFModel_ImageFeedback
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from drone_msgs.msg import Links as DroneLinks
from drone_msgs.msg import Topics as DroneTopics
import tf2_ros
import tf2_geometry_msgs
class AUVPositionEstimator(Node):
    def __init__(self):
        super().__init__('auv_position_estimator')

        # ===== Declare parameters =====
        self.declare_node_parameters()

        # ===== Get parameters =====
        self.robot_name = self.get_parameter("robot_name").value
        self.map_frame = self.get_parameter("map_frame").value

        # Camera intrinsics
        self.f_x = self.get_parameter("f_x").value
        self.f_y = self.get_parameter("f_y").value
        self.c_x = self.get_parameter("c_x").value
        self.c_y = self.get_parameter("c_y").value

        # KF noise parameters
        self.Q_auv_relative = np.eye(6) * self.get_parameter("Q_noise").value
        self.R_auv_relative = np.eye(3) * self.get_parameter("R_noise").value
        self.R_auv_relative[2, 2] = self.get_parameter("R_noise_depth").value
        self.P_auv_relative = np.eye(6) * self.get_parameter("P_noise").value

        # Inverse camera matrix
        self.K = np.array([[self.f_x, 0, self.c_x],
                           [0, self.f_y, self.c_y],
                           [0, 0, 1]])
        self.K_inv = np.linalg.inv(self.K)

        # Kalman filter initialization
        self.kf_auv = EKFModel_ImageFeedback('AUV_relative_position_estimator')

        
        # Initialize attributes to store positions
        self.drone_estimated_position = None   # Holds latest drone estimated position
        self.drone_ground_truth_position = None  # Holds latest ground truth position
        # Subscriptions and publishers
        # Initialize subscribers for drone's estimated and ground truth positions
        self.create_subscription(Odometry, f"/{self.robot_name}/{DroneTopics.DR_POSITION_TOPIC}", self.drone_est_position_cb, 10)
        self.create_subscription(Odometry, f"/{self.robot_name}/{DroneTopics.DRONE_ODOM_GT_TOPIC}", self.drone_ground_truth_cb , 10)
        # self.create_subscription(Float32MultiArray, f"/{self.robot_name}/{DroneTopics.DR_POSITION_TOPIC}", self.drone_position_cb, 10)
        self.create_subscription(Float32MultiArray, f"/{self.robot_name}/{DroneTopics.BUOY_DETECTOR_ESTIMATE_TOPIC}", self.min_gradient_cb, 10)
        self.create_subscription(Float32, f"/{self.robot_name}/{DroneTopics.DEPTH_TOPIC}" , self.depth_cb, 10)

        # self.auv_position_publisher = self.create_publisher(Float32MultiArray, f"/{self.robot_name}/{DroneTopics.AUV_RELATIVE_POSITION_TOPIC}", 10)
        self.auv_position_publisher = self.create_publisher(Odometry, f"/{self.robot_name}/{DroneTopics.AUV_RELATIVE_POSITION_TOPIC}", 10)

        # tf2 buffer for IMU transformation
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        # Initialize a TF broadcaster
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        self.depth = None
        self.image_point = None
        self.X_auv_relative = None
        self.X_drone = None
        self.first_measurement = False

    def declare_node_parameters(self):
        """
        Declare the node parameters for the AUV position estimator node.
        """
        self.declare_parameter("robot_name", "Quadrotor")
        #frames for tf
        self.declare_parameter("map_frame", "map_gt")

        # Camera intrinsic parameters (these can vary depending on your camera setup)
        self.declare_parameter("f_x", 20.78461 * 640 / 36)
        self.declare_parameter("f_y", 20.78461 * 480 / 24)
        self.declare_parameter("c_x", 320)
        self.declare_parameter("c_y", 240)

        # Kalman Filter noise parameters
        self.declare_parameter("Q_noise", 10 ** -3)
        self.declare_parameter("R_noise", 10 ** -3)
        self.declare_parameter("R_noise_depth", 10 ** -6)
        self.declare_parameter("P_noise", 10 ** -2)

    def drone_est_position_cb(self, msg: Odometry):
        self.drone_estimated_position = np.array([msg.pose.pose.position.x,
                                                  msg.pose.pose.position.y,
                                                  msg.pose.pose.position.z])
    
    def drone_ground_truth_cb(self, msg: Odometry):
        # Store the latest ground truth position
        self.drone_ground_truth_position = np.array([msg.pose.pose.position.x,
                                                     msg.pose.pose.position.y,
                                                     msg.pose.pose.position.z])

    def depth_cb(self, msg: Float32) -> None:
        self.depth = msg.data

    def min_gradient_cb(self, msg: Float32MultiArray) -> None:
        u, v = msg.data[0], msg.data[1]
        self.image_point = np.array([u, v, 1])
        
        if self.image_point is not None: 
            # and self.X_drone is not None:
            self.estimate_relative_position()

    def estimate_relative_position(self):
        observation = self.image_point.copy()
        observation[2] = self.depth

        if not self.first_measurement:
            self.X_auv_relative = self.get_first_measured_state(observation)
            self.kf_auv.initialize_state(self.X_auv_relative, self.Q_auv_relative, self.R_auv_relative, self.P_auv_relative)
            self.first_measurement = True
            # self.get_logger().info(f"initializaing: {self.X_auv_relative }") debugging....
        else:
            self.X_auv_relative, self.P_auv_relative = self.kf_auv.estimate(observation, feedback_image=True)
            self.get_logger().info(f"estimating relative position: {self.X_auv_relative }")
        if self.X_auv_relative is not None:
            auv_position = self.get_world_position(self.X_auv_relative[:3])
            self.publish_auv_position(auv_position)
            self.publish_tf(auv_position)

    def get_first_measured_state(self, observation):
        direction_vector = np.dot(self.K_inv, observation)
        direction_world = np.dot(np.eye(3), direction_vector)  # Using an identity matrix for R_wa
        scale = self.depth / direction_world[2]
        vector_auv_drone = direction_world * scale
        return np.array([vector_auv_drone, np.zeros(3)]).flatten().T

    def publish_tf(self, position, orientation=None):
        # Create a TransformStamped message
        t = TransformStamped()

        # Set the frame information
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = self.map_frame  # Parent frame
        t.child_frame_id = 'auv_estimated_state'  # Child frame for the estimated state

        # Set the translation (position) in the TF message
        t.transform.translation.x = position[0]
        t.transform.translation.y = position[1]
        t.transform.translation.z = position[2]

        # Check if orientation is provided; if not, set it to identity quaternion (no rotation)
        if orientation:
            t.transform.rotation.x = orientation[0]
            t.transform.rotation.y = orientation[1]
            t.transform.rotation.z = orientation[2]
            t.transform.rotation.w = orientation[3]
        else:
            # Default to no rotation if no orientation is provided
            t.transform.rotation.x = 0.0
            t.transform.rotation.y = 0.0
            t.transform.rotation.z = 0.0
            t.transform.rotation.w = 1.0  # Identity quaternion (no rotation)

        # Broadcast the transform
        self.tf_broadcaster.sendTransform(t)

    def publish_auv_position(self, position):
        # self.get_logger().info(f"position being published : {position}")
        
        # Create an Odometry message
        odom_msg = Odometry()
        
        # Set header information
        odom_msg.header.stamp = self.get_clock().now().to_msg()  # Add timestamp
        odom_msg.header.frame_id = f"{self.robot_name}/auv/odom"  # Typically, "odom" frame for localization
        
        # Set position
        odom_msg.pose.pose.position.x = position[0]
        odom_msg.pose.pose.position.y = position[1]
        odom_msg.pose.pose.position.z = position[2]

        # Assuming no orientation information available, setting as identity quaternion
        odom_msg.pose.pose.orientation.w = 1.0
        odom_msg.pose.pose.orientation.x = 0.0
        odom_msg.pose.pose.orientation.y = 0.0
        odom_msg.pose.pose.orientation.z = 0.0

        # If you have velocity data, you can populate the twist section
        odom_msg.twist.twist.linear.x = 0.0
        odom_msg.twist.twist.linear.y = 0.0
        odom_msg.twist.twist.linear.z = 0.0

        # Publish the Odometry message
        self.auv_position_publisher.publish(odom_msg)

    def get_world_position(self,auv_relative_position) :
        if self.drone_estimated_position is not None:
            # Use estimated position + relative AUV position
            world_position = self.drone_estimated_position + auv_relative_position
            self.get_logger().info(f"World position using estimated position: {world_position}")
            return world_position
        elif self.drone_ground_truth_position is not None:
            # Fall back to ground truth position + relative AUV position
            world_position = self.drone_ground_truth_position + auv_relative_position
            self.get_logger().info(f"world position using ground truth position: {world_position}")
            return world_position
        else:
            # If neither position is available, return None or handle accordingly
            self.get_logger().warn("No position data available to calculate world position.")
            return None

def main(args=None):
    rclpy.init(args=args)
    node = AUVPositionEstimator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
