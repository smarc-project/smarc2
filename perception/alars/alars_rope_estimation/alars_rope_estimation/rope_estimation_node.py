
import rclpy
from rclpy.node import Node
import tf2_ros
import numpy as np
from std_msgs.msg import Float32

class RopeEstimationNode(Node):
    """
    ROS2 Node for estimating rope direction and force from 3 load cells.

    This node subscribes to the 3 load cell topics, infers their geometry from TF,
    and publishes the estimated rope force/direction as a TF transform.
    """
    def __init__(self):
        super().__init__('rope_estimation_node')

        self.get_params()

        self.log_info("Rope Estimation node initialized.")

        # tf
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        self.lc_readings = np.zeros(3) # load cell readings in kg
        # subscribers
        self.sub_cell_1 = self.create_subscription(Float32, self.topic_cell_1, self.cell_1_cb, 10)
        self.sub_cell_2 = self.create_subscription(Float32, self.topic_cell_2, self.cell_2_cb, 10)
        self.sub_cell_3 = self.create_subscription(Float32, self.topic_cell_3, self.cell_3_cb, 10)

        self.equation_matrix = None

        self.create_timer(1.0 / self.publish_rate, self.publish_rope_estimation)

    def build_equation_matrix(self):
        """
        Build the equation matrix from the load cell transforms.
        The matrix is used to solve for the rope force vector via force and torque balance equations.
        """
        try:
            tf_cell_1 = self.tf_buffer.lookup_transform(self.frame_rope, self.frame_cell_1, rclpy.time.Time())
            tf_cell_2 = self.tf_buffer.lookup_transform(self.frame_rope, self.frame_cell_2, rclpy.time.Time())
            tf_cell_3 = self.tf_buffer.lookup_transform(self.frame_rope, self.frame_cell_3, rclpy.time.Time())
        except tf2_ros.TransformException as e:
            self.log_info(f"Error looking up transforms: {e}")
            return None

        # Extract positions
        p1 = [tf_cell_1.transform.translation.x, tf_cell_1.transform.translation.y, tf_cell_1.transform.translation.z]
        p2 = [tf_cell_2.transform.translation.x, tf_cell_2.transform.translation.y, tf_cell_2.transform.translation.z]
        p3 = [tf_cell_3.transform.translation.x, tf_cell_3.transform.translation.y, tf_cell_3.transform.translation.z]
        # TODO: check that z part is 0 (i.e., all load cells are in the same plane)
        # TODO: Make the estimation available to 3/4/... number of load cells
        equation_matrix = np.array([
            [1, 1, 1], # force balance: sum(F_i) = -F_z
            [p1[1], p2[1], p3[1]], # torque balance 1: sum(y_i * F_i) = - plate_width * F_y
            [p1[0], p2[0], p3[0]] # torque balance 2: sum(x_i * F_i) = - plate_width * F_x
        ])
        return equation_matrix

    def publish_rope_estimation(self):
        if self.equation_matrix is None:
            self.equation_matrix = self.build_equation_matrix()
            if self.equation_matrix is None:
                return
        # right hand side of the equation:
        force_vector = np.zeros(3)
        b = self.equation_matrix @ self.lc_readings*9.81
        force_vector[2] = -b[0]
        force_vector[1] = -b[1] / self.plate_width
        force_vector[0] = -b[2] / self.plate_width
        self.log_info(f"Estimated rope force: {force_vector}")
        # TODO: publish force vector as a TF



    def cell_1_cb(self, msg):
        self.lc_readings[0] = msg.data

    def cell_2_cb(self, msg):
        self.lc_readings[1] = msg.data

    def cell_3_cb(self, msg):
        self.lc_readings[2] = msg.data

    def log_info(self, msg):
        if self.logger_info_enable:
            self.get_logger().info(msg)

    def get_params(self):
        PARAMS = [
            ("topics.load_cell_1", "sensor/load_cell_1"),
            ("topics.load_cell_2", "sensor/load_cell_2"),
            ("topics.load_cell_3", "sensor/load_cell_3"),

            ("robot_name", "sim_M350"), # basically just for sim (because it differs from namespace)
            ("frames.load_cell_1", "LoadCell1"),
            ("frames.load_cell_2", "LoadCell2"),
            ("frames.load_cell_3", "LoadCell3"),
            ("frames.rope_link", "rope_base_link"),
            ("frames.output", "predicted_rope_link"),

            ("plate_width", 0.1),

            ("publish_rate", 10.0),

            ("logger_info.enable", True)
        ]
        self.declare_parameters(namespace = "", parameters = PARAMS)

        self.plate_width = self.get_parameter("plate_width").value
        self.topic_cell_1 = self.get_parameter("topics.load_cell_1").value
        self.topic_cell_2 = self.get_parameter("topics.load_cell_2").value
        self.topic_cell_3 = self.get_parameter("topics.load_cell_3").value

        robot_name = self.get_parameter("robot_name").value
        frame_cell_1 = self.get_parameter("frames.load_cell_1").value
        frame_cell_2 = self.get_parameter("frames.load_cell_2").value
        frame_cell_3 = self.get_parameter("frames.load_cell_3").value
        frame_output = self.get_parameter("frames.output").value
        frame_rope = self.get_parameter("frames.rope_link").value

        self.frame_cell_1 = f"{robot_name}/{frame_cell_1}"
        self.frame_cell_2 = f"{robot_name}/{frame_cell_2}"
        self.frame_cell_3 = f"{robot_name}/{frame_cell_3}"
        self.frame_output = f"{robot_name}/{frame_output}"
        self.frame_rope = f"{robot_name}/{frame_rope}"
        self.publish_rate = self.get_parameter("publish_rate").value

        self.logger_info_enable = self.get_parameter("logger_info.enable").value

def main():
    rclpy.init()
    node = RopeEstimationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()