from dataclasses import dataclass, field

import rclpy
from rclpy.node import Node

# General messages
from sensor_msgs.msg import Imu
from std_msgs.msg import Int8, Float64
from sensor_msgs.msg import BatteryState, Imu

# SMaRC messages
from smarc_msgs.msg import Topics as SmarcTopics
from smarc_msgs.msg import Leak, DVL

# Vehicle specific messages -- Consider how to handle this
from sam_msgs.msg import Topics as SamTopics
from diagnostic_msgs.msg import DiagnosticArray

try:
    from .helpers.health_helpers import TopicRateMonitor
except ImportError:
    from helpers.health_helpers import TopicRateMonitor


@dataclass
class StatusReport:
    ready: bool = field(default=False)
    fault: bool = field(default=False)


class MonitorNode(Node):
    """
    This is a basic example of how health checks will be performed
    """

    def __init__(self, namespace=None):
        super().__init__('Rate_monitor_node', namespace=namespace)
        self.namespace = namespace

        # === Load Parameters ===
        self.declare_parameter('verbose', False)
        self.verbose = self.get_parameter("verbose").value

        self.declare_parameter("output_rate", 1.0)
        self.output_rate = self.get_parameter("output_rate").value

        # Leak and batter parameters
        self.declare_parameter("leak_topic", SamTopics.LEAK_TOPIC_FB)
        self.leak_topic = self.get_parameter("leak_topic").value

        self.declare_parameter("battery_topic", SamTopics.BATTERY_STATUS_TOPIC)
        self.battery_topic = self.get_parameter("battery_topic").value

        self.declare_parameter("battery_min_voltage", 20.0)
        self.battery_min_voltage = self.get_parameter("battery_min_voltage").value

        self.declare_parameter("battery_min_capacity", 0.25)
        self.battery_min_capacity = self.get_parameter("battery_min_capacity").value

        # Topic rate monitor parameters
        # time since start if no message is received
        self.declare_parameter("initial_timeout_time_sec", 30.0)
        self.initial_timeout_time_sec = self.get_parameter("initial_timeout_time_sec").value

        # time since last message was received
        self.declare_parameter("timeout_time_sec", 5.0)
        self.timeout_time_sec = self.get_parameter("timeout_time_sec").value

        self.declare_parameter("report_topic", SmarcTopics.VEHICLE_HEALTH_TOPIC)
        self.report_topic = self.get_parameter("report_topic").value

        if self.verbose:
            self.log_all_parameters()

        # === Hardcoded topics, message types, and rates ===
        monitored_topics = {
            '/diagnostics': [DiagnosticArray, .5],
            SamTopics.DVL_TOPIC: [DVL, 1.0],
            SamTopics.STIM_IMU_TOPIC: [Imu, 20.0]
        }

        self.start_time = self.get_clock().now().nanoseconds/1e9
        self.current_leak = None
        self.current_leak_time = None
        self.current_leak_status = StatusReport()
        self.current_battery = None
        self.current_battery_time = None
        self.current_battery_status = StatusReport()

        # === Set up subs, pubs, and timers ===
        self.leak_sub = self.create_subscription(msg_type=Leak,
                                                 topic=self.leak_topic,
                                                 callback=self.leak_callback,
                                                 qos_profile=10)

        self.battery_sub = self.create_subscription(msg_type=BatteryState,
                                                    topic=self.battery_topic,
                                                    callback=self.battery_callback,
                                                    qos_profile=10)

        self.get_logger().info(f"topic rate monitor instantiated")
        self.monitor = TopicRateMonitor(self, monitored_topics, timeout_time_sec=self.timeout_time_sec,
                                        verbose=self.verbose)

        self.report_pub = self.create_publisher(msg_type=Int8, topic=self.report_topic, qos_profile=10)
        self.report_timer = self.create_timer(timer_period_sec=float(1.0 / self.output_rate),
                                              callback=self.output_callback)

    def leak_callback(self, msg):
        self.current_leak = msg
        self.current_leak_time = self.get_clock().now().nanoseconds/1e9

    def battery_callback(self, msg):
        self.current_battery = msg
        self.current_battery_time = self.get_clock().now().nanoseconds/1e9

    def leak_check(self):

        if self.current_leak_status.fault:
            return self.current_leak_status

        check_time = self.get_clock().now().nanoseconds/1e9

        if self.current_leak is None:
            if check_time - self.start_time > self.initial_timeout_time_sec:
                self.get_logger().warn(f"Fault detected: Leak initial time out!")
                self.current_leak_status.fault = True
        else:
            self.current_leak_status.ready = True

            if self.current_leak.value:
                self.get_logger().warn(f"Fault detected: Leak!")
                self.current_leak_status.fault = True

            if (check_time - self.current_leak_time) > self.timeout_time_sec:
                self.get_logger().warn(f"Fault detected: Leak time out!")
                self.current_leak_status.fault = True

        if self.verbose:
            self.get_logger().info(f"Leak: {self.current_leak_status}")

        return self.current_leak_status

    def battery_check(self):

        if self.current_battery_status.fault:
            return self.current_battery_status

        check_time = self.get_clock().now().nanoseconds/1e9

        if self.current_battery is None:
            if check_time - self.start_time > self.initial_timeout_time_sec:
                self.get_logger().warn(f"Fault detected: battery initial time out!")
                self.current_battery_status.fault = True
        else:
            self.current_battery_status.ready = True

            if self.current_battery.voltage < self.battery_min_voltage:
                self.get_logger().warn(f"Fault detected: Battery low voltage!")
                self.current_battery_status.fault = True

            if self.current_battery.percentage < self.battery_min_capacity:
                self.get_logger().warn(f"Fault detected: Battery low capacity!")
                self.current_battery_status.fault = True

            if (check_time - self.current_battery_time) > self.timeout_time_sec:
                self.get_logger().info(f"Fault detected: Leak time out!")
                self.current_battery_status.fault = True

        if self.verbose:
            self.get_logger().info(f"Battery: {self.current_battery_status}")

        return self.current_battery_status

    def output_callback(self):
        """
        Perform
        """

        self.leak_check()
        self.battery_check()
        # Self.monitor updates on it's own

        faults = [self.monitor.fault, self.current_leak_status.fault, self.current_battery_status.fault]
        readys = [self.monitor.ready, self.current_leak_status.ready, self.current_battery_status.ready]

        if True in faults:
            self.get_logger().warn(f"Fault detected [rate, leak, battery]: {faults}")
            fault_msg = Int8()
            fault_msg.data = SmarcTopics.VEHICLE_HEALTH_ERROR
            self.report_pub.publish(fault_msg)
        elif all(readys):
            ready_msg = Int8()
            ready_msg.data = SmarcTopics.VEHICLE_HEALTH_READY
            self.report_pub.publish(ready_msg)
        else:
            # Another check for initial timeing out
            current_time = self.get_clock().now().nanoseconds/1e9
            elapsed_time = current_time - self.start_time

            if self.verbose:
                self.get_logger().info(f"Waiting, Elapsed time: {elapsed_time}")

            if elapsed_time > self.initial_timeout_time_sec:
                fault_msg = Int8()
                fault_msg.data = SmarcTopics.VEHICLE_HEALTH_ERROR
                self.report_pub.publish(fault_msg)
            else:
                waiting_msg = Int8()
                waiting_msg.data = SmarcTopics.VEHICLE_HEALTH_WAITING
                self.report_pub.publish(waiting_msg)

    def log_all_parameters(self):
        param_names = self._parameters.keys()
        self.get_logger().info("Declared Parameters and their values:")
        for name in param_names:
            value = self.get_parameter(name).value
            self.get_logger().info(f"  {name}: {value}")

def main(args=None, namespace=None):
    rclpy.init(args=args)
    lolo_health_node = MonitorNode(namespace=namespace)
    try:
        rclpy.spin(lolo_health_node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    default_namespace = "lolo"
    main(namespace=default_namespace)
