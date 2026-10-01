import math


import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Joy, Imu
from geometry_msgs.msg import Twist, Vector3, TransformStamped
from nav_msgs.msg import Odometry
from std_msgs.msg import Int8
from tf2_ros import TransformBroadcaster

from mavros_msgs.msg import ManualControl, State
from mavros_msgs.srv import CommandBool, SetMode

from active_hook_msgs.msg import Topics as ActiveHookTopics
from smarc_msgs.msg import Topics as SmarcTopics

ARM_BUTTON = 9              # OPTIONS
DISARM_BUTTON = 8           # CREATE

MANUAL_MODE_BUTTON = 3      # SQUARE
STABILIZE_MODE_BUTTON = 2   # TRIANGLE
DEPTH_HOLD_MODE_BUTTON = 1  # CIRCLE

AXIS_YAW = 0        # Left Stick X
AXIS_FORWARD = 1    # Left Stick Y
AXIS_L2 = 2
AXIS_ROLL = 3       # Right Stick X
AXIS_PITCH = 4      # Right Stick Y
AXIS_R2 = 5

EXPO = 1.8

FORWARD_SCALE = 1.0
VERTICAL_SCALE = 1.0

YAW_SCALE = 0.8
PITCH_SCALE = 0.3
ROLL_SCALE = 0.3


def quaternion_to_euler(x: float, y: float, z: float, w: float) -> tuple[float, float, float]:
    # standard quaternion -> roll/pitch/yaw (radians) conversion
    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    sinp = 2.0 * (w * y - z * x)
    if abs(sinp) >= 1.0:
        pitch = math.copysign(math.pi / 2, sinp)  # gimbal lock: clamp to +-90 deg
    else:
        pitch = math.asin(sinp)

    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return roll, pitch, yaw


