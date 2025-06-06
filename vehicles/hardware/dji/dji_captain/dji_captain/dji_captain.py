#!/usr/bin/python3

import rclpy, sys, math
from enum import Enum


from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor


from std_msgs.msg import Float32, Int8
from sensor_msgs.msg import NavSatFix, Joy, BatteryState
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TwistStamped, Pose, PoseStamped, TransformStamped, QuaternionStamped, PointStamped, Vector3Stamped
from geographic_msgs.msg import GeoPoint
from tf2_msgs.msg import TFMessage

from psdk_interfaces.msg import PositionFused, ControlMode
from smarc_msgs.msg import Topics as SmarcTopics

from smarc_utilities.georef_utils import convert_latlon_to_utm, convert_utm_to_latlon
from tf_transformations import euler_from_quaternion


class PSDKTopics(Enum):
    # these are hardcoded topics in PSDK bridge...
    WRAPPER_NS = "/Quadrotor/wrapper/psdk_ros2/"
    
    GPS_POSITION        = WRAPPER_NS + "gps_position"
    POSITION_FUSED      = WRAPPER_NS + "position_fused"
    ATTITUDE            = WRAPPER_NS + "attitude"
    HOME_POINT          = WRAPPER_NS + "home_point"
    HOME_POINT_ALTITUDE = WRAPPER_NS + "home_point_altitude"
    ALTITUDE            = WRAPPER_NS + "altitude_sea_level"
    HEIGHT_ABOVE_GROUND = WRAPPER_NS + "height_above_ground"
    CONTROL_MODE        = WRAPPER_NS + "control_mode"
    BATTERY             = WRAPPER_NS + "battery" 
    VELOCTY_GROUND_FSD  = WRAPPER_NS + "velocity_ground_fused"
    ANGULAR_RATE_GND_FSD= WRAPPER_NS + "angular_rate_ground_fused"



