#!/usr/bin/env python3

import re
import subprocess

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32


class InternetMonitorNode(Node):

    def __init__(self):
        super().__init__('internet_monitor')

        self.publisher_ = self.create_publisher(
            Int32,
            'internet_connected',
            10
        )

        self.timer = self.create_timer(1.0, self.timer_callback)

        self.get_logger().info('Internet monitor node started')

    def timer_callback(self):
        ttl = self.get_ping_ttl('8.8.8.8')

        msg = Int32()
        msg.data = ttl

        self.publisher_.publish(msg)

        self.get_logger().info(
            f'internet_connected TTL = {ttl}'
        )

    def get_ping_ttl(self, host: str) -> int:
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '1', host],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return -1

            # Example line:
            # 64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=14.2 ms
            match = re.search(r'ttl=(\d+)', result.stdout)

            if match:
                return int(match.group(1))

            return -1

        except Exception as e:
            self.get_logger().error(f'Ping failed: {e}')
            return -1


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