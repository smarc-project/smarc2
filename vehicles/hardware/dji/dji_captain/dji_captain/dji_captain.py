#!/usr/bin/python3

import rclpy, sys, math
import numpy as np
from enum import Enum


from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.time import Time, Duration
from rclpy.timer import Timer
from tf2_ros import Buffer, TransformListener


from std_msgs.msg import Float32, Int8, String
from std_srvs.srv import Trigger
from sensor_msgs.msg import NavSatFix, Joy, BatteryState
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TwistStamped, Pose, PoseStamped, TransformStamped, QuaternionStamped, PointStamped, Vector3Stamped, Quaternion
from geographic_msgs.msg import GeoPoint
from tf2_msgs.msg import TFMessage

from psdk_interfaces.msg import PositionFused, ControlMode, EscData, EscStatusIndividual
from smarc_msgs.msg import Topics as SmarcTopics


from smarc_utilities.georef_utils import convert_latlon_to_utm, convert_utm_to_latlon
from tf_transformations import euler_from_quaternion, quaternion_from_euler
from tf2_geometry_msgs import do_transform_pose_stamped


class PSDKTopics(Enum):
    # these are hardcoded topics in PSDK bridge...
    WRAPPER_NS = "wrapper/psdk_ros2/"
    
    GPS_POSITION        = WRAPPER_NS + "gps_position"
    POSITION_FUSED      = WRAPPER_NS + "position_fused"
    ATTITUDE            = WRAPPER_NS + "attitude"
    HOME_POINT          = WRAPPER_NS + "home_point"
    HOME_POINT_ALTITUDE = WRAPPER_NS + "home_point_altitude"
    ALTITUDE            = WRAPPER_NS + "altitude_sea_level"
    CONTROL_MODE        = WRAPPER_NS + "control_mode"
    BATTERY             = WRAPPER_NS + "battery" 
    VELOCTY_GROUND_FSD  = WRAPPER_NS + "velocity_ground_fused"
    ANGULAR_RATE_GND_FSD= WRAPPER_NS + "angular_rate_ground_fused"
    ESC_DATA            = WRAPPER_NS + "esc_data"
    RC                  = WRAPPER_NS + "rc"

    TAKE_CONTROL_SRV    = WRAPPER_NS + "obtain_ctrl_authority"
    RELEASE_CONTROL_SRV = WRAPPER_NS + "release_ctrl_authority"
    TAKEOFF_SRV         = WRAPPER_NS + "takeoff"
    LAND_SRV            = WRAPPER_NS + "land"

    FLU_JOY             = WRAPPER_NS + "flight_control_setpoint_FLUvelocity_yawrate"



