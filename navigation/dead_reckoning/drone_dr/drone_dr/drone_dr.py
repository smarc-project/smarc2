import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix, Imu
from std_msgs.msg import Float32MultiArray, Float32
import numpy as np
from state_estimation.model_kf import KFModel_DoubleIntegrator
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
        # === Frames ===
        self.map_frame = self.get_parameter("map_frame").value

        self.odom_frame = f"{self.robot_name}/{DroneLinks.ODOM_LINK}"
        self.base_frame = f"{self.robot_name}/{DroneLinks.BASE_LINK}"
        # self.get_logger().info(f"Robot Name: {self.robot_name}")
        # self.get_logger().info(f"Map Frame: {self.map_frame}")
        # self.get_logger().info(f"UTM Frame: {self.utm_frame}")

        # Initialize a TF broadcaster
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        self.create_subscription(NavSatFix,f"/{self.robot_name}/{DroneTopics.GPS_TOPIC}", self.gps_cb, 10)
        self.create_subscription(Imu, f"/{self.robot_name}/{DroneTopics.IMU_TOPIC}", self.imu_cb, 10)
        self.create_subscription(Float32, f"/{self.robot_name}/{DroneTopics.DEPTH_TOPIC}", self.depth_cb, 10)
        self.get_logger().info(f"/{self.robot_name}/{DroneTopics.GPS_TOPIC}")
        # self.position_publisher = self.create_publisher(Float32MultiArray, f"/{self.robot_name}/{DroneTopics.DR_POSITION_TOPIC}", 10)
        self.position_publisher = self.create_publisher(Odometry, f"/{self.robot_name}/{DroneTopics.DR_POSITION_TOPIC}", 10)

        self.gps_coordinates = None
        self.gps_iter = 0
        self.saved_gps_iter = 0

        # Drone KF model
        self.kf_drone = KFModel_DoubleIntegrator('drone_position_estimator')
        self.X_drone = None
        self.Q_drone = np.eye(6) * 10 ** -3  # IMU Noise
        self.R_drone = np.eye(3) * 10 ** -4  # GPS Noise
        self.P_drone = np.block([[np.eye(3)*10**(-3), np.zeros((3,3))],
                                 [np.zeros((3,3)), np.eye(3)*10**(-2)]])  # Velocity with high uncertainty
        self.kf_drone_initialized = False

        self.drone_acc = np.zeros(3)
        self.timestep = 0
        self.prev_time = None

        # tf2 buffer for IMU transformation
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

    def declare_node_parameters(self):
        """
        Declare the node parameters for the dr node

        :return:
        """
        default_robot_name = "Quadrotor"
        self.declare_parameter("robot_name", default_robot_name)
        # === Frames ===
        self.declare_parameter("map_frame", "map")
        
    def gps_cb(self, msg: NavSatFix) -> None:
        drone_utm = utm.fromLatLong(msg.latitude, msg.longitude)
        #FIXME magic numbers!
        # It looks like this is a constant offset between the GPS and the map/odom frame
        # if its utm->odom, then the offset should be set by the first GPS input and kept constant from there.
        # if its utm->map, then it should either be given (because someone wants the map to start somewhere specific) or already 
        # be present in the TF tree (because theres a SLAM system running)
        self.gps_coordinates = np.array([drone_utm.easting - 651301.133, drone_utm.northing - 6524094.583 + 1000, msg.altitude])
        self.gps_iter += 1

    def depth_cb(self, msg: Float32) -> None:
        self.depth = msg.data

    def imu_cb(self, msg):
        self.drone_acc[0] = msg.linear_acceleration.x
        self.drone_acc[1] = msg.linear_acceleration.y
        self.drone_acc[2] = msg.linear_acceleration.z
        current_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

        if self.prev_time is not None:
            self.timestep = current_time - self.prev_time
        self.prev_time = current_time

        try:
            imu_accel = Vector3Stamped()
            imu_accel.header.stamp = msg.header.stamp
            #FIXME self.base_frame no?
            imu_accel.header.frame_id = "drone_base_link"
            imu_accel.vector.x = self.drone_acc[0]
            imu_accel.vector.y = self.drone_acc[1]
            imu_accel.vector.z = self.drone_acc[2]

            transform = self.tf_buffer.lookup_transform(
                # "map_gt", "Quadrotor/base_link_gt", rclpy.time.Time()
                self.map_frame, self.base_frame, rclpy.time.Time()
            )

            world_accel = tf2_geometry_msgs.do_transform_vector3(imu_accel, transform)

            self.drone_acc[0] = world_accel.vector.x
            self.drone_acc[1] = world_accel.vector.y
            self.drone_acc[2] = world_accel.vector.z

        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException) as e:
            self.get_logger().warn(f"TF lookup failed: {e}")

        self.estimate_position()

    def estimate_position(self):
        gps_feedback_received = (self.gps_iter > self.saved_gps_iter)

        if not self.kf_drone_initialized:
            if self.gps_coordinates is not None:
                self.X_drone = np.array([self.gps_coordinates, np.zeros(3)]).flatten().T
                self.kf_drone.initialize_state(self.X_drone, self.Q_drone, self.R_drone, self.P_drone)
                self.kf_drone_initialized = True
        else:
            if gps_feedback_received:
                self.saved_gps_iter = self.gps_iter
                self.X_drone, self.P_drone = self.kf_drone.estimate(self.gps_coordinates, self.timestep, self.drone_acc)
            else:
                self.X_drone, self.P_drone = self.kf_drone.motion_model(self.drone_acc, self.timestep)

        if self.X_drone is not None:
            self.publish_position(self.X_drone[:3])
            self.publish_tf(self.X_drone[:3])

    # def publish_position(self, position):
    #     self.get_logger().info(f"position being published :  {position}")
    #     position_msg = Float32MultiArray(data=position)
    #     self.position_publisher.publish(position_msg)
    
    def publish_position(self, position):
        self.get_logger().info(f"position being published : {position}")
        
        # Create an Odometry message
        odom_msg = Odometry()
        
        # Set header information
        odom_msg.header.stamp = self.get_clock().now().to_msg()  # Add timestamp
        #FIXME so the odom topic has the position of the drone in the odom frame
        # but the TF publisher seems to publish the position of "drone_estimated_state" in the map frame
        # yet they are publishing the same _numbers_ (position) so one of these need to change.
        # given "drone_estimated_state" is an ad-hoc frame undefined anywhere else, i'd wager
        # publish_tf needs to publish base_link in odom frame and not touch the map frame.
        odom_msg.header.frame_id = "odom"  # Typically, "odom" frame for localization
        
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
        self.position_publisher.publish(odom_msg)

    def publish_tf(self, position, orientation=None):
        # Create a TransformStamped message
        t = TransformStamped()

        # Set the frame information
        t.header.stamp = self.get_clock().now().to_msg()
        #FIXME map->drone_estimated_state?? wtf is this frame?
        t.header.frame_id = self.map_frame  # Parent frame
        t.child_frame_id = 'drone_estimated_state'  # Child frame for the estimated state

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


def main(args=None):
    rclpy.init(args=args)
    node = DronePositionEstimator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
