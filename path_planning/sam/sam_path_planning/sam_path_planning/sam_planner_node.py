import rclpy
import rclpy.logging
import time
import numpy as np
from rclpy.node import Node
from scipy.spatial.transform import Rotation as R

from geometry_msgs.msg import PoseStamped, TransformStamped
from nav_msgs.msg import Odometry, Path
from tf2_ros import Buffer, TransformListener, TransformException
from tf_transformations import quaternion_from_euler
from rclpy.executors import MultiThreadedExecutor
from rcl_interfaces.msg import ParameterDescriptor
from smarc_control_msgs.msg import Topics as ControlTopics
from smarc_control_msgs.msg import WpMPC, SamControl 
from smarc_msgs.msg import PercentStamped, ThrusterRPM, ThrusterFeedback
from sam_msgs.msg import Topics as SamTopics
from sam_msgs.msg import ThrusterAngles
from message_filters import Subscriber, ApproximateTimeSynchronizer
from rclpy.action import ActionClient

# Path planning modules from smarc_modelling go here
from smarc_modelling.motion_planning.MotionPrimitives.MainScript import MotionPlanningROS
#from smarc_modelling.sam_sim import plot_results, Sol

from sam_path_following.path_client import PathClient
from smarc_action_base.smarc_action_base import (
    ActionResult,                                
    ActionType,                                  
    SMARCActionServer,                           
)                                                
from smarc_msgs.action import BaseAction
from smarc_msgs.msg import Topics as SMaRCTopics
import json

from go_to_hydrobaticpoint.hydrobaticpoint_server import HydropointServer
from rclpy.action.server import ServerGoalHandle
from go_to_hydrobaticpoint.hydrobaticpoint_action import ActionComponent as ActC
from sam_path_following.path_client import PathClient
# from sam_path_following.path_action import PathAction
    
