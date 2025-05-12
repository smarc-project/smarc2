import traceback

import numpy as np
import rclpy
from geodesy import utm
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import Pose, PoseStamped
from rcl_interfaces.msg import ParameterDescriptor
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

from lolo_move_to.move_to_action import ActionComponent as ActC
from lolo_move_to.move_to_action import MoveToAction
from lolo_move_to.lolo import Lolo

KM_TO_METER = 1000


class MoveToServer(SMARCActionServer):
    """Action point server to handle MoveTo messages.

    Attributes:
        logger: shorthand for `node.get_logger()`
        robot_name: provided robot name from launch file
        target_frame: frame that goal's should be transformed to
    """

    def __init__(
        self, node: Node, action_name, action_type: ActionType, task_name: str
    ):
        super().__init__(
            node,
            action_name,
            action_type,
            task_name,
            Topics.WARA_PS_ACTION_SERVER_HB_TOPIC,
        )
        self.logger = node.get_logger()
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(
            self._tf_buffer, self._node, spin_thread=True
        )
        self.logger.set_level(rclpy.logging.LoggingSeverity.INFO)
        self._json_ops: MoveToAction = MoveToAction()

        # self.declare_parameters()

        # FIXME: we should configure lolo here. Robot name + navigation frame of reference.
        self.lolo = Lolo()

        # self._pub_setpoint = self._node.create_publisher(
            # Pose, f"{self.robot_name}/{self._setpoint_topic}", 2
        # )


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

    def compute_distance(self, pose_stamped: PoseStamped) -> float:
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
        delta = np.sqrt(
            (pose_delta.position.x) ** 2
            + (pose_delta.position.y) ** 2
            + (pose_delta.position.z) ** 2
        )
        return delta

    def _tol_check(self, delta):
        """Checks if vehicle is within tolerance of setpoint.

        Args:
            delta (float): distance to setpoint

        Returns:
            tol_check (bool): true if vehicle is within zone
        """
        if delta > self._setpoint_tol:
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
        self.logger.info("Executing callback")
        self.logger.info(f"{goal_handle.request}")
        result_msg = self.action_type.Result
        moveto_goal = self._json_ops.decode(goal_handle.request.goal, ActC.GOAL)
        # FIXME: we need a better sanity check for Lolo.
        # e.g. try: self.lolo.check_goal(goal)
        pose_stamped = self.convert_to_utm(moveto_goal.geopoint)
        try:
            self.goal_base_link = self.transform_goal(pose_stamped)
            self.logger.debug(
                f"Goal in {self.target_frame} is {self._str_posestamp(self.goal_base_link)}"
            )
        except TransformException as err:
            self.logger.error(
                f"Failed to transform goal target frame {self.target_frame} from source {self._source_frame}.\n\t Tf2 exception error {err}"
            )
            goal_handle.abort()
            result_msg.success = False
            return result_msg
        self.logger.info(
            f"Publishing to {self._setpoint_topic}, Setpoint"
            + self._str_posestamp(self.goal_base_link)
        )

        # TODO: once the goal has been sanity-checked, update it in lolo.
        # FIXME: which frame of reference should the waypoint be expressed in?
        self.lolo.set_goal(target_pose=pose_stamped, goal=moveto_goal)

        self.feedback_loop(pose_stamped, goal_handle)

        result_msg.success = True
        return result_msg

    def goal_callback(self, goal_request: ActionType.Goal) -> GoalResponse:
        """Considers a goal validity and evaluates whether it should be accepted or not.

        Args:
            goal_request (ActionType.Goal): Goal message

        Returns:
            response: Either GoalResponse.Accept or GoalResponse.Reject

        """
        goal_request = goal_request.goal
        moveto_goal = self._json_ops.decode(goal_request, ActC.GOAL)
        self.logger.info(f"Recieved MoveTo goal with parameters:\n {moveto_goal}")
        # FIXME: We need a better goal sanity check for Lolo.
        pose_stamped = self.convert_to_utm(moveto_goal.geopoint)
        try:
            dist = self.compute_distance(pose_stamped)
        except TransformException as err:
            err_str = "Could not successfully compute transform. Rejecting goal!\n"
            exec_up = TransformException(err_str)
            exec_up.__cause__ = err
            # Adding error message to traceback for debug log.
            self.logger.info(err_str)
            self.logger.debug(traceback.format_exc())
            return GoalResponse.REJECT

        if dist >= self._goal_threshold:
            err_str = f"Rejecting goal due to violating distance threshold. Criteria: {dist:.1f} >= {self._goal_threshold:.1f}"
            self.logger.info(err_str)

            # providing additional details if possible about error
            try:
                pose = self.get_robot_pose_in_msg_frame(pose_stamped)
                err_str = "Robot pose in message frame is:" + self._str_posestamp(pose)
                self.logger.debug(err_str)
            except TransformException:
                pass
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
        self.lolo.reset_goal()
        return CancelResponse.ACCEPT

    def feedback_loop(self, pose_stamped: PoseStamped, goal_handle: ServerGoalHandle):
        """Abstracted feedback loop where tolerance checks are conducted.

        Args:
            pose_stamped: target location, in UTM.
            goal_handle: passed in to enable feedback publishing
        """
        # TODO: make the loop's frequency a parameter.
        rate = self._node.create_rate(self.lolo.update_freq)
        d = self.compute_distance(pose_stamped)
        feedback = self.action_type.Feedback
        tol_check = self._tol_check(d)
        while not tol_check:
            feedback.feedback = self._json_ops.encode(d)
            goal_handle.publish_feedback(feedback)
            rate.sleep()
            # TODO: update lolo and send setpoints.
            self.lolo.update()
            d = self.compute_distance(pose_stamped)
            tol_check = self._tol_check(d)
            self.logger.debug(f"Tol check result: {tol_check}, Distance: {d} m.")

        rate.destroy()
        return


def main(args=None):
    rclpy.init(args=args)
    node_name = "setpoint_client"
    node = rclpy.node.Node(node_name)
    action_type = ActionType(BaseAction)
    setpoint = MoveToServer(node, "go_to_setpoint", action_type, "move-to")
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()
