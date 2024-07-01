#!/usr/bin/python

# import numpy as np
import math
import time as python_time
import message_filters

import rclpy
from rclpy import time
from rclpy.node import Node
from rclpy.qos import QoSProfile

import tf2_ros
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from tf2_ros import LookupException, ConnectivityException, ExtrapolationException

# ROS2 version of tf transformations
from tf_transformations import euler_from_quaternion, quaternion_from_euler  # quaternion_multiply

# from std_srvs.srv import SetBool  # SetBoolRequest, SetBoolRequest
# from builtin_interfaces.msg import Time
from tf2_geometry_msgs import PointStamped
from geometry_msgs.msg import TransformStamped, PoseWithCovarianceStamped  # PointStamped, Quaternion
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from smarc_msgs.msg import DVL, ThrusterFeedback
from sam_msgs.msg import ThrusterAngles

# Topics
# from smarc_msgs.msg import Topics as SmarcTopics
from sam_msgs.msg import Topics as SamTopics
from dead_reckoning_msgs.msg import Topics as DRTopics

# links
from sam_msgs.msg import Links as SamLinks

# from sbg_driver.msg import SbgEkfEuler

try:
    from .sam_mm import *
    from .helpers.ros_helpers import rcl_time_to_secs, rcl_time_to_stamp, construct_stamped_transform, ros_time_to_secs
except ImportError:
    from sam_mm import *
    from helpers.ros_helpers import rcl_time_to_secs, rcl_time_to_stamp, construct_stamped_transform, ros_time_to_secs


