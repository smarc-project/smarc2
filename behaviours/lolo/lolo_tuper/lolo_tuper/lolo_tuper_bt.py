#!/usr/bin/python3
"""LoLo TUPER: an action server whose execution is a behaviour tree.

Mirrors the alars_bt pattern: a single GentlerActionServer (BaseAction + JSON
goals) whose loop_inner ticks a py_trees BehaviourTree at a fixed rate.

Mission:
  1. GoToStart        - delegate to the external auv_depth_move_to action to
                        reach the start position at mission_depth (returns
                        immediately if already there).
  2. FollowSetpoint   - UKF-consistent COURSE control toward the live UKF
                        setpoint, holding depth + min-altitude, modulating RPM
                        with a PID/bang-bang law. Fails on excessive position
                        uncertainty; succeeds when the setpoint stops moving.
  3. MoveToLastSetpoint - settle on the last setpoint within arrival_tolerance.
  4. SurfaceAndReturn - delegate to auv_depth_move_to with target_depth=-1 to
                        surface and return to the start position.
"""

import json
import sys

import py_trees as pt
from py_trees.common import Status
from py_trees.composites import Sequence
from py_trees.trees import BehaviourTree

import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from std_msgs.msg import String

from smarc_action_base.bt_action_client_action import A_ActionClient, FuncToStatus
from smarc_action_base.gentler_action_server import GentlerActionServer
from smarc_action_base.smarc_action_base import ActionClientState

from virtual_lolo.lolo import Lolo

from lolo_tuper.follower_state import FollowerState
from lolo_tuper.tuper_behaviours import (
    ControlGains,
    FollowSetpoint,
    MoveToLastSetpoint,
    TuperGoal,
)


# Goal fields with sane defaults (filled in if omitted from the request).
GOAL_DEFAULTS = {
    "min_rpm": 400.0,
    "max_rpm": 700.0,
    "max_pos_uncertainty": 4.0,
}


