import sys
import rclpy
from rclpy.node import Node
from smarc_mission_msgs.srv import DronePath, InitAUVSearch
from geometry_msgs.msg import PointStamped, PoseArray


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

        gps = PointStamped()
        gps.header.stamp = self.get_clock().now().to_msg()
        gps.header.frame_id = 'map_gt_gt'
        gps.point.x = 1268.0
        gps.point.y = 1150.0
        self.req.gps = gps

        quadrotor_ipos = PointStamped()
        quadrotor_ipos.header.stamp = self.get_clock().now().to_msg()
        quadrotor_ipos.header.frame_id = 'Quadrotor/odom_gt'
        quadrotor_ipos.point.x = 2.0
        quadrotor_ipos.point.y = 2.0
        self.req.quadrotor_ipos = quadrotor_ipos

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