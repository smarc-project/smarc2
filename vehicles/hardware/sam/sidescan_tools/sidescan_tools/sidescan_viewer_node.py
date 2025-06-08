#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from functools import partial
from smarc_msgs.msg import Sidescan


class SidescanViewer(Node):
    def __init__(self):
        super().__init__('sidescan_viewer')
        self.declare_parameter('image_height', 1000)
        self.declare_parameter('image_width', 1000)

        self.image_height = self.get_parameter('image_height').value
        self.image_width = self.get_parameter('image_width').value

        self.img = np.zeros((self.image_height, 2 * self.image_width), dtype=np.ubyte)
        cv2.namedWindow('Sidescan image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Sidescan image', 2 * 256, self.image_height)

        self.subscription = self.create_subscription(
            Sidescan,
            '/sam/payload/sidescan',
            partial(self.callback, self.img),
            10
        )

        self.timer = self.create_timer(0.2, self.timer_callback)

    def callback(self, img, msg):
        port = np.array(bytearray(msg.port_channel), dtype=np.ubyte)
        stbd = np.array(bytearray(msg.starboard_channel), dtype=np.ubyte)
        meas = np.concatenate([np.flip(port), stbd])
        # print(meas)

        img[1:, :] = img[:-1, :]
        img[0, :] = meas

    def timer_callback(self):
        resized = cv2.resize(self.img, (2 * 256, self.image_height), interpolation=cv2.INTER_AREA)
        cv2.imshow("Sidescan image", resized)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = SidescanViewer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
