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
from smarc_msgs.action import BaseAction
from smarc_msgs.msg import Topics
from tf2_geometry_msgs import do_transform_pose_stamped
from tf2_ros import Buffer, TransformException, TransformListener

from lolo_loiter.action_parsing import ActionSubMsg as ActMsg
from lolo_loiter.action_parsing import LoiterActionParsing
from virtual_lolo.lolo import Lolo

MIN_ALTITUDE = 1
SURFACE_DEPTH = -1

class LoiterServer(SMARCActionServer):
    """Action point server to handle Loiter messages.

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
        self._json_ops: LoiterActionParsing = LoiterActionParsing()

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
        if delta > self.vehicle.limits["loiter_goal_tolerance"]:
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
        loiter_goal = self._json_ops.decode(goal_handle.request.goal, ActMsg.GOAL)
        self.vehicle.update()
        pose_stamped_nav_frame = PoseStamped()
        pose_stamped_nav_frame.header.frame_id = self.vehicle.navigation_frame
        pose_stamped_nav_frame.pose.position.x = self.vehicle.pos_x
        pose_stamped_nav_frame.pose.position.y = self.vehicle.pos_y
        result_msg.success = self.feedback_loop(
            pose_stamped_nav_frame,
            goal_handle,
            int(loiter_goal.timeout)
        )
        return result_msg

    def send_goal_to_vehicle(self, goal):
        """Sends the goal to the vehicle object (only lolo is supported atm).

        Args:
            goal: LoiterGoal instance.

        Returns:
            Boolean flag, true if the goal was accepted successfully.
        """
        self.vehicle.update()
        return self.vehicle.set_goal(x=self.vehicle.pos_x,
                                    y=self.vehicle.pos_y,
                                    depth=float(SURFACE_DEPTH),
                                    altitude=float(MIN_ALTITUDE),
                                    rpm=float(self.vehicle.limits["loiter_rpm"]),
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
        loiter_goal = self._json_ops.decode(goal_request, ActMsg.GOAL)
        self.logger.info(f"Recieved Loiter goal with parameters:\n {loiter_goal}")

        # Send the goal to the vehicle and check if it passed the check.
        if not self.send_goal_to_vehicle(loiter_goal):
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

    def feedback_loop(self,  pose_stamped: PoseStamped,
                      goal_handle: ServerGoalHandle,
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

        timed_out = self.timed_out(action_start_time, timeout)
        while not timed_out:
            # Check if we've been cancelled!
            if goal_handle.is_cancel_requested:
                self.logger.info("Goal was cancelled by client!")
                goal_handle.canceled()
                goal_reached = False
                break

            d = self.compute_distance(pose_stamped, check_depth=False)
            if not self._tol_check(d):
                self.vehicle.update()
                self.logger.info(f"Moved too far away from the point around which we loiter, distance: {d} m. Moving closer now.")

            time_now = int(self._node.get_clock().now().nanoseconds * 1e-9)  # now

            time_until_done = timeout - (time_now - action_start_time)
            feedback.feedback = self._json_ops.encode(float(time_until_done))
            self.logger.info(f"Loitering for {time_until_done} more seconds.")
            goal_handle.publish_feedback(feedback)

            rate.sleep()

            timed_out = self.timed_out(action_start_time, timeout)

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
    node_name = "lolo_loiter_server"
    node = rclpy.node.Node(node_name)
    action_type = ActionType(BaseAction)
    lolo_loiter = LoiterServer(node, "loiter", action_type)
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()
