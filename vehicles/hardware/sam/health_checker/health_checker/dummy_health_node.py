import rclpy
from rclpy.node import Node

# General messages
from std_msgs.msg import Int8

# SMaRC messages
from smarc_msgs.msg import Topics as SmarcTopics  # VEHICLE_HEALTH_WAITING, VEHICLE_HEALTH_READY, VEHICLE_HEALTH_ERROR


class DummyHealthNode(Node):
    """
    This is a basic example of how health checks will be performed
    """
    def __init__(self, namespace=None):
        super().__init__('dummy_health_node', namespace=namespace)
        self.get_logger().info(f"Dummy health check")


        # Topic rate monitor paramters
        self.declare_parameter('output_rate', 1.0)
        self.output_rate = self.get_parameter('output_rate').value

        self.declare_parameter('timeout_time_sec', 2.0)
        self.timeout_time_sec = self.get_parameter('timeout_time_sec').value

        self.declare_parameter("report_topic", SmarcTopics.VEHICLE_HEALTH_TOPIC)
        self.report_topic = self.get_parameter("report_topic").value

        self.report_pub = self.create_publisher(msg_type=Int8, topic=self.report_topic, qos_profile=1)
        self.report_timer = self.create_timer(timer_period_sec=float(1.0/self.output_rate),
                                              callback=self.publish_ready)

    def publish_ready(self):
        """
        Perform
        """
        ready_msg = Int8()
        ready_msg.data = SmarcTopics.VEHICLE_HEALTH_READY
        self.report_pub.publish(ready_msg)


def main(args=None, namespace=None):
    rclpy.init(args=args)
    lolo_health_node = DummyHealthNode(namespace=namespace)
    try:
        rclpy.spin(lolo_health_node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    default_namespace = "lolo"
    main(namespace=default_namespace)
