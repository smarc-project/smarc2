#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
from smarc_msgs.msg import Sidescan
from sam_msgs.msg import Topics
from functools import partial
import numpy as np
from ctypes import cast, pointer, POINTER, c_char, c_int


def convert(c):
    return cast(pointer(c_char(c)), POINTER(c_int)).contents.value


def callback(img, msg: Sidescan):
    #print msg

    #for p in msg.sidescan.sidescan.port_channel:
    #    print convert(p)

    port = np.array(bytearray(msg.port_channel), dtype=np.ubyte)
    stbd = np.array(bytearray(msg.starboard_channel), dtype=np.ubyte)
    #port = np.array([int(p) for p in msg.sidescan.sidescan.port_channel]) # dtype=np.ubyte)
    #stbd = np.array([int(p) for p in msg.sidescan.sidescan.starboard_channel])
    #stbd = np.array(msg.sidescan.sidescan.starboard_channel, dtype=float) #dtype=np.ubyte)
    #print port.shape, stbd.shape
    #print port, stbd
    meas = np.concatenate([np.flip(port), stbd])
    print(meas)
    img[1:, :] = img[:-1, :]
    img[0, :] = meas


def main(args = None):
    rclpy.init(args=args)
    node = Node('sss_viewer')

    img = np.zeros((1000, 2 * 1000), dtype=np.ubyte)  # dtype=float) #
    cv2.namedWindow('Sidescan image', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Sidescan image', 2 * 256, 1000)

    sub = node.create_subscription(Sidescan,f"sam/{Topics.SIDESCAN_TOPIC}", partial(callback, img),qos_profile=10)

    # spin() simply keeps python from exiting until this node is stopped
    # r = rclpy.Rate(5)  # 10hz
    try:
        while rclpy.ok():
            rclpy.spin_once(node,timeout_sec=0.1)
            resized = cv2.resize(img, (2 * 256, 1000), interpolation=cv2.INTER_AREA)
            cv2.imshow("Sidescan image", resized)
            cv2.waitKey(1)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
