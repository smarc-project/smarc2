import numpy as np
import rclpy
from sensor_msgs.msg import NavSatFix, Imu
from rclpy.node import Node

import random

class EKFModel_ImageFeedback(Node):

    def __init__(self, i):
        super().__init__(i)

        self.drone_acc = np.zeros([3,])
        self.timestep = 0
        self.M = np.zeros([1,6])
        self.M[0,2] = 1
        self.C = None
        self.A = np.zeros(6)
        self.B = np.zeros([6,3])

        # Camera intrinsic parameters(values taken from unity editor)
        self.f_x = 20.78461*640/36  # Focal length in pixels (x-direction)
        self.f_y = 20.78461*480/24  # Focal length in pixels (y-direction)
        self.c_x = 320  # Principal point x-coordinate
        self.c_y = 240  # Principal point y-coordinate
        self.R_wa = np.eye(3)
        
        self.K = np.array([[self.f_x, 0, self.c_x],
                           [0, self.f_y, self.c_y],
                           [0, 0, 1]])
        self.K_inv = np.linalg.inv(self.K)

    def initialize_state(self, X, Q, R, P,R_q):
        """
        Initialize the state, process noise, measurement noise, and covariance matrix.
        """

        self.X = X
        self.Q = Q
        self.R_1 = R
        self.P = P
        self.R_wa = np.array([[0, 1, 0],
                              [1, 0, 0],
                              [0, 0, 1]])

        self.obs = False
        

    def prediction_model(self) : 
        self.A = np.eye(self.X.shape[0])
        self.X = self.A @ self.X
        P_pred = self.A @ self.P @ self.A.T + self.Q  #pre and post multiply A to P 
        return self.X, P_pred

    def observation_model_image(self):
        """
        Observation model that predicts the measurement given the current state.
        """
        # x, y, z = self.X[0], self.X[1], -self.X[2]
        x, y, z = self.X[0], self.X[1], self.X[2]
        dir_world = [x/z,y/z,1]
        image_point = self.K@np.linalg.inv(self.R_wa)@(dir_world) #of the form [u,v,1]
        image_point[2] = -z   #self.X[2]
        # self.get_logger().info(f"observation model : {image_point}")
        return image_point

    def observation_model_no_image(self):
        """
        Observation model that predicts the measurement given the current state.
        """
        return self.M @ self.X

    def jacobian_image(self):
        # x, y, z = self.X[0], self.X[1], -self.X[2]  # Assuming X[2] is the depth
        x, y, z = self.X[0], self.X[1], self.X[2]  # Assuming X[2] is the depth

        # Avoid division by zero
        if z == 0:
            raise ValueError("Division by zero in Jacobian computation")

        # Compute the derivative of the normalized direction vector
        J_direction = np.array([
            [1/z, 0, -x/(z**2)],
            [0, 1/z, -y/(z**2)]
        ])

        # Jacobian is the multiplication of K, R_wa_inv, and J_direction
        R_wa_inv = np.linalg.inv(self.R_wa)  # Inverse of the rotation matrix
        jacobian_matrix = self.K[:2, :2] @ R_wa_inv[:2, :2] @ J_direction  # 2x3 Jacobian
        
        # Extend to 2x6 matrix (assuming the last 3 state variables don't affect the measurement)
        jacobian_extended = np.hstack((jacobian_matrix, np.zeros((2, 3))))

        # Add the depth row: [0, 0, 1, 0, 0, 0]
        depth_jacobian = np.array([[0, 0, -1, 0, 0, 0]])
        # depth_jacobian = np.array([[0, 0, 1, 0, 0, 0]])

        # Vstack the 2x6 jacobian with the 1x6 depth row
        jacobian_full = np.vstack((jacobian_extended, depth_jacobian))
        
        return jacobian_full

    def estimate(self, obs, R_q, feedback_image = False):
        """
        Perform the EKF estimation step: predict and update.
        """
        #predict
        # self.R_wa = R_q
        X_pred, P_pred = self.prediction_model()
        # self.get_logger().info(f' first predicted state : {X_pred} ')
        # update
        if (feedback_image) :
            self.C = self.jacobian_image()
            obs_model = self.observation_model_image()
            R = self.R_1
        else : 
            self.C = self.M
            obs_model = self.observation_model_no_image()
            R = np.eye(1)*10**-3
        # self.get_logger().info(f' image obs : {obs} and modelled : {obs_model} ')
        # self.get_logger().info(f' image obs : {obs}')
        S = self.C @ P_pred @ self.C.T + R
        
        K = P_pred @ self.C.T @ np.linalg.inv(S)
        self.X = X_pred + K @ (obs - obs_model)
        # self.get_logger().info(f' Kalman gain: {K} ')
        self.P = (np.eye(len(self.X)) - K @ self.C) @ P_pred
        # self.get_logger().info(f' first estimated state : {self.X} ')
        return self.X, self.P