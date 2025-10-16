#!/usr/bin/python3

import rclpy, sys, math, time
import numpy as np
from enum import Enum


from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.time import Time, Duration
from rclpy.timer import Timer
from tf2_ros import Buffer, TransformListener


from std_msgs.msg import Float32, Int8, String
from std_srvs.srv import Trigger
from sensor_msgs.msg import NavSatFix, Joy, BatteryState, JoyFeedback
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TwistStamped, Pose, PoseStamped, TransformStamped, QuaternionStamped, PointStamped, Vector3Stamped, Quaternion
from geographic_msgs.msg import GeoPoint
from tf2_msgs.msg import TFMessage

from psdk_interfaces.msg import PositionFused, ControlMode, EscData, EscStatusIndividual
from smarc_msgs.msg import Topics as SmarcTopics
from dji_msgs.msg import Links as DjiLinks
from dji_msgs.msg import Topics as DjiTopics


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
    VELOCITY_GROUND_FSD  = WRAPPER_NS + "velocity_ground_fused"
    ANGULAR_RATE_GND_FSD= WRAPPER_NS + "angular_rate_ground_fused"
    ESC_DATA            = WRAPPER_NS + "esc_data"
    RC                  = WRAPPER_NS + "rc"

    TAKE_CONTROL_SRV    = WRAPPER_NS + "obtain_ctrl_authority"
    RELEASE_CONTROL_SRV = WRAPPER_NS + "release_ctrl_authority"
    TAKEOFF_SRV         = WRAPPER_NS + "takeoff"
    LAND_SRV            = WRAPPER_NS + "land"

    FLUvel_JOY          = WRAPPER_NS + "flight_control_setpoint_FLUvelocity_yawrate"
    ENUvel_JOY          = WRAPPER_NS + "flight_control_setpoint_ENUvelocity_yawrate"
    ENUpos_JOY          = WRAPPER_NS + "flight_control_setpoint_ENUposition_yaw"    



class ControlModes(Enum):
    FLUvel = "FLU Velocity"
    ENUvel = "ENU Velocity"
    ENUpos = "ENU Position"