class DjiCaptain():
    def __init__(self, node: Node):
        self._node = node
        self._TF_NS = "Quadrotor/" #TODO take as rosparam...
        self.declare_node_parameters()
        
        self._move_to_setpoint : PoseStamped | None = None
        self._joy_timer : None | Timer = None
        self._joy_pub = node.create_publisher(Joy, PSDKTopics.FLU_JOY.value, qos_profile=10)
        
        self.MOVE_TO_SETPOINT_TOPIC = "move_to_setpoint"
        self.MOVE_TO_SETPOINT_MAX_AGE : float = 1.0 #originally 0.5, was modified to 1 for testing in sim # seconds, how long we keep the move to setpoint before we consider it stale
        self.JOY_MAX = 0.4
        self.JOY_PERIOD = .1
        self.READY_BATTERY_PERCENTAGE = 40
        self.READY_HEIGHT_ABOVE_GROUND = 2
        self.ERROR_BATTERY_PERCENTAGE = 15
        self.ERROR_HEIGHT_ABOVE_GROUND = 1
        # this is the idle RPM/current for the ESCs, below this we consider the vehicle not flying
        self.NUM_PROPS = 4 # because the esc message always has 8 fields...
        self.ESC_IDLE_RPM = 1000  
        self.ESC_IDLE_CURRENT = 200
        # if things are below these values, we probably have no payload
        self.ESC_NO_PAYLOAD_CURRENT_MAX = 3000
        self.ESC_NO_PAYLOAD_RPM_MAX = 3000

        self.UTM_FRAME = "utm"
        self.ODOM_FRAME = self._TF_NS + "odom"
        self.MAP_FRAME = self._TF_NS + "map"
        self.BASE_FRAME = self._TF_NS + "base_link"
        self.BASE_FLAT_FRAME = self._TF_NS + "base_flat_link"
        self.BASE_ENU_FRAME = self._TF_NS + "base_ENU_link"
        self.HOME_FRAME = self._TF_NS + "home_point"
        self._utm_labeled_frame : str | None = None


        self._base_pose_in_home : PoseStamped | None = None
        self._base_pose_flat_in_home : PoseStamped | None = None
        self._base_pose_ENU_in_home : PoseStamped | None = None
        self._home_point_in_utm : PointStamped | None = None
        self._home_geo_altitude : float | None = None
        self._gps_point_in_home : PointStamped | None = None
        self._rtk_point_in_home : PointStamped | None = None
        self._velocity_ground : Vector3Stamped | None = None
        self._angular_rate_ground : Vector3Stamped | None = None
        self._vehicle_health = Int8()
        self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_WAITING

        self._esc_data : EscData | None = None

        self._geo_altitude : float | None = None
        self._heading_deg : float | None = None
        self._course_deg : float | None = None

        self._got_control : bool = False
        self._flying : bool = False
        self._carrying_payload : bool = False
        self._battery_percent : float | None = None

        self.prev_joy_vec : np.ndarray | None = None
        self.joy_deriv : np.ndarray | None = None
        self.kP: float | None = None
        self.deriv_limit: float | None = None


        topics = [PSDKTopics.__dict__[t].value for t in PSDKTopics.__members__.keys()]
        topics = ["/Quadrotor/  " + PSDKTopics.__dict__[t].value for t in PSDKTopics.__members__.keys()]
        self.log(f"Subscribed to PSDK topics: --topics {' '.join(topics)}")
       

        self._tf_pub = node.create_publisher(TFMessage,"/tf",qos_profile=10)
        self._tf_timer = node.create_timer(0.02, self._publish_tf)

        self._vehicle_health_pub = node.create_publisher(Int8, SmarcTopics.VEHICLE_HEALTH_TOPIC, qos_profile=10)
        self._vehicle_health_timer = node.create_timer(1, self._publish_vehicle_health)

        self._odom_pub = node.create_publisher(Odometry, SmarcTopics.ODOM_TOPIC, qos_profile=10)
        self._heading_pub = node.create_publisher(Float32, SmarcTopics.HEADING_TOPIC, qos_profile=10)
        self._course_pub = node.create_publisher(Float32, SmarcTopics.COURSE_TOPIC, qos_profile=10)
        self._speed_pub = node.create_publisher(Float32, SmarcTopics.SPEED_TOPIC, qos_profile=10)
        self._pos_latlon_pub = node.create_publisher(GeoPoint, SmarcTopics.POS_LATLON_TOPIC, qos_profile=10)
        self._battery_percent_pub = node.create_publisher(Float32, SmarcTopics.BATTERY_PERCENT_TOPIC, qos_profile=10)
        self._altitude_pub = node.create_publisher(Float32, SmarcTopics.ALTITUDE_TOPIC, qos_profile=10)
        self._smarc_timer = node.create_timer(0.1, self._publish_smarc)

        self._status_pub = node.create_publisher(String, "captain_status", qos_profile=10)
        self._status_str_timer = node.create_timer(0.1,lambda: self._status_pub.publish(String(data=self.status_str)))
        self._tf_pub_status = "Not published yet"
        self._smarc_pub_status = "Not published yet"


        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self._node, spin_thread=True)

        node.create_subscription(
            NavSatFix,
            PSDKTopics.GPS_POSITION.value,
            self._gps_callback,
            qos_profile=10)

        node.create_subscription(
            PositionFused,
            PSDKTopics.POSITION_FUSED.value,
            self._position_fused_callback,
            qos_profile=10)

        node.create_subscription(
            NavSatFix,
            PSDKTopics.HOME_POINT.value,
            self._home_point_callback,
            qos_profile=10)
        
        node.create_subscription(
            Float32,
            PSDKTopics.HOME_POINT_ALTITUDE.value,
            self._home_point_altitude_callback,
            qos_profile=10)

        node.create_subscription(
            QuaternionStamped,
            PSDKTopics.ATTITUDE.value,
            self._attitude_callback,
            qos_profile=10)

        node.create_subscription(
            Float32,
            PSDKTopics.ALTITUDE.value,
            self._geo_alt_cb,
            qos_profile=10)

        node.create_subscription(
            ControlMode,
            PSDKTopics.CONTROL_MODE.value,
            self._control_mode_callback,
            qos_profile=10)
        
        node.create_subscription(
            BatteryState,
            PSDKTopics.BATTERY.value,
            self._battery_callback,
            qos_profile=10)
        
        node.create_subscription(
            Vector3Stamped,
            PSDKTopics.VELOCTY_GROUND_FSD.value,
            self._velocity_ground_callback,
            qos_profile=10)
        
        node.create_subscription(
            Vector3Stamped,
            PSDKTopics.ANGULAR_RATE_GND_FSD.value,
            self._angular_rate_ground_callback,
            qos_profile=10)
        
        node.create_subscription(
            EscData,
            PSDKTopics.ESC_DATA.value,
            lambda msg: setattr(self, "_esc_data", msg),
            qos_profile=10)
        
        node.create_subscription(
            Joy,
            PSDKTopics.RC.value,
            self._rc_cb,
            qos_profile=10)

        node.create_subscription(
            PoseStamped,
            self.MOVE_TO_SETPOINT_TOPIC,
            self._move_to_setpoint_callback,
            qos_profile=10)

        
        # services to take and give-up control + take-off and land
        # call service: obtain/release_ctrl_authority
        self._take_control_srv = node.create_client(Trigger, PSDKTopics.TAKE_CONTROL_SRV.value)
        self._release_control_srv = node.create_client(Trigger, PSDKTopics.RELEASE_CONTROL_SRV.value)
        self._takeoff_srv = node.create_client(Trigger, PSDKTopics.TAKEOFF_SRV.value)
        self._land_srv = node.create_client(Trigger, PSDKTopics.LAND_SRV.value)


        while True:
            commands = "Commands:\n"
            commands += "  1: Take control  \n"
            commands += "  2: Release control\n"
            commands += "  3: Take off\n"
            commands += "  4: Land\n"
            commands += "  5: Print status (also available on $ROBOT_NAME/captain_status topic) \n"
            commands += "  8: EXIT \n"
            commands += "  9: Set max joy to (DANGEROUS, DONT USE UNLESS YOUR NAME STARTS WITH O)\n"
            try:
                self.log(commands)
                n = int(input("Enter number for command: \n"))
                if n == 1: #Take control
                    if not self._take_control_srv.wait_for_service(timeout_sec=5.0):
                        self.log("Take control service not available...")
                        continue
                    future = self._take_control_srv.call_async(Trigger.Request())
                    future.add_done_callback(
                        lambda f: self.log(f"Take control service called, success: {f.result().success}, message: {f.result().message}")
                    )
                elif n == 2: #Release control
                    if not self._release_control_srv.wait_for_service(timeout_sec=5.0):
                        self.log("Release control service not available...")
                        continue
                    future = self._release_control_srv.call_async(Trigger.Request())
                    future.add_done_callback(
                        lambda f: self.log(f"Release control service called, success: {f.result().success}, message: {f.result().message}")
                    )
                elif n == 3: #Take off
                    if self._got_control is False:
                        self.log("You must take control first!")
                        continue
                    n2 = input("Are you sure you want to take-off? (y/[N]): ")
                    if n2.lower() != 'y':
                        self.log("Takeoff cancelled.")
                        continue
                    if not self._takeoff_srv.wait_for_service(timeout_sec=5.0):
                        self.log("Take off service not available...")
                        continue
                    future = self._takeoff_srv.call_async(Trigger.Request())
                    future.add_done_callback(
                        lambda f: self.log(f"Take off service called, success: {f.result().success}, message: {f.result().message}")
                    )
                elif n == 4: #Land
                    if self._got_control is False:
                        self.log("You must take control first!")
                        continue
                    n2 = input("Are you sure you want to land? (y/[N]): ")
                    if n2.lower() != 'y':
                        self.log("Landing cancelled.")
                        continue
                    if not self._land_srv.wait_for_service(timeout_sec=5.0):
                        self.log("Land service not available...")
                        continue
                    future = self._land_srv.call_async(Trigger.Request())
                    future.add_done_callback(
                        lambda f: self.log(f"Land service called, success: {f.result().success}, message: {f.result().message}")
                    )
                elif n == 5: #Print status
                    self.log(self.status_str)
                elif n == 8:
                    self.log("Exiting captain")
                    break
                elif n == 9: # set max joy
                    self.JOY_MAX = float(input("Enter new max joy value: ") or "0")
                    self.log(f"Set max joy to {self.JOY_MAX:.2f} (m/s?)")

            except:
                self.log(f"Invalid input:{input}, please enter a number.")
                continue
            
        


    @property
    def now_stamp(self):
        return self._node.get_clock().now().to_msg() #TODO: Does not work in Sim
    
    
    @property
    def status_str(self) -> str:
        s = "\nDjiCaptain Status:\n"
        s += f"  UTM Frame: {self._utm_labeled_frame}\n"
        s += f"  Home in UTM: {format_point_stamped(self._home_point_in_utm)}\n"
        s += f"  GPS in Home: {format_point_stamped(self._gps_point_in_home)}\n"
        s += f"  RTK in Home: {format_point_stamped(self._rtk_point_in_home)}\n"

        s += f"\n  Position in Home: {format_pose_stamped(self._base_pose_in_home)}\n"
        s += f"  Velocity Ground: {format_vector3_stamped(self._velocity_ground)}\n"
        s += f"  Angular Rate Ground: {format_vector3_stamped(self._angular_rate_ground)}\n"
        s += f"  Geo Altitude: {self._geo_altitude}\n"
        s += f"  Home Geo Altitude: {self._home_geo_altitude}\n"
        s += f"  Heading: {self._heading_deg}\n"
        s += f"  Course: {self._course_deg}\n"
        s += f"  Battery Percent: {self._battery_percent} (ready:{self.READY_BATTERY_PERCENTAGE}, error:{self.ERROR_BATTERY_PERCENTAGE})\n"
        
        s += f"\n  Smarc Topics: {self._smarc_pub_status}\n"
        s += f"  TF: {self._tf_pub_status}\n"

        s += f"\n  Got Control: {self._got_control}\n"
        s += f"  Current target setpoint: {format_pose_stamped(self._move_to_setpoint)}\n"
        if self._base_pose_in_home is None: 
            s+= "  Flying: Unknown (base pose not set)\n"
        else:
            s += f"  Flying: {self._flying} ({self._base_pose_in_home.pose.position.z:.3f} >? {self.READY_HEIGHT_ABOVE_GROUND})\n"
        # s += f"  Carrying Payload: {self._carrying_payload}\n"
        if self._vehicle_health.data == SmarcTopics.VEHICLE_HEALTH_READY:
            s += f"  Vehicle Health: READY\n"
        elif self._vehicle_health.data == SmarcTopics.VEHICLE_HEALTH_ERROR:
            s += f"  Vehicle Health: ERROR\n"
        else:
            s += f"  Vehicle Health: WAITING\n"

        if self.prev_joy_vec is not None:
            s += f"\nJoystick position being sent: forw: {self.prev_joy_vec[0]}, left: {self.prev_joy_vec[1]}, up: {self.prev_joy_vec[2]}\n"
        else:
            s += f"\nNo Joystick position being sent.\n"
        if self.joy_deriv is not None:
            s += f"Joystick derivative: forw: {self.joy_deriv[0]}, left: {self.joy_deriv[1]}, up: {self.joy_deriv[2]}\n"
        else:
            s += f"No Joystick derivative\n"


        return s
    
    def log(self, msg: str):
        self._node.get_logger().info(msg)



    def _geo_alt_cb(self, msg: Float32):
        self._geo_altitude = msg.data


    def _move_to_setpoint_callback(self, msg: PoseStamped):
        # check if the message is too old
        if (self.now_stamp.sec - msg.header.stamp.sec) + \
           (self.now_stamp.nanosec - msg.header.stamp.nanosec) * 1e-9 > self.MOVE_TO_SETPOINT_MAX_AGE:
            self.log(f"Move to setpoint message is older than {self.MOVE_TO_SETPOINT_MAX_AGE}s, ignoring it.")
            self.log(f"Current time: {self.now_stamp.sec}.{self.now_stamp.nanosec}\nSetpoint Time: {msg.header.stamp.sec}.{msg.header.stamp.nanosec}")
            self._move_to_setpoint = None
            return

        if msg.header.frame_id != self.ODOM_FRAME:
            try:
                tf = self._tf_buffer.lookup_transform(
                    self.ODOM_FRAME, 
                    msg.header.frame_id, 
                    Time(seconds=0),
                    timeout=Duration(seconds=1)
                )
                self._move_to_setpoint = do_transform_pose_stamped(msg, tf)
            except Exception as e:
                self.log(f"Failed to transform move to setpoint from {msg.header.frame_id} to {self.ODOM_FRAME}: {e}")
                self._move_to_setpoint = None
                return
        else:
            self._move_to_setpoint = msg

        # self.log(f"Move to setpoint received: {format_pose_stamped(self._move_to_setpoint)}")
        
        if self._joy_timer is None:
            # try:
            #     tf = self._tf_buffer.lookup_transform(
            #         target_frame=self.BASE_ENU_FRAME,
            #         source_frame=self.BASE_FLAT_FRAME,
            #         time=Time(seconds=0),
            #         timeout=Duration(seconds=1)
            #     )
            #     # velocity_as_pose_stamped = PoseStamped()
            #     # velocity_as_pose_stamped.header.frame_id = self.BASE_ENU_FRAME
            #     # velocity_as_pose_stamped.header.stamp = self.now_stamp
            #     # if(self._velocity_ground is not None):
            #     #     velocity_as_pose_stamped.pose.position.x = self._velocity_ground.vector.x
            #     #     velocity_as_pose_stamped.pose.position.y = self._velocity_ground.vector.y
            #     #     velocity_as_pose_stamped.pose.position.z = self._velocity_ground.vector.z
            #     #     velocity_as_pose_stamped_base_flat = do_transform_pose_stamped(velocity_as_pose_stamped, tf)
            #     #     self.prev_joy_vec = np.array([velocity_as_pose_stamped_base_flat.pose.position.x, \
            #     #                                   velocity_as_pose_stamped_base_flat.pose.position.y, \
            #     #                                   velocity_as_pose_stamped_base_flat.pose.position.z])
            #     # else:
            #     #     self.prev_joy_vec = np.array([0.0, 0.0, 0.0])
                
            # except Exception as e:
            #     self.log(f"Failed to transform velocity from {self.BASE_ENU_FRAME} to {self.BASE_FLAT_FRAME}: {e}")
            #     self._move_to_setpoint = None
            #     return
                
            self.kP = self._node.get_parameter("p_gain").value
            self.deriv_limit = self._node.get_parameter("deriv_limit").value
            self._joy_timer = self._node.create_timer(self.JOY_PERIOD, self._move_with_joy)
            self.log("Joy timer started to move with joy.")




    def _move_with_joy(self):
        def cancel_joy_timer():
            if self._joy_timer is not None:
                self._joy_timer.cancel()
                self._joy_timer = None
                self.prev_joy_vec = None
                self.joy_deriv = None
                self.kP = None
                self.deriv_limit = None
                self.log("Joy timer cancelled.")

        if self._move_to_setpoint is None:
            self.log("No move to setpoint set, cannot move with joy.")
            return
        
        if (self.now_stamp.sec - self._move_to_setpoint.header.stamp.sec) + \
           (self.now_stamp.nanosec - self._move_to_setpoint.header.stamp.nanosec) * 1e-9 > self.MOVE_TO_SETPOINT_MAX_AGE:
            self.log(f"Move to setpoint message is older than {self.MOVE_TO_SETPOINT_MAX_AGE}s, cancelling joy timer.")
            self._move_to_setpoint = None
            cancel_joy_timer()
            return
        
        if not self._got_control:
            self.log("Not got control, cannot move with joy.")
            cancel_joy_timer()
            return
        
        if self.kP is None or self.deriv_limit is None:
            self.log("PID gains or limits not set, cannot move with joy.")
            cancel_joy_timer()
            return
        
        if self.prev_joy_vec is None:
            self.log("previous conditions not set, cannot move with joy.")
            cancel_joy_timer()
            return
        
        tf_diff = self._tf_buffer.lookup_transform(
            target_frame = self.BASE_FLAT_FRAME,
            source_frame = self._move_to_setpoint.header.frame_id,
            time=Time(seconds=0),
            timeout=Duration(seconds=1))
        
        target_in_base = do_transform_pose_stamped(self._move_to_setpoint, tf_diff)
        e_forw = target_in_base.pose.position.x # error about each axis
        e_left = target_in_base.pose.position.y
        e_updn = target_in_base.pose.position.z # we like mirrors around a point
        
        e_vec = np.array([e_forw, e_left, e_updn])
        e_mag = np.linalg.norm(e_vec)
        e_dir = e_vec / e_mag

        j_vec = max(min(self.kP * e_mag, self.JOY_MAX), -self.JOY_MAX) * e_dir
        self.joy_deriv = (j_vec - self.prev_joy_vec) / self.JOY_PERIOD
        if(np.linalg.norm(self.joy_deriv) > self.deriv_limit):
            j_vec = (self.prev_joy_vec + self.joy_deriv / np.linalg.norm(self.joy_deriv) * self.deriv_limit)

        if(np.linalg.norm(j_vec) > self.JOY_MAX):
            j_vec = j_vec / np.linalg.norm(j_vec) * self.JOY_MAX

        self.prev_joy_vec = j_vec

        joy_msg = Joy()
        joy_msg.header.stamp = self.now_stamp
        joy_msg.axes = [j_vec[0], j_vec[1], j_vec[2], 0.0]  # Assuming axes: [forward, left, up/down, yaw]
        joy_msg.buttons = []

        self._joy_pub.publish(joy_msg)

    def declare_node_parameters(self):
        self._node.declare_parameter("p_gain", 2.5)
        self._node.declare_parameter("deriv_limit", .4)

    def _rc_cb(self, msg: Joy):
        # if RC is touched by user, we give up control
        if not self._got_control: return

        if msg.axes[0] != 0.0 or msg.axes[1] != 0.0 or msg.axes[2] != 0.0 or msg.axes[3] != 0.0:
            self.log("RC touched, giving up control.")
            self._release_control_srv.call_async(Trigger.Request()).add_done_callback(
                lambda future: self.log(f"Release control service called, success: {future.result().success}, message: {future.result().message}")
            )


    def _velocity_ground_callback(self, msg: Vector3Stamped):
        if self._velocity_ground is None:
            self._velocity_ground = Vector3Stamped()
            self._velocity_ground.header.frame_id = self.ODOM_FRAME
        
        self._velocity_ground.vector = msg.vector
        self._velocity_ground.header.stamp = self.now_stamp

        # also set the course
        if self._velocity_ground.vector.x == 0.0 and self._velocity_ground.vector.y == 0.0:
            self._course_deg = None
        else:
            self._course_deg = math.degrees(math.atan2(
                self._velocity_ground.vector.y,
                self._velocity_ground.vector.x
            ))
            if self._course_deg < 0:
                self._course_deg += 360.0

    def _angular_rate_ground_callback(self, msg: Vector3Stamped):
        if self._angular_rate_ground is None:
            self._angular_rate_ground = Vector3Stamped()
            self._angular_rate_ground.header.frame_id = self.ODOM_FRAME
        
        self._angular_rate_ground.vector = msg.vector
        self._angular_rate_ground.header.stamp = self.now_stamp



    def _control_mode_callback(self, msg: ControlMode):
        # hardcoded numbers from the psdk_ros2 interface
        # 1 = Has control authority, 4 = PSDK
        self._got_control = msg.control_auth == 1 and msg.device_mode == 4

    def _battery_callback(self, msg: BatteryState):
        self._battery_percent = msg.percentage*100
            

    def _position_fused_callback(self, msg: PositionFused):
        if self._home_point_in_utm is None:
            self.log("Home point not set, cannot process position fused message.")
            return
        
        if self._base_pose_in_home is None or self._base_pose_flat_in_home is None or self._base_pose_ENU_in_home is None:
            self._base_pose_in_home = PoseStamped()
            self._base_pose_in_home.header.frame_id = self.ODOM_FRAME
            self._base_pose_flat_in_home = PoseStamped()
            self._base_pose_flat_in_home.header.frame_id = self.ODOM_FRAME
            self._base_pose_ENU_in_home = PoseStamped()
            self._base_pose_ENU_in_home.header.frame_id = self.ODOM_FRAME
            
        self._base_pose_in_home.pose.position.x = msg.position.x
        self._base_pose_in_home.pose.position.y = msg.position.y
        self._base_pose_in_home.pose.position.z = msg.position.z
        self._base_pose_in_home.header.stamp = self.now_stamp

        self._base_pose_flat_in_home.pose.position = self._base_pose_in_home.pose.position
        self._base_pose_flat_in_home.header.stamp = self._base_pose_in_home.header.stamp
        self._base_pose_ENU_in_home.pose.position = self._base_pose_in_home.pose.position
        self._base_pose_ENU_in_home.header.stamp = self._base_pose_in_home.header.stamp
        

    def _attitude_callback(self, msg: QuaternionStamped):
        # the attitude is in ENU by psdk definition, so we need to convert it to NED (compasses use this...)
        # and the use the z component as heading
        if self._base_pose_in_home is None or self._base_pose_flat_in_home is None or self._base_pose_ENU_in_home is None:
            self._base_pose_in_home = PoseStamped()
            self._base_pose_in_home.header.frame_id = self.ODOM_FRAME
            self._base_pose_flat_in_home = PoseStamped()
            self._base_pose_flat_in_home.header.frame_id = self.ODOM_FRAME
            self._base_pose_ENU_in_home = PoseStamped()
            self._base_pose_ENU_in_home.header.frame_id = self.ODOM_FRAME

        rpy_enu = euler_from_quaternion([msg.quaternion.x, msg.quaternion.y, msg.quaternion.z, msg.quaternion.w])
        self._heading_deg = 90 - math.degrees(rpy_enu[2])
        self._base_pose_in_home.pose.orientation = msg.quaternion

        flat_quat = Quaternion()
        flat_quat.x, flat_quat.y, flat_quat.z, flat_quat.w = quaternion_from_euler(0, 0, rpy_enu[2])
        self._base_pose_flat_in_home.pose.orientation = flat_quat
        ENU_quat = Quaternion()
        ENU_quat.x, ENU_quat.y, ENU_quat.z, ENU_quat.w = quaternion_from_euler(0, 0, 0)
        self._base_pose_ENU_in_home.pose.orientation = ENU_quat


        

    def _home_point_callback(self, msg: NavSatFix):
        if self._home_point_in_utm is None:
            self._home_point_in_utm = PointStamped()
            self._home_point_in_utm.header.frame_id = self.UTM_FRAME
            self.log("Home point initialized in UTM.")

        gp = GeoPoint()
        gp.latitude = math.degrees(msg.latitude) # for some reason these are in radians...
        gp.longitude = math.degrees(msg.longitude)
        gp.altitude = msg.altitude
        utm = convert_latlon_to_utm(gp)
        self._home_point_in_utm.point.x = utm.point.x
        self._home_point_in_utm.point.y = utm.point.y
        self._home_point_in_utm.point.z = 0.0
        self._home_point_in_utm.header.stamp = self.now_stamp

    def _home_point_altitude_callback(self, msg: Float32):
        if self._home_point_in_utm is None:
            self.log("home point in utm not set, can't set _home_geo_altitude")
            return
        self._home_geo_altitude = msg.data


    def _gps_callback(self, msg: NavSatFix):
        if self._geo_altitude is None or self._home_point_in_utm is None or self._home_geo_altitude is None:
            self.log(f"Geo Altitude({self._geo_altitude is not None}) or Home({self._home_point_in_utm is not None}) or home geo altitude({self._home_geo_altitude is not None}) not set, cannot process GPS message.")
            return
        
        if self._gps_point_in_home is None:
            self._gps_point_in_home = PointStamped()
            self._gps_point_in_home.header.frame_id = self.ODOM_FRAME
        # self.log(f"GPS Time: {msg.header.stamp}")
        gp = GeoPoint()
        gp.latitude = msg.latitude
        gp.longitude = msg.longitude
        gp.altitude = msg.altitude
        utm = convert_latlon_to_utm(gp)
        self._gps_point_in_home.point.x = utm.point.x - self._home_point_in_utm.point.x
        self._gps_point_in_home.point.y = utm.point.y - self._home_point_in_utm.point.y
        self._gps_point_in_home.point.z = self._geo_altitude - self._home_geo_altitude
        self._gps_point_in_home.header.stamp = self.now_stamp

        if self._utm_labeled_frame is None:
            self._utm_labeled_frame = utm.header.frame_id
            self.log(f"Setting UTM labeled frame to: {self._utm_labeled_frame}")


    def _rtk_cb(self, msg: NavSatFix):
        if self._geo_altitude is None or self._home_point_in_utm is None or self._home_geo_altitude is None:
            self.log(f"Geo Altitude({self._geo_altitude is not None}) or Home({self._home_point_in_utm is not None}) or home geo altitude({self._home_geo_altitude is not None}) not set, cannot process GPS message.")
            return
        
        if self._rtk_point_in_home is None:
            self._rtk_point_in_home = PointStamped()
            self._rtk_point_in_home.header.frame_id = self.ODOM_FRAME

        gp = GeoPoint()
        gp.latitude = msg.latitude
        gp.longitude = msg.longitude
        gp.altitude = msg.altitude
        utm = convert_latlon_to_utm(gp)
        self._rtk_point_in_home.point.x = utm.point.x - self._home_point_in_utm.point.x
        self._rtk_point_in_home.point.y = utm.point.y - self._home_point_in_utm.point.y
        self._rtk_point_in_home.point.z = self._geo_altitude - self._home_geo_altitude
        self._rtk_point_in_home.header.stamp = self.now_stamp

        
    def _publish_vehicle_health(self):
        self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_WAITING
        
        if self._base_pose_in_home is None or self._home_point_in_utm is None or self._gps_point_in_home is None or self._esc_data is None:
            self._vehicle_health_pub.publish(self._vehicle_health)
            return

        position_ok = self._home_point_in_utm is not None and self._base_pose_in_home is not None
        gps_ok = self._gps_point_in_home is not None and self._home_point_in_utm is not None
        battery_ok = self._battery_percent is not None and self._battery_percent > self.READY_BATTERY_PERCENTAGE
        height_ok = self._base_pose_in_home.pose.position.z > self.READY_HEIGHT_ABOVE_GROUND
        control_ok = self._got_control

        if all([position_ok, gps_ok, battery_ok, height_ok, control_ok]):
            self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_READY


        # collect all the rpms and currents into lists
        #TODO use the currents/speed to determine if we are carrying a payload eventually.
        speeds = [esc.speed for esc in list(self._esc_data.esc)[:self.NUM_PROPS]]
        # currents = [esc.current for esc in list(self._esc_data.esc)[:self.NUM_PROPS]]
        # check if all of the rpms are above the idle rpm
        speeds_flying = all(rpm > self.ESC_IDLE_RPM for rpm in speeds)
        self._flying = speeds_flying and height_ok



        if self._flying:
            battery_error = self._battery_percent is not None and self._battery_percent < self.ERROR_BATTERY_PERCENTAGE

            if battery_error:
                self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_ERROR
                self.log(f"BATTERY BELOW LIMIT: {self._battery_percent:.2f} < {self.ERROR_BATTERY_PERCENTAGE:.2f}")


        self._vehicle_health_pub.publish(self._vehicle_health)
            
    
    def _publish_tf(self):
        tf_msg = TFMessage()
        tf_msg.transforms = []
        now = self.now_stamp

        self._tf_pub_status = f"Published at {now.sec}.{now.nanosec} sec"

        # 0 transforms for home -> map, home -> odom, utm_z_b -> utm
        # for compatibility with other systems
        # and so we can use "odom" for all things that relate to home point
        map_in_home = TransformStamped()
        map_in_home.header.stamp = now
        map_in_home.header.frame_id = self.HOME_FRAME
        map_in_home.child_frame_id = self.MAP_FRAME
        tf_msg.transforms.append(map_in_home)

        odom_in_home = TransformStamped()
        odom_in_home.header.stamp = now
        odom_in_home.header.frame_id = self.HOME_FRAME
        odom_in_home.child_frame_id = self.ODOM_FRAME
        tf_msg.transforms.append(odom_in_home)

        if self._utm_labeled_frame is not None:
            utms = TransformStamped()
            utms.header.stamp = now
            utms.header.frame_id = self._utm_labeled_frame
            utms.child_frame_id = self.UTM_FRAME
            tf_msg.transforms.append(utms)

        if self._home_point_in_utm is not None:
            # Home point in UTM
            home_tf = TransformStamped()
            home_tf.header.stamp = now
            home_tf.header.frame_id = self.UTM_FRAME
            home_tf.child_frame_id = self.HOME_FRAME
            home_tf.transform.translation.x = self._home_point_in_utm.point.x
            home_tf.transform.translation.y = self._home_point_in_utm.point.y
            home_tf.transform.translation.z = self._home_point_in_utm.point.z
            tf_msg.transforms.append(home_tf)


        if self._base_pose_in_home is not None:
            # Base in odom
            base_in_home = TransformStamped()
            base_in_home.header.stamp = now
            base_in_home.header.frame_id = self.ODOM_FRAME
            base_in_home.child_frame_id = self.BASE_FRAME
            base_in_home.transform.rotation = self._base_pose_in_home.pose.orientation
            base_in_home.transform.translation.x = self._base_pose_in_home.pose.position.x
            base_in_home.transform.translation.y = self._base_pose_in_home.pose.position.y
            base_in_home.transform.translation.z = self._base_pose_in_home.pose.position.z
            tf_msg.transforms.append(base_in_home)


        if self._base_pose_flat_in_home is not None:
            # base flat in odom
            base_flat_in_home = TransformStamped()
            base_flat_in_home.header.stamp = now
            base_flat_in_home.header.frame_id = self.ODOM_FRAME
            base_flat_in_home.child_frame_id = self.BASE_FLAT_FRAME
            base_flat_in_home.transform.rotation = self._base_pose_flat_in_home.pose.orientation
            base_flat_in_home.transform.translation.x = self._base_pose_flat_in_home.pose.position.x
            base_flat_in_home.transform.translation.y = self._base_pose_flat_in_home.pose.position.y
            base_flat_in_home.transform.translation.z = self._base_pose_flat_in_home.pose.position.z
            tf_msg.transforms.append(base_flat_in_home)

        if self._base_pose_ENU_in_home is not None:
            # base ENU in odom
            base_ENU_in_home = TransformStamped()
            base_ENU_in_home.header.stamp = now
            base_ENU_in_home.header.frame_id = self.ODOM_FRAME
            base_ENU_in_home.child_frame_id = self.BASE_ENU_FRAME
            base_ENU_in_home.transform.rotation = self._base_pose_ENU_in_home.pose.orientation
            base_ENU_in_home.transform.translation.x = self._base_pose_ENU_in_home.pose.position.x
            base_ENU_in_home.transform.translation.y = self._base_pose_ENU_in_home.pose.position.y
            base_ENU_in_home.transform.translation.z = self._base_pose_ENU_in_home.pose.position.z
            tf_msg.transforms.append(base_ENU_in_home)


        if self._gps_point_in_home is not None:
            # GPS point in Home
            gps_tf = TransformStamped()
            gps_tf.header.stamp = now
            gps_tf.header.frame_id = self.ODOM_FRAME
            gps_tf.child_frame_id = self._TF_NS + "gps_point"
            gps_tf.transform.translation.x = self._gps_point_in_home.point.x
            gps_tf.transform.translation.y = self._gps_point_in_home.point.y
            gps_tf.transform.translation.z = self._gps_point_in_home.point.z
            tf_msg.transforms.append(gps_tf)


        # RTK point in odom
        if self._rtk_point_in_home is not None:
            rtk_tf = TransformStamped()
            rtk_tf.header.stamp = now
            rtk_tf.header.frame_id = self.ODOM_FRAME
            rtk_tf.child_frame_id = self._TF_NS + "rtk_point"
            rtk_tf.transform.translation.x = self._rtk_point_in_home.point.x
            rtk_tf.transform.translation.y = self._rtk_point_in_home.point.y
            rtk_tf.transform.translation.z = self._rtk_point_in_home.point.z
            rtk_tf.transform.rotation.w = 1.0
            tf_msg.transforms.append(rtk_tf)
        
        if self._move_to_setpoint is not None:
            move_to_setpoint_tf = TransformStamped()
            move_to_setpoint_tf.header.stamp = now
            move_to_setpoint_tf.header.frame_id = self._move_to_setpoint.header.frame_id
            move_to_setpoint_tf.child_frame_id = self._TF_NS + "move_to_setpoint"
            move_to_setpoint_tf.transform.translation.x = self._move_to_setpoint.pose.position.x
            move_to_setpoint_tf.transform.translation.y = self._move_to_setpoint.pose.position.y
            move_to_setpoint_tf.transform.translation.z = self._move_to_setpoint.pose.position.z
            tf_msg.transforms.append(move_to_setpoint_tf)

        self._tf_pub.publish(tf_msg)

    def _publish_smarc(self):
        if self._base_pose_in_home is None or self._home_point_in_utm is None or self._gps_point_in_home is None:
            return
        
        self._smarc_pub_status = f"Published at {self.now_stamp.sec}.{self.now_stamp.nanosec} sec"

        odom = Odometry()
        odom.header.stamp = self.now_stamp
        odom.header.frame_id = self.ODOM_FRAME
        odom.child_frame_id = self.BASE_FRAME

        odom.pose.pose.position.x = self._base_pose_in_home.pose.position.x
        odom.pose.pose.position.y = self._base_pose_in_home.pose.position.y
        odom.pose.pose.position.z = self._base_pose_in_home.pose.position.z
        odom.pose.pose.orientation = self._base_pose_in_home.pose.orientation

        if self._velocity_ground is not None:
            odom.twist.twist.linear.x = self._velocity_ground.vector.x
            odom.twist.twist.linear.y = self._velocity_ground.vector.y
            odom.twist.twist.linear.z = self._velocity_ground.vector.z

        if self._angular_rate_ground is not None:
            odom.twist.twist.angular.x = self._angular_rate_ground.vector.x
            odom.twist.twist.angular.y = self._angular_rate_ground.vector.y
            odom.twist.twist.angular.z = self._angular_rate_ground.vector.z

        self._odom_pub.publish(odom)

        # we need current position in latlon
        # so we first need to convert our odom-frame position to UTM
        if self._home_point_in_utm is None or self._base_pose_in_home is None or self._home_geo_altitude is None:
            self.log("Home point or base pose not set, cannot publish latlon position.")
            return
        base_in_utm = PointStamped()
        base_in_utm.header.frame_id = self._utm_labeled_frame
        base_in_utm.point.x = self._base_pose_in_home.pose.position.x + self._home_point_in_utm.point.x
        base_in_utm.point.y = self._base_pose_in_home.pose.position.y + self._home_point_in_utm.point.y
        base_in_geopoint = convert_utm_to_latlon(base_in_utm)
        base_in_geopoint.altitude = self._base_pose_in_home.pose.position.z
        self._pos_latlon_pub.publish(base_in_geopoint)
        self._altitude_pub.publish(Float32(data=self._base_pose_in_home.pose.position.z))


        if self._heading_deg is not None:
            self._heading_pub.publish(Float32(data=self._heading_deg))

        if self._course_deg is not None:
            self._course_pub.publish(Float32(data=self._course_deg))

        if self._velocity_ground is not None:
            speed = math.sqrt(
                self._velocity_ground.vector.x ** 2 +
                self._velocity_ground.vector.y ** 2
            )
            self._speed_pub.publish(Float32(data=speed))

        if self._battery_percent is not None:
            self._battery_percent_pub.publish(Float32(data=self._battery_percent))
                        
        

