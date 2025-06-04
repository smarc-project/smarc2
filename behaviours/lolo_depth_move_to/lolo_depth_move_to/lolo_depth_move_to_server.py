
import numpy as np
import rclpy
from geodesy import utm
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PoseStamped
from rclpy.action import CancelResponse, GoalResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.time import Duration, Time
from smarc_action_base.smarc_action_base import (
    ActionResult,
    ActionType,
    SMARCActionServer,
)
from smarc_mission_msgs.action import BaseAction
from smarc_msgs.msg import Topics
from tf2_geometry_msgs import do_transform_pose_stamped
from tf2_ros import Buffer, TransformException, TransformListener

from lolo_depth_move_to.action_parsing import ActionSubMsg as ActMsg
from lolo_depth_move_to.action_parsing import DepthMoveToActionParsing
from virtual_lolo.lolo import Lolo


class DepthMoveToServer(SMARCActionServer):
    """Action point server to handle DepthMoveTo messages.

    Attributes:
        logger: shorthand for `node.get_logger()`
        robot_name: provided robot name from launch file
        target_frame: frame that goal's should be transformed to
    """

    def __init__(
        self, node: Node, action_name, action_type: ActionType,
    ):
        super().__init__(
            node,
            action_name,
            action_type,
            Topics.WARA_PS_ACTION_SERVER_HB_TOPIC,
        )
        self.logger = node.get_logger()
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(
            self._tf_buffer, self._node, spin_thread=True
        )
        self.logger.set_level(rclpy.logging.LoggingSeverity.INFO)
        self._json_ops: DepthMoveToActionParsing = DepthMoveToActionParsing()

        self.declare_parameters()
        self.vehicle = Lolo(node=node, robot_name=self._robot_name,
                            limits_filename=self._vehicle_limits_filename)


    def declare_parameters(self):
        """Declares all of node's parameters in a single location."""
        node = self._node
        self._robot_name = node.declare_parameter(
            "setpoint_tolerance", self._node.get_namespace()).value
        self._update_rate = node.declare_parameter("update_rate", 10).value
        # If filename not declared, default values should be
        # set by the vehicle and not the server.
        self._vehicle_limits_filename = node.declare_parameter(
            "limits_filename", "").value

    def init_frames(self):
        """
        Initialize the vehicle navigation frames.
        """
        # The goal's frame should be the same as the vehicle's navigation frame.
        # Won't go forward if the vehicle does not have state feeback.
        rate = self._node.create_rate(0.2)
        while self.vehicle.navigation_frame == None and self.vehicle.base_frame == None:
            self.logger.warning(f"Vehicle does not have defined reference and base frames, does {self.vehicle.odom_topic} exists?")
            rate.sleep()
        rate.destroy()
        self.target_frame = self.vehicle.navigation_frame
        self.distance_frame = self.vehicle.base_frame
        self.logger.info(f"Initialized server with:\ntarget_frame: {self.target_frame}\ndistance_frame: {self.distance_frame}")

    @staticmethod
    def _str_posestamp(pose: PoseStamped):
        """Helper function to print PoseStamped Messages nicely."""
        return f"\nFrame: {pose.header.frame_id}\nPosition: {pose.pose.position}\nOrientation: {pose.pose.orientation}"

    def transform_goal(
        self,
        pose_stamped: PoseStamped,
        override_target: str | None = None,
    ) -> PoseStamped:
        """Provides transformed point from pose_stamped.header.frame_id to self.target_frame.

        Raises:
            TransformException when transformation fails allowing for caller to handle exception

        Returns:
            PoseStamped in specified frame
        """
        if override_target is None:
            t = self._tf_buffer.lookup_transform(
                target_frame=self.target_frame,
                source_frame=pose_stamped.header.frame_id,
                time=Time(seconds=0),
                timeout=Duration(seconds=2),
            )
        else:
            t = self._tf_buffer.lookup_transform(
                target_frame=override_target,
                source_frame=pose_stamped.header.frame_id,
                time=Time(seconds=0),
                timeout=Duration(seconds=2),
            )
        # based on ReadMe in repository
        return do_transform_pose_stamped(pose_stamped, t)

    def get_robot_pose_in_msg_frame(self, pose_stamped: PoseStamped) -> PoseStamped:
        """Provides robot position in message frame.

        Useful for showing user how far away the drone is from the target and understand why goal is rejected

        Raises:
            TransformException when transformation fails allowing for caller to handle exception

        Returns:
            pose: pose in specified frame
        """

        t = self._tf_buffer.lookup_transform(
            target_frame=pose_stamped.header.frame_id,
            source_frame=self.target_frame,
            time=rclpy.time.Duration(seconds=0),
            timeout=Duration(seconds=2),
        )
        # based on ReadMe in repository
        return do_transform_pose_stamped(PoseStamped(), t)

    def compute_distance(self, pose_stamped: PoseStamped,
                         check_depth=True) -> float:
        """Euclidean distance to target.

        Args:
            pose_stamped: current location of target in utm frame
        Returns:
            distance: euclidean distance to target
        Raises:
            TransformException when transform fails
        """
        try:
            override_frame = self.distance_frame
            pose_transformed: PoseStamped = self.transform_goal(
                pose_stamped, override_target=override_frame
            )
            self.logger.debug(
                "Position after transform:" + self._str_posestamp(pose_transformed)
            )
        except TransformException as err:
            err_str = "Failed to compute transform when computing distance to target"
            raise TransformException(err_str) from err

        pose_delta = pose_transformed.pose
        if check_depth:
            delta = np.linalg.norm([pose_delta.position.x,
                                    pose_delta.position.y,
                                    pose_delta.position.z])
        else:
            delta = np.linalg.norm([pose_delta.position.x,
                                    pose_delta.position.y])
        return delta

    def _tol_check(self, delta):
        """Checks if vehicle is within tolerance of setpoint.

        Args:
            delta (float): distance to setpoint

        Returns:
            tol_check (bool): true if vehicle is within zone
        """
        if delta > self.vehicle.limits["goal_tolerance_plane"]:
            return False
        else:
            return True

    def convert_to_utm(self, point: GeoPoint) -> PoseStamped:
        """Converts GeoPoint to UTM with proper frame id

        Args:
            point: lat-long geopoint

        Returns:
            PoseStamped that has frame_id labeled based on UTM zone and band.

        """
        point: utm.UTMPoint = utm.fromMsg(point)
        pose_stamp = PoseStamped()
        pose_stamp.pose.position = point.toPoint()
        zone, band = point.gridZone()
        pose_stamp.header.frame_id = f"utm_{zone}_{band}"
        self.logger.debug(
            f"Point Position from lat long:{self._str_posestamp(pose_stamp)}"
        )
        return pose_stamp

    def execution_callback(self, goal_handle: ServerGoalHandle) -> ActionResult:
        """Primary execution callback where goal's are handled after acceptance.

        Args:
            goal_handle: handle to control server and add callbacks

        Returns:
            A populated ActionResult message
        """
        self.logger.debug("Executing callback")
        self.logger.debug(f"{goal_handle.request}")
        result_msg = self.action_type.Result
        moveto_goal = self._json_ops.decode(goal_handle.request.goal, ActMsg.GOAL)
        pose_stamped_utm_frame = self.convert_to_utm(moveto_goal.geopoint)
        pose_stamped_nav_frame = self.transform_goal(pose_stamped=pose_stamped_utm_frame,
                                                     override_target=self.target_frame)

        result_msg.success = self.feedback_loop(pose_stamped_nav_frame,
                                                goal_handle,
                                                int(moveto_goal.timeout))

        return result_msg

    def send_goal_to_vehicle(self, pose: PoseStamped, goal):
        """Sends the goal to the vehicle object (only lolo is supported atm).

        Args:
            pose: target's pose in the vehicle's navigation frame.
            goal: DepthMoveToGoal instance.

        Returns:
            Boolean flag, true if the goal was accepted successfully.
        """
        return self.vehicle.set_goal(x=pose.pose.position.x,
                                    y=pose.pose.position.y,
                                    depth=goal.target_depth,
                                    altitude=goal.min_altitude,
                                    rpm=goal.rpm,
                                    timeout=goal.timeout)

    def goal_callback(self, goal_request: ActionType.Goal) -> GoalResponse:
        """Considers a goal validity and evaluates whether it should be accepted or not.

        Args:
            goal_request (ActionType.Goal): Goal message

        Returns:
            response: Either GoalResponse.Accept or GoalResponse.Reject

        """
        # Initialize vehicle navigation frames.
        self.init_frames()

        goal_request = goal_request.goal
        moveto_goal = self._json_ops.decode(goal_request, ActMsg.GOAL)
        self.logger.info(f"Recieved DepthMoveTo goal with parameters:\n {moveto_goal}")

        # I think the goal should be sent in the robots nav frame?
        pose_stamped_utm_frame = self.convert_to_utm(moveto_goal.geopoint)
        pose_stamped_nav_frame = self.transform_goal(pose_stamped=pose_stamped_utm_frame,
                                                     override_target=self.target_frame)

        # Send the goal to the vehicle and check if it passed the check.
        if not self.send_goal_to_vehicle(pose_stamped_nav_frame, moveto_goal):
            err_str = "Rejecting goal. Goal does not fulfill vehicle limits"
            self.logger.error(err_str)
            return GoalResponse.REJECT

        # Accepts as all criteria fulfilled
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle: ServerGoalHandle) -> CancelResponse:
        """Handles canceling of goal requests.

        Args:
            goal_handle: handle

        Returns:
            Cancel response as ACCEPT
        """
        self.vehicle.reset_goal()
        return CancelResponse.ACCEPT

    def feedback_loop(self, pose_stamped: PoseStamped, goal_handle: ServerGoalHandle,
                      timeout: int) -> bool:
        """Abstracted feedback loop where tolerance checks are conducted.

        Args:
            pose_stamped: target location, in UTM.
            goal_handle: passed in to enable feedback publishing
            timeout: time limit for the server to reach the goal

        Returns:
            Boolean flag, True if the goal was reached within the timeout.
        """
        # FIXME: the tolerance check considers the distance to the waypoint in 3D, which means that
        # if our robot reaches the goal in the XY plane, but not in Z, it will be going in circles
        # until it times out. What's the best way of dealing with this??
        rate = self._node.create_rate(self._update_rate)
        feedback = self.action_type.Feedback
        action_start_time = int(self._node.get_clock().now().nanoseconds * 1e-9)
        goal_reached = True

        # Check tolerance before going into the loop.
        # TODO: Should we consider the depth error as well?!
        d = self.compute_distance(pose_stamped, check_depth=False)
        tol_check = self._tol_check(d)
        while not tol_check:
            # Check if we've been cancelled!
            if goal_handle.is_cancel_requested:
                self.logger.info("Goal was cancelled by client!")
                goal_handle.canceled()
                goal_reached = False
                break
            # Check if we have timed out first.
            if self.timed_out(action_start_time, timeout):
                self.logger.warning(f"Goal was not reached within the time limit of {timeout}s. Aborting goal.")
                goal_handle.abort()
                goal_reached = False
                break

            feedback.feedback = self._json_ops.encode(d)
            goal_handle.publish_feedback(feedback)
            self.vehicle.update()
            rate.sleep()

            # TODO: Should we consider the depth error as well?!
            d = self.compute_distance(pose_stamped, check_depth=False)
            tol_check = self._tol_check(d)
            self.logger.info(f"\nWaypoint reached: {tol_check}\nDistance: {d} m.",
                             throttle_duration_sec=10)

        rate.destroy()
        return goal_reached

    def timed_out(self, start_time: int, timeout: int) -> bool:
        """Checks if action has taken too long.

        Args:
            start_time: start time of feedback_loop of action server.
            timeout: max duration allowed to reach goal.

        Returns:
            Boolean flag, true if goal should be aborted.
        """
        time_now = int(self._node.get_clock().now().nanoseconds * 1e-9)
        return True if (time_now - start_time) > timeout else False


def main(args=None):
    rclpy.init(args=args)
    node_name = "lolo_depth_move_to_server"
    node = rclpy.node.Node(node_name)
    action_type = ActionType(BaseAction)
    lolo_move_to = DepthMoveToServer(node, "auv_depth_move_to", action_type)
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()
