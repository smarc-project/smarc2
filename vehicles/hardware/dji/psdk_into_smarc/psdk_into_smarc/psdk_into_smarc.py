#!/usr/bin/python3

import rclpy, sys
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from smarc_msgs.msg import Topics as SmarcTopics
from sensor_msgs.msg import NavSatFix, Joy
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32
from geometry_msgs.msg import TwistStamped, Pose, PoseStamped, TransformStamped, QuaternionStamped, PointStamped
from geographic_msgs.msg import GeoPoint
from tf2_msgs.msg import TFMessage

from smarc_utilities.georef_utils import convert_latlon_to_utm

from psdk_interfaces.msg import PositionFused

from enum import Enum
import math
from geodesy import utm
from tf_transformations import euler_from_quaternion

class PSDKTopics(Enum):
    # these are hardcoded topics in PSDK bridge...
    GPS_POSITION_FUSED = "gps_position_fused"
    POSTION_FUSED = "position_fused"
    # ATTITUDE = "attitude"

    # GPS_VELOCITY = "gps_velocity"
    # RTK_VELOCITY = "rtk_velocity"
    # RTK_POSITION = "rtk_position"
    # ALTITUDE = "altitude"

    # # control input to the drone
    # # all are Joy messages, and relative to drone's body frame
    # # basically replicates a joystick push, there is no position control!
    # CONTROL_FLU_VEL_YAWRATE = "flight_control_setpoint_FLUvelocity_yawrate"
    # CONTROL_ENU_VEL_YAWRATE = "flight_control_setpoint_ENUvelocity_yawrate"
    # CONTROL_ENU_POS_YAW = "flight_control_setpoint_ENUposition_yaw"



