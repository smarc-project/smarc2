import rclpy
from rclpy.node import Node

# General messages
from sensor_msgs.msg import Imu
from std_msgs.msg import Int8, Float64

# SMaRC messages
from smarc_msgs.msg.Topics import VEHICLE_HEALTH_WAITING, VEHICLE_HEALTH_READY, VEHICLE_HEALTH_ERROR

# Vehicle specific messages -- Consider how to handle this
from ixblue_ins_msgs.msg import Ins, DiagnosticArray


try:
    from .helpers.health_helpers import TopicRateMonitor
except ImportError:
    from helpers.health_helpers import TopicRateMonitor


class RateMonitorNode(Node):
    """
    This is a basic example of how health checks will be performed

    The values are currently hard coded for lolo
    """
    def __init__(self, namespace=None):
        super().__init__('Rate_monitor_node', namespace=namespace)

        self.get_logger().info(dict(self.get_topic_names_and_types()))

        self.verbose = True
        self.check_period = 1.0

        # Topic rate monitor parameters
        self.timeout_time_sec = 2.0  # This is a little redundant maybe... I guess

        monitored_topics = {
            '/ix/ins': [Ins, 5],
            'diagnostics': [DiagnosticArray, 5]
        }

        self.get_logger().info(f"Generic health check instantiated")
        self.monitor = TopicRateMonitor(self, monitored_topics, timeout_time_sec=self.timeout_time_sec,
                                        verbose=self.verbose)

        self.declare_parameter("report_topic", "rate_monitor_status")
        self.report_topic = self.get_parameter("report_topic").value

        self.report_pub = self.create_publisher(msg_type=Int8, topic=self.report_topic, qos_profile=1)
        self.report_timer = self.create_timer(timer_period_sec=float(1.0/self.check_period),
                                              callback=self.report_callback)

    def report_callback(self):
        """
        Perform
        """
        if self.monitor.fault:
            fault_msg = Int8()
            fault_msg.data = VEHICLE_HEALTH_ERROR
            self.report_pub.publish(fault_msg)
        elif self.monitor.ready:
            ready_msg = Int8()
            ready_msg.data = VEHICLE_HEALTH_READY
            self.report_pub.publish(ready_msg)
        else:
            waiting_msg = Int8()
            waiting_msg.data = VEHICLE_HEALTH_WAITING
            self.report_pub.publish(waiting_msg)


def main(args=None, namespace=None):
    rclpy.init(args=args)
    lolo_health_node = RateMonitorNode(namespace=namespace)
    try:
        rclpy.spin(lolo_health_node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    default_namespace = "lolo"
    main(namespace=default_namespace)
