#!/usr/bin/env python3

import re
import subprocess

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class InternetMonitorNode(Node):

    def __init__(self):
        super().__init__('internet_monitor')

        self.publisher_ = self.create_publisher(
            Float32,
            'sensor/ping_time',
            10
        )

        self.timer = self.create_timer(1.0, self.timer_callback)
        self.msg = Float32()

        self.get_logger().info('Internet monitor node started')

    def timer_callback(self):
        time = self.get_ping_time('8.8.8.8')

        self.msg.data = time

        self.publisher_.publish(self.msg)
        self.get_logger().info(f'internet_connected time = {time}')

    def get_ping_time(self, host: str) -> float:
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '1', host],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return -1.0

            # Example line:
            # 64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=14.2 ms
            match = re.search(r'time=(\d+\.?\d*)', result.stdout)

            if match:
                return float(match.group(1))

            return -1.0

        except Exception as e:
            self.get_logger().error(f'Ping failed: {e}')
            return -1.0


def main(args=None):
    rclpy.init(args=args)

    node = InternetMonitorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()