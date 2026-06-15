#!/usr/bin/python3

import rclpy, sys, math, time
import numpy as np
from enum import Enum

from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.time import Time, Duration
from rclpy.timer import Timer
from rclpy.qos import QoSProfile, ReliabilityPolicy, QoSDurabilityPolicy
from rclpy.callback_groups import ReentrantCallbackGroup

from tf2_ros import Buffer, TransformListener
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster
from tf2_ros.transform_broadcaster import TransformBroadcaster

from std_msgs.msg import Float32, Int8, String, Bool
from std_srvs.srv import Trigger
from sensor_msgs.msg import NavSatFix, Joy, BatteryState, JoyFeedback
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TwistStamped, Pose, PoseStamped, TransformStamped, QuaternionStamped, PointStamped, Vector3Stamped, Quaternion
from geographic_msgs.msg import GeoPoint
from tf2_msgs.msg import TFMessage

from psdk_interfaces.msg import PositionFused, ControlMode, EscData, SingleBatteryInfo
from smarc_msgs.msg import Topics as SmarcTopics
from smarc_msgs.msg import GeofenceStatusStamped
from dji_msgs.msg import Links as DjiLinks
from dji_msgs.msg import Topics as DjiTopics
from dji_msgs.msg import PsdkTopics as PSDKTopics


from smarc_utilities.georef_utils import convert_latlon_to_utm, convert_utm_to_latlon
from tf_transformations import euler_from_quaternion, quaternion_from_euler, quaternion_matrix
from tf2_geometry_msgs import do_transform_pose_stamped