class SamPathPlanner(HydropointServer, PathClient):

    def __init__(
                self,
                node: Node,
                **kwargs,
                ):

        self._node = node
        # super().__init__("sam_planner_node")

        action_type = ActionType(BaseAction)
        action_name = "go_to_hydropoint"
        HydropointServer.__init__(
            self,
            self._node,
            action_name,
            action_type,
        )

        action_name = "auv_trajectory_tracking"
        PathClient.__init__(
            self,
            self._node, 
            action_name,
            action_type,
        )

        self.declare_parameters()

        self._hydropoint = None
        # self._received_waypoint = False
        self.path_computed = False
        self.call_planner = False
        self.path_found = False

        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self._node, spin_thread=False)

        # Declare your publishers here
        self.path_pub = self._node.create_publisher(Path, 'planned_path', 1)  # For Rviz

        # Declare your subscribers here
        # self.pose_sub = self.create_subscription(PoseStamped, 
        #                                          "/mocap/hula/pose", self.target_cb, 1)

        # TODO: get state from TF instead of odom since we want mocap --> base_link
        self.odom_sub = self._node.create_subscription(Odometry, 
                                                 ControlTopics.MOCAP_STATE, self.state_cb, 1)
        # self._node.get_logger().info(f"Created listener")
        
        # Synch subscribers here 
        self.lcg_fb = Subscriber(self._node, PercentStamped, SamTopics.LCG_FB_TOPIC)
        self.vbs_fb = Subscriber(self._node, PercentStamped, SamTopics.VBS_FB_TOPIC)
        #self.thrusters_cmd = Subscriber(self, ThrusterAngles , SamTopics.THRUST_VECTOR_CMD_TOPIC)
        # self.thrusters_cmd = Subscriber(self, ThrusterAngles , 'with_header/thrust_vector_cmd')
        self.rpm1_fb = Subscriber(self._node, ThrusterFeedback, SamTopics.THRUSTER1_FB_TOPIC)
        self.rpm2_fb = Subscriber(self._node, ThrusterFeedback, SamTopics.THRUSTER2_FB_TOPIC)
        # self.rpm1_fb = Subscriber(self, ThrusterFeedback, 'with_header/thruster1_fb')
        # self.rpm2_fb = Subscriber(self, ThrusterFeedback, 'with_header/thruster2_fb')
        self._node.get_logger().info(f'Subscribers for ctrl inputs created')    

        self.ctrl_synch_msg = ApproximateTimeSynchronizer(
            [self.vbs_fb, self.lcg_fb],
            queue_size = 100,
            slop = 10, 
            allow_headerless=True
        )
        self.ctrl_synch_msg.registerCallback(self.ctrl_synch_cb)

        self._goal_handle = None

    def declare_parameters(self):
        """Location to declare parameters."""
        node = self._node

        ## Add your parameters here
        if not node.has_parameter("robot_name"):
            self.robot_name = self._node.declare_parameter("robot_name", "sam").value
        if not node.has_parameter("map_frame"):
            self.map_frame = self._node.declare_parameter("map_frame", "mocap").value
        if not node.has_parameter("base_frame"):
            self.base_frame = self._node.declare_parameter("base_frame", f"{self.robot_name}/base_link").value
        if not node.has_parameter("node_rate"):
            self.node_rate = self._node.declare_parameter("node_rate", 1.).value
        if not node.has_parameter("x_max"):
            self.x_max = self._node.declare_parameter("x_max", 10).value   # map
        if not node.has_parameter("y_max"):            
            self.y_max = self._node.declare_parameter("y_max", 2.5).value  # map
        if not node.has_parameter("z_max"):
            self.z_max = self._node.declare_parameter("z_max", 3).value   # map
        if not node.has_parameter("x_min"):
            self.x_min = self._node.declare_parameter("x_min", 0).value    # map
        if not node.has_parameter("y_min"):
            self.y_min = self._node.declare_parameter("y_min", -2.5).value   # map
        if not node.has_parameter("z_min"):
            self.z_min = self._node.declare_parameter("z_min", -0.5).value   # map
        if not node.has_parameter("map_resolution"):
            self.map_resolution = self._node.declare_parameter("map_resolution", 0.5).value   # map resolution

        # Variables
        self.sam_pose_t = None
        self.sam_control_t = None
        self.sam_goal_t = PoseStamped() # The action server will send an empty msg when cancelling
        if not node.has_parameter("target_frame"):
            self._target_frame_param = node.declare_parameter("target_frame", "odom").value

        self.target_frame = (
            f"{self.robot_name}/{self._target_frame_param}"
        )
        self._node.get_logger().info(f"Target frame {self.target_frame}")
        
        if not node.has_parameter("distance_frame"):
            self._distance_frame_param = node.declare_parameter(
                "distance_frame",
                "base_link",
                ParameterDescriptor(
                    description="Frame for which the distance to target will be computed (usually base_link)"
                ),
            ).value

        if not node.has_parameter("goal_threshold"):
            self._goal_threshold = (
                node.declare_parameter(
                    "goal_threshold",
                    10,
                    ParameterDescriptor(
                        description="Distance threshold in meters where a goal should be rejected. (Euclidean Norm)"
                    )
                ).value
            )
        
        self.distance_frame = f"{self.robot_name}/{self._distance_frame_param}"
        self._node.get_logger().info(f"Distance frame {self.distance_frame}")


    def state_cb(self, msg: Odometry):
        self._node.get_logger().info(f'Received state', once=True)
        
        # Tf 
        try:    
            t = self._tf_buffer.lookup_transform(self.map_frame, self.distance_frame, rclpy.time.Time())
        except TransformException as ex:
            self._node.get_logger().warn(f'Could not transform {self.map_frame} to {self.distance_frame}: {ex}')
            return
        
        # Transform the pose        
        self.sam_pose_t = msg
        self.sam_pose_t.pose.pose.position.x = t.transform.translation.x
        self.sam_pose_t.pose.pose.position.y = t.transform.translation.y
        self.sam_pose_t.pose.pose.position.z = t.transform.translation.z
        self.sam_pose_t.pose.pose.orientation.w = t.transform.rotation.w
        self.sam_pose_t.pose.pose.orientation.x = t.transform.rotation.x
        self.sam_pose_t.pose.pose.orientation.y = t.transform.rotation.y
        self.sam_pose_t.pose.pose.orientation.z = t.transform.rotation.z


    def ctrl_synch_cb(self, vbs_fb_msg: PercentStamped, lcg_fb_msg: PercentStamped):
        #self.get_logger().info(f'Received ctrl inputs')
        self.sam_control_t = SamControl()
        self.sam_control_t.vbs = vbs_fb_msg
        self.sam_control_t.lcg = lcg_fb_msg
        # self.sam_control_t.thruster_angles = dsdr_cmd_msg
        # self.sam_control_t.rpms.thruster_1_rpm = rpm1_fb_msg.rpm.rpm
        # self.sam_control_t.rpms.thruster_2_rpm = rpm2_fb_msg.rpm.rpm

    def execution_callback(self, goal_handle: ServerGoalHandle) -> ActionResult:
        """Primary execution callback where goal's are handled after acceptance.

        Args:
            goal_handle: handle to control server and add callbacks

        Returns:
            A populated ActionResult message
        """

        if self.sam_pose_t == None:
            self.logger.info(f"Missing pose")
        if self.sam_control_t == None:
            self.logger.info(f"Missing control")
        
        # If goal is empty or feedback has not been received yet, keep spinning
        result_msg = self.action_type.Result
        if self._received_waypoint and self.sam_pose_t != None and self.sam_control_t != None:
            self.logger.info(f"All inputs received")  
            self._hydropoint = self.pose_stamped
            # self._json_ops.decode(goal_handle.request.goal, 0)
            self.logger.info(f"Hydropoint received: {self._hydropoint}")
            
            # Call path planner and move on to feedback
            self.call_planner = True
            status = self.feedback_loop(self._hydropoint, goal_handle)

            if status == "cancelled":
                self.logger.info("Goal was cancelled by client.")
                result_msg.success = False
                self.path_found = False
                return result_msg
        
            if self.path_found:
                result_msg.success = True
                goal_handle.succeed()

            else:
                goal_handle.abort()
                result_msg.success = False

        else:
            goal_handle.abort()
            result_msg.success = False
        
        self.path_found = False
        return result_msg
    
    def feedback_loop(self, pose_stamped: PoseStamped, goal_handle: ServerGoalHandle):
        """Abstracted feedback loop where tolerance checks are conducted.

        Args:
            pose_stamped: target location
            goal_handle: passed in to enable feedback publishing
        """
        rate = self._node.create_rate(1, self._node.get_clock())
        d = self.compute_distance(pose_stamped)
        feedback = self.action_type.Feedback
        # tol_check = self._tol_check(d)
        while not self.path_computed:
                
            if goal_handle.is_cancel_requested:
                self.logger.info("Goal was cancelled by client.")
                goal_handle.canceled()
                # self.publish_stop_setpoint()
                return "cancelled"
            
            feedback.feedback = self._json_ops.encode(d)
            goal_handle.publish_feedback(feedback)
            d = self.compute_distance(pose_stamped)
            rate.sleep()
            # tol_check = self._tol_check(d)
            # self.logger.debug(f"Tol check result: {tol_check}, Distance: {d} m.")

        self.path_computed = False
        rate.destroy()
        return "done"


    def compute_path(self):

        if self.call_planner:
            self.call_planner = False

            # Do planning stuff here
            # === Start state ===
            # Normalize orientation quaternion and transform from FLU to FRD
            quat_flu = np.array([self.sam_pose_t.pose.pose.orientation.x,
                    self.sam_pose_t.pose.pose.orientation.y,
                    self.sam_pose_t.pose.pose.orientation.z,
                    self.sam_pose_t.pose.pose.orientation.w], dtype=float)
            quat_flu = quat_flu/np.linalg.norm(quat_flu)

            r_roll_180 = R.from_euler('x', 180, degrees=True)
            r_original = R.from_quat(quat_flu)
            quat_frd = (r_original * r_roll_180).as_quat()  # Local frame rotation

            start_state = np.array([
                    self.sam_pose_t.pose.pose.position.x,
                    self.sam_pose_t.pose.pose.position.y,
                    self.sam_pose_t.pose.pose.position.z + 0.5,  # Add offset to avoid collision with surface
                    quat_frd[3],quat_frd[0],quat_frd[1],quat_frd[2],
                    # 1,0,0,0,
                    self.sam_pose_t.twist.twist.linear.x,
                    self.sam_pose_t.twist.twist.linear.y,
                    self.sam_pose_t.twist.twist.linear.z,
                    self.sam_pose_t.twist.twist.angular.x,
                    self.sam_pose_t.twist.twist.angular.y,
                    self.sam_pose_t.twist.twist.angular.z,
                    self.sam_control_t.vbs.value,
                    self.sam_control_t.lcg.value ,
                    0., 0., 0., 0
                ])


            # Goal recevied by the ac. Set received to false
            self.sam_goal_t = self._hydropoint

            # Getting the current orientation of the goal
            # Normalize orientation quaternion and transform from FLU to FRD
            quat_flu_goal = np.array([self.sam_goal_t.pose.orientation.x,
                    self.sam_goal_t.pose.orientation.y,
                    self.sam_goal_t.pose.orientation.z,
                    self.sam_goal_t.pose.orientation.w], dtype=float)
            quat_flu_goal = quat_flu_goal/np.linalg.norm(quat_flu_goal)

            r_original = R.from_quat(quat_flu_goal)
            quat_frd_goal = (r_original * r_roll_180).as_quat()  # Local frame rotation

            # # === End state ===
            end_state = np.array([
                    self.sam_goal_t.pose.position.x,
                    self.sam_goal_t.pose.position.y,
                    self.sam_goal_t.pose.position.z,
                    quat_frd_goal[3],quat_frd_goal[0],quat_frd_goal[1],quat_frd_goal[2],
                    # 1,0,0,0,
                    0, 0, 0,
                    0, 0, 0,
                    50, 50, 0, 0, 0, 0
                ])

            # === Motion Planner ===
            #Print the states
            self._node.get_logger().info(f"Initial state:...{start_state}")
            r = R.from_quat([quat_frd[0], quat_frd[1], quat_frd[2], quat_frd[3]])
            roll, pitch, yaw = r.as_euler('xyz', degrees=True)
            self._node.get_logger().info(f"Yaw: {yaw:.2f}, Pitch: {pitch:.2f}, Roll: {roll}")
            self._node.get_logger().info(f"-----------")

            self._node.get_logger().info(f"Final State:...{end_state}")
            r = R.from_quat([quat_frd_goal[0],quat_frd_goal[1],quat_frd_goal[2],quat_frd_goal[3]])
            roll, pitch, yaw = r.as_euler('xyz', degrees=True)
            self._node.get_logger().info(f"Yaw:...{yaw:.2f}, Pitch:{pitch:.2f}, Roll:{roll}")

            # For debugging

            # Call the planner
            t = time.time()
            self._node.get_logger().info(f'Calling planner')
            map_boundaries = (self.x_max, self.y_max, self.z_max, self.x_min, self.y_min, self.z_min)
            trajectory, self.path_found, debugMsg = MotionPlanningROS(start_state, end_state, map_boundaries, self.map_resolution)
            self._node._logger.info(f"Planner output msg: {debugMsg}")

            # If path found
            if self.path_found:
                # Number of vertices in the trajectory
                print(f"Length of trajectory: {len(trajectory):.2f} vertices>>")
                
                self._node._logger.info(f"Sending path to controller")
                path = self.convert_np_path_to_trajectory(np.array(trajectory))
                self.send_path(path)

                ## Publish trajectory for Rviz
                trajectory.append(end_state[0:7].tolist())  # Append goal state for visualization
                self.publishTrajectoryRviz(trajectory)

            self.path_computed = True
            # ## Plot the inputs 
            # if successful == 1:
            #     sol = np.asarray(trajectory).T  # the columns are the states
            #     t_eval = np.linspace(0, 0.1*len(trajectory), len(trajectory))
            #     sol = Sol(t_eval, sol)
                
            #     plot_results(sol)
            #     self.get_logger().info(f'Inputs successfully plotted')



    def publishTrajectoryRviz(self, trajectory, typeMsg = "trajectory"):
        """
        typeMsg = "pose" or "trajectory"
        """

        path_msg = Path()
        path_msg.header.stamp = self._node.get_clock().now().to_msg()
        path_msg.header.frame_id = self.map_frame

        for wp in trajectory:
            pose = PoseStamped()
            pose.header.stamp = self._node.get_clock().now().to_msg()
            pose.header.frame_id = self.map_frame
            pose.pose.position.x = float(wp[0])
            pose.pose.position.y = float(wp[1])
            pose.pose.position.z = float(wp[2])
            pose.pose.orientation.w = float(wp[3])
            pose.pose.orientation.x = float(wp[4])
            pose.pose.orientation.y = float(wp[5])
            pose.pose.orientation.z = float(wp[6])
            path_msg.poses.append(pose)

        self.path_pub.publish(path_msg)
        self._node._logger.info(f"Trajectory published for Rviz2")


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("sam_planner_node")
    planner = SamPathPlanner(node)
    node.create_timer(1, planner.compute_path)

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()
        pass


if __name__ == '__main__':
    main()
