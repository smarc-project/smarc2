#!/usr/bin/env python3
"""FloatSam vehicle health checker.

Implements a DJI-like health state flow adapted to FloatSam:
- WAITING by default until required readiness signals are available.
- READY when readiness checks pass.
- ERROR when applicable runtime safety limits are violated.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int8
from std_msgs.msg import Float32
from std_msgs.msg import Bool
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from sensor_msgs.msg import NavSatFix
from smarc_msgs.msg import Topics as SmarcTopics


class FloatsamHealthChecker(Node):
    def __init__(self):
        super().__init__("floatsam_health_checker")

        self.declare_parameter("robot_name", "floatsam_usv")
        self.declare_parameter("check_rate_hz", 1.0)
        self.declare_parameter("stale_timeout_sec", 5.0)
        self.declare_parameter("ready_battery_percent", 25.0)
        self.declare_parameter("error_battery_percent", 15.0)
        self.declare_parameter("thruster_active_rpm", 100.0)

        self.robot_name = str(self.get_parameter("robot_name").value)
        self.check_rate_hz = float(self.get_parameter("check_rate_hz").value)
        self.stale_timeout_sec = float(self.get_parameter("stale_timeout_sec").value)
        self.ready_battery_percent = float(self.get_parameter("ready_battery_percent").value)
        self.error_battery_percent = float(self.get_parameter("error_battery_percent").value)
        self.thruster_active_rpm = float(self.get_parameter("thruster_active_rpm").value)

        if self.check_rate_hz <= 0.0:
            self.get_logger().warn("check_rate_hz must be > 0. Falling back to 1.0")
            self.check_rate_hz = 1.0

        # Required readiness signals (DJI-like: must exist and be fresh before READY).
        self.topic_odom = f"/{self.robot_name}/smarc/odom"
        self.topic_imu = f"/{self.robot_name}/core/imu"
        self.topic_gps = f"/{self.robot_name}/core/gps_left"
        self.topic_depth = f"/{self.robot_name}/smarc/depth"
        self.topic_battery = f"/{self.robot_name}/smarc/battery_percent"
        self.topic_leak = f"/{self.robot_name}/core/leak"
        self.topic_thruster_port = f"/{self.robot_name}/actuators/thruster_port_cmd"
        self.topic_thruster_strb = f"/{self.robot_name}/actuators/thruster_strb_cmd"

        self.last_odom_time = None
        self.last_imu_time = None
        self.last_gps_time = None
        self.last_depth_time = None
        self.last_battery_time = None
        self.last_leak_time = None
        self.last_thruster_port_time = None
        self.last_thruster_strb_time = None

        self.battery_percent = None
        self.leak_detected = False
        self.thruster_port_rpm = 0.0
        self.thruster_strb_rpm = 0.0

        self.create_subscription(Odometry, self.topic_odom, self._odom_cb, 10)
        self.create_subscription(Imu, self.topic_imu, self._imu_cb, 10)
        self.create_subscription(NavSatFix, self.topic_gps, self._gps_cb, 10)
        self.create_subscription(Float32, self.topic_depth, self._depth_cb, 10)
        self.create_subscription(Float32, self.topic_battery, self._battery_cb, 10)
        self.create_subscription(Bool, self.topic_leak, self._leak_cb, 10)
        self.create_subscription(Float32, self.topic_thruster_port, self._thruster_port_cb, 10)
        self.create_subscription(Float32, self.topic_thruster_strb, self._thruster_strb_cb, 10)

        self.health_topic = f"/{self.robot_name}/{SmarcTopics.VEHICLE_HEALTH_TOPIC}"
        self.health_pub = self.create_publisher(Int8, self.health_topic, 10)

        self.timer = self.create_timer(1.0 / self.check_rate_hz, self._publish_health)

        self.get_logger().info(
            f"FloatSam health checker started. Publishing on {self.health_topic}. "
            f"Required topics: {[self.topic_odom, self.topic_imu, self.topic_gps, self.topic_depth, self.topic_battery]}"
        )

    def time_now(self) -> float:
        return self.get_clock().now().nanoseconds * 1e-9

    def _odom_cb(self, _msg: Odometry):
        self.last_odom_time = self.time_now()

    def _imu_cb(self, _msg: Imu):
        self.last_imu_time = self.time_now()

    def _gps_cb(self, _msg: NavSatFix):
        self.last_gps_time = self.time_now()

    def _depth_cb(self, _msg: Float32):
        self.last_depth_time = self.time_now()

    def _battery_cb(self, msg: Float32):
        self.last_battery_time = self.time_now()
        self.battery_percent = self._normalize_battery_percent(msg.data)

    def _leak_cb(self, msg: Bool):
        self.last_leak_time = self.time_now()
        self.leak_detected = bool(msg.data)

    def _thruster_port_cb(self, msg: Float32):
        self.last_thruster_port_time = self.time_now()
        self.thruster_port_rpm = float(msg.data)

    def _thruster_strb_cb(self, msg: Float32):
        self.last_thruster_strb_time = self.time_now()
        self.thruster_strb_rpm = float(msg.data)

    def _normalize_battery_percent(self, value: float) -> float:
        # Accept either [0,1] or [0,100] inputs.
        return value * 100.0 if 0.0 <= value <= 1.0 else value

    def _is_fresh(self, timestamp: float | None, now: float) -> bool:
        return timestamp is not None and (now - timestamp) <= self.stale_timeout_sec

    def _publish_health(self):
        now = self.time_now()

        msg = Int8()

        # DJI-like default state.
        msg.data = SmarcTopics.VEHICLE_HEALTH_WAITING

        # Readiness checks that must pass before READY.
        odom_ok = self._is_fresh(self.last_odom_time, now)
        imu_ok = self._is_fresh(self.last_imu_time, now)
        gps_ok = self._is_fresh(self.last_gps_time, now)
        depth_ok = self._is_fresh(self.last_depth_time, now)
        battery_ok = (
            self._is_fresh(self.last_battery_time, now)
            and self.battery_percent is not None
            and self.battery_percent > self.ready_battery_percent
        )

        if all([odom_ok, imu_ok, gps_ok, depth_ok, battery_ok]):
            msg.data = SmarcTopics.VEHICLE_HEALTH_READY

        # Runtime safety escalation to ERROR (applicable FloatSam checks).
        thrusters_active = (
            abs(self.thruster_port_rpm) > self.thruster_active_rpm
            or abs(self.thruster_strb_rpm) > self.thruster_active_rpm
        )

        battery_error = (
            self.battery_percent is not None
            and self.battery_percent < self.error_battery_percent
        )
        leak_error = self._is_fresh(self.last_leak_time, now) and self.leak_detected

        if leak_error or (thrusters_active and battery_error):
            msg.data = SmarcTopics.VEHICLE_HEALTH_ERROR
            if battery_error:
                self.get_logger().warn(
                    f"Health ERROR: battery below limit {self.battery_percent:.2f}% < {self.error_battery_percent:.2f}%",
                    throttle_duration_sec=2.0,
                )
            if leak_error:
                self.get_logger().warn("Health ERROR: leak detected", throttle_duration_sec=2.0)

        self.health_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = FloatsamHealthChecker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
