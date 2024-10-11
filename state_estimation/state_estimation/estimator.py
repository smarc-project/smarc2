import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import NavSatFix, Imu, FluidPressure
from std_msgs.msg import Float32MultiArray,Float32
from geometry_msgs.msg import Point, TransformStamped, Vector3Stamped
import numpy as np
from state_estimation.model_kf import KFModel_DoubleIntegrator
from state_estimation.model_ekf import EKFModel_ImageFeedback
# from visualization_msgs.msg import Marker, MarkerArray
from geodesy import utm
import tf2_ros
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
import tf2_geometry_msgs

class GeoreferencingNode(Node):
    def __init__(self):
        super().__init__('georeferencing_node')

        # self.create_subscription(Odometry, '/Quadrotor/odom_gt', self.odom_cb, 10)
        self.create_subscription(Float32MultiArray, '/drone/buoy_est', self.min_gradient_cb, 10)
        self.create_subscription(Imu, '/drone/imu', self.imu_cb, 10)
        self.create_subscription(Float32, '/drone/depth', self.depth_cb, 10)
        self.create_subscription(NavSatFix,'/drone/gps', self.gps_cb, 10)

         # Initialize a TF broadcaster
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        self.georef_publisher = self.create_publisher(Float32MultiArray, '/drone/georeferenced_coordinates', 10)
        # self.marker_publisher = self.create_publisher(Marker, '/drone/estimated_states_marker', 10)
        self.gps_coordinates = None
        self.gps_iter = 0
        self.saved_gps_iter = 0
        self.detector_iter = 0
        self.saved_detector_iter = 0


        self.x_w = None
        self.v_w = None
        self.prev_x_w = None
        # self.R_wa = None REMOVE THE EYE AND PUT THE IMU ORIENTATION LATER. HOW TO GET ORIENTATION FEEDBACK??????
        self.R_wa = np.eye(3)
        self.kf_drone_initialized = False

        self.f_x = 20.78461 * 640 / 36
        self.f_y = 20.78461 * 480 / 24
        self.c_x = 320
        self.c_y = 240
        self.image_point = None
        self.K = np.array([[self.f_x, 0, self.c_x],
                           [0, self.f_y, self.c_y],
                           [0, 0, 1]])
        self.K_inv = np.linalg.inv(self.K)
        #drone kf and its params and covariances
        self.kf_drone = KFModel_DoubleIntegrator('drone_position_estimator')
        self.X_drone = None
        self.Q_drone = np.eye(6) * 10 ** -3 #IMU Noise
        self.R_drone = np.eye(3) * 10 ** -4 #GPS Noise
        self.P_drone = np.block([[np.eye(3)*10**(-3), np.zeros((3,3))],
                                        [np.zeros((3,3)), np.eye(3)*10**(-2)]])  # initializing velocity with 0s and high uncertainity

        #auv kf and its params and covariances
        self.kf_auv = EKFModel_ImageFeedback('AUV_relative_position_estimator')
        self.Q_auv_relative = np.eye(6) * 10 ** -3   #Gaussian Process Noise 
        self.R_auv_relative = np.eye(3) * 10 ** -3   #Detector Measurement noise
        self.R_auv_relative[2, 2] = 10 ** -6
        
        self.P_auv_relative = np.eye(6) * 10 ** -2
        #the world estimate of AUV
        self.X_auv_world = None

        #logic bools for estimation
        self.first_measurement = False
        self.depth = None
        self.georef_coords = None
        self.drone_acc = np.zeros(3)
        self.timestep = 0
        self.prev_time = None
        self.mg_callback_recieved = False
        self.odom_state = None

        self.last_time = None

        #tf2_buffer to get the ground truth position of the buoy
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

    def depth_cb(self, msg: Float32) -> None:
        self.depth = msg.data

    def gps_cb(self, msg : NavSatFix) -> None:
        drone_utm = utm.fromLatLong(msg.latitude, msg.longitude)
        
        self.gps_coordinates = np.array([drone_utm.easting - 651301.133, drone_utm.northing - 6524094.583 +1000, msg.altitude ])
        self.gps_iter+=1
        # self.get_logger().info(f'gps drone in world coordinates : {self.gps_coordinates}'  )
        # self.gps_coordinates[1] = drone_utm.northing - 6524094.583 +980
        # self.gps_coordinates[2] = msg.altitude 
        
    # def odom_cb(self, msg: Odometry) -> None:
    #     self.x_w = np.array([msg.pose.pose.position.x, msg.pose.pose.position.y, msg.pose.pose.position.z])
    #     self.v_w = np.array([msg.twist.twist.linear.x, msg.twist.twist.linear.y, msg.twist.twist.linear.z])
    #     self.odom_state = np.array([self.x_w, self.v_w]).flatten().T
    #     self.R_wa = np.eye(3)

    def min_gradient_cb(self, msg: Float32MultiArray) -> None:
        if self.gps_coordinates is not None :
            self.detector_iter+=1
            u, v = msg.data[0], msg.data[1]
            self.first_measurement = True if self.image_point is None else False
            self.image_point = np.array([u, v, 1])   
            
        else:
            self.get_logger().info("Waiting for odometry data...")

    def imu_cb(self, msg):
        self.drone_acc[0] = msg.linear_acceleration.x
        self.drone_acc[1] = msg.linear_acceleration.y
        self.drone_acc[2] = msg.linear_acceleration.z
        current_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

        # If we have a previous timestamp, calculate the timestep
        if self.prev_time is not None:
            self.timestep = current_time - self.prev_time
        self.prev_time = current_time

        # Convert IMU linear acceleration from drone frame to world frame
        try:
            # Prepare IMU data as a Vector3Stamped message in drone frame
            imu_accel = Vector3Stamped()
            imu_accel.header.stamp = msg.header.stamp
            imu_accel.header.frame_id = "drone_base_link"  # Frame where IMU data is located
            imu_accel.vector.x = self.drone_acc[0]
            imu_accel.vector.y = self.drone_acc[1]
            imu_accel.vector.z = self.drone_acc[2]

            # Look up the transformation from drone frame to world frame (e.g., "world" frame)
            transform = self.tf_buffer.lookup_transform(
                "map_gt",  # Target frame (world)
                "Quadrotor/base_link_gt",  # Source frame (drone's IMU frame)
               rclpy.time.Time(),  # Transform time at the IMU message timestamp
                # rclpy.duration.Duration(seconds=1.0)  # Timeout for lookup
            )
            # Transform the IMU acceleration into the world frame
            world_accel = tf2_geometry_msgs.do_transform_vector3(imu_accel, transform)

            # Use transformed acceleration for state estimation
            self.drone_acc[0] = world_accel.vector.x
            self.drone_acc[1] = world_accel.vector.y
            self.drone_acc[2] = world_accel.vector.z
            self.get_logger().info(f'imu acceleration data : {self.drone_acc}'  )

        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException) as e:
            self.get_logger().warn(f"TF lookup failed: {e}")
        
        # Perform state estimation
        estimated_coords = self.estimation()

        # If estimation is successful, publish the estimated coordinates
        if estimated_coords is not None:
            self.publish_georeferenced_coordinates(estimated_coords)

    def publish_tf(self, position, orientation=None):
        # Create a TransformStamped message
        t = TransformStamped()

        # Set the frame information
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'Quadrotor/map_gt'  # Parent frame
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

    def estimation(self):
        # image_point = np.array([u, v, 1])
        
        
        if self.image_point is not None:
            observation = self.image_point.copy()
            observation[2] = self.depth 


        gps_feedback_recieved = (self.gps_iter > self.saved_gps_iter)
        image_feedback_recieved = (self.detector_iter > self.saved_detector_iter)
        #initialize drone kf
        if not self.kf_drone_initialized :
            if self.gps_coordinates is not None :
                self.X_drone = np.array([self.gps_coordinates, np.zeros(3)]).flatten().T
                self.kf_drone.initialize_state(self.X_drone, self.Q_drone, self.R_drone, self.P_drone)
                self.kf_drone_initialized = True
        #estimate and propogate model in drone kf 
        else :
            if gps_feedback_recieved :
                self.saved_gps_iter = self.gps_iter
                self.X_drone,self.P_drone = self.kf_drone.estimate(self.gps_coordinates, self.timestep, self.drone_acc)
            else:
                self.X_drone,self.P_drone = self.kf_drone.motion_model(self.drone_acc,self.timestep)

        if self.first_measurement:
            # self.X = np.array([self.x_w, self.v_w]).flatten().T #GROUND TRUTH INITIALIZATION
            
            self.X_auv_relative = self.get_first_measured_state(self.image_point)
            self.kf_auv.initialize_state(self.X_auv_relative, self.Q_auv_relative, self.R_auv_relative, self.P_auv_relative)
            
        elif image_feedback_recieved :
            self.saved_detector_iter = self.detector_iter
            self.X_auv_relative, self.P_auv_relative = self.kf_auv.estimate(observation, feedback_image=True)
            
        #get the ground truth position of the buoy from the buffer
        try:
            tf = self.tf_buffer.lookup_transform('map_gt', 'sam_auv_v1/RopeLink(Clone)_18_buoy_gt', rclpy.time.Time())#self.t_prev)
            buoy_position = np.array([tf.transform.translation.x, tf.transform.translation.y, tf.transform.translation.z])
            self.get_logger().info(f'buoys ground truth state in world coordinates : {buoy_position}' )
        except : 
            self.get_logger().info(f'buoys gt not published' )
        #logic to integrate drone and auv filters
        if image_feedback_recieved : self.X_auv_world = self.X_drone + self.X_auv_relative
        if self.X_auv_world is not None : 
            # publish to transform tree
            # self.get_logger().info(f'Drones estimated state in world coordinates : {self.X_drone[0:3]}'  )

            # self.get_logger().info(f'buoys estimated state in world coordinates : {self.X_auv_world[0:3]}' )
            self.publish_tf(self.X_auv_world[0:3])
            return self.X_auv_world[0:3]
        return None

    def get_first_measured_state(self, image_point):
        direction_vector = np.dot(self.K_inv, self.image_point)
        # direction_vector = np.dot(self.K_inv, np.array([320, 240, 1]))
        direction_world = np.dot(self.R_wa, direction_vector)

        sea_level_z = float(0.0)
        scale = self.depth / direction_world[2]
        direction_world[2] = direction_world[2] * -1
        vector_auv_drone = direction_world * scale
        self.first_measurement = False
        # self.get_logger().info(f'image point : {self.image_point}'  )
        # self.get_logger().info(f'first measured relative position : {vector_auv_drone}' )
        # self.get_logger().info(f'and the drone gps position at the time : {self.gps_coordinates}' )
        # buoy_position = self.X_drone[0:3] + vector_auv_drone
        # self.get_logger().info(f'first buoy estimate : {buoy_position}' )
        return np.array([vector_auv_drone, np.zeros(3)]).flatten().T
    
    def publish_georeferenced_coordinates(self, coords):
        georef_msg = Float32MultiArray(data=coords)
        self.georef_publisher.publish(georef_msg)

    def _quat2mat(self, quat):
        x, y, z, w = quat
        R = np.array([
            [1 - 2 * (y ** 2 + z ** 2), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x ** 2 + z ** 2), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x ** 2 + y ** 2)]
        ])
        return R

def main(args=None):
    rclpy.init(args=args)
    georeferencing_node = GeoreferencingNode()
    rclpy.spin(georeferencing_node)
    georeferencing_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
