import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import NavSatFix, Imu, FluidPressure
from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import Point
import numpy as np
from model_ekf import EKFModel

class GeoreferencingNode(Node):
    def __init__(self):
        super().__init__('georeferencing_node')

        # Subscribe to odometry and minimum gradient point topics
        self.create_subscription(Odometry, '/Quadrotor/odom_gt', self.odom_cb, 10)
        self.create_subscription(Float32MultiArray, '/drone/buoy_est', self.min_gradient_cb, 10)
        self.create_subscription(Imu, '/drone/imu', self.imu_cb, 10)
        self.create_subscription(FluidPressure, '/drone/depth', self.depth_cb, 10)

        # Publisher for georeferenced coordinates
        self.georef_publisher = self.create_publisher(Float32MultiArray, '/drone/georeferenced_coordinates', 10)
        #self.georef_publisher = self.create_publisher(Point, '/drone/georeferenced_point', 10)

        # UAV's position and orientation
        self.x_w = None
        self.v_w = None
        self.prev_x_w = None
        self.R_wa = None
        self.kf_initialized = False #turn off when initialized

        # Camera intrinsic parameters (example values)
        self.f_x = 20.78461*640/36  # Focal length in pixels (x-direction)
        self.f_y = 20.78461*480/24  # Focal length in pixels (y-direction)
        self.c_x = 320  # Principal point x-coordinate
        self.c_y = 240  # Principal point y-coordinate

        self.K = np.array([[self.f_x, 0, self.c_x],
                           [0, self.f_y, self.c_y],
                           [0, 0, 1]])
        self.K_inv = np.linalg.inv(self.K)

        #KALMAN FILTER ESTIMATION
        #define the covariances
        self. kf = EKFModel('AUV_relative_position_estimator')
        self.Q = np.eye(6) * 10**-3  # Process noise covariance
        # self.R = np.eye(2) * 10**-2  # Measurement noise covariance for 2D measurements (x, y)
        self.R = np.eye(3) * 10**-3
        self.R[2,2] = 10**-6
        self.P = np.eye(6) * 10**-2  # Initial state covariance
        self.P[3,3] = self.P[4,4] = self.P[5,5] = 10**-1
        self.first_measurement = True
        self.depth = None
        self.georef_coords = None
        self.drone_acc = np.zeros([3,])
        self.timestep = 0
        self.prev_time = None
        self.mg_callback_recieved = False
        self.odom_state = None

        # Store time for timestep calculations
        self.last_time = None

    def depth_cb(self, msg: FluidPressure) -> None :
        self.depth = msg.fluid_pressure
        # print("callback depth is : " + str(self.depth))
        
    def odom_cb(self, msg: Odometry) -> None:
        # Extract UAV's position in the world frame
        self.x_w = np.array([msg.pose.pose.position.x, msg.pose.pose.position.y, msg.pose.pose.position.z])
        self.v_w = np.array([msg.twist.twist.linear.x, msg.twist.twist.linear.y, msg.twist.twist.linear.z])
        self.odom_state = np.array([self.x_w, self.v_w]).flatten().T
        print("odometry state : " + str(self.odom_state))
        # # Extract UAV's orientation as a rotation matrix
        # self.R_wa = self._quat2mat((msg.pose.pose.orientation.x,
        #                             msg.pose.pose.orientation.y,
        #                             msg.pose.pose.orientation.z,
        #                             msg.pose.pose.orientation.w))
        self.R_wa = np.eye(3)

    def min_gradient_cb(self, msg: Float32MultiArray) -> None:
        if self.x_w is not None and self.R_wa is not None:
            u, v = msg.data[0], msg.data[1]  # Get the pixel coordinates of the min gradient point
            self.georef_coords = self.georeference(u, v)
            # self.first_measurement = False
            self.prev_x_w = self.x_w
            #print((u,v))
            self.publish_georeferenced_coordinates(self.georef_coords)
            self.mg_callback_recieved = False
            
        else:
            self.get_logger().info("Waiting for odometry data...")

    def imu_cb(self, msg) : 
        self.drone_acc[0] = msg.linear_acceleration.x
        self.drone_acc[1] = msg.linear_acceleration.y
        self.drone_acc[2] = msg.linear_acceleration.z
        # print("drone_acc" + str(self.drone_acc))
        # Get the current time from the message header
        current_time = msg.header.stamp.sec + msg.header.stamp.nanosec*1e-9
        if self.prev_time is not None:
            self.timestep = (current_time - self.prev_time)    #.nanoseconds * 1e-9  # Convert from nanoseconds to seconds
            print("timstep : " + str(self.timestep) + "acceleration : " + str(self.drone_acc))
            # Now you can use `timestep` in your state estimation process
            # self.get_logger().info(f"Timestep: {self.timestep} seconds")
        #  Update previous time to the current time for the next iteration
        self.prev_time = current_time

        if not self.first_measurement and  not self.mg_callback_recieved and self.depth is not None:
            
            self.X,self.P = self.kf.estimate(self.depth, self.timestep, self.drone_acc)
            # self.get_logger().info("only depth feedback estimate : " + str( self.X.T))///////////////////////////////
            # print("predicted velocity : " + str(self.X.T[3:]))
            # print("Actual velocity : " + str([self.v_w[0],self.v_w[2],self.v_w[1]]))
            # print("only prediction based state : " + str(self.x_w - self.X.T[0:3]) + " " + str())
            # print("error in predicted state : " + str(self.odom_state - self.X.T)) #AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        elif not self.first_measurement and  not self.mg_callback_recieved and self.depth is  None:
            self.X, self.P = self.kf.motion_model(self.drone_acc, self.timestep)  # THIS IS ONLY MOTION /PREDICTION MODEL
            # self.get_logger().info("only prediction estimate : " + str(self.X.T))////////////////////////////////////////

        self.mg_callback_recieved = False


    def georeference(self, u, v):
        # Convert pixel coordinates to the camera coordinate system
        image_point = np.array([u, 
                                v, 1])
        direction_vector = np.dot(self.K_inv, image_point)
        # self.get_logger().info(f"position in image from center: {u - 320,v - 240}")
        # Debug: Print the direction vector before and after transformation
        # self.get_logger().info(f"Direction vector (camera frame): {direction_vector}")

        # Transform direction vector to the world frame using the UAV's orientation
        direction_world = np.dot(self.R_wa, direction_vector)

        # Debug: Print the direction vector in world frame
        # self.get_logger().info(f"Direction vector (world frame): {direction_world}")

        # Scale by altitude to find the intersection with sea level
        sea_level_z = float(0.0) #replace with subscribah
        # self.depth = self.x_w[2] -  sea_level_z
        scale = self.depth / direction_world[2]
        direction_world_corrected = scale * direction_world
        direction_world_corrected[2] = direction_world_corrected[2]*-1
        world_coordinates = self.x_w + scale * direction_world_corrected
        # print("in the calculation model" + str(image_point))
        # print("in the calculation model" + str(world_coordinates))
        
        # print("in the calculation model" + str(np.array([-scale * direction_world[0], -scale * direction_world[1], self.depth])))

        # self.observation = np.array([-scale * direction_world[0], -scale * direction_world[1]]).T
        self.observation = image_point
        self.observation[2] = self.depth 

        # Convert to real-world coordinates
        real_world_x = world_coordinates[0]
        real_world_y = world_coordinates[1]
        real_world_z = sea_level_z  # Sea level

        # self.get_logger().info(f"Drone coordinates: {self.x_w}")
        # self.get_logger().info(f"Georeferenced coordinates: X={real_world_x}, Y={real_world_y}, Z={real_world_z}")
        
        #ESTIMATION
        if(self.prev_x_w is None):
            return [real_world_x, real_world_y, real_world_z]
        if(self.first_measurement and self.prev_x_w is not None):
            # velocity_vector = (self.x_w - self.prev_x_w)/self.timestep
            velocity_vector = self.v_w
            # print("intial velocity state : " + str(velocity_vector))
            # self.X = np.array([real_world_x, real_world_y, self.depth,velocity_vector[0],velocity_vector[1],velocity_vector[2]]).T
            # self.X = np.array([-scale * direction_world[0], -scale * direction_world[1], self.depth,velocity_vector[0],velocity_vector[1],velocity_vector[2]]).T
            # print("odometry state : " + str(np.array([self.x_w, self.v_w]).reshape([6,1])))
            self. X = np.array([self.x_w, self.v_w]).flatten().T#.reshape([6,1])
            self.kf.initialize_state(self.X, self.Q, self.R, self.P)
            self.first_measurement = False
        else : 
            self.X, self.P = self.kf.estimate(self.observation, self.timestep, self.drone_acc, feedback_image = True)
            # self.get_logger().info("image point feedback estimate : " + str(self.X.T))/////////////////////////////
            # print("estimated velocity : " + str(self.X.T[3:]))
            # print("actual velocity : " + str([self.v_w[0],self.v_w[2],self.v_w[1]]))
            # print("estimation based state : " + str(self.x_w - self.X.T[0:3]))
        # print("the measurement is: " + str(np.array([real_world_x, real_world_y])))
        # print("the position kalman estimate is" + str(self.x_w - self.X.T[0:3]))
        
        return [real_world_x, real_world_y, real_world_z]

    def publish_georeferenced_coordinates(self, coords):
        # Create a message for the georeferenced coordinates
        georef_msg = Float32MultiArray(data=coords)
        self.georef_publisher.publish(georef_msg)
        # self.get_logger().info(f"Published georeferenced coordinates: {coords}")

    def _quat2mat(self, quat):
        # Convert quaternion to rotation matrix
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
