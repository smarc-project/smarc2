
import rclpy
from rclpy.node import Node
import tf2_ros

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

        # subscribers
        self.sub_cell_1 = self.create_subscription(Float32, self.topic_cell_1, self.cell_1_cb, 10)
        self.sub_cell_2 = self.create_subscription(Float32, self.topic_cell_2, self.cell_2_cb, 10)
        self.sub_cell_3 = self.create_subscription(Float32, self.topic_cell_3, self.cell_3_cb, 10)





    def cell_1_cb(self, msg):
        self.log_info(f"Load cell 1: {msg.data:.4f} kg")

    def cell_2_cb(self, msg):
        self.log_info(f"Load cell 2: {msg.data:.4f} kg")

    def cell_3_cb(self, msg):
        self.log_info(f"Load cell 3: {msg.data:.4f} kg")

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
            ("frames.plate", "Plate"),
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
        frame_plate = self.get_parameter("frames.plate").value

        self.frame_cell_1 = f"{robot_name}/{frame_cell_1}"
        self.frame_cell_2 = f"{robot_name}/{frame_cell_2}"
        self.frame_cell_3 = f"{robot_name}/{frame_cell_3}"
        self.frame_output = f"{robot_name}/{frame_output}"
        self.frame_plate = f"{robot_name}/{frame_plate}"

        self.publish_rate = self.get_parameter("publish_rate").value

        self.logger_info_enable = self.get_parameter("logger_info.enable").value

def main():
    rclpy.init()
    node = RopeEstimationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()