class DjiCaptain():
    def __init__(self, node: Node):
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
        self.ROBOT_NAME : str = self._node.get_parameter("robot_name").get_parameter_value().string_value
        

        # give an error-causing default value to force the user to pass this parameter every time
        # there is no safe assumption that can be made for this.
        self._node.declare_parameter("home_altitude_above_water", -1.0)
        self._HOME_ALT_ABOVE_WATER = self._node.get_parameter("home_altitude_above_water").get_parameter_value().double_value
        if self._HOME_ALT_ABOVE_WATER <= 0:
            self.log(f"Warning: home_altitude_above_water parameter not set or invalid! It is {self._HOME_ALT_ABOVE_WATER}")
            self.log("YOU MUST PASS THIS PARAMETER AND MAKE SURE IT IS CORRECT!")
            self.log("Captain will not run. Exiting.")
            sys.exit(1)

        self._node.declare_parameter("min_altitude_above_water", 1.5)
        self.MIN_ALTITUDE_ABOVE_WATER = self._node.get_parameter("min_altitude_above_water").get_parameter_value().double_value
        if self.MIN_ALTITUDE_ABOVE_WATER <= 0:
            self.log(f"Warning: min_altitude_above_water parameter not set or invalid! It is {self.MIN_ALTITUDE_ABOVE_WATER}")
            self.log("Setting it to 1.5m to prevent damage to the vehicle, but you should set it to something appropriate for your mission!")
            self.MIN_ALTITUDE_ABOVE_WATER = 1.5

        
        self._move_to_setpoint : PoseStamped | None = None
        self._joy_timer : Timer | None = None
        self.JOY_PUB_MAX = 1.5
        self.JOY_PUB_PERIOD = 1.0 / 50.0
        self._prev_joy_output : np.ndarray | None = None
        self._last_pubbed_fluvel_joy : Joy | None = None
        
        
        self.MOVE_TO_SETPOINT_MAX_AGE : float = 1.5 #How long we keep the move to setpoint before we consider it stale
        self.MAX_SETPOINT_DISTANCE : float = 100.0 # meters, max distance from current position to accept a move to setpoint
        # if new setpoint time is close to current setpoint time
        # we check if new setpoint is similar enough to current setpoint
        self.CHECK_SETPOINT_SIMILARITY_TIME_THRESHOLD : float = 0.3 
        self.CHECK_SETPOINT_SIMILARITY_COSINE_THRESHOLD : float = math.cos(math.radians(90))


        self.READY_BATTERY_PERCENTAGE = 25
        self.ERROR_BATTERY_PERCENTAGE = 15
        
        # this is the idle RPM for the ESCs, below this we consider the vehicle not flying
        self.NUM_PROPS = 4 if self.ROBOT_NAME == "M350" else 8
        self.ESC_IDLE_RPM = 2500 if self.ROBOT_NAME == "M350" else 500 #TODO FC30 idle, who knows...
        self._prop_rpms = [0] * self.NUM_PROPS


        self._TF_NS : str = f"{self.ROBOT_NAME}/"
        self.ODOM_FRAME = self._TF_NS + DjiLinks.ODOM
        self.MAP_FRAME = self._TF_NS + DjiLinks.MAP
        self.BASE_FRAME = self._TF_NS + DjiLinks.BASE_LINK
        self.BASE_FLAT_FRAME = self._TF_NS + DjiLinks.BASE_FLAT
        self.HOME_FRAME = self._TF_NS + DjiLinks.HOME_POINT

        self._utm_zb_label : str | None = None

        self._base_pose_in_home : PoseStamped | None = None
        self._base_pose_in_map : PoseStamped | None = None
        self._base_pose_flat_in_home : PoseStamped | None = None
        self._home_point_in_utm : PointStamped | None = None
        self._velocity_ground : Vector3Stamped | None = None
        self._angular_rate_ground : Vector3Stamped | None = None
        self._esc_data : EscData | None = None
        self._heading_deg : float | None = None
        self._course_deg : float | None = None
        self._battery_percent : float | None = None
        self._control_mode_nums : tuple[int,int,int] | None = None
        self._rc_nums : tuple[float,float,float,float,int] | None = None

        self._vehicle_health = Int8()
        self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_WAITING

        self._got_control : bool = False
        self._flying : bool = False
        self._cam_processor_happy : bool = False
        self._geofence_status : GeofenceStatusStamped | None = None
        self._cleared_water_level_once : bool = False
        
        self.MAX_GEOFENCE_STATUS_AGE = 1.0 # seconds


        # this could be a param, but really we likely will never run this on anything except
        # the M350 which has a nominal 3kg max payload, so hardcoding it here is fine.
        # I set it to 4kg to have some momentary overshoot margins due to motion etc.
        self._node.declare_parameter("max_load_kg", 4.0)
        self._MAX_LOAD_KG : float = self._node.get_parameter("max_load_kg").get_parameter_value().double_value
        self._load_cell_weight : float | None = None

        self._node.declare_parameter("rope_length", 10.0)
        self._ROPE_LENGTH : float = self._node.get_parameter("rope_length").get_parameter_value().double_value


        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self._node, spin_thread=False)

        qos_best_effort10 = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT, durability=QoSDurabilityPolicy.VOLATILE)

        node.create_subscription(
            NavSatFix,
            PSDKTopics.GPS_POSITION,
            self._gps_callback,
            qos_profile=qos_best_effort10)

        node.create_subscription(
            PositionFused,
            PSDKTopics.POSITION_FUSED,
            self._position_fused_callback,
            qos_profile=qos_best_effort10)

        node.create_subscription(
            NavSatFix,
            PSDKTopics.HOME_POINT,
            self._home_point_callback,
            qos_profile=qos_best_effort10)

        node.create_subscription(
            QuaternionStamped,
            PSDKTopics.ATTITUDE,
            self._attitude_callback,
            qos_profile=qos_best_effort10)

        node.create_subscription(
            ControlMode,
            PSDKTopics.CONTROL_MODE,
            self._control_mode_callback,
            qos_profile=qos_best_effort10)
        
        if self.ROBOT_NAME == "M350":
            node.create_subscription(
                BatteryState,
                PSDKTopics.BATTERY,
                self._battery_callback,
                qos_profile=qos_best_effort10)
            
        if self.ROBOT_NAME == "FC30":
            node.create_subscription(
                SingleBatteryInfo,
                PSDKTopics.SINGLE_BATT1,
                self._single_batt_callback,
                qos_profile=qos_best_effort10)

            node.create_subscription(
                SingleBatteryInfo,
                PSDKTopics.SINGLE_BATT2,
                self._single_batt_callback,
                qos_profile=qos_best_effort10)

        
        node.create_subscription(
            Vector3Stamped,
            PSDKTopics.VELOCITY_GROUND_FSD,
            self._velocity_ground_callback,
            qos_profile=qos_best_effort10)
        
        node.create_subscription(
            Vector3Stamped,
            PSDKTopics.ANGULAR_RATE_GND_FSD,
            self._angular_rate_ground_callback,
            qos_profile=qos_best_effort10)
        
        node.create_subscription(
            EscData,
            PSDKTopics.ESC_DATA,
            lambda msg: setattr(self, "_esc_data", msg),
            qos_profile=qos_best_effort10)
        
        node.create_subscription(
            Joy,
            PSDKTopics.RC,
            self._dji_rc_cb,
            qos_profile=qos_best_effort10)

        node.create_subscription(
            PoseStamped,
            DjiTopics.MOVE_TO_SETPOINT_TOPIC,
            self._move_to_setpoint_callback,
            qos_profile=qos_best_effort10)
        
        node.create_subscription(
            Float32,
            DjiTopics.LOAD_CELL_WEIGHT_TOPIC,
            self._load_cell_callback,
            qos_profile=qos_best_effort10)

        node.create_subscription(
            Bool,
            DjiTopics.CAM_PROCESSOR_HAPPY_TOPIC,
            self._cam_processor_happy_callback,
            qos_profile=qos_best_effort10
        )

        node.create_subscription(
            GeofenceStatusStamped,
            SmarcTopics.GEOFENCE_STATUS_TOPIC,
            self._geofence_status_callback,
            qos_profile=qos_best_effort10
        )

        self._release_control_srv = node.create_client(Trigger, PSDKTopics.RELEASE_CONTROL_SRV)
        self._got_release_control_srv = False
        
        self._status_pub = node.create_publisher(String, "captain_status", qos_profile=10)
        self._tf_pub = TransformBroadcaster(node)
        self._static_tf_pub = StaticTransformBroadcaster(node)

        self._labeled_utm_frame_pub = node.create_publisher(String, DjiTopics.LABELED_UTM_TOPIC, qos_profile=10)
        self._base_in_map_pub = node.create_publisher(PoseStamped, DjiTopics.BASE_LINK_IN_MAP_TOPIC, qos_profile=10)
        self._FLU_vel_joy_pub = node.create_publisher(Joy, PSDKTopics.FLU_VEL_YAWRATE_JOY_CMD, qos_profile=10)

        self._vehicle_health_pub = node.create_publisher(Int8, SmarcTopics.VEHICLE_HEALTH_TOPIC, qos_profile=10)
        self._odom_pub = node.create_publisher(Odometry, SmarcTopics.ODOM_TOPIC, qos_profile=10)
        self._heading_pub = node.create_publisher(Float32, SmarcTopics.HEADING_TOPIC, qos_profile=10)
        self._course_pub = node.create_publisher(Float32, SmarcTopics.COURSE_TOPIC, qos_profile=10)
        self._speed_pub = node.create_publisher(Float32, SmarcTopics.SPEED_TOPIC, qos_profile=10)
        self._pos_latlon_pub = node.create_publisher(GeoPoint, SmarcTopics.POS_LATLON_TOPIC, qos_profile=10)
        self._battery_percent_pub = node.create_publisher(Float32, SmarcTopics.BATTERY_PERCENT_TOPIC, qos_profile=10)
        self._altitude_pub = node.create_publisher(Float32, SmarcTopics.ALTITUDE_TOPIC, qos_profile=10)

        self._vehicle_health_timer = node.create_timer(1, self._publish_vehicle_health)
        self._tf_timer = node.create_timer(0.1, self._publish_tf)
        self._static_tf_timer = node.create_timer(1.0, self._publish_static_tf) 
        self._smarc_timer = node.create_timer(0.1, self._publish_smarc)
        self._status_str_timer = node.create_timer(0.1,lambda: self._status_pub.publish(String(data=self.status_str)))
        
        

    ############
    # Properties
    ############
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
    def altitude_above_water(self) -> float|None:
        if self._base_pose_in_home is None: return None
        return self._base_pose_in_home.pose.position.z + self._HOME_ALT_ABOVE_WATER

    @property
    def depth_of_hook(self) -> float | None:
        alt = self.altitude_above_water
        if alt is None: return None
        return alt - self._ROPE_LENGTH

    
    
    @property
    def status_str(self) -> str:
        s = "\nDjiCaptain Status:\n"
        s += f">> GOT CONTROL: {self._got_control} ({', '.join(f'{num}' for num in self._control_mode_nums) if self._control_mode_nums else 'N/A'})\n"

        vh = ">> Vehicle Health: "
        if self._vehicle_health.data == SmarcTopics.VEHICLE_HEALTH_READY:
            vh += f"READY\n"
        elif self._vehicle_health.data == SmarcTopics.VEHICLE_HEALTH_ERROR:
            vh += f"ERROR\n"
        else:
            vh += f"WAITING\n"
        s += vh

        s += f"  DJI RC: {', '.join(f'{num:.2f}' for num in self._rc_nums) if self._rc_nums else 'N/A'}\n"

        if self._battery_percent is not None:
            s += f"  Battery Percent: {self._battery_percent:.2f} (ready:{self.READY_BATTERY_PERCENTAGE}, error:{self.ERROR_BATTERY_PERCENTAGE})\n"
        else:
            s += f"  Battery Percent: N/A\n"
        
        s += f"  Cam Proc Happy: {self._cam_processor_happy}\n"

        if self._load_cell_weight is not None:
            s += f"  Load Cell Weight: {self._load_cell_weight:+.2f} kg (max: {self._MAX_LOAD_KG} kg)\n"
        else:
            s += f"  Load Cell Weight: N/A\n"

        if self.depth_of_hook is not None:
            s += f"  Depth of Hook: {self.depth_of_hook:+.2f} m (rope length: {self._ROPE_LENGTH} m)\n"
        else:
            s += f"  Depth of Hook: N/A\n"

        s += f"  Flying: {self._flying} [{', '.join(f'{rpm:.2f}' for rpm in self._prop_rpms)}]\n"
        
        if self._base_pose_in_home is not None:
            s += f"  Altitude from water: {self.altitude_above_water:+.2f} m\n"
        else:
            s += f"  Altitude from water: N/A, base pose in home not known!\n"

        if self._last_pubbed_fluvel_joy is not None:
            a = self._last_pubbed_fluvel_joy.axes
            t = self._last_pubbed_fluvel_joy.header.stamp.sec + self._last_pubbed_fluvel_joy.header.stamp.nanosec * 1e-9
            s += f"  Last FLUVel Joy (XYZ): [{a[0]:+.2f}, {a[1]:+.2f}, {a[2]:+.2f}, {a[3]:+.2f}] ({self.now_time - t:.2f}s ago)\n"
        else:
            s += f"  Last FLUVel Joy: None\n"

        s += "========================\n"

        s += f"  Home in UTM: {format_point_stamped(self._home_point_in_utm)} ({self._utm_zb_label})\n"
        s += f"  Position in Home: {format_pose_stamped(self._base_pose_in_home)}\n"
        
        if self._heading_deg is not None: s += f"  Heading: {self._heading_deg:+.2f}\n"
        else: s += f"  Heading: N/A\n"

        if self._course_deg is not None: s += f"  Course: {self._course_deg:+.2f}\n"
        else: s += f"  Course: N/A\n"

        s += f"  Velocity Ground: {format_vector3_stamped(self._velocity_ground)}\n"
        s += f"  Angular Rate Ground: {format_vector3_stamped(self._angular_rate_ground)}\n"
                
        if self.setpoint_received_at is None and self._move_to_setpoint is None:
            s += f"  No setpoint set.\n"
        elif self.setpoint_received_at is None and self._move_to_setpoint is not None:
            s += f"  Setpoint received time unknown, this is a bug! FIX THIS\n"
        elif self.setpoint_received_at is not None and self._move_to_setpoint is not None:
            s += f"  Current target setpoint: {format_pose_stamped(self._move_to_setpoint)} ({self.now_time - self.setpoint_received_at:.2f}s ago)\n"
        
        return s
    
    ############
    # Feedback
    ############
    # Because logger can block if there are too many?!
    def log(self, msg: str):
        # self._node.get_logger().info(f'\n{msg}')
        print(f'[INFO] {msg}', flush=True)

    def logerr(self, msg: str):
        # self._node.get_logger().error(f'\n{msg}')
        print(f'[ERROR] {msg}', flush=True)

    def logwarn(self, msg: str):
        # self._node.get_logger().warn(f'\n{msg}')
        print(f'[WARN] {msg}', flush=True)


    ############
    # DJI Services
    ############
    def _release_control(self):
        def on_result(f):
            self.log(f"Release control service called, success: {f.result().success}, message: {f.result().message}")

        self.log("Releasing control.")
        if not self._release_control_srv.wait_for_service(timeout_sec=5.0):
            self.log("Release control service not available...")
            return
        future = self._release_control_srv.call_async(Trigger.Request())
        future.add_done_callback(on_result)


    ############
    # Tiny callbacks
    ############
    def _load_cell_callback(self, msg: Float32):
        self._load_cell_weight = msg.data

    def _cam_processor_happy_callback(self, msg: Bool):
        self._cam_processor_happy = msg.data

    def _geofence_status_callback(self, msg: GeofenceStatusStamped):
        self._geofence_status = msg

    def _battery_callback(self, msg: BatteryState):
        self._battery_percent = msg.percentage*100

    def _single_batt_callback(self, msg: SingleBatteryInfo):
        # we get two SingleBatteryInfo messages, one for each battery, but we only care about the lowest percentage one for our health estimation
        if self._battery_percent is None:
            self._battery_percent = msg.capacity_percentage*100
        else:
            self._battery_percent = min(self._battery_percent, msg.capacity_percentage*100)





    ############
    # Motion commands
    ############
    def _move_to_setpoint_callback(self, msg: PoseStamped):
        # check if the message even has anything in it
        if msg.pose.position.x == 0 and msg.pose.position.y == 0 and msg.pose.position.z == 0:
            self.logwarn(f"Move to setpoint message is all zeros, ignoring it.\nSetpoint msg:\n{msg}")
            self._move_to_setpoint = None
            return
        
        msg_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        
        # check if message time makes sense. sim time vs real time etc
        if msg_time > self.now_time + 2.0:
            s = f"Move to setpoint message time is >2s in the future, ignoring it. Probably because the publisher and captain have different time sources."
            s += f"\nCurrent time: {self.now_time}\nSetpoint Time: {msg_time}"
            self.logwarn(s)
            self._move_to_setpoint = None
            return
        
        # check if the message is too old
        if self.now_time - msg_time > self.MOVE_TO_SETPOINT_MAX_AGE:
            s = f"Move to setpoint message is older than {self.MOVE_TO_SETPOINT_MAX_AGE}s, ignoring it."
            s += f"\nCurrent time: {self.now_time}\nSetpoint Time: {msg_time}"
            self.logwarn(s)
            self._move_to_setpoint = None
            return

        # transform it into base link frame
        try:
            transform = self._tf_buffer.lookup_transform(
                self.BASE_FLAT_FRAME,
                msg.header.frame_id,
                Time())
            new_setpoint = do_transform_pose_stamped(msg, transform)
        except Exception as e:
            self.logwarn(f"Failed to transform move to setpoint from {msg.header.frame_id} to {self.BASE_FLAT_FRAME}, ignoring it. Error: {e}")
            self._move_to_setpoint = None
            return
        
        # check if the new setpoint is roughly in the same direction as the current setpoint
        # so we can prevent quick back-and-forth if sth is publishing setpoints in a loop...
        # at this point, both setpoints are in base_flat_frame
        if self._move_to_setpoint is not None:
            # only relevant to check if the points are coming in at a high rate
            # if there is time between, we can turn around np
            # if there is very little time between, we dont want to turn around at 10hz or sth dumb
            time_between_setpoints = self.now_time - self.setpoint_received_at if self.setpoint_received_at is not None else None
            if time_between_setpoints is not None and time_between_setpoints < self.CHECK_SETPOINT_SIMILARITY_TIME_THRESHOLD:
                old_vec = np.array([
                    self._move_to_setpoint.pose.position.x,
                    self._move_to_setpoint.pose.position.y,
                    self._move_to_setpoint.pose.position.z])
                new_vec = np.array([
                    new_setpoint.pose.position.x,
                    new_setpoint.pose.position.y,
                    new_setpoint.pose.position.z])
                old_norm = np.linalg.norm(old_vec)
                new_norm = np.linalg.norm(new_vec)
                if old_norm > 0 and new_norm > 0:
                    cos_angle = np.dot(old_vec, new_vec) / (old_norm * new_norm)
                    if cos_angle < self.CHECK_SETPOINT_SIMILARITY_COSINE_THRESHOLD:
                        self.logwarn(f"New setpoint is too soon, too different. Ignoring. dT: {time_between_setpoints:.2f}s, Cosine of angle: {cos_angle:.2f}")
                        return

        
        # finally, good point, do it
        self._move_to_setpoint = new_setpoint
        if self._joy_timer is None:
            self._joy_timer = self._node.create_timer(self.JOY_PUB_PERIOD, self._move_towards_setpoint_FLUvel)
            self.log("Joy timer started to move with joy.")



    def _pub_flu_vel_joy(self, joy: list[float]):
        if abs(joy[0]) < 1e-5 and abs(joy[1]) < 1e-5 and abs(joy[2]) < 1e-5:
            # publishing 0s on F,L,U axes crashes the PSDK bridge...
            self.log("Not publishing zero joy on FLU velocity, ignoring.")
            return
        joy_msg = Joy()
        joy_msg.header.stamp = self.now_stamp
        joy_msg.axes = joy
        self._FLU_vel_joy_pub.publish(joy_msg)
        self._last_pubbed_fluvel_joy = joy_msg
        
        
        
    def _cancel_joy_timer(self):
        self._move_to_setpoint = None
        self._prev_joy_output = None
        self.log("Setpoint discarded.")
        if self._joy_timer is not None:
            self._joy_timer.cancel()
            self._joy_timer = None
            self.log("Joy timer cancelled.")


    def _move_towards_setpoint_FLUvel(self):
        # assumes move_to_setpoint is in BASE_FLAT_FRAME already

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
        
        

        e_forw = self._move_to_setpoint.pose.position.x # error about each axis
        e_left = self._move_to_setpoint.pose.position.y
        e_updn = self._move_to_setpoint.pose.position.z # we like mirrors around a point

        if (abs(e_forw) < 0.1 and abs(e_left) < 0.1 and abs(e_updn) < 0.1):
            self.log("Reached setpoint within 10cm on all axes, cancelling joy timer.")
            self._cancel_joy_timer()
            return

        if np.linalg.norm([e_forw, e_left]) > self.MAX_SETPOINT_DISTANCE:
            self.log(f"Setpoint is more than {self.MAX_SETPOINT_DISTANCE}m away horizontally, cancelling joy timer.")
            self._cancel_joy_timer()
            return
        
        if abs(e_updn) > self.MAX_SETPOINT_DISTANCE:
            self.log(f"Setpoint is more than {self.MAX_SETPOINT_DISTANCE}m away vertically, cancelling joy timer.")
            self._cancel_joy_timer()
            return


        joy_forw = self._k_pose * e_forw
        joy_left = self._k_pose * e_left
        joy_updn = self._k_pose * e_updn

        if (self._prev_joy_output is None):
            max_speed = 0.1
            self._prev_joy_output = np.array([0.0, 0.0, 0.0])
            self.log(f"No previous joy output using low initial max speed of {max_speed} m/s for smooth start.")
        else:
            max_speed = self.JOY_PUB_MAX

        # limit the velocity to the maximum joy value
        joy_err = np.array([joy_forw, joy_left, joy_updn])
        joy_err = self._normalize_max_speed(joy_err, max_speed)

        joy_net = (1 - self._r_sigma) * joy_err + self._r_sigma * self._prev_joy_output
        joy_net = self._normalize_max_speed(joy_net, max_speed)

        #self.log(f"\njoy_err: {joy_err}\njoy_pre: {self._prev_joy_output}\njoy_net: {joy_net}")

        J = [joy_net[0], joy_net[1], joy_net[2], 0.0]
        self._pub_flu_vel_joy(J)
        self._prev_joy_output = np.array([joy_net[0], joy_net[1], joy_net[2]])


    def _normalize_max_speed(self, joy_net, max_speed):
        joy_norm = np.linalg.norm(joy_net)
        if joy_norm > max_speed:
            joy_net = joy_net / joy_norm * max_speed
        return joy_net
    

    ###########
    # External human hands
    ###########
    def _dji_rc_cb(self, msg: Joy):
        self._rc_nums = (msg.axes[0], msg.axes[1], msg.axes[2], msg.axes[3], msg.buttons[0])
        # if RC is touched by user, we give up control
        if not self._got_control: return

        def give_up():
            self._got_control = False # even if the service call fails, we assume we lost control!
            self._release_control_srv.call_async(Trigger.Request()).add_done_callback(
                lambda future: self.log(f"Release control service called, success: {future.result().success}, message: {future.result().message}")
            )
        
        deadband = 100
        if np.abs(msg.axes[0]) > deadband or np.abs(msg.axes[1]) > deadband or np.abs(msg.axes[2]) > deadband or np.abs(msg.axes[3]) > deadband:
            self.logwarn("RC Joysticks touched, giving up control.")
            give_up()

        # buttons[0] is the mode switch on the RC.
        if msg.buttons[0] != 8000:
            self.logwarn("RC mode is not N, giving up control.")
            give_up()
        


    ############
    # State Callbacks
    ############
    def _velocity_ground_callback(self, msg: Vector3Stamped):
        if self._velocity_ground is None:
            self._velocity_ground = Vector3Stamped()
            self._velocity_ground.header.frame_id = self.ODOM_FRAME
        
        self._velocity_ground.vector = msg.vector
        self._velocity_ground.header.stamp = self.now_stamp

        # also set the course
        vx, vy = self._velocity_ground.vector.x, self._velocity_ground.vector.y
        if np.abs(vx) < 0.01 and np.abs(vy) < 0.01:
            self._course_deg = None
        else:
            self._course_deg = math.degrees(math.atan2(vy,vx))
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
        # control_auth = [1,0] 1-> have auth, 0-> dont have auth
        # device_mode = [0,1,4] 0->RC, 1->MSDK, 4->PSDK
        # control_mode = ??? undocumented
        # for the FC30, things are different....
        # when we HAVE control, in N mode, 
        # contorl mode is 4, device mode is 3, control_auth is 0...
        self._control_mode_nums = (msg.control_mode, msg.device_mode, msg.control_auth)
        if self.ROBOT_NAME == "M350":
            just_got_control = msg.control_auth == 1 and msg.device_mode == 4
        elif self.ROBOT_NAME == "FC30":
            just_got_control = msg.control_auth == 0 and msg.device_mode == 3 and msg.control_mode == 4
        else:
            self.logwarn(f"Unknown robot name {self.ROBOT_NAME}, cannot determine control authority from control mode message! Assuming no control.")
            just_got_control = False
            
        if self._got_control == just_got_control:
            return
        
        if self._got_control and not just_got_control:
            self.log("Released control authority, stopping joy timer, discarding setpoint.")
            self._cancel_joy_timer()
            self._got_control = False

        elif not self._got_control and just_got_control:
            self.log("Gained control authority.")
            self._got_control = True
        

    def _position_fused_callback(self, msg: PositionFused):
        if self._home_point_in_utm is None:
            self.log("Home point not set, ignoring position fused until it is...")
            return
        
        if self._base_pose_in_home is None:
            self._base_pose_in_home = PoseStamped()
            self._base_pose_in_home.header.frame_id = self.ODOM_FRAME
            self.log("Base pose initialized.")
        self._base_pose_in_home.pose.position.x = msg.position.x
        self._base_pose_in_home.pose.position.y = msg.position.y
        self._base_pose_in_home.pose.position.z = msg.position.z
        self._base_pose_in_home.header.stamp = self.now_stamp
            

        if self._base_pose_flat_in_home is None:
            self._base_pose_flat_in_home = PoseStamped()
            self._base_pose_flat_in_home.header.frame_id = self.ODOM_FRAME
        self._base_pose_flat_in_home.pose.position = self._base_pose_in_home.pose.position
        self._base_pose_flat_in_home.header.stamp = self._base_pose_in_home.header.stamp

        if self._base_pose_in_map is None:
            self._base_pose_in_map = PoseStamped()
            self._base_pose_in_map.header.frame_id = self.MAP_FRAME
        self._base_pose_in_map.pose.position.x = self._base_pose_in_home.pose.position.x
        self._base_pose_in_map.pose.position.y = self._base_pose_in_home.pose.position.y
        self._base_pose_in_map.pose.position.z = self._base_pose_in_home.pose.position.z + self._HOME_ALT_ABOVE_WATER
        self._base_pose_in_map.header.stamp = self._base_pose_in_home.header.stamp
        self._base_in_map_pub.publish(self._base_pose_in_map)
        

    def _attitude_callback(self, msg: QuaternionStamped):
        # the attitude is in ENU by psdk definition, so we need to convert it to NED (compasses use this...)
        # and the use the z component as heading
        if self._base_pose_in_home is None or self._base_pose_flat_in_home is None:
            self._base_pose_in_home = PoseStamped()
            self._base_pose_in_home.header.frame_id = self.ODOM_FRAME
            self._base_pose_flat_in_home = PoseStamped()
            self._base_pose_flat_in_home.header.frame_id = self.ODOM_FRAME

        rpy_enu = euler_from_quaternion([msg.quaternion.x, msg.quaternion.y, msg.quaternion.z, msg.quaternion.w])
        self._heading_deg = 90 - math.degrees(rpy_enu[2])
        self._base_pose_in_home.pose.orientation = msg.quaternion

        flat_quat = Quaternion()
        flat_quat.x, flat_quat.y, flat_quat.z, flat_quat.w = quaternion_from_euler(0, 0, rpy_enu[2])
        self._base_pose_flat_in_home.pose.orientation = flat_quat


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



    def _gps_callback(self, msg: NavSatFix):
        if self._utm_zb_label is None:
            gp = GeoPoint()
            gp.latitude = msg.latitude
            gp.longitude = msg.longitude
            gp.altitude = msg.altitude
            utm = convert_latlon_to_utm(gp)
            self._utm_zb_label = utm.header.frame_id
            self.log(f"Setting UTM labeled frame to: {self._utm_zb_label}")


    

    ############
    # Health and TF publishing
    ############
    def _health_to_str(self, health_state: int) -> str:
        if health_state == SmarcTopics.VEHICLE_HEALTH_WAITING:
            return "WAITING"
        elif health_state == SmarcTopics.VEHICLE_HEALTH_READY:
            return "READY"
        elif health_state == SmarcTopics.VEHICLE_HEALTH_ERROR:
            return "ERROR"
        else:
            return f"UNKNOWN({health_state})"

    def _publish_vehicle_health(self):
        prev_health_state = self._vehicle_health.data

        self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_WAITING

        if self._home_point_in_utm is None:
            self.logwarn(f"Home point not received yet, waiting.")
            self._vehicle_health_pub.publish(self._vehicle_health)
            return
        
        if self._base_pose_in_home is None:
            self.logwarn(f"Position fused not received yet, waiting.")
            self._vehicle_health_pub.publish(self._vehicle_health)
            return
        
        if self._esc_data is None:
            self.logwarn(f"ESC data not received yet, waiting.")
            self._vehicle_health_pub.publish(self._vehicle_health)
            return
        
        if self._heading_deg is None:
            self.logwarn(f"Heading not received yet, waiting for attitude topic...")
            self._vehicle_health_pub.publish(self._vehicle_health)
            return
        
        if self._battery_percent is None:
            self.logwarn(f"Battery percentage not received yet, waiting.")
            self._vehicle_health_pub.publish(self._vehicle_health)
            return
        else:
            if self._battery_percent < self.READY_BATTERY_PERCENTAGE:
                self.logwarn(f"Battery below ready: {self._battery_percent:.2f}% < {self.READY_BATTERY_PERCENTAGE:.2f}%")
                self._vehicle_health_pub.publish(self._vehicle_health)
                return
            elif self._battery_percent < self.ERROR_BATTERY_PERCENTAGE:
                self.logerr(f"Battery below error: {self._battery_percent:.2f}% < {self.ERROR_BATTERY_PERCENTAGE:.2f}%")
                self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_ERROR
                self._vehicle_health_pub.publish(self._vehicle_health)
                return
            
        if self._load_cell_weight is not None and self._load_cell_weight > self._MAX_LOAD_KG:
            self.logerr(f"Load cell weight above max: {self._load_cell_weight:.2f} kg > {self._MAX_LOAD_KG:.2f} kg")
            self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_ERROR
            self._vehicle_health_pub.publish(self._vehicle_health)
            return

        if not self._tf_buffer.can_transform(self.MAP_FRAME, self.BASE_FLAT_FRAME, Time()):
            self.logwarn(f"Cannot transform from {self.BASE_FLAT_FRAME} to {self.MAP_FRAME} yet, waiting for TF to be available...")
            self._vehicle_health_pub.publish(self._vehicle_health)
            return
        
        if not self._got_release_control_srv:
            self.log("Acquiring release control service...")
            self._got_release_control_srv = self._release_control_srv.wait_for_service(timeout_sec=1.0)
            if not self._got_release_control_srv:
                self.logerr("Release control service not available...\nCaptain will do nothing but wait for this...\nTo fix, run PSDK ROS Wrapper OR sim+ros bridge.")
                return
            
            

        # if we made it here, then we got all the sensor happy
        # and we _can_ do things, like take off and look around
        self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_READY

        # if we are flying, we need to check more things to make sure we are flying safely
        self._prop_rpms = [esc.speed for esc in list(self._esc_data.esc)[:self.NUM_PROPS]]
        self._flying = all(rpm > self.ESC_IDLE_RPM for rpm in self._prop_rpms)

        if not self._cleared_water_level_once and self.altitude_above_water > self.MIN_ALTITUDE_ABOVE_WATER:
            self.log(f"Cleared water level for the first time! Altitude above water: {self.altitude_above_water:.2f} m > {self.MIN_ALTITUDE_ABOVE_WATER:.2f} m")
        self._cleared_water_level_once = self._cleared_water_level_once or self.altitude_above_water > self.MIN_ALTITUDE_ABOVE_WATER

        if self._flying:
            water_altitude_error = self.altitude_above_water < self.MIN_ALTITUDE_ABOVE_WATER and self._cleared_water_level_once
            if water_altitude_error:
                self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_WAITING
                self.logerr(f"TOO CLOSE TO WATER: {self.altitude_above_water:.2f} < {self.MIN_ALTITUDE_ABOVE_WATER:.2f}")


            if self._geofence_status is not None:
                msg_time = self._geofence_status.time.sec + self._geofence_status.time.nanosec * 1e-9
                if self.now_time - msg_time < self.MAX_GEOFENCE_STATUS_AGE:
                    if self._geofence_status.status == GeofenceStatusStamped.STATUS_OUTSIDE:
                        self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_WAITING
                        s = f"Geofence violation:"
                        if self._geofence_status.status == GeofenceStatusStamped.STATUS_OUTSIDE:
                            s += " OUTSIDE geofence!"
                        if self._geofence_status.outside_reason == GeofenceStatusStamped.REASON_FENCE:
                            s += " OUTSIDE FENCE!"
                        if self._geofence_status.outside_reason == GeofenceStatusStamped.REASON_FLOOR:
                            s += " BELOW FLOOR!"
                        if self._geofence_status.outside_reason == GeofenceStatusStamped.REASON_CEILING:
                            s += " ABOVE CEILING!"
                        self.logerr(s)

        if prev_health_state != self._vehicle_health.data:
            self.log(f"Vehicle health changed: {self._health_to_str(prev_health_state)} -> {self._health_to_str(self._vehicle_health.data)}")
        self._vehicle_health_pub.publish(self._vehicle_health)


    def _publish_static_tf(self):
        if self._utm_zb_label is None or self._home_point_in_utm is None:
            self.log("UTM frame label or home point in UTM not set, cannot publish static TF yet.")
            return

        now = self.now_stamp
        # 0 transforms for home -> odom for compatibility with other systems
        # and so we can use "odom" for all things that relate to home point
        odom_in_home = TransformStamped()
        odom_in_home.header.stamp = now
        odom_in_home.header.frame_id = self.HOME_FRAME
        odom_in_home.child_frame_id = self.ODOM_FRAME
        self._static_tf_pub.sendTransform(odom_in_home)

        utms = TransformStamped()
        utms.header.stamp = now
        utms.header.frame_id = self._utm_zb_label
        utms.child_frame_id = DjiLinks.UTM 
        self._static_tf_pub.sendTransform(utms)

        # Home point in UTM
        home_tf = TransformStamped()
        home_tf.header.stamp = now
        home_tf.header.frame_id = DjiLinks.UTM
        home_tf.child_frame_id = self.HOME_FRAME
        home_tf.transform.translation.x = self._home_point_in_utm.point.x 
        home_tf.transform.translation.y = self._home_point_in_utm.point.y
        home_tf.transform.translation.z = self._home_point_in_utm.point.z
        self._static_tf_pub.sendTransform(home_tf)

        # home point in UTM, but at water surface = map frame
        map_tf = TransformStamped()
        map_tf.header.stamp = now
        map_tf.header.frame_id = self.ODOM_FRAME # == home_frame
        map_tf.child_frame_id = self.MAP_FRAME
        map_tf.transform.translation.x = 0.0
        map_tf.transform.translation.y = 0.0
        # home is above water somewhere, map is at water level, so the transform is just moving down
        map_tf.transform.translation.z = -self._home_point_in_utm.point.z 
        self._static_tf_pub.sendTransform(map_tf)

            
    
    def _publish_tf(self):
        now = self.now_stamp

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
            self._tf_pub.sendTransform(base_in_home)


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
            self._tf_pub.sendTransform(base_flat_in_home)

        
        if self._move_to_setpoint is not None:
            move_to_setpoint_tf = TransformStamped()
            move_to_setpoint_tf.header.stamp = now
            move_to_setpoint_tf.header.frame_id = self._move_to_setpoint.header.frame_id
            move_to_setpoint_tf.child_frame_id = self._TF_NS + "move_to_setpoint"
            move_to_setpoint_tf.transform.translation.x = self._move_to_setpoint.pose.position.x
            move_to_setpoint_tf.transform.translation.y = self._move_to_setpoint.pose.position.y
            move_to_setpoint_tf.transform.translation.z = self._move_to_setpoint.pose.position.z
            self._tf_pub.sendTransform(move_to_setpoint_tf)




    def _publish_smarc(self):
        if self._home_point_in_utm is None:
            self.log("[smarc] Home point not set, cannot publish latlon position.")
            return
        
        if self._base_pose_in_home is None:
            self.log("[smarc] Base pose not set, cannot publish latlon position.")
            return
        
        if self._utm_zb_label is None:
            self.log("[smarc] UTM frame label not set, cannot publish latlon position.")
            return
        

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
        
        base_in_utm = PointStamped()
        base_in_utm.header.frame_id = self._utm_zb_label
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

        if self._utm_zb_label is not None:
            self._labeled_utm_frame_pub.publish(String(data=self._utm_zb_label))
                        
        

