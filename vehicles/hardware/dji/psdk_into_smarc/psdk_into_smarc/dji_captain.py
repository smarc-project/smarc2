#!/usr/bin/python3

import rclpy, sys, math
from enum import Enum


from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor


from psdk_interfaces.msg import PositionFused
from smarc_msgs.msg import Topics as SmarcTopics
from sensor_msgs.msg import NavSatFix, Joy
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32
from geometry_msgs.msg import TwistStamped, Pose, PoseStamped, TransformStamped, QuaternionStamped, PointStamped
from geographic_msgs.msg import GeoPoint
from tf2_msgs.msg import TFMessage

from smarc_utilities.georef_utils import convert_latlon_to_utm
from tf_transformations import euler_from_quaternion


class PSDKTopics(Enum):
    # these are hardcoded topics in PSDK bridge...
    WRAPPER_NS = "/Quadrotor/wrapper/psdk_ros2/"
    
    GPS_POSITION  = WRAPPER_NS + "gps_position"
    POSITION_FUSED = WRAPPER_NS + "position_fused"
    ATTITUDE      = WRAPPER_NS + "attitude"
    HOME_POINT    = WRAPPER_NS + "home_point"
    HOME_POINT_ALTITUDE = WRAPPER_NS + "home_point_altitude"
    ALTITUDE      = WRAPPER_NS + "altitude_sea_level"



