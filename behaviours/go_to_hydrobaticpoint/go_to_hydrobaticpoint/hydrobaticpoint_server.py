import traceback
import time
import numpy as np
import rclpy
from geodesy import utm
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
from smarc_msgs.msg import Topics as SmarcTopics
from smarc_control_msgs.msg import Topics as ControlTopics

from tf2_geometry_msgs import do_transform_pose_stamped
from tf2_ros import Buffer, TransformException, TransformListener

from go_to_hydrobaticpoint.hydrobaticpoint_action import ActionComponent as ActC
from go_to_hydrobaticpoint.hydrobaticpoint_action import HydrobaticPointAction

KM_TO_METER = 1000

class HydropointServer(SMARCActionServer):
    """Action point server that handle GotoGeopoint messages.

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
            SmarcTopics.WARA_PS_ACTION_SERVER_HB_TOPIC,
        )
        self.logger = node.get_logger()
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(
            self._tf_buffer, self._node, spin_thread=True
        )
        self.declare_parameters()

        self._pub_setpoint = self._node.create_publisher(
            PoseStamped, ControlTopics.WAYPOINT, 2
        )
        self.logger.set_level(rclpy.logging.LoggingSeverity.INFO)
        self._json_ops: HydrobaticPointAction = HydrobaticPointAction()

    def declare_parameters(self):
        """Declares all of node's parameters in a single location."""
        node = self._node
        self.robot_name = node.declare_parameter("robot_name", "Quadrotor").value
        self._target_frame_param = node.declare_parameter("target_frame", "odom").value

        self._distance_frame_param = node.declare_parameter(
            "distance_frame",
            "base_link",
            ParameterDescriptor(
                description="Frame for which the distance to target will be computed (usually base_link)"
            ),
        ).value

        self._distance_frame_suffix = node.declare_parameter(
            "distance_frame_suffix",
            "_gt",
            ParameterDescriptor(
                description="Frame suffix for distance frame. Commonly is '_gt' for ground truth if applicable"
            ),
        ).value

        self._frame_suffix = node.declare_parameter(
            "frame_suffix",
            "_gt",
            ParameterDescriptor(
                description="Frame suffix for transform. Commonly is '_gt' for ground truth if applicable"
            ),
        ).value

        self._setpoint_tol: float = node.declare_parameter(
            "setpoint_tolerance",
            0.25,
            ParameterDescriptor(
                description="Setpoint tolerance for when the goal is considered achieved (Euclidean norm)."
            ),
        ).value

        # self._setpoint_topic = node.declare_parameter(
        #     "setpoint_topic",
        #     "go_to_setpoint",
        #     ParameterDescriptor(
        #         description="Topic to publish setpoint targets to. Will be prepended with 'robot_name'"
        #     ),
        # ).value

        self._goal_threshold = (
            node.declare_parameter(
                "goal_threshold",
                10,
                ParameterDescriptor(
                    description="Distance threshold in meters where a goal should be rejected. (Euclidean Norm)"
                ),
            ).value
        )

        self.target_frame = (
            f"{self.robot_name}/{self._target_frame_param}{self._frame_suffix}"
        )
        self.logger.info(f"Target frame {self.target_frame}")

        self.distance_frame = f"{self.robot_name}/{self._distance_frame_param}{self._distance_frame_suffix}"
        self.logger.info(f"Distance frame {self.distance_frame}")

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

        # TODO: add orientation errors

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

    def execution_callback(self, goal_handle: ServerGoalHandle) -> ActionResult:
        """Primary execution callback where goal's are handled after acceptance.

        Args:
            goal_handle: handle to control server and add callbacks

        Returns:
            A populated ActionResult message
        """
        result_msg = self.action_type.Result
        hydropoint = self._json_ops.decode(goal_handle.request.goal, ActC.GOAL)
        self.logger.info(f"Hydropoint sent: {hydropoint}")
        time.sleep(5)
        self._pub_setpoint.publish(hydropoint)
        status = self.feedback_loop(hydropoint, goal_handle)
        if status == "cancelled":
            self.logger.info("Goal was cancelled by client.")
            result_msg.success = False
            return result_msg
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
        hydro_setpoint = self._json_ops.decode(goal_request, ActC.GOAL)
        self.logger.info(f"Recieved setpoint at {hydro_setpoint}")
        pose_stamped = hydro_setpoint
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
        pose_msg = Pose()

        self._pub_setpoint.publish(pose_msg)

        return CancelResponse.ACCEPT

    def feedback_loop(self, pose_stamped: PoseStamped, goal_handle: ServerGoalHandle):
        """Abstracted feedback loop where tolerance checks are conducted.

        Args:
            pose_stamped: target location
            goal_handle: passed in to enable feedback publishing
        """
        rate = self._node.create_rate(2)
        d = self.compute_distance(pose_stamped)
        feedback = self.action_type.Feedback
        tol_check = self._tol_check(d)
        while not tol_check:
            if goal_handle.is_cancel_requested:
                self.logger.info("Goal was cancelled by client.")
                goal_handle.canceled()
                self.publish_stop_setpoint()
                return "cancelled"
            feedback.feedback = self._json_ops.encode(d)
            goal_handle.publish_feedback(feedback)
            rate.sleep()
            d = self.compute_distance(pose_stamped)
            tol_check = self._tol_check(d)
            self.logger.debug(f"Tol check result: {tol_check}, Distance: {d} m.")
        rate.destroy()
        return "done"


def main(args=None):
    rclpy.init(args=args)
    node_name = "auv_hydrobatic_move_to"
    node = rclpy.node.Node(node_name)
    action_type = ActionType(BaseAction)
    setpoint = HydropointServer(node, "go_to_hydropoint", action_type)
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()
