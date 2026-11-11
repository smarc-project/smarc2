#!/usr/bin/env python3
"""
SMaRC Topics Publisher Node for Floatsam (Simulation only)
Converts simulator topics to standard SMaRC topics
"""

import rclpy
from rclpy.node import Node
import math
import importlib
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy

# ROS message types
from sensor_msgs.msg import NavSatFix, Imu, FluidPressure
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32
from geographic_msgs.msg import GeoPoint
from tf_transformations import euler_from_quaternion
from tf2_ros import Buffer, TransformListener
from rclpy.time import Time

from floatsam_controllers.floatsam_common import FloatSam


class SmarcTopicsPublisher(Node):
    """
    Bridge node that converts Floatsam simulator topics to standard SMaRC topics.
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
        self.thruster_limit = self.get_parameter("thruster_limit").get_parameter_value().double_value

        self.floatsam = FloatSam(self, self.robot_name, use_sim=True)

        if self.thruster_limit <= 0.0:
            self.get_logger().warn('Parameter thruster_limit must be > 0. Falling back to 1000.0 RPM')
            self.thruster_limit = 1000.0

        # Standard QoS for simulation
        self.qos = 10

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

        self.latest_port_cmd = 0.0
        self.latest_strb_cmd = 0.0
        self.last_cmd_time = self.get_clock().now()

        # Relative topics — PushRosNamespace will prepend robot_name automatically
        self.heading_pub = self.create_publisher(Float32, 'smarc/heading', 10)
        self.course_pub  = self.create_publisher(Float32, 'smarc/course', 10)
        self.speed_pub   = self.create_publisher(Float32, 'smarc/speed', 10)
        self.latlon_pub  = self.create_publisher(GeoPoint, 'smarc/latlon', 10)

        # BEST_EFFORT QoS for odom_in_map.
        # Any external subscriber to this topic MUST also use BEST_EFFORT.
        self.odom_in_map_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1
        )
        self.odom_in_map_pub = self.create_publisher(Odometry, 'smarc/odom_in_map', self.odom_in_map_qos)

        # TF buffer/listener (used to convert odometry into the shared "map" frame)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Create subscribers and publishers from YAML config
        self._setup_topic_bridges()

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
        """Dynamically import and return message class from string like 'std_msgs/Float32' or 'pkg/msg/Type'"""
        try:
            parts = msg_type_str.split('/')
            pkg = parts[0]        # The first part is always the package name
            msg = parts[-1]       # The last part is always the message class name

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
                                     self._gps_left_callback, self.qos)
            self.gps_left_pub = self.create_publisher(NavSatFix, sensors['gps_left']['output_topic'], 10)

        if 'gps_right' in sensors:
            msg_class = self._get_message_class(sensors['gps_right']['msg_type'])
            self.create_subscription(msg_class, sensors['gps_right']['input_topic'],
                                     self._gps_right_callback, self.qos)
            self.gps_right_pub = self.create_publisher(NavSatFix, sensors['gps_right']['output_topic'], 10)
            self.get_logger().info(f'  GPS Right: {sensors["gps_right"]["input_topic"]} → {sensors["gps_right"]["output_topic"]}')

        # IMU
        if 'imu' in sensors:
            msg_class = self._get_message_class(sensors['imu']['msg_type'])
            self.create_subscription(msg_class, sensors['imu']['input_topic'], self._imu_callback, self.qos)
            self.imu_pub = self.create_publisher(Imu, sensors['imu']['output_topic'], 10)
            self.get_logger().info(f'  IMU: {sensors["imu"]["input_topic"]} → {sensors["imu"]["output_topic"]}')

        # Depth Pressure
        if 'depth_pressure' in sensors:
            msg_class = self._get_message_class(sensors['depth_pressure']['msg_type'])
            self.create_subscription(msg_class, sensors['depth_pressure']['input_topic'],
                                     self._depth_callback, self.qos)
            self.depth_pub = self.create_publisher(Float32, sensors['depth_pressure']['output_topic'], 10)
            self.get_logger().info(f'  Depth: {sensors["depth_pressure"]["input_topic"]} → {sensors["depth_pressure"]["output_topic"]}')

        # Odometry
        if 'odom_gt' in sensors:
            odom_config = sensors['odom_gt']
        elif 'odom' in sensors:
            odom_config = sensors['odom']
        else:
            odom_config = None

        if odom_config:
            msg_class = self._get_message_class(odom_config['msg_type'])
            self.create_subscription(msg_class, odom_config['input_topic'], self._odom_callback, self.qos)
            self.odom_pub = self.create_publisher(Odometry, odom_config['output_topic'], 10)
            self.get_logger().info(f'  Odom: {odom_config["input_topic"]} → {odom_config["output_topic"]}')
            self.get_logger().info(f'  ↳ Also computing heading, course, speed, and latlon from best GPS')

        # Battery
        if 'battery' in sensors:
            msg_class = self._get_message_class(sensors['battery']['msg_type'])
            self.create_subscription(msg_class, sensors['battery']['input_topic'],
                                     self._battery_callback, self.qos)
            self.battery_pub = self.create_publisher(Float32, sensors['battery']['output_topic'], 10)
            self.get_logger().info(f'  Battery: {sensors["battery"]["input_topic"]} → {sensors["battery"]["output_topic"]}')

        # Actuators (decoupled port/starboard thruster commands)
        if 'thruster_port_cmd' in actuators and 'thruster_strb_cmd' in actuators:
            self.create_subscription(Float32, actuators['thruster_port_cmd']['input_topic'],
                                     self._port_cmd_callback, 10)
            self.create_subscription(Float32, actuators['thruster_strb_cmd']['input_topic'],
                                     self._strb_cmd_callback, 10)

            self.sim_port_pub = self.create_publisher(Float32, actuators['thruster_port_cmd']['output_topic'], 10)
            self.sim_strb_pub = self.create_publisher(Float32, actuators['thruster_strb_cmd']['output_topic'], 10)
            self.get_logger().info('  Actuators: Bridged (Sim Mode)')

        # Payload (passthrough)
        for payload_name, config in payload.items():
            msg_class = self._get_message_class(config['msg_type'])
            if msg_class:
                pub = self.create_publisher(msg_class, config['output_topic'], self.qos)
                self.create_subscription(msg_class, config['input_topic'],
                                         self._create_passthrough_callback(pub), 10)
                self.get_logger().info(f'  Payload {payload_name}: {config["input_topic"]} → {config["output_topic"]}')

    def _port_cmd_callback(self, msg: Float32):
        self.latest_port_cmd  = msg.data
        self.last_cmd_time = self.get_clock().now()

    def _strb_cmd_callback(self, msg: Float32):
        self.latest_strb_cmd = msg.data 
        self.last_cmd_time = self.get_clock().now()

    def _publish_actuators(self):
        """Applies a safety timeout that zeroes thrusters if commands stop arriving"""
        dt = (self.get_clock().now() - self.last_cmd_time).nanoseconds / 1e9
        if dt > 0.5:
            self.latest_port_cmd = 0.0
            self.latest_strb_cmd = 0.0

        port_msg = Float32()
        port_msg.data = self.latest_port_cmd
        strb_msg = Float32()
        strb_msg.data = self.latest_strb_cmd
        self.sim_port_pub.publish(port_msg)
        self.sim_strb_pub.publish(strb_msg)

    def _control_loop_callback(self):
        """Runs at 10Hz. Applies the actuator safety timeout and publishes current thruster commands."""
        self._publish_actuators()

    def _gps_left_callback(self, msg):
        self.latest_gps_left = msg
        self.gps_left_pub.publish(msg)
        self._publish_best_gps()

    def _gps_right_callback(self, msg):
        self.latest_gps_right = msg
        self.gps_right_pub.publish(msg)
        self._publish_best_gps()

    def _publish_best_gps(self):
        """Publish best available GPS fix as lat/lon."""
        best_position = self.latest_gps_left or self.latest_gps_right
        if not best_position:
            return

        geopoint = GeoPoint()
        geopoint.latitude  = best_position.latitude
        geopoint.longitude = best_position.longitude
        geopoint.altitude  = best_position.altitude
        self.latlon_pub.publish(geopoint)

    def _imu_callback(self, msg):
        self.imu_pub.publish(msg)

    def _depth_callback(self, msg: FluidPressure):
        atmospheric_pressure = 101325.0
        water_pressure_per_meter = 10000.0
        depth_m = (msg.fluid_pressure - atmospheric_pressure) / water_pressure_per_meter
        depth_msg = Float32()
        depth_msg.data = depth_m
        self.depth_pub.publish(depth_msg)

    def _odom_callback(self, msg: Odometry):
        std_msg = msg

        self.latest_odom = std_msg
        self.odom_pub.publish(std_msg)


        target_frame = self.floatsam.LOCAL_MAP_FRAME
        if self.tf_buffer.can_transform(target_frame, std_msg.header.frame_id, Time()):
            try:
                # Convert Position from Odom to global Map
                map_point = self.floatsam.convert_point_frame_to_frame(
                    std_msg.pose.pose.position.x,
                    std_msg.pose.pose.position.y,
                    std_msg.pose.pose.position.z,
                    source_frame=std_msg.header.frame_id,
                    target_frame=target_frame  
                )

                # Convert Velocity from Odom to global Map
                map_twist = self.floatsam.convert_twist_frame_to_frame(
                    std_msg.twist.twist,
                    source_frame=std_msg.header.frame_id,
                    target_frame=target_frame  
                )

                # Build  Odometry in global map frame
                odom_in_map = Odometry()
                odom_in_map.header.stamp = std_msg.header.stamp
                odom_in_map.header.frame_id = target_frame  
                odom_in_map.child_frame_id = ""  

                # Position in map frame
                odom_in_map.pose.pose.position = map_point.point
                odom_in_map.pose.pose.orientation.w = 1.0  # map is fixed
                odom_in_map.pose.pose.orientation.x = 0.0
                odom_in_map.pose.pose.orientation.y = 0.0
                odom_in_map.pose.pose.orientation.z = 0.0

                # Velocity in map frame
                odom_in_map.twist.twist = map_twist

                self.odom_in_map_pub.publish(odom_in_map)

            except Exception as e:
                self.get_logger().debug(f'Could not compute odom_in_map: {e}')
        else:
            self.get_logger().warn(
                f'Waiting for "{target_frame}" frame to exist in TF tree — odom_in_map will not be published until then.',
                throttle_duration_sec=5.0
            )

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
        std_msg.data = msg.data
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