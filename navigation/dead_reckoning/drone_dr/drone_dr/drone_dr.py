import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix, Imu
from std_msgs.msg import Float32MultiArray, Float32
import numpy as np
from drone_dr.model_kf import KFModel_DoubleIntegrator
from geodesy import utm
import tf2_ros
import tf2_geometry_msgs
from geometry_msgs.msg import Vector3Stamped, TransformStamped
from nav_msgs.msg import Odometry
# import links and topics as params for drone
from drone_msgs.msg import Links as DroneLinks
from drone_msgs.msg import Topics as DroneTopics

class DronePositionEstimator(Node):
    def __init__(self):
        super().__init__('drone_position_estimator')

        # ===== Declare parameters =====
        self.declare_node_parameters()
        # ===== Get parameters =====
        self.robot_name = self.get_parameter("robot_name").value
        self.utm_frame =  f"{DroneLinks.GLOBAL_ORIGIN}"
        self.map_frame =  f"{self.robot_name}/{DroneLinks.DR_MAP}"
        self.odom_frame = f"{self.robot_name}/{DroneLinks.ODOM_LINK}"  # New odom frame for the drone
        self.base_frame = f"{self.robot_name}/{DroneLinks.BASE_LINK}"

        # Initialize a TF broadcaster
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Subscriptions
        self.create_subscription(NavSatFix, f"/{self.robot_name}/{DroneTopics.GPS_TOPIC}", self.gps_cb, 10)
        self.create_subscription(Imu, f"/{self.robot_name}/{DroneTopics.IMU_TOPIC}", self.imu_cb, 10)
        # self.create_subscription(Float32, f"/{self.robot_name}/{DroneTopics.DEPTH_TOPIC}", self.depth_cb, 10)

        # Odometry Publisher
        self.position_publisher = self.create_publisher(Odometry, f"/{self.robot_name}/{DroneTopics.DR_POSITION_TOPIC}", 10)

        # GPS and Offset Initialization
        self.gps_coordinates = None
        self.gps_iter = 0
        self.saved_gps_iter = 0
        self.utm_offset = None  # Offset to translate UTM coordinates to the odom frame
        self.offset_initialized = False  # Boolean flag to check if utm offset is set
        self.map_offset = self.get_parameter("map_offset").value
        
        # Drone KF model
        self.kf_drone = KFModel_DoubleIntegrator('drone_position_estimator')
        self.X_drone = None
        self.kf_drone_initialized = False
        Q_str = self.get_parameter("process_noise").value
        R_str = self.get_parameter("measurement_noise").value
        P_str = self.get_parameter("state_covariance").value
        self.Q_drone = np.zeros([6, 6])
        self.R_drone = np.zeros([3, 3])
        self.P_drone = np.zeros([6, 6])
        self.Q_drone = np.array(Q_str).reshape(6, 6)
        self.R_drone = np.array(R_str).reshape(3, 3)
        self.P_drone = np.array(P_str).reshape(6, 6)
        self.drone_acc = np.zeros(3)
        self.timestep = 0
        self.prev_time = None

    def declare_node_parameters(self):
        """
        Declare the node parameters for the node
        """
        default_robot_name = "Quadrotor"
        self.declare_parameter("robot_name", default_robot_name)
        self.declare_parameter("use_provided_map_origin", False)
        # Initialize map_offset as a Vector3Stamped with all entries set to zero
        default_map_offset = None
        self.declare_parameter("map_offset", default_map_offset)

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

        
        # self.declare_parameter("process_noise", default_q_matrix)
        # self.declare_parameter("measurement_noise", default_r_matrix)
        # self.declare_parameter("state_covariance", default_p_matrix)
        
    def gps_cb(self, msg: NavSatFix) -> None:
        """
        GPS callback to initialize UTM offset based on the first GPS reading.
        """
        if not self.offset_initialized:
            self.initialize_offset(msg)
        if self.offset_initialized:
            # Calculate the GPS coordinates adjusted by the UTM offset
            drone_utm = utm.fromLatLong(msg.latitude, msg.longitude)
            self.gps_coordinates = np.array([drone_utm.easting, drone_utm.northing, msg.altitude]) - self.utm_offset
            self.gps_iter += 1

    def initialize_offset(self, msg: NavSatFix):
        """
        Initialize the offset by using the first GPS ping to define the new map origin.
        """
        # Get UTM coordinates for the initial GPS reading
        drone_utm = utm.fromLatLong(msg.latitude, msg.longitude)
        self.utm_offset = np.array([drone_utm.easting, drone_utm.northing, msg.altitude])
        self.offset_initialized = True

        # Publish the initial transform from map to odom
        self.publish_utm_to_map_to_odom_transforms()
        self.get_logger().info(f"Map to odom transform initialized with offset: {self.utm_offset}")

    def publish_utm_to_map_to_odom_transforms(self):
        """
        Publish static transforms from 'utm' to 'map' and 'map' to 'odom' based on initial readings.
        """
        # Publish the initial UTM to Map transformation
        t_map = TransformStamped()
        t_map.header.stamp = self.get_clock().now().to_msg()
        t_map.header.frame_id = self.utm_frame  # UTM as the origin frame
        t_map.child_frame_id = self.map_frame

        if self.map_offset is not None:
            # Apply map offset transformation if map_offset is set
            t_map.transform.translation.x = self.map_offset[0]
            t_map.transform.translation.y = self.map_offset[1]
            t_map.transform.translation.z = self.map_offset[2]
        else:
            # If map_offset is None, use utm_offset as fallback
            t_map.transform.translation.x = self.utm_offset[0]
            t_map.transform.translation.y = self.utm_offset[1]
            t_map.transform.translation.z = self.utm_offset[2]

        t_map.transform.rotation.x = 0.0
        t_map.transform.rotation.y = 0.0
        t_map.transform.rotation.z = 0.0
        t_map.transform.rotation.w = 1.0  # Identity quaternion for no rotation

        # Publish "utm" to "map" transform
        self.tf_broadcaster.sendTransform(t_map)

        # Publish the initial Map to Odom transformation
        t_odom = TransformStamped()
        t_odom.header.stamp = self.get_clock().now().to_msg()
        t_odom.header.frame_id = self.map_frame  # Using "map" as the origin frame now
        t_odom.child_frame_id = self.odom_frame

        # Set the translation (initial offset from Map to Odom)
        t_odom.transform.translation.x = self.utm_offset[0] - self.map_offset[0] if self.map_offset is not None else self.utm_offset[0]
        t_odom.transform.translation.y = self.utm_offset[1] - self.map_offset[1] if self.map_offset is not None else self.utm_offset[1]
        t_odom.transform.translation.z = self.utm_offset[2] - self.map_offset[2] if self.map_offset is not None else self.utm_offset[2]
        t_odom.transform.rotation.x = 0.0
        t_odom.transform.rotation.y = 0.0
        t_odom.transform.rotation.z = 0.0
        t_odom.transform.rotation.w = 1.0  # Identity quaternion for no rotation

        # Publish the "map" to "odom" transform
        self.tf_broadcaster.sendTransform(t_odom)

    def imu_cb(self, msg):
        # Store the linear acceleration
        self.drone_acc[0] = msg.linear_acceleration.x
        self.drone_acc[1] = msg.linear_acceleration.y
        self.drone_acc[2] = msg.linear_acceleration.z
        current_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

        # Store the orientation from IMU directly
        self.orientation = [
            msg.orientation.x,
            msg.orientation.y,
            msg.orientation.z,
            msg.orientation.w
        ]

        # Calculate timestep
        if self.prev_time is not None:
            self.timestep = current_time - self.prev_time
        self.prev_time = current_time

        # Call the position estimation function
        self.estimate_position()

    def estimate_position(self):
        gps_feedback_received = (self.gps_iter > self.saved_gps_iter)

        if not self.kf_drone_initialized and self.gps_coordinates is not None:
            self.X_drone = np.array([self.gps_coordinates, np.zeros(3)]).flatten().T
            self.kf_drone.initialize_state(self.X_drone, self.Q_drone, self.R_drone, self.P_drone)
            self.kf_drone_initialized = True
        elif self.kf_drone_initialized:
            if gps_feedback_received:
                self.saved_gps_iter = self.gps_iter
                self.X_drone, self.P_drone = self.kf_drone.estimate(self.gps_coordinates, self.timestep, self.drone_acc)
            else:
                self.X_drone, self.P_drone = self.kf_drone.motion_model(self.drone_acc, self.timestep)

        if self.X_drone is not None:
            self.publish_position(self.X_drone[:3])
            self.publish_tf(self.X_drone[:3])

    def publish_position(self, position):
        self.get_logger().info(f"Position being published: {position}")
        
        # Create an Odometry message
        odom_msg = Odometry()
        
        # Set header information
        odom_msg.header.stamp = self.get_clock().now().to_msg()  # Timestamp
        odom_msg.header.frame_id = self.odom_frame  # "odom" frame for publishing
        
        # Set position
        odom_msg.pose.pose.position.x = position[0]
        odom_msg.pose.pose.position.y = position[1]
        odom_msg.pose.pose.position.z = position[2]

        # Identity quaternion for orientation
        odom_msg.pose.pose.orientation.w = 1.0

        # Publish the Odometry message
        self.position_publisher.publish(odom_msg)

    def publish_tf(self, position, orientation=None):
        """
        Publish the drone's estimated position in the odom frame relative to base_link.
        """
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = self.odom_frame
        t.child_frame_id = self.base_frame

        # Translation
        t.transform.translation.x = position[0]
        t.transform.translation.y = position[1]
        t.transform.translation.z = position[2]

        # Apply the IMU orientation directly
        if self.orientation is not None:
            t.transform.rotation.x = self.orientation[0]
            t.transform.rotation.y = self.orientation[1]
            t.transform.rotation.z = self.orientation[2]
            t.transform.rotation.w = self.orientation[3]
        else:
            t.transform.rotation.w = 1.0  # Default to identity if no orientation is set
        
        # Broadcast the transform
        self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = DronePositionEstimator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()