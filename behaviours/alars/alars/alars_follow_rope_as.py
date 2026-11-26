import rclpy
import numpy as np
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from dji_msgs.msg import Links as DJILinks
from dji_msgs.msg import Topics as DJITopics

from geometry_msgs.msg import WrenchStamped, TwistStamped
from smarc_action_base.gentler_action_server import GentlerActionServer
from alars.alars_common import DroneState

from tf2_ros import Vector3Stamped

LOOP_FREQUENCY = 10  # Hz

class FollowRopeAction():
    """
    Keeps the rope vector parallel to the drone's vertical axis by moving the drone in the horizontal plane.
    """
    def __init__(self,
                 node: Node):
        self._node = node
        self._node.declare_parameter('robot_name', 'M350')
        self._robot_name = self._node.get_parameter('robot_name').get_parameter_value().string_value
        self.BASE_FLAT_FRAME = self._robot_name +'/' + DJILinks.BASE_FLAT
        # Initialize the action server with the node and action name
        self._node.declare_parameter('topic_rope', DJITopics.ROPE_FORCE_ESTIMATE_TOPIC)
        self._topic_rope = self._node.get_parameter('topic_rope').get_parameter_value().string_value
        self._rope_force_sub = self._node.create_subscription(WrenchStamped, self._topic_rope, self._sub_cb, 10)
        self._rope_force_timeout = 0.5 # seconds
        self._last_sub_time = self._node.get_clock().now()
        self._drone_state = DroneState(node, self._robot_name)

        self._rope_force = np.zeros(3)
        # velocity publisher
        self._setpoint_pub = self._node.create_publisher(
            msg_type = TwistStamped,
            topic = DJITopics.VELOCITY_SETPOINT_TOPIC,
            qos_profile= 10
        )
        # control variables
        self._last_angle = None # error for the PD controller
        self._node.declare_parameter('min_force_magnitude', 1.0)
        self._min_force_magnitude = self._node.get_parameter('min_force_magnitude').get_parameter_value().double_value
        self._node.declare_parameter('min_angle', 0.3)
        self._min_angle = self._node.get_parameter('min_angle').get_parameter_value().double_value
        self._node.declare_parameter('max_vel', 1.0)
        self.max_vel = self._node.get_parameter('max_vel').get_parameter_value().double_value
        # PD controller gains
        self._node.declare_parameter('K_p', 0.5)
        self._K_p = self._node.get_parameter('K_p').get_parameter_value().double_value
        self._node.declare_parameter('K_d', 0.05)
        self._K_d = self._node.get_parameter('K_d').get_parameter_value().double_value

        self._as = GentlerActionServer(
            node,
            "follow_rope",
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency=LOOP_FREQUENCY
        )

    def _on_goal_received(self, goal_request: dict) -> bool:
        self._node.get_logger().info(f"Received goal request: {goal_request}")
        return True
    
    def _on_cancel_received(self) -> bool:
        self._node.get_logger().info("Received cancel request")
        return True
    
    def _prepare_loop(self) -> None:
        self._node.get_logger().info("Preparing loop for action execution")
        self._last_angle = None

    def _loop_inner(self) -> bool | None:
        # project the rope force onto the horizontal plane
        f_xy = np.linalg.norm(self._rope_force[:2])
        angle = np.arctan2(f_xy, -self._rope_force[2])
        if self._node.get_clock().now() - self._last_sub_time > rclpy.duration.Duration(seconds=self._rope_force_timeout):
                self._node.get_logger().warn("Rope force data timeout. Stopping the drone.")
                return False
        if self._last_angle is None:
            self._last_angle = angle
        if angle < self._min_angle:
            self._last_angle = angle
            return None
        if np.linalg.norm(self._rope_force) < self._min_force_magnitude:
            self._last_angle = angle
            return None
        amplitude = self._K_p * (angle - self._min_angle) + self._K_d * (angle - self._last_angle)/(1/LOOP_FREQUENCY)
        self._last_angle = angle
        # limit the amplitude to max_vel
        amplitude = np.clip(amplitude, -self.max_vel, self.max_vel)
        # create a velocity vector in the direction of the rope
        vel = amplitude * self._rope_force[:2] / f_xy 
        self._publish_velocity(vel[0], vel[1])
        return None
    
    def _give_feedback(self) -> str:
        feedback = f"Action is in progress"
        self._node.get_logger().info(feedback)
        # Here you would typically generate feedback for the action
        # This is run after each _loop_inner call
        return feedback

    def _publish_velocity(self, vel_x, vel_y):
        msg = TwistStamped()
        msg.header.frame_id = self.BASE_FLAT_FRAME
        msg.header.stamp = self._node.get_clock().now().to_msg()
        msg.twist.linear.x = float(vel_x)
        msg.twist.linear.y = float(vel_y)
        self._setpoint_pub.publish(msg)

    def _sub_cb(self, msg: WrenchStamped) -> None:
        transformed = self._force_to_base_flat(msg)
        if transformed is None:
            return
        self._rope_force = np.array([transformed.vector.x, transformed.vector.y, transformed.vector.z])
        self._last_sub_time = self._node.get_clock().now()

    def _force_to_base_flat(self, force: WrenchStamped):
        force_vector = Vector3Stamped()
        force_vector.header.stamp = force.header.stamp
        force_vector.header.frame_id = force.header.frame_id
        force_vector.vector.x = force.wrench.force.x
        force_vector.vector.y = force.wrench.force.y
        force_vector.vector.z = force.wrench.force.z
        res = self._drone_state.vector_stamped_in_base_flat(force_vector)
        return res



def main():
    rclpy.init()
    node = Node("follow_rope_action_server")
    
    FollowRopeAction(node)

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down Follow Rope Action server")
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()
