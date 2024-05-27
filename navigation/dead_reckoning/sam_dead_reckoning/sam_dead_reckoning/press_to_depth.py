#!/usr/bin/env python

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import FluidPressure
from geometry_msgs.msg import PoseWithCovarianceStamped

# Topics
from sam_msgs.msg import Topics as SamTopics
from dead_reckoning_msgs.msg import Topics as DRTopics

# Frames/Links
from sam_msgs.msg import Links as SamLinks

try:
    from .helpers.ros_helpers import rcl_time_to_stamp
except ImportError:
    from helpers.ros_helpers import rcl_time_to_stamp


class Press2Depth(Node):

    def __init__(self):
        super().__init__("press_to_depth_node")
        self.get_logger().info("Starting node defined in press_to_depth.py")

        # ===== Declare parameters =====
        self.declare_node_parameters()

        self.robot_name = self.get_parameter("robot_name").value

        self.odom_frame = self.get_parameter('odom_frame').value

        self.base_frame = f"{self.robot_name}_{SamLinks.BASE_LINK}"
        self.press_frame = f"{self.robot_name}_{SamLinks.PRESS_LINK}"  # Unused
        # Removed depth frame

        self.subs = self.create_subscription(msg_type=FluidPressure, topic=SamTopics.PRESS_DEPTH20_TOPIC,
                                             callback=self.depthCB, qos_profile=10)

        self.pub = self.create_publisher(msg_type=PoseWithCovarianceStamped, topic=DRTopics.DR_DEPTH_POSE_TOPIC,
                                         qos_profile=10)

        self.depth_msg = PoseWithCovarianceStamped()
        self.depth_msg.header.frame_id = self.odom_frame
        self.depth_msg.pose.covariance = [100., 0.0, 0.0, 0.0, 0.0, 0.0,
                                          0.0, 100., 0.0, 0.0, 0.0, 0.0,
                                          0.0, 0.0, 0.1, 0.0, 0.0, 0.0,
                                          0.0, 0.0, 0.0, 0.01, 0.0, 0.0,
                                          0.0, 0.0, 0.0, 0.0, 0.01, 0.0,
                                          0.0, 0.0, 0.0, 0.0, 0.0, 0.01]

        self.depth_msg.pose.pose.orientation.w = 1.

        # TODO is there a reason to have two listeners?
        # HAHA is there a reason for even one?
        # self.listener_odom = tf.TransformListener()  # remove
        # self.listener_press = tf.TransformListener()  # remove
        self.x_base_depth = 0.580

        # try:
        # 	(trans,quaternion) = self.listener_press.lookupTransform(self.base_frame, self.depth_frame, rospy.Time(10))

        # except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
        # 	print('Could not get tf base to depth.')

    def declare_node_parameters(self):
        """
        Declare the parameters for the node
        """

        # TODO This might be a bad way to set defaults
        # allows for me to run from the terminal directly for test
        default_robot_name = 'sam0'
        self.declare_parameter("robot_name", default_robot_name)

        self.declare_parameter('odom_frame', 'odom')

    # def depthCB_old(self, press_msg):
    #     try:
    #
    #         # # depth_abs is positive, must be manually negated
    #         depth_abs = - self.pascal_pressure_to_depth(press_msg.fluid_pressure)
    #         # rospy.loginfo("Depth abs %s", depth_abs)
    #         # rospy.loginfo("Fluid press %s", press_msg.fluid_pressure)
    #
    #         if press_msg.fluid_pressure > 90000. and press_msg.fluid_pressure < 500000.:
    #             self.depth_msg.header.stamp = rospy.Time.now()
    #             self.depth_msg.pose.pose.position.z = depth_abs  # = [0., 0., 2.]
    #             self.pub.publish(self.depth_msg)
    #
    #     except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
    #         rospy.logerr("Depth transform missing tf")

    def depthCB(self, press_msg):
        """
        callback for converting pressure message into a depth.
        """
        # depth_abs is positive, must be manually negated
        depth_abs = - self.pascal_pressure_to_depth(press_msg.fluid_pressure)
        # rospy.loginfo("Depth abs %s", depth_abs)
        # rospy.loginfo("Fluid press %s", press_msg.fluid_pressure)

        if press_msg.fluid_pressure > 90000. and press_msg.fluid_pressure < 500000.:
            self.depth_msg.header.stamp = rcl_time_to_stamp(self.get_clock().now())
            self.depth_msg.pose.pose.position.z = depth_abs  # = [0., 0., 2.]
            self.pub.publish(self.depth_msg)

    def pascal_pressure_to_depth(self, pressure):
        """
        Convert pressure in pascal to depth in meters

        What sensor is this for? The offset by 1 feels a little weird.

        P = pgh
        P: pascals, kg/ms^2
        p: density of water, kg/m^3
        g: accel due to gravity, m/s^2
        h: height of water column, m

        p(fresh) = 997.0  # random internet value
        p(salt) = 1023.6  # random internet value
        g(stockholm) = 9.818
        """
        # TODO check this
        return 10. * ((pressure / 100000.) - 1.)  # 117000 -> 1.7

    def simulated_pressure_to_depth(self, pressure: float) -> float:
        """
        Convert pressure from simulator in pascals to depth in meters.

        General:
        pressure = density * gravity * depth

        Unity:
        Unity uses a value of 9806.65 to convert from depth to pressure
        pressure = 9806.65 * depth
        """
        depth_to_pressure = 9806.65
        return pressure / depth_to_pressure


def main(args=None):
    rclpy.init(args=args)
    depth_node = Press2Depth()
    try:
        rclpy.spin(depth_node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
