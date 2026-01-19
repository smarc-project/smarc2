import csv
from pathlib import Path as FilePath
import numpy as np

import rclpy
from action_msgs.msg import GoalStatus
from geographic_msgs.msg import GeoPoint
from rclpy.action import CancelResponse
from rclpy.action.client import ClientGoalHandle
from rclpy.node import Node
from smarc_action_base.smarc_action_base import (
    ActionFeedback,
    ActionResult,
    ActionType,
    SMARCActionClient,
    ActionClientState,
)
from smarc_msgs.action import BaseAction
from geometry_msgs.msg import Pose, PoseStamped
from smarc_control_msgs.msg import Topics as ControlTopics
from smarc_control_msgs.msg import WpMPC, TrajectoryMPC
from nav_msgs.msg import Path

from sam_path_following.path_action import ActionComponent as ActC
from sam_path_following.path_action import PathAction


class PathClient(SMARCActionClient):
    """Client for sending Geopoint message requests to vehicles.

    Attributes:
        logger: shorthand for `node.get_logger()`
    """

    def __init__(
        self,
        node: Node,
        action_name: str,
        action_type: ActionType,
        **kwargs,
    ):
        super().__init__(node, action_name, action_type)
        self.logger = self._node.get_logger()
        self.declare_parameters()
        self._json_ops = PathAction()
        self.logger.set_level(rclpy.logging.LoggingSeverity.INFO)
        self.goal_processed = False

        self.frame_id = '/mocap'

        self.path_msg = Path()
        self.publisher_ = self._node.create_publisher(Path, 'sam/ctrl/conv/planned_trajectory', 10)

        # Wait for server
        # while not self._client.wait_for_server(timeout_sec=1.) and rclpy.ok():
        #     self.logger.info(f"Node {action_name} waiting for go_to_hydropoint server")

        self.logger.info(f"Node {action_name} connected to go_to_hydropoint server")

    def declare_parameters(self):
        """Location to declare parameters."""
        pass


    def run(self):
        # DEBUGGING the trajectory tracking
        #file_path = "/home/parallels/ros2_ws/src/smarc2/behaviours/sam/sam_diving_controller/sam_diving_controller/simple_path_complexity_1.csv"
        #file_path = "/home/orin/colcon_ws/src/smarc2/behaviours/sam/sam_path_following/sam_path_following/trajectories/straight_trajectory_1.csv"
        #file_path = "/home/orin/colcon_ws/src/smarc2/behaviours/sam/sam_path_following/sam_path_following/trajectories/straight_trajectory_1_mod_z.csv"
        file_path = "/home/parallels/ros2_ws/src/smarc2/behaviours/sam/sam_diving_controller/sam_diving_controller/trajectories/straight_trajectory_1.csv"

        np_path = self.read_csv_to_array(file_path)
        
        path = self.convert_np_path_to_trajectory(np_path)
        self.create_path_msg(FilePath(file_path))

        #self.path_msg.header.stamp = self._node.get_clock().now().to_msg()
        #for p in self.path_msg.poses:
        #    p.header.stamp = self.path_msg.header.stamp
        #self.publisher_.publish(self.path_msg)

        self.send_path(path)

        self.logger.info("Path sent")

        self.timer = self._node.create_timer(1.0, self.timer_callback)

        pass
        #self.logger.info("Subscribing to mocap hydro point topic")
        #self.mocap_goal_sub = self._node.create_subscription(PoseStamped, 
        #                                                     ControlTopics.MOCAP_HYDROPOINT,
        #                                                     self.mocap_hydro_cb, 1)

    def timer_callback(self):
        self.path_msg.header.stamp = self._node.get_clock().now().to_msg()
        for p in self.path_msg.poses:
            p.header.stamp = self.path_msg.header.stamp
        self.publisher_.publish(self.path_msg)

    def read_csv_to_array(self, file_path: str):                    
        """                                                         
        Reads a CSV file and converts the elements to a NumPy array.
                                                                    
        Parameters:                                                 
        file_path (str): The path to the CSV file.                  
                                                                    
        Returns:                                                    
        np.array: A NumPy array containing the CSV data.            
        """                                                         
        data = []                                                   
        with open(file_path, 'r') as csvfile:                       
            csvreader = csv.reader(csvfile)                         
            next(csvreader)                                         
            for row in csvreader:                                   
                data.append([float(element) for element in row])    
                                                                    
        return np.array(data)

    def convert_np_path_to_trajectory(self, np_path):
        path = TrajectoryMPC()
        path.header.frame_id = self.frame_id
        for i in range(0,np_path.shape[0]):
            i_wp = WpMPC()
            i_wp.wp.pose.position.x = np_path[i,0]
            i_wp.wp.pose.position.y = np_path[i,1]
            i_wp.wp.pose.position.z = np_path[i,2]
            i_wp.wp.pose.orientation.w = np_path[i,3]
            i_wp.wp.pose.orientation.x = np_path[i,4]
            i_wp.wp.pose.orientation.y = np_path[i,5]
            i_wp.wp.pose.orientation.z = np_path[i,6]
            i_wp.velocities.linear.x = np_path[i,7]  
            i_wp.velocities.linear.y = np_path[i,8]  
            i_wp.velocities.linear.z = np_path[i,9]  
            i_wp.velocities.angular.x = np_path[i,10]
            i_wp.velocities.angular.y = np_path[i,11]
            i_wp.velocities.angular.z = np_path[i,12]
            i_wp.nominal_control.vbs.value = np_path[i,13]
            i_wp.nominal_control.lcg.value = np_path[i,14]
            i_wp.nominal_control.rpms.thruster_1_rpm = int(np_path[i,17])
            i_wp.nominal_control.rpms.thruster_2_rpm = int(np_path[i,18])
            i_wp.nominal_control.thruster_angles.thruster_vertical_radians = np_path[i,15]
            i_wp.nominal_control.thruster_angles.thruster_horizontal_radians = np_path[i,16]

            path.trajectory.append(i_wp)

        return path

    def create_path_msg(self, csv_path):
        self.path_msg.header.frame_id = self.frame_id

        #if not csv_path.exists():
        #    self.get_logger().error(f'CSV file not found: {csv_path}')
        #    return 

        with csv_path.open() as f:
            reader = csv.DictReader(f)
            #for row in csvreader:
            for row in reader:
                pose = PoseStamped()
                pose.header.frame_id = self.frame_id
                pose.pose.position.x = float(row['x'])
                pose.pose.position.y = float(row['y'])
                pose.pose.position.z = float(row['z'])
                # orientation left as default (0,0,0,1)
                self.path_msg.poses.append(pose)

        self.logger.info(f'Loaded {len(self.path_msg.poses)} poses from {csv_path}')
        #return path_msg

    def send_path(self, path: Path):

        if not self.goal_processed:

            if self.state != ActionClientState.SENT:

                if self.state == ActionClientState.ACCEPTED or self.state == ActionClientState.RUNNING:
                    self.goal_processed = True
                    #self._node.destroy_subscription(self.mocap_goal_sub)
                    return

                self.logger.info(f"Sending trajectory")
                goal_msg = BaseAction.Goal()
                goal_msg.goal = self._json_ops.encode(path)
                self.send_goal(goal_msg)


    def goal_response_callback(self, goal_handle: ClientGoalHandle):
        """Result when a goal is sent to the server."""
        if not goal_handle.accepted:
            self.logger.info("Goal was not accepted")
            return
        else:
            self.logger.info("Goal was accepted")


    def feedback_callback(self, feedback_msg: ActionFeedback):
        """Result when a goal is sent to the server."""
        self.logger.debug(f"Received feedback {feedback_msg.feedback}")
        self.dist_rem = self._json_ops.decode(
            feedback_msg.feedback,
            ActC.FEEDBACK,
        )

    def result_callback(self, result: ActionResult, status: GoalStatus):
        """Result when a goal is sent to the server."""
        self.logger.info(f"Waypoint reached boolean: {result}")
        if result.success:
            return self.get_goal_success()
        else:
            return self.get_goal_error()

    def cancel_callback(self, response):
        """Cancellation callback.

        Args:
            response: receives CancelGoal action msg
        """
        if len(response.goals_canceling) > 0:
            self.logger.info("Successfully canceled goal.")
        else:
            self.logger.info("Unsuccessfully canceled goal.")

    def cancel_geopoint(self):
        """Interacts with action server to cancel action.

        Returns:
            Boolean where true signifies a goal was successfully canceled. False if not true.

        """
        self.cancel_goal(self.cancel_callback)




def main(args=None):
    rclpy.init(args=args)
    node_name = "path_client"
    node = Node(node_name)
    action_type = ActionType(BaseAction)
    path_client = PathClient(node, "sam_david/auv_trajectory_tracking", action_type)
    path_client._setup()
    path_client.run()
    rclpy.spin(node)


if __name__ == "__main__":
    main()
