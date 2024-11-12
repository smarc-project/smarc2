import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray, Float32
import numpy as np
from auv_detector.model_ekf import EKFModel_ImageFeedback
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from drone_msgs.msg import Links as DroneLinks
from drone_msgs.msg import Topics as DroneTopics
from sensor_msgs.msg import CameraInfo
import tf2_ros
import tf2_geometry_msgs

class AUVPositionEstimator(Node):
    def __init__(self):
        super().__init__('auv_position_estimator')

        # ===== Declare parameters =====
        self.declare_node_parameters()

        # ===== Get parameters =====
        self.robot_name = self.get_parameter("robot_name").value
        self.map_frame =  f"{self.robot_name}/{DroneLinks.DR_MAP}"
        self.auv_rel_frame = f"{self.robot_name}/{DroneLinks.AUV_RELATIVE_FRAME}"

        #node check string name
        self.dr_node_name = self.get_parameter("dr_node_name").value
        # Check if dead reckoning is active and set appropriate odom frame
        if self.is_dead_reckoning_active():
            self.odom_frame = f"{self.robot_name}/{DroneLinks.ODOM_LINK}"
        else:
            self.odom_frame = f"{self.robot_name}/{DroneLinks.ODOM_LINK}_gt"
        
        
        # Initialize the camera intrinsic matrix
        self.K = np.zeros([3, 3])

        # Subscribe to CameraInfo for intrinsics
        self.create_subscription(CameraInfo, f"/{self.robot_name}/{DroneTopics.CAMERA_INFO_TOPIC}", self.cam_param_cb, 10)
        
        # KF noise parameters
        Q_str = self.get_parameter("process_noise").value
        R_str = self.get_parameter("measurement_noise").value
        P_str = self.get_parameter("state_covariance").value
        self.Q_auv_relative = np.zeros([6, 6])
        self.R_auv_relative = np.zeros([3, 3])
        self.P_auv_relative = np.zeros([6, 6])
        self.Q_auv_relative = np.array(Q_str).reshape(6, 6)
        self.R_auv_relative = np.array(R_str).reshape(3, 3)
        self.P_auv_relative = np.array(P_str).reshape(6, 6)

        # Kalman filter initialization
        self.kf_auv = EKFModel_ImageFeedback('AUV_relative_position_estimator')
        
        # Subscriptions and publishers
        self.create_subscription(Float32MultiArray, f"/{self.robot_name}/{DroneTopics.BUOY_DETECTOR_ESTIMATE_TOPIC}", self.min_gradient_cb, 10)
        self.create_subscription(Float32, f"/{self.robot_name}/{DroneTopics.DEPTH_TOPIC}", self.depth_cb, 10)
        self.auv_position_publisher = self.create_publisher(Odometry, f"/{self.robot_name}/{DroneTopics.AUV_RELATIVE_POSITION_TOPIC}", 10)

        # tf2 buffer for IMU transformation
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        self.depth = None
        self.image_point = None
        self.X_auv_relative = None
        self.first_measurement = False

    def is_dead_reckoning_active(self):
        """ Check if the dead reckoning node is active by listing active nodes """
        node_names = self.get_node_names()
        self.get_logger().info(f"Active nodes: {node_names}")
        # Adjust 'drone_position_estimator' to match actual node name
        return self.dr_node_name in node_names  

    def declare_node_parameters(self):
        """ Declare the parameters for the AUV position estimator node """
        self.declare_parameter("robot_name", "Quadrotor")
        self.declare_parameter("dr_node_name", "'drone_state_estimator_node'")
        self.declare_parameter("process_noise", [
            0.001, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.001, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.001, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.001, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.001, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.001
            ])

        self.declare_parameter("measurement_noise", [
            0.0001, 0.0, 0.0,
            0.0, 0.0001, 0.0,
            0.0, 0.0, 0.0001
        ])

        self.declare_parameter("state_covariance", [
            0.001, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.001, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.001, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.001, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.001, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.001
        ])

    def cam_param_cb(self, msg: CameraInfo):
        """ Callback for receiving camera intrinsic parameters """
        self.K = np.array(msg.k).reshape(3, 3)
        self.K_inv = np.linalg.inv(self.K)

    def depth_cb(self, msg: Float32):
        """ Depth sensor callback """
        self.depth = msg.data

    def min_gradient_cb(self, msg: Float32MultiArray):
        """ Buoy detector callback for image point data """
        u, v = msg.data[0], msg.data[1]
        self.image_point = np.array([u, v, 1])
        if self.image_point is not None:
            self.estimate_relative_position()

    def estimate_relative_position(self):
        """ Estimate AUV's relative position based on depth and image data """
        observation = self.image_point.copy()
        observation[2] = self.depth

        if not self.first_measurement:
            self.X_auv_relative = self.get_first_measured_state(observation)
            self.kf_auv.initialize_state(self.X_auv_relative, self.Q_auv_relative, self.R_auv_relative, self.P_auv_relative)
            self.first_measurement = True
        else:
            self.X_auv_relative, self.P_auv_relative = self.kf_auv.estimate(observation, feedback_image=True)
            self.get_logger().info(f"Estimating relative position: {self.X_auv_relative}")

        if self.X_auv_relative is not None:
            auv_rel_position = self.X_auv_relative[:3]  # Only position, assuming no rotation
            self.publish_auv_position(auv_rel_position)
            self.publish_tf(auv_rel_position)

    def get_first_measured_state(self, observation):
        """ Initialize the state from the first observation """
        direction_vector = np.dot(self.K_inv, observation)
        direction_world = np.dot(np.eye(3), direction_vector)
        scale = self.depth / direction_world[2]
        vector_auv_drone = direction_world * scale
        return np.hstack((vector_auv_drone, np.zeros(3)))

    def publish_tf(self, position, orientation=None):
        """ Publish a TF transform with the given position """
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = self.odom_frame
        t.child_frame_id = self.auv_rel_frame
        t.transform.translation.x, t.transform.translation.y, t.transform.translation.z = position

        if orientation:
            t.transform.rotation.x, t.transform.rotation.y, t.transform.rotation.z, t.transform.rotation.w = orientation
        else:
            t.transform.rotation.w = 1.0  # Identity quaternion

        self.tf_broadcaster.sendTransform(t)

    def publish_auv_position(self, position):
        """ Publish the AUV's relative position as an Odometry message """
        odom_msg = Odometry()
        odom_msg.header.stamp = self.get_clock().now().to_msg()
        odom_msg.header.frame_id = self.auv_rel_frame
        odom_msg.pose.pose.position.x, odom_msg.pose.pose.position.y, odom_msg.pose.pose.position.z = position
        odom_msg.pose.pose.orientation.w = 1.0
        self.auv_position_publisher.publish(odom_msg)

def main(args=None):
    rclpy.init(args=args)
    node = AUVPositionEstimator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()