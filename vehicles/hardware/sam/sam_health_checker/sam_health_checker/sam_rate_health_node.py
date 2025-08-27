import os
import yaml
from dataclasses import dataclass, field

import rclpy
from rclpy.node import Node
from ament_index_python import get_package_share_directory

# General messages
from sensor_msgs.msg import Imu
from std_msgs.msg import Int8, Float32, String
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

        # Limits
        self.declare_parameter("limits_filename", "sam_health_limits.yaml")
        self.limits_filename = self.get_parameter("limits_filename").value
        self.limits = self.read_limits()

        self.declare_parameter("output_rate", 1.0)
        self.output_rate = self.get_parameter("output_rate").value

        # Leak and battery parameters
        self.declare_parameter("leak_topic", SamTopics.LEAK_TOPIC)
        self.leak_topic = self.get_parameter("leak_topic").value

        self.declare_parameter("battery_topic", SamTopics.BATTERY_STATUS_TOPIC)
        self.battery_topic = self.get_parameter("battery_topic").value

        self.declare_parameter("battery_min_voltage", 20.0)
        self.battery_min_voltage = self.get_parameter("battery_min_voltage").value

        self.declare_parameter("battery_min_capacity", 0.25)
        self.battery_min_capacity = self.get_parameter("battery_min_capacity").value

        # Depth and Altitude parameters
        # The values from these topics are compared to the values read from limits
        self.declare_parameter("depth_topic", SmarcTopics.DEPTH_TOPIC)
        self.depth_topic = self.get_parameter("depth_topic").value

        self.declare_parameter("altitude_topic", SmarcTopics.ALTITUDE_TOPIC)
        self.altitude_topic = self.get_parameter("altitude_topic").value

        # Topic rate monitor parameters
        # time since start if no message is received
        self.declare_parameter("initial_timeout_time_sec", 30.0)
        self.initial_timeout_time_sec = self.get_parameter("initial_timeout_time_sec").value

        # time since last message was received
        self.declare_parameter("timeout_time_sec", 5.0)
        self.timeout_time_sec = self.get_parameter("timeout_time_sec").value

        self.declare_parameter("report_topic", SmarcTopics.VEHICLE_HEALTH_TOPIC)
        self.report_topic = self.get_parameter("report_topic").value

        self.declare_parameter('verbose', False)
        self.verbose = self.get_parameter("verbose").value
        if self.verbose:
            self.log_all_parameters()

        self.declare_parameter('testing', False)
        self.testing = self.get_parameter('testing').value

        # === Hardcoded topics, message types, and rates ===
        # Essential topics - Will trigger fault if no detected within initial timeout time
        self.essential_topics = {
            SamTopics.STIM_IMU_TOPIC: [Imu, 20.0]
        }

        # Optional topics - Will NOT trigger fault based on initial timeout time
        self.optional_topics = {
            SamTopics.DVL_TOPIC: [DVL, 1.0],
        }

        self.start_time = self.get_clock().now().nanoseconds/1e9

        self.current_leak = None
        self.current_leak_time = None
        self.current_leak_status = StatusReport(ready=True,fault=False)  # No waiting, messages only when a fault is detected
        self.current_battery = None
        self.current_battery_time = None
        self.current_battery_status = StatusReport()

        self.current_depth = None
        self.current_depth_time = None
        self.current_depth_status = StatusReport()
        self.current_altitude = None
        self.current_altitude_time = None
        self.current_altitude_status = StatusReport()

        self.fault_report = None
        self.fault_logged = False

        # === Set up subs, pubs, and timers ===
        self.leak_sub = self.create_subscription(msg_type=Leak,
                                                 topic=self.leak_topic,
                                                 callback=self.leak_callback,
                                                 qos_profile=10)

        self.battery_sub = self.create_subscription(msg_type=BatteryState,
                                                    topic=self.battery_topic,
                                                    callback=self.battery_callback,
                                                    qos_profile=10)

        self.depth_sub = self.create_subscription(msg_type=Float32,
                                                  topic=self.depth_topic,
                                                  callback=self.depth_callback,
                                                  qos_profile=10)

        self.altitude_sub = self.create_subscription(msg_type=Float32,
                                                     topic=self.altitude_topic,
                                                     callback=self.altitude_callback,
                                                     qos_profile=10)

        self.get_logger().info(f"topic rate monitor(s) instantiated")
        self.essential_monitor = TopicRateMonitor(self, self.essential_topics, timeout_time_sec=self.timeout_time_sec,
                                                  verbose=self.verbose)

        self.optional_monitor = TopicRateMonitor(self, self.optional_topics, timeout_time_sec=self.timeout_time_sec,
                                                 verbose=self.verbose)

        if self.testing:
            self.report_pub = self.create_publisher(msg_type=Int8, topic='health_testing', qos_profile=10)
        else:
            self.report_pub = self.create_publisher(msg_type=Int8, topic=self.report_topic, qos_profile=10)
        
        self.report_string_pub = self.create_publisher(msg_type=String, topic=f"{self.report_topic}/report", qos_profile=10)
        
        self.report_timer = self.create_timer(timer_period_sec=float(1.0 / self.output_rate),
                                              callback=self.output_callback)
        

    def leak_callback(self, msg):
        self.current_leak = msg
        self.current_leak_time = self.get_clock().now().nanoseconds/1e9

    def battery_callback(self, msg):
        self.current_battery = msg
        self.current_battery_time = self.get_clock().now().nanoseconds/1e9

    def depth_callback(self, msg):
        self.current_depth = msg
        self.current_depth_time = self.get_clock().now().nanoseconds / 1e9

    def altitude_callback(self, msg):
        self.current_altitude = msg
        self.current_altitude_time = self.get_clock().now().nanoseconds / 1e9

    def leak_check(self):
        if self.current_leak_status.fault:
            return self.current_leak_status
        
        if self.current_leak is None:
            return
        
        self.current_leak_status.ready = True

        if self.current_leak.value:
            current_fault_report = f"Fault detected: Leak!"
            if self.fault_report is None:
                self.fault_report = current_fault_report
            self.get_logger().warn(f"Fault detected: Leak!")
            self.current_leak_status.fault = True

        return self.current_leak_status

    def battery_check(self):
        
        # TODO the batter is not required to move into ready
        if self.current_battery_status.fault:
            return self.current_battery_status

        # check_time = self.get_clock().now().nanoseconds/1e9

        if self.current_battery is None:
            self.current_battery_status.ready = True
            return self.current_battery_status

        # Battery status received
        self.current_battery_status.ready = True

        if self.current_battery.voltage < self.battery_min_voltage:
            current_fault_report = f"Fault detected: Battery low voltage! Current voltage: {self.current_battery.voltage}, Min voltage: {self.battery_min_voltage}"
            if self.fault_report is None:
                self.fault_report = current_fault_report
            
            self.get_logger().warn(current_fault_report)
            self.current_battery_status.fault = True

        if self.current_battery.percentage < self.battery_min_capacity:
            current_fault_report = f"Fault detected: Battery low capacity! Current capacity: {self.current_battery.percentage}, Min capacity: {self.battery_min_capacity}"
            if self.fault_report is None:
                self.fault_report = current_fault_report
            self.get_logger().warn(self.fault_report)
            self.current_battery_status.fault = True

        # if (check_time - self.current_battery_time) > self.timeout_time_sec:
        #     self.get_logger().info(f"Fault detected: Leak time out!")
        #     self.current_battery_status.fault = True

        return self.current_battery_status

    def depth_check(self):

        if self.current_depth_status.fault:
            return self.current_depth_status

        check_time = self.get_clock().now().nanoseconds/1e9

        if self.current_depth is None:
            if self.check_initial_timeout(check_time):
                current_fault_report = f"Fault detected: depth initial time out!"
                if self.fault_report is None:
                    self.fault_report = current_fault_report
                self.get_logger().warn(current_fault_report)
                self.current_depth_status.fault = True
        else:
            self.current_depth_status.ready = True

            # Check that 'max_depth' is defined in limits
            if 'max_depth' not in self.limits:
                return self.current_depth_status

            if self.current_depth.data > self.limits['max_depth']:
               current_fault_report = f"Fault detected: Max depth exceeded! Current depth: {self.current_depth.data:.2f}, Max depth: {self.limits['max_depth']}"
               if self.fault_report is None:
                   self.fault_report = current_fault_report
               self.get_logger().warn(current_fault_report)
               self.current_depth_status.fault = True

            time_diff = check_time - self.current_depth_time
            if time_diff > self.timeout_time_sec:
                current_fault_report = f"Fault detected: depth time out! Time diff = {time_diff:.2f} s > {self.timeout_time_sec:.2f} s"
                if self.fault_report is None:
                    self.fault_report = current_fault_report
                self.get_logger().info(current_fault_report)
                self.current_depth_status.fault = True

        return self.current_depth_status

    def altitude_check(self):
        """
        REMOVED INITIAL
        """

        if self.current_altitude_status.fault:
            return self.current_altitude_status

        check_time = self.get_clock().now().nanoseconds/1e9

        if self.current_altitude is None:
            return self.current_altitude_status
        
        self.current_altitude_status.ready = True

        # Check that 'max_depth' is defined in limits
        if 'min_altitude' not in self.limits:
            return self.current_altitude_status
        
        if self.current_altitude.data == -1:
            return self.current_altitude_status

        if self.current_altitude.data < self.limits['min_altitude']:
            current_fault_report = f"Fault detected: low altitude! Current altitude: {self.current_altitude.data:.2f}, Min altitude: {self.limits['min_altitude']}"
            if self.fault_report is None:
                self.fault_report = current_fault_report
            self.get_logger().warn(current_fault_report)
            self.current_altitude_status.fault = True

        time_diff = check_time - self.current_altitude_time
        if time_diff > self.timeout_time_sec:
            current_fault_report = f"Fault detected: altitude time out! Time diff = {time_diff:.2f} s > {self.timeout_time_sec:.2f} s"
            if self.fault_report is None:
                self.fault_report = current_fault_report
            self.get_logger().info(current_fault_report)
            self.current_altitude_status.fault = True

        return self.current_altitude_status

    def output_callback(self):
        """
        Perform
        """

        self.leak_check()
        self.battery_check()
        self.altitude_check()
        self.depth_check()

        if self.verbose and not self.fault_logged:
            self.get_logger().info(f"Leak: {self.current_leak_status}")
            self.get_logger().info(f"Battery: {self.current_battery_status}")
            self.get_logger().info(f"Altitude: {self.current_altitude_status}")
            self.get_logger().info(f"Depth: {self.current_depth_status}")


        # Self.monitor updates on it's own

        faults = [
            self.essential_monitor.fault, self.optional_monitor.fault,
            self.current_leak_status.fault, self.current_battery_status.fault,
            self.current_altitude_status.fault, self.current_depth_status.fault
        ]

        # These are subject to the initial timeout
        readys = [
            self.essential_monitor.ready,
            self.current_leak_status.ready, self.current_battery_status.ready,
            # self.current_altitude_status.ready, self.current_depth_status.ready
        ]

        # These are not subject to the initial timeout
        optional_readys = [
            self.optional_monitor.ready,
            self.current_altitude_status.ready, self.current_depth_status.ready
        ]

        if True in faults:
            if not self.fault_logged:
                self.get_logger().warn(f"Fault detected [essential, optional, leak, battery, altitude, depth]: {faults}")
                self.fault_logged = True
            self.publish_fault()
            return
        
        elif all(readys) and all(optional_readys):
            ready_msg = Int8()
            ready_msg.data = SmarcTopics.VEHICLE_HEALTH_READY
            self.report_pub.publish(ready_msg)
        else:
            # Another check for initial timeing out
            current_time = self.get_clock().now().nanoseconds/1e9
            elapsed_time = current_time - self.start_time

            if self.verbose:
                self.get_logger().info(f"Waiting, Elapsed time: {elapsed_time}")

            if self.check_initial_timeout(current_time) and False in readys:
                self.publish_fault()
                return

            else:
                waiting_msg = Int8()
                waiting_msg.data = SmarcTopics.VEHICLE_HEALTH_WAITING
                self.report_pub.publish(waiting_msg)

    def publish_fault(self):

            fault_msg = Int8()
            fault_msg.data = SmarcTopics.VEHICLE_HEALTH_ERROR
            self.report_pub.publish(fault_msg)

            if self.fault_report is not None:
                fault_report_msg = String()
                fault_report_msg.data = str(self.fault_report)
                self.report_string_pub.publish(fault_report_msg)

    def read_limits(self):
        """
        Read YAML file with Lolo's limits.
        Returns a dictionary with the values.
        """
        if not self.limits_filename:
            self.limits_filename = "sam_health_limits.yaml"

        path_to_pkg = get_package_share_directory('sam_health_checker')
        yaml_path = os.path.join(path_to_pkg, "config", self.limits_filename)

        with open(yaml_path, 'r') as file:
            limits = yaml.safe_load(file)
        self.get_logger().info(f"SAM limits have been configured with filename {self.limits_filename}")
        [self.get_logger().info(f"{key}:{value}") for key, value in limits.items()]

        return limits

    def check_initial_timeout(self, time):
        if self.initial_timeout_time_sec < 0:
            return False

        if (time - self.start_time) > self.initial_timeout_time_sec:
            return True
        else:
            return False


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
