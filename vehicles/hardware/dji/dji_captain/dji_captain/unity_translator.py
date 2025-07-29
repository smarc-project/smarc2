import rclpy, sys, math
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

class Translator(Node):
    def __init__(self):
        super().__init__('translator')

        self._pos_fused_pub = self.create_publisher(PositionFused, PSDKTopics.POSITION_FUSED.value, 10)
        self._pos_fused_sub = self.create_subscription(
            Odometry, 
            'odom_gt',
            self._pos_fused_callback,
            10)
        self._esc_data_pub = self.create_publisher(EscData, PSDKTopics.ESC_DATA.value, 10)
        self._esc_data_timer = self.create_timer(1, self._esc_pub_callback)
        self._joy_pub = self.create_publisher(Vector3Stamped, "sim/joy", 10)
        self._joy_sub = self.create_subscription(
            Joy,
            PSDKTopics.FLU_JOY.value,
            self._joy_callback,
            10)

        self._takeoff_serv = self.create_service(Trigger, PSDKTopics.TAKEOFF_SRV.value, self._takeoff_srv_callback)
        self._takeoff_pub = self.create_publisher(Float32, "sim/target_alt", 10)
        self._take_control_serv = self.create_service(Trigger, PSDKTopics.TAKE_CONTROL_SRV.value, self._take_control_srv_callback)
        self._release_control_serv = self.create_service(Trigger, PSDKTopics.RELEASE_CONTROL_SRV.value, self._release_control_srv_callback)

        self._control_mode_pub = self.create_publisher(ControlMode, PSDKTopics.CONTROL_MODE.value, qos_profile=10)
        self._control_mode_sim_pub = self.create_publisher(Int8, "sim/control_mode", 10)
        self._control_mode_timer = self.create_timer(1, self._control_mode_pub_callback)
        self.control = 0


    def _pos_fused_callback(self, msg: Odometry):
        position_fused : PositionFused = PositionFused()
        position_fused.position.x = msg.pose.pose.position.x
        position_fused.position.y = msg.pose.pose.position.y
        position_fused.position.z = msg.pose.pose.position.z
        position_fused.header = msg.header
        self._pos_fused_pub.publish(position_fused)

    def _esc_pub_callback(self):
        dummy_ESC = EscStatusIndividual()
        dummy_ESC.speed = 4000
        esc_data = EscData()
        for i in range(6):
            esc_data.esc.append(dummy_ESC)
        self._esc_data_pub.publish(esc_data)

    def _joy_callback(self, msg):
        joy_vec = Vector3Stamped()
        joy_vec.header = msg.header
        joy_vec.vector.x = msg.axes[0]
        joy_vec.vector.y = msg.axes[1]
        joy_vec.vector.z = msg.axes[2]
        self._joy_pub.publish(joy_vec)

    def _takeoff_srv_callback(self, request, response):
        response.success = True
        self._takeoff_pub.publish(Float32(data = 5.0))
        return response
    
    def _take_control_srv_callback(self, request, response):
        self.control = 1
        response.success = True
        return response
    
    def _release_control_srv_callback(self, request, response):
        self.control = 0
        response.success = True
        return response


    def _control_mode_pub_callback(self):
        dummy_control_mode = ControlMode()
        dummy_control_mode.control_auth = self.control
        dummy_control_mode.device_mode = 4
        self._control_mode_pub.publish(dummy_control_mode)
        sim_control = Int8()
        sim_control.data = self.control
        self._control_mode_sim_pub.publish(sim_control)


def main(args=None):
    rclpy.init(args=args)

    translator = Translator()

    rclpy.spin(translator)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    translator.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()