import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import socket
import time


class UDP_receiver(Node):

    def __init__(self):
        super().__init__('udp_receiver')

        self.declare_parameter("listen_port", 8888)
        self.listen_port = int(self.get_parameter("listen_port").value)

        self.declare_parameter("received_topic", '/udp/received')
        self.received_topic = self.get_parameter("received_topic").get_parameter_value().string_value

        self.declare_parameter("poll_rate", 50)  # Hz
        self.poll_rate = int(self.get_parameter("poll_rate").value)

        self.publisher = self.create_publisher(String, self.received_topic, 10)

        self.sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM) # UDP
        self.sock.settimeout(5)
        self.sock.bind(("0.0.0.0", self.listen_port))
        
        self.read_timer = self.create_timer(1.0 / self.poll_rate, self.read_data_callback)

    #Poll data from udp port
    def read_data_callback(self):
        try:
            data, addr = self.sock.recvfrom(1024)
            if(len(data) < 1):
                return
            msg = String()
            msg.data = data.decode()
            self.publisher.publish(msg)
        except socket.timeout:
            pass

def main(args=None):
    rclpy.init(args=args)

    udp_driver = UDP_receiver()

    rclpy.spin(udp_driver)
    udp_driver.destroy_node()

    executor = MultiThreadedExecutor()
    executor.add_node(translator)
    executor.spin()

    udp_driver.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()