def format_point_stamped(point: PointStamped|None) -> str:
        if( point is None):
            return "None"
        return f"(x={point.point.x:+.3f}, y={point.point.y:+.3f}, z={point.point.z:+.3f}, frame_id={point.header.frame_id})"

def format_pose_stamped(pose: PoseStamped|None) -> str:
        if( pose is None):
            return "None"
        rpy = euler_from_quaternion([
            pose.pose.orientation.x,
            pose.pose.orientation.y,
            pose.pose.orientation.z,
            pose.pose.orientation.w
        ])
        return f"(x={pose.pose.position.x:+.3f}, y={pose.pose.position.y:+.3f}, z={pose.pose.position.z:+.3f}, " \
               f"roll={math.degrees(rpy[0]):+.3f}, pitch={math.degrees(rpy[1]):+.3f}, yaw={math.degrees(rpy[2]):+.3f}, " \
               f"frame_id={pose.header.frame_id})"
        
def format_vector3_stamped(vec: Vector3Stamped|None) -> str:
        if( vec is None):
            return "None"
        return f"(x={vec.vector.x:+.3f}, y={vec.vector.y:+.3f}, z={vec.vector.z:+.3f}, frame_id={vec.header.frame_id})"



# thanks chat?
def transform_velocity_vector(
    tf_buffer: Buffer,
    vel_src: Vector3Stamped,
    target_frame: str,
    *,
    time: Time | None = None,
    timeout: Duration = Duration(seconds=0, nanoseconds=5_000_000),  # 5ms = 5,000,000ns
) -> Vector3Stamped:
    """
    Rotate a velocity Vector3Stamped from vel_src.header.frame_id -> target_frame.

    Notes
    -----
    - Velocity is a *pure vector*: only the rotation from the TF transform is applied.
    - Translation is ignored (as it should be for vectors).
    - If source and target frames match, the input is returned (header updated).
    """
    if not vel_src.header.frame_id:
        raise ValueError("vel_src.header.frame_id must be set")

    if vel_src.header.frame_id == target_frame:
        out = Vector3Stamped()
        out.header.stamp = vel_src.header.stamp
        out.header.frame_id = target_frame
        out.vector = vel_src.vector  # shallow copy is fine for geometry_msgs
        return out

    # Default to "latest available transform" time if not provided
    if time is None:
        time = Time(seconds=0)

    try:
        # Transform that maps vectors from source_frame -> target_frame
        tf = tf_buffer.lookup_transform(
            target_frame=target_frame,
            source_frame=vel_src.header.frame_id,
            time=time,
            timeout=timeout,
        )
    except :
        raise RuntimeError(f"TF lookup failed from {vel_src.header.frame_id} to {target_frame}") 

    # Extract and (defensively) normalize quaternion
    qx, qy, qz, qw = (
        tf.transform.rotation.x,
        tf.transform.rotation.y,
        tf.transform.rotation.z,
        tf.transform.rotation.w,
    )
    q = np.array([qx, qy, qz, qw], dtype=float)
    n = np.linalg.norm(q)
    if n == 0.0:
        raise RuntimeError("TF rotation quaternion has zero norm")
    q /= n

    # 3x3 rotation matrix
    R = quaternion_matrix(q)[0:3, 0:3]

    v_src = np.array(
        [vel_src.vector.x, vel_src.vector.y, vel_src.vector.z],
        dtype=float,
    )
    v_tgt = R @ v_src

    vel_out = Vector3Stamped()
    # Keep the original measurement time; you can also choose tf.header.stamp
    vel_out.header.stamp = vel_src.header.stamp
    vel_out.header.frame_id = target_frame
    vel_out.vector.x, vel_out.vector.y, vel_out.vector.z = v_tgt.tolist()
    return vel_out

    
    
def main():
    rclpy.init(args=sys.argv)
    node = Node("DjiCaptainNode")
    
    capt = DjiCaptain(node)

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()
