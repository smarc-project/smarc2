
from geometry_msgs.msg import WrenchStamped
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import Float32

from smarc_georef_cpp import GeorefUtils, TransformException

class RopeEstimationNode(Node):
    """
    ROS2 Node for estimating rope direction and force from N load cells.

    This node subscribes to load cell topics, infers their geometry from TF,
    and publishes the estimated rope force/direction.
    """
    def __init__(self):
        super().__init__('rope_estimation_node')

        self.get_params()

        # tf
        self.georef = GeorefUtils(node=self)

        if self.num_load_cells < 3:
            self.get_logger().error("[RopeEstimationNode] The number of load cells must be >= 3!")
            raise ValueError("The number of load cells must be >= 3")

        self.lc_readings = np.zeros(self.num_load_cells) # load cell readings in kg
        self.readings_timestamps = np.zeros(self.num_load_cells) # timestamps of the load cell readings

        # subscribers
        self.lc_subs = [
            self.create_subscription(Float32, self.topic_cell_template.format(i+1), lambda msg, idx=i: self.load_cell_cb(msg, idx), 10)
            for i in range(self.num_load_cells)
        ]
        # publishers
        self.force_pub = self.create_publisher(WrenchStamped, self.topic_output, 10)

        self.equation_matrix = None

        self.create_timer(1.0 / self.publish_rate, self.publish_rope_estimation)

        self.log_info("Rope Estimation node initialized.")

    def build_equation_matrix(self):
        """
        Build the equation matrix from the load cell transforms.
        The matrix is used to solve for the rope force vector via force and torque balance equations.
        """
        transforms = []
        try:
            for i in range(self.num_load_cells):
                transforms.append(self.georef.lookup_transform(self.frame_rope, self.frame_lcs[i],rclpy.time.Time()))
        except TransformException as e:
            self.log_info(f"Error looking up transforms: {e}")
            return None

        # Extract positions
        # TODO: check that z part is 0 (i.e., all load cells are in the same plane)
        equation_matrix = np.ones((3,self.num_load_cells)) # 3 equations:
        # force balance: sum(F_i) = -F_z
        # torque balance 1: sum(y_i * F_i) = - plate_width * F_y
        # torque balance 2: sum(x_i * F_i) = - plate_width * F_x
        for i in range(self.num_load_cells):
            equation_matrix[1,i] = transforms[i].transform.translation.y
            equation_matrix[2,i] = transforms[i].transform.translation.x
        # check if the matrix is full rank
        if (np.linalg.matrix_rank(equation_matrix) < 3):
            self.get_logger().error("[RopeEstimationNode] The load cells are collinear!")
            return None
        return equation_matrix

    def publish_rope_estimation(self):
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
        force_vector[1] = -b[1] / self.plate_width
        force_vector[0] = -b[2] / self.plate_width
        self.publish_transform(force_vector)
        self.log_info(f"Estimated rope force: {force_vector}")
        

    def publish_transform(self, translation):
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

    def load_cell_cb(self, msg, idx):
        self.lc_readings[idx] = msg.data
        self.readings_timestamps[idx] = self.get_clock().now().nanoseconds / 1e9

    def log_info(self, msg):
        if self.logger_info_enable:
            self.get_logger().info(msg)

    def get_params(self):
        PARAMS = [
            ("topics.load_cell_template", "sensor/load_cell_{}"),
            ("topics.sub_timeout", 0.5),
            ("topics.output", "rope_force"),

            
            ("frames.load_cell_template", "LoadCell{}"),
            ("frames.rope_link", "rope_base_link"),

            ("robot_name", "sim_M350"), # basically just for sim (because it differs from namespace)
            ("plate_width", 0.05),
            ("num_load_cells", 4),

            ("publish_rate", 10.0),
            ("logger_info.enable", True)
        ]
        self.declare_parameters(namespace = "", parameters = PARAMS)

        self.num_load_cells = self.get_parameter("num_load_cells").value

        self.plate_width = self.get_parameter("plate_width").value
        self.topic_cell_template = self.get_parameter("topics.load_cell_template").value
        self.topic_output = self.get_parameter("topics.output").value
        self.sub_timeout = self.get_parameter("topics.sub_timeout").value

        robot_name = self.get_parameter("robot_name").value
        self.frame_cell_template = self.get_parameter("frames.load_cell_template").value
        frame_rope = self.get_parameter("frames.rope_link").value

        # check the templates:
        if "{}" not in self.topic_cell_template:
            raise ValueError("Topic template must contain {}")
        if "{}" not in self.frame_cell_template:
            raise ValueError("Frame template must contain {}")

        self.frame_lcs = [f"{robot_name}/{self.frame_cell_template.format(i+1)}" for i in range(self.num_load_cells)]
        self.frame_rope = f"{robot_name}/{frame_rope}"
        self.publish_rate = self.get_parameter("publish_rate").value

        self.logger_info_enable = self.get_parameter("logger_info.enable").value

        

        
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