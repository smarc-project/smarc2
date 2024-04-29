#!/usr/bin/python

import rclpy
import matplotlib.pyplot as plt
import numpy as np
import time
from rclpy.node import Node

from std_msgs.msg import Bool
# from rclpy.numpy_msg import numpy_msg
import tf2_ros
import message_filters
from tf2_ros.buffer import Buffer
from tf2_geometry_msgs import do_transform_point
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PointStamped
from dead_reckoning_msgs.msg import Topics 
try:
    from .helpers.ros_helpers import rcl_time_to_secs, rcl_time_to_stamp, ros_time_to_secs
except ImportError:
    from helpers.ros_helpers import rcl_time_to_secs, rcl_time_to_stamp, ros_time_to_secs

class DRStatsVisualization(Node):
    
    def __init__(self, namespace=None):
        super().__init__("visual_tools_node", namespace=namespace)
        self.declare_node_parameters()
        # Real mbes pings subscriber    
        self.robot_name = self.get_parameter("robot_name").value
        # gps_odom_top = self.get_parameter(Topics.DR_GPS_ODOM_TOPIC).value
        # dr_odom_top = self.get_parameter(Topics.DR_ODOM_TOPIC).value
        #pf_odom_top = rclpy.get_param("~odom_corrected_topic", 'gps_odom')

        self.utm_frame = self.get_parameter('utm_frame').value
        self.odom_frame = self.get_parameter("odom_frame").value
        self.sim_time = self.get_parameter("use_sim_time").value

        # PF ping subscriber

        self.gps_odom_sub = message_filters.Subscriber(self, Odometry,Topics.DR_GPS_ODOM_TOPIC)
        self.dr_odom_sub = message_filters.Subscriber(self, Odometry,Topics.DR_ODOM_TOPIC)
        #self.pf_odom_sub = message_filters.Subscriber(self, Odometry,pf_odom_top)
        self.ts = message_filters.ApproximateTimeSynchronizer([self.gps_odom_sub,
                                                               self.dr_odom_sub], # add pf_odom_sub when available
                                                              20,
                                                              slop=20.0,
                                                              allow_headerless=False)

        self.ts.registerCallback(self.odom_cb)
        self.tf_buffer = Buffer()
        self.listener = tf2_ros.TransformListener(self.tf_buffer, self)
        
        # # When the survey is finished, save the data to disk
        # finished_top = rospy.get_param("~survey_finished_top", '/survey_finished')
        # self.synch_pub = rospy.Subscriber(finished_top, Bool, self.synch_cb)
        # self.survey_finished = False

        # self.cov_traces = [0.]

        self.filter_cnt = 1

        self.gps_odom_vec = np.zeros((3, 1))
        self.dr_odom_vec = np.zeros((3, 1))
        self.pf_odom_vec = np.zeros((3, 1))
        #comment out to remove plots
        self.timer = self.create_timer(2, self.visualize)



    def declare_node_parameters(self):
        """
        Declare the parameters of the node
        """
        default_robot_name = "sam0"
        self.declare_parameter("robot_name", default_robot_name)
        self.declare_parameter('utm_frame', 'utm')
        self.declare_parameter("odom_frame", "odom")

    def finish_hld(self):
        dr_dist = 0.
        gps_dist = 0.
        pf_dist = 0.
        for i in range(1, self.dr_odom_vec.shape[1]):
            dr_dist += np.linalg.norm(self.dr_odom_vec[:,i] - self.dr_odom_vec[:,i-1])
            gps_dist += np.linalg.norm(self.gps_odom_vec[:,i] - self.gps_odom_vec[:,i-1])
            #pf_dist += np.linalg.norm(self.pf_odom_vec[:,i] - self.pf_odom_vec[:,i-1])
        
        print("GPS distance ", gps_dist)
        print("DR distance ", dr_dist)
        print("PF distance ", pf_dist)

        print("GPS final error ", np.linalg.norm(self.gps_odom_vec[:, -1]))
        print("DR final error ", np.linalg.norm(self.dr_odom_vec[:, -1]))
        print("PF final error ", np.linalg.norm(self.pf_odom_vec[:, -1]))


   
    def odom_cb(self, gps_msg:Odometry, dr_msg: Odometry, ):#pf_msg = None
        goal_point = PointStamped()
        goal_point.header.frame_id = self.utm_frame
        goal_point.header.stamp = dr_msg.header.stamp
        goal_point.point.x = gps_msg.pose.pose.position.x
        goal_point.point.y = gps_msg.pose.pose.position.y
        goal_point.point.z = 0.

        try:
            gps_map_transform = self.tf_buffer.lookup_transform(target_frame=self.odom_frame,
                                                                source_frame=goal_point.header.frame_id,
                                                                 time=goal_point.header.stamp)
            gps_map = do_transform_point(goal_point, gps_map_transform)
            #gps_map = self.listener.transformPoint("sam/odom", goal_point)
            gps = np.array([gps_map.point.x,
                            gps_map.point.y,
                            gps_map.point.z])

            self.gps_odom_vec = np.hstack((self.gps_odom_vec, gps.reshape((3,1))))

           
            dr = np.array([dr_msg.pose.pose.position.x,
                        dr_msg.pose.pose.position.y,
                        dr_msg.pose.pose.position.z])
            self.dr_odom_vec = np.hstack((self.dr_odom_vec, dr.reshape((3,1))))

            # if(pf_msg):
            #     pf = np.array([pf_msg.pose.pose.position.x,
            #                 pf_msg.pose.pose.position.y,
            #                 pf_msg.pose.pose.position.z])

            #     self.pf_odom_vec = np.hstack((self.pf_odom_vec, pf.reshape((3,1))))

            self.filter_cnt += 1
        
        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
                self.get_logger().warning("Visual tools: Transform to utm-->map not available yet")
        pass

    def visualize(self):

        if self.filter_cnt > 0:
            
            plt.gcf().canvas.mpl_connect('key_release_event',
                    lambda event: [exit(0) if event.key == 'escape' else None])

            # Plot error between DR PF and GT
            if True:
                plt.subplot(2, 1, 1)
                plt.cla()
                plt.plot(np.linspace(0,self.filter_cnt, self.filter_cnt),
                         np.linalg.norm(self.gps_odom_vec-self.pf_odom_vec, axis=0), "-b")
                plt.grid(True)

                # Error between GPS and DR
                plt.subplot(2, 1, 2)
                plt.cla()
                plt.plot(np.linspace(0,self.filter_cnt, self.filter_cnt),
                         np.linalg.norm(self.gps_odom_vec-self.dr_odom_vec, axis=0), "-r")

                plt.grid(True)

            plt.pause(0.00001)





def main(args=None, namespace=None):
    rclpy.init(args=args)
    dr_visual = DRStatsVisualization(namespace=namespace)
    try:
        rclpy.spin(dr_visual)
    except KeyboardInterrupt:
        dr_visual.finish_hld()
        pass


if __name__ == "__main__":
    main(namespace="sam0")