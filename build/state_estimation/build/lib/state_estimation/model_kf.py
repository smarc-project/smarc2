import numpy as np
import rclpy
from sensor_msgs.msg import NavSatFix, Imu
from rclpy.node import Node

import random

class KFModel_DoubleIntegrator(Node):

    def __init__(self, i):
        super().__init__(i)

        self.drone_acc = np.zeros([3,])
        self.timestep = 0
        self.M = np.block([[np.eye(3), np.zeros((3,3))]])
        # self.M[0,0] = 1
        self.C = None
        self.A = np.zeros(6)
        self.B = np.zeros([6,3])


    def initialize_state(self, X, Q, R, P):
        """
        Initialize the state, process noise, measurement noise, and covariance matrix.
        """

        self.X = X
        self.Q = Q
        self.R_1 = R
        self.P = P
        self.obs = False

    def motion_model(self, u, timestep = 0):
        """
        Predict the next state based on the motion model.
        """
        timestep1 = 1/3 #based on unities way of integrating position(????)
        self.A = np.array([[1, 0, 0, timestep1, 0, 0],
                            [0, 1, 0, 0, timestep1, 0],
                            [0, 0, 1, 0, 0, timestep1],
                            [0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 1]]
        )
        self.B = np.array( [[0, 0, 0],      # No direct acceleration influence on position
                            [0, 0, 0],      # No direct acceleration influence on position
                            [0, 0, 0],      # No direct acceleration influence on position
                            [timestep, 0, 0],  # Velocity update from acceleration
                            [0, timestep, 0],  # Velocity update from acceleration
                            [0, 0, timestep]]) # Velocity update from acceleration
        self.X = self.A @ self.X + self.B @ u
        
        P_pred = self.A @ self.P @ self.A.T + self.Q  #pre and post multiply A to P 
        return self.X, P_pred
    
    def observation_model_gps(self):
        """
        Observation model that predicts the measurement given the current state.
        """
        return self.M @ self.X

    

    def estimate(self, obs, timestep, input):
        """
        Perform the EKF estimation step: predict and update.
        """
        #predict
        X_pred, P_pred = self.motion_model(input, timestep)
        
        self.C = self.M
        obs_model = self.observation_model_gps()
        R = np.eye(1)*10**-3
        # self.get_logger().info(f' gps obs : {obs} and modelled : {obs_model} '  )
        S = self.C @ P_pred @ self.C.T + R
        K = P_pred @ self.C.T @ np.linalg.inv(S)
        self.X = X_pred + K @ (obs - obs_model)

        self.P = (np.eye(len(self.X)) - K @ self.C) @ P_pred

        return self.X, self.P