class DjiCaptain():
    def __init__(self, node: Node):
        self._node = node
        self._tf_ns = "Quadrotor/"
        
        self.READY_BATTERY_PERCENTAGE = 0.4
        self.READY_HEIGHT_ABOVE_GROUND = 3
        self.ERROR_BATTERY_PERCENTAGE = 0.15
        self.ERROR_HEIGHT_ABOVE_GROUND = 1

        self.UTM_FRAME = "utm"
        self.ODOM_FRAME = self._tf_ns + "odom"
        self.MAP_FRAME = self._tf_ns + "map"
        self.BASE_FRAME = self._tf_ns + "base_link"
        self.HOME_FRAME = self._tf_ns + "home_point"


        self._base_pose_in_home : PoseStamped | None = None
        self._home_point_in_utm : PointStamped | None = None
        self._gps_point_in_home : PointStamped | None = None
        self._rtk_point_in_home : PointStamped | None = None
        self._velocity_ground : Vector3Stamped | None = None
        self._angular_rate_ground : Vector3Stamped | None = None
        self._vehicle_health = Int8()
        self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_WAITING

        self._geo_altitude : float | None = None
        self._heading_deg : float | None = None
        self._course_deg : float | None = None
        self._height_above_ground : float | None = None

        self._got_control : bool = False
        self._flying : bool = False
        self._battery_percent : float | None = None

        self._utm_labeled_frame : str | None = None


       

        self._tf_pub = node.create_publisher(TFMessage,"/tf",qos_profile=10)
        self._tf_timer = node.create_timer(0.05, self._publish_tf)

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

        self._status_str_timer = node.create_timer(0.5,lambda: self.log(self.status_str))


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
            Float32,
            PSDKTopics.HEIGHT_ABOVE_GROUND.value,
            self._height_above_ground_cb,
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
        
        


    @property
    def now_stamp(self):
        return self._node.get_clock().now().to_msg()
    
    
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
        s += f"  Heading: {self._heading_deg}\n"
        s += f"  Course: {self._course_deg}\n"
        s += f"  Height Above Ground: {self._height_above_ground}\n"
        s += f"  Battery Percent: {self._battery_percent}\n"
        
        s += f"\n  Got Control: {self._got_control}\n"
        if self._vehicle_health.data == SmarcTopics.VEHICLE_HEALTH_READY:
            s += f"  Vehicle Health: READY (flying:{self._flying})\n"
        elif self._vehicle_health.data == SmarcTopics.VEHICLE_HEALTH_ERROR:
            s += f"  Vehicle Health: ERROR (flying:{self._flying})\n"
        else:
            s += f"  Vehicle Health: WAITING (flying:{self._flying})\n"


        return s
    
    def log(self, msg: str):
        self._node.get_logger().info(msg)


    def _geo_alt_cb(self, msg: Float32):
        self._geo_altitude = msg.data

    def _height_above_ground_cb(self, msg: Float32):
        self._height_above_ground = msg.data

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
        
        if self._base_pose_in_home is None:
            self._base_pose_in_home = PoseStamped()
            self._base_pose_in_home.header.frame_id = self.ODOM_FRAME
            
        self._base_pose_in_home.pose.position.x = msg.position.x
        self._base_pose_in_home.pose.position.y = msg.position.y
        self._base_pose_in_home.pose.position.z = msg.position.z - self._home_point_in_utm.point.z
        self._base_pose_in_home.header.stamp = self.now_stamp
        

    def _attitude_callback(self, msg: QuaternionStamped):
        # the attitude is in ENU by psdk definition, so we need to convert it to NED (compasses use this...)
        # and the use the z component as heading
        if self._base_pose_in_home is None:
            self._base_pose_in_home = PoseStamped()
            self._base_pose_in_home.header.frame_id = self.ODOM_FRAME

        rpy_enu = euler_from_quaternion([msg.quaternion.x, msg.quaternion.y, msg.quaternion.z, msg.quaternion.w])
        self._heading_deg = 90 - math.degrees(rpy_enu[2])
        self._base_pose_in_home.pose.orientation = msg.quaternion
        

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
        self._home_point_in_utm.header.stamp = self.now_stamp

    def _home_point_altitude_callback(self, msg: Float32):
        if self._home_point_in_utm is None: return
        self._home_point_in_utm.point.z = msg.data


    def _gps_callback(self, msg: NavSatFix):
        if self._geo_altitude is None or self._home_point_in_utm is None:
            self.log(f"Geo Altitude({self._geo_altitude is not None}) or Home({self._home_point_in_utm is not None}) not set, cannot process GPS message.")
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
        self._gps_point_in_home.point.z = self._geo_altitude - self._home_point_in_utm.point.z
        self._gps_point_in_home.header.stamp = self.now_stamp

        if self._utm_labeled_frame is None:
            self._utm_labeled_frame = utm.header.frame_id
            self.log(f"Setting UTM labeled frame to: {self._utm_labeled_frame}")


    def _rtk_cb(self, msg: NavSatFix):
        if self._geo_altitude is None or self._home_point_in_utm is None:
            self.log(f"Geo Altitude({self._geo_altitude is not None}) or Home({self._home_point_in_utm is not None}) not set, cannot process GPS message.")
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
        self._rtk_point_in_home.point.z = self._geo_altitude - self._home_point_in_utm.point.z
        self._rtk_point_in_home.header.stamp = self.now_stamp

        
    def _publish_vehicle_health(self):
        self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_WAITING

        position_ok = self._home_point_in_utm is not None and self._base_pose_in_home is not None
        gps_ok = self._gps_point_in_home is not None and self._home_point_in_utm is not None
        battery_ok = self._battery_percent is not None and self._battery_percent > self.READY_BATTERY_PERCENTAGE
        height_ok = self._height_above_ground is not None and self._height_above_ground > self.READY_HEIGHT_ABOVE_GROUND
        control_ok = self._got_control

        if all([position_ok, gps_ok, battery_ok, height_ok, control_ok]):
            self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_READY


        if self._flying:
            battery_error = self._battery_percent is not None and self._battery_percent < self.ERROR_BATTERY_PERCENTAGE
            height_error = self._height_above_ground is not None and self._height_above_ground < self.ERROR_HEIGHT_ABOVE_GROUND
            if battery_error:
                self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_ERROR
                self.log(f"BATTERY BELOW LIMIT: {self._battery_percent:.2f} < {self.ERROR_BATTERY_PERCENTAGE:.2f}")

            if height_error:
                self._vehicle_health.data = SmarcTopics.VEHICLE_HEALTH_ERROR
                self.log(f"HEIGHT BELOW LIMIT: {self._height_above_ground:.2f} < {self.ERROR_HEIGHT_ABOVE_GROUND:.2f}")


        self._vehicle_health_pub.publish(self._vehicle_health)
            
    
    def _publish_tf(self):
        if self._base_pose_in_home is None or self._home_point_in_utm is None or self._gps_point_in_home is None:
            self.log(f"Position({self._base_pose_in_home is not None}),\
home({self._home_point_in_utm is not None}) or GPS({self._gps_point_in_home is not None})\
not set, skipping TF publish.")
            return

        tf_msg = TFMessage()
        tf_msg.transforms = []
        now = self.now_stamp

        # 0 transforms for home -> map, home -> odom
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

        # Home point in UTM
        home_tf = TransformStamped()
        home_tf.header.stamp = now
        home_tf.header.frame_id = self.UTM_FRAME
        home_tf.child_frame_id = self.HOME_FRAME
        home_tf.transform.translation.x = self._home_point_in_utm.point.x
        home_tf.transform.translation.y = self._home_point_in_utm.point.y
        home_tf.transform.translation.z = self._home_point_in_utm.point.z
        home_tf.transform.rotation.w = 1.0

        # Base in odom
        base_in_home = TransformStamped()
        base_in_home.header.stamp = now
        base_in_home.header.frame_id = self.ODOM_FRAME
        base_in_home.child_frame_id = self.BASE_FRAME
        base_in_home.transform.translation.x = self._base_pose_in_home.pose.position.x
        base_in_home.transform.translation.y = self._base_pose_in_home.pose.position.y
        base_in_home.transform.translation.z = self._base_pose_in_home.pose.position.z
        base_in_home.transform.rotation = self._base_pose_in_home.pose.orientation

        tf_msg.transforms.append(base_in_home)

        

        tf_msg.transforms.append(home_tf)

        # GPS point in Home
        gps_tf = TransformStamped()
        gps_tf.header.stamp = now
        gps_tf.header.frame_id = self.ODOM_FRAME
        gps_tf.child_frame_id = self._tf_ns + "gps_point"
        gps_tf.transform.translation.x = self._gps_point_in_home.point.x
        gps_tf.transform.translation.y = self._gps_point_in_home.point.y
        gps_tf.transform.translation.z = self._gps_point_in_home.point.z
        gps_tf.transform.rotation.w = 1.0


        # RTK point in odom
        if self._rtk_point_in_home is not None:
            rtk_tf = TransformStamped()
            rtk_tf.header.stamp = now
            rtk_tf.header.frame_id = self.ODOM_FRAME
            rtk_tf.child_frame_id = self._tf_ns + "rtk_point"
            rtk_tf.transform.translation.x = self._rtk_point_in_home.point.x
            rtk_tf.transform.translation.y = self._rtk_point_in_home.point.y
            rtk_tf.transform.translation.z = self._rtk_point_in_home.point.z
            rtk_tf.transform.rotation.w = 1.0
            tf_msg.transforms.append(rtk_tf)
        
        
        tf_msg.transforms.append(gps_tf)

        # ground in base
        ground_in_base = TransformStamped()
        ground_in_base.header.stamp = now
        ground_in_base.header.frame_id = self.BASE_FRAME
        ground_in_base.child_frame_id = self._tf_ns + "ground"
        ground_in_base.transform.translation.x = 0.0
        ground_in_base.transform.translation.y = 0.0
        ground_in_base.transform.translation.z = -self._height_above_ground if self._height_above_ground is not None else 0.0

        tf_msg.transforms.append(ground_in_base)

        self._tf_pub.publish(tf_msg)

    def _publish_smarc(self):
        if self._base_pose_in_home is None or self._home_point_in_utm is None or self._gps_point_in_home is None:
            self.log(f"Position({self._base_pose_in_home is not None}),\
home({self._home_point_in_utm is not None}) or GPS({self._gps_point_in_home is not None})\
not set, skipping SMaRC publish.")
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

        # we need current position in latlon
        # so we first need to convert our odom-frame position to UTM
        if self._home_point_in_utm is None or self._base_pose_in_home is None:
            self.log("Home point or base pose not set, cannot publish latlon position.")
            return
        base_in_utm = PointStamped()
        base_in_utm.header.frame_id = self._utm_labeled_frame
        base_in_utm.point.x = self._base_pose_in_home.pose.position.x + self._home_point_in_utm.point.x
        base_in_utm.point.y = self._base_pose_in_home.pose.position.y + self._home_point_in_utm.point.y
        base_in_utm.point.z = self._base_pose_in_home.pose.position.z + self._home_point_in_utm.point.z
        base_in_geopoint = convert_utm_to_latlon(base_in_utm)
        self._pos_latlon_pub.publish(base_in_geopoint)

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
            
        if self._height_above_ground is not None:
            self._altitude_pub.publish(Float32(data=self._height_above_ground))

        

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
        return f"(roll={math.degrees(rpy[0]):.3f}, pitch={math.degrees(rpy[1]):.3f}, yaw={math.degrees(rpy[2]):.3f}, " \
               f"x={pose.pose.position.x:.3f}, y={pose.pose.position.y:.3f}, z={pose.pose.position.z:.3f}, " \
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