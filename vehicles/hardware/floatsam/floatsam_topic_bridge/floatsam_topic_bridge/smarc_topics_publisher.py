#!/usr/bin/env python3
"""
SMaRC Topics Publisher Node for Floatsam
Converts simulator or real hardware topics to standard SMaRC topics
"""

import rclpy
from rclpy.node import Node
import math
import importlib
from septentrio_gnss_driver.msg import AttEuler
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy

from px4_msgs.msg import OffboardControlMode, VehicleControlMode, VehicleThrustSetpoint, VehicleTorqueSetpoint, SensorGps

# ROS message types
from sensor_msgs.msg import NavSatFix, Imu, FluidPressure, Range, Image, PointCloud2
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32, Bool
from geographic_msgs.msg import GeoPoint
from tf_transformations import euler_from_quaternion
from tf2_ros import TransformBroadcaster, StaticTransformBroadcaster, Buffer, TransformListener
from geometry_msgs.msg import TransformStamped
from smarc_utilities.georef_utils import convert_latlon_to_utm


class SmarcTopicsPublisher(Node):
    """
    Bridge node that converts Floatsam-specific topics (sim or real) to standard SMaRC topics.
    Topic configurations are loaded automatically via ROS 2 parameters from a YAML file.
    Topic namespacing is handled externally by PushRosNamespace in the launch file.
    """
    
    def __init__(self):
        # Tell ROS 2 to automatically accept all parameters passed from the YAML file
        super().__init__(
            'floatsam_smarc_topics_publisher',
            allow_undeclared_parameters=True,
            automatically_declare_parameters_from_overrides=True
        )

        self.robot_name = self.get_parameter("robot_name").get_parameter_value().string_value
        self.use_sim = self.get_parameter("use_sim").get_parameter_value().bool_value
        self.thruster_limit = self.get_parameter("thruster_limit").get_parameter_value().double_value
        self.master_robot_name = self.get_parameter('master_floatsam').get_parameter_value().string_value

        if self.thruster_limit <= 0.0:
            self.get_logger().warn('Parameter thruster_limit must be > 0. Falling back to 1000.0 RPM')
            self.thruster_limit = 1000.0

        # --- DYNAMIC QoS AND CONFIG SETUP ---
        if self.use_sim:
            self.px4_qos = 10
            self.actuator_qos = 10
            self.get_logger().info('SIMULATION MODE: Using standard QoS (10)')
        else:
            self.px4_qos = QoSProfile(
                reliability=QoSReliabilityPolicy.BEST_EFFORT,
                durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
                history=QoSHistoryPolicy.KEEP_LAST,
                depth=1
            )
            self.actuator_qos = QoSProfile(
                reliability=QoSReliabilityPolicy.BEST_EFFORT,
                durability=QoSDurabilityPolicy.VOLATILE,
                history=QoSHistoryPolicy.KEEP_LAST,
                depth=1
            )
            self.get_logger().info('REAL HARDWARE MODE: Using PX4 Best-Effort QoS')

        # Reconstruct the configuration dictionaries directly from ROS 2 parameters
        self.config = {
            'sensors': self._get_nested_params('sensors'),
            'actuators': self._get_nested_params('actuators'),
            'payload': self._get_nested_params('payload')
        }

        # Storage for latest messages
        self.latest_odom = None
        self.latest_gps_left = None
        self.latest_gps_right = None
        self.latest_rtk_position = None
        self.is_receiving_rtk_heading = False
        self.latest_rtk_heading_rad = float('nan')

        self.latest_port_cmd = 0.0
        self.latest_strb_cmd = 0.0
        self.last_cmd_time = self.get_clock().now()
        self.is_offboard = False

        self._actuator_motors_cls = None

        # Relative topics — PushRosNamespace will prepend robot_name automatically
        self.heading_pub = self.create_publisher(Float32, 'smarc/heading', 10)
        self.course_pub  = self.create_publisher(Float32, 'smarc/course', 10)
        self.speed_pub   = self.create_publisher(Float32, 'smarc/speed', 10)
        self.latlon_pub  = self.create_publisher(GeoPoint, 'smarc/latlon', 10)

        # Create subscribers and publishers from YAML config
        self._setup_topic_bridges()

        # PX4 topics: absolute paths prefixed with robot_name to isolate per-robot
        self.offboard_mode_pub = self.create_publisher(
            OffboardControlMode,
            f'fmu/in/offboard_control_mode',
            self.actuator_qos
        )
        self.create_subscription(
            VehicleControlMode,
            f'fmu/out/vehicle_control_mode',
            self._control_mode_callback,
            self.px4_qos
        )

        # --- Auto-Datum Variables ---
        self.datum_is_set = False
        self.datum_utm_x = 0.0
        self.datum_utm_y = 0.0
        self.datum_zone = "utm"

        # Multi-agent variables
        self.local_map_offset_x = 0.0
        self.local_map_offset_y = 0.0
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # TF Broadcasters
        self.tf_broadcaster = TransformBroadcaster(self)
        self.static_tf_broadcaster = StaticTransformBroadcaster(self)

        self.get_logger().info(f'Floatsam SMaRC Topics Publisher started for: {self.robot_name}')
        self.control_loop_timer = self.create_timer(0.1, self._control_loop_callback)

    def _get_nested_params(self, prefix):
        result = {}
        # get_parameters_by_prefix returns a dict of relative keys and their Parameter objects
        params = self.get_parameters_by_prefix(prefix)
        for key, param in params.items():
            parts = key.split('.')
            current_level = result
            for part in parts[:-1]:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
            current_level[parts[-1]] = param.value
        return result

    def _get_message_class(self, msg_type_str):
        """Dynamically import and return message class from string like 'std_msgs/Float32'"""
        try:
            pkg, msg = msg_type_str.split('/')
            module = importlib.import_module(f'{pkg}.msg')
            return getattr(module, msg)
        except Exception as e:
            self.get_logger().error(f'Failed to import message type {msg_type_str}: {e}')
            return None

    def _create_passthrough_callback(self, publisher):
        """Create a generic passthrough callback"""
        def callback(msg):
            publisher.publish(msg)
        return callback

    def _setup_topic_bridges(self):
        """Set up subscribers and publishers for all configured topics.
        Output topics are relative — PushRosNamespace handles the robot prefix."""
        sensors  = self.config.get('sensors', {})
        actuators = self.config.get('actuators', {})
        payload  = self.config.get('payload', {})

        # GPS sensors (dual)
        if 'gps_left' in sensors:
            msg_class = self._get_message_class(sensors['gps_left']['msg_type'])
            self.create_subscription(msg_class, sensors['gps_left']['input_topic'],
                                     self._gps_left_callback, self.px4_qos)
            self.gps_left_pub = self.create_publisher(NavSatFix, sensors['gps_left']['output_topic'], 10)

        if 'gps_right' in sensors:
            msg_class = self._get_message_class(sensors['gps_right']['msg_type'])
            self.create_subscription(msg_class, sensors['gps_right']['input_topic'],
                                     self._gps_right_callback, self.px4_qos)
            self.gps_right_pub = self.create_publisher(NavSatFix, sensors['gps_right']['output_topic'], 10)
            self.get_logger().info(f'  GPS Right: {sensors["gps_right"]["input_topic"]} → {sensors["gps_right"]["output_topic"]}')

        # RTK GPS (high precision)
        if 'rtk_heading' in sensors:
            msg_class = self._get_message_class(sensors['rtk_heading']['msg_type'])
            if msg_class is None:
                msg_class = AttEuler
            if msg_class is not None:
                self.create_subscription(msg_class, sensors['rtk_heading']['input_topic'],
                                         self._rtk_heading_callback, 10)
                self.rtk_heading_pub = self.create_publisher(Float32, sensors['rtk_heading']['output_topic'], 10)
                self.get_logger().info(f'  RTK Heading: {sensors["rtk_heading"]["input_topic"]} → {sensors["rtk_heading"]["output_topic"]}')
            else:
                self.get_logger().error("Could not load AttEuler message class. Is septentrio_gnss_driver sourced?")

        if 'rtk_position' in sensors:
            msg_class = self._get_message_class(sensors['rtk_position']['msg_type'])
            self.create_subscription(msg_class, sensors['rtk_position']['input_topic'],
                                     self._rtk_position_callback, 10)
            self.rtk_position_pub = self.create_publisher(NavSatFix, sensors['rtk_position']['output_topic'], 10)
            self.get_logger().info(f'  RTK Position: {sensors["rtk_position"]["input_topic"]} → {sensors["rtk_position"]["output_topic"]}')

            # PX4 RTK injection — always absolute, always robot-scoped
            px4_rtk_topic = sensors['rtk_position'].get('output_for_px4', None)
            if not self.use_sim and px4_rtk_topic:
                self.sensor_gps_pub = self.create_publisher(SensorGps, px4_rtk_topic, self.px4_qos)
                self.get_logger().info(f'  RTK: Injection to {px4_rtk_topic} ENABLED')

        # IMU
        if 'imu' in sensors:
            msg_class = self._get_message_class(sensors['imu']['msg_type'])
            self.create_subscription(msg_class, sensors['imu']['input_topic'], self._imu_callback, self.px4_qos)
            self.imu_pub = self.create_publisher(Imu, sensors['imu']['output_topic'], 10)
            self.get_logger().info(f'  IMU: {sensors["imu"]["input_topic"]} → {sensors["imu"]["output_topic"]}')

        # Depth Pressure
        if 'depth_pressure' in sensors:
            msg_class = self._get_message_class(sensors['depth_pressure']['msg_type'])
            self.create_subscription(msg_class, sensors['depth_pressure']['input_topic'],
                                     self._depth_callback, self.px4_qos)
            self.depth_pub = self.create_publisher(Float32, sensors['depth_pressure']['output_topic'], 10)
            self.get_logger().info(f'  Depth: {sensors["depth_pressure"]["input_topic"]} → {sensors["depth_pressure"]["output_topic"]}')

        # DVL
        if 'dvl' in sensors:
            msg_class = self._get_message_class(sensors['dvl']['msg_type'])
            self.create_subscription(msg_class, sensors['dvl']['input_topic'], self._dvl_callback, self.px4_qos)
            self.dvl_pub = self.create_publisher(Range, sensors['dvl']['output_topic'], 10)
            self.get_logger().info(f'  DVL: {sensors["dvl"]["input_topic"]} → {sensors["dvl"]["output_topic"]}')

        # Leak sensor
        if 'leak' in sensors:
            msg_class = self._get_message_class(sensors['leak']['msg_type'])
            self.create_subscription(msg_class, sensors['leak']['input_topic'], self._leak_callback, self.px4_qos)
            self.leak_pub = self.create_publisher(msg_class, sensors['leak']['output_topic'], 10)
            self.get_logger().info(f'  Leak: {sensors["leak"]["input_topic"]} → {sensors["leak"]["output_topic"]}')

        # Odometry
        if 'odom_gt' in sensors:
            odom_config = sensors['odom_gt']
        elif 'odom' in sensors:
            odom_config = sensors['odom']
        else:
            odom_config = None

        if odom_config:
            msg_class = self._get_message_class(odom_config['msg_type'])
            self.create_subscription(msg_class, odom_config['input_topic'], self._odom_callback, self.px4_qos)
            self.odom_pub = self.create_publisher(Odometry, odom_config['output_topic'], 10)
            self.get_logger().info(f'  Odom: {odom_config["input_topic"]} → {odom_config["output_topic"]}')
            self.get_logger().info(f'  ↳ Also computing heading, course, speed, and latlon from best GPS')

        # Battery
        if 'battery' in sensors:
            msg_class = self._get_message_class(sensors['battery']['msg_type'])
            self.create_subscription(msg_class, sensors['battery']['input_topic'],
                                     self._battery_callback, self.px4_qos)
            self.battery_pub = self.create_publisher(Float32, sensors['battery']['output_topic'], 10)
            self.get_logger().info(f'  Battery: {sensors["battery"]["input_topic"]} → {sensors["battery"]["output_topic"]}')

        # Actuators
        if 'thruster_port_cmd' in actuators and 'thruster_strb_cmd' in actuators:
            self.create_subscription(Float32, actuators['thruster_port_cmd']['input_topic'],
                                     self._port_cmd_callback, 10)
            self.create_subscription(Float32, actuators['thruster_strb_cmd']['input_topic'],
                                     self._strb_cmd_callback, 10)

            if self.use_sim:
                self.sim_port_pub = self.create_publisher(Float32, actuators['thruster_port_cmd']['output_topic'], 10)
                self.sim_strb_pub = self.create_publisher(Float32, actuators['thruster_strb_cmd']['output_topic'], 10)
                self.get_logger().info('  Actuators: Bridged as DECOUPLED (Sim Mode)')
            else:
                self._actuator_motors_cls = self._get_message_class(actuators['px4_motors']['msg_type'])
                self.px4_motors_pub = self.create_publisher(
                    self._actuator_motors_cls,
                    actuators['px4_motors']['output_topic'],
                    self.actuator_qos
                )
                self.get_logger().info('  Actuators: Bridged as COUPLED (PX4 Mode)')

        # Payload (passthrough)
        for payload_name, config in payload.items():
            msg_class = self._get_message_class(config['msg_type'])
            if msg_class:
                pub = self.create_publisher(msg_class, config['output_topic'], self.px4_qos)
                self.create_subscription(msg_class, config['input_topic'],
                                         self._create_passthrough_callback(pub), 10)
                self.get_logger().info(f'  Payload {payload_name}: {config["input_topic"]} → {config["output_topic"]}')

    def _port_cmd_callback(self, msg: Float32):
        raw = msg.data / self.thruster_limit
        self.latest_port_cmd = max(-1.0, min(1.0, raw))
        self.last_cmd_time = self.get_clock().now()

    def _strb_cmd_callback(self, msg: Float32):
        raw = msg.data / self.thruster_limit
        self.latest_strb_cmd = max(-1.0, min(1.0, raw))
        self.last_cmd_time = self.get_clock().now()

    def _publish_actuators(self):
        """Applies safety timeouts and yields to Manual RC"""
        dt = (self.get_clock().now() - self.last_cmd_time).nanoseconds / 1e9
        if dt > 0.5:
            self.latest_port_cmd = 0.0
            self.latest_strb_cmd = 0.0

        if self.use_sim:
            port_msg = Float32()
            port_msg.data = self.latest_port_cmd * self.thruster_limit
            strb_msg = Float32()
            strb_msg.data = self.latest_strb_cmd * self.thruster_limit
            self.sim_port_pub.publish(port_msg)
            self.sim_strb_pub.publish(strb_msg)
        else:
            if not self.is_offboard:
                return

            now_us = self.get_clock().now().nanoseconds // 1000
            px4_msg = self._actuator_motors_cls()
            px4_msg.timestamp = now_us
            px4_msg.timestamp_sample = now_us
            px4_msg.control = [float('nan')] * 12
            px4_msg.control[0] = float(self.latest_strb_cmd)
            px4_msg.control[1] = float(self.latest_port_cmd)
            px4_msg.reversible_flags = 0b00000011
            self.px4_motors_pub.publish(px4_msg)

    def _control_loop_callback(self):
        """Runs at 10Hz. Publishes the heartbeat and current motor commands continuously."""
        msg = OffboardControlMode()
        msg.timestamp = self.get_clock().now().nanoseconds // 1000
        msg.position = False
        msg.velocity = False
        msg.acceleration = False
        msg.attitude = False
        msg.body_rate = False
        msg.thrust_and_torque = False
        msg.direct_actuator = True
        self.offboard_mode_pub.publish(msg)
        self._publish_actuators()

    def _gps_left_callback(self, msg):
        if self.use_sim:
            std_msg = msg
        else:
            std_msg = NavSatFix()
            std_msg.latitude  = msg.lat / 1e7
            std_msg.longitude = msg.lon / 1e7
            std_msg.altitude  = msg.alt / 1000.0
        self.latest_gps_left = std_msg
        self.gps_left_pub.publish(std_msg)
        self._publish_best_gps()

    def _gps_right_callback(self, msg):
        if self.use_sim:
            std_msg = msg
        else:
            std_msg = NavSatFix()
            std_msg.latitude  = msg.lat / 1e7
            std_msg.longitude = msg.lon / 1e7
            std_msg.altitude  = msg.alt / 1000.0
        self.latest_gps_right = std_msg
        self.gps_right_pub.publish(std_msg)
        self._publish_best_gps()

    def _control_mode_callback(self, msg):
        self.is_offboard = msg.flag_control_offboard_enabled

    def _rtk_heading_callback(self, msg):
        if math.isnan(msg.heading):
            return
        self.is_receiving_rtk_heading = True
        heading_rad = math.radians(msg.heading)
        self.latest_rtk_heading_rad = math.atan2(math.sin(heading_rad), math.cos(heading_rad))
        heading_msg = Float32()
        heading_msg.data = float(msg.heading)
        self.heading_pub.publish(heading_msg)

    def _rtk_position_callback(self, msg: NavSatFix):
        self.latest_rtk_position = msg
        self.rtk_position_pub.publish(msg)
        self._publish_best_gps()

        if not self.use_sim and hasattr(self, 'sensor_gps_pub'):
            px4_gps = SensorGps()
            now_us = self.get_clock().now().nanoseconds // 1000
            px4_gps.timestamp = now_us
            px4_gps.timestamp_sample = now_us
            px4_gps.latitude_deg = float(msg.latitude)
            px4_gps.longitude_deg = float(msg.longitude)
            px4_gps.altitude_msl_m = float(msg.altitude)
            px4_gps.altitude_ellipsoid_m = float(msg.altitude)
            px4_gps.fix_type = 6

            if len(msg.position_covariance) == 9 and msg.position_covariance[0] > 0:
                px4_gps.eph = float(math.sqrt(msg.position_covariance[0]))
            else:
                px4_gps.eph = 0.1

            if len(msg.position_covariance) == 9 and msg.position_covariance[8] > 0:
                px4_gps.epv = float(math.sqrt(msg.position_covariance[8]))
            else:
                px4_gps.epv = 0.2

            px4_gps.heading = self.latest_rtk_heading_rad
            px4_gps.satellites_used = 12
            px4_gps.vel_n_m_s = 0.0
            px4_gps.vel_e_m_s = 0.0
            px4_gps.vel_d_m_s = 0.0
            px4_gps.vel_ned_valid = False
            self.sensor_gps_pub.publish(px4_gps)

    def _publish_best_gps(self):
        """Publish best available GPS and set the Multi-Agent Auto-Datum on first fix"""
        best_position = self.latest_rtk_position or self.latest_gps_left or self.latest_gps_right
        if not best_position:
            return

        geopoint = GeoPoint()
        geopoint.latitude  = best_position.latitude
        geopoint.longitude = best_position.longitude
        geopoint.altitude  = best_position.altitude
        self.latlon_pub.publish(geopoint)

        if not self.datum_is_set and not self.use_sim:
            try:
                utm_point = convert_latlon_to_utm(geopoint)
                self.datum_zone = utm_point.header.frame_id

                if self.robot_name == self.master_robot_name:
                    self.datum_utm_x = utm_point.point.x
                    self.datum_utm_y = utm_point.point.y
                    self.datum_is_set = True
                    self._publish_static_transforms()
                    self.get_logger().info(f"MASTER MAP ORIGIN LOCKED. Zone: {self.datum_zone} | X: {self.datum_utm_x:.2f} | Y: {self.datum_utm_y:.2f}")
                else:
                    try:
                        tf = self.tf_buffer.lookup_transform(self.datum_zone, "map", rclpy.time.Time())
                        master_utm_x = tf.transform.translation.x
                        master_utm_y = tf.transform.translation.y
                        self.local_map_offset_x = utm_point.point.x - master_utm_x
                        self.local_map_offset_y = utm_point.point.y - master_utm_y
                        self.datum_is_set = True
                        self._publish_static_transforms()
                        self.get_logger().info(f"SLAVE MAP LOCKED! Offset from Master -> X: {self.local_map_offset_x:.2f}m | Y: {self.local_map_offset_y:.2f}m")
                    except Exception:
                        self.get_logger().info(f"Waiting for Master ({self.master_robot_name}) to publish global map...", throttle_duration_sec=2.0)
                        return
            except Exception as e:
                self.get_logger().error(f"Failed to set auto-datum: {e}")

    def _publish_static_transforms(self):
        """Creates the permanent links for the shared multi-agent map"""
        transforms_to_publish = []

        if self.robot_name == self.master_robot_name:
            t_utm = TransformStamped()
            t_utm.header.stamp = self.get_clock().now().to_msg()
            t_utm.header.frame_id = self.datum_zone
            t_utm.child_frame_id = "map"
            t_utm.transform.translation.x = float(self.datum_utm_x)
            t_utm.transform.translation.y = float(self.datum_utm_y)
            t_utm.transform.translation.z = 0.0
            t_utm.transform.rotation.w = 1.0
            transforms_to_publish.append(t_utm)

        t_global = TransformStamped()
        t_global.header.stamp = self.get_clock().now().to_msg()
        t_global.header.frame_id = "map"
        t_global.child_frame_id = f"{self.robot_name}/map"
        t_global.transform.translation.x = float(self.local_map_offset_x)
        t_global.transform.translation.y = float(self.local_map_offset_y)
        t_global.transform.translation.z = 0.0
        t_global.transform.rotation.w = 1.0
        transforms_to_publish.append(t_global)

        t_local = TransformStamped()
        t_local.header.stamp = self.get_clock().now().to_msg()
        t_local.header.frame_id = f"{self.robot_name}/map"
        t_local.child_frame_id = f"{self.robot_name}/odom"
        t_local.transform.translation.x = 0.0
        t_local.transform.translation.y = 0.0
        t_local.transform.translation.z = 0.0
        t_local.transform.rotation.w = 1.0
        transforms_to_publish.append(t_local)

        self.static_tf_broadcaster.sendTransform(transforms_to_publish)

    def _imu_callback(self, msg):
        if self.use_sim:
            std_msg = msg
        else:
            std_msg = Imu()
            std_msg.angular_velocity.x = float(msg.gyro_rad[0])
            std_msg.angular_velocity.y = float(msg.gyro_rad[1])
            std_msg.angular_velocity.z = float(msg.gyro_rad[2])
            std_msg.linear_acceleration.x = float(msg.accelerometer_m_s2[0])
            std_msg.linear_acceleration.y = float(msg.accelerometer_m_s2[1])
            std_msg.linear_acceleration.z = float(msg.accelerometer_m_s2[2])
        self.imu_pub.publish(std_msg)

    def _depth_callback(self, msg: FluidPressure):
        atmospheric_pressure = 101325.0
        water_pressure_per_meter = 10000.0
        depth_m = (msg.fluid_pressure - atmospheric_pressure) / water_pressure_per_meter
        depth_msg = Float32()
        depth_msg.data = depth_m
        self.depth_pub.publish(depth_msg)

    def _dvl_callback(self, msg: Range):
        self.dvl_pub.publish(msg)

    def _leak_callback(self, msg: Bool):
        self.leak_pub.publish(msg)
        if msg.data:
            self.get_logger().warn('  LEAK DETECTED!')

    def _odom_callback(self, msg):
        if self.use_sim:
            std_msg = msg
        else:
            std_msg = Odometry()
            std_msg.header.stamp = self.get_clock().now().to_msg()
            std_msg.header.frame_id = f"{self.robot_name}/odom"
            std_msg.child_frame_id = f"{self.robot_name}/base_link"
            std_msg.pose.pose.position.x = float(msg.position[0])
            std_msg.pose.pose.position.y = float(msg.position[1])
            std_msg.pose.pose.position.z = float(msg.position[2])
            std_msg.pose.pose.orientation.w = float(msg.q[0])
            std_msg.pose.pose.orientation.x = float(msg.q[1])
            std_msg.pose.pose.orientation.y = float(msg.q[2])
            std_msg.pose.pose.orientation.z = float(msg.q[3])
            std_msg.twist.twist.linear.x = float(msg.velocity[0])
            std_msg.twist.twist.linear.y = float(msg.velocity[1])
            std_msg.twist.twist.linear.z = float(msg.velocity[2])

            t = TransformStamped()
            t.header.stamp = std_msg.header.stamp
            t.header.frame_id = std_msg.header.frame_id
            t.child_frame_id = std_msg.child_frame_id
            t.transform.translation.x = std_msg.pose.pose.position.x
            t.transform.translation.y = std_msg.pose.pose.position.y
            t.transform.translation.z = std_msg.pose.pose.position.z
            t.transform.rotation = std_msg.pose.pose.orientation
            self.tf_broadcaster.sendTransform(t)

        self.latest_odom = std_msg
        self.odom_pub.publish(std_msg)
        self._compute_and_publish_derived_odom(std_msg)

    def _compute_and_publish_derived_odom(self, std_msg: Odometry):
        orientation_list = [
            std_msg.pose.pose.orientation.x,
            std_msg.pose.pose.orientation.y,
            std_msg.pose.pose.orientation.z,
            std_msg.pose.pose.orientation.w
        ]
        _, _, yaw = euler_from_quaternion(orientation_list)
        heading_deg = math.degrees(yaw)
        if heading_deg < 0:
            heading_deg += 360.0

        if not self.is_receiving_rtk_heading:
            heading_msg = Float32()
            heading_msg.data = 90.0 - heading_deg
            self.heading_pub.publish(heading_msg)

        vx = std_msg.twist.twist.linear.x
        vy = std_msg.twist.twist.linear.y
        course_rad = math.atan2(vy, vx)
        course_deg = math.degrees(course_rad)
        if course_deg < 0:
            course_deg += 360.0

        course_msg = Float32()
        course_msg.data = course_deg
        self.course_pub.publish(course_msg)

        speed_msg = Float32()
        speed_msg.data = math.sqrt(vx**2 + vy**2)
        self.speed_pub.publish(speed_msg)

    def _battery_callback(self, msg):
        std_msg = Float32()
        std_msg.data = msg.data if self.use_sim else float(msg.remaining * 100.0)
        self.battery_pub.publish(std_msg)


def main(args=None):
    rclpy.init(args=args)
    node = SmarcTopicsPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()