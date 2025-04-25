#!/usr/bin/python3
import sys
import rclpy
from rclpy.node import Node
from rclpy import time

# ROS imports
from builtin_interfaces.msg import Time as Stamp
from geometry_msgs.msg import TransformStamped
from rclpy.time import Time as rcl_Time

from std_msgs.msg import Float64
from smarc_msgs.msg import ThrusterRPM, PercentStamped
from sam_msgs.msg import Topics as SamTopics
from sam_msgs.msg import ThrusterAngles
from nav_msgs.msg import Odometry
from smarc_control_msgs.msg import Topics as ControlTopics


from rclpy.executors import MultiThreadedExecutor

class SetpointPublisher():
    """
    Simple set point publisher for development and debugging purposes.
    Publishes setpoint pose to a topic the controller listens to.
    """
    def __init__(self, node: Node) -> None:

        self._node = node

        self._node.declare_parameter('robot_name')
        self._node.declare_parameter('tf_suffix')
        self.tf_suffix = self._node.get_parameter('tf_suffix').get_parameter_value().string_value
        self.robot_name = self._node.get_parameter('robot_name').get_parameter_value().string_value

        self._states = Odometry()

        self.state_sub = node.create_subscription(msg_type=Odometry, topic=ControlTopics.STATES, callback=self._states_cb, qos_profile=10)

        self._setpoint_pub = node.create_publisher(Odometry, ControlTopics.WAYPOINT, 10) 
        self._setpoint_msg = Odometry()

        self.received_current_state = False
        self.created_waypoint = False

        self._loginfo("Created Setpoint Publisher")


    def _loginfo(self, s):
        self._node.get_logger().info(s)

    def _states_cb(self, msg):
        self._states = msg
        self.received_current_state = True

    def _create_waypoint_message(self):

        current_x = self._states.pose.pose.position.x
        current_y = self._states.pose.pose.position.y

        self._setpoint_msg.header.stamp = self.rcl_time_to_stamp(self._node.get_clock().now())
        #self._setpoint_msg.header.frame_id = self.robot_name + '/map' + self.tf_suffix # NOTE: map frame to be in the same frame as the states.
        self._setpoint_msg.header.frame_id = 'map' + self.tf_suffix # NOTE: map frame to be in the same frame as the states.
        self._setpoint_msg.pose.pose.position.x = current_x
        self._setpoint_msg.pose.pose.position.y = current_y
        self._setpoint_msg.pose.pose.position.z = -1.0
        self._setpoint_msg.pose.pose.orientation.x = 0.0
        self._setpoint_msg.pose.pose.orientation.y = 0.0
        self._setpoint_msg.pose.pose.orientation.z = 0.0
        self._setpoint_msg.pose.pose.orientation.w = 1.0

        self.created_waypoint = True

    def rcl_time_to_stamp(self,time: rcl_Time) -> Stamp:
        """
        Converts rcl Time to stamp
        :param time:
        :return:
        """
        stamp = Stamp()
        stamp.sec = int(time.nanoseconds // 1e9)
        stamp.nanosec = int(time.nanoseconds % 1e9)
        return stamp

    def update(self) -> None:
        """
        Publish setpoint message
        """
        if not self.created_waypoint:
            if self.received_current_state:
                self._create_waypoint_message()
        else:
            self._setpoint_pub.publish(self._setpoint_msg)
            #self._loginfo(f"SN: WP: {self._setpoint_msg.pose.pose.position}")


def main():
    """
    Node to publish a setpoint when debugging controller
    Use with: ros2 run dive_control setpoint
    """

    rclpy.init(args=sys.argv)
    node = rclpy.create_node("SetpointNode")
    setpoint_pub = SetpointPublisher(node)

    node_rate = 1/10

    def _loginfo(node, s):
        node.get_logger().info(s)

    _loginfo(node,"Setpoint Node created")

    node.create_timer(node_rate, setpoint_pub.update)

    executor = MultiThreadedExecutor()

    try:
        rclpy.spin(node, executor=executor)
    except KeyboardInterrupt:
        pass

    node.get_logger().info("Shutting down")


# Could also run this without ros2
if __name__ == "__main__":
    main()
