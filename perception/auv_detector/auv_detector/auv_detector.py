import rclpy
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

        self.declare_node_parameters()
        self.robot_name = self.get_parameter("robot_name").value
        self.map_frame =  f"{self.robot_name}/{DroneLinks.DR_MAP}"
        self.auv_rel_frame = f"{self.robot_name}/{DroneLinks.AUV_RELATIVE_FRAME}"
        self.frame_suffix = self.get_parameter("frame_suffix").value
        self.odom_frame = f"{self.robot_name}/{DroneLinks.ODOM_LINK}{self.frame_suffix}"
        self.camera_frame = f"{self.robot_name}/{DroneLinks.CAMERA_LINK}{self.frame_suffix}"
        self.K = np.zeros([3, 3])
        self.check_distance_gt = False

        self.create_subscription(CameraInfo, f"/{self.robot_name}/{DroneTopics.CAMERA_INFO_TOPIC}", self.cam_param_cb, 10)
        self.odom_tf = True
        Q_str = self.get_parameter("process_noise").value
        R_str = self.get_parameter("measurement_noise").value
        P_str = self.get_parameter("state_covariance").value
        self.Q_auv_relative = np.array(Q_str).reshape(6, 6)
        self.R_auv_relative = np.array(R_str).reshape(3, 3)
        self.P_auv_relative = np.array(P_str).reshape(6, 6)

        self.R_cam_to_link = np.array([[0, 1, 0],
                                       [1, 0, 0],
                                       [0, 0, 1]])

        self.kf_auv = EKFModel_ImageFeedback('AUV_relative_position_estimator')

        self.create_subscription(Float32MultiArray, f"/{self.robot_name}/{DroneTopics.BUOY_DETECTOR_ESTIMATE_TOPIC}", self.buoy_cb, 10)
        self.create_subscription(Float32, f"/{self.robot_name}/{DroneTopics.DEPTH_TOPIC}", self.depth_cb, 10)
        self.auv_position_publisher = self.create_publisher(Odometry, f"/{self.robot_name}/{DroneTopics.AUV_RELATIVE_POSITION_TOPIC}", 10)

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        self.depth = None
        self.image_point = None
        self.X_auv_relative = None
        self.first_measurement = False

    def declare_node_parameters(self):
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
        self.K = np.array(msg.k).reshape(3, 3)
        self.K_inv = np.linalg.inv(self.K)

    def depth_cb(self, msg: Float32):
        self.depth = -msg.data

    def buoy_cb(self, msg: Float32MultiArray):
        u, v = msg.data[0], msg.data[1]
        self.image_point = np.array([u, v, 1])
        if self.image_point is not None:
            self.estimate_relative_position()

    def estimate_relative_position(self):
        observation = self.image_point.copy()
        observation[2] = self.depth
        if not self.first_measurement:
            self.X_auv_relative = self.get_first_measured_state(observation)
            self.kf_auv.initialize_state(self.X_auv_relative, self.Q_auv_relative, self.R_auv_relative, self.P_auv_relative, self.R_cam_to_link)
            self.first_measurement = True
        else:
            self.X_auv_relative, self.P_auv_relative = self.kf_auv.estimate(observation, self.R_cam_to_link, feedback_image=True)
            if self.check_distance_gt:
                try:
                    transform = self.tf_buffer.lookup_transform(
                        # 'sam_auv_v1/back_prop_link_gt',
                        'sam_auv_v1/Buoy_gt',
                        self.camera_frame,
                        self.get_clock().now()
                    )
                    self.get_logger().info(f"error bet gt and estimate: {np.linalg.norm(np.array([transform.transform.translation.x, transform.transform.translation.y, transform.transform.translation.z]) - self.X_auv_relative[:3])}")
                except Exception as e:
                    self.get_logger().warn(f"Transformation error: {e}")

        if self.X_auv_relative is not None:
            auv_rel_position = self.X_auv_relative[:3]
            self.publish_auv_position(auv_rel_position)
            self.publish_tf(auv_rel_position)

    def get_first_measured_state(self, observation):
        direction_vector = np.dot(self.K_inv, np.array([observation[0], observation[1], 1]))
        direction_world = np.dot(self.R_cam_to_link, direction_vector)
        scale = -self.depth / direction_world[2]
        vector_auv_drone = direction_world * scale
        self.get_logger().info(f"georeferenced coordinates of buoy: {vector_auv_drone}")
        return np.hstack((vector_auv_drone, np.zeros(3)))

    def publish_tf(self, position, orientation=None):
        if not self.odom_tf: 
            t = TransformStamped()
            t.header.stamp = self.get_clock().now().to_msg()
            t.header.frame_id = self.camera_frame
            t.child_frame_id = self.auv_rel_frame
            t.transform.translation.x, t.transform.translation.y, t.transform.translation.z = position
            if orientation:
                t.transform.rotation.x, t.transform.rotation.y, t.transform.rotation.z, t.transform.rotation.w = orientation
            else:
                t.transform.rotation.w = 1.0
            self.tf_broadcaster.sendTransform(t)
        else:
            try:
                point_camera = PointStamped()
                point_camera.point.x, point_camera.point.y, point_camera.point.z = np.dot(np.linalg.inv(self.R_cam_to_link), position)
                transform = self.tf_buffer.lookup_transform(
                    self.odom_frame,
                    self.camera_frame,
                    self.get_clock().now()
                )
                t_odom = TransformStamped()
                point_odom = tf2_geometry_msgs.do_transform_point(point_camera, transform)
                transformed_position = np.array([
                    point_odom.point.x,
                    point_odom.point.y,
                    point_odom.point.z
                ])
                t_odom.header.stamp = self.get_clock().now().to_msg()
                t_odom.header.frame_id = self.odom_frame
                t_odom.child_frame_id = self.auv_rel_frame
                t_odom.transform.translation.x, t_odom.transform.translation.y, t_odom.transform.translation.z = transformed_position
                t_odom.transform.rotation.w = 1.0
                self.tf_broadcaster.sendTransform(t_odom)
            except Exception as e:
                self.get_logger().warn(f"TF broadcast error: {e}")

    def publish_auv_position(self, position):
        msg = Odometry()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.odom_frame
        msg.child_frame_id = self.auv_rel_frame
        msg.pose.pose.position.x, msg.pose.pose.position.y, msg.pose.pose.position.z = position
        msg.pose.pose.orientation.w = 1.0
        self.auv_position_publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = AUVPositionEstimator()
    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
