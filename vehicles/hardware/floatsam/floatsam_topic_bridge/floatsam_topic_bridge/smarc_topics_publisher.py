#!/usr/bin/env python3
"""
SMaRC Topics Publisher Node for Floatsam
Converts simulator or real hardware topics to standard SMaRC topics
"""

import rclpy
from rclpy.node import Node
import yaml
import os
from ament_index_python.packages import get_package_share_directory
import math
import importlib
from rclpy.qos import qos_profile_sensor_data
from septentrio_gnss_driver.msg import AttEuler
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy

# --- ADDED: SensorGps import ---
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
    Uses a switch case (if/else) based on use_sim parameter to load appropriate config.
    """
    
    def __init__(self):
        super().__init__('floatsam_smarc_topics_publisher')

        # Declare parameters
        self.declare_parameter('use_sim', True)
        self.declare_parameter('robot_name', 'floatsam_usv')
        self.declare_parameter('thruster_limit', 1000.0)
        self.declare_parameter('master_floatsam', 'floatsam_usv_0')

        self.use_sim = self.get_parameter('use_sim').value
        self.robot_name = self.get_parameter('robot_name').value
        self.thruster_limit = float(self.get_parameter('thruster_limit').value)
        self.master_robot_name = self.get_parameter('master_floatsam').value

        
        if self.thruster_limit <= 0.0:
            self.get_logger().warn('Parameter thruster_limit must be > 0. Falling back to 1000.0 RPM')
            self.thruster_limit = 1000.0

        # --- DYNAMIC QoS AND CONFIG SETUP ---
        if self.use_sim:
            # SIMULATION: Use standard ROS 2 Reliable QoS (queue size 10)
            self.px4_qos = 10
            self.actuator_qos = 10
            config_file = 'sim_topics.yaml'
            self.get_logger().info('SIMULATION MODE: Using standard QoS (10) and sim topics')
        else:
            # REAL HARDWARE: Use strict PX4 Best-Effort QoS profiles
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
            config_file = 'real_topics.yaml'
            self.get_logger().info('REAL HARDWARE MODE: Using PX4 Best-Effort QoS and real topics')

        # Load configuration
        self.config = self._load_config(config_file)
        
        # Replace {robot_name} placeholder in all topic paths
        self._substitute_robot_name()
        
        # Storage for latest messages
        self.latest_odom = None
        self.latest_gps_left = None
        self.latest_gps_right = None
        self.latest_rtk_position = None
        self.is_receiving_rtk_heading = False
        
        # --- ADDED: Track latest RTK heading in radians ---
        self.latest_rtk_heading_rad = float('nan') 
        
        self.latest_port_cmd = 0.0
        self.latest_strb_cmd = 0.0
        # Tracking variables for safety timeouts and flight modes
        self.last_cmd_time = self.get_clock().now()
        self.is_offboard = False

        # Cache for ActuatorMotors class (set during _setup_topic_bridges)
        self._actuator_motors_cls = None
        
        # Create publishers for derived values (with vehicle namespace)
        self.heading_pub = self.create_publisher(Float32, f'{self.robot_name}/smarc/heading', 10)
        self.course_pub = self.create_publisher(Float32, f'{self.robot_name}/smarc/course', 10)
        self.speed_pub = self.create_publisher(Float32, f'{self.robot_name}/smarc/speed', 10)
        self.latlon_pub = self.create_publisher(GeoPoint, f'{self.robot_name}/smarc/latlon', 10)
        
        # Create subscribers and publishers
        self._setup_topic_bridges()
        self.offboard_mode_pub = self.create_publisher(
            OffboardControlMode,
            f'/fmu/in/offboard_control_mode',
            self.actuator_qos
        )
        
        # Listen to PX4 to see if the human has switched to Manual or Offboard
        self.create_subscription(
            VehicleControlMode, 
            '/fmu/out/vehicle_control_mode', 
            self._control_mode_callback, 
            self.px4_qos
        )

        # --- Auto-Datum Variables ---
        self.datum_is_set = False
        self.datum_utm_x = 0.0
        self.datum_utm_y = 0.0
        self.datum_zone = "utm" # Will be overwritten by the real zone

        # MASTER/SLAVE MULTI-AGENT VARIABLES ---
        self.local_map_offset_x = 0.0
        self.local_map_offset_y = 0.0
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # --- TF Broadcasters (Rebuilding the Unity Engine) ---
        self.tf_broadcaster = TransformBroadcaster(self)
        self.static_tf_broadcaster = StaticTransformBroadcaster(self)

        self.get_logger().info(f'Floatsam SMaRC Topics Publisher started for: {self.robot_name}')
        self.control_loop_timer = self.create_timer(0.1, self._control_loop_callback)
    
    def _load_config(self, config_file):
        """Load YAML configuration file"""
        try:
            package_dir = get_package_share_directory('floatsam_topic_bridge')
            config_path = os.path.join(package_dir, 'config', config_file)
            
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            self.get_logger().info(f' Loaded configuration from: {config_file}')
            return config
        except Exception as e:
            self.get_logger().error(f' Failed to load config file {config_file}: {e}')
            return {'sensors': {}, 'actuators': {}, 'payload': {}}
    
    def _substitute_robot_name(self):
        """Replace {robot_name} placeholder in all topic paths with actual robot name"""
        for category in ['sensors', 'actuators', 'payload']:
            if category in self.config:
                for topic_name, topic_config in self.config[category].items():
                    if 'input_topic' in topic_config:
                        topic_config['input_topic'] = topic_config['input_topic'].replace('{robot_name}', self.robot_name)
                    if 'output_topic' in topic_config:
                        topic_config['output_topic'] = topic_config['output_topic'].replace('{robot_name}', self.robot_name)
        self.get_logger().info(f' Substituted {{robot_name}} with: {self.robot_name}')
    
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
        """Set up subscribers and publishers for all configured topics"""
        sensors = self.config.get('sensors', {})
        actuators = self.config.get('actuators', {})
        payload = self.config.get('payload', {})
        
        # Helper to add vehicle namespace
        def namespaced_topic(topic):
            """Add vehicle namespace if not already present"""
            if topic.startswith('/') or topic.startswith(self.robot_name):
                return topic
            return f'{self.robot_name}/{topic}'
        
        # GPS sensors (dual)
        if 'gps_left' in sensors:
            msg_class = self._get_message_class(sensors['gps_left']['msg_type'])
            self.create_subscription(msg_class, sensors['gps_left']['input_topic'], 
                                    self._gps_left_callback, self.px4_qos)
            self.gps_left_pub = self.create_publisher(NavSatFix, namespaced_topic(sensors['gps_left']['output_topic']), 10)
            
        if 'gps_right' in sensors:
            msg_class = self._get_message_class(sensors['gps_right']['msg_type'])
            self.create_subscription(msg_class, sensors['gps_right']['input_topic'], 
                                    self._gps_right_callback, self.px4_qos)
            self.gps_right_pub = self.create_publisher(NavSatFix, namespaced_topic(sensors['gps_right']['output_topic']), 10)
            self.get_logger().info(f'  GPS Right: {sensors["gps_right"]["input_topic"]} → {namespaced_topic(sensors["gps_right"]["output_topic"])}')
        
        # RTK GPS (high precision)
        if 'rtk_heading' in sensors:
            # Try dynamic lookup first, then fallback to explicit import
            msg_class = self._get_message_class(sensors['rtk_heading']['msg_type'])
            if msg_class is None:
                msg_class = AttEuler
            
            if msg_class is not None:
                self.create_subscription(msg_class, sensors['rtk_heading']['input_topic'], 
                                        self._rtk_heading_callback, 10)
                self.rtk_heading_pub = self.create_publisher(Float32, namespaced_topic(sensors['rtk_heading']['output_topic']), 10)
                self.get_logger().info(f'  RTK heading: {sensors["rtk_heading"]["input_topic"]} → {namespaced_topic(sensors["rtk_heading"]["output_topic"])}')
            else:
                self.get_logger().error("Could not load AttEuler message class. Is septentrio_gnss_driver sourced?")

        if 'rtk_position' in sensors:
            msg_class = self._get_message_class(sensors['rtk_position']['msg_type'])
            self.create_subscription(msg_class, sensors['rtk_position']['input_topic'], 
                                    self._rtk_position_callback, 10)
            self.rtk_position_pub = self.create_publisher(NavSatFix, namespaced_topic(sensors['rtk_position']['output_topic']), 10)
            self.get_logger().info(f'  RTK Position: {sensors["rtk_position"]["input_topic"]} → {namespaced_topic(sensors["rtk_position"]["output_topic"])}')
            
            # --- Setup PX4 RTK Injection based on YAML ---
            px4_rtk_topic = sensors['rtk_position'].get('output_for_px4', None)
            if not self.use_sim and px4_rtk_topic:
                self.sensor_gps_pub = self.create_publisher(
                    SensorGps,
                    px4_rtk_topic,
                    self.px4_qos
                )
                self.get_logger().info(f'  RTK: Injection to {px4_rtk_topic} ENABLED')
        
        # IMU (raw data only, heading comes from odom)
        if 'imu' in sensors:
            msg_class = self._get_message_class(sensors['imu']['msg_type'])
            self.create_subscription(msg_class, sensors['imu']['input_topic'], self._imu_callback, self.px4_qos)
            self.imu_pub = self.create_publisher(Imu, namespaced_topic(sensors['imu']['output_topic']), 10)
            self.get_logger().info(f'  IMU (raw): {sensors["imu"]["input_topic"]} → {namespaced_topic(sensors["imu"]["output_topic"])}')
        
        # Depth Pressure
        if 'depth_pressure' in sensors:
            msg_class = self._get_message_class(sensors['depth_pressure']['msg_type'])
            self.create_subscription(msg_class, sensors['depth_pressure']['input_topic'], 
                                    self._depth_callback, self.px4_qos)
            self.depth_pub = self.create_publisher(Float32, namespaced_topic(sensors['depth_pressure']['output_topic']), 10)
            self.get_logger().info(f'  Depth: {sensors["depth_pressure"]["input_topic"]} → {namespaced_topic(sensors["depth_pressure"]["output_topic"])}')
        
        # DVL
        if 'dvl' in sensors:
            msg_class = self._get_message_class(sensors['dvl']['msg_type'])
            self.create_subscription(msg_class, sensors['dvl']['input_topic'], self._dvl_callback, self.px4_qos)
            self.dvl_pub = self.create_publisher(Range, namespaced_topic(sensors['dvl']['output_topic']), 10)
            self.get_logger().info(f'  DVL: {sensors["dvl"]["input_topic"]} → {namespaced_topic(sensors["dvl"]["output_topic"])}')
        
        # Leak sensor
        if 'leak' in sensors:
            msg_class = self._get_message_class(sensors['leak']['msg_type'])
            self.create_subscription(msg_class, sensors['leak']['input_topic'], self._leak_callback, self.px4_qos)
            self.leak_pub = self.create_publisher(msg_class, namespaced_topic(sensors['leak']['output_topic']), 10)
            self.get_logger().info(f'  Leak: {sensors["leak"]["input_topic"]} → {namespaced_topic(sensors["leak"]["output_topic"])}')
        
        # Odometry (computes heading, course, speed, latlon)
        if 'odom_gt' in sensors:
            odom_config = sensors['odom_gt']
        elif 'odom' in sensors:
            odom_config = sensors['odom']
        else:
            odom_config = None
            
        if odom_config:
            msg_class = self._get_message_class(odom_config['msg_type'])
            self.create_subscription(msg_class, odom_config['input_topic'], self._odom_callback, self.px4_qos)
            self.odom_pub = self.create_publisher(Odometry, namespaced_topic(odom_config['output_topic']), 10)
            self.get_logger().info(f'  Odom: {odom_config["input_topic"]} → {namespaced_topic(odom_config["output_topic"])}')
            self.get_logger().info(f'  ↳ Also computing heading, course, speed, and latlon from best GPS')
        
        # Battery
        if 'battery' in sensors:
            msg_class = self._get_message_class(sensors['battery']['msg_type'])
            self.create_subscription(msg_class, sensors['battery']['input_topic'], 
                                    self._battery_callback, self.px4_qos)
            self.battery_pub = self.create_publisher(Float32, namespaced_topic(sensors['battery']['output_topic']), 10)
            self.get_logger().info(f'  Battery: {sensors["battery"]["input_topic"]} → {namespaced_topic(sensors["battery"]["output_topic"])}')
        
        # --- Actuators (Coupled vs Decoupled Logic) ---
        if 'thruster_port_cmd' in actuators and 'thruster_strb_cmd' in actuators:
            self.create_subscription(Float32, actuators['thruster_port_cmd']['input_topic'], 
                                    self._port_cmd_callback, 10)
            self.create_subscription(Float32, actuators['thruster_strb_cmd']['input_topic'], 
                                    self._strb_cmd_callback, 10)
            
            if self.use_sim:
                # SIMULATION: Publish to decoupled topics
                self.sim_port_pub = self.create_publisher(Float32, namespaced_topic(actuators['thruster_port_cmd']['output_topic']), 10)
                self.sim_strb_pub = self.create_publisher(Float32, namespaced_topic(actuators['thruster_strb_cmd']['output_topic']), 10)
                self.get_logger().info('  Actuators: Bridged as DECOUPLED (Sim Mode)')
            else:
                # REAL HARDWARE: Publish to coupled PX4 array
                # Cache the class so we don't re-import it on every publish
                self._actuator_motors_cls = self._get_message_class(actuators['px4_motors']['msg_type'])
                self.px4_motors_pub = self.create_publisher(
                    self._actuator_motors_cls,
                    actuators['px4_motors']['output_topic'],
                    self.actuator_qos  # ← BEST_EFFORT + VOLATILE
                )
                self.get_logger().info('  Actuators: Bridged as COUPLED (PX4 Mode)')
        
        # Payload sensors (passthrough with dynamic typing)
        for payload_name, config in payload.items():
            msg_class = self._get_message_class(config['msg_type'])
            if msg_class:
                pub = self.create_publisher(msg_class, namespaced_topic(config['output_topic']), self.px4_qos)
                self.create_subscription(msg_class, config['input_topic'], 
                                        self._create_passthrough_callback(pub), 10)
                self.get_logger().info(f'  Payload {payload_name}: {config["input_topic"]} → {namespaced_topic(config["output_topic"])}')
    
    def _port_cmd_callback(self, msg: Float32):
        #if self.use_sim:
        #    self.latest_port_cmd = msg.data
        #    self.last_cmd_time = self.get_clock().now()
        #else:
        raw = msg.data / self.thruster_limit
        self.latest_port_cmd = max(-1.0, min(1.0, raw))
        self.last_cmd_time = self.get_clock().now()

    def _strb_cmd_callback(self, msg: Float32):
        #if self.use_sim:
        #    self.latest_strb_cmd = msg.data
        #    self.last_cmd_time = self.get_clock().now()
        #else:
        raw = msg.data / self.thruster_limit
        self.latest_strb_cmd = max(-1.0, min(1.0, raw))
        self.last_cmd_time = self.get_clock().now()


    def _publish_actuators(self):
        """Applies safety timeouts and yields to Manual RC"""
        
        # --- THE TIMEOUT (Safety Dead-Man's Switch) ---
        dt = (self.get_clock().now() - self.last_cmd_time).nanoseconds / 1e9
        if dt > 0.5:
            self.latest_port_cmd = 0.0
            self.latest_strb_cmd = 0.0

        if self.use_sim:
            port_msg = Float32()
            port_msg.data = self.latest_port_cmd * self.thruster_limit
            strb_msg = Float32()
            strb_msg.data = self.latest_strb_cmd * self.thruster_limit
            self.get_logger().info("SONO USE SIM TRUEEEEEEEEEEE")
            self.sim_port_pub.publish(port_msg)
            self.sim_strb_pub.publish(strb_msg)
        else:
            # If the human is in Manual mode, ROS stops publishing.
            # RC takes over flawlessly without fighting.
            self.get_logger().info("SONO USE SIM FALSEEE")
            if not self.is_offboard:
                self.get_logger().info("SONO GAY")
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
        # Publish the Offboard Heartbeat
        msg = OffboardControlMode()
        msg.timestamp = self.get_clock().now().nanoseconds // 1000
        
        # Disable all boat autonomy
        msg.position = False
        msg.velocity = False
        msg.acceleration = False
        msg.attitude = False
        msg.body_rate = False
        msg.thrust_and_torque = False
        
        # Enable direct hardware control
        msg.direct_actuator = True
        
        self.offboard_mode_pub.publish(msg)
        self._publish_actuators()

    def _gps_left_callback(self, msg):
        """Translate PX4 SensorGps into standard ROS 2 NavSatFix"""
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

    def _control_mode_callback(self, msg):
        """Constantly updates whether we are in Offboard mode or not"""
        self.is_offboard = msg.flag_control_offboard_enabled

    
    def _gps_right_callback(self, msg):
        """Translate PX4 SensorGps into standard ROS 2 NavSatFix"""
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
    
    # --- ADDED/MODIFIED: Complete RTK handling logic ---
    def _rtk_heading_callback(self, msg):
        """Handle Septentrio AttEuler message"""
        # Note: septentrio_gnss_driver/msg/AttEuler uses 'heading' attribute
        if math.isnan(msg.heading):
            return

        self.is_receiving_rtk_heading = True
        
        # Convert to Radians for PX4
        heading_rad = math.radians(msg.heading)
        self.latest_rtk_heading_rad = math.atan2(math.sin(heading_rad), math.cos(heading_rad))
        
        # Publish SMaRC standard (Degrees)
        heading_msg = Float32()
        heading_msg.data = float(msg.heading)
        self.heading_pub.publish(heading_msg)

    def _rtk_position_callback(self, msg: NavSatFix):
        """Publish standard RTK position AND inject combined SensorGps into PX4"""
        self.latest_rtk_position = msg
        self.rtk_position_pub.publish(msg)
        self._publish_best_gps()
        
        # Only inject if we are on real hardware and the publisher was successfully created
        if not self.use_sim and hasattr(self, 'sensor_gps_pub'):
            px4_gps = SensorGps()
            now_us = self.get_clock().now().nanoseconds // 1000
            px4_gps.timestamp = now_us
            px4_gps.timestamp_sample = now_us
            
            # --- UPDATED FIELD NAMES FOR NEW PX4 VERSIONS ---
            px4_gps.latitude_deg = float(msg.latitude)   # New versions use float degrees
            px4_gps.longitude_deg = float(msg.longitude) # New versions use float degrees
            px4_gps.altitude_msl_m = float(msg.altitude) # New versions use meters
            px4_gps.altitude_ellipsoid_m = float(msg.altitude)
            
            px4_gps.fix_type = 6 # 6 = RTK Fixed
            
            # Estimate accuracy from ROS covariance
            if len(msg.position_covariance) == 9 and msg.position_covariance[0] > 0:
                px4_gps.eph = float(math.sqrt(msg.position_covariance[0]))
            else:
                px4_gps.eph = 0.1 # Very tight for RTK
                
            if len(msg.position_covariance) == 9 and msg.position_covariance[8] > 0:
                px4_gps.epv = float(math.sqrt(msg.position_covariance[8]))
            else:
                px4_gps.epv = 0.2
            
            px4_gps.heading = self.latest_rtk_heading_rad
            
            # Required placeholders for the EKF
            px4_gps.satellites_used = 12 
            px4_gps.vel_n_m_s = 0.0
            px4_gps.vel_e_m_s = 0.0
            px4_gps.vel_d_m_s = 0.0
            px4_gps.vel_ned_valid = False
            
            self.sensor_gps_pub.publish(px4_gps)
    # --- END OF ADDED RTK LOGIC ---
    
    def _publish_best_gps(self):
        """Publish best available GPS and set the Multi-Agent Auto-Datum on first fix"""
        best_position = self.latest_rtk_position or self.latest_gps_left or self.latest_gps_right
        
        if best_position:
            geopoint = GeoPoint()
            geopoint.latitude  = best_position.latitude
            geopoint.longitude = best_position.longitude
            geopoint.altitude  = best_position.altitude
            self.latlon_pub.publish(geopoint)
            
            # If we haven't locked the map to Earth yet, do it now
            if not self.datum_is_set and not self.use_sim:
                try:
                    utm_point = convert_latlon_to_utm(geopoint)
                    self.datum_zone = utm_point.header.frame_id
                    
                    if self.robot_name == self.master_robot_name:
                        # I AM THE MASTER: I define the global map origin
                        self.datum_utm_x = utm_point.point.x
                        self.datum_utm_y = utm_point.point.y
                        self.datum_is_set = True
                        self._publish_static_transforms()
                        self.get_logger().info(f"MASTER MAP ORIGIN LOCKED. Zone: {self.datum_zone} | X: {self.datum_utm_x:.2f} | Y: {self.datum_utm_y:.2f}")
                    
                    else:
                        # I AM A SLAVE: I must calculate my offset from the Master
                        try:
                            # Ask the TF tree where the Master put the map
                            tf = self.tf_buffer.lookup_transform(
                                self.datum_zone, 
                                "map", 
                                rclpy.time.Time()
                            )
                            master_utm_x = tf.transform.translation.x
                            master_utm_y = tf.transform.translation.y
                            
                            # Calculate the physical distance from the Master
                            self.local_map_offset_x = utm_point.point.x - master_utm_x
                            self.local_map_offset_y = utm_point.point.y - master_utm_y
                            
                            self.datum_is_set = True
                            self._publish_static_transforms()
                            self.get_logger().info(f"SLAVE MAP LOCKED! Offset from Master -> X: {self.local_map_offset_x:.2f}m | Y: {self.local_map_offset_y:.2f}m")
                            
                        except Exception as e:
                            self.get_logger().info(f"Waiting for Master ({self.master_robot_name}) to publish global map...", throttle_duration_sec=2.0)
                            return
                            
                except Exception as e:
                    self.get_logger().error(f"Failed to set auto-datum: {e}")

    def _publish_static_transforms(self):
        """Creates the permanent links for the shared multi-agent map"""
        transforms_to_publish = []
        
        # --- Planet Earth (UTM) to Global Map ---
        # ONLY THE MASTER PUBLISHES THIS TO AVOID TF FLICKERING
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

        # --- Global Map to Local Map (The Shared Multi-Agent Universe) ---
        t_global = TransformStamped()
        t_global.header.stamp = self.get_clock().now().to_msg()
        t_global.header.frame_id = "map"  
        t_global.child_frame_id = f"{self.robot_name}/map"
        
        # Inject the calculated Slave Offset here (Master's offset is naturally 0.0)
        t_global.transform.translation.x = float(self.local_map_offset_x)
        t_global.transform.translation.y = float(self.local_map_offset_y)
        t_global.transform.translation.z = 0.0
        t_global.transform.rotation.w = 1.0
        transforms_to_publish.append(t_global)
        
        # --- Local Map to Odometry (The Robot's specific starting point) ---
        t_local = TransformStamped()
        t_local.header.stamp = self.get_clock().now().to_msg()
        t_local.header.frame_id = f"{self.robot_name}/map"
        t_local.child_frame_id = f"{self.robot_name}/odom"
        
        t_local.transform.translation.x = 0.0
        t_local.transform.translation.y = 0.0
        t_local.transform.translation.z = 0.0
        t_local.transform.rotation.w = 1.0
        transforms_to_publish.append(t_local)
        
        # Publish everything
        self.static_tf_broadcaster.sendTransform(transforms_to_publish)
    
    def _imu_callback(self, msg):
        """Translate PX4 SensorCombined into standard ROS 2 Imu"""
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
        """Convert pressure to depth (assuming seawater)"""
        atmospheric_pressure = 101325.0   # Pa
        water_pressure_per_meter = 10000.0  # Pa/m (seawater)
        
        depth_m = (msg.fluid_pressure - atmospheric_pressure) / water_pressure_per_meter
        depth_m = max(0.0, depth_m)  # Depth cannot be negative
        
        depth_msg = Float32()
        depth_msg.data = depth_m
        self.depth_pub.publish(depth_msg)
    
    def _dvl_callback(self, msg: Range):
        """Pass through DVL data"""
        self.dvl_pub.publish(msg)
    
    def _leak_callback(self, msg: Bool):
        """Pass through leak sensor data"""
        self.leak_pub.publish(msg)
        if msg.data:
            self.get_logger().warn('  LEAK DETECTED!')
    
    def _odom_callback(self, msg):
        """Handle odometry from either Simulator (Standard) or PX4 (px4_msgs)"""
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

            # TF BROADCASTER (odom -> base_link)
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
        """Helper function to calculate SMaRC derived values"""
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
        
        # Only publish odometry-derived heading if RTK heading is not available
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
        
        speed = math.sqrt(vx**2 + vy**2)
        speed_msg = Float32()
        speed_msg.data = speed
        self.speed_pub.publish(speed_msg)
    
    def _battery_callback(self, msg):
        """Translate PX4 BatteryStatus into a standard Float32 percentage"""
        std_msg = Float32()
        
        if self.use_sim:
            std_msg.data = msg.data
        else:
            std_msg.data = float(msg.remaining * 100.0)
            
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


