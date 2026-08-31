import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist
from mavros_msgs.msg import ManualControl, State
from mavros_msgs.srv import CommandBool, SetMode


class ActiveHookCaptain(Node):

    def __init__(self):
        super().__init__('active_hook_captain')

        # TODO: yayıncılar (joy_rov_publisher, manual_control_publisher)

        # TODO: dinleyiciler (joy_subscriber, twist_subscriber, state_subscriber)

        # TODO: servis istemcileri (arming_client, set_mode_client)

        # TODO: durum değişkenleri (previous_button_states, current_mode, current_armed)

    # === A) Joystick ön işleme ===
    def joy_callback(self, msg):
        pass

    def handle_buttons(self, msg):
        pass

    # === B) Komut çevirisi ===
    def twist_callback(self, msg):
        pass

    @staticmethod
    def shape_axis(value, scale):
        pass

    # === C) MAVROS durum takibi ===
    def state_callback(self, msg):
        pass

    # === D) MAVROS servis çağrıları ===
    def send_arm_command(self, arm):
        pass

    def send_mode_command(self, mode_name):
        pass


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