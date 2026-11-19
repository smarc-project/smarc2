
from geometry_msgs.msg import WrenchStamped
import numpy as np
from numpy.typing import NDArray
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import Float32

from dji_msgs.msg import Topics as DJITopics
from dji_msgs.msg import Links  as DJILinks
from smarc_georef_cpp import GeorefUtils, TransformException

NUM_LOAD_CELLS: int = 3
ROPE_LEVER_ARM: float = 0.05

assert NUM_LOAD_CELLS in (3,4)

class RopeEstimationNode(Node):
    """
    ROS2 Node for estimating rope direction and force from 3/4 load cells.

    This node subscribes to load cell topics, infers their geometry from TF,
    and publishes the estimated rope force/direction.
    """
    def __init__(self) -> None:
        super().__init__('rope_estimation_node')

        # PARAMETERS
        self.declare_parameter("topics.sub_timeout", 0.5)
        self.sub_timeout : float = self.get_parameter("topics.sub_timeout").get_parameter_value().double_value

        self.declare_parameter("topics.publish_rate", 10.0)
        self.publish_rate : float = self.get_parameter("topics.publish_rate").get_parameter_value().double_value

        self.declare_parameter("logger_info.enable", True)
        self.logger_info_enable : bool = self.get_parameter("logger_info.enable").get_parameter_value().bool_value

        # tf
        ns = self.get_namespace().strip("/")
        lc_links = [DJILinks.LOAD_CELL_1_LINK, DJILinks.LOAD_CELL_2_LINK, DJILinks.LOAD_CELL_3_LINK, DJILinks.LOAD_CELL_4_LINK]
        self.frame_lcs = [f"{ns}/{lc_links[i]}" for i in range(NUM_LOAD_CELLS)]
        self.frame_rope = f"{ns}/{DJILinks.ROPE_BASE_LINK}" # the rope pivot

        self.georef = GeorefUtils(node=self)


        self.lc_readings = np.zeros(NUM_LOAD_CELLS) # load cell readings in kg
        self.readings_timestamps = np.zeros(NUM_LOAD_CELLS) # timestamps of the load cell readings

        # subscribers
        load_cell_topics = [DJITopics.LOAD_CELL_1_WEIGHT_TOPIC, DJITopics.LOAD_CELL_2_WEIGHT_TOPIC, DJITopics.LOAD_CELL_3_WEIGHT_TOPIC, DJITopics.LOAD_CELL_4_WEIGHT_TOPIC]
        self.lc_subs = [
            self.create_subscription(Float32, load_cell_topics[i], lambda msg, idx=i: self.load_cell_cb(msg, idx), 10)
            for i in range(NUM_LOAD_CELLS)
        ]
        # publishers
        self.force_pub = self.create_publisher(WrenchStamped, DJITopics.ROPE_FORCE_ESTIMATE_TOPIC, 10)

        self.equation_matrix : NDArray[np.float64] | None = None

        self.create_timer(1.0 / self.publish_rate, self.publish_rope_estimation)

        self.log_info("Rope Estimation node initialized.")

    def build_equation_matrix(self) -> NDArray[np.float64] | None:
        """
        Build the equation matrix from the load cell transforms.
        The matrix is used to solve for the rope force vector via force and torque balance equations.
        """
        transforms = []
        try:
            for i in range(NUM_LOAD_CELLS):
                transforms.append(self.georef.lookup_transform(self.frame_rope, self.frame_lcs[i]))
        except TransformException as e:
            self.log_info(f"Error looking up transforms: {e}")
            return None

        # Extract positions
        equation_matrix = np.ones((3,NUM_LOAD_CELLS)) # 3 equations:
        # force balance: sum(F_i) = -F_z
        # torque balance 1: sum(y_i * F_i) = - ROPE_LEVER_ARM * F_y
        # torque balance 2: sum(x_i * F_i) = - ROPE_LEVER_ARM * F_x
        for i in range(NUM_LOAD_CELLS):
            equation_matrix[1,i] = transforms[i].transform.translation.y
            equation_matrix[2,i] = transforms[i].transform.translation.x
        # check if the matrix is full rank
        if (np.linalg.matrix_rank(equation_matrix) < 3):
            self.get_logger().error("[RopeEstimationNode] The load cells are collinear!")
            return None
        return equation_matrix

    def publish_rope_estimation(self) -> None:
        if self.equation_matrix is None:
            self.equation_matrix = self.build_equation_matrix()
            if self.equation_matrix is None:
                return
        # Check if the readings are recent enough
        current_time = self.get_clock().now().nanoseconds / 1e9
        if np.any(current_time - self.readings_timestamps > self.sub_timeout):
            self.get_logger().warn("Load cell readings are too old, skipping estimation.", throttle_duration_sec=2.0)
            return
        # right hand side of the equation:
        force_vector = np.zeros(3)
        b = self.equation_matrix @ self.lc_readings*9.81
        force_vector[2] = -b[0]
        force_vector[1] = -b[1] / ROPE_LEVER_ARM
        force_vector[0] = -b[2] / ROPE_LEVER_ARM
        self.publish_force(force_vector)
        self.log_info(f"Estimated rope force: {force_vector}")
        

    def publish_force(self, translation: NDArray[np.float64]) -> None:
        """
        Publishes the estimated rope force as a WrenchStamped message.
        """
        msg = WrenchStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_rope
        msg.wrench.force.x = translation[0]
        msg.wrench.force.y = translation[1]
        msg.wrench.force.z = translation[2]
        self.force_pub.publish(msg)

    def load_cell_cb(self, msg: Float32, idx: int) -> None:
        self.lc_readings[idx] = msg.data
        self.readings_timestamps[idx] = self.get_clock().now().nanoseconds / 1e9

    def log_info(self, msg: str) -> None:
        if self.logger_info_enable:
            self.get_logger().info(msg)
        

def main():
    rclpy.init()
    node = RopeEstimationNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()