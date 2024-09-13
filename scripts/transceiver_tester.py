#!/usr/bin/python3

import rclpy, sys, time
import matplotlib.pyplot as plt

from smarc_msgs.msg import StringStamped

def sub():
    print("Subbing")
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("tx_delays_sub")

    delays = []


    def sub_cb(data: StringStamped):
        nonlocal delays
        r = data.time_received.sec + data.time_received.nanosec*1e-9
        s = data.time_sent.sec + data.time_sent.nanosec*1e-9
        delay = (r-s)*1500.0
        delays.append(delay)


    node.create_subscription(StringStamped,
                         "sam_back/acoustic/read",
                         sub_cb,
                         1000)
    
    try:
        rclpy.spin(node)
    except:
        plt.figure(figsize=(10, 6))
        plt.plot(range(len(delays)), delays, marker='o', linestyle='-', color='b')
        plt.xlabel("Message index")
        plt.ylabel("Range")
        plt.show()


def pub(num: int):
    print("Pubbing")
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("tx_delays_pub")

    pub = node.create_publisher(StringStamped, "sam_front/acoustic/write", 10)
    msg_num = 0

    def publish():
        nonlocal pub, msg_num
        F = StringStamped()
        F.data = f"Msg num:{msg_num}"
        pub.publish(F)
        msg_num += 1

    for i in range(num):
        node.create_timer(0.02, publish)

    rclpy.spin(node)


if __name__ == "__main__":
    a = sys.argv[1]
    if a=="sub": sub()
    if a=="pub": pub(1)