import csv
from pathlib import Path as FilePath

import numpy as np
import rclpy
from action_msgs.msg import GoalStatus
from std_msgs.msg import Bool
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import Pose, PoseStamped
from nav_msgs.msg import Path
from rclpy.action import CancelResponse
from rclpy.action.client import ClientGoalHandle
from rclpy.node import Node
from rclpy.time import Time
from smarc_action_base.smarc_action_base import (
    ActionClientState,
    ActionFeedback,
    ActionResult,
    ActionType,
    SMARCActionClient,
)
from smarc_control_msgs.msg import Topics as ControlTopics
from smarc_control_msgs.msg import TrajectoryMPC, WpMPC
from smarc_msgs.action import BaseAction
from tf2_ros import TransformException

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
        self.start_mission = False  


        self.world_prefix = (
            self._node.get_parameter("world_prefix").get_parameter_value().string_value
        )

        self.world_prefix = (
            self._node.get_parameter("world_prefix").get_parameter_value().string_value
        )

        self.frame_id = self.world_prefix + "mocap"

        self.path_msg = Path()
        self.trajectory_msg = TrajectoryMPC()
        self.path_pub = self._node.create_publisher(Path, "ctrl/conv/planned_path", 10)
        self.trajectory_pub = self._node.create_publisher(
            TrajectoryMPC, "ctrl/conv/planned_trajectory", 10
        )

        # Wait for server
        # while not self._client.wait_for_server(timeout_sec=1.) and rclpy.ok():
        #     self.logger.info(f"Node {action_name} waiting for go_to_hydropoint server")

        self.logger.info(f"Node {action_name} connected to go_to_hydropoint server")
        self.logger.info(f"Frame id: {self.frame_id}")

    def declare_parameters(self):
        """Location to declare parameters."""
        self._node.declare_parameter(
            "world_prefix", ""
        )  # choose if we're in the tank of not
            

    def uwcomm_start_mission(self, start_msg: Bool):
        if not self.start_mission:
            self.logger.info(f"Start received from uwcomm: {start_msg.data}")
        self.start_mission = True

    def run(self):
        
        self.uw_comm_goal_sub = self._node.create_subscription(Bool,    
                                                              '/sam/uwgps/nachos',
                                                              self.uwcomm_start_mission, 1)
                                                              
        # DEBUGGING the trajectory tracking
        #HERE = FilePath(__file__).parent  # resolves the directory of the script.
        HERE = FilePath("/home/orin/colcon_ws/src/smarc2/behaviours/sam/sam_path_following/sam_path_following/")
        # file_path = HERE / "trajectories" / "2026-01-19__straight_trajectory_1m.csv"
        # file_path = HERE / "trajectories" / "turbo_turn_N11_alpha180_radius2.csv"
        file_path = (
            #HERE / "trajectories" / "turbo_turn_zigzag_N9_alpha14_radius0.5.csv"
            #HERE / "trajectories" / "three_point_turn.csv"
            #HERE / "trajectories" / "straight_line_return_surface.csv"
            #HERE / "trajectories" / "N_point_N5.csv"
            #HERE / "trajectories" / "straight_line_s-curve_depth-1.5_return_dive.csv"
            #HERE / "trajectories" / "straight_line_s-curve_depth-1.5_90deg_turn_dive.csv"
            #HERE / "trajectories" / "surface_test.csv"
            #HERE / "trajectories" / "return_dive.csv"
            
            ## Dive tests run on SAM in increasing difficulty
            #HERE / "trajectories" / "gentle_straight_dive.csv" # straight dive during the experiments
            #HERE / "trajectories" / "gentle_turn_dive.csv"  # turn towards the corner
            #HERE / "trajectories" / "sharper_turn_dive.csv"  # sharper turn dive (full 90 degree turn)
            HERE / "trajectories" / "sharper_left_turn_dive.csv"  # sharper turn dive (full 90 degree turn)
            #HERE / "trajectories" / "sharper_turn_dive_2.csv"  # sharper turn dive (full 90 degree turn)
            #HERE / "trajectories" / "gentle_dive_test.csv"  # full turn dive
            #HERE / "trajectories" / "steep_straight_dive.csv"  # steep straight dive
            #HERE / "trajectories" / "gentle_straight_dive_with_return.csv"  # gentle straight dive with return

        )

        np_path = self.read_csv_to_array(file_path)
        self.mpc_trajectory = self.convert_np_path_to_trajectory(np_path)
        self.create_path_msg(FilePath(file_path))



        self.trajectory_msg = self.mpc_trajectory
        self.timer = self._node.create_timer(1.0, self.timer_callback)

        pass
        # self.logger.info("Subscribing to mocap hydro point topic")
        # self.mocap_goal_sub = self._node.create_subscription(PoseStamped,
        #                                                     ControlTopics.MOCAP_HYDROPOINT,
        #                                                     self.mocap_hydro_cb, 1)

    def timer_callback(self):

        self.logger.debug("running timer callback")
        if self.start_mission and self.mpc_trajectory is not None:
                self.logger.info("Starting path following mission")
                if not self.goal_processed:
                    if self.state != ActionClientState.SENT:

                        if self.state == ActionClientState.ACCEPTED or self.state == ActionClientState.RUNNING:
                            self.goal_processed = True
                            self.start_mission = False
                            self.mpc_trajectory = None
                            #self._node.destroy_subscription(self.mocap_goal_sub)
                            return
                        
                        self.send_path(self.mpc_trajectory)
                        self.logger.info("Trajectory sent")

        now = self._node.get_clock().now()
        stamp = now.to_msg()

        self.path_msg.header.stamp = stamp
        for p in self.path_msg.poses:
            p.header.stamp = stamp

        self.path_pub.publish(self.path_msg)
        self.trajectory_pub.publish(self.trajectory_msg)

    def read_csv_to_array(self, file_path: str):
        """
        Reads a CSV file and converts the elements to a NumPy array.

        Parameters:
        file_path (str): The path to the CSV file.

        Returns:
        np.array: A NumPy array containing the CSV data.
        """
        data = []
        with open(file_path, "r") as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)
            for row in csvreader:
                data.append([float(element) for element in row])

        return np.array(data)

    def convert_np_path_to_trajectory(self, np_path):
        """Convert numpy trajectory to TrajectoryMPC message.

        The MPC stage cost tracks position (cols 0-2), quaternion (cols 3-6),
        and surge velocity (col 7).  The terminal cost additionally tracks
        the full velocity vector (cols 7-12) to drive the vehicle to a stop.
        Actuator references (cols 13-18) are not part of the cost -- the MPC
        freely chooses actuator values within its constraints.  We set them
        to neutral defaults so the message works with both 13-column and
        19-column CSVs.
        """
        n_cols = np_path.shape[1]
        path = TrajectoryMPC()
        path.header.frame_id = self.frame_id
        for i in range(0, np_path.shape[0]):
            i_wp = WpMPC()
            i_wp.wp.pose.position.x = np_path[i, 0]
            i_wp.wp.pose.position.y = np_path[i, 1]
            i_wp.wp.pose.position.z = np_path[i, 2]
            i_wp.wp.pose.orientation.w = np_path[i, 3]
            i_wp.wp.pose.orientation.x = np_path[i, 4]
            i_wp.wp.pose.orientation.y = np_path[i, 5]
            i_wp.wp.pose.orientation.z = np_path[i, 6]

            if n_cols > 7:
                i_wp.velocities.linear.x = np_path[i, 7]
                i_wp.velocities.linear.y = np_path[i, 8]
                i_wp.velocities.linear.z = np_path[i, 9]
                i_wp.velocities.angular.x = np_path[i, 10]
                i_wp.velocities.angular.y = np_path[i, 11]
                i_wp.velocities.angular.z = np_path[i, 12]

            # Neutral actuator defaults -- not tracked by the MPC cost.
            i_wp.nominal_control.vbs.value = 50.0
            i_wp.nominal_control.lcg.value = 50.0
            i_wp.nominal_control.rpms.thruster_1_rpm = 0
            i_wp.nominal_control.rpms.thruster_2_rpm = 0
            i_wp.nominal_control.thruster_angles.thruster_vertical_radians = 0.0
            i_wp.nominal_control.thruster_angles.thruster_horizontal_radians = 0.0

            path.trajectory.append(i_wp)

        return path

    def create_path_msg(self, csv_path):
        self.path_msg.header.frame_id = self.frame_id

        # if not csv_path.exists():
        #    self.get_logger().error(f'CSV file not found: {csv_path}')
        #    return

        with csv_path.open() as f:
            reader = csv.DictReader(f)
            # for row in csvreader:
            for row in reader:
                pose = PoseStamped()
                pose.header.frame_id = self.frame_id
                pose.pose.position.x = float(row["x"])
                pose.pose.position.y = float(row["y"])
                pose.pose.position.z = float(row["z"])
                pose.pose.orientation.x = float(row["q1"])
                pose.pose.orientation.y = float(row["q2"])
                pose.pose.orientation.z = float(row["q3"])
                pose.pose.orientation.w = float(row["q0"])
                self.path_msg.poses.append(pose)

        self.logger.info(f"Loaded {len(self.path_msg.poses)} poses from {csv_path}")

    def send_path(self, path: Path):

        if not self.goal_processed:
            if self.state != ActionClientState.SENT:
                if (
                    self.state == ActionClientState.ACCEPTED
                    or self.state == ActionClientState.RUNNING
                ):
                    self.goal_processed = True
                    # self._node.destroy_subscription(self.mocap_goal_sub)
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
    path_client = PathClient(node, "auv_trajectory_tracking", action_type)
    path_client._setup()
    path_client.run()
    rclpy.spin(node)


if __name__ == "__main__":
    main()
