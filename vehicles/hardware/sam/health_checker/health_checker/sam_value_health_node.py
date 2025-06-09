#!/usr/bin/python

# General
import yaml
import math
import os
from dataclasses import dataclass

# ROS
import rclpy
from rclpy.node import Node
from rclpy import time
from ament_index_python import get_package_share_directory

# Messages
from std_msgs.msg import Bool, String, Int8, Empty
from lolo_msgs.msg import Pressures, Status, Temperatures
from ixblue_ins_msgs.msg import Ins

# SMaRC Topics
from lolo_msgs.msg import Topics as LoloTopics
from smarc_msgs.msg import Topics as SmarcTopics  # VEHICLE_HEALTH_READY, VEHICLE_HEALTH_WAITING, VEHICLE_HEALTH_ERROR

# from smarc_mission_msgs.msg import Topics as MissionTopics

try:
    from .helpers.ros_helpers import rcl_time_to_secs
except ImportError:
    from helpers.ros_helpers import rcl_time_to_secs


@dataclass
class StatusReport:
    ready: bool
    fault: bool


class HealthNode(Node):
    """
    This node will check health related topics and report overall status to the BT at a specified rate
    """

    # TODO - Currently only using the Pressures, Status, and Temperatures messages
    # TODO - Add the ability to monitor the update rate of sensors
    # TODO - Clean way of specifying desired values/ranges for certain values

    def __init__(self, namespace=None):
        super().__init__("health_node", namespace=namespace)
        self._log("Starting node defined in lolo_health_node.py")

        # Debugging mode
        self.debugging = True

        # # Desired values
        # # === Load desired values from YAML file
        # self.declare_parameter("config_file_name", None)
        # self.config_file_name = self.get_parameter("config_file_name").value
        #
        # if self.config_file_name is None:
        #     self._log("No config file set")
        #     raise ValueError("No config file set")
        #
        # self.config_file_path = os.path.join(get_package_share_directory('health_checker'),
        #                                      'config',
        #                                      self.config_file_name)
        #
        # if not os.path.isfile(self.config_file_path) or '.yaml' not in self.config_file_name:
        #     self._log("Invalid config file set")
        #     raise ValueError("Invalid config file set")
        #
        # # Load YAML
        # with open(self.config_file_path, 'r') as file:
        #     config_data = yaml.safe_load(file)

        # TODO - for now only indicated values will be checked, should there be a default?
        self.valid_pressure_values = {
            "usbl_isb": [250, 1500],
            "thrusters_isb": [250, 1500],
            "vertical_thrusters_isb": [250, 1500],
            "prevco_isb": [250, 1500],
            # "####_isb": [0, 1],
            "battery1_isb": [250, 1500],
            "battery2_isb": [250, 1500],
        }

        self.valid_status_values = {
            # "rc_signal"
            "voltage": [22, 40],
            # "current"
            "captain_leak": [0],
            "esc_leak": [0],
            "prevco_leak": [0],
            "edw_leak": [0],
            "battery1_leak": [0],
            "battery2_leak": [0],

            # ISB status
            "time_status": [1],
            "trigger_status": [1],
            "actuators_status": [1],
            "thrusters_status": [1],
            # "vertical_thrusters_status": [1],
            # "usbl_status": [1],
            # "scientist_status": [1],
            # "edw_status": [1],
            "battery1_status": [1],
            "battery2_status": [1]

            # Aux outputs
            # aux_output
            # servo1_output
            # servo2_output
            # lumen_output
            # mbes_output

            # string emergency_status
            # string control_mode
            # string control_source

            # int8 thrusters_enabled
            # int8 vertical_thrusters_enabled

            # int8 edw_armed
            # int8 edw_timer_armed
            # int32 edw_timer_time_left
        }


        # Temperatures are maybe a little cruder
        temperature_min = -271
        temperature_max = 80
        self.valid_temperature_values = {
            "captain_cpu": [],
            "time_cpu": [],
            "captain_top": [],
            "captain_eth": [],
            "captain_nuc": [],
            "usbl_isb": [],
            "actuator_cpu": [],
            "elevator_pcb": [],
            "elevator_motor": [],
            "rudder_motor": [],
            "rudder_pcb": [],
            "elevon_port_motor": [],
            "elevon_port_pcb": [],
            "elevon_strb_motor": [],
            "elevon_strb_pcb": [],
            "thruster_isb": [],
            "port_esc": [],
            'strb_esc': [],
            "vertical_thruster_isb": [],
            "vertical_thruster_1_esc": [],
            "vertical_thruster_2_esc": [],
            "vertical_thruster_3_esc": [],
            "vertical_thruster_4_esc": [],
            "prevco_isb": [],
            "edw_isb": [],
            "battery1_isb": [],
            "battery1_temp1": [],
            "battery1_temp2": [],
            "battery1_temp3": [],
            "battery1_temp4": [],
            "battery1_temp5": [],
            "battery2_isb": [],
            "battery2_temp1": [],
            "battery2_temp2": [],
            "battery2_temp3": [],
            "battery2_temp4": [],
            "battery2_temp5": [],
        }

        # Simple setting of valid temperature values
        for key in self.valid_temperature_values.keys():
            self.valid_temperature_values[key] = [temperature_min, temperature_max]

        # ===== Declare parameters =====
        # Default values set in declare_parameters()
        self.declare_node_parameters()

        # ===== Get parameters =====
        # Note: All parameters must be declared first! see self.declare_parameters
        # === Topics ===
        self.pressure_topic = self.get_parameter("pressure_topic").value
        self.status_topic = self.get_parameter("status_topic").value
        self.temperature_topic = self.get_parameter("temperature_topic").value

        # TODO - Consider monitoring these topics
        # self.leak_topic = self.get_parameter("leak_topic").value  # Not used
        # self.battery_1_topic = self.get_parameter("battery_1_topic").value  # Not used
        # self.battery_2_topic = self.get_parameter("battery_2_topic").value  # Not used

        # Output topics
        self.output_status_topic = self.get_parameter("output_status_topic").value
        self.output_abort_topic = self.get_parameter("output_abort_topic").value

        # ===== Data ====
        self.current_pressure = None
        self.current_pressure_time = None  # time of last received message
        self.current_status = None
        self.current_status_time = None  # time of last received message
        self.current_temperature = None
        self.current_temperature_time = None  # time of last received message

        # ===== Status =====
        self.status = SmarcTopics.VEHICLE_HEALTH_WAITING
        self.topics_status = False  # Indicates whether all the monitored topics have been received

        # ===== Behavior Parameters =====
        # self.verbose_setup = self.get_parameter("verbose_setup").value
        self.output_rate = self.get_parameter("output_rate").value

        # ===== Subscribers =====
        # self.ins_sub = self.create_subscription(msg_type=Ins,
        #                                         topic=self.input_ins_topic,
        #                                         callback=self.ins_callback,
        #                                         qos_profile=10)

        self.pressure_sub = self.create_subscription(msg_type=Pressures,
                                                     topic=self.pressure_topic,
                                                     callback=self.pressure_callback,
                                                     qos_profile=10)

        self.status_sub = self.create_subscription(msg_type=Status,
                                                   topic=self.status_topic,
                                                   callback=self.status_callback,
                                                   qos_profile=10)

        self.temperature_sub = self.create_subscription(msg_type=Temperatures,
                                                        topic=self.temperature_topic,
                                                        callback=self.temperature_callback,
                                                        qos_profile=10)

        # ===== Publishers =====
        # self.odom_pub = self.create_publisher(msg_type=Odometry,
        #                                       topic=self.output_odom_topic,
        #                                       qos_profile=10)

        self.status_pub = self.create_publisher(msg_type=Int8,
                                                topic=self.output_status_topic,
                                                qos_profile=10)

        self.abort_pub = self.create_publisher(msg_type=Empty,
                                               topic=self.output_abort_topic,
                                               qos_profile=10)

        # ===== Timers =====
        self.publisher_timer = self.create_timer(timer_period_sec=float(1.0 / self.output_rate),
                                                 callback=self.publisher_callback)

    def _log(self, message):
        self.get_logger().info(message)

    # Basic node set up
    def declare_node_parameters(self):
        # Declare all the default values for parameters
        # Example: self.declare_parameter("automatic_zone", False)
        # Topics to subscribe to...
        self.declare_parameter("pressure_topic", LoloTopics.EXTENDED_INTERNAL_PRESSURE_TOPIC)
        self.declare_parameter("status_topic", LoloTopics.EXTENDED_STATUS_TOPIC)
        self.declare_parameter("temperature_topic", LoloTopics.EXTENDED_INTERNAL_TEMPERATURE_TOPIC)

        # Topics to publish to
        # self.output_status_topic
        self.declare_parameter("output_status_topic", SmarcTopics.VEHICLE_HEALTH_TOPIC)
        self.declare_parameter("output_abort_topic", SmarcTopics.ABORT_TOPIC)

        # Parameters
        self.declare_parameter("output_rate", 1.0)  # Rate (Hz) at with status and abort will be published

    def pressure_callback(self, msg):
        if self.debugging and self.current_pressure is None:
            self._log("pressure_callback()")

        self.current_pressure = msg
        self.current_pressure_time = self.get_clock().now().nanoseconds / 1e9

    def status_callback(self, msg):
        if self.debugging and self.current_status is None:
            self._log("status_callback()")

        self.current_status = msg
        self.current_status_time = self.get_clock().now().nanoseconds / 1e9

    def temperature_callback(self, msg):
        if self.debugging and self.current_temperature is None:
            self._log("temperature_callback()")

        self.current_temperature = msg
        self.current_temperature_time = self.get_clock().now().nanoseconds / 1e9

    def checker(self, current_msg, current_msg_valid):
        """
        return StatusReport
        """

        status = StatusReport(ready=False, fault=False)

        if current_msg is None:
            return status
        else:
            status.ready = True

        for key, values in current_msg_valid.items():
            # if self.debugging:
            #     self._log(f"Key: {key} -- Values: {values}")
            msg_value = getattr(current_msg, key)
            if len(values) == 1:
                if msg_value != values[0]:
                    status.fault = True
                    if self.debugging:
                        self._log(f"Failure: {key} - {msg_value}")
                    break
            else:
                if not (values[0] <= msg_value <= values[1]):
                    status.fault = True
                    if self.debugging:
                        self._log(f"Failure: {key} - {msg_value}")
                    break

        return status

    def check_pressure(self):
        """
        return StatusReport
        """
        return self.checker(self.current_pressure, self.valid_pressure_values)

    def check_status(self):
        """
        return StatusReport
        """
        return self.checker(self.current_status, self.valid_status_values)

    def check_temperature(self):
        """
        return StatusReport
        """
        return self.checker(self.current_temperature, self.valid_temperature_values)

    def publisher_callback(self):
        """
        Do all the checking here
        """

        # self._log("DEBUG: publisher_callback")

        # Once fault is detected, node will latch in that state and require a reset
        if self.status == SmarcTopics.VEHICLE_HEALTH_ERROR:
            # Publish Error status
            msg = Int8()
            msg.data = self.status
            self.status_pub.publish(msg)

            self.abort_pub.publish(Empty())
            return

        # Perform Checks
        pressure_check = self.check_pressure()
        status_check = self.check_status()
        temperature_check = self.check_temperature()

        if self.debugging:
            self._log("publisher_callback()")
            self._log(f"Pressure: {pressure_check}")
            self._log(f"Status: {status_check}")
            self._log(f"Temperature: {temperature_check}")

        ready_check = all([pressure_check.ready, status_check.ready, temperature_check.ready])
        fault_check = True in [pressure_check.fault, status_check.fault, temperature_check.fault]

        # Determine current state
        # Fault will only trigger once all topics have been detected
        # TODO - Is this really what we want??!
        if fault_check and ready_check:
            # Fault Condition
            self.status = SmarcTopics.VEHICLE_HEALTH_ERROR
        elif ready_check:
            # Ready Condition
            self.status = SmarcTopics.VEHICLE_HEALTH_READY
        else:
            self.status = SmarcTopics.VEHICLE_HEALTH_WAITING

        # Publish status
        msg = Int8()
        msg.data = self.status
        self.status_pub.publish(msg)

        # Publish abort if error is detected
        if self.status == SmarcTopics.VEHICLE_HEALTH_ERROR:
            self.abort_pub.publish(Empty())


def main(args=None, namespace=None):
    rclpy.init(args=args)
    node = HealthNode(namespace=namespace)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down")
        rclpy.shutdown()


if __name__ == "__main__":
    default_namespace = "lolo"
    main(namespace=default_namespace)
