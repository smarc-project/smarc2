import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry, Path
from tf2_ros import Buffer, TransformListener
from rclpy.executors import MultiThreadedExecutor
from rcl_interfaces.msg import ParameterDescriptor
from smarc_control_msgs.msg import Topics as ControlTopics
from smarc_msgs.msg import PercentStamped, ThrusterRPM, ThrusterFeedback
from sam_msgs.msg import Topics as SamTopics
from message_filters import Subscriber, ApproximateTimeSynchronizer

# Path planning modules from smarc_modelling go here
from smarc_modelling.vehicles.SAM import SAM

class SamPathPlanner(Node):

    def __init__(self):
        super().__init__("sam_planner_node")

        self.set_parameters()

        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(
            self._tf_buffer, self, spin_thread=True
        )

        # Declare your publishers here

        # Declar your subscribers here
        self.pose_sub = self.create_subscription(PoseStamped, 
                                                 ControlTopics.WAYPOINT, self.goal_cb, 1)

        self.odom_sub = self.create_subscription(Odometry, 
                                                 ControlTopics.STATES, self.state_cb, 1)
        
        # Synch subscribers here 
        self.lcg_fb = Subscriber(self, PercentStamped, SamTopics.VBS_FB_TOPIC)
        self.vbs_fb = Subscriber(self, PercentStamped, SamTopics.LCG_FB_TOPIC)
        # keep adding stuff...

        self.ctrl_synch_msg = ApproximateTimeSynchronizer(
            [self.vbs_fb, self.lcg_fb],
            queue_size = 100,
            slop = 0.0001
        )
        self.ctrl_synch_msg.registerCallback(self.ctrl_synch_cb)
        

    def set_parameters(self):
        self.robot_name = self.declare_parameter("robot_name", "sam").value
        self.map_frame = self.declare_parameter("map_frame", "mocap").value

        ## Add your parameters here

    def goal_cb(self, msg: PoseStamped):
        self.get_logger().info(f'Received goal')

    def state_cb(self, msg: Odometry):
        self.get_logger().info(f'Received state')

    def ctrl_synch_cb(self, vbs_fb_msg: PercentStamped, lcg_fb_msg: PercentStamped):
        self.get_logger().info(f'Received ctrl inputs')



def main(args=None):
    rclpy.init(args=args)
    node = SamPathPlanner()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    executor.spin()


if __name__ == '__main__':
    main()