class PsdkToSmarc():
    def __init__(self, node: Node):
        self._node = node

        self._origin_utm : PointStamped = PointStamped()
        self._position_in_map : PoseStamped = PoseStamped()

        self._wrapper_ns = "/Quadrotor/wrapper/psdk_ros2/"
        self._tf_ns = "Quadrotor/"

        # self._odom_pub = node.create_publisher(
        #     Odometry,
        #     SmarcTopics.ODOM_TOPIC,
        #     qos_profile=10
        # )

        # self._odom_timer = node.create_timer(
        #     0.1,  # 10 Hz
        #     self._odom_tf_timer_callback
        # )

        

        # self._heading_pub = node.create_publisher(
        #     Float32,
        #     SmarcTopics.HEADING_TOPIC,
        #     qos_profile=10
        # )

        # self._speed_pub = node.create_publisher(
        #     Float32,
        #     SmarcTopics.SPEED_TOPIC,
        #     qos_profile=10
        # )

        # self._pos_latlon_pub = node.create_publisher(
        #     NavSatFix,
        #     SmarcTopics.POS_LATLON_TOPIC,
        #     qos_profile=10
        # )

        # self._alt_pub = node.create_publisher(
        #     Float32,
        #     SmarcTopics.ALTITUDE_TOPIC,
        #     qos_profile=10
        # )

        # self._tf_pub = node.create_publisher(
        #     TFMessage,
        #     "/tf",
        #     qos_profile=10
        # )

        # self._control_pub = node.create_publisher(
        #     Joy,
        #     self._wrapper_ns + PSDKTopics.CONTROL_FLU_VEL_YAWRATE.value,
        #     qos_profile=10
        # )

    
        
        node.create_subscription(
            NavSatFix,
            self._wrapper_ns + PSDKTopics.GPS_POSITION_FUSED.value,
            # self._wrapper_ns + PSDKTopics.RTK_POSITION.value,
            self._gps_callback,
            qos_profile=10
        )

     

        # node.create_subscription(
        #     QuaternionStamped,
        #     self._wrapper_ns + PSDKTopics.ATTITUDE.value,
        #     self._attitude_callback,
        #     qos_profile=10
        # )


        # node.create_subscription(
        #     TwistStamped,
        #     # self._wrapper_ns + PSDKTopics.VELOCITY_GROUND_FUSED.value,
        #     # self._wrapper_ns + PSDKTopics.RTK_VELOCITY.value,
        #     self._wrapper_ns + PSDKTopics.GPS_VELOCITY.value,
        #     self._velocity_callback,
        #     qos_profile=10
        # )


        
        # node.create_subscription(
        #     Joy,
        #     "/joy",
        #     self._joy_callback,
        #     qos_profile=10
        # )


    # def _joy_callback(self, msg: Joy):
    #     self._control_pub.publish(msg)


    def _gps_callback(self, msg: NavSatFix):
        gp = GeoPoint(
            latitude=msg.latitude,
            longitude=msg.longitude,
            altitude=msg.altitude
        )

        if self._origin_utm.header.frame_id == "":
            self._origin_utm = convert_latlon_to_utm(gp)

       


    # def _velocity_callback(self, msg: TwistStamped):
    #     self._velocity = msg.twist.linear
    #     vx, vy = self._velocity.x, self._velocity.y
    #     self._speed_pub.publish(Float32(data=math.sqrt(vx**2 + vy**2)))


    # def _attitude_callback(self, msg):
    #     # the attitude is in ENU by psdk definition, so we need to convert it to NED (compasses use this...)
    #     # and the use the z component as heading
    #     rpy_enu = euler_from_quaternion([msg.quaternion.x, msg.quaternion.y, msg.quaternion.z, msg.quaternion.w])
    #     heading = 90 - math.degrees(rpy_enu[2])
    #     self._heading_pub.publish(Float32(data=heading))


    # def _odom_tf_timer_callback(self):
    #     if self._position_geopoint is None or self._velocity is None:
    #         self._node.get_logger().warn(f"Position or velocity not set, skipping odom publish. Position: {self._position_geopoint}, Velocity: {self._velocity}")
    #         return

    #     odom_msg = Odometry()
    #     odom_msg.header.stamp = self._node.get_clock().now().to_msg()
    #     odom_msg.header.frame_id = self._tf_ns+"odom"
    #     odom_msg.child_frame_id = self._tf_ns+"base_link"

    #     utm_position = self.convert_to_utm(self._position_geopoint)

    #     odom_msg.pose.pose.position.x = utm_position.pose.position.x - self._origin_utm.pose.position.x
    #     odom_msg.pose.pose.position.y = utm_position.pose.position.y - self._origin_utm.pose.position.y
    #     odom_msg.pose.pose.position.z = utm_position.pose.position.z - self._origin_utm.pose.position.z
    #     odom_msg.header.stamp = odom_msg.header.stamp
    #     odom_msg.header.frame_id = odom_msg.header.frame_id

    #     odom_msg.twist.twist.linear = self._velocity

    #     # might as well publish the same thing to TF too...
    #     tf_msg = TFMessage()
    #     base_in_odom = TransformStamped()
    #     base_in_odom.header.stamp = odom_msg.header.stamp
    #     base_in_odom.header.frame_id = odom_msg.header.frame_id
    #     base_in_odom.child_frame_id = odom_msg.child_frame_id
    #     base_in_odom.transform.translation.x = odom_msg.pose.pose.position.x
    #     base_in_odom.transform.translation.y = odom_msg.pose.pose.position.y
    #     base_in_odom.transform.translation.z = odom_msg.pose.pose.position.z
    #     base_in_odom.transform.rotation = odom_msg.pose.pose.orientation

    #     # 0-transform for map->odom
    #     odom_in_map = TransformStamped()
    #     odom_in_map.header.stamp = odom_msg.header.stamp
    #     odom_in_map.header.frame_id = self._tf_ns+"map"
    #     odom_in_map.child_frame_id = self._tf_ns+"odom"

    #     # map in utm
    #     map_in_utm = TransformStamped()
    #     map_in_utm.header.stamp = odom_msg.header.stamp
    #     map_in_utm.header.frame_id = self._origin_utm.header.frame_id
    #     map_in_utm.child_frame_id = self._tf_ns+"map"
    #     map_in_utm.transform.translation.x = self._origin_utm.pose.position.x
    #     map_in_utm.transform.translation.y = self._origin_utm.pose.position.y
    #     map_in_utm.transform.translation.z = self._origin_utm.pose.position.z
    #     map_in_utm.transform.rotation = self._origin_utm.pose.orientation

    #     tf_msg.transforms = [base_in_odom, odom_in_map, map_in_utm]
        
    #     self._tf_pub.publish(tf_msg)
    #     self._odom_pub.publish(odom_msg)
    


    
def main():
    rclpy.init(args=sys.argv)
    node = Node("psdk_to_smarc")

    psdk_to_smarc = PsdkToSmarc(node)

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()