class DjiCaptain():
    def __init__(self, node: Node):
        self._prev_log_msg = ""
        self._node = node


        try:
            self._RUNNING_IN_SIM : bool = self._node.get_parameter("use_sim_time").get_parameter_value().bool_value
        except:
            self._RUNNING_IN_SIM : bool = False

        # Velocity controller parameters
        #Tuning: For large movements, k_pose will have essentially no impact on the startup. r_sigma dominates in this range, with a larger r_sigma producing a smoother 
        #start and a smaller r_sigma producing a faster start. When stopping, both variables matter. A larger r_sigma will produce more overshoot in the target position.
        #A smaller k_pose will cause this to behave more like a normal proportional controller, reducing overshoot by making the deceleration happen over a greater 
        #distance. A larger k_pose will decrease the time spent decelerating, which could either increase or decrease overshoot, depending on how large it is. The best 
        #choice for these values is also dependent on JOY_PUB_MAX and even more so on JOY_PUB_PERIOD, so make sure to be very careful and retune after adjusting these.

        if self._RUNNING_IN_SIM:
            self._k_pose = .4
            self._r_sigma = 0.8
        else:
            # these are tested and liked for the real M350 as of writing this (Oct 1st, 2025)
            self._k_pose = .5 #proportional gain
            self._r_sigma = .9 #"gain" on previous output, between 0 and 1 (kind of, the "desired output" is multiplied by 1 - r_sigma and the previous output is multiplied by r_sigma).


        self._node.declare_parameter("robot_name", "M350")
        self._node.declare_parameter("controller_deadzone", 0.1)
        self._node.declare_parameter("controller_yawrate_multiplier", 0.3)
        # give an error-causing default value to force the user to pass this parameter every time
        # there is no safe assumption that can be made for this.
        self._node.declare_parameter("home_altitude_above_water", -1.0)

        self.ROBOT_NAME : str = self._node.get_parameter("robot_name").get_parameter_value().string_value
        self._TF_NS : str = f"{self.ROBOT_NAME}/"

        self._CONTROLLER_DEADZONE : float = self._node.get_parameter("controller_deadzone").get_parameter_value().double_value
        self._CONTROLLER_YAWRATE_MULTIPLIER : float = self._node.get_parameter("controller_yawrate_multiplier").get_parameter_value().double_value
        
        self._HOME_ALT_ABOVE_WATER = self._node.get_parameter("home_altitude_above_water").get_parameter_value().double_value

        if self._HOME_ALT_ABOVE_WATER <= 0:
            self.log(f"Warning: home_altitude_above_water parameter not set or invalid! It is {self._HOME_ALT_ABOVE_WATER}")
            self.log("YOU MUST PASS THIS PARAMETER AND MAKE SURE IT IS CORRECT!")
            self.log("Captain will not run. Exiting.")
            sys.exit(1)

        
        
        self._control_mode = ControlModes.FLUvel
        self._move_to_setpoint : PoseStamped | None = None
        self._joy_timer : None | Timer = None
        self._FLU_vel_joy_pub = node.create_publisher(Joy, PSDKTopics.FLUvel_JOY.value, qos_profile=10)
        self._ENU_vel_joy_pub = node.create_publisher(Joy, PSDKTopics.ENUvel_JOY.value, qos_profile=10)
        self._ENU_pos_joy_pub = node.create_publisher(Joy, PSDKTopics.ENUpos_JOY.value, qos_profile=10)
        
        self.MOVE_TO_SETPOINT_MAX_AGE : float = 1.0 #Usually .5, set to 1 for sim testing seconds, how long we keep the move to setpoint before we consider it stale
        self._MAX_SETPOINT_DISTANCE : float = 50.0 # meters, max distance from current position to accept a move to setpoint
        self.JOY_PUB_MAX = 1.5
        self.JOY_PUB_PERIOD = .1

        self._prev_joy_output : None | np.ndarray = None

        self.READY_BATTERY_PERCENTAGE = 25
        self.READY_HEIGHT_ABOVE_GROUND = 2
        self.ERROR_BATTERY_PERCENTAGE = 15
        self.ERROR_HEIGHT_ABOVE_GROUND = 1
        
        # this is the idle RPM/current for the ESCs, below this we consider the vehicle not flying
        self.NUM_PROPS = 4 # because the esc message always has 8 fields...
        self.ESC_IDLE_RPM = 1000  


        self.ODOM_FRAME = self._TF_NS + DjiLinks.ODOM
        self.MAP_FRAME = self._TF_NS + DjiLinks.MAP
        self.BASE_FRAME = self._TF_NS + DjiLinks.BASE_LINK
        self.BASE_FLAT_FRAME = self._TF_NS + DjiLinks.BASE_FLAT
        self.BASE_ENU_FRAME = self._TF_NS + DjiLinks.BASE_ENU
        self.HOME_FRAME = self._TF_NS + DjiLinks.HOME_POINT
        self._utm_labeled_frame : str | None = None
        self.GIMBAL_FRAME = self._TF_NS + DjiLinks.GIMBAL_CAMERA_LINK
        self.WINCH_FRAME = self._TF_NS + DjiLinks.WINCH_LINK


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
        
        # this could be a param, but really we likely will never run this on anything except
        # the M350 which has a nominal 3kg max payload, so hardcoding it here is fine.
        # I set it to 4kg to have some momentary overshoot margins due to motion etc.
        self._MAX_LOAD_KG : float = 4.0 # kg, max payload we consider safe to carry
        self._load_cell_weight : float | None = None



        topics = [PSDKTopics.__dict__[t].value for t in PSDKTopics.__members__.keys()]
        topics = [self.ROBOT_NAME + "/" + PSDKTopics.__dict__[t].value for t in PSDKTopics.__members__.keys()]
        self.log(f"Subscribed to PSDK topics: --topics {' '.join(topics)}")
       

        self._tf_pub = node.create_publisher(TFMessage,"/tf",qos_profile=10)
        self._tf_timer = node.create_timer(0.01, self._publish_tf)

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

        self._labeled_utm_frame_pub = node.create_publisher(String, DjiTopics.LABELED_UTM_TOPIC, qos_profile=10)

        # a simple TTS node should be listening to this (robot_name/speak)
        self._speak_pub = node.create_publisher(String, DjiTopics.TTS_TOPIC, qos_profile=10)
        self._controller_vibrator_pub = node.create_publisher(JoyFeedback, DjiTopics.CONTROLLER_VIBRATION_TOPIC, qos_profile=10)
        

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
            PSDKTopics.VELOCITY_GROUND_FSD.value,
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
            self._dji_rc_cb,
            qos_profile=10)
        
        node.create_subscription(
            Joy,
            DjiTopics.CONTROLLER_INPUT_TOPIC,
            self._controller_callback,
            qos_profile=10)

        node.create_subscription(
            PoseStamped,
            DjiTopics.MOVE_TO_SETPOINT_TOPIC,
            self._move_to_setpoint_callback,
            qos_profile=10)
        
        node.create_subscription(
            Float32,
            DjiTopics.LOAD_CELL_WEIGHT_TOPIC,
            self._load_cell_callback,
            qos_profile=10)
        

        
        # services to take and give-up control + take-off and land
        # call service: obtain/release_ctrl_authority
        self._take_control_srv = node.create_client(Trigger, PSDKTopics.TAKE_CONTROL_SRV.value)
        self._release_control_srv = node.create_client(Trigger, PSDKTopics.RELEASE_CONTROL_SRV.value)
        self._takeoff_srv = node.create_client(Trigger, PSDKTopics.TAKEOFF_SRV.value)
        self._land_srv = node.create_client(Trigger, PSDKTopics.LAND_SRV.value)


        while rclpy.ok():
            commands = "Commands:\n"
            commands += "  1: Take control  \n"
            commands += "  2: Release control\n"
            commands += "  3: Take off\n"
            commands += "  4: Land\n"
            commands += f"\n  8: Print status (also available on {self._TF_NS}captain_status topic) \n"
            commands += "  9: Set max joy to (DANGEROUS, DONT USE UNLESS YOUR NAME STARTS WITH O)\n"
            commands += "  0: EXIT \n"
            try:
                self.log(commands)
                n = int(input("Enter number for command: \n"))
                if n == 1: #Take control
                    self._take_control()
                elif n == 2: #Release control
                    self._release_control()
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
                elif n == 8: #Print status
                    self.log(self.status_str)
                elif n == 9: # set max joy
                    self.JOY_PUB_MAX = float(input("Enter new max joy value: ") or "0")
                    self.log(f"Set max joy to {self.JOY_PUB_MAX:.2f} (m/s)")
                elif n == 0:
                    try:
                        self.log("Exiting captain")
                        self._speak("Bye bye.")
                    except:
                        print("Exiting captain.")
                    break

            except:
                self.log(f"Invalid input:{input}, please enter a number.")
                continue
            
        


    @property
    def now_stamp(self):
        return self._node.get_clock().now().to_msg()
    
    @property
    def now_time(self):
        return self.now_stamp.sec + self.now_stamp.nanosec * 1e-9
    
    @property
    def setpoint_received_at(self) -> float|None:
        return self._move_to_setpoint.header.stamp.sec + self._move_to_setpoint.header.stamp.nanosec * 1e-9 if self._move_to_setpoint is not None else None
    
    
    @property
    def status_str(self) -> str:
        s = "\nDjiCaptain Status:\n"
        s += f"  Home in UTM: {format_point_stamped(self._home_point_in_utm)} ({self._utm_labeled_frame})\n"
        s += f"\n  Position in Home: {format_pose_stamped(self._base_pose_in_home)}\n"
        
        if self._battery_percent is not None:
            s += f"  Battery Percent: {self._battery_percent:.2f} (ready:{self.READY_BATTERY_PERCENTAGE}, error:{self.ERROR_BATTERY_PERCENTAGE})\n"
        else:
            s += f"  Battery Percent: N/A\n"
        
        if self._load_cell_weight is not None:
            s += f"  Load Cell Weight: {self._load_cell_weight:.2f} kg (max: {self._MAX_LOAD_KG} kg)\n"
        else:
            s += f"  Load Cell Weight: N/A\n"
        
        if self._base_pose_in_home is not None:
            s += f"  Altitude from water: {self._base_pose_in_home.pose.position.z + self._HOME_ALT_ABOVE_WATER:.2f} m\n"
        else:
            s += f"  Altitude from water: N/A, base pose in home not known!\n"

        if self._heading_deg is not None: s += f"  Heading: {self._heading_deg:.2f}\n"
        else: s += f"  Heading: N/A\n"

        if self._course_deg is not None: s += f"  Course: {self._course_deg:.2f}\n"
        else: s += f"  Course: N/A\n"

        s += f"  Velocity Ground: {format_vector3_stamped(self._velocity_ground)}\n"
        s += f"  Angular Rate Ground: {format_vector3_stamped(self._angular_rate_ground)}\n"
        
        s += f"\n  Smarc Topics: {self._smarc_pub_status}\n"
        s += f"  TF: {self._tf_pub_status}\n"

        s += f"\n  Got Control: {self._got_control}\n"
        s += f"  Control Mode: {self._control_mode.value}\n"
        if self.setpoint_received_at is None and self._move_to_setpoint is None:
            s += f"  No setpoint set.\n"
        elif self.setpoint_received_at is None and self._move_to_setpoint is not None:
            s += f"  Setpoint received time unknown, this is a bug! FIX THIS\n"
        elif self.setpoint_received_at is not None and self._move_to_setpoint is not None:
            s += f"  Current target setpoint: {format_pose_stamped(self._move_to_setpoint)} ({self.now_time - self.setpoint_received_at:.2f}s ago)\n"
        s += f"  Flying: {self._flying}\n"

        if self._vehicle_health.data == SmarcTopics.VEHICLE_HEALTH_READY:
            s += f"  Vehicle Health: READY\n"
        elif self._vehicle_health.data == SmarcTopics.VEHICLE_HEALTH_ERROR:
            s += f"  Vehicle Health: ERROR\n"
        else:
            s += f"  Vehicle Health: WAITING\n"

        return s
    
    
    def log(self, msg: str):
        if msg == self._prev_log_msg:
            return
        self._node.get_logger().info(msg)
        self._prev_log_msg = msg


    def _take_control(self):
        def on_result(f):
            self.log(f"Take control service called, success: {f.result().success}, message: {f.result().message}")
            if f.result().success:
                self._speak("Got control.")
            else:
                self._speak("Failed to get control.")

        self.log("Taking control.")
        self._speak("Taking control.")
        if not self._take_control_srv.wait_for_service(timeout_sec=5.0):
            self.log("Take control service not available...")
            self._speak("Take control service not available.")
            return
        future = self._take_control_srv.call_async(Trigger.Request())
        future.add_done_callback(on_result)


    def _release_control(self):
        def on_result(f):
            self.log(f"Release control service called, success: {f.result().success}, message: {f.result().message}")
            if f.result().success:
                self._speak("Gave up control.")
            else:
                self._speak("Failed to release control.")

        self.log("Releasing control.")
        self._speak("Releasing control.")
        if not self._release_control_srv.wait_for_service(timeout_sec=5.0):
            self.log("Release control service not available...")
            self._speak("Release control service not available.")
            return
        future = self._release_control_srv.call_async(Trigger.Request())
        future.add_done_callback(on_result)


    def _geo_alt_cb(self, msg: Float32):
        self._geo_altitude = msg.data

    def _load_cell_callback(self, msg: Float32):
        self._load_cell_weight = msg.data


    def _move_to_setpoint_callback(self, msg: PoseStamped):
        # check if the message even has anything in it
        if msg.pose.position.x == 0 and msg.pose.position.y == 0 and msg.pose.position.z == 0:
            self.log(f"Move to setpoint message is all zeros, ignoring it.\nSetpoint msg:\n{msg}")
            self._move_to_setpoint = None
            return
        
        msg_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        
        # check if message time makes sense. sim time vs real time etc
        if msg_time > self.now_time + 2.0:
            s = f"Move to setpoint message time is >2s in the future, ignoring it. Probably because the publisher and captain have different time sources."
            s += f"\nCurrent time: {self.now_time}\nSetpoint Time: {msg_time}"
            self.log(s)
            self._move_to_setpoint = None
            return
        
        # check if the message is too old
        if self.now_time - msg_time > self.MOVE_TO_SETPOINT_MAX_AGE:
            s = f"Move to setpoint message is older than {self.MOVE_TO_SETPOINT_MAX_AGE}s, ignoring it."
            s += f"\nCurrent time: {self.now_time}\nSetpoint Time: {msg_time}"
            self.log(s)
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
                s = f"Could not transform move to setpoint from {msg.header.frame_id} to {self.ODOM_FRAME}: {e}"
                s+= f"\nIgnoring this setpoint:\n{msg}"
                self.log(s)
                self._move_to_setpoint = None
                return
        else:
            self._move_to_setpoint = msg


        # At this point, the setpoint is in ODOM=HOME frame.

        # Check if the new setpoint is the same as the current one
        if self._move_to_setpoint is not None:
            curr = self._move_to_setpoint.pose.position
            new = msg.pose.position
            if abs(curr.x - new.x) > 1e-6 and \
               abs(curr.y - new.y) > 1e-6 and \
               abs(curr.z - new.z) > 1e-6:
                self.log(f"New move to setpoint received: {format_pose_stamped(msg)}")

        # Check if it is too far
        if self._base_pose_in_home is not None and self._move_to_setpoint is not None:
            dx = self._move_to_setpoint.pose.position.x - self._base_pose_in_home.pose.position.x
            dy = self._move_to_setpoint.pose.position.y - self._base_pose_in_home.pose.position.y
            dz = self._move_to_setpoint.pose.position.z - self._base_pose_in_home.pose.position.z
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist > self._MAX_SETPOINT_DISTANCE:
                self.log(f"Move to setpoint is too far away ({dist:.1f}m), ignoring it.")
                self._speak("Setpoint too far away, ignoring it.")
                self._move_to_setpoint = None
                return

        # self.log(f"Move to setpoint received: {format_pose_stamped(self._move_to_setpoint)}")
        
        if self._joy_timer is None:
            if self._control_mode == ControlModes.FLUvel:
                self._joy_timer = self._node.create_timer(self.JOY_PUB_PERIOD, self._move_towards_setpoint_FLUvel)
            elif self._control_mode == ControlModes.ENUvel:
                self._joy_timer = self._node.create_timer(self.JOY_PUB_PERIOD, self._move_towards_setpoint_ENUvel)
            elif self._control_mode == ControlModes.ENUpos:
                self._joy_timer = self._node.create_timer(self.JOY_PUB_PERIOD, self._move_towards_setpoint_ENUpos)

            self.log("Joy timer started to move with joy.")


    def _buzz(self, intensity: float = 1.0):
        self._controller_vibrator_pub.publish(JoyFeedback(
                type=JoyFeedback.TYPE_RUMBLE,
                id=0,
                intensity=intensity))
        
    def _speak(self, msg: str):
        self._speak_pub.publish(String(data=msg))

    def _controller_callback(self, msg: Joy):
        if msg.header.stamp.sec == 0 and msg.header.stamp.nanosec == 0:
            # malformed...
            return
        
        now = self.now_stamp
        # Check if the message is older than 0.1 seconds
        msg_age = (now.sec - msg.header.stamp.sec) + (now.nanosec - msg.header.stamp.nanosec) * 1e-9
        if msg_age > 0.1:
            self.log(f"Controller message is older than 0.1s ({msg_age:.3f}s), ignoring.")
            return


        # right stick = horizontal movement, left stick = vertical movement + yaw
        # like the DJI RC controller
        LH = msg.axes[0]  # left stick horizontal
        LV = msg.axes[1]  # left stick vertical
        RH = msg.axes[2]  # right stick horizontal
        RV = msg.axes[3]  # right stick vertical
        L2:float = msg.axes[4]  # L2 button 
        R2:float = msg.axes[5]  # R2 button
        south = msg.buttons[0]  # south button
        east = msg.buttons[1]   # east button
        west = msg.buttons[2]   # west button
        north = msg.buttons[3]  # north button
        select = msg.buttons[4] # select button
        ps_button = msg.buttons[5]  # PS button
        start = msg.buttons[6]  # start button
        left_stick_in = msg.buttons[7]  # left stick in
        right_stick_in = msg.buttons[8]  # right stick in
        L1 = msg.buttons[9]  # L1 button
        R1 = msg.buttons[10]  # R1 button
        up = msg.buttons[11]  # up button
        down = msg.buttons[12]  # down button
        left = msg.buttons[13]  # left button
        right = msg.buttons[14]  # right button

        sticks_pushed = any(
            [
                abs(LH) > self._CONTROLLER_DEADZONE,
                abs(LV) > self._CONTROLLER_DEADZONE,
                abs(RH) > self._CONTROLLER_DEADZONE,
                abs(RV) > self._CONTROLLER_DEADZONE
            ]
        )

        if not self._got_control:
            if start == 1 and ps_button == 1:
                self._take_control()
                return
            
            if sticks_pushed:
                self.log("Sticks pushed without control!")
                self._speak("You must first take control with the PS button and Start button.")
                self._buzz()
                return
            
        if self._move_to_setpoint is not None:
            if sticks_pushed:
                self.log("Sticks pushed, cancelling move to setpoint.")
                self._speak("Move to setpoint cancelled because you touched the controller sticks!")
                self._cancel_joy_timer()                
        

        if up:
            self.JOY_PUB_MAX += 0.2
            if self.JOY_PUB_MAX > 5.0:
                self.JOY_PUB_MAX = 5.0
            self.log(f"Joy max increased to {self.JOY_PUB_MAX:.2f} (m/s)")
            self._speak(f"Joy max {self.JOY_PUB_MAX:.1f}")
        if down:
            self.JOY_PUB_MAX -= 0.2
            if self.JOY_PUB_MAX < 0.0:
                self.JOY_PUB_MAX = 0.0
            self.log(f"Joy max decreased to {self.JOY_PUB_MAX:.2f} (m/s)")
            self._speak(f"Joy max {self.JOY_PUB_MAX:.1f}")


        control_modes = list(ControlModes)
        if left:
            self._control_mode = control_modes[(control_modes.index(self._control_mode) - 1) % len(control_modes)]
            self.log(f"Control mode changed to {self._control_mode.value}")
            self._speak(f"Control mode {self._control_mode.value}")
        if right:
            self._control_mode = control_modes[(control_modes.index(self._control_mode) + 1) % len(control_modes)]
            self.log(f"Control mode changed to {self._control_mode.value}")
            self._speak(f"Control mode {self._control_mode.value}")
        

            
        if self._got_control and sticks_pushed:
            joy_msg = Joy()
            joy_msg.header.stamp = self.now_stamp
            if self._control_mode == ControlModes.FLUvel:
                # DJI expects Axes: [forward, left, up, yawrate]
                joy_msg.axes = [RV, RH, LV, LH]
                self._FLU_vel_joy_pub.publish(joy_msg)

            elif self._control_mode == ControlModes.ENUvel:
                self.log("Moving with ENU velocity control mode, be careful! Right stick is real East/North!")
                # DJI expects Axes: [east, north, up, yawrate]
                joy_msg.axes = [RV, RH, LV, LH]
                self._ENU_vel_joy_pub.publish(joy_msg)

            elif self._control_mode == ControlModes.ENUpos:
                self.log("Moving with ENU position control mode, be careful! Right stick is real East/North!")
                if(self._heading_deg is None):
                    self.log("No heading set, cannot move with ENUpos control mode.")
                    return
                if(self._base_pose_flat_in_home is None):
                    self.log("No heading set, cannot move with ENUpos control mode.")
                    return
                if(LV is None or LH is None):
                    self.log("No left stick, cannot move with ENUpos control mode.")
                    return
                
                yaw = math.pi/2 - math.radians(self._heading_deg)
                yaw_move = yaw + LH * self._CONTROLLER_YAWRATE_MULTIPLIER
                altitude = self._base_pose_flat_in_home.pose.position.z
                joy_msg.axes = [RV, RH, altitude + LV, yaw_move]
                self._ENU_pos_joy_pub.publish(joy_msg)
                

        
        
    def _cancel_joy_timer(self):
        self._move_to_setpoint = None
        self._prev_joy_output = None
        self.log("Setpoint discarded.")
        if self._joy_timer is not None:
            self._joy_timer.cancel()
            self._joy_timer = None
            self.log("Joy timer cancelled.")

        # send a zero joy message to stop the vehicle
        zero_joy = Joy()
        zero_joy.header.stamp = self.now_stamp
        self._FLU_vel_joy_pub.publish(zero_joy)



    def _move_towards_setpoint_FLUvel(self):

        if self._move_to_setpoint is None or self.setpoint_received_at is None:
            self.log("No move to setpoint set, cannot move with joy.")
            self._cancel_joy_timer()
            return

        if self.now_time - self.setpoint_received_at > self.MOVE_TO_SETPOINT_MAX_AGE:
            self.log(f"Move to setpoint message is older than {self.MOVE_TO_SETPOINT_MAX_AGE}s, cancelling joy timer.")
            self._cancel_joy_timer()
            return
        
        if not self._got_control:
            self.log("Not got control, cannot move with joy.")
            self._cancel_joy_timer()
            return
        
        if(self._velocity_ground == None):
            self.log(f"Ground Velocity not defined, cancelling Joy")
            self._cancel_joy_timer()
            return
        
        tf = self._tf_buffer.lookup_transform(
            target_frame = self.BASE_FLAT_FRAME,
            source_frame = self._velocity_ground.header.frame_id,
            time=Time(seconds=0),
            timeout=Duration(seconds=1))
        
        vel_pose = PoseStamped()
        vel_pose.pose.position.x = self._velocity_ground.vector.x
        vel_pose.pose.position.y = self._velocity_ground.vector.y
        vel_pose.pose.position.z = self._velocity_ground.vector.z
        FLU_vel = do_transform_pose_stamped(vel_pose, tf)

        if (self._prev_joy_output is None):
            self._prev_joy_output = np.array([FLU_vel.pose.position.x, FLU_vel.pose.position.y, FLU_vel.pose.position.z])

        try:
            tf_diff = self._tf_buffer.lookup_transform(
                target_frame = self.BASE_FLAT_FRAME,
                source_frame = self._move_to_setpoint.header.frame_id,
                time=Time(seconds=0),
                timeout=Duration(seconds=1))
            target_in_base = do_transform_pose_stamped(self._move_to_setpoint, tf_diff)
        except Exception as e:
            self.log(f"Failed to transform move to setpoint from {self._move_to_setpoint.header.frame_id} to {self.BASE_FLAT_FRAME}, cancelling joy timer.: {e}")
            self._cancel_joy_timer()
            return
        
        
        k_pose = self._k_pose
        r_sigma = self._r_sigma

        e_forw = target_in_base.pose.position.x # error about each axis
        e_left = target_in_base.pose.position.y
        e_updn = target_in_base.pose.position.z # we like mirrors around a point

        joy_forw = k_pose * e_forw
        joy_left = k_pose * e_left
        joy_updn = k_pose * e_updn

        # limit the velocity to the maximum joy value
        joy_net = np.array([joy_forw, joy_left, joy_updn])
        joy_net = self._normalize_max_speed(joy_net)

        joy_net = (1 - r_sigma) * joy_net + r_sigma * self._prev_joy_output
        joy_net = self._normalize_max_speed(joy_net)

        joy_msg = Joy()
        joy_msg.header.stamp = self.now_stamp
        joy_msg.axes = [joy_net[0], joy_net[1], joy_net[2], 0.0]  # Axes: [forward, left, up/down, yaw]
        joy_msg.buttons = []

        self._FLU_vel_joy_pub.publish(joy_msg)
        self._prev_joy_output = np.array([joy_net[0], joy_net[1], joy_net[2]])

    def _normalize_max_speed(self, joy_net):
        joy_norm = np.linalg.norm(joy_net)
        if joy_norm > self.JOY_PUB_MAX:
            joy_net = joy_net / joy_norm * self.JOY_PUB_MAX
        return joy_net
    
    def _move_towards_setpoint_ENUpos(self):
        if self._move_to_setpoint is None or self.setpoint_received_at is None:
            self.log("No move to setpoint set, cannot move with joy.")
            self._cancel_joy_timer()
            return
        
        if(self._heading_deg is None):
            self.log("No heading set, cannot move with joy.")
            self._cancel_joy_timer()
            return
        
        if self.now_time - self.setpoint_received_at > self.MOVE_TO_SETPOINT_MAX_AGE:
            self.log(f"Move to setpoint message is older than {self.MOVE_TO_SETPOINT_MAX_AGE}s, cancelling joy timer.")
            self._move_to_setpoint = None
            self._cancel_joy_timer()
            return
        
        if not self._got_control:
            self.log("Not got control, cannot move with joy.")
            self._cancel_joy_timer()
            return
        
        try:
            tf_diff = self._tf_buffer.lookup_transform(
                target_frame = self.BASE_ENU_FRAME, #This is the frame centered on the baselink but locked to ENU rotationally
                source_frame = self._move_to_setpoint.header.frame_id,
                time=Time(seconds=0),
                timeout=Duration(seconds=1))
            target_in_base = do_transform_pose_stamped(self._move_to_setpoint, tf_diff)
        except Exception as e:
            self.log(f"Failed to transform move to setpoint from {self._move_to_setpoint.header.frame_id} to {self.BASE_FLAT_FRAME}, cancelling joy timer.: {e}")
            self._cancel_joy_timer()
            return
        
        try:
            tf = self._tf_buffer.lookup_transform(
                target_frame = self.ODOM_FRAME,
                source_frame = self._move_to_setpoint.header.frame_id,
                time=Time(seconds=0),
                timeout=Duration(seconds=1))
            target_in_odom = do_transform_pose_stamped(self._move_to_setpoint, tf)
        except Exception as e:
            self.log(f"Failed to transform move to setpoint from {self._move_to_setpoint.header.frame_id} to {self.ODOM_FRAME}, cancelling joy timer.: {e}")
            self._cancel_joy_timer()
            return
        e_east = target_in_base.pose.position.x # error about each axis
        e_north = target_in_base.pose.position.y
        target_updn = target_in_odom.pose.position.z #Should be "relative to the global Cartesian frame where the aircraft has been initialized." This is in the ODOM frame, which I think is correct?
        yaw = math.pi/2 - math.radians(self._heading_deg) #Should be the current yaw. Not 100% certain on this, but I think _heading_deg is in NED and needs to be in ENU. "The commanded yaw is assumed to be following REP 103, thus a FLU rotation wrt to ENU frame"

        joy_msg = Joy()
        joy_msg.header.stamp = self.now_stamp
        joy_msg.axes = [e_east, e_north, target_updn, yaw]  # Axes: [east offset, north offset, up/down position, yaw position] 
        joy_msg.buttons = []

        self._ENU_pos_joy_pub.publish(joy_msg)


    def _move_towards_setpoint_ENUvel(self):
        self.log("_move_towards_setpoint_ENUvel not implemented yet.")
        self._cancel_joy_timer()
    

    def _dji_rc_cb(self, msg: Joy):
        # if RC is touched by user, we give up control
        if not self._got_control: return

        if msg.axes[0] != 0.0 or msg.axes[1] != 0.0 or msg.axes[2] != 0.0 or msg.axes[3] != 0.0:
            self.log("RC touched, giving up control.")
            self._got_control = False # even if the service call fails, we assume we lost control!
            self._release_control_srv.call_async(Trigger.Request()).add_done_callback(
                lambda future: self.log(f"Release control service called, success: {future.result().success}, message: {future.result().message}")
            )
        
        # self.log(f"RC buttons: {msg.buttons}")


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
        just_got_control = msg.control_auth == 1 and msg.device_mode == 4
        if self._got_control == just_got_control:
            return
        
        if self._got_control and not just_got_control:
            self.log("Released control authority, stopping joy timer, discarding setpoint.")
            self._speak("Released control.")
            self._cancel_joy_timer()
            self._got_control = False

        elif not self._got_control and just_got_control:
            self.log("Gained control authority.")
            self._speak("Taken control.")
            self._got_control = True
        


    def _battery_callback(self, msg: BatteryState):
        self._battery_percent = msg.percentage*100
            

    def _position_fused_callback(self, msg: PositionFused):
        if self._home_point_in_utm is None:
            self.log("Home point not set, ignoring position fused until it is...")
            return
        
        if self._base_pose_in_home is None or self._base_pose_flat_in_home is None or self._base_pose_ENU_in_home is None:
            self._base_pose_in_home = PoseStamped()
            self._base_pose_in_home.header.frame_id = self.ODOM_FRAME
            self._base_pose_flat_in_home = PoseStamped()
            self._base_pose_flat_in_home.header.frame_id = self.ODOM_FRAME
            self._base_pose_ENU_in_home = PoseStamped()
            self._base_pose_ENU_in_home.header.frame_id = self.ODOM_FRAME
            self.log("Base pose initialized in home frame.")
            
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
        try:
            gp = GeoPoint()
            gp.latitude = math.degrees(msg.latitude) # for some reason these are in radians...
            gp.longitude = math.degrees(msg.longitude)
            gp.altitude = msg.altitude
            utm = convert_latlon_to_utm(gp)
        except Exception as e:
            self.log(f"Failed to convert home point to UTM: {e}")
            return

        if self._home_point_in_utm is None:
            self._home_point_in_utm = PointStamped()
            self._home_point_in_utm.header.frame_id = DjiLinks.UTM
            self.log("Home point initialized in UTM.")

        self._home_point_in_utm.point.x = utm.point.x
        self._home_point_in_utm.point.y = utm.point.y
        # we set the altitude of home point to a constant above water level
        # since almost everything we do is relative to the water level, and not geographical altitude
        # in sim, we can _know_ this altitude, but in real life we can't, so we take it as a param from
        # the user. 
        self._home_point_in_utm.point.z = self._HOME_ALT_ABOVE_WATER
        self._home_point_in_utm.header.stamp = self.now_stamp

    def _home_point_altitude_callback(self, msg: Float32):
        if self._home_point_in_utm is None:
            self.log("home point in utm not set, can't set _home_geo_altitude")
            return
        self._home_geo_altitude = msg.data


    def _gps_callback(self, msg: NavSatFix):
        if self._geo_altitude is None or self._home_point_in_utm is None or self._home_geo_altitude is None:
            self.log(f"Geo Altitude({self._geo_altitude is not None}) or Home({self._home_point_in_utm is not None}) or home geo altitude({self._home_geo_altitude is not None}) not set, cannot process GPS message yet.")
            return
        
        if self._gps_point_in_home is None:
            self._gps_point_in_home = PointStamped()
            self._gps_point_in_home.header.frame_id = self.ODOM_FRAME
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
        control_ok = self._got_control
        weight_ok = self._load_cell_weight is None or self._load_cell_weight < self._MAX_LOAD_KG

        if all([position_ok, gps_ok, battery_ok, control_ok, weight_ok]):
            self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_READY


        # collect all the rpms and currents into lists
        speeds = [esc.speed for esc in list(self._esc_data.esc)[:self.NUM_PROPS]]
        # currents = [esc.current for esc in list(self._esc_data.esc)[:self.NUM_PROPS]]
        # check if all of the rpms are above the idle rpm
        # we cant check position above home, because it is very possible that we launched high and flew down...
        self._flying = all(rpm > self.ESC_IDLE_RPM for rpm in speeds)


        if self._flying:
            battery_error = self._battery_percent is not None and self._battery_percent < self.ERROR_BATTERY_PERCENTAGE
            if battery_error:
                self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_ERROR
                self.log(f"BATTERY BELOW LIMIT: {self._battery_percent:.2f} < {self.ERROR_BATTERY_PERCENTAGE:.2f}")

            weight_error = self._load_cell_weight is not None and self._load_cell_weight > self._MAX_LOAD_KG
            if weight_error:
                self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_ERROR
                self.log(f"WEIGHT ABOVE LIMIT: {self._load_cell_weight:.2f} > {self._MAX_LOAD_KG:.2f}")


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

        # 0-transform for base_link -> gimbal_camera_link as well, for now
        # until we have a better idea of where the gimbal is...
        # and we do this in the _flat_ frame, so roll and pitch are zeroed out
        # like the gimbal in theory does.
        gimbal_in_base = TransformStamped()
        gimbal_in_base.header.stamp = now
        gimbal_in_base.header.frame_id = self.BASE_FLAT_FRAME
        gimbal_in_base.child_frame_id = self.GIMBAL_FRAME
        tf_msg.transforms.append(gimbal_in_base)

        # sam as above, winch in base_link
        winch_in_base = TransformStamped()
        winch_in_base.header.stamp = now
        winch_in_base.header.frame_id = self.BASE_FLAT_FRAME
        winch_in_base.child_frame_id = self.WINCH_FRAME
        # Set correct offset for winch_link:
        winch_in_base.transform.translation.x = 0.0  # example values
        winch_in_base.transform.translation.y = 0.0
        winch_in_base.transform.translation.z = 0.5
        winch_in_base.transform.rotation.x = 0.0
        winch_in_base.transform.rotation.y = 0.0
        winch_in_base.transform.rotation.z = 0.0
        winch_in_base.transform.rotation.w = 1.0
        tf_msg.transforms.append(winch_in_base)

        if self._utm_labeled_frame is not None: 
            utms = TransformStamped()
            utms.header.stamp = now
            utms.header.frame_id = self._utm_labeled_frame
            utms.child_frame_id = DjiLinks.UTM 
            tf_msg.transforms.append(utms)

        if self._home_point_in_utm is not None:
            # Home point in UTM
            home_tf = TransformStamped()
            home_tf.header.stamp = now
            home_tf.header.frame_id = DjiLinks.UTM
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
        
        # this is specific to smarc, since we take the water level as basis for everything
        alt_above_water = self._HOME_ALT_ABOVE_WATER + self._base_pose_in_home.pose.position.z

        base_in_geopoint.altitude = alt_above_water
        self._pos_latlon_pub.publish(base_in_geopoint)

        self._altitude_pub.publish(Float32(data = alt_above_water))


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

        if self._utm_labeled_frame is not None:
            self._labeled_utm_frame_pub.publish(String(data=self._utm_labeled_frame))
                        
        

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