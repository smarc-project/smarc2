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

from go_to_geopoint.geopoint_action import ActionComponent as ActC
from go_to_geopoint.geopoint_action import GeoPointAction

KM_TO_METER = 1000


class GeopointServer(SMARCActionServer):
    """Action point server that handle GotoGeopoint messages.

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
        self.declare_parameters()

        self._pub_setpoint = self._node.create_publisher(
            Pose, f"{self._setpoint_topic}", 2
        )
        self.logger.set_level(rclpy.logging.LoggingSeverity.INFO)
        self._json_ops: GeoPointAction = GeoPointAction()

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

        self._setpoint_topic = node.declare_parameter(
            "setpoint_topic",
            "go_to_setpoint",
            ParameterDescriptor(
                description="Topic to publish setpoint targets to. Will be prepended with 'robot_name'"
            ),
        ).value

        self._goal_threshold = (
            node.declare_parameter(
                "goal_threshold",
                10,
                ParameterDescriptor(
                    description="Distance threshold in kilometers where a goal should be rejected. (Euclidean Norm)"
                ),
            ).value
            * KM_TO_METER
        )

        self.target_frame = (
            f"{self.robot_name}/{self._target_frame_param}{self._frame_suffix}"
        )

        self.distance_frame = f"{self.robot_name}/{self._distance_frame_param}{self._distance_frame_suffix}"

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
        # self.logger.info("Executing callback")
        # self.logger.info(f"{goal_handle.request}")
        result_msg = self.action_type.Result
        geopoint = self._json_ops.decode(goal_handle.request.goal, ActC.GOAL)
        pose_stamped = self.convert_to_utm(geopoint)
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
        self._pub_setpoint.publish(self.goal_base_link.pose)

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
        geo_setpoint = self._json_ops.decode(goal_request, ActC.GOAL)
        self.logger.info(f"Recieved UTM point at {geo_setpoint}")
        pose_stamped = self.convert_to_utm(geo_setpoint)
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
            feedback.feedback = self._json_ops.encode(d)
            goal_handle.publish_feedback(feedback)
            rate.sleep()
            d = self.compute_distance(pose_stamped)
            tol_check = self._tol_check(d)
            self.logger.debug(f"Tol check result: {tol_check}, Distance: {d} m.")

        rate.destroy()
        return


def main(args=None):
    rclpy.init(args=args)
    node_name = "setpoint_server"
    node = rclpy.node.Node(node_name)
    action_type = ActionType(BaseAction)
    setpoint = GeopointServer(node, "go_to_setpoint", action_type, "move-to")
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


if __name__ == "__main__":
    main()