class ActiveHookCaptain(Node):

    def __init__(self):
        super().__init__('active_hook_captain')

        # (manual_control_publisher)
        self.manual_control_publisher = self.create_publisher(ManualControl, ActiveHookTopics.MAVROS_MANUAL_CONTROL_TOPIC, 10)

        # (joy_subscriber, twist_subscriber, state_subscriber)
        self.joy_subscriber = self.create_subscription(Joy, ActiveHookTopics.JOY_TOPIC, self.joy_callback, 10)
        self.twist_subscriber = self.create_subscription(Twist, ActiveHookTopics.AUTONOMY_CMD_VEL_TOPIC, self.twist_callback, 10)
        self.state_subscriber = self.create_subscription(State, ActiveHookTopics.MAVROS_STATE_TOPIC, self.state_callback, 10)

        # (arming_client, set_mode_client)
        self.arming_client = self.create_client(CommandBool, ActiveHookTopics.MAVROS_ARMING_SRV)
        self.set_mode_client = self.create_client(SetMode, ActiveHookTopics.MAVROS_SET_MODE_SRV)

        # (previous_button_states, current_mode, current_armed)
        self.previous_button_states = {}
        self.current_mode = ''
        self.current_armed = False      

        # smarc pubs
        self._vehicle_health_pub = self.create_publisher(Int8, SmarcTopics.VEHICLE_HEALTH_TOPIC, qos_profile=10)
        self._vehicle_health_timer = self.create_timer(1, self._publish_vehicle_health)

        # --- IMU -> attitude / odom / TF conversion ---
        self.declare_parameter('robot_name', 'ActiveHook')
        self._robot_name = self.get_parameter('robot_name').get_parameter_value().string_value
        self._odom_frame = self._robot_name + '/odom'
        self._base_link_frame = self._robot_name + '/base_link'

        self._attitude_publisher = self.create_publisher(Vector3, ActiveHookTopics.ATTITUDE_TOPIC, 10)
        self._odom_publisher = self.create_publisher(Odometry, ActiveHookTopics.ODOM_TOPIC, 10)
        self._tf_broadcaster = TransformBroadcaster(self)

        # mavros publishes IMU data with "sensor data" QoS (best-effort, volatile).
        # A default (reliable) subscription is NOT compatible with a best-effort
        # publisher -- it silently never receives a message, no error, no crash.
        self.imu_subscriber = self.create_subscription(
            Imu, ActiveHookTopics.MAVROS_IMU_TOPIC, self.imu_callback, qos_profile_sensor_data
        )



    # Joystick 
    def joy_callback(self, joy_message):
        if len(joy_message.axes) < 6:
            return

        vertical = (joy_message.axes[AXIS_L2] - joy_message.axes[AXIS_R2]) / 2.0

        twist = Twist()
        twist.linear.x = joy_message.axes[AXIS_FORWARD]
        twist.linear.z = vertical
        twist.angular.x = joy_message.axes[AXIS_ROLL]
        twist.angular.y = joy_message.axes[AXIS_PITCH]
        # yaw is reversed here to keep the control scheme as wanted -- this
        # must stay local to the joystick path, not inside apply_twist,
        # since apply_twist is shared with autonomy behaviours (e.g.
        # spiral_search) which expect a direct, non-inverted convention:
        # positive angular.z from /cmd_vel should mean increasing yaw.
        twist.angular.z = -joy_message.axes[AXIS_YAW]

        self.apply_twist(twist)
        self.handle_buttons(joy_message)


    def button_pressed_once(self, joy_message, button_index):
        if not (0 <= button_index < len(joy_message.buttons)):
            return False
    
        current_state = int(joy_message.buttons[button_index])
        previous_state = self.previous_button_states.get(button_index, 0)
        self.previous_button_states[button_index] = current_state

        return current_state == 1 and previous_state == 0

    def handle_buttons(self, joy_message):
        if self.button_pressed_once(joy_message, ARM_BUTTON):
            self.send_arm_command(True)
        if self.button_pressed_once(joy_message, DISARM_BUTTON):
            self.send_arm_command(False)
        if self.button_pressed_once(joy_message, MANUAL_MODE_BUTTON):
            self.send_mode_command('MANUAL')
        if self.button_pressed_once(joy_message, STABILIZE_MODE_BUTTON):
            self.send_mode_command('STABILIZE')
        if self.button_pressed_once(joy_message, DEPTH_HOLD_MODE_BUTTON):
            self.send_mode_command('ALT_HOLD')
            

    # velocity (Twist) to manual control conversion.
    # Any axis-convention flipping belongs in the message SOURCE (joy_callback),
    # not here -- this function is shared by the joystick and by autonomy
    # behaviours publishing to /cmd_vel (e.g. spiral_search), so it must apply
    # the same, direct convention to whatever Twist it receives.
    def twist_callback(self, twist_message):
        self.apply_twist(twist_message)

    def apply_twist(self, twist_message):
        forward = self.shape_axis(twist_message.linear.x, FORWARD_SCALE)
        vertical = self.shape_axis(twist_message.linear.z, VERTICAL_SCALE)
        roll = self.shape_axis(twist_message.angular.x, ROLL_SCALE)
        pitch = self.shape_axis(twist_message.angular.y, PITCH_SCALE)
        yaw = self.shape_axis(twist_message.angular.z, YAW_SCALE)
 
        
        manual_message = ManualControl()
        manual_message.header.stamp = self.get_clock().now().to_msg()
 
        manual_message.x = forward * 1000.0
        manual_message.y = 0.0
        manual_message.z = 500 + vertical * 500.0
        manual_message.r = yaw * 1000.0
        manual_message.s = pitch * 1000.0
        manual_message.t = roll * 1000.0
 
        manual_message.buttons = 0
        manual_message.buttons2 = 0
        manual_message.enabled_extensions = 0b00000011
 
        manual_message.aux1 = 0.0
        manual_message.aux2 = 0.0
        manual_message.aux3 = 0.0
        manual_message.aux4 = 0.0
        manual_message.aux5 = 0.0
        manual_message.aux6 = 0.0
 
        self.manual_control_publisher.publish(manual_message)


    @staticmethod
    def shape_axis(value, scale):
        value = max(-1.0, min(1.0, value))
        value = math.copysign(abs(value) ** EXPO, value)
        value *= scale
        return max(-1.0, min(1.0, value))
    

    # MAVROS State 
    def state_callback(self, state_message):
        if state_message.mode != self.current_mode:
            self.current_mode = state_message.mode
            self.get_logger().info(f"Vehicle mode changed to: {self.current_mode}")

        if state_message.armed != self.current_armed:
            self.current_armed = state_message.armed
            arm_state = "ARMED" if self.current_armed else "DISARMED"
            self.get_logger().info(f"Vehicle state changed to: {arm_state}")

    # MAVROS Command Services
    def send_arm_command(self, arm):
        action = "ARM" if arm else "DISARM"

        if not self.arming_client.service_is_ready():
            self.get_logger().warning(f"{action} request ignored: service not available.")
            return

        request = CommandBool.Request()
        request.value = arm
        future = self.arming_client.call_async(request)

        def on_response(completed_future):
            try:
                response = completed_future.result()
                if response.success:
                    self.get_logger().info(f"{action} accepted.")
                else:
                    self.get_logger().warning(f"{action} rejected.")
            except Exception as error:
                self.get_logger().error(f"{action} failed: {error}")

        future.add_done_callback(on_response)

    def send_mode_command(self, mode_name):
        if self.current_mode == mode_name:
            self.get_logger().info(f"Vehicle is already in {mode_name} mode.")
            return

        if not self.set_mode_client.service_is_ready():
            self.get_logger().warning(f"{mode_name} request ignored: service not available.")
            return

        request = SetMode.Request()
        request.base_mode = 0
        request.custom_mode = mode_name
        future = self.set_mode_client.call_async(request)

        def on_response(completed_future):
            try:
                response = completed_future.result()
                if response.mode_sent:
                    self.get_logger().info(f"{mode_name} mode request sent.")
                else:
                    self.get_logger().warning(f"{mode_name} mode request rejected.")
            except Exception as error:
                self.get_logger().error(f"{mode_name} mode service call failed: {error}")

        future.add_done_callback(on_response)


    # IMU -> attitude (deg) / odom / TF
    def imu_callback(self, msg: Imu) -> None:
        q = msg.orientation
        roll, pitch, yaw = quaternion_to_euler(q.x, q.y, q.z, q.w)

        # human-readable angles, in degrees
        angles = Vector3()
        angles.x = math.degrees(roll)
        angles.y = math.degrees(pitch)
        angles.z = math.degrees(yaw)
        self._attitude_publisher.publish(angles)

        # Odometry -- position stays zero, we only have attitude, no position source
        odom = Odometry()
        odom.header = msg.header
        odom.header.frame_id = self._odom_frame
        odom.child_frame_id = self._base_link_frame
        odom.pose.pose.orientation = q
        odom.twist.twist.angular = msg.angular_velocity
        self._odom_publisher.publish(odom)

        # TF broadcast -- rotates base_link relative to Fixed Frame "odom" in RViz
        t = TransformStamped()
        t.header.stamp = msg.header.stamp
        t.header.frame_id = self._odom_frame
        t.child_frame_id = self._base_link_frame
        t.transform.rotation = q
        self._tf_broadcaster.sendTransform(t)


    def _publish_vehicle_health(self):
        #TODO Actually keep tracks of health in some way!
        # At the moment, just a placeholder to act as a heartbeat
        health_msg = Int8()
        health_msg.data = SmarcTopics.VEHICLE_HEALTH_READY
        self._vehicle_health_pub.publish(health_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ActiveHookCaptain()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()