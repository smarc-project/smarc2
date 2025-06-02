import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import socket
import time


class UDP_sender(Node):

    def __init__(self):
        super().__init__('UDP_sender')

        self.declare_parameter("endpoint_ip", '127.0.0.1')
        self.endpoint_ip = self.get_parameter("endpoint_ip").get_parameter_value().string_value

        self.declare_parameter("endpoint_port", 8888)
        self.endpoint_port = int(self.get_parameter("endpoint_port").value)

        self.declare_parameter("transmit_topic", '/udp/send')
        self.transmit_topic = self.get_parameter("transmit_topic").get_parameter_value().string_value

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        
        self.subscription = self.create_subscription(String,self.transmit_topic, self.transmit_callback, 10)


        #Send data
    def transmit_callback(self,msg):
        self.sock.sendto(msg.data.encode(), (self.endpoint_ip, self.endpoint_port))



def main(args=None):
    rclpy.init(args=args)

    udp_driver = UDP_sender()

    rclpy.spin(udp_driver)
    udp_driver.destroy_node()

    executor = MultiThreadedExecutor()
    executor.add_node(translator)
    executor.spin()

    udp_driver.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()