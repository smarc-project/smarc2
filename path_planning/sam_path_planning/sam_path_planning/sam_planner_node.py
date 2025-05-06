import rclpy
import rclpy.logging
import numpy as np
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry, Path
from tf2_ros import Buffer, TransformListener
from rclpy.executors import MultiThreadedExecutor
from rcl_interfaces.msg import ParameterDescriptor
from smarc_control_msgs.msg import Topics as ControlTopics
from smarc_control_msgs.msg import WpMPC, SamControl 
from smarc_control_msgs.action import TrajectoryMPC
from smarc_msgs.msg import PercentStamped, ThrusterRPM, ThrusterFeedback
from sam_msgs.msg import Topics as SamTopics
from sam_msgs.msg import ThrusterAngles
from message_filters import Subscriber, ApproximateTimeSynchronizer
from rclpy.action import ActionClient

# Path planning modules from smarc_modelling go here
from smarc_modelling.vehicles.SAM import SAM
from smarc_modelling.motion_planning.MotionPrimitives.MainScript import MotionPlanningROS

class SamPathPlanner(Node):

    def __init__(self):
        super().__init__("sam_planner_node")

        self.set_parameters()

        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(
            self._tf_buffer, self, spin_thread=True
        )

        # Declare your publishers here
        # self.traj_pub = self.create_publisher(TrajectoryMPC, ControlTopics.TRAJ_MPC, 1)

        # Declare your subscribers here
        self.pose_sub = self.create_subscription(PoseStamped, 
                                                 ControlTopics.WAYPOINT, self.target_cb, 1)

        self.odom_sub = self.create_subscription(Odometry, 
                                                 ControlTopics.STATES, self.state_cb, 1)
        
        # Synch subscribers here 
        self.lcg_fb = Subscriber(self, PercentStamped, SamTopics.LCG_FB_TOPIC)
        self.vbs_fb = Subscriber(self, PercentStamped, SamTopics.VBS_FB_TOPIC)
        self.thrusters_cmd = Subscriber(self, ThrusterAngles , SamTopics.THRUST_VECTOR_CMD_TOPIC)
        self.rpm1_fb = Subscriber(self, ThrusterFeedback, SamTopics.THRUSTER1_FB_TOPIC)
        self.rpm2_fb = Subscriber(self, ThrusterFeedback, SamTopics.THRUSTER2_FB_TOPIC)

        self.ctrl_synch_msg = ApproximateTimeSynchronizer(
            [self.vbs_fb, self.lcg_fb, self.thrusters_cmd, self.rpm1_fb, self.rpm2_fb],
            queue_size = 100,
            slop = 0.0001
        )
        self.ctrl_synch_msg.registerCallback(self.ctrl_synch_cb)

        # Action client to communicate with MPC
        self._action_client = ActionClient(self, TrajectoryMPC, ControlTopics.TRAJ_MPC)
        while not self._action_client.wait_for_server(timeout_sec=1.) and rclpy.ok():
            self._logger.info(f"Planner waiting for {ControlTopics.TRAJ_MPC} server")

        self._goal_handle = None

    def run(self):
        
        rate = self.create_rate(self.node_rate)  # Hz rate
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.0) 
            
            # If goal is empty or feedback has not been received yet, keep spinning
            if self.sam_goal_t != PoseStamped() and self.sam_pose_t != None and self.sam_control_t != None:
                
                ## Do planning stuff here
                # === Start state ===
                start_state = np.array([
                        self.sam_pose_t.pose.pose.position.x,
                        self.sam_pose_t.pose.pose.position.y,
                        self.sam_pose_t.pose.pose.position.z,
                        self.sam_pose_t.pose.pose.orientation.w,
                        self.sam_pose_t.pose.pose.orientation.x,
                        self.sam_pose_t.pose.pose.orientation.y,
                        self.sam_pose_t.pose.pose.orientation.z,
                        self.sam_pose_t.twist.twist.linear.x,
                        self.sam_pose_t.twist.twist.linear.y,
                        self.sam_pose_t.twist.twist.linear.z,
                        self.sam_pose_t.twist.twist.angular.x,
                        self.sam_pose_t.twist.twist.angular.y,
                        self.sam_pose_t.twist.twist.angular.z,
                        self.sam_control_t.vbs.value,
                        self.sam_control_t.lcg.value ,
                        self.sam_control_t.dsdr.thruster_vertical_radians,
                        self.sam_control_t.dsdr.thruster_horizontal_radians,
                        self.sam_control_t.rpm1.rpm,
                        self.sam_control_t.rpm2.rpm
                    ])

                # === End state ===
                end_state = np.array([
                        self.sam_goal_t.pose.position.x,
                        self.sam_goal_t.pose.position.y,
                        self.sam_goal_t.pose.position.z,
                        self.sam_goal_t.pose.orientation.w,
                        self.sam_goal_t.pose.orientation.x,
                        self.sam_goal_t.pose.orientation.y,
                        self.sam_goal_t.pose.orientation.z,
                        0, 0, 0,
                        0, 0, 0,
                        50, 50, 0, 0, 0, 0
                    ])

                # === Motion Planner ===
                self.get_logger().info(f'Calling planner...')
                trajectory, successful = MotionPlanningROS(start_state, end_state)

                ## Parse your output into this action
                goal_path = TrajectoryMPC.Goal()
                goal_path.header.stamp = self.get_clock().now().to_msg()
                goal_path.header.frame_id = self.sam_goal_t.header.frame_id = self.sam_goal_t.header.frame_id

                # For each trajectory wp, do this
                wp_i = WpMPC()
                goal_path.trajectory.append(wp_i)

                # Send to MPC
                self.send_goal(goal_path)

                # Reset this after planning
                self.sam_goal_t = PoseStamped() 

            rate.sleep()

    def set_parameters(self):
        ## Add your parameters here
        self.robot_name = self.declare_parameter("robot_name", "sam").value
        self.map_frame = self.declare_parameter("map_frame", "mocap").value
        self.node_rate = self.declare_parameter("node_rate", 1.).value

        # Variables
        self.sam_pose_t = None
        self.sam_control_t = None
        self.sam_goal_t = PoseStamped() # The action server will send an empty msg when cancelling

        # Define your map somewhere here

    def target_cb(self, msg: PoseStamped):
        self.get_logger().info(f'Received goal')
        self.sam_goal_t = msg
        
        # The action server will send an empty msg when cancelling
        if self.sam_goal_t == PoseStamped():
            # Pass cancel to controller as an empty TrajectoryMPC()
            path_t = TrajectoryMPC()
            self.traj_pub.publish(path_t)

    def state_cb(self, msg: Odometry):
        self.get_logger().info(f'Received state')
        self.sam_pose_t = msg

    def ctrl_synch_cb(self, vbs_fb_msg: PercentStamped, lcg_fb_msg: PercentStamped, dsdr_cmd_msg: ThrusterAngles, rpm1_fb_msg: ThrusterFeedback, rpm2_fb_msg: ThrusterFeedback):
        self.get_logger().info(f'Received ctrl inputs')
        self.sam_control_t = SamControl()
        self.sam_control_t.vbs = vbs_fb_msg
        self.sam_control_t.lcg = lcg_fb_msg
        self.sam_control_t.dsdr = dsdr_cmd_msg
        self.sam_control_t.rpm1 = rpm1_fb_msg
        self.sam_control_t.rpm2 = rpm2_fb_msg

    #### AC for the MPC functions from here
    def send_goal(self, goal_msg):
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        self.get_logger().info(f'Current sub wp: {feedback_msg.feedback.current_wp_idx}')

    def goal_response_callback(self, future):
        self._goal_handle = future.result()
        if not self._goal_handle.accepted:
            self.get_logger().info('MPC goal rejected')
            return
        self.get_logger().info('MPC goal accepted')
        self._get_result_future = self._goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: {result.success}')

    def cancel_goal(self):
        if self._goal_handle is None:
            self.get_logger().info('No goal to cancel.')
            return

        cancel_future = self._goal_handle.cancel_goal_async()
        cancel_future.add_done_callback(self.cancel_done)

    def cancel_done(self, future):
        cancel_response = future.result()
        if len(cancel_response.goals_canceling) > 0:
            self.get_logger().info('Goal successfully canceled.')
            self._goal_handle
        else:
            self.get_logger().info('Goal failed to cancel.')


def main(args=None):
    rclpy.init(args=args)
    node = SamPathPlanner()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
