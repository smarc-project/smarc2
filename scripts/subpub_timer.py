#!/usr/bin/python3

import rclpy, sys, time
import matplotlib.pyplot as plt
from std_msgs.msg import Float64

def sub():
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("subpubtimer_sub")

    delays = []


    def sub_cb(data: Float64):
        nonlocal delays
        t = time.time()
        delay = t - data.data
        # print(f'{t} : {data.data}')
        delays.append(delay/1000.0)


    node.create_subscription(Float64,
                         "timer",
                         sub_cb,
                         1000)
    
    try:
        rclpy.spin(node)
    except:
        # print(delays[:100])
        plt.figure(figsize=(10, 6))
        plt.plot(range(len(delays)), delays, marker='o', linestyle='-', color='b')
        plt.xlabel("Message index")
        plt.ylabel("Delay(ms)")
        plt.show()



def pub(num: int):
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("subpubtimer_pub")

    pub = node.create_publisher(Float64, "timer", 10)

    def publish():
        nonlocal pub
        t = time.time()
        F = Float64()
        F.data = t
        pub.publish(F)
        # print(F)

    for i in range(num):
        node.create_timer(0.02, publish)

    rclpy.spin(node)





if __name__ == "__main__":
    a = input("sub? pub? [sub/pub]")
    if a=="sub": sub()
    if a=="pub": pub(1)
    if a=="many": pub(50)


