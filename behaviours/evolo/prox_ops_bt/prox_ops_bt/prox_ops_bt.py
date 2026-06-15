#!/usr/bin/python3

import json
import math
from typing import Callable

import py_trees as pt
import rclpy
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from py_trees.composites import Selector as Fallback
from py_trees.composites import Sequence
from py_trees.trees import BehaviourTree
from evolo_msgs.msg import ProxOpsBackendStatus
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String

from smarc_action_base.bt_action_client_action import A_ActionClient, FuncToStatus
from smarc_action_base.gentler_action_server import GentlerActionServer
from smarc_action_base.smarc_action_base import ActionClientState


class ProxOpsBT:
    """Evolo prox-ops behaviour tree skeleton."""

    REQUIRED_GOAL_SECTIONS = {
        "inspect",
        "intercept",
        "loiter_patrol",
    }

    def __init__(self, node: Node):
        self._node = node
        self.act_target_inspect = A_ActionClient(node, "evolo_target_inspect",
                                                 "target_inspect")
        self.act_target_intercept = A_ActionClient(node,
                                                   "evolo_target_intercept",
                                                   "target_intercept")
        self.act_loiter_patrol = A_ActionClient(node, "evolo_loiter_patrol",
                                                "loiter_patrol")
        
        # This will mean that all action clients must be available from
        # startup since the BT will check whether they're alive or not.
        self._action_clients = [
            self.act_target_inspect,
            self.act_target_intercept,
            self.act_loiter_patrol,
        ]

        self._goal: dict = self._empty_goal()

        self._bt: BehaviourTree | None = None
        self._prev_tree_str = ""
        self._inspection_started_time_s: float | None = None
        self._patrol_started_time_s: float | None = None
        self._inspection_timeout_stop_reset_sent = False
        self._patrol_timeout_stop_reset_sent = False
        self._last_backend_status: ProxOpsBackendStatus | None = None

        self._status_pub = self._node.create_publisher(String,
                                                       "prox_ops_bt/status",
                                                       10)
        self._backend_command_pub = self._node.create_publisher(
            String, "backend/command", 10)

        self._node.declare_parameter("backend_status_max_age_s", 2.0)
        self._backend_status_max_age_s = (self._node.get_parameter(
            "backend_status_max_age_s").get_parameter_value().double_value)

        self._node.create_subscription(
            ProxOpsBackendStatus,
            "backend/status",
            self._backend_status_cb,
            10,
        )

        def publish_status():
            msg = String()
            msg.data = self._status_str
            self._status_pub.publish(msg)

        self._node.create_timer(1.0, publish_status)

        self._as = GentlerActionServer(
            node,
            "prox_ops_bt",
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency=5.0,
        )

    def log(self, msg: str) -> None:
        self._node.get_logger().info(msg)

    def _backend_status_cb(self, msg: ProxOpsBackendStatus) -> None:
        self._last_backend_status = msg

    @property
    def _now_s(self) -> float:
        now = self._node.get_clock().now().to_msg()
        return now.sec + now.nanosec * 1e-9

    def _backend_status_is_fresh(self) -> bool:
        status = self._last_backend_status
        if status is None:
            return False

        stamp = status.header.stamp
        if stamp.sec == 0 and stamp.nanosec == 0:
            return False

        age_s = self._now_s - (stamp.sec + stamp.nanosec * 1e-9)
        return 0.0 <= age_s <= self._backend_status_max_age_s

    def _publish_backend_command(self, command: str, reason: str) -> None:
        msg = String()
        msg.data = json.dumps({"command": command, "reason": reason})
        self._backend_command_pub.publish(msg)

    def _publish_backend_stop_reset_once(self, reason: str,
                                         flag_name: str) -> None:
        if getattr(self, flag_name):
            return

        self.log(f"Sending backend RESET and STOP: {reason}.")
        self._publish_backend_command("RESET", reason)
        self._publish_backend_command("STOP", reason)
        setattr(self, flag_name, True)

    def _reset_states(self) -> None:
        self._inspection_started_time_s = None
        self._patrol_started_time_s = None
        self._inspection_timeout_stop_reset_sent = False
        self._patrol_timeout_stop_reset_sent = False
        self._last_backend_status = None
        self._prev_tree_str = ""
        for ac in self._action_clients:
            ac.terminate(Status.INVALID)
        self.log("States reset")

    def _empty_goal(self) -> dict:
        return {
            "inspect": {},
            "intercept": {},
            "loiter_patrol": {},
        }

    def _unwrap_goal_request(self, goal_request: dict) -> dict:
        if not isinstance(goal_request, dict):
            raise ValueError("prox-ops goal must be a JSON object")

        if "json-params" not in goal_request:
            return goal_request

        params = goal_request["json-params"]
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "prox-ops goal json-params must contain valid JSON"
                ) from exc

        if not isinstance(params, dict):
            raise ValueError(
                "prox-ops goal json-params must be a JSON object or encoded JSON object"
            )

        return params

    def _parse_goal_request(self, goal_request: dict) -> dict:
        goal_request = self._unwrap_goal_request(goal_request)

        provided_sections = set(goal_request.keys())
        missing_sections = self.REQUIRED_GOAL_SECTIONS - provided_sections
        if missing_sections:
            raise ValueError(
                f"prox-ops goal missing required sections: {sorted(missing_sections)}"
            )

        unknown_sections = provided_sections - self.REQUIRED_GOAL_SECTIONS
        if unknown_sections:
            raise ValueError(
                f"prox-ops goal has unknown sections: {sorted(unknown_sections)}"
            )

        goal = self._empty_goal()
        for section in self.REQUIRED_GOAL_SECTIONS:
            section_goal = goal_request[section]
            if not isinstance(section_goal, dict):
                raise ValueError(
                    f"prox-ops goal section '{section}' must be a JSON object"
                )
            goal[section] = section_goal

        # TODO: Decide whether the intercept section should have an explicit
        # mode field once evolo_target_intercept needs one.
        return goal

    def _on_goal_received(self, goal_request: dict) -> bool:
        self.log(f"Received new prox-ops goal request: {goal_request}")
        self._reset_states()

        try:
            self._goal = self._parse_goal_request(goal_request)
        except Exception as exc:
            self.log(f"Rejecting prox-ops goal: {exc}")
            return False

        self.log(f"Accepted prox-ops goal: {self._goal}")
        return True

    def _on_cancel_received(self) -> bool:
        self.log("Received prox-ops goal cancel request.")
        self._reset_states()
        return True

    def _prepare_loop(self) -> None:
        # Reset states in BT and tell backend to reset and start.
        self._reset_states()
        self.log("Sending backend RESET/START from prox_ops_bt prepare_loop.")
        self._publish_backend_command("RESET", "prox_ops_bt started")
        self._publish_backend_command("START", "prox_ops_bt started")
        
        # Start patrol timer/counter.
        self._patrol_started_time_s = self._now_s

    @property
    def _status_str(self) -> str:
        tip = self._bt.tip() if self._bt is not None else None
        tip_str = "-" if tip is None else f"{tip.name}({tip.status}):{tip.feedback_message}"
        return f"Tip: {tip_str}"

    def _loop_inner(self) -> bool | None:
        if self._bt is None:
            self.log("Behaviour tree not set up, failing.")
            return False

        self._bt.tick()

        tree_str = pt.display.ascii_tree(self._bt.root, show_status=True)
        if tree_str != self._prev_tree_str:
            self.log("\n" + tree_str)
            self._prev_tree_str = tree_str

        # The only measure of success is if we have inspected the target long
        # enough.
        if self._inspection_timeout_reached():
            self.log("We have prox-ops'd.")
            self._reset_states()
            return True

        root_status = self._bt.root.status
        # FIXME: Will this fail prematurely? Should it only be a failure
        # if the patrol timeout is reached?
        if root_status == Status.FAILURE or not self._patrol_timeout_not_exceeded():
            self.log("We have failed to prox-ops.")
            self._reset_states()
            return False

        return None

    def _action_ready(self, action_client: A_ActionClient) -> bool:
        running_states = {
            ActionClientState.SENT,
            ActionClientState.ACCEPTED,
            ActionClientState.RUNNING,
            ActionClientState.CANCELLING,
        }
        if action_client.state in running_states | {ActionClientState.READY}:
            return True

        action_client.setup()
        return action_client.state == ActionClientState.READY

    def _set_goal(self, action_client: A_ActionClient, goal: dict,
                  name: str) -> bool:
        if not self._action_ready(action_client):
            self.log(
                f"{name} action server is not ready. State: {action_client.state}"
            )
            return False

        try:
            action_client.set_goal(json.dumps(goal))
            self.log(f"Set goal for {name}.")
            return True
        except Exception as exc:
            self.log(f"Failed to set goal for {name}: {exc}")
            return False

    def _set_goal_target_inspect(self) -> bool:
        return self._set_goal(
            self.act_target_inspect,
            self._goal.get("inspect", {}),
            "target inspect",
        )

    def _set_goal_target_intercept(self) -> bool:
        return self._set_goal(
            self.act_target_intercept,
            self._goal.get("intercept", {}),
            "target intercept",
        )

    def _set_goal_loiter_patrol(self) -> bool:
        return self._set_goal(
            self.act_loiter_patrol,
            self._goal.get("loiter_patrol", {}),
            "loiter patrol",
        )

    def _target_intercepted(self) -> bool:
        status = self._last_backend_status
        if status is None or not self._backend_status_is_fresh():
            return False

        return (status.target_intercepted
                or status.mode == ProxOpsBackendStatus.MODE_INSPECT)

    def _inspection_timeout_reached(self) -> bool:
        timeout_s = float(self._goal.get("inspect", {}).get("timeout_s", 0.0))
        if timeout_s <= 0.0 or self._inspection_started_time_s is None:
            return False

        if self._now_s - self._inspection_started_time_s < timeout_s:
            return False

        self._publish_backend_stop_reset_once(
            "inspection_timeout_exceeded",
            "_inspection_timeout_stop_reset_sent",
        )
        return True

    def _target_intercepted_and_info_fresh(self) -> bool:
        status = self._last_backend_status
        if status is None or not self._backend_status_is_fresh():
            return False
        
        if not (status.target_intercepted
                or status.mode == ProxOpsBackendStatus.MODE_INSPECT):
            return False

        target_info_fresh = (
            status.long_range_track_live
            or status.terminal_track_live) and not status.target_lost
        if not target_info_fresh:
            return False

        if self._inspection_started_time_s is None:
            self._inspection_started_time_s = self._now_s

        return True

    def _backend_converged_healthy_and_tracking(self) -> bool:
        status = self._last_backend_status
        if status is None or not self._backend_status_is_fresh():
            return False

        health_ok = status.health in (
            ProxOpsBackendStatus.HEALTH_OK,
            ProxOpsBackendStatus.HEALTH_DEGRADED,
        )

        converged = (status.long_range_track_converged or status.mode in (
            ProxOpsBackendStatus.MODE_LONG_RANGE_INTERCEPT,
            ProxOpsBackendStatus.MODE_FUSED_INTERCEPT,
            ProxOpsBackendStatus.MODE_TERMINAL_INTERCEPT,
        ))
        
        if health_ok and converged and status.plan_available and not status.target_lost:
            # We're in intercept mode now. Reset both inspection and patrol
            # timeouts.
            self._inspection_started_time_s = None
            self._patrol_started_time_s = None
            return True

        return False

    def _backend_converged_target_found_and_has_plan(self) -> bool:
        status = self._last_backend_status
        if status is None or not self._backend_status_is_fresh():
            return False

        converged = (status.long_range_track_converged or status.mode in (
            ProxOpsBackendStatus.MODE_LONG_RANGE_INTERCEPT,
            ProxOpsBackendStatus.MODE_FUSED_INTERCEPT,
            ProxOpsBackendStatus.MODE_TERMINAL_INTERCEPT,
        ))
        return converged and status.plan_available and not status.target_lost

    def _patrol_timeout_not_exceeded(self) -> bool:
        timeout_s = float(
            self._goal.get("loiter_patrol", {}).get("timeout_s", 0.0))
        if timeout_s <= 0.0:
            return True

        if self._patrol_started_time_s is None:
            self._patrol_started_time_s = self._now_s

        if self._now_s - self._patrol_started_time_s <= timeout_s:
            return True

        # If we got here it means that we've failed the prox-ops.
        self._publish_backend_stop_reset_once(
            "patrol_timeout_exceeded",
            "_patrol_timeout_stop_reset_sent",
        )
        return False

    def _post_pre_act(
        self,
        title: str,
        post_condition: Callable[[], bool],
        post_title: str,
        pre_condition: Callable[[], bool],
        pre_title: str,
        act: Behaviour,
    ) -> Fallback:
        subtree = Fallback(f"FB {title}", memory=False)
        subtree.add_child(FuncToStatus(post_title, post_condition))
        action_seq = Sequence(f"SQ Try <{act.name}>", memory=True)
        action_seq.add_child(FuncToStatus(pre_title, pre_condition))
        action_seq.add_child(act)
        subtree.add_child(action_seq)
        return subtree

    def setup(self) -> bool:
        self.log("Setting up prox-ops BT actions...")

        for ac in self._action_clients:
            ac.setup()
            if ac.state != ActionClientState.READY:
                self.log(f"{ac.name} failed to setup. State: {str(ac.state)}")
                return False

        do_inspection = Sequence(
            "SQ Do inspection",
            memory=True,
            children=[
                FuncToStatus("Set inspect goal",
                             self._set_goal_target_inspect),
                self.act_target_inspect,
            ],
        )

        inspect = self._post_pre_act(
            title="Inspect",
            post_condition=self._inspection_timeout_reached,
            post_title="Inspection timeout",
            pre_condition=self._target_intercepted_and_info_fresh,
            pre_title="Target still close and info is fresh",
            act=do_inspection,
        )

        do_intercept = Sequence(
            "SQ Do intercept",
            memory=True,
            children=[
                FuncToStatus("Set intercept goal",
                             self._set_goal_target_intercept),
                self.act_target_intercept,
            ],
        )

        intercept = self._post_pre_act(
            title="Intercept",
            post_condition=self._target_intercepted,
            post_title="Target intercepted",
            pre_condition=self._backend_converged_healthy_and_tracking,
            pre_title="Backend is consistent, healthy, and tracking the target",
            act=do_intercept,
        )

        do_loiter_patrol = Sequence(
            "SQ Do loiter / patrol",
            memory=True,
            children=[
                FuncToStatus("Set loiter / patrol goal",
                             self._set_goal_loiter_patrol),
                self.act_loiter_patrol,
            ],
        )

        loiter_patrol = self._post_pre_act(
            title="Lost target / patrol",
            post_condition=self._backend_converged_target_found_and_has_plan,
            post_title="Backend converged, has found the target, and has plan",
            pre_condition=self._patrol_timeout_not_exceeded,
            pre_title="Patrol timeout not exceeded",
            act=do_loiter_patrol,
        )

        # Root of the BT.
        root = Fallback(
            "FB Root",
            memory=False,
            children=[
                inspect,
                intercept,
                loiter_patrol,
            ],
        )

        self._bt = BehaviourTree(root)
        self.log("prox-ops BT setup complete.")
        return True

    def _give_feedback(self) -> str:
        return self._status_str


def main(args=None):
    rclpy.init(args=args)
    node = Node("prox_ops_bt_node")
    prox_ops_bt = ProxOpsBT(node)
    if not prox_ops_bt.setup():
        node.get_logger().error("Failed to setup prox_ops_bt, shutting down.")
        rclpy.shutdown()
        return

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()
