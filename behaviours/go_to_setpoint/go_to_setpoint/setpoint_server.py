from typing import Optional
import traceback

import numpy as np
import rclpy
from geodesy import utm
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PoseStamped, Pose
from rcl_interfaces.msg import ParameterDescriptor
from rclpy.action import CancelResponse, GoalResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.time import Duration, Time
from smarc_action_client.smarc_action_client import ActionType, SMARCActionServer
from smarc_mission_msgs.action import GotoSetpoint
from tf2_geometry_msgs import do_transform_pose_stamped
from tf2_ros import Buffer, TransformException, TransformListener

KM_TO_METER = 100


class SetpointServer(SMARCActionServer):
    def __init__(self, node: rclpy.node.Node, action_name, action_type: ActionType):
        super().__init__(node, action_name, action_type)
        self.logger = node.get_logger()
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(
            self._tf_buffer, self._node, spin_thread=True
        )
        self.declare_parameters()

        self._pub_setpoint = self._node.create_publisher(
            Pose, f"{self.robot_name}/{self._setpoint_topic}", 2
        )
        self.logger.set_level(rclpy.logging.LoggingSeverity.DEBUG)

    def declare_parameters(self):
        """Declares node's parameters in a single space for easier editing."""
        node = self._node
        self.robot_name = node.declare_parameter("robot_name", "Quadrotor").value
        self._target_frame_param = node.declare_parameter(
            "target_frame", "base_link"
        ).value

        self._source_frame = node.declare_parameter(
            "source_frame",
            "utm",
            ParameterDescriptor(
                description="UTM source frame that values setpoints will be sent from."
            ),
        ).value

        self._frame_suffix = node.declare_parameter(
            "frame_suffix",
            "_gt",
            ParameterDescriptor(
                description="Frame suffix for transform. Commonly is '_gt' for ground truth if applicable"
            ),
        ).value

        self._setpoint_tol = node.declare_parameter(
            "setpoint_tolerance",
            0.1,
            ParameterDescriptor(
                description="Setpoint tolerance for one the goal is considered achieved (think of it as radius)"
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
                    description="Distance threshold in kilometers where a goal should be rejected."
                ),
            ).value
            * KM_TO_METER
        )

        if self._frame_suffix == "":
            self.target_frame = f"{self.robot_name}/{self._target_frame_param}"
        else:
            self.target_frame = (
                f"{self.robot_name}/{self._target_frame_param}{self._frame_suffix}"
            )

    def transform_goal(self, pose_stamped: PoseStamped) -> PoseStamped:
        """Provides transformed point from self._source_frame to self.target_frame.

        Raises:
            TransformException when transformation fails allowing for caller to handle exception

        Returns:
            pose: pose in specified frame
        """
        t = self._tf_buffer.lookup_transform(
            self.target_frame,
            pose_stamped.header.frame_id,
            Time(seconds=0),
            timeout=Duration(seconds=2),
        )
        # based on ReadMe in repository
        return do_transform_pose_stamped(pose_stamped, t)

    def compute_distance(self, pose_stamped: PoseStamped) -> float:
        """Euclidean distance to target.

        Args:
            utm_val: current location of utm target in self._source_frame
        Returns:
            distance: euclidean distance to target
        Raises:
            TransformException when transform fails
        """
        try:
            # FIXME: The transform I am getting here is incorrect and needs fixing
            position = self.transform_goal(pose_stamped)
            self.logger.debug(
                f"Position after tranform to {self.target_frame}: {position}"
            )
        except TransformException as err:
            err_str = "Failed to compute transform when computing distance to target"
            raise TransformException(err_str) from err

        position = pose_stamped.pose
        delta = np.sqrt(
            (position.position.x) ** 2
            + (position.position.y) ** 2
            + (position.position.z) ** 2
        )
        return delta

    def tol_check(self, delta):
        """Checks if vehicle is within tolerance of setpoint.

        Args:
            delta (float): distance to setpoint

        Returns:
            tol_check (bool): if vehicle is within zone
        """
        if delta > self._setpoint_tol:
            return False
        else:
            return True

    def convert_to_utm(self, point: GeoPoint) -> PoseStamped:
        point: utm.UTMPoint = utm.fromMsg(point)
        pose_stamp = PoseStamped()
        pose_stamp.pose.position = point.toPoint()
        zone, band = point.gridZone()
        pose_stamp.header.frame_id = f"utm_{zone}_{band}"
        return pose_stamp

    def execution_callback(self, goal_handle: ServerGoalHandle) -> ActionType.Result:
        self.logger.info("Executing callback")
        self.logger.info(f"{goal_handle.request}")
        result_msg = self.action_type.Result
        pose_stamped = self.convert_to_utm(goal_handle.request.setpoint)
        try:
            self.goal_base_link = self.transform_goal(pose_stamped)
        except TransformException as err:
            self.logger.error(
                f"Failed to transform goal target frame {self.target_frame} from source {self._source_frame}.\n\t Tf2 exception error {err}"
            )
            goal_handle.abort()
            result_msg.reached_setpoint = False
            return result_msg
        self.logger.info(
            f"Publishing to {self._setpoint_topic}, with position {self.goal_base_link}"
        )
        # TODO: need to implement feedback here
        self._pub_setpoint.publish(self.goal_base_link.pose)
        result_msg.reached_setpoint = True
        return result_msg

    def goal_callback(self, goal_request: ActionType.Goal) -> GoalResponse:
        """Considers a goal validity and evaluates whether it should be accepted or not.

        Args:
            goal_request (ActionType.Goal): Goal message

        Returns:
            response: Either GoalResponse.Accept or GoalResponse.Reject

        """
        geo_setpoint = goal_request.setpoint
        self.logger.info(f"Recieved UTM point at {geo_setpoint}")
        pose_stamped = self.convert_to_utm(geo_setpoint)
        try:
            dist = self.compute_distance(pose_stamped)
        except TransformException as err:
            err_str = "Could not successfully compute transform. Rejecting goal!\n"
            exec_up = TransformException(err_str)
            exec_up.__cause__ = err
            self.logger.info(err_str)
            self.logger.debug(traceback.print_exception(exec()))
            return GoalResponse.REJECT
        if dist >= self._goal_threshold:
            err_str = f"Rejecting goal due to violating distance threshold. Criteria: {dist:.1f} >= {self._goal_threshold:.1f}"
            self.logger.info(err_str)
            return GoalResponse.REJECT
        # Accepts as all criteria fulfilled
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle) -> CancelResponse:
        # TODO: Implement method to cancel the goal (move the target)
        pose_msg = Pose()
        pose_msg.header.frame_id = self.target_frame
        self._pub_setpoint.publish(pose_msg)
        return CancelResponse.ACCEPT


def main(args=None):
    rclpy.init(args=args)
    node_name = "setpoint_client"
    node = rclpy.node.Node(node_name)
    action_type = ActionType(GotoSetpoint)
    setpoint = SetpointServer(node, "go_to_setpoint", action_type)
    rclpy.spin(node)


if __name__ == "__main__":
    main()
