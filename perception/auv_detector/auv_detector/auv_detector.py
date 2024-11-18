import rclpy
import rclpy.duration
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray, Float32
import numpy as np
from auv_detector.model_ekf import EKFModel_ImageFeedback
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped, PointStamped
from drone_msgs.msg import Links as DroneLinks
from drone_msgs.msg import Topics as DroneTopics
from sensor_msgs.msg import CameraInfo
import tf2_ros
import tf2_geometry_msgs
from rclpy.executors import MultiThreadedExecutor
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
        self.frame_suffix = self.get_parameter("frame_suffix").value
        # Check if dead reckoning is active and set appropriate odom frame
        # if self.is_dead_reckoning_active():
        #     self.odom_frame = f"{self.robot_name}/{DroneLinks.ODOM_LINK}"
        # else:
        self.odom_frame = f"{self.robot_name}/{DroneLinks.ODOM_LINK}{self.frame_suffix}"
        self.camera_frame = f"{self.robot_name}/{DroneLinks.CAMERA_LINK}{self.frame_suffix}"
        self.R_odom_cam = None

        self.odom_tf = True
        # self.camera_sensor_frame = f"{self.robot_name}/{DroneLinks.CAMERA_SENSOR}{self.frame_suffix}"

        
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
        # AD-HOC CAM TO LINK I FOUND BY THE NUMBERS
        self.R_cam_to_link = np.array([[0, 1, 0],
                                       [1, 0, 0],
                                       [0, 0, 1]])

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
        
        # self.last_observation_time = self.get_clock().now()  # Use rclpy time to track last observation
        # self.new_observation_available = False # Flag to indicate if a new observation is available
        # self.drone_translation_previous = None
        # # Timer to propagate position
        # self.timer = self.create_timer(0.1, self.propagate_position)  # Update every 100ms

    # def is_dead_reckoning_active(self):
    #     """ Check if the dead reckoning node is active by listing active nodes """
    #     node_names = self.get_node_names()
    #     self.get_logger().info(f"Active nodes: {node_names}")
    #     # Adjust 'drone_position_estimator' to match actual node name
    #     return self.dr_node_name in node_names

    def declare_node_parameters(self):
        """ Declare the parameters for the AUV position estimator node """
        self.declare_parameter("robot_name", "Quadrotor")
        self.declare_parameter("frame_suffix", "")
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
        # self.depth = msg.data
        self.depth = -msg.data

    def min_gradient_cb(self, msg: Float32MultiArray):
        """ Buoy detector callback for image point data """
        u, v = msg.data[0], msg.data[1]
        self.image_point = np.array([u, v, 1])
        if self.image_point is not None:
            self.estimate_relative_position()

    # def min_gradient_cb(self, msg: Float32MultiArray):
    #     """Buoy detector callback for image point data."""
    #     u, v = msg.data[0], msg.data[1]
    #     self.image_point = np.array([u, v, 1])
    #     self.new_observation_available = True
    #     self.last_observation_time = self.get_clock().now()  # Update the last observation time

    # def propagate_position(self):
    #     """Estimate or propagate the AUV's relative position."""
    #     current_time = self.get_clock().now()
    #     time_since_last_obs = current_time - self.last_observation_time

    #     if self.image_point is not None:
    #         if self.new_observation_available:
    #             # Process the new observation
    #             self.estimate_relative_position()
    #             self.new_observation_available = False
    #         elif time_since_last_obs > rclpy.duration.Duration(seconds=0.1):  # Threshold for propagation
    #             # No new observation; propagate the position
    #             self.propagate_without_feedback(time_since_last_obs)

    def estimate_relative_position(self):
        """ Estimate AUV's relative position based on depth and image data """
        observation = self.image_point.copy()
        observation[2] = self.depth
        self.R_odom_cam = self.rotation_matrix_odom()
        if not self.first_measurement and self.R_odom_cam is not None:
            # self.get_logger().info(f"initializing: {self.R_odom_cam}")
            self.X_auv_relative = self.get_first_measured_state(observation)
            self.kf_auv.initialize_state(self.X_auv_relative, self.Q_auv_relative, self.R_auv_relative, self.P_auv_relative,self.R_odom_cam)
            self.first_measurement = True
        elif self.R_odom_cam is not None:
            self.X_auv_relative, self.P_auv_relative = self.kf_auv.estimate(observation,self.R_odom_cam, feedback_image=True)
            # self.get_logger().info(f"transformation bet: {self.R_odom_cam}")
            # self.get_logger().info(f"Estimating relative position: {self.X_auv_relative}")
            # self.get_logger().info(f"the coordinates in odom aligned frame: {np.dot(self.R_odom_cam,self.X_auv_relative[:3])}")

            try:
                # Lookup the transform from the camera frame to the odom frame
                transform = self.tf_buffer.lookup_transform(
                    'sam_auv_v1/back_prop_link_gt',
                    self.camera_frame,  # Source frame
                    self.get_clock().now()  # Time of the transform
                )
                # self.get_logger().info(f"gt position: {transform.transform.translation}")
                self.get_logger().info(f"error bet gt and estimate: {np.linalg.norm(np.array([transform.transform.translation.x,transform.transform.translation.y,transform.transform.translation.z])-self.X_auv_relative[:3])}")

            except Exception as e:
                self.get_logger().warn(f"Transformation error: {e}")


            # epic = self.get_first_measured_state(observation)

        if self.X_auv_relative is not None:
            auv_rel_position = self.X_auv_relative[:3]  # Only position, assuming no rotation
            self.publish_auv_position(auv_rel_position)
            self.publish_tf(auv_rel_position)

    # def propagate_without_feedback(self, time_since_last_obs):
    #     """Propagate the AUV's relative position in the absence of new feedback."""
    #     if self.X_auv_relative is None or self.R_odom_cam is None:
    #         return  # Nothing to propagate

    #     try:
    #         # Get the latest transform from odom to 'camera_frame'
    #         transform = self.tf_buffer.lookup_transform(
    #             self.odom_frame,
    #             self.camera_frame,
    #             self.tf_buffer.get_latest_common_time(self.odom_frame, self.camera_frame)
    #         )

    #         # Extract current translation
    #         current_translation = np.array([
    #             transform.transform.translation.x,
    #             transform.transform.translation.y,
    #             transform.transform.translation.z
    #         ])

    #         # Initialize previous translation if not already set
    #         if self.drone_translation_previous is None:
    #             self.drone_translation_previous = current_translation
    #             return  # No propagation yet

    #         # Calculate the difference in drone translation
    #         self.drone_translation_diff = current_translation - self.drone_translation_previous
    #         self.drone_translation_previous = current_translation

    #     except Exception as e:
    #         self.get_logger().warn(f"Transformation error in propagate_without_feedback: {e}")
    #         return

    #     # Update relative position based on drone motion
    #     self.X_auv_relative[:3] -= self.drone_translation_diff

    #     # Publish the propagated position
    #     auv_rel_position = self.X_auv_relative[:3]
    #     self.publish_auv_position(auv_rel_position)
    #     self.publish_tf(auv_rel_position)

    def rotation_matrix_odom(self):
        try:
            # Get the latest transform from odom to 'camera_frame'
            transform = self.tf_buffer.lookup_transform(
                self.camera_frame,
                self.odom_frame,
                self.tf_buffer.get_latest_common_time(self.camera_frame, self.odom_frame)
            )
            return quaternion_to_rotation_matrix(transform.transform.rotation)
            
        except Exception as e:
            self.get_logger().warn(f"Transformation error: {e}")
            return

    def get_first_measured_state(self, observation):
        """ Initialize the state from the first observation """
        direction_vector = np.dot(self.K_inv, np.array([observation[0],observation[1],1]))
        #HERE WE SHOULD HAVE THE APPROPRIATE ROTATION VECTOR INSTEAD OF EYE
        
        # direction_world = np.dot(np.eye(3), direction_vector)
        # direction_world = np.dot(self.R_odom_cam, direction_vector)
        direction_world = np.dot(self.R_cam_to_link, direction_vector)
        scale = -self.depth / direction_world[2]
        vector_auv_drone = direction_world * scale
        # vector_auv_drone[2] = np.sign(self.depth)*vector_auv_drone[2]
        # self.get_logger().info(f"no rotation georeferenced coordinates: {direction_vector* scale}")
        self.get_logger().info(f"georeferenced coordinates of buoy: {vector_auv_drone}")
        
        return np.hstack((vector_auv_drone, np.zeros(3)))
        
        # return np.hstack((direction_vector* scale, np.zeros(3)))
    

    # def publish_tf(self, position, orientation=None):
    #     """ Publish a TF transform with the given position """
        

    #     t = TransformStamped()
    #     t.header.stamp = self.get_clock().now().to_msg()
    #     # t.header.frame_id = self.camera_frame
    #     t.header.frame_id = self.camera_frame
    #     t.child_frame_id = self.auv_rel_frame
    #     t.transform.translation.x, t.transform.translation.y, t.transform.translation.z = position

    #     if orientation:
    #         t.transform.rotation.x, t.transform.rotation.y, t.transform.rotation.z, t.transform.rotation.w = orientation
    #     else:
    #         t.transform.rotation.w = 1.0  # Identity quaternion

        # self.tf_broadcaster.sendTransform(t)

    def publish_tf(self, position, orientation=None):
        """ Publish a TF transform with the given position """

        if not self.odom_tf: 
            t = TransformStamped()
            t.header.stamp = self.get_clock().now().to_msg()
            # t.header.frame_id = self.camera_frame
            t.header.frame_id = self.camera_frame
            t.child_frame_id = self.auv_rel_frame
            t.transform.translation.x, t.transform.translation.y, t.transform.translation.z = position

            if orientation:
                t.transform.rotation.x, t.transform.rotation.y, t.transform.rotation.z, t.transform.rotation.w = orientation
            else:
                t.transform.rotation.w = 1.0  # Identity quaternion

            self.tf_broadcaster.sendTransform(t)
        else:
            try:
                point_camera = PointStamped()
            
                point_camera.point.x, point_camera.point.y, point_camera.point.z = np.dot(np.linalg.inv(self.R_cam_to_link),position)
                # Lookup the transform from the camera frame to the odom frame
                transform = self.tf_buffer.lookup_transform(
                    self.odom_frame,  # Target frame
                    self.camera_frame,  # Source frame
                    self.get_clock().now()  # Time of the transform
                )
                t_odom = TransformStamped()
                # Transform the point to the odom frame
                point_odom = tf2_geometry_msgs.do_transform_point(point_camera, transform)

                # Adjust for flipped Z-axis if needed
                transformed_position = np.array([
                    point_odom.point.x,
                    point_odom.point.y,
                    point_odom.point.z  # Negate Z if flipping occurs
                ])

                # Create the TransformStamped for odom
                t_odom = TransformStamped()
                t_odom.header.stamp = self.get_clock().now().to_msg()
                t_odom.header.frame_id = self.odom_frame  # Odom frame as parent
                t_odom.child_frame_id = self.auv_rel_frame
                t_odom.transform.translation.x, t_odom.transform.translation.y, t_odom.transform.translation.z = transformed_position

                if orientation:
                    t_odom.transform.rotation.x, t_odom.transform.rotation.y, t_odom.transform.rotation.z, t_odom.transform.rotation.w = orientation
                else:
                    t_odom.transform.rotation.w = 1.0  # Identity quaternion

                self.tf_broadcaster.sendTransform(t_odom)

                # t_odom.header.stamp = self.get_clock().now().to_msg()
                #  # t.header.frame_id = self.camera_frame
                # t_odom.header.frame_id = self.camera_frame
                # t_odom.child_frame_id = self.auv_rel_frame
                # t_odom.transform.translation.x = point_odom.point.x
                # t_odom.transform.translation.y = point_odom.point.y
                # t_odom.transform.translation.z = point_odom.point.z
                # if orientation:
                #     t_odom.transform.rotation.x, t_odom.transform.rotation.y, t_odom.transform.rotation.z, t_odom.transform.rotation.w = orientation
                # else:
                #     t_odom.transform.rotation.w = 1.0  # Identity quaternion

                # self.tf_broadcaster.sendTransform(t_odom)

            except Exception as e:
                self.get_logger().warn(f"Transformation error: {e}")
                return

    def publish_auv_position(self, position):
        """ Publish the AUV's relative position as an Odometry message in the odom_frame """
        # Create a PointStamped for the AUV's position in the camera frame
        point_camera = PointStamped()
        point_camera.header.stamp = self.get_clock().now().to_msg()
        point_camera.header.frame_id = self.camera_frame
        point_camera.point.x, point_camera.point.y, point_camera.point.z = position

        try:
            # Lookup the transform from the camera frame to the odom frame
            transform = self.tf_buffer.lookup_transform(
                self.odom_frame,  # Target frame
                self.camera_frame,  # Source frame
                self.get_clock().now()  # Time of the transform
            )

            # Transform the point to the odom frame
            point_odom = tf2_geometry_msgs.do_transform_point(point_camera, transform)

            # Create an Odometry message for the transformed point
            odom_msg = Odometry()
            odom_msg.header.stamp = self.get_clock().now().to_msg()
            odom_msg.header.frame_id = self.odom_frame
            odom_msg.pose.pose.position.x = point_odom.point.x
            odom_msg.pose.pose.position.y = point_odom.point.y
            odom_msg.pose.pose.position.z = point_odom.point.z

            # Set orientation to identity (no rotation)
            odom_msg.pose.pose.orientation.w = 1.0

            # Publish the transformed position
            self.auv_position_publisher.publish(odom_msg)

        except Exception as e:
            self.get_logger().warn(f"Transformation error: {e}")
            return


def quaternion_to_rotation_matrix(quat):
    """
    Convert quaternion to rotation matrix.
    :param quat: Quaternion message (x, y, z, w)
    :return: 3x3 rotation matrix
    """
    x, y, z, w = quat.x, quat.y, quat.z, quat.w
    # Compute the rotation matrix elements
    R = np.array([
        [1 - 2 * (y**2 + z**2), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x**2 + z**2), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x**2 + y**2)]
    ])
    return R

def main(args=None):
    rclpy.init(args=args)
    node = AUVPositionEstimator()
    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()