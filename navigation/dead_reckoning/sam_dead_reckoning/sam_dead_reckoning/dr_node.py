#!/usr/bin/python

import numpy as np
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
from tf_transformations import euler_from_quaternion, quaternion_from_euler, quaternion_multiply

# from std_srvs.srv import SetBool  # SetBoolRequest, SetBoolRequest
from builtin_interfaces.msg import Time
from geometry_msgs.msg import PointStamped, TransformStamped, Quaternion, PoseWithCovarianceStamped
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from smarc_msgs.msg import DVL, ThrusterFeedback
from sam_msgs.msg import ThrusterAngles

# from sbg_driver.msg import SbgEkfEuler

try:
    from .sam_mm import *
    from .helpers.ros_helpers import rcl_time_to_secs, rcl_time_to_stamp, construct_stamped_transform, ros_time_to_secs
except ImportError:
    from sam_mm import *
    from helpers.ros_helpers import rcl_time_to_secs, rcl_time_to_stamp, construct_stamped_transform, ros_time_to_secs


class VehicleDR(Node):

    def __init__(self):
        super().__init__("dr_node")

        # ===== Declare parameters =====
        self.declare_node_parameters()

        # ===== Get parameters =====
        # === Topics ===
        self.dvl_topic = self.get_parameter('dvl_topic').value
        self.odom_topic = self.get_parameter('odom_topic').value  # topic used in the launch file for the DVL sensor
        self.stim_topic = self.get_parameter('imu').value
        self.sbg_topic = self.get_parameter('sbg_topic').value
        self.depth_top = self.get_parameter('depth_topic').value
        self.rpm1_topic = self.get_parameter('thrust1_fb').value
        self.rpm2_topic = self.get_parameter('thrust2_fb').value
        self.thrust_topic = self.get_parameter('thrust_vec_cmd').value
        self.gps_topic = self.get_parameter('gps_odom_topic').value
        # === Frames ===
        self.base_frame = self.get_parameter('base_frame').value
        self.base_frame_2d = self.get_parameter('base_frame_2d').value
        self.odom_frame = self.get_parameter('odom_frame').value
        self.map_frame = self.get_parameter('map_frame').value
        self.utm_frame = self.get_parameter('utm_frame').value
        self.dvl_frame = self.get_parameter('dvl_frame').value
        self.press_frame = self.get_parameter('pressure_frame').value
        # === other ===
        self.dvl_period = self.get_parameter('dvl_period').value
        self.dr_period = self.get_parameter('dr_period').value
        # self.dr_pub_period = rospy.get_param('~dr_pub_period', 0.1)

        self.tf_buffer = Buffer()
        self.listener = TransformListener(self.tf_buffer, self)
        self.static_tf_bc = tf2_ros.StaticTransformBroadcaster(self)
        self.br = tf2_ros.TransformBroadcaster(self)
        self.transformStamped = TransformStamped()

        self.t_prev = self.get_clock().now()  # rclpy.Time was rospy.Time, rospy.Time.now()
        self.pose_prev = [0.] * 6
        self.init_heading = False
        self.init_m2o = False

        # Stim integration
        self.rot_t = [0.] * 3
        self.t_stim_prev = 0.
        self.init_stim = False
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

        # ===== Connections =====
        # self.pub_odom = rospy.Publisher(self.odom_topic, Odometry, queue_size=100)
        # self.sbg_sub = rospy.Subscriber(self.sbg_topic, Imu, self.sbg_cb)
        # self.dvl_sub = rospy.Subscriber(self.dvl_topic, DVL, self.dvl_cb)
        # self.stim_sub = rospy.Subscriber(self.stim_topic, Imu, self.stim_cb)
        # self.depth_sub = rospy.Subscriber(self.depth_top, PoseWithCovarianceStamped, self.depth_cb)
        # self.gps_sub = rospy.Subscriber(self.gps_topic, Odometry, self.gps_cb)

        # self.thrust_cmd_sub = rospy.Subscriber(self.thrust_topic, ThrusterAngles, self.thrust_cmd_cb)
        # self.thrust1_sub = message_filters.Subscriber(self.rpm1_topic, ThrusterFeedback)
        # self.thrust2_sub = message_filters.Subscriber(self.rpm2_topic, ThrusterFeedback)

        # === Publishers ===
        odom_qos_profile = QoSProfile(depth=100)
        self.pub_odom = self.create_publisher(msg_type=Odometry, topic=self.odom_topic, qos_profile=odom_qos_profile)

        # === Subscriptions ===
        self.sbg_sub = self.create_subscription(msg_type=Imu, topic=self.sbg_topic,
                                                callback=self. sbg_cb, qos_profile=10, )
        self.dvl_sub = self.create_subscription(msg_type=DVL, topic=self.dvl_topic,
                                                callback=self.dvl_cb, qos_profile=10)
        self.stim_sub = self.create_subscription(msg_type=Imu, topic=self.stim_topic,
                                                 callback=self.stim_cb, qos_profile=10)
        self.depth_sub = self.create_subscription(msg_type=PoseWithCovarianceStamped, topic=self.depth_top,
                                                  callback=self.depth_cb, qos_profile=10)
        self.gps_sub = self.create_subscription(msg_type=Odometry, topic=self.gps_topic,
                                                callback=self.gps_cb, qos_profile=10)
        self.thrust_cmd_sub = self.create_subscription(msg_type=ThrusterAngles, topic=self.thrust_topic ,
                                                       callback=self.thrust_cmd_cb , qos_profile=10)
        # TODO will this work in ROS2
        # ROS1
        # self.thrust1_sub = message_filters.Subscriber(self.rpm1_topic, ThrusterFeedback)
        # self.thrust2_sub = message_filters.Subscriber(self.rpm2_topic, ThrusterFeedback)

        # ROS2
        # TODO hope this works
        self.thrust1_sub = message_filters.Subscriber(self, ThrusterFeedback, self.rpm1_topic)
        self.thrust2_sub = message_filters.Subscriber(self, ThrusterFeedback, self.rpm2_topic)

        # Synchronizer
        self.ts = message_filters.ApproximateTimeSynchronizer([self.thrust1_sub, self.thrust2_sub],
                                                              20, slop=20.0, allow_headerless=False)
        self.ts.registerCallback(self.thrust_cb)

        # Time
        #rospy.Timer(rospy.Duration(self.dr_period), self.dr_timer)
        self.timer = self.create_timer(timer_period_sec=self.dr_period, callback=self.dr_timer)


        #rospy.spin()

    def declare_node_parameters(self):
        """
        Declare the node parameters for the dr node

        :return:
        """

        """
        self.dvl_topic = rospy.get_param('~dvl_topic', '/sam/core/dvl')
        self.odom_top = rospy.get_param('~odom_topic',
                                        '/sam/dr/dvl_dr')  # topic used in the launch file for the DVL sensor
        self.stim_topic = rospy.get_param('~imu', '/sam/core/imu')
        self.sbg_topic = rospy.get_param('~sbg_topic', '/sam/core/imu')
        self.base_frame = rospy.get_param('~base_frame', 'sam/base_link')
        self.base_frame_2d = rospy.get_param('~base_frame_2d', 'sam/base_link')
        self.odom_frame = rospy.get_param('~odom_frame', 'sam/odom')
        self.map_frame = rospy.get_param('~map_frame', 'map')
        self.utm_frame = rospy.get_param('~utm_frame', 'utm')
        self.dvl_frame = rospy.get_param('~dvl_frame', 'dvl_link')
        self.dvl_period = rospy.get_param('~dvl_period', 0.2)
        self.dr_period = rospy.get_param('~dr_period', 0.02)
        self.depth_top = rospy.get_param('~depth_topic', '/depth')
        self.press_frame = rospy.get_param('~pressure_frame', 'pressure_link')
        self.rpm1_topic = rospy.get_param('~thrust1_fb', '/sam/core/rpm_fb1')
        self.rpm2_topic = rospy.get_param('~thrust2_fb', '/sam/core/rpm_fb2')
        self.thrust_topic = rospy.get_param('~thrust_vec_cmd', '/sam/core/thrust')
        self.gps_topic = rospy.get_param('~gps_odom_topic', '/sam/core/gps')
        # self.dr_pub_period = rospy.get_param('~dr_pub_period', 0.1)
        """
        default_robot_name = 'sam0'
        # === Topics ===
        self.declare_parameter('dvl_topic', f'/{default_robot_name}/core/dvl')
        self.declare_parameter('odom_topic',f'/{default_robot_name}/dr/dvl_dr')  # topic used in the launch file for the DVL sensor
        self.declare_parameter('imu', f'/{default_robot_name}/core/imu')
        self.declare_parameter('sbg_topic', f'/{default_robot_name}/core/imu')
        self.declare_parameter('depth_topic', '/depth')
        self.declare_parameter('thrust1_fb', f'/{default_robot_name}/core/rpm_fb1')
        self.declare_parameter('thrust2_fb', f'/{default_robot_name}/core/rpm_fb2')
        self.declare_parameter('thrust_vec_cmd', f'/{default_robot_name}/core/thrust')
        self.declare_parameter('gps_odom_topic', f'/{default_robot_name}/core/gps')
        # === Frames ===
        self.declare_parameter('base_frame', f'{default_robot_name}/base_link')
        self.declare_parameter('base_frame_2d', f'{default_robot_name}/base_link')
        self.declare_parameter('odom_frame', f'{default_robot_name}/odom')
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('utm_frame', 'utm')
        self.declare_parameter('dvl_frame', 'dvl_link')
        self.declare_parameter('pressure_frame', 'pressure_link')
        # === Other ===
        self.declare_parameter('dvl_period', 0.2)
        self.declare_parameter('dr_period', 0.02)



    def thrust_cmd_cb(self, thrust_cmd_msg):
        self.thrust_cmd = thrust_cmd_msg

    def gps_cb(self, gps_msg):
        try:
            # goal_point_local = self.listener.transformPoint("map", goal_point)
            # ROS1
            # (world_trans, world_rot) = self.listener.lookupTransform(self.map_frame, self.odom_frame, rospy.Time(0))
            (world_trans, world_rot) = self.tf_buffer.lookup_transform(target_frame= self.map_frame,
                                                                       source_frame= self.odom_frame,
                                                                       time=rclpy.time.Time())

        except (LookupException, ConnectivityException):

            goal_point = PointStamped()
            goal_point.header.frame_id = self.utm_frame
            # Check if this is the correct stamp
            goal_point.header.stamp = rcl_time_to_stamp(self.get_clock().now())  # rospy.Time(0)
            goal_point.point.x = gps_msg.pose.pose.position.x
            goal_point.point.y = gps_msg.pose.pose.position.y
            goal_point.point.z = 0.

            try:
                # gps_map = self.listener.transformPoint(self.map_frame, goal_point)
                gps_map = self.tf_buffer.transform(goal_point, self.map_frame)

                if self.init_heading:
                    self.get_logger().info(f"DR node: broadcasting transform {self.map_frame} to {self.odom_frame}")
                    # SBG points to north while map's x axis points east (ENU) so 
                    # the map --> odom tf needs an extra +90 deg turn in z 

                    euler = euler_from_quaternion(
                        [self.init_quat.x, self.init_quat.y, self.init_quat.z, self.init_quat.w])
                    quat = quaternion_from_euler(0., 0., euler[2])  # -0.3 for feb_24 with floatsam

                    self.transformStamped.transform.translation.x = gps_map.point.x
                    self.transformStamped.transform.translation.y = gps_map.point.y
                    self.transformStamped.transform.translation.z = 0.
                    # self.transformStamped.transform.rotation = Quaternion(*quat)
                    self.transformStamped.transform.rotation.x = quat[0] # I've had problems unpacking
                    self.transformStamped.transform.rotation.y = quat[1]
                    self.transformStamped.transform.rotation.z = quat[2]
                    self.transformStamped.transform.rotation.w = quat[3]
                    self.transformStamped.header.frame_id = self.map_frame
                    self.transformStamped.child_frame_id = self.odom_frame
                    self.transformStamped.header.stamp = rcl_time_to_stamp(self.get_clock().now())  # rospy.Time.now()
                    self.static_tf_bc.sendTransform(self.transformStamped)
                    self.init_m2o = True
                    # self.gps_sub.unregister()
                    self.destroy_subscription(self.gps_sub)

            except (LookupException, ConnectivityException, ExtrapolationException):
                self.get_logger().warn("DR: Transform to utm-->map not available yet")
            pass

        # Is there a depth sensor? If so, AUV.
        try:
            # TODO: test this on SAM. If needed, add wait()
            # ROS1: self.listener.lookupTransform(self.base_frame, self.press_frame, rclpy.time.Time())
            (self.b2p_trans, b2p_rot) = self.tf_buffer.lookup_transform(target_frame=self.base_frame,
                                                                        source_frame=self.press_frame,
                                                                        time= rclpy.time.Time())
            self.depth_meas = True
            self.get_logger().info(f"DR node: got transform {self.base_frame} to {self.press_frame}")


        except (LookupException, ConnectivityException):
            self.get_logger().info(f"DR node: could not get transform {self.base_frame} to {self.press_frame}")
            self.get_logger().warn("Assuming surface vehicle")

    def dr_timer(self):
        self.get_logger().info(f"DR_timer - m2o: {self.init_m2o}  stim:{self.init_stim}")
        if self.init_m2o and self.init_stim:

            pose_t = np.concatenate([self.pos_t, self.rot_t])  # Catch latest estimate from IMU
            rot_vel_t = self.vel_rot  # TODO: rn this keeps the last vels even if the IMU dies
            lin_vel_t = np.zeros(3)

            # DVL data coming in
            self.get_logger().info(f"DVL Status: {self.dvl_on}")
            if self.dvl_on:
                rot_mat_t = self.fullRotation(pose_t[3], pose_t[4], pose_t[5])

                # Integrate linear velocities from DVL
                # If last DVL msg isn't too old
                if self.t_now - self.t_dvl_prev < self.dvl_period and \
                        abs(self.dvl_latest.velocity.y) < 0.2 and \
                        abs(self.dvl_latest.velocity.x) < 1.5 and \
                        self.dvl_latest.velocity.x > -0.1:

                    lin_vel_t = np.array([self.dvl_latest.velocity.x,
                                          self.dvl_latest.velocity.y,
                                          self.dvl_latest.velocity.z])

                    print("DVL vel ", lin_vel_t)

                # # Otherwise, integrate motion model estimate
                else:

                    # Input x, y, yaw, x_vel, y_vel, yaw_vel
                    # Output x_vel, y_vel, yaw_vel, x_acc, y_acc, yaw_acc
                    self.lin_acc_t = self.sam.motion(self.u)[0:3]

                    self.lin_acc_t = np.array(
                        [self.lin_acc_t[0], -self.lin_acc_t[1], 0.])

                    lin_vel_t = self.lin_acc_t * self.dr_period
                    print("MM vel ", lin_vel_t)

                # Integrate linear vels                    
                step_t = np.matmul(rot_mat_t, lin_vel_t * self.dr_period)
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

            # TODO check that frame ids are swapped
            base_transform = construct_stamped_transform(transform_trans=[pose_t[0], pose_t[1], pose_t[2]],
                                                         transform_rot=quat_t,
                                                         frame_id=self.base_frame,
                                                         child_frame_id=self.odom_frame,
                                                         rcl_time=rcl_now)

            base_2d_transform = construct_stamped_transform(transform_trans=[pose_t[0], pose_t[1], pose_t[2]],
                                                         transform_rot=quat_t,
                                                         frame_id=self.base_frame_2d,
                                                         child_frame_id=self.odom_frame,
                                                         rcl_time=rcl_now)

            self.br.sendTransform(base_transform)
            self.br.sendTransform(base_2d_transform)

            # ROS1
            # self.br.sendTransform([pose_t[0], pose_t[1], pose_t[2]],
            #                       quat_t,
            #                       rospy.Time.now(),
            #                       self.base_frame,
            #                       self.odom_frame)

            # Base link frame
            # quat_t = tf.transformations.quaternion_from_euler(0., 0., pose_t[5])
            # ROS1
            # self.br.sendTransform([pose_t[0], pose_t[1], pose_t[2]],
            #                       quat_t,
            #                       rospy.Time.now(),
            #                       self.base_frame_2d,
            #                       self.odom_frame)

            self.t_now += self.dr_period

            # Update global variable
            self.pos_t = pose_t[0:3]

    def thrust_cb(self, thrust1_msg, thrust2_msg):
        dr = np.clip(-self.thrust_cmd.thruster_horizontal_radians, -7 * np.pi / 180, 7 * np.pi / 180)

        self.u = [thrust1_msg.rpm.rpm + thrust2_msg.rpm.rpm, dr]

    def depth_cb(self, depth_msg):

        # TODO: test with SAM data
        if self.depth_meas:
            self.base_depth = depth_msg.pose.pose.position.z + self.b2p_trans[0] * np.sin(self.rot_t[1])

    def sbg_cb(self, sbg_msg):
        self.init_quat = sbg_msg.orientation
        self.init_heading = True
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
        if self.init_stim and self.init_m2o:
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
            self.t_stim_prev = imu_msg.header.stamp
            self.init_stim = True

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
            self.get_logger().info("DVL data coming in")
            current_header = dvl_msg.header.stamp
            current_time = ros_time_to_secs(current_header)
            self.t_dvl_prev = current_time
            self.t_now = current_time
            self.t_pub = current_time
            self.dvl_on = True


# if __name__ == "__main__":
#     rospy.init_node('dr_node')
#     try:
#         VehicleDR()
#     except rospy.ROSInterruptException:
#         pass

def main(args=None):
    rclpy.init(args=args)
    dr_node = VehicleDR()
    try:
        rclpy.spin(dr_node)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
