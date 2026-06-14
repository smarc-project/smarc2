#!/usr/bin/python3
"""LoLo TUPER: an action server whose execution is a behaviour tree.

Mirrors the alars_bt pattern: a single GentlerActionServer (BaseAction + JSON
goals) whose loop_inner ticks a py_trees BehaviourTree at a fixed rate.

Mission:
  1. GoToStart        - delegate to the external auv_depth_move_to action to
                                                reach the start position at the surface (returns
                                                immediately if already there).
  2. FollowSetpoint   - UKF-consistent COURSE control toward the live UKF
                        setpoint, holding depth + min-altitude, modulating RPM
                        with a PID/bang-bang law. Fails when the estimate
                        diverges from truth (measured delta_pos); succeeds when
                        the setpoint stops moving.
  3. MoveToLastSetpoint - settle on the last setpoint within final_arrival_tolerance.
  4. SurfaceAndReturn - delegate to auv_depth_move_to with target_depth=-1 to
                        surface and return to the start position.
"""

import dataclasses
import json
import sys

import py_trees as pt
from py_trees.common import Status
from py_trees.composites import Sequence
from py_trees.trees import BehaviourTree

import rclpy
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile

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
    "max_delta_pos": 5.0,
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
            odom_topic=self._odom_topic,
            latlon_topic=self._latlon_topic,
            delta_pos_topic=self._delta_pos_topic,
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
            rpm_idle=self._rpm_idle,
            rpm_per_mps=self._rpm_per_mps,
            kp_pos=self._kp_pos,
            ki_speed=self._ki_speed,
            speed_trim_limit=self._speed_trim_limit,
            hold_rpm=self._hold_rpm,
            heading_gate_deg=self._heading_gate_deg,
            stale_grace_period=self._stale_grace_period,
            submersion_min_depth=self._submersion_min_depth,
            dive_depth_tolerance=self._dive_depth_tolerance,
            dive_warn_period=self._dive_warn_period,
            leader_speed_window=self._leader_speed_window,
            control_period=1.0 / max(self._control_frequency, 1e-3),
        )

        # Shared telemetry dict: the control behaviours write into it each tick,
        # and the node publishes it as structured JSON (see _loop_inner).
        self._telemetry: dict = {}

        # --- BT leaves (custom control phases) ------------------------------
        # Phase 2 and Phase 3 of the tree. These are the custom control-loop
        # behaviours (their per-tick logic lives in tuper_behaviours.py): they
        # steer LoLo via COURSE goals, gate on estimate divergence, and decide
        # when the phase is SUCCESS/FAILURE/RUNNING. Wired into the tree in setup().
        self._follow = FollowSetpoint(
            "Follow setpoint", node, self._follower_state, self._vehicle,
            self._current_goal, telemetry=self._telemetry)
        self._follow.set_gains(gains)

        self._move_to_last = MoveToLastSetpoint(
            "Move to last setpoint", node, self._follower_state, self._vehicle,
            self._current_goal, telemetry=self._telemetry)
        self._move_to_last.set_gains(gains)

        self._goal_obj: TuperGoal | None = None
        self._bt: BehaviourTree | None = None
        self._prev_tree_str = ""

        # Whole-mission timer. The BT owns the authoritative clock: it fails the
        # task when the budget is exhausted, and hands only the *remaining* time
        # to the delegated move_to legs so they cannot outlive the mission.
        self._mission_start_time: float | None = None
        self._mission_timeout: float | None = None

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

        # Structured, machine-parseable telemetry at the control rate (so a bag
        # captures the follow loop without lossy regex on the human status).
        self._telemetry_pub = node.create_publisher(
            String, 'lolo_tuper/telemetry', 10)

        # Latched (transient-local) per-run goal+gains, so every recorded bag
        # self-documents the parameters that were actually used.
        latched_qos = QoSProfile(
            depth=1,
            history=HistoryPolicy.KEEP_LAST,
            durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self._goal_params_pub = node.create_publisher(
            String, 'lolo_tuper/goal_params', latched_qos)
        self._active_gains = gains

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
        # Measured estimate-vs-truth divergence (std_msgs/Float32). The follow
        # loop fails the task when this exceeds the goal's max_delta_pos.
        self._delta_pos_topic = gp('delta_pos_topic', '/follower/ukf/delta_pos')
        # Onboard nav (relative -> resolved in the robot namespace) used to
        # bootstrap toward the initial_setpoint before the UKF is live.
        self._odom_topic = gp('odom_topic', 'smarc/odom')
        self._latlon_topic = gp('latlon_topic', 'smarc/latlon')
        self._move_to_action_name = gp('move_to_action_name', 'auv_depth_move_to')

        # --- Velocity-matching follow loop (node-level tuning) ---------------
        self._rpm_idle = float(gp('rpm_idle', 0.0))
        self._rpm_per_mps = float(gp('rpm_per_mps', 530.0))
        self._kp_pos = float(gp('kp_pos', 0.15))
        self._ki_speed = float(gp('ki_speed', 20.0))
        self._speed_trim_limit = float(gp('speed_trim_limit', 150.0))
        self._hold_rpm = float(gp('hold_rpm', 400.0))
        self._heading_gate_deg = float(gp('heading_gate_deg', 60.0))
        self._leader_speed_window = float(gp('leader_speed_window', 5.0))

        # --- Dive-floor (node-level depth thresholds) ------------------------
        self._submersion_min_depth = float(gp('submersion_min_depth', 0.5))
        self._dive_depth_tolerance = float(gp('dive_depth_tolerance', 1.5))
        self._dive_warn_period = float(gp('dive_warn_period', 20.0))

        # --- Goal-JSON overridable defaults (node fallback) -----------------
        # Operators may override these per-mission in the action goal JSON;
        # these node params are the fallback when a field is omitted. Follow
        # speed itself is bounded by the goal's min_rpm / max_rpm, not a speed.
        self._standoff_distance = float(gp('standoff_distance', 5.0))
        self._final_arrival_tolerance = float(gp('final_arrival_tolerance', 10.0))
        self._dive_entry_rpm = float(gp('dive_entry_rpm', 550.0))
        # Leaders are "done" only when the fitted setpoint speed drops below
        # this (m/s) - set well under the leaders' cruise so a slow corner does
        # not read as a stop. Goal-JSON overridable.
        self._setpoint_stop_speed = float(gp('setpoint_stop_speed', 0.1))

    # ------------------------------------------------------------- helpers
    def log(self, msg: str) -> None:
        self._node.get_logger().info(msg)

    def _current_goal(self) -> TuperGoal | None:
        return self._goal_obj

    @property
    def _now(self) -> float:
        return self._node.get_clock().now().nanoseconds * 1e-9

    def _mission_elapsed(self) -> float:
        if self._mission_start_time is None:
            return 0.0
        return self._now - self._mission_start_time

    def _mission_remaining(self) -> float:
        """Seconds left in the WHOLE-mission budget (goal.timeout)."""
        if self._mission_timeout is None:
            return float('inf')
        return self._mission_timeout - self._mission_elapsed()

    def _reset_states(self) -> None:
        if self._bt is not None:
            self._bt.root.stop(Status.INVALID)
        self._vehicle.reset_goal()
        # Drop any UKF estimates cached from a previous mission so a stale pose
        # cannot leak into this run's control loop.
        self._follower_state.reset()

    # --------------------------------------------------------- goal handling
    def _unwrap_goal(self, goal_request: dict) -> dict:
        """Unwrap the WARA-PS custom-task envelope if present.

        The GUI / MQTT bridge sends the goal as
        {"action-name": "...", "json-params": "<json string or dict>"}.
        A direct `ros2 action send_goal` sends the raw mission dict instead;
        both are accepted.
        """
        if isinstance(goal_request, dict) and "json-params" in goal_request:
            jp = goal_request["json-params"]
            return json.loads(jp) if isinstance(jp, str) else jp
        return goal_request

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
            max_delta_pos=float(g["max_delta_pos"]),
            setpoint_stop_tolerance=float(g["setpoint_stop_tolerance"]),
            setpoint_stop_period=float(g["setpoint_stop_period"]),
            setpoint_stop_speed=float(req.get(
                "setpoint_stop_speed", self._setpoint_stop_speed)),
            arrival_tolerance=float(g["arrival_tolerance"]),
            final_arrival_tolerance=float(req.get(
                "final_arrival_tolerance", self._final_arrival_tolerance)),
            start_tolerance=float(g["start_tolerance"]),
            timeout=float(g["timeout"]),
            # Optional control knobs: goal JSON value > node param fallback.
            standoff_distance=float(req.get(
                "standoff_distance", self._standoff_distance)),
            dive_entry_rpm=float(req.get(
                "dive_entry_rpm", self._dive_entry_rpm)),
        )

    def _on_goal_received(self, goal_request: dict) -> bool:
        self.log(f"Received new goal request: {goal_request}")
        self._reset_states()

        try:
            req = self._unwrap_goal(goal_request)
            if not self._validate_goal(req):
                return False
            self._goal_obj = self._parse_goal(req)
        except Exception as e:  # noqa: BLE001
            self.log(f"Exception while parsing goal request: {e}")
            return False

        # Make sure the stop-detector retains enough history for this mission.
        self._follower_state.set_stop_window_period(
            self._goal_obj.setpoint_stop_period + 5.0)

        self._publish_goal_params()
        self.log("Goal accepted.")
        return True

    def _publish_goal_params(self) -> None:
        """Latch the resolved per-run goal + active gains so bags self-document."""
        g = self._goal_obj
        if g is None:
            return
        payload = {
            "goal": dataclasses.asdict(g),
            "gains": dataclasses.asdict(self._active_gains),
        }
        msg = String()
        msg.data = json.dumps(payload)
        self._goal_params_pub.publish(msg)

    def _on_cancel_received(self) -> bool:
        self.log("Received goal cancel request.")
        self._reset_states()
        return True

    def _prepare_loop(self) -> None:
        self._reset_states()
        # Start the whole-mission clock once, at the moment execution begins.
        self._mission_start_time = self._now
        self._mission_timeout = (
            self._goal_obj.timeout if self._goal_obj is not None else None)
        if self._mission_timeout is not None:
            self.log(f"Mission clock started: budget {self._mission_timeout:.0f}s.")

    # ------------------------------------------------ move_to goal serializers
    def _move_to_goal_json(self, lat: float, lon: float, target_depth: float,
                           rpm: float, tolerance: float) -> str:
        g = self._goal_obj
        # Hand the leg only the time the mission has left, so a delegated move_to
        # can never overrun the whole-mission budget (the bug behind pass-1's
        # return-leg timeout). Floored at a small positive value; if the budget
        # is genuinely spent, _loop_inner fails the mission on the next tick.
        leg_timeout = max(round(self._mission_remaining(), 1), 1.0)
        return json.dumps({
            "waypoint": {
                "latitude": lat,
                "longitude": lon,
                "target_depth": target_depth,
                "min_altitude": g.min_altitude,
                "rpm": rpm,
                "timeout": leg_timeout,
                "tolerance": tolerance,
            }
        })

    def _set_goal_go_to_start(self) -> bool:
        g = self._goal_obj
        if g is None:
            return False
        try:
            self._act_go_to_start.set_goal(self._move_to_goal_json(
                g.start_lat, g.start_lon, -1.0, g.max_rpm,
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
        dpos = fs.delta_pos
        s += f"\n delta_pos: {dpos:.2f}m" if dpos is not None else "\n delta_pos: ??? (no truth)"
        s += f"\n setpoint_fresh: {fs.setpoint_fresh}"
        if self._mission_timeout is not None:
            s += (f"\n mission: {self._mission_elapsed():.0f}s / "
                  f"{self._mission_timeout:.0f}s "
                  f"(remaining {self._mission_remaining():.0f}s)")
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

        # Whole-mission timeout: the BT is the authoritative timer. Fail the task
        # as soon as the budget is exhausted, regardless of which phase is active.
        if (self._mission_timeout is not None
                and self._mission_elapsed() >= self._mission_timeout):
            self.log(f"TUPER mission timed out after {self._mission_elapsed():.0f}s "
                     f"(budget {self._mission_timeout:.0f}s).")
            self._publish_telemetry()
            self._reset_states()
            return False

        # One tick = one traversal of the tree (GoToStart -> Follow -> ...).
        self._bt.tick()
        self._publish_telemetry()

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

    def _publish_telemetry(self) -> None:
        """Publish the shared control telemetry dict as JSON (control rate)."""
        tip = self._bt.tip() if self._bt is not None else None
        data = dict(self._telemetry)
        data["t"] = self._node.get_clock().now().nanoseconds * 1e-9
        data["tip"] = tip.name if tip is not None else "-"
        data["tip_status"] = str(tip.status) if tip is not None else "-"
        data["mission_elapsed"] = round(self._mission_elapsed(), 1)
        rem = self._mission_remaining()
        data["mission_remaining"] = round(rem, 1) if rem != float('inf') else None
        msg = String()
        msg.data = json.dumps(data)
        self._telemetry_pub.publish(msg)

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
    try:
        rclpy.spin(node, executor=executor)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
