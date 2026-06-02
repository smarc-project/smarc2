#!/usr/bin/python3

import json

import py_trees as pt
import rclpy
from py_trees.common import Status
from py_trees.composites import Selector as Fallback
from py_trees.composites import Sequence
from py_trees.trees import BehaviourTree
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String

from smarc_action_base.bt_action_client_action import A_ActionClient, FuncToStatus
from smarc_action_base.gentler_action_server import GentlerActionServer
from smarc_action_base.smarc_action_base import ActionClientState


class ProxOpsBT:
    """Evolo prox-ops behaviour tree skeleton."""

    def __init__(self, node: Node):
        self._node = node
        self.act_target_intercept = A_ActionClient(
            node, "evolo_target_intercept", "target_intercept"
        )
        self._action_clients = [self.act_target_intercept]

        self._goal: dict = {
            "intercept": {},
            "safety": {},
            "lost_target": {},
        }
        self._bt: BehaviourTree | None = None
        self._prev_tree_str = ""

        status_pub = self._node.create_publisher(String, "prox_ops_bt/status", 10)

        def publish_status():
            msg = String()
            msg.data = self._status_str
            status_pub.publish(msg)

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

    def _reset_states(self) -> None:
        for ac in self._action_clients:
            ac.terminate(Status.INVALID)
        self.log("States reset")

    def _on_goal_received(self, goal_request: dict) -> bool:
        self.log(f"Received new prox-ops goal request: {goal_request}")
        self._reset_states()

        try:
            if not (goal_request.keys() >= self._goal.keys()):
                self.log("Goal request missing required fields, rejecting.")
                self.log(f"Missing fields: {self._goal.keys() - goal_request.keys()}")
                return False
        except Exception as exc:
            self.log(f"Exception while checking goal request fields: {exc}")
            return False

        self._goal = goal_request
        return True

    def _on_cancel_received(self) -> bool:
        self.log("Received prox-ops goal cancel request.")
        self._reset_states()
        return True

    def _prepare_loop(self) -> None:
        self._reset_states()

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

        root_status = self._bt.root.status
        if root_status == Status.SUCCESS:
            self.log("Prox-ops BT succeeded.")
            self._reset_states()
            return True

        if root_status == Status.FAILURE:
            self.log("Prox-ops BT failed.")
            self._reset_states()
            return False

        return None

    def _set_goal_target_intercept(self) -> bool:
        try:
            self.act_target_intercept.set_goal(json.dumps(self._goal["intercept"]))
            self.log("Set goal for target intercept.")
            return True
        except Exception as exc:
            self.log(f"Failed to set target intercept goal: {exc}")
            return False

    def setup(self) -> bool:
        self.log("Setting up prox-ops BT actions...")

        for ac in self._action_clients:
            ac.setup()
            if ac.state != ActionClientState.READY:
                self.log(f"{ac.name} failed to setup. State: {str(ac.state)}")
                return False

        target_intercept = Sequence(
            "SQ Target intercept",
            memory=True,
            children=[
                FuncToStatus("Set intercept goal", self._set_goal_target_intercept),
                self.act_target_intercept,
            ],
        )

        root = Fallback(
            "FB Root",
            memory=False,
            children=[
                target_intercept,
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
