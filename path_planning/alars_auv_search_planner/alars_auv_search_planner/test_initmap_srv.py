import sys
import rclpy
from rclpy.node import Node
from smarc_mission_msgs.srv import DronePath, InitAUVSearch
from geometry_msgs.msg import PointStamped
from geographic_msgs.msg import GeoPoint


class TestSrv(Node):
    def __init__(self):
        super().__init__('test_srv_node')
        self.path_flag = False
        self.init_gridmap_client = self.create_client(srv_type = InitAUVSearch, 
                                         srv_name = '/Quadrotor/init_auv_search')
        while not self.init_gridmap_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('services not available, waiting again...')

        
    
    def send_init_gridmap_request(self):
        # Define GPS ping and initial drone position
        self.req = InitAUVSearch.Request()

        gps = GeoPoint()
        gps.latitude = 58.85058132601718 #58.85028132601718
        gps.longitude = 17.67416659875381 #17.67486659875381
        gps.altitude = 1.1628758907318115 #11.1628758907318115
        
        self.req.gps = gps

        self.req.radius = 100.0

        self.future = self.init_gridmap_client.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()


def main(args=None):
    rclpy.init(args=args)

    client = TestSrv()
    client.get_logger().info(f'Requesting map initialization ...')
    _ = client.send_init_gridmap_request()
    client.get_logger().info(f'Response received - map initialized')






if __name__ == '__main__':
    main()