class VehicleDR(Node):
    """
    This node is responsible for dead reckoning of SAM anf floatSAM

    NOTE: When using in the simulation ... Things are a bit different since the frame transforms are known.
    """

    def __init__(self, namespace=None):
        super().__init__("dr_node", namespace=namespace)

        # ===== Declare parameters =====
        self.declare_node_parameters()
        # ===== Get parameters =====
        self.robot_name = self.get_parameter("robot_name").value
        # === Frames ===
        self.map_frame = self.get_parameter("map_frame").value
        self.utm_frame = self.get_parameter("utm_frame").value
        self.odom_frame = f"{self.robot_name}/odom"
        self.base_frame = f"{self.robot_name}/{SamLinks.BASE_LINK}"
        self.base_frame_2d = f"{self.robot_name}/{SamLinks.BASE_LINK_2D}"
        self.dvl_frame = f"{self.robot_name}/{SamLinks.DVL_LINK}"
        self.press_frame = f"{self.robot_name}/{SamLinks.PRESS_LINK}"
        # === other ===
        self.dvl_period = self.get_parameter("dvl_period").value
        self.dr_period = self.get_parameter("dr_period").value
        # self.dr_pub_period = rospy.get_param("~dr_pub_period", 0.1)
        self.simulation = self.get_parameter("simulation").value

        self.tf_buffer = Buffer()
        self.listener = TransformListener(self.tf_buffer, self)
        self.static_tf_bc = tf2_ros.StaticTransformBroadcaster(self)
        self.br = tf2_ros.TransformBroadcaster(self)
        self.transformStamped = TransformStamped()

        self.t_prev = self.get_clock().now()  # rclpy.Time was rospy.Time, rospy.Time.now()
        self.pose_prev = [0.] * 6
        self.heading_initialized = False
        self.map_2_odom_initialized = False

        # Stim integration
        self.rot_t = [0.] * 3
        self.t_stim_prev = 0.
        self.stim_initialized = False
        self.vel_rot = [0.] * 3

        # Useful when working with rosbags
        self.t_start = 0.
        self.t_now = 0.
        self.t_pub = 0.

        # DVL integration
        self.pos_t = [0.] * 3
        self.t_dvl_prev = 0.
        self.dvl_on = False
        self.dvl_latest = DVL()
        self.dvl_latest.velocity.x = 0.
        self.dvl_latest.velocity.y = 0.
        self.dvl_latest.velocity.z = 0.

        # Depth measurements: init to zero
        self.b2p_trans = [0.] * 3
        self.depth_meas = False  # If no press sensor available, assume surface vehicle
        self.base_depth = 0.  # abs depth of base frame

        # Motion model
        self.sam = SAM()
        self.mm_on = False
        self.mm_linear_vel = [0.] * 3
        dr = np.clip(0., -7 * np.pi / 180, 7 * np.pi / 180)
        self.u = [0., dr]
        self.thrust_cmd = ThrusterAngles()

        # DR behavior
        # Valid DVL values: if valid DVL IS used, else motion model is used
        self.dvl_max_mag_x = 1.5
        self.dvl_max_mag_y = 0.2
        self.dvl_max_neg_x = -math.inf  # What is this for? Why not trust the dvl when moving in reverse, -0.1

        # Problem: The actual timer period was not consistent with the requested period.
        # Solution: Measure and use the actual period
        self.dr_measured_period = 0
        self.dr_last_time = None

        # Status
        self.status_min_period = 1.0
        self.status_last_time = None
        self.status_verbose = self.get_parameter("status_verbose").value

        # ===== Connections =====
        # self.pub_odom = rospy.Publisher(self.odom_topic, Odometry, queue_size=100)
        # self.depth_sub = rospy.Subscriber(self.depth_top, PoseWithCovarianceStamped, self.depth_cb)
        # self.gps_sub = rospy.Subscriber(self.gps_topic, Odometry, self.gps_cb)

        # === Subscriptions ===
        # DR subscriptions
        self.depth_sub = self.create_subscription(msg_type=PoseWithCovarianceStamped,
                                                  topic=DRTopics.DR_DEPTH_POSE_TOPIC,
                                                  callback=self.depth_cb, qos_profile=10)
        self.gps_sub = self.create_subscription(msg_type=Odometry,
                                                topic=DRTopics.DR_GPS_ODOM_TOPIC,
                                                callback=self.gps_cb, qos_profile=10)

        # General subscriptions
        self.dvl_sub = self.create_subscription(msg_type=DVL, topic=SamTopics.DVL_TOPIC,
                                                callback=self.dvl_cb, qos_profile=10)
        self.stim_sub = self.create_subscription(msg_type=Imu, topic=SamTopics.STIM_IMU_TOPIC,
                                                 callback=self.stim_cb, qos_profile=10)
        self.sbg_sub = self.create_subscription(msg_type=Imu, topic=SamTopics.SBG_IMU_TOPIC,
                                                callback=self.sbg_cb, qos_profile=10, )
        self.thrust_cmd_sub = self.create_subscription(msg_type=ThrusterAngles,
                                                       topic=SamTopics.THRUST_VECTOR_CMD_TOPIC,
                                                       callback=self.thrust_cmd_cb, qos_profile=10)

        # Synchronizer
        self.thrust1_sub = message_filters.Subscriber(self, ThrusterFeedback, SamTopics.THRUSTER1_FB_TOPIC)
        self.thrust2_sub = message_filters.Subscriber(self, ThrusterFeedback, SamTopics.THRUSTER2_FB_TOPIC)

        self.ts = message_filters.ApproximateTimeSynchronizer([self.thrust1_sub, self.thrust2_sub],
                                                              20, slop=20.0, allow_headerless=False)
        self.ts.registerCallback(cb=self.thrust_cb)

        # === Publishers ===
        odom_qos_profile = QoSProfile(depth=100)
        self.pub_odom = self.create_publisher(msg_type=Odometry, topic=DRTopics.DR_ODOM_TOPIC,
                                              qos_profile=odom_qos_profile)

        # === Timers ===
        self.timer = self.create_timer(timer_period_sec=self.dr_period, callback=self.dr_timer)

        # Timer debugging
        self.dr_last_time_dbg = None  # Measure timer performance
        self.times_n_dbg = 100
        self.times_dbg = np.zeros(self.times_n_dbg)  # Initialize a numpy array to store the last n times
        self.index_dbg = 0
        self.count_dbg = 0

    def declare_node_parameters(self):
        """
        Declare the node parameters for the dr node

        :return:
        """
        # TODO
        default_robot_name = "sam0"
        self.declare_parameter("robot_name", default_robot_name)
        # === Frames ===
        # self.declare_parameter("odom_frame", default_robot_name+"/odom")  # changed
        self.declare_parameter("map_frame", "map")
        self.declare_parameter("utm_frame", "utm")

        # self.declare_parameter("base_frame_2d", f"{default_robot_name}_base_link_2d")
        # self.declare_parameter("dvl_frame", f"{default_robot_name}_dvl_link")
        # self.declare_parameter("pressure_frame", f"{default_robot_name}_pressure_link")
        # === Other ===
        self.declare_parameter("dvl_period", 0.1)
        self.declare_parameter("dr_period", 0.1)  # 0.01,
        self.declare_parameter("simulation", True)
        self.declare_parameter("status_verbose", False)

    def thrust_cmd_cb(self, thrust_cmd_msg):
        self.thrust_cmd = thrust_cmd_msg

    def gps_cb(self, gps_msg):
        self.get_logger().info("GPS received")
        try:
            world_transform = self.tf_buffer.lookup_transform(target_frame=self.odom_frame,
                                                              source_frame=self.map_frame,
                                                              time=rclpy.time.Time())

            # world_trans = world_transform.transform.translation
            # world_rot = world_transform.transform.rotation

            # This might no longer be needed,
            if self.simulation:
                self.get_logger().info(f"Simulation: known transform from {self.map_frame} to {self.odom_frame}")
                self.map_2_odom_initialized = True
                self.destroy_subscription(self.gps_sub)

        except (LookupException, ConnectivityException):

            self.get_logger().info("Setting goal point")

            goal_point = PointStamped()
            goal_point.header.frame_id = self.utm_frame
            # Check if this is the correct stamp
            goal_point.header.stamp = rcl_time_to_stamp(self.get_clock().now())  # rospy.Time(0)
            goal_point.point.x = gps_msg.pose.pose.position.x
            goal_point.point.y = gps_msg.pose.pose.position.y
            goal_point.point.z = 0.

            try:
                # gps_map = self.listener.transformPoint(self.map_frame, goal_point)
                gps_map = self.tf_buffer.transform(object_stamped=goal_point,
                                                   target_frame=self.map_frame)

                if self.heading_initialized:
                    self.get_logger().info(f"DR node: broadcasting transform {self.map_frame} to {self.odom_frame}")
                    # SBG points to north while map's x axis points east (ENU) so 
                    # the map --> odom tf needs an extra +90 deg turn in z 

                    euler = euler_from_quaternion(
                        [self.init_quat.x, self.init_quat.y, self.init_quat.z, self.init_quat.w])
                    quat = quaternion_from_euler(0., 0., euler[2])  # -0.3 for feb_24 with floatsam

                    self.transformStamped.transform.translation.x = gps_map.point.x
                    self.transformStamped.transform.translation.y = gps_map.point.y
                    self.transformStamped.transform.translation.z = 0.
                    self.transformStamped.transform.rotation.x = quat[0]
                    self.transformStamped.transform.rotation.y = quat[1]
                    self.transformStamped.transform.rotation.z = quat[2]
                    self.transformStamped.transform.rotation.w = quat[3]
                    self.transformStamped.header.frame_id = self.map_frame
                    self.transformStamped.child_frame_id = self.odom_frame
                    self.transformStamped.header.stamp = rcl_time_to_stamp(self.get_clock().now())
                    self.static_tf_bc.sendTransform(self.transformStamped)
                    self.map_2_odom_initialized = True
                    # self.gps_sub.unregister()
                    self.destroy_subscription(self.gps_sub)

            except (LookupException, ConnectivityException, ExtrapolationException):
                self.get_logger().info("DR: Transform to utm-->map not available yet")
            pass

        # Is there a depth sensor? If so, AUV.
        try:
            # TODO: test this on SAM. If needed, add wait()
            # ROS1: self.listener.lookupTransform(self.base_frame, self.press_frame, rclpy.time.Time())
            b2p_transform = self.tf_buffer.lookup_transform(target_frame=self.press_frame,
                                                            source_frame=self.base_frame,
                                                            time=rclpy.time.Time())

            self.b2p_trans = b2p_transform.transform.translation
            b2p_rot = b2p_transform.transform.rotation

            self.depth_meas = True
            self.get_logger().info(f"DR node: got transform {self.base_frame} to {self.press_frame}")


        except (LookupException, ConnectivityException):
            self.get_logger().info(f"DR node: could not get transform {self.base_frame} to {self.press_frame}")
            self.get_logger().warn("Assuming surface vehicle")

    def dr_timer(self):
        # Determine actual period of timer
        dr_current_time = rcl_time_to_secs(self.get_clock().now())
        if self.dr_last_time is None:
            self.dr_measured_period = 0
        else:
            self.dr_measured_period = dr_current_time - self.dr_last_time
        self.dr_last_time = dr_current_time

        # Debug timing issues
        start_time_dbg = python_time.time()

        if self.map_2_odom_initialized and self.stim_initialized:

            pose_t = np.concatenate([self.pos_t, self.rot_t])  # Catch latest estimate from IMU
            rot_vel_t = self.vel_rot  # TODO: rn this keeps the last vels even if the IMU dies
            lin_vel_t = np.zeros(3)

            # DVL data coming in
            # self.get_logger().info(f"DVL Status: {self.dvl_on}")
            if self.dvl_on:
                rot_mat_t = self.fullRotation(pose_t[3], pose_t[4], pose_t[5])

                # Integrate linear velocities from DVL
                # If last DVL msg isn't too old
                if self.t_now - self.t_dvl_prev < self.dvl_period and \
                        abs(self.dvl_latest.velocity.y) < self.dvl_max_mag_y and \
                        abs(self.dvl_latest.velocity.x) < self.dvl_max_mag_x and \
                        self.dvl_latest.velocity.x > self.dvl_max_neg_x:

                    if self.check_status_valid(dr_current_time) and self.status_verbose:
                        self.get_logger().info(f"DR - DVL - {self.dr_measured_period}")

                    lin_vel_t = np.array([self.dvl_latest.velocity.x,
                                          self.dvl_latest.velocity.y,
                                          self.dvl_latest.velocity.z])

                    # print("DVL vel ", lin_vel_t)

                # # Otherwise, integrate motion model estimate
                else:
                    if self.check_status_valid(dr_current_time) and self.status_verbose:
                        self.get_logger().info(f"DR - Motion model - {self.dr_measured_period}")

                    # Input x, y, yaw, x_vel, y_vel, yaw_vel
                    # Output x_vel, y_vel, yaw_vel, x_acc, y_acc, yaw_acc
                    self.lin_acc_t = self.sam.motion(self.u)[0:3]

                    self.lin_acc_t = np.array(
                        [self.lin_acc_t[0], -self.lin_acc_t[1], 0.])

                    lin_vel_t = self.lin_acc_t * self.dr_measured_period  # self.dr_period
                    # print("MM vel ", lin_vel_t)

                # Integrate linear vels                    
                step_t = np.matmul(rot_mat_t, lin_vel_t * self.dr_measured_period)  # self.dr_period
                pose_t[0:2] += step_t[0:2]

            # Measure depth directly
            pose_t[2] = self.base_depth

            # Publish and broadcast aux frame for testing
            # ROS1: tf.transformations.quaternion_from_euler(...)
            quat_t = quaternion_from_euler(pose_t[3], pose_t[4], pose_t[5])
            odom_msg = Odometry()
            odom_msg.header.frame_id = self.odom_frame
            odom_msg.header.stamp = rcl_time_to_stamp(self.get_clock().now())  # rospy.Time.now()
            odom_msg.child_frame_id = self.base_frame
            odom_msg.pose.pose.position.x = pose_t[0]
            odom_msg.pose.pose.position.y = pose_t[1]
            odom_msg.pose.pose.position.z = pose_t[2]
            odom_msg.twist.twist.linear.x = lin_vel_t[0]
            odom_msg.twist.twist.linear.y = lin_vel_t[1]
            odom_msg.twist.twist.linear.z = lin_vel_t[2]
            odom_msg.twist.twist.angular.x = rot_vel_t[0]
            odom_msg.twist.twist.angular.y = rot_vel_t[1]
            odom_msg.twist.twist.angular.z = rot_vel_t[2]
            odom_msg.pose.covariance = [0.] * 36
            # odom_msg.pose.pose.orientation = Quaternion(*quat_t)
            odom_msg.pose.pose.orientation.x = quat_t[0]
            odom_msg.pose.pose.orientation.y = quat_t[1]
            odom_msg.pose.pose.orientation.z = quat_t[2]
            odom_msg.pose.pose.orientation.w = quat_t[3]
            self.pub_odom.publish(odom_msg)

            rcl_now = self.get_clock().now()

            base_transform = construct_stamped_transform(transform_trans=[pose_t[0], pose_t[1], pose_t[2]],
                                                         transform_rot=quat_t,
                                                         frame_id=self.odom_frame,
                                                         child_frame_id=self.base_frame,
                                                         rcl_time=rcl_now)

            base_2d_transform = construct_stamped_transform(transform_trans=[pose_t[0], pose_t[1], pose_t[2]],
                                                            transform_rot=quat_t,
                                                            frame_id=self.odom_frame,
                                                            child_frame_id=self.base_frame_2d,
                                                            rcl_time=rcl_now)

            self.br.sendTransform(base_transform)
            self.br.sendTransform(base_2d_transform)

            self.t_now += self.dr_measured_period  # self.dr_period

            # Update global variable
            self.pos_t = pose_t[0:3]

            # Testing for the duration
            end_time_dbg = python_time.time()
            elapsed_time = end_time_dbg - start_time_dbg

            # # record elapsed times
            # self.times[self.index] = elapsed_time
            # self.index = (self.index + 1) % self.times_n
            # self.count = min(self.count + 1, self.times_n)
            #
            # # Average
            # average_time = np.sum(self.times)/self.count

            # self.get_logger().info(f"Elapsed time: {elapsed_time:.4f}")  # Average Elapsed time: {average_time:.4f}")

            if self.dr_last_time_dbg is not None:
                last_callback_period = start_time_dbg - self.dr_last_time_dbg

                self.times_dbg[self.index_dbg] = last_callback_period
                self.index_dbg = (self.index_dbg + 1) % self.times_n_dbg
                self.count_dbg = min(self.count_dbg + 1, self.times_n_dbg)

                # Average
                average_time = np.sum(self.times_dbg) / self.count_dbg

                # self.get_logger().info(f'Last callback period: {last_callback_period:.4f} -- '
                #                        f'Average callback period: {average_time} -- '
                #                        f'Used period: {self.dr_measured_period} __ '
                #                        f'Requested period: {self.dr_period}')

            self.dr_last_time_dbg = start_time_dbg

        else:
            # At this point the DR is not properly initialized
            # Status report at a limited rate
            status_current_time = rcl_time_to_secs(self.get_clock().now())

            if self.check_status_valid(status_current_time):
                self.get_logger().info(f"DR_timer - m2o: {self.map_2_odom_initialized}"
                                       f"  stim:{self.stim_initialized}  heading:{self.heading_initialized}")

    def check_status_valid(self, current_time: float):
        """
        check if it is time to provide a status update
        """
        if self.status_last_time is None:
            self.status_last_time = current_time
            status_valid = True
        elif current_time - self.status_last_time >= self.status_min_period:
            self.status_last_time = current_time
            status_valid = True
        else:
            status_valid = False

        return status_valid

    def thrust_cb(self, thrust1_msg, thrust2_msg):
        # self.get_logger().info("Thrust callback")
        dr = np.clip(-self.thrust_cmd.thruster_horizontal_radians, -7 * np.pi / 180, 7 * np.pi / 180)
        self.u = [thrust1_msg.rpm.rpm + thrust2_msg.rpm.rpm, dr]

    def depth_cb(self, depth_msg):

        # TODO: test with SAM data
        if self.depth_meas:
            self.base_depth = depth_msg.pose.pose.position.z + self.b2p_trans.x * np.sin(self.rot_t[1])

    def sbg_cb(self, sbg_msg):
        if self.heading_initialized == False:
            self.get_logger().info("SBG heading initialized")
            self.heading_initialized = True

        self.init_quat = sbg_msg.orientation
        # self.euler_sub.unregister()

    def fullRotation(self, roll, pitch, yaw):
        rot_z = np.array([[np.cos(yaw), -np.sin(yaw), 0.0],
                          [np.sin(yaw), np.cos(yaw), 0.0],
                          [0., 0., 1]])
        rot_y = np.array([[np.cos(pitch), 0.0, np.sin(pitch)],
                          [0., 1., 0.],
                          [-np.sin(pitch), np.cos(pitch), 0.0]])
        rot_x = np.array([[1., 0., 0.],
                          [0., np.cos(roll), -np.sin(roll)],
                          [0., np.sin(roll), np.cos(roll)]])

        return np.matmul(rot_z, np.matmul(rot_y, rot_x))

    def stim_cb(self, imu_msg):
        if self.stim_initialized and self.map_2_odom_initialized:
            self.rot_stim = np.array([imu_msg.orientation.x,
                                      imu_msg.orientation.y,
                                      imu_msg.orientation.z,
                                      imu_msg.orientation.w])
            euler_t = euler_from_quaternion(self.rot_stim)

            # Integrate yaw velocities
            self.vel_rot = np.array([imu_msg.angular_velocity.x,
                                     imu_msg.angular_velocity.y,
                                     imu_msg.angular_velocity.z])

            # dt = imu_msg.header.stamp.to_sec() - self.t_stim_prev
            dt = ros_time_to_secs(imu_msg.header.stamp) - self.t_stim_prev
            self.rot_t = np.array(self.rot_t) + self.vel_rot * dt
            self.t_stim_prev = ros_time_to_secs(imu_msg.header.stamp)

            for rot in self.rot_t:
                rot = (rot + np.pi) % (2 * np.pi) - np.pi

            # Measure roll and pitch directly
            self.rot_t[0] = euler_t[0]
            self.rot_t[1] = euler_t[1]

        else:
            # rospy.loginfo("Stim data coming in")
            self.t_stim_prev = ros_time_to_secs(imu_msg.header.stamp)
            self.stim_initialized = True

    def dvl_cb(self, dvl_msg):
        # if self.rot_stim.any():

        #     # # Project velocities into odom frame to correct for pitching of floatsam
        #     euler = euler_from_quaternion(self.rot_stim)
        #     mat_t = self.fullRotation(euler[0],euler[1],euler[2])

        #     aux  = np.matmul(mat_t, np.array([dvl_msg.velocity.x,
        #                                     dvl_msg.velocity.y,
        #                                     dvl_msg.velocity.z]))
        #     dvl_msg.velocity.x = aux[0]
        #     dvl_msg.velocity.y = aux[1]
        #     dvl_msg.velocity.z = aux[2]
        self.dvl_latest = dvl_msg

        if self.dvl_on:
            dt = ros_time_to_secs(dvl_msg.header.stamp) - self.t_dvl_prev
            self.t_dvl_prev = ros_time_to_secs(dvl_msg.header.stamp)

            # if dt > self.dvl_period:
            #     print("Missed DVL meas")            

        else:
            self.get_logger().info("DVL data received")
            current_header = dvl_msg.header.stamp
            current_time = ros_time_to_secs(current_header)
            self.t_dvl_prev = current_time
            self.t_now = current_time
            self.t_pub = current_time
            self.dvl_on = True


def main(args=None, namespace=None):
    rclpy.init(args=args)
    dr_node = VehicleDR(namespace=namespace)
    try:
        rclpy.spin(dr_node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main(namespace="sam0")
