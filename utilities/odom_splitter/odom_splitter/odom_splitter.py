#!/usr/bin/python

# ROS
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
import tf_transformations

# Messages
from std_msgs.msg import Float32
from nav_msgs.msg import Odometry

# SMaRC Topics
from smarc_control_msgs.msg import Topics as ControlTopics
from smarc_msgs.msg import Topics as SmarcTopics


class OdomSplitter(Node):
    """
    This node splits a standard Odometry message to individual
    topics used for low-level controllers.
    """

    def __init__(self, namespace=None):
        super().__init__("odom_splitter", namespace=namespace)
        self._log("Starting the odom splitter node.")

        # Input odometry.
        self.input_odom_topic = f"{SmarcTopics.ODOM_TOPIC}"
        self.odom_sub = self.create_subscription(msg_type=Odometry,
                                                 topic=self.input_odom_topic,
                                                 callback=self.odom_callback,
                                                 qos_profile=QoSProfile(depth=1))

        # Publishers.
        # === Yaw ===
        self.ctrl_yaw_pub = self.create_publisher(msg_type=Float32,
                                                  topic=f"{ControlTopics.CONTROL_YAW_TOPIC}",
                                                  qos_profile=QoSProfile(depth=1))

        self.ctrl_yaw_rate_pub = self.create_publisher(msg_type=Float32,
                                                       topic=f"{ControlTopics.CONTROL_YAW_RATE_TOPIC}",
                                                       qos_profile=QoSProfile(depth=1))

        # === pitch ===
        self.ctrl_pitch_pub = self.create_publisher(msg_type=Float32,
                                                  topic=f"{ControlTopics.CONTROL_PITCH_TOPIC}",
                                                  qos_profile=QoSProfile(depth=1))

        self.ctrl_pitch_rate_pub = self.create_publisher(msg_type=Float32,
                                                       topic=f"{ControlTopics.CONTROL_PITCH_RATE_TOPIC}",
                                                       qos_profile=QoSProfile(depth=1))

        # === roll ===
        self.ctrl_roll_pub = self.create_publisher(msg_type=Float32,
                                                  topic=f"{ControlTopics.CONTROL_ROLL_TOPIC}",
                                                  qos_profile=QoSProfile(depth=1))

        self.ctrl_roll_rate_pub = self.create_publisher(msg_type=Float32,
                                                       topic=f"{ControlTopics.CONTROL_ROLL_RATE_TOPIC}",
                                                       qos_profile=QoSProfile(depth=1))

        # === Other ===
        self.ctrl_surge_rate_pub = self.create_publisher(msg_type=Float32,
                                                         topic=f"{ControlTopics.CONTROL_SURGE_RATE_TOPIC}",
                                                         qos_profile=QoSProfile(depth=1))

    def _log(self, message):
        self.get_logger().info(message)

    def odom_callback(self, msg):

        orientation_q = msg.pose.pose.orientation
        orientation_rpy = tf_transformations.euler_from_quaternion([orientation_q.x,
                                                                    orientation_q.y,
                                                                    orientation_q.z,
                                                                    orientation_q.w])

        # === Orientations ===
        # Roll
        roll_msg = Float32()
        roll_msg.data = orientation_rpy[0]
        self.ctrl_roll_pub.publish(roll_msg)
        # Pitch
        pitch_msg = Float32()
        pitch_msg.data = orientation_rpy[1]
        self.ctrl_pitch_pub.publish(pitch_msg)
        # Yaw
        yaw_msg = Float32()
        yaw_msg.data = orientation_rpy[2]
        self.ctrl_yaw_pub.publish(yaw_msg)

        # === Rates ===
        # Roll
        roll_msg.data = msg.twist.twist.angular.x
        self.ctrl_roll_rate_pub.publish(roll_msg)
        # pitch
        pitch_msg.data = msg.twist.twist.angular.y
        self.ctrl_pitch_rate_pub.publish(pitch_msg)
        # yaw
        yaw_msg.data = msg.twist.twist.angular.z
        self.ctrl_yaw_rate_pub.publish(yaw_msg)
        # surge
        surge_msg = Float32()
        surge_msg.data = msg.twist.twist.linear.x
        self.ctrl_surge_rate_pub.publish(surge_msg)


def main(args=None, namespace=None):
    rclpy.init(args=args)
    odom_splitter_node = OdomSplitter(namespace=namespace)
    try:
        rclpy.spin(odom_splitter_node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    default_namespace = "lolo"
    main(namespace=default_namespace)
