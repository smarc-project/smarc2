#!/usr/bin/env python3
"""
Keyboard control for interfacing with OverrideRCIn
w,s for forward
a,d for lateral
-,+ for throttle
q,r for yaw
up, down for pitch
left, right for roll
"""

import rclpy
from rclpy.node import Node
from mavros_msgs.srv import CommandBool
from mavros_msgs.msg import OverrideRCIn

from pynput import keyboard

class TeleopKeyboardNode(Node):
    def __init__(self):
        super().__init__('teleop_keyboard')

        # Publisher for RC Override
        self.rc_override_pub = self.create_publisher(OverrideRCIn, '/mavros/rc/override', 10)

        # Service clients for arming/disarming
        # self.arming_client = self.create_client(CommandBool, '/mavros/cmd/arming')

        # Timer to continuously check for key presses
        self.timer = self.create_timer(0.01, self.key_loop)

        # Initialize all channels with no change
        self.channels = [OverrideRCIn.CHAN_NOCHANGE] * 18

        self.pos_pwm = 1600
        self.neg_pwm = 1400

    def key_loop(self):
        """ Continuously check for key press and send the correct RC values """
        # CH1: Pitch
        # CH2: Roll
        # CH3: Throttle / Vertical
        # CH4: Yaw
        # CH5: Forward
        # CH6: Lateral

        # Up/down
        if pressed_key == '-': # Up
            self.channels[2] = self.pos_pwm 
            self.get_logger().info("Up")
        elif pressed_key == '+': # Down
            self.channels[2] = self.neg_pwm
            self.get_logger().info("Down")

        elif pressed_key == 'Key.up': # pitch up
            self.channels[0] = self.pos_pwm 
            self.get_logger().info("pitch Up")
        elif pressed_key == 'Key.down': # pitch down
            self.channels[0] = self.neg_pwm
            self.get_logger().info("pitch Down")

        elif pressed_key == 'Key.right': 
            self.channels[1] = self.pos_pwm 
            self.get_logger().info("roll left")
        elif pressed_key == 'Key.left': 
            self.channels[1] = self.neg_pwm
            self.get_logger().info("roll right")

        # Yaw left/right
        elif pressed_key == 'q':
            self.channels[3] = self.neg_pwm  
            self.get_logger().info("Yaw left 'q'")
        elif pressed_key == 'e': 
            self.channels[3] = self.pos_pwm  
            self.get_logger().info("Yaw right 'e'")
        
        # Forward/backwardii
        elif pressed_key == 'w':
            self.channels[4] = self.pos_pwm
            self.get_logger().info("Forward 'w'")
        elif pressed_key == 's':
            self.channels[4] = self.neg_pwm 
            self.get_logger().info("Backward 's'")

        # Left/right
        elif pressed_key == 'a': 
            self.channels[5] = self.neg_pwm  
            self.get_logger().info("Left 'a'")
        elif pressed_key == 'd':
            self.channels[5] = self.pos_pwm 
            self.get_logger().info("Right 'd'")
        
        
        
        # elif pressed_key == 'i':
        #     print("i")
        #     self.channels[13] = 750
        #     #self.channels[13] = 1200
        # elif pressed_key == 'o':
        #     print("o")
        #     self.channels[13] = 1500
        #     self.channels[13] = 1800
        # elif pressed_key == 'p':
        #     print("p")
        #     self.channels[13] = 2250
        #     #self.channels[13] = 2000

        # If nothing pressed, set to no movement
        else:
            self.channels[0] = 1500  
            self.channels[1] = 1500  
            self.channels[2] = 1500  
            self.channels[3] = 1500  
            self.channels[4] = 1500  
            self.channels[5] = 1500
            self.get_logger().info("Nothing pressed")

        self.publish_rc_override()

    def publish_rc_override(self):
        """ Publishes the RC override message with the updated channels """
        msg = OverrideRCIn()
        msg.channels = self.channels
        self.rc_override_pub.publish(msg) 


pressed_key = None  # Variable to hold the currently pressed key

def on_press(key):
    global pressed_key

    try:
        # Standard keys have a 'char' attribute
        pressed_key = key.char
    except AttributeError:
        # Special keys (like space, shift) are captured here
        pressed_key = str(key)

def on_release(key):
    global pressed_key
    # Reset pressed_key when the key is released
    pressed_key = None
    # Stop the loop if 'esc' is released
    if key == keyboard.Key.esc:
        print("Escape key pressed, exiting...")
        return False

def main(args=None):
    rclpy.init(args=args)
    node = TeleopKeyboardNode()
    # Start the listener in a non-blocking way
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
