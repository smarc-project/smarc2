import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import socket
import select
import time


class TCP_driver(Node):

    def __init__(self):
        super().__init__('tcp_driver')

        self.receive_buffer = b''

        self.declare_parameter("endpoint_ip", '127.0.0.1')
        self.endpoint_ip = self.get_parameter("endpoint_ip").get_parameter_value().string_value

        self.declare_parameter("endpoint_port", 7777)
        self.endpoint_port = int(self.get_parameter("endpoint_port").value)

        self.declare_parameter("transmit_topic", '/tcp/send')
        self.transmit_topic = self.get_parameter("transmit_topic").get_parameter_value().string_value

        self.declare_parameter("received_topic", '/tcp/received')
        self.received_topic = self.get_parameter("received_topic").get_parameter_value().string_value

        self.declare_parameter("poll_rate", 50)  # Hz
        self.poll_rate = int(self.get_parameter("poll_rate").value)

        self.publisher = self.create_publisher(String, self.received_topic, 10)
        self.subscription = self.create_subscription(String,self.transmit_topic, self.transmit_callback, 10)

        
        self.read_timer = self.create_timer(1.0 / self.poll_rate, self.read_data_callback)
        self.socket_connected = False

    #Poll data from tcp port
    def read_data_callback(self):
        if(self.socket_connected == False):
            try:
                # Create a TCP/IP socket
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(3)
                self.get_logger().info(f"Connecting to :{self.endpoint_ip} port {self.endpoint_port}..")
                self.sock.connect((self.endpoint_ip, self.endpoint_port))
                self.get_logger().info("connected")
                self.socket_connected = True
            except Exception as e:
                self.get_logger().info(f"connection failed {e}")
                time.sleep(2)

        if(self.socket_connected):
            try:
                ready_to_read, ready_to_write, in_error = \
                    select.select([self.sock,], [self.sock,], [], 5)
            except select.error:
                #Connection was probably closed by the other side
                self.socket_connected = False
                self.sock.shutdown(2)    # 0 = done receiving, 1 = done sending, 2 = both
                self.sock.close()
                self.get_logger().info(f"connection closed {e}")
            
            #Read data fom socket
            if self.socket_connected and len(ready_to_read) > 0:
                try:
                    recv = self.sock.recv(2048)
                    if(len(recv) == 0):
                        #Connection lost
                        self.socket_connected = False
                        self.sock.shutdown(2)    # 0 = done receiving, 1 = done sending, 2 = both
                        self.sock.close()
                    msg = String()
                    msg.data = recv.decode()
                    self.publisher.publish(msg)
                except socket.timeout:
                    self.get_logger().info(f"timeout")
            

    #Send data
    def transmit_callback(self,msg):
        data = msg.data
        if(self.socket_connected):
            try:
                self.sock.send(data.encode())
            except Exception as e:
                self.get_logger().info(f"send error {e}")
        


def main(args=None):
    rclpy.init(args=args)

    tcp_driver = TCP_driver()

    rclpy.spin(tcp_driver)
    tcp_driver.destroy_node()

    executor = MultiThreadedExecutor()
    executor.add_node(translator)
    executor.spin()

    tcp_driver.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()