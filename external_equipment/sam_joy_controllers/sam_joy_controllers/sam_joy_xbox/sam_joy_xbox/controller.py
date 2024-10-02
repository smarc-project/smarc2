#!/usr/bin/env python3

"""
MIT License

Copyright (c) 2023 Matthew Lock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Interface between Joy messages and the smarc_joy_controller for the Xbox controller

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from sensor_msgs.msg import Joy
from sam_msgs.msg import JoyButtons
from rclpy.qos import QoSProfile
import threading

from evdev import ecodes
from evdev import InputDevice
from evdev import ff
from evdev import util

import time

class xbox_joy(Node):

    def __init__(self):

        super().__init__("ds5_controller")
        

        self.button_pressed_flag = threading.Event()

        self.enable_teleop_pressed = False
        self.enable_assisted_driving_pressed = False

        self.teleop_enabled = False
        self.assisted_driving_enabled = False

        self.declare_parameter("teleop_enable", "/enable")
        teleop_enable_top=self.get_parameter("teleop_enable").value
        self.declare_parameter("assist_enable", "/assist")
        assist_enable_top = self.get_parameter("assist_enable").value

        self.declare_parameter("joy_buttons", "/joy_buttons")
        joy_buttons_top=self.get_parameter("joy_buttons").value

        self.declare_parameter("joy_top", "/joy")
        joy_top = self.get_parameter("joy_top").value
        self.teleop_enabled_pub = self.create_publisher(Bool,teleop_enable_top,  qos_profile=1)
        self.teleop_enabled_pub = self.create_publisher(Bool, teleop_enable_top, QoSProfile(depth=1))

        self.assisted_driving_enabled_pub = self.create_publisher(Bool,assist_enable_top, qos_profile=1)
        self.joy_btn_pub = self.create_publisher(JoyButtons,joy_buttons_top,  qos_profile=1)

        self.joy_sub = self.create_subscription(Joy,joy_top,  self.joy_callback,qos_profile=1)

        self.get_logger().info("[XBOX CONTROLLER] Starting Xbox controller node")

        self.setup_controller()



    def setup_controller(self):

        self.device_file = None
        for name in util.list_devices():
            self.device_file = InputDevice(name)
            if ecodes.EV_FF in self.device_file.capabilities():
                break
        if self.device_file is None:
            # rospy.logerr_once("[XBOX CONTROLLER] Sorry, no FF capable device found")
            self.get_logger().error("[XBOX CONTROLLER] Sorry, no FF capable device found")
        self.load_effects()

    def load_effects(self):
        """
        Load the effects for the controller
        Taken from https://github.com/atar-axis/xpadneo/blob/master/misc/examples/python_asyncio_evdev/gamepad.py
        """
        try:
            # Effect 1, light rumble
            rumble = ff.Rumble(strong_magnitude=0xc000, weak_magnitude=0x500)
            duration_ms = 300
            effect = ff.Effect(
                ecodes.FF_RUMBLE, -1, 0, ff.Trigger(0, 0),
                ff.Replay(duration_ms, 0), ff.EffectType(ff_rumble_effect=rumble)
            )
            self.effect1_id = self.device_file.upload_effect(effect)
            self.get_logger().info(f"Effect 1 uploaded with id {self.effect1_id}")

            # Effect 2, strong rumble
            rumble = ff.Rumble(strong_magnitude=0xc000, weak_magnitude=0x0000)
            duration_ms = 200
            effect = ff.Effect(
                ecodes.FF_RUMBLE, -1, 0, ff.Trigger(0, 0),
                ff.Replay(duration_ms, 0), ff.EffectType(ff_rumble_effect=rumble)
            )
            self.effect2_id = self.device_file.upload_effect(effect)
            self.get_logger().info(f"Effect 2 uploaded with id {self.effect2_id}")
        except Exception as e:
            self.get_logger().error(f"Error loading effects: {e}")

    # ================================================================================
    # Callbacks
    # ================================================================================

    def joy_callback(self, msg:Joy):
        """
        Callback function for the joystick subscriber
        """
        teleop_btn_pressed = msg.buttons[0] == 1
        assited_driving_pressed = msg.buttons[3] == 1

        if teleop_btn_pressed and not self.enable_teleop_pressed:
            self.teleop_enabled = not self.teleop_enabled
            self.enable_teleop_pressed = True
            self.get_logger().info(f"[XBOX CONTROLLER] Teleop enabled: {format(self.teleop_enabled)}")
            teleop_enabled_msg = Bool()
            teleop_enabled_msg.data = self.teleop_enabled
            self.teleop_enabled_pub.publish(teleop_enabled_msg)
            if self.teleop_enabled:
                self.rumble(1)
            else:
                self.rumble(2)
                

        if assited_driving_pressed and not self.enable_assisted_driving_pressed:
            self.assisted_driving_enabled = not self.assisted_driving_enabled
            self.enable_assisted_driving_pressed = True
            self.get_logger().info(f"[XBOX CONTROLLER] Assisted driving enabled: {format(self.assisted_driving_enabled)}")
            assisted_driving_enabled_msg = Bool()
            assisted_driving_enabled_msg.data = self.assisted_driving_enabled
            self.assisted_driving_enabled_pub.publish(self.assisted_driving_enabled)
            if self.assisted_driving_enabled:
                self.rumble(1)
            else:
                self.rumble(2)

        if not teleop_btn_pressed:
            self.enable_teleop_pressed = False

        if not assited_driving_pressed:
            self.enable_assisted_driving_pressed = False
            
        joy_buttons_msg = JoyButtons()
        joy_buttons_msg.header.stamp = self.get_clock().now().to_msg()
        joy_buttons_msg.header.frame_id = "xbox_controller"
        joy_buttons_msg.left_x = msg.axes[0]
        joy_buttons_msg.left_y = msg.axes[1]
        joy_buttons_msg.right_x = msg.axes[3]
        joy_buttons_msg.right_y = msg.axes[4]

        joy_buttons_msg.teleop_enable = msg.buttons[0] == 1
        joy_buttons_msg.assited_driving = msg.buttons[3] == 1

        joy_buttons_msg.d_down = msg.axes[7] == -1
        joy_buttons_msg.d_up = msg.axes[7] == 1
        joy_buttons_msg.d_left = msg.axes[6] == 1
        joy_buttons_msg.d_right = msg.axes[6] == -1

        joy_buttons_msg.shoulder_l1 = msg.buttons[4] == 1
        joy_buttons_msg.shoulder_l2 = msg.axes[2]
        joy_buttons_msg.shoulder_r1 = msg.buttons[5] == 1
        joy_buttons_msg.shoulder_r2 = msg.axes[5]
        self.joy_btn_pub.publish(joy_buttons_msg)


    # ================================================================================
    # Controller Function
    # ================================================================================

    def rumble(self, no_pulses = 1):
        """
        Set the rumble motors on the controller
        
        Parameters
        ----------
        left_motor : int
            Left motor speed between 0 and 255
        right_motor : int
            Right motor speed between 0 and 255
        """

        repeat_count = no_pulses
        self.device_file.write(ecodes.EV_FF, self.effect1_id, repeat_count)
def main(args=None):    
    rclpy.init(args=args)
    xbox_controller = xbox_joy()
    try:
        rclpy.spin(xbox_controller)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()