class DjiCaptain():
    def __init__(self, node: Node):
        self._node = node
        self._tf_ns = "Quadrotor/"

        self._position_in_home : PoseStamped | None = None
        self._home_in_utm : PointStamped | None = None
        self._gps_in_home : PointStamped | None = None
        self._altitude : Float32 | None = None
        self._heading : Float32 = Float32()
        self._course : Float32 = Float32()

        self._utm_labeled_frame : str | None = None

        

        self._tf_pub = node.create_publisher(
            TFMessage,
            "/tf",
            qos_profile=10
        )

        self.tf_timer = node.create_timer(
            1,  # 10 Hz
            self.publish_tf
        )

        node.create_subscription(
            NavSatFix,
            PSDKTopics.GPS_POSITION.value,
            # self._wrapper_ns + PSDKTopics.RTK_POSITION.value,
            self._gps_callback,
            qos_profile=10
        )

        node.create_subscription(
            PositionFused,
            PSDKTopics.POSITION_FUSED.value,
            self._position_fused_callback,
            qos_profile=10
        )

        node.create_subscription(
            NavSatFix,
            PSDKTopics.HOME_POINT.value,
            self._home_point_callback,
            qos_profile=10
        )
        node.create_subscription(
            Float32,
            PSDKTopics.HOME_POINT_ALTITUDE.value,
            self._home_point_altitude_callback,
            qos_profile=10
        )

        node.create_subscription(
            QuaternionStamped,
            PSDKTopics.ATTITUDE.value,
            self._attitude_callback,
            qos_profile=10
        )

        node.create_subscription(
            Float32,
            PSDKTopics.ALTITUDE.value,
            lambda msg: setattr(self, "_altitude", msg),
            qos_profile=10
        )


    @property
    def now_stamp(self):
        return self._node.get_clock().now().to_msg()
    
    def log(self, msg: str):
        self._node.get_logger().info(msg)


    def _position_fused_callback(self, msg: PositionFused):
        if self._home_in_utm is None:
            self.log("Home point not set, cannot process position fused message.")
            return
        
        if self._position_in_home is None:
            self._position_in_home = PoseStamped()
            self._position_in_home.header.frame_id = msg.header.frame_id
            
        self._position_in_home.pose.position.x = msg.position.x
        self._position_in_home.pose.position.y = msg.position.y
        self._position_in_home.pose.position.z = msg.position.z - self._home_in_utm.point.z
        self._position_in_home.header.stamp = self.now_stamp
        

    def _attitude_callback(self, msg: QuaternionStamped):
        # the attitude is in ENU by psdk definition, so we need to convert it to NED (compasses use this...)
        # and the use the z component as heading
        if self._position_in_home is None:
            self._position_in_home = PoseStamped()
            self._position_in_home.header.frame_id = msg.header.frame_id

        rpy_enu = euler_from_quaternion([msg.quaternion.x, msg.quaternion.y, msg.quaternion.z, msg.quaternion.w])
        self._heading.data = 90 - math.degrees(rpy_enu[2])
        self._position_in_home.pose.orientation = msg.quaternion
        

    def _home_point_callback(self, msg: NavSatFix):
        if self._home_in_utm is None:
            self._home_in_utm = PointStamped()
            self._home_in_utm.header.frame_id = "utm"

        gp = GeoPoint()
        gp.latitude = math.degrees(msg.latitude) # for some reason these are in radians...
        gp.longitude = math.degrees(msg.longitude)
        gp.altitude = msg.altitude
        utm = convert_latlon_to_utm(gp)
        self._home_in_utm.point.x = utm.point.x
        self._home_in_utm.point.y = utm.point.y
        self._home_in_utm.header.stamp = self.now_stamp

    def _home_point_altitude_callback(self, msg: Float32):
        if self._home_in_utm is None: return
        self._home_in_utm.point.z = msg.data


    def _gps_callback(self, msg: NavSatFix):
        if self._altitude is None or self._home_in_utm is None:
            self.log("Altitude or Home not set, cannot process GPS message.")
            return
        
        if self._gps_in_home is None:
            self._gps_in_home = PointStamped()
            self._gps_in_home.header.frame_id = "utm"

        gp = GeoPoint()
        gp.latitude = msg.latitude
        gp.longitude = msg.longitude
        gp.altitude = msg.altitude
        utm = convert_latlon_to_utm(gp)
        self._gps_in_home.point.x = utm.point.x - self._home_in_utm.point.x
        self._gps_in_home.point.y = utm.point.y - self._home_in_utm.point.y
        self._gps_in_home.point.z = self._altitude.data - self._home_in_utm.point.z
        self._gps_in_home.header.stamp = self.now_stamp

        if self._utm_labeled_frame is None:
            self._utm_labeled_frame = utm.header.frame_id
            self.log(f"Setting UTM labeled frame to: {self._utm_labeled_frame}")


    
    def publish_tf(self):
        if self._position_in_home is None or self._home_in_utm is None or self._gps_in_home is None:
            self.log("Position, home or GPS not set, skipping TF publish.")
            return

        tf_msg = TFMessage()
        tf_msg.transforms = []
        now = self.now_stamp

        # Base in Home
        base_in_home = TransformStamped()
        base_in_home.header.stamp = now
        base_in_home.header.frame_id = self._tf_ns + "home_point"
        base_in_home.child_frame_id = self._tf_ns + "base_link"
        base_in_home.transform.translation.x = self._position_in_home.pose.position.x
        base_in_home.transform.translation.y = self._position_in_home.pose.position.y
        base_in_home.transform.translation.z = self._position_in_home.pose.position.z
        base_in_home.transform.rotation = self._position_in_home.pose.orientation

        tf_msg.transforms.append(base_in_home)

        # Home point in UTM
        home_tf = TransformStamped()
        home_tf.header.stamp = now
        home_tf.header.frame_id = "utm"
        home_tf.child_frame_id = self._tf_ns + "home_point"
        home_tf.transform.translation.x = self._home_in_utm.point.x
        home_tf.transform.translation.y = self._home_in_utm.point.y
        home_tf.transform.translation.z = self._home_in_utm.point.z
        home_tf.transform.rotation.w = 1.0

        tf_msg.transforms.append(home_tf)

        # GPS point in UTM
        gps_tf = TransformStamped()
        gps_tf.header.stamp = now
        gps_tf.header.frame_id = self._tf_ns + "home_point"
        gps_tf.child_frame_id = self._tf_ns + "gps_point"
        gps_tf.transform.translation.x = self._gps_in_home.point.x
        gps_tf.transform.translation.y = self._gps_in_home.point.y
        gps_tf.transform.translation.z = self._gps_in_home.point.z
        gps_tf.transform.rotation.w = 1.0
        
        tf_msg.transforms.append(gps_tf)

        # 0 transforms for home -> map, home -> odom
        # for compatibility with other systems
        map_in_home = TransformStamped()
        map_in_home.header.stamp = now
        map_in_home.header.frame_id = self._tf_ns + "home_point"
        map_in_home.child_frame_id = self._tf_ns + "map"
        tf_msg.transforms.append(map_in_home)

        odom_in_home = TransformStamped()
        odom_in_home.header.stamp = now
        odom_in_home.header.frame_id = self._tf_ns + "home_point"
        odom_in_home.child_frame_id = self._tf_ns + "odom"
        tf_msg.transforms.append(odom_in_home)


        self._tf_pub.publish(tf_msg)
        

    
def main():
    rclpy.init(args=sys.argv)
    node = Node("DjiCaptainNode")
    capt = DjiCaptain(node)

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()