class LoloTuperBT:
    def __init__(self, node: Node):
        self._node = node

        self._declare_params()

        self._follower_state = FollowerState(
            node,
            pose_topic=self._pose_topic,
            setpoint_topic=self._setpoint_topic,
            estimate_max_age=self._estimate_max_age,
        )

        self._vehicle = Lolo(node=node,
                             robot_name=self._robot_name,
                             limits_filename=self._limits_filename)

        # --- BT leaves (delegating phases) ----------------------------------
        # Two action-client behaviours that drive the external auv_depth_move_to
        # server: one for Phase 1 (GoToStart), one for Phase 4 (SurfaceAndReturn).
        # Two separate instances because a py_trees behaviour can only live at
        # one place in the tree. These get wired into the tree in setup().
        self._act_go_to_start = A_ActionClient(
            node, self._move_to_action_name, 'go_to_start')
        self._act_surface_return = A_ActionClient(
            node, self._move_to_action_name, 'surface_and_return')

        gains = ControlGains(
            kp_rpm=self._kp_rpm,
            ki_rpm=self._ki_rpm,
            kd_rpm=self._kd_rpm,
            integral_limit=self._integral_limit,
            heading_gate_deg=self._heading_gate_deg,
            uncertainty_deadband_k=self._uncertainty_deadband_k,
            stale_grace_period=self._stale_grace_period,
            control_period=1.0 / max(self._control_frequency, 1e-3),
        )

        # --- BT leaves (custom control phases) ------------------------------
        # Phase 2 and Phase 3 of the tree. These are the custom control-loop
        # behaviours (their per-tick logic lives in tuper_behaviours.py): they
        # steer LoLo via COURSE goals, gate on uncertainty, and decide when the
        # phase is SUCCESS/FAILURE/RUNNING. Wired into the tree in setup().
        self._follow = FollowSetpoint(
            "Follow setpoint", node, self._follower_state, self._vehicle,
            self._current_goal)
        self._follow.set_gains(gains)

        self._move_to_last = MoveToLastSetpoint(
            "Move to last setpoint", node, self._follower_state, self._vehicle,
            self._current_goal)
        self._move_to_last.set_gains(gains)

        self._goal_obj: TuperGoal | None = None
        self._bt: BehaviourTree | None = None
        self._prev_tree_str = ""

        # Required goal structure (presence-checked like alars).
        self._goal_template = {
            "start_position": {"latitude": None, "longitude": None},
            "initial_setpoint": {"latitude": None, "longitude": None},
            "mission_depth": None,
            "min_altitude": None,
            "setpoint_stop_tolerance": None,
            "setpoint_stop_period": None,
            "arrival_tolerance": None,
            "start_tolerance": None,
            "timeout": None,
        }

        status_pub = node.create_publisher(String, 'lolo_tuper/status', 10)

        def publish_status():
            msg = String()
            msg.data = self._status_str
            status_pub.publish(msg)
        node.create_timer(1.0, publish_status)

        self._as = GentlerActionServer(
            node,
            'lolo_tuper',
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency=self._control_frequency,
        )

    # ------------------------------------------------------------- params
    def _declare_params(self) -> None:
        node = self._node

        def gp(name, default):
            return node.declare_parameter(name, default).value

        self._robot_name = gp('robot_name', 'lolo')
        self._limits_filename = gp('limits_filename', '')
        self._control_frequency = float(gp('control_frequency', 10.0))
        self._estimate_max_age = float(gp('estimate_max_age', 5.0))
        self._stale_grace_period = float(gp('stale_grace_period', 10.0))
        self._pose_topic = gp('pose_topic', '/follower/ukf/pose')
        self._setpoint_topic = gp('setpoint_topic', '/follower/ukf/setpoint')
        self._move_to_action_name = gp('move_to_action_name', 'auv_depth_move_to')
        self._kp_rpm = float(gp('kp_rpm', 20.0))
        self._ki_rpm = float(gp('ki_rpm', 0.0))
        self._kd_rpm = float(gp('kd_rpm', 5.0))
        self._integral_limit = float(gp('integral_limit', 200.0))
        self._heading_gate_deg = float(gp('heading_gate_deg', 60.0))
        self._uncertainty_deadband_k = float(gp('uncertainty_deadband_k', 2.0))

    # ------------------------------------------------------------- helpers
    def log(self, msg: str) -> None:
        self._node.get_logger().info(msg)

    def _current_goal(self) -> TuperGoal | None:
        return self._goal_obj

    def _reset_states(self) -> None:
        if self._bt is not None:
            self._bt.root.stop(Status.INVALID)
        self._vehicle.reset_goal()

    # --------------------------------------------------------- goal handling
    def _validate_goal(self, req: dict) -> bool:
        if not isinstance(req, dict):
            self.log("Goal request is not a dict, rejecting.")
            return False
        missing = self._goal_template.keys() - req.keys()
        if missing:
            self.log(f"Goal request missing required fields: {missing}")
            return False
        for key in ("start_position", "initial_setpoint"):
            sub = req.get(key)
            if not isinstance(sub, dict) or not ({"latitude", "longitude"} <= sub.keys()):
                self.log(f"Goal field '{key}' must contain latitude and longitude.")
                return False
        return True

    def _parse_goal(self, req: dict) -> TuperGoal:
        g = dict(GOAL_DEFAULTS)
        g.update(req)
        return TuperGoal(
            start_lat=float(req["start_position"]["latitude"]),
            start_lon=float(req["start_position"]["longitude"]),
            initial_setpoint_lat=float(req["initial_setpoint"]["latitude"]),
            initial_setpoint_lon=float(req["initial_setpoint"]["longitude"]),
            mission_depth=float(g["mission_depth"]),
            min_altitude=float(g["min_altitude"]),
            min_rpm=float(g["min_rpm"]),
            max_rpm=float(g["max_rpm"]),
            max_pos_uncertainty=float(g["max_pos_uncertainty"]),
            setpoint_stop_tolerance=float(g["setpoint_stop_tolerance"]),
            setpoint_stop_period=float(g["setpoint_stop_period"]),
            arrival_tolerance=float(g["arrival_tolerance"]),
            start_tolerance=float(g["start_tolerance"]),
            timeout=float(g["timeout"]),
        )

    def _on_goal_received(self, goal_request: dict) -> bool:
        self.log(f"Received new goal request: {goal_request}")
        self._reset_states()

        try:
            if not self._validate_goal(goal_request):
                return False
            self._goal_obj = self._parse_goal(goal_request)
        except Exception as e:  # noqa: BLE001
            self.log(f"Exception while parsing goal request: {e}")
            return False

        # Make sure the stop-detector retains enough history for this mission.
        self._follower_state.set_stop_window_period(
            self._goal_obj.setpoint_stop_period + 5.0)

        self.log("Goal accepted.")
        return True

    def _on_cancel_received(self) -> bool:
        self.log("Received goal cancel request.")
        self._reset_states()
        return True

    def _prepare_loop(self) -> None:
        self._reset_states()

    # ------------------------------------------------ move_to goal serializers
    def _move_to_goal_json(self, lat: float, lon: float, target_depth: float,
                           rpm: float, tolerance: float) -> str:
        g = self._goal_obj
        return json.dumps({
            "waypoint": {
                "latitude": lat,
                "longitude": lon,
                "target_depth": target_depth,
                "min_altitude": g.min_altitude,
                "rpm": rpm,
                "timeout": g.timeout,
                "tolerance": tolerance,
            }
        })

    def _set_goal_go_to_start(self) -> bool:
        g = self._goal_obj
        if g is None:
            return False
        try:
            self._act_go_to_start.set_goal(self._move_to_goal_json(
                g.start_lat, g.start_lon, g.mission_depth, g.max_rpm,
                g.start_tolerance))
            return True
        except Exception as e:  # noqa: BLE001
            self.log(f"Failed to set go-to-start goal: {e}")
            return False

    def _set_goal_surface_return(self) -> bool:
        g = self._goal_obj
        if g is None:
            return False
        try:
            # target_depth = -1 -> stay on the surface for the return leg.
            self._act_surface_return.set_goal(self._move_to_goal_json(
                g.start_lat, g.start_lon, -1.0, g.max_rpm, g.start_tolerance))
            return True
        except Exception as e:  # noqa: BLE001
            self.log(f"Failed to set surface-return goal: {e}")
            return False

    # ------------------------------------------------------------- status
    @property
    def _status_str(self) -> str:
        tip = self._bt.tip() if self._bt is not None else None
        if tip is None:
            tip_str = "-"
        else:
            tip_str = f"{tip.name}({tip.status}):{tip.feedback_message}"
        fs = self._follower_state
        s = f"Tip: {tip_str}"
        s += "\nFollower state:"
        s += f"\n pose_fresh: {fs.pose_fresh}"
        unc = fs.uncertainty_semimajor
        s += f"\n uncertainty(semi-major): {unc:.2f}m" if unc is not None else "\n uncertainty: ???"
        s += f"\n setpoint_fresh: {fs.setpoint_fresh}"
        return s

    # ------------------------------------------------------------- main loop
    def _loop_inner(self) -> bool | None:
        # This is the BT "engine": GentlerActionServer calls _loop_inner once per
        # control cycle (control_frequency Hz) while a goal is active. Each call
        # ticks the whole tree once and maps the root status to the action result:
        #   RUNNING -> None (keep going), SUCCESS -> True, FAILURE -> False.
        if self._bt is None:
            self.log("Behaviour tree not set up, failing.")
            return False

        # One tick = one traversal of the tree (GoToStart -> Follow -> ...).
        self._bt.tick()

        tree_str = pt.display.ascii_tree(self._bt.root, show_status=True)
        if tree_str != self._prev_tree_str:
            self.log("\n" + tree_str)
            self._prev_tree_str = tree_str

        status = self._bt.root.status
        if status == Status.SUCCESS:
            self.log("TUPER mission complete.")
            self._reset_states()
            return True
        if status == Status.FAILURE:
            self.log("TUPER mission failed.")
            self._reset_states()
            return False
        return None

    def _give_feedback(self) -> str:
        return self._status_str

    # ------------------------------------------------------------- setup
    def setup(self) -> bool:
        self.log("Setting up TUPER action clients...")
        for ac in (self._act_go_to_start, self._act_surface_return):
            ac.setup()
            if ac.state != ActionClientState.READY:
                self.log(f"{ac.name} failed to setup! State: {ac.state}")
                return False
        self.log("Action clients ready.")

        # =====================================================================
        # THE BEHAVIOUR TREE (this is the structure drawn in the plan diagram).
        #
        #   SQ Tuper Mission (Sequence, memory=True)   <- runs the 4 phases in
        #   ├── SQ GoToStart        (Sequence)            order; any FAILURE
        #   │   ├── set move_to goal (FuncToStatus)        aborts the whole task
        #   │   └── auv_depth_move_to (A_ActionClient)
        #   ├── Follow setpoint      (FollowSetpoint)   <- custom control loop
        #   ├── Move to last setpoint(MoveToLastSetpoint)<- custom control loop
        #   └── SQ SurfaceAndReturn (Sequence)
        #       ├── set move_to goal (FuncToStatus)
        #       └── auv_depth_move_to (A_ActionClient)
        #
        # memory=True means each Sequence remembers which child is RUNNING and
        # resumes there next tick, instead of re-evaluating from the start.
        # =====================================================================

        # --- Phase 1: GoToStart -> delegate to the external auv_depth_move_to.
        # First set the goal JSON, then run the action client behaviour.
        go_to_start = Sequence("SQ GoToStart", memory=True, children=[
            FuncToStatus("Set go-to-start goal", self._set_goal_go_to_start),
            self._act_go_to_start,
        ])

        # --- Phase 4: SurfaceAndReturn -> auv_depth_move_to with target_depth=-1.
        surface_and_return = Sequence("SQ SurfaceAndReturn", memory=True, children=[
            FuncToStatus("Set surface-return goal", self._set_goal_surface_return),
            self._act_surface_return,
        ])

        # --- Root: the 4 mission phases in order. Phases 2 (self._follow) and 3
        # (self._move_to_last) are the custom control-loop behaviours built in
        # __init__; see tuper_behaviours.py for their tick logic.
        root = Sequence("SQ Tuper Mission", memory=True, children=[
            go_to_start,          # Phase 1
            self._follow,         # Phase 2: FollowSetpoint
            self._move_to_last,   # Phase 3: MoveToLastSetpoint
            surface_and_return,   # Phase 4
        ])

        self._bt = BehaviourTree(root)
        self.log("Behaviour tree built.")
        return True


def main():
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("lolo_tuper_node")
    tuper = LoloTuperBT(node)

    if not tuper.setup():
        node.get_logger().error("Failed to setup lolo_tuper, shutting down.")
        rclpy.shutdown()
        return

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    rclpy.spin(node, executor=executor)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
