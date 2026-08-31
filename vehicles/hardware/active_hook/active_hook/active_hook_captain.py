import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist
from mavros_msgs.msg import ManualControl, State
from mavros_msgs.srv import CommandBool, SetMode

ARM_BUTTON = 9              # OPTIONS
DISARM_BUTTON = 8           # CREATE

MANUAL_MODE_BUTTON = 3      # SQUARE
STABILIZE_MODE_BUTTON = 2   # TRIANGLE
DEPTH_HOLD_MODE_BUTTON = 1  # CIRCLE


class ActiveHookCaptain(Node):

    def __init__(self):
        super().__init__('active_hook_captain')

        # TODO: yayıncılar (joy_rov_publisher, manual_control_publisher)
        self.joy_rov_publisher = self.create_publisher(Joy, 'joy_rov', 10)
        self.manual_control_publisher = self.create_publisher(ManualControl, 'mavros/manual_control/control', 10)

        # TODO: dinleyiciler (joy_subscriber, twist_subscriber, state_subscriber)
        self.joy_subscriber = self.create_subscription(Joy, 'joy', self.joy_callback, 10)
        self.twist_subscriber = self.create_subscription(Twist, 'cmd_vel', self.twist_callback, 10)
        self.state_subscriber = self.create_subscription(State, 'mavros/state', self.state_callback, 10)

        # TODO: servis istemcileri (arming_client, set_mode_client)
        self.arming_client = self.create_client(CommandBool, 'mavros/cmd/arming')
        self.set_mode_client = self.create_client(SetMode, 'mavros/set_mode')

        # TODO: durum değişkenleri (previous_button_states, current_mode, current_armed)
        self.previous_button_states = {}
        self.current_mode = ''
        self.current_armed = False      

    # === A) Joystick ön işleme ===
    def joy_callback(self, joy_message):

        l2 = joy_message.axes[2]
        r2 = joy_message.axes[5]
        vertical = (l2 - r2) / 2.0

        new_msg = Joy()
        new_msg.header = joy_message.header
        new_msg.axes = list(joy_message.axes[:6]) + [vertical]
        new_msg.buttons = list(joy_message.buttons)

        self.joy_rov_publisher.publish(new_msg)
        self.handle_buttons(joy_message)


    @staticmethod
    def get_button(joy_message, button_index):
        if button_index < 0 :
            return 0
        if button_index >= len(joy_message.buttons):
            return 0
        return int(joy_message.buttons[button_index])

    def button_pressed_once(self, joy_message, button_index):
        current_state = self.get_button(joy_message, button_index)
        previous_state = self.previous_button_states.get(button_index, 0)
        self.previous_button_states[button_index] = current_state

        return current_state == 1 and previous_state == 0

    def handle_buttons(self, joy_message):
        if self.button_pressed_once(joy_message, ARM_BUTTON):
            self.send_arm_command(True)
        elif self.button_pressed_once(joy_message, DISARM_BUTTON):
            self.send_disarm_command(True)
        elif self.button_pressed_once(joy_message, MANUAL_MODE_BUTTON):
            self.send_mode_command('MANUAL')
        elif self.button_pressed_once(joy_message, STABILIZE_MODE_BUTTON):
            self.send_mode_command('STABILIZE')
        elif self.button_pressed_once(joy_message, DEPTH_HOLD_MODE_BUTTON):
            self.send_mode_command('ALT_HOLD')
    # === B) Komut çevirisi ===
    def twist_callback(self, msg):
        

    @staticmethod
    def shape_axis(value, scale):
        

    # === C) MAVROS durum takibi ===
    def state_callback(self, msg):
        

    # === D) MAVROS servis çağrıları ===
    def send_arm_command(self, arm):
        

    def send_mode_command(self, mode_name):
        


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