def format_point_stamped(point: PointStamped|None) -> str:
        if( point is None):
            return "None"
        return f"(x={point.point.x:.3f}, y={point.point.y:.3f}, z={point.point.z:.3f}, frame_id={point.header.frame_id})"

def format_pose_stamped(pose: PoseStamped|None) -> str:
        if( pose is None):
            return "None"
        rpy = euler_from_quaternion([
            pose.pose.orientation.x,
            pose.pose.orientation.y,
            pose.pose.orientation.z,
            pose.pose.orientation.w
        ])
        return f"(x={pose.pose.position.x:.3f}, y={pose.pose.position.y:.3f}, z={pose.pose.position.z:.3f}, " \
               f"roll={math.degrees(rpy[0]):.3f}, pitch={math.degrees(rpy[1]):.3f}, yaw={math.degrees(rpy[2]):.3f}, " \
               f"frame_id={pose.header.frame_id})"
        
def format_vector3_stamped(vec: Vector3Stamped|None) -> str:
        if( vec is None):
            return "None"
        return f"(x={vec.vector.x:.3f}, y={vec.vector.y:.3f}, z={vec.vector.z:.3f}, frame_id={vec.header.frame_id})"
    
    
def main():
    rclpy.init(args=sys.argv)
    node = Node("DjiCaptainNode")
    capt = DjiCaptain(node)

    
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()
