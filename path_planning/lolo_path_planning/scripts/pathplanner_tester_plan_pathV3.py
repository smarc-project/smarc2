import sys

from nav_msgs.srv import GetPlan
from nav_msgs.msg import Path
import rclpy
from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import time


class MinimalClientAsync(Node):

    def __init__(self):
        super().__init__('minimal_client_async')

        #Statistics on good / bad service calls
        self.good = 0
        self.bad = 0

        srv_callback_group = ReentrantCallbackGroup()
        timer_callback_group = MutuallyExclusiveCallbackGroup()

        self.cli = self.create_client(GetPlan, 'plan_path', callback_group=srv_callback_group)

        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for plan path service...')

        self.path_pub = self.create_publisher(Path, 'path', 10) #Default callback group?
        self.timer = self.create_timer(0.1, self.send_request, callback_group=timer_callback_group)


    def send_request(self):
        self.req = GetPlan.Request()

        self.req.start.header.frame_id = 'map'
        self.req.start.pose.position.x = 0.0
        self.req.start.pose.position.y = 0.0
        self.req.start.pose.position.z = 0.0
        
        self.req.goal.header.frame_id = 'map'
        self.req.goal.pose.position.x = 10.0
        self.req.goal.pose.position.y = 10.0
        self.req.goal.pose.position.z = 0.0

        #TODO start and end yaw

        #result = self.cli.call(self.req)

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
            self.path_pub.publish(result.plan)
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


