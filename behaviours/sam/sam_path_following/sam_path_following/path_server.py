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

from sam_path_following.path_action import ActionComponent as ActC
from sam_path_following.path_action import PathAction

KM_TO_METER = 1000

class PathServer(SMARCActionServer):
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

        self.path = None
        self.path_len = None
        self.current_idx = 0

        #self.declare_parameters()

        self.logger.set_level(rclpy.logging.LoggingSeverity.INFO)

        self._json_ops: PathAction = PathAction()

    # TODO: Cancel process. Need to stop the controller as well, similar to the wp action server.

    def declare_parameters(self):
        """Declares all of node's parameters in a single location."""

        # TODO: Which ones are actually needed?

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

    def _save_path(self, path):
        """
        Convert path from list to numpy array.
        """
        self.path = np.asarray(path)


    def goal_callback(self, goal_request: ActionType.Goal) -> GoalResponse:
        """Considers a goal validity and evaluates whether it should be accepted or not.

        Args:
            goal_request (ActionType.Goal): Goal message

        Returns:
            response: Either GoalResponse.Accept or GoalResponse.Reject

        """
        # TODO: Think of whether you want to reject any goal. For now, accept
        # everything, as we assume the planner to know what it's doing.
        goal_request = goal_request.goal
        path = self._json_ops.decode(goal_request, ActC.GOAL)
        self.logger.info(f"Recieved path")
        self._save_path(path)
        self.path_len = len(self.path) # TODO: Check which index to use, 0 or 1

        # Accepts as all criteria fulfilled
        return GoalResponse.ACCEPT


    def execution_callback(self, goal_handle: ServerGoalHandle) -> ActionResult:
        """Primary execution callback where goal's are handled after acceptance.

        Args:
            goal_handle: handle to control server and add callbacks

        Returns:
            A populated ActionResult message
        """
        result_msg = self.action_type.Result
        status = self.feedback_loop(goal_handle)
        if status == "cancelled":
            self.logger.info("Goal was cancelled by client.")
            result_msg.success = False
            return result_msg
        
        result_msg.success = True
        return result_msg


    def feedback_loop(self, goal_handle: ServerGoalHandle):
        """Abstracted feedback loop where tolerance checks are conducted.

        Args:
            pose_stamped: target location
            goal_handle: passed in to enable feedback publishing
        """
        rate = self._node.create_rate(2)
        feedback = self.action_type.Feedback

        while self.current_idx <= self.path_len:

            if goal_handle.is_cancel_requested:
                self.logger.info("Goal was cancelled by client.")
                goal_handle.canceled()
                return "cancelled"
            
            feedback.feedback = self._json_ops.encode(self.current_idx)
            goal_handle.publish_feedback(feedback)
            rate.sleep()

        goal_handle.succeed()
        rate.destroy()
        return "done"


    def cancel_callback(self, goal_handle: ServerGoalHandle) -> CancelResponse:
        """Handles canceling of goal requests.

        Args:
            goal_handle: handle

        Returns:
            Cancel response as ACCEPT
        """

        return CancelResponse.ACCEPT

    def set_current_idx(self, idx):
        self.current_idx = idx



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
