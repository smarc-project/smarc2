import sys

from nav_msgs.srv import SetMap
import rclpy
from nav_msgs.msg import OccupancyGrid
from nav_msgs.msg import MapMetaData
import numpy as np
from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import time


class MinimalClientAsync(Node):

    def __init__(self):
        super().__init__('set_map_tester')

        #Statistics on good / bad service calls
        self.good = 0
        self.bad = 0

        srv_callback_group = ReentrantCallbackGroup()
        timer_callback_group = MutuallyExclusiveCallbackGroup()

        self.cli = self.create_client(SetMap, 'set_map')

        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for set map service...')

        self.grid_pub = self.create_publisher(OccupancyGrid, 'grid', 10)
        self.timer = self.create_timer(0.1, self.send_request, callback_group=timer_callback_group)



    def send_request(self):
        self.req = SetMap.Request()
        
        #Boundary polygon
        points = [ [0,0], [0,100], [100,100], [100,0]]
        
        #Build the map
        self.req.map.header.frame_id = 'map'
        self.req.map.info.height = 100
        self.req.map.info.width = 100
        self.req.map.info.resolution = 1.0
        self.req.map.info.origin.position.x = 0.0
        self.req.map.info.origin.position.y = 0.0
        self.req.map.info.origin.position.z = 0.0

        #self.req.map.data = np.zeros((self.req.map.info.width*self.req.map.info.height, ), dtype=int)

        self.req.map.data = [-1]*(self.req.map.info.width*self.req.map.info.height)

        for i in range(0,100):
            row = i
            col = i
            self.req.map.data[row + col*self.req.map.info.height] = 100
            

        self.grid_pub.publish(self.req.map)
        

        future = self.cli.call_async(self.req)
        #result = rclpy.spin_until_future_complete(self, future, timeout_sec=0.5) #Deadlock
        t = 0
        while not (future.done()):
            time.sleep(0.01)
            t += 1
            if(t > 100):
                future.cancel()
                break
        result = future.result()
        
        if(result is not None ): 
            self.good +=1
        else: self.bad +=1

        self.get_logger().info('Good: ' + str(self.good) + " Bad: " + str(self.bad))




  
def main(args=None):
    rclpy.init(args=args)
    minimal_client = MinimalClientAsync()

    executor = MultiThreadedExecutor()
    executor.add_node(minimal_client)
    executor.spin()

    minimal_client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()


