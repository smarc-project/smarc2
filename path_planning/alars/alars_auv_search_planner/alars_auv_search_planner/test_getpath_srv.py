import sys
import rclpy
from rclpy.node import Node
from dji_msgs.srv import DronePath, InitAUVSearch
from geometry_msgs.msg import PointStamped, PoseArray


class TestSrv(Node):
    def __init__(self):
        super().__init__('test_srv2_node')
        self.get_path_client = self.create_client(srv_type = DronePath, 
                                         srv_name = '/Quadrotor/get_quadrotor_path')
        while not self.get_path_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('services not available, waiting again...')


    def send_get_path_request(self):
        self.req = DronePath.Request()
        self.req.data = True
        
        self.future2 = self.get_path_client.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future2)
        return self.future2.result()



def main(args=None):
    rclpy.init(args=args)

    client = TestSrv()

    client.get_logger().info(f'Requesting path ...')
    path = client.send_get_path_request()
    client.get_logger().info(f'Response received - map: {path}')






if __name__ == '__main__':
    main()