#!/usr/bin/python3

import time

import numpy as np
from geometry_msgs.msg import Pose, PoseStamped
from nav_msgs.msg import Odometry
from scipy.interpolate import CubicSpline, PchipInterpolator
from scipy.optimize import minimize_scalar
from scipy.spatial.transform import Rotation as R
from smarc_control_msgs.msg import ControlInput
from smarc_modelling.control.control import *
from smarc_modelling.vehicles.SAM_casadi import SAM_casadi

from sam_diving_controller.controllers.DiveControllerInterface import (
    DiveControllerInterface,
)
from sam_diving_controller.IDivePub import ActuatorStates, MissionStates


class DiveControllerMPC(DiveControllerInterface):
    def __init__(
        self, node, dive_pub, dive_sub, param, ref_is_trajectory=False, rate=0.1
    ):

        self._node = node
        self._dive_sub = dive_sub
        self._dive_pub = dive_pub
        self.param = param
        self._dt = rate

        super().__init__(
            self._node, self._dive_pub, self._dive_sub, self.param, self._dt
        )

        self._current_state = None
        self._current_state_in_mocap = None
        self._current_control = None
        self._ref = None
        self._input = None
        self._control_ref = None
        self.waypoint = None

        self.pred_mpc = []

        # Declare counter
        self.traj_len = 0
        self.traj_index = 0

        # Variables for the actuator state estimators where we don't get feedback
        self.a_hat_stern = 0.0
        self.a_hat_rudder = 0.0
        self.rpm_hat_1 = 0.0
        self.rpm_hat_2 = 0.0
        
        # Total speed (norm of u,v,w) below which the last waypoint is
        # declared reached and the action server is allowed to signal COMPLETED.
        self._vel_stop_threshold = 0.15  # m/s (SAM decelerates through drag only; 0.1 takes too long)

        # Position tolerance for completion detection at the final waypoint.
        self._final_pos_tolerance = 1.0  # m (relaxed: real vehicle can't stop on a dime)

        # Debounce counter for COMPLETED detection.  All stopping conditions must be
        # satisfied for this many consecutive control steps before the action is
        # declared COMPLETED.
        self._completion_debounce_required = 3   # steps (~0.3 s at 10 Hz)
        self._completion_debounce_count = 0

        # Extract the CasADi model
        sam = SAM_casadi(dt=self._dt)

        # Flag if you want to rebuild the OCP or not (if changes has been made to the MPC)
        self._node.declare_parameter("build_ocp", False)
        self.build_ocp = self._node.get_parameter(
            "build_ocp"
        ).get_parameter_value().bool_value
        build = self.build_ocp

        # create nmpc object for the OCP
        self.N_horizon = 30 #30# 40 #30  # Prediction horizon
        self.mpc_rate = 0.1
        self.nmpc = NMPC(sam, self.mpc_rate, self.N_horizon, update_solver_settings=build)
        self.nx = self.nmpc.nx  # State vector length + control vector
        self.nu = self.nmpc.nu  # Control derivative vector length
        self.simU = np.zeros(self.nu)

        self.wp_array = np.zeros(self.nx + self.nu)

        self.ref = np.zeros((self.N_horizon, (self.nx + self.nu)))

        # Goal position [x, y, z] of the final trajectory waypoint.
        # Appended to every parameter vector sent to the OCP solver so the
        # braking/speed-funnel constraint can compute dist-to-goal at each stage.
        self._goal_pos = np.zeros(3)

        # ---- MPCC progress state --------------------------------------------------
        self.theta = 0.0             # current arc-length progress along the path
        self.v_theta = 0.1           # current velocity along the path (seeded > 0 so the
        self.delta_v_theta = 0.0     #   solver sees theta advancing from the first solve)
        self.theta_total = 0.0       # total arc-length of the loaded trajectory
        self.arc_lengths = None      # cumulative arc-length at each waypoint
        self.path_t_hat = np.zeros((self.N_horizon, 3))    # tangent per stage
        self.path_theta_hat = np.zeros(self.N_horizon)     # linearization point per stage
        self._v_target = 0.2         # progress speed target for yref (m/s)
        self._v_theta_prev = 0.0     # v_theta from previous solve (for manual propagation)
        self._depth_locked = False   # armed once z crosses depth_lock_threshold
        self._wall_locked = False    # armed once x crosses wall_lock_threshold

        # Cubic spline representation of the path (built in _compute_arc_lengths)
        self._spl_x = None           # CubicSpline: arc_length -> x
        self._spl_y = None           # PchipInterpolator: arc_length -> y (monotone-preserving)
        self._spl_z = None           # CubicSpline: arc_length -> z
        
        # Spline evaluation
        self.spl_eval_x = None
        self.spl_eval_y = None
        self.spl_eval_z = None
        self.n_eval = 100

        # Run the MPC setup
        self.ocp_solver, self.integrator = self.nmpc.setup()


        # NOTE: This needs to happen in the update function with some check
        # before proceeding. Otherwise, you don't get the right data from the
        # dive sub node, because it's not yet spinning and thus doesn't get the
        # topics yet.
        self._initialized = False
        self._prev_commanding = False

        self.ref_is_traj = ref_is_trajectory

        # Runtime sign calibration for model-vs-robot command conventions.
        # False = MPC rudder sign matches robot (positive rudder => starboard, per SAM_casadi NED/FRD).
        # Set to True only if the vehicle turns port when it should turn starboard.
        self._node.declare_parameter("flip_stern_command", False)
        self._node.declare_parameter("flip_rudder_command", False)
        self.flip_stern_command = self._node.get_parameter(
            "flip_stern_command"
        ).get_parameter_value().bool_value
        self.flip_rudder_command = self._node.get_parameter(
            "flip_rudder_command"
        ).get_parameter_value().bool_value
        # Keep state and reference in the same frame convention.
        # NOTE: Set to False if trajectory is already generated in FRD/NED convention!
        # Your create_turbo_turn_path.py uses USE_NED_CONVENTION=True, so it's already FRD.
        self.convert_trajectory_to_frd = False

        self._loginfo("Dive Controller created")

        self._acados_status = {
            0: "ACADOS_SUCCESS",
            1: "ACADOS_NAN_DETECTED",
            2: "ACADOS_MAXITER",
            3: "ACADOS_MINSTEP",
            4: "ACADOS_QP_FAILURE",
            5: "ACADOS_READY",
            6: "ACADOS_UNBOUNDED",
        }

        # Set True (or use param debug_print_ref_state) to log reference vs state (e.g. port/starboard debug)
        self._node.declare_parameter("debug_print_ref_state", False)
        self._print_ref_state_debug = self._node.get_parameter(
            "debug_print_ref_state"
        ).get_parameter_value().bool_value
        self._print_ref_state_throttle = 0


    def update(self):
        """
        This is where all the magic happens.
        """
        t_loop_start = time.time()
        mission_state = self._dive_sub.get_mission_state()

        has_ref = self.get_reference()
        commanding = (mission_state == MissionStates.RUNNING) and has_ref

        # Marker for mission start and end
        if commanding != self._prev_commanding:
            self._dive_pub.publish_mission_event(commanding, mission_state)
            self._prev_commanding = commanding

        if mission_state == MissionStates.RECEIVED:
            self._loginfo_once("Mission Received")
            self._set_actuators_neutral()
            return

        if mission_state == MissionStates.COMPLETED:
            self._loginfo_once("Mission Complete")
            self._set_actuators_neutral()
            return

        if mission_state == MissionStates.CANCELLED:
            self._loginfo_once("Mission Cancelled")
            self._set_actuators_neutral()
            return

        # Engage actuators in case they were off before.
        self._dive_pub.set_actuator_states(ActuatorStates.ENGAGED, "DC")

        if not has_ref:
            return

        convert_state = True
        self._current_state_in_mocap = self._dive_sub.get_states_in_mocap()

        if self._current_state_in_mocap is None:
            self._loginfo(f"No state available yet.")
            return

        self._current_state = self.convert_flu_to_frd(
            self._current_state_in_mocap, convert_state
        )
        self._current_control = self._dive_sub.get_control_input()

        if not self._initialized:
            self.initialize_mpc()

        x_current = self.get_state_array(
            self._current_state,
            self._current_control,
            is_init_state=self._initialized,
            is_trajectory=self.ref_is_traj,
        )
        start_ref_time = time.time()
        self.get_current_ref_array()
        end_ref_time = time.time()
        np.set_printoptions(precision=3)
        self._loginfo(f"x_current: {x_current[:3]}")

        # ---- NaN guard ----
        if np.any(np.isnan(x_current)):
            nan_idx = np.where(np.isnan(x_current))[0]
            self._logwarn(f"NaN in x_current at indices {nan_idx} — skipping solve")
            self._set_actuators_neutral()
            return

        # ---- Depth lock: prevent resurfacing once submerged ----
        z_now = x_current[2]
        if not self._depth_locked and z_now >= self.nmpc.depth_lock_threshold:
            self._depth_locked = True
            self._loginfo(
                f"Depth lock armed at z={z_now:.2f} m "
                f"(threshold={self.nmpc.depth_lock_threshold}, "
                f"min={self.nmpc.depth_lock_min})"
            )
        if self._depth_locked:
            idx = self.nmpc.IDX_Z_BOX
            for k in range(1, self.N_horizon + 1):
                lbx = self.ocp_solver.constraints_get(k, "lbx")
                if lbx[idx] < self.nmpc.depth_lock_min:
                    lbx[idx] = self.nmpc.depth_lock_min
                    self.ocp_solver.constraints_set(k, "lbx", lbx)

        # ---- Wall lock: prevent drifting back into the wall ----
        x_now = x_current[0]
        if not self._wall_locked and x_now >= self.nmpc.wall_lock_threshold:
            self._wall_locked = True
            self._loginfo(
                f"Wall lock armed at x={x_now:.2f} m "
                f"(threshold={self.nmpc.wall_lock_threshold}, "
                f"min={self.nmpc.wall_lock_min})"
            )
        if self._wall_locked:
            idx = self.nmpc.IDX_X_BOX
            for k in range(1, self.N_horizon + 1):
                lbx = self.ocp_solver.constraints_get(k, "lbx")
                if lbx[idx] < self.nmpc.wall_lock_min:
                    lbx[idx] = self.nmpc.wall_lock_min
                    self.ocp_solver.constraints_set(k, "lbx", lbx)

        # ---- Build MPCC parameter vector and yref per stage ----
        # v_theta target ramps to zero over the last decel_dist metres of
        # arc length so the solver plans a smooth deceleration over many
        # stages instead of seeing "go fast" everywhere and "stop" only at
        # the terminal.
        decel_dist = 2.5  # [m] arc-length before end to start ramping v_theta down
        for stage in range(self.N_horizon):
            ref_row = self.ref[stage, :] if stage < self.ref.shape[0] else self.ref[-1, :]
            p = np.r_[ref_row, self._goal_pos,
                       self.path_t_hat[stage], self.path_theta_hat[stage]]
            self.ocp_solver.set(stage, "p", p)

            yref_k = np.zeros(self.nmpc.n_stage_cost)
            if self.ref_is_traj and self.theta_total > 0:
                remaining_k = max(self.theta_total - self.path_theta_hat[stage], 0.0)
                if remaining_k < decel_dist:
                    yref_k[4] = self._v_target * (remaining_k / decel_dist)
                else:
                    yref_k[4] = self._v_target
            else:
                yref_k[4] = self._v_target
            self.ocp_solver.cost_set(stage, "yref", yref_k)

        terminal_ref = getattr(self, '_terminal_ref', self.ref[-1, :])
        p_terminal = np.r_[terminal_ref, self._goal_pos,
                           self.path_t_hat[-1], self.path_theta_hat[-1]]
        self.ocp_solver.set(self.N_horizon, "p", p_terminal)
        yref_e = np.zeros(self.nmpc.n_terminal_cost)
        self.ocp_solver.cost_set(self.N_horizon, "yref", yref_e)

        # Set current state
        self.ocp_solver.set(0, "lbx", x_current)
        self.ocp_solver.set(0, "ubx", x_current)

        start_time = time.time()
        status = self.ocp_solver.solve()
        end_time = time.time()

        # ---- Recovery on solver failure ----
        if status != 0:
            stat_name = self._acados_status.get(status, f"UNKNOWN({status})")
            qnorm = np.linalg.norm(x_current[3:7])
            self._logwarn(
                f"Solver failed: {stat_name} | "
                f"pos=({x_current[0]:.2f},{x_current[1]:.2f},{x_current[2]:.2f}) "
                f"vel=({x_current[7]:.3f},{x_current[8]:.3f},{x_current[9]:.3f}) "
                f"qnorm={qnorm:.4f} "
                f"lcg={x_current[14]:.1f} vbs={x_current[13]:.1f} "
                f"rpm=({x_current[17]:.0f},{x_current[18]:.0f}) "
                f"stern={x_current[15]:.4f} rudder={x_current[16]:.4f} "
                f"theta={self.theta:.2f}/{self.theta_total:.2f} "
                f"v_theta={self.v_theta:.3f}"
            )
            # Tier 1 — light recovery: just run more SQP iterations on the
            # existing iterate.  The previous solution is usually close; it
            # just needs 1-2 more iterations to converge.  This preserves
            # warm-start quality → much better control than a full reset.
            for attempt in range(3):
                status = self.ocp_solver.solve()
                if status == 0:
                    self._loginfo(f"Light recovery after {attempt+1} extra iterations")
                    break

            # Tier 2 — heavy recovery: reset everything and re-seed.
            if status != 0:
                self._logwarn("Light recovery failed, performing full reset")
                try:
                    self.ocp_solver.reset()
                except Exception:
                    pass
                for stg in range(self.N_horizon + 1):
                    self.ocp_solver.set(stg, "x", x_current)
                for stg in range(self.N_horizon):
                    self.ocp_solver.set(stg, "u", np.zeros(self.nu))
                self.ocp_solver.set(0, "lbx", x_current)
                self.ocp_solver.set(0, "ubx", x_current)
                for stg in range(self.N_horizon):
                    ref_row = self.ref[stg, :] if stg < self.ref.shape[0] else self.ref[-1, :]
                    p = np.r_[ref_row, self._goal_pos,
                               self.path_t_hat[stg], self.path_theta_hat[stg]]
                    self.ocp_solver.set(stg, "p", p)
                self.ocp_solver.set(self.N_horizon, "p", p_terminal)
                for attempt in range(5):
                    status = self.ocp_solver.solve()
                    if status == 0:
                        self._loginfo(f"Heavy recovery after {attempt+1} re-solves")
                        break
            end_time = time.time()

        # simulate system
        self.simU = self.ocp_solver.get(0, "u")
        simX = self.ocp_solver.get(0, "x")

        self.pred_mpc = []
        for j in range(self.N_horizon + 1):
            self.pred_mpc.append(self.ocp_solver.get(j, "x"))

        mpc_solution = self.integrator.simulate(x=x_current, u=self.simU)

        if mpc_solution is None:
            self._set_actuators_neutral()
        elif status != 0:
            self._logwarn("Recovery failed — setting actuators neutral")
            self._set_actuators_neutral()
        else:
            self.set_publishers(mpc_solution)
            # Optional: log reference vs state and actual rudder/stern command (after solve)
            if self._print_ref_state_debug:
                self._print_ref_state_throttle += 1
                if self._print_ref_state_throttle >= 10:
                    self._print_ref_state_throttle = 0
                    self.print_reference_vs_state_debug(x_current, mpc_solution=mpc_solution)

        # Actuator state estimators: integrate commanded rates to track actuator
        # states. All rates are in model convention; sign is applied in
        # _map_actuator_commands / _rpm1_sign() at publishing time.
        u_k = self.ocp_solver.get(0, "u")
        self.a_hat_stern = np.clip(self.a_hat_stern + self._dt * u_k[2], -0.122173, 0.122173)
        self.a_hat_rudder = np.clip(self.a_hat_rudder + self._dt * u_k[3], -0.122173, 0.122173)
        self.rpm_hat_1 = np.clip(self.rpm_hat_1 + self._dt * u_k[4], -500.0, 450.0)
        self.rpm_hat_2 = np.clip(self.rpm_hat_2 + self._dt * u_k[5], -500.0, 450.0)
        
        self.delta_v_theta = u_k[6]

        # Update MPCC progress variable.
        # Theta is set by projecting the vehicle position onto the cubic
        # spline path.  The solver's v_theta >= 0 hard bound and e_sync
        # coupling already prevent theta from racing ahead of the vehicle,
        # so no forward-only ratchet is needed here.
        start_theta_time = time.time()
        if mpc_solution is not None and status == 0 and self.ref_is_traj and self.theta_total > 0:
            p_now = x_current[:3]
            search_window = max(2.0, self.v_theta * self._dt * 20)
            theta_proj = self._project_onto_path(
                p_now, theta_hint=self.theta, window=search_window
            )
            self.theta = np.clip(theta_proj, 0.0, self.theta_total)

            #self.v_theta = max(
            #    float(mpc_solution[self.nmpc.N_PHYS_STATES + 1]),
            #    0.1,
            #)
            self.v_theta = float(mpc_solution[self.nmpc.N_PHYS_STATES + 1])

        end_theta_time = time.time()
        theta_solver = float(self.ocp_solver.get(1, "x")[self.nmpc.N_PHYS_STATES])

        # Completion detection: theta-based (MPCC) + position/velocity check.
        theta_near_end = (
            self.theta_total > 0 and self.theta >= self.theta_total - 0.7   # increased from 0.1 to 0.5 since 0.1 is quite close to the end.
        )
        if self.ref_is_traj and theta_near_end:
            p_current_3d = x_current[:3]
            total_speed = np.linalg.norm(x_current[7:10])
            d_to_final = np.linalg.norm(p_current_3d - self.trajectory[-1, :3])
            stopped = total_speed < self._vel_stop_threshold
            at_goal = d_to_final < self._final_pos_tolerance

            self._loginfo(
                f"Final WP: speed={total_speed:.3f} m/s, d={d_to_final:.3f} m, "
                f"debounce={self._completion_debounce_count}/{self._completion_debounce_required}"
            )

            if stopped and at_goal:
                self._completion_debounce_count += 1
            else:
                self._completion_debounce_count = 0

            if self._completion_debounce_count >= self._completion_debounce_required:
                self._loginfo_once("Trajectory complete — signalling COMPLETED")
                self._dive_sub.set_current_idx(self.traj_len)
            else:
                self._dive_sub.set_current_idx(max(0, self.traj_len - 1))
        else:
            self._dive_sub.set_current_idx(self.traj_index)

        t_loop_end = time.time()
        t_loop = t_loop_end - t_loop_start
        np.set_printoptions(precision=3)
        s = f"\nNMPC INFO\n"
        s += f"NMPC solver status: {status}\n"
        s += f"MPC solve time: {end_time - start_time:.3f} s, \n"
        s += f"Ref loop time: {end_ref_time - start_ref_time:.3f} s\n"
        s += f"Theta loop time: {end_theta_time - start_theta_time:.3f} s\n"
        s += f"Loop time: {t_loop:.3f} s, dt: {self._dt:.3f} s\n"
        s += f"MPC pred: x: {simX[0]:.3f}, y: {simX[1]:.3f}, z: {simX[2]:.3f}\n"
        s += f"current state: x: {x_current[0]:.3f}, y: {x_current[1]:.3f}, z: {x_current[2]:.3f}\n"
        s += f"velocities: u: {x_current[7]:.3f}, v: {x_current[8]:.3f}, w: {x_current[9]:.3f}\n"
        s += f"refs: x: {self.ref[0, 0]:.3f}, y: {self.ref[0, 1]:.3f}, z: {self.ref[0, 2]:.3f}\n"
        s += f"theta: {self.theta:.3f}/{self.theta_total:.3f} (solver: {theta_solver:.3f}), v_theta: {self.v_theta:.3f} (solver: {mpc_solution[self.nmpc.N_PHYS_STATES + 1]:.3f}), delta_v_theta: {self.delta_v_theta:.3f}\n"
        tr = self._terminal_ref[:3]
        s += f"traj idx: {self.traj_index}/{self.traj_len}, term_ref: ({tr[0]:.2f}, {tr[1]:.2f}, {tr[2]:.2f})\n"
        s += f"u_vbs = {mpc_solution[13]:.3f}, u_lcg = {mpc_solution[14]:.3f} (state: vbs={x_current[13]:.1f}, lcg={x_current[14]:.1f})\n"

        u_stern, u_rudder = self._map_actuator_commands(mpc_solution)
        s += f"MPC Output: u_stern = {u_stern:.3f} u_rudder = {u_rudder:.3f}\n"
        s += f" u_rpm1 = {mpc_solution[17]:.3f} u_rpm2 = {mpc_solution[18]:.3f}\n"

        self._loginfo(s)

        return


    def _map_actuator_commands(self, mpc_solution):
        """Map MPC state (stern, rudder angles in model convention) to robot command.
        Flip sign only here if robot convention is opposite (e.g. positive rudder => port).
        Do not flip the rates (u_k[2], u_k[3]) used in a_hat_stern/a_hat_rudder."""
        u_stern = -mpc_solution[15] if self.flip_stern_command else mpc_solution[15]
        u_rudder = -mpc_solution[16] if self.flip_rudder_command else mpc_solution[16]
        return u_stern, u_rudder

    def _yaw_from_state_quat(self, q_wxyz):
        """Extract yaw (rad) from state quaternion [w, x, y, z] via xyz euler."""
        if np.any(np.isnan(q_wxyz)) or len(q_wxyz) < 4:
            return np.nan
        q_xyzw = [q_wxyz[1], q_wxyz[2], q_wxyz[3], q_wxyz[0]]
        return R.from_quat(q_xyzw).as_euler("xyz")[2]

    # ---- MPCC path geometry helpers ------------------------------------------

    def _compute_arc_lengths(self):
        """Compute cumulative arc-lengths and fit cubic splines through the waypoints.

        After this call:
          self.arc_lengths  — cumulative arc-length at each waypoint
          self.theta_total  — total path length
          self._spl_x/z     — CubicSpline: arc_length -> position (C2 smooth)
          self._spl_y       — PchipInterpolator: arc_length -> y (C1, monotone-preserving) to prevent switching y derivative.
        """
        self.arc_lengths = np.zeros(self.traj_len)
        for i in range(1, self.traj_len):
            self.arc_lengths[i] = self.arc_lengths[i - 1] + np.linalg.norm(
                self.trajectory[i, :3] - self.trajectory[i - 1, :3]
            )
        self.theta_total = self.arc_lengths[-1]

        s = self.arc_lengths
        # "not-a-knot" gives smooth, non-zero tangents at the endpoints
        # (unlike "clamped" which forces zero derivative).
        # Falls back to "natural" for 2-point paths where "not-a-knot" needs >= 3.
        bc = "not-a-knot" if self.traj_len >= 3 else "natural"
        self._spl_x = CubicSpline(s, self.trajectory[:, 0], bc_type=bc)
        self._spl_y = CubicSpline(s, self.trajectory[:, 1], bc_type=bc) #PchipInterpolator(s, self.trajectory[:, 1])
        self._spl_z = CubicSpline(s, self.trajectory[:, 2], bc_type=bc)
        self._loginfo(
            f"MPCC spline built: {self.traj_len} waypoints, "
            f"theta_total={self.theta_total:.3f} m"
        )
        # Pre-evaluate the spline for faster runtime access
        self.spl_eval_x = self._spl_x(np.linspace(0.0, self.theta_total, self.n_eval))
        self.spl_eval_y = self._spl_y(np.linspace(0.0, self.theta_total, self.n_eval))
        self.spl_eval_z = self._spl_z(np.linspace(0.0, self.theta_total, self.n_eval))

    def _get_path_geometry(self, theta_query):
        """Evaluate the cubic spline at an arc-length value.

        Returns (p_ref, t_hat, theta_hat):
          p_ref     — 3D position on the path
          t_hat     — unit tangent (from spline first derivative, smooth)
          theta_hat — clamped query value (linearization point)
        """
        theta_q = np.clip(theta_query, 0.0, self.theta_total)
        p_ref = np.array([
            float(self._spl_x(theta_q)),
            float(self._spl_y(theta_q)),
            float(self._spl_z(theta_q)),
        ])
        dp = np.array([
            float(self._spl_x(theta_q, 1)),
            float(self._spl_y(theta_q, 1)),
            float(self._spl_z(theta_q, 1)),
        ])
        norm = np.linalg.norm(dp) + 1e-12
        t_hat = dp / norm
        return p_ref, t_hat, theta_q

    def _project_onto_path(self, pos, theta_hint=None, window=None):
        """Project a 3D position onto the cubic spline path, return arc-length.

        Minimises the squared distance from *pos* to the spline curve within
        [theta_hint - 0.5, theta_hint + window] (or the full path when no hint
        is given).  A coarse sample sweep seeds a bounded scalar optimisation
        so the result tracks the spline the vehicle is actually following,
        not the piecewise-linear waypoint segments.
        """
        pos = np.asarray(pos, dtype=float)

        if theta_hint is not None and window is not None:
            lo = max(theta_hint, 0.0)
            hi = min(theta_hint + window, self.theta_total)
        else:
            lo, hi = 0.0, self.theta_total

        if hi - lo < 1e-12:
            return lo

        def _dist_sq(theta):
            dx = float(self._spl_x(theta)) - pos[0]
            dy = float(self._spl_y(theta)) - pos[1]
            dz = float(self._spl_z(theta)) - pos[2]
            return dx * dx + dy * dy + dz * dz

        result = minimize_scalar(
            _dist_sq, bounds=(lo, hi), method="bounded",
            options={"xatol": 1e-3, "maxiter": 50},
        )
        return float(result.x)

    # ---- debug helper --------------------------------------------------------

    def compute_x_error_numpy(self, x, ref, terminal=True, t_hat=None, theta_hat=0.0):
        """
        NumPy mirror of x_error() for runtime debugging.

        MPCC residual structure:
          Stage:    [e_c_vec(3), e_l(1), v_theta(1), u_phys(6)] = 11
          Terminal: [pos_error(3), q_att_error(4), vel_error(6)] = 13
        """
        ref = np.asarray(ref).flatten()
        ref_pad = np.zeros(max(self.nmpc.N_PHYS_STATES, len(ref)))
        ref_pad[: min(len(ref), self.nmpc.N_PHYS_STATES)] = ref[: self.nmpc.N_PHYS_STATES]

        q1 = ref_pad[3:7].copy()
        q1 = q1 / (np.linalg.norm(q1) + 1e-12)
        q2 = np.array(x[3:7], dtype=float)
        q2 = q2 / (np.linalg.norm(q2) + 1e-12)
        q_conj = np.array([q2[0], -q2[1], -q2[2], -q2[3]])

        q_err_w = (
            q1[0] * q_conj[0]
            - q1[1] * q_conj[1]
            - q1[2] * q_conj[2]
            - q1[3] * q_conj[3]
        )
        q_err_x = (
            q1[0] * q_conj[1]
            + q1[1] * q_conj[0]
            + q1[2] * q_conj[3]
            - q1[3] * q_conj[2]
        )
        q_err_y = (
            q1[0] * q_conj[2]
            - q1[1] * q_conj[3]
            + q1[2] * q_conj[0]
            + q1[3] * q_conj[1]
        )
        q_err_z = (
            q1[0] * q_conj[3]
            + q1[1] * q_conj[2]
            - q1[2] * q_conj[1]
            + q1[3] * q_conj[0]
        )
        if q_err_w < 0:
            q_err_w, q_err_x, q_err_y, q_err_z = (
                -q_err_w,
                -q_err_x,
                -q_err_y,
                -q_err_z,
            )
        q_att_error = np.array(
            [1.0 - q_err_w, q_err_x, q_err_y, q_err_z], dtype=float
        )

        pos_error = np.array(x[0:3], dtype=float) - ref_pad[0:3]
        vel_error = np.array(x[7:13], dtype=float) - ref_pad[7:13]

        # MPCC contour / lag errors (only meaningful when t_hat is provided)
        if t_hat is not None:
            theta_val = float(x[self.nmpc.N_PHYS_STATES]) if len(x) > self.nmpc.N_PHYS_STATES else 0.0
            p_ref = ref_pad[:3]
            path_pos = p_ref + t_hat * (theta_val - theta_hat)
            pos_diff = np.array(x[:3], dtype=float) - path_pos
            e_l_val = float(np.dot(pos_diff, t_hat))
            e_c_vec = pos_diff - e_l_val * t_hat
        else:
            e_c_vec = np.zeros(3)
            e_l_val = 0.0

        result = {
            "pos_error": pos_error,
            "q_att_error": q_att_error,
            "q_error_wxyz": np.array([q_err_w, q_err_x, q_err_y, q_err_z]),
            "vel_error": vel_error,
            "e_c_vec": e_c_vec,
            "e_l": e_l_val,
        }
        return result

    def print_reference_vs_state_debug(self, x_current, mpc_solution=None):
        """Log MPCC reference vs state for debugging."""
        if self.ref is None or self.ref.shape[0] == 0:
            self._loginfo("REF_STATE_DBG: no reference set")
            return

        r = self.ref[0, :]
        yaw_ref = self._yaw_from_state_quat(r[3:7])
        yaw_cur = self._yaw_from_state_quat(x_current[3:7])
        yaw_err = np.arctan2(
            np.sin(yaw_cur - yaw_ref), np.cos(yaw_cur - yaw_ref)
        )

        err = self.compute_x_error_numpy(
            x_current, r, terminal=False,
            t_hat=self.path_t_hat[0], theta_hat=self.path_theta_hat[0],
        )
        lines = [
            "========== MPCC DEBUG ==========",
            f"  theta: {self.theta:.3f}/{self.theta_total:.3f}  traj_idx: {self.traj_index}/{self.traj_len}",
            f"  REF  pos=({r[0]:.3f}, {r[1]:.3f}, {r[2]:.3f})  yaw={np.rad2deg(yaw_ref):.1f} deg",
            f"  STATE pos=({x_current[0]:.3f}, {x_current[1]:.3f}, {x_current[2]:.3f})  yaw={np.rad2deg(yaw_cur):.1f} deg",
            f"  vel u,v,w=({x_current[7]:.3f}, {x_current[8]:.3f}, {x_current[9]:.3f})",
            f"  stern={x_current[15]:.3f}  rudder={x_current[16]:.3f}",
            f"  MPCC  e_c={np.linalg.norm(err['e_c_vec']):.4f}  e_l={err['e_l']:.4f}  yaw_err={np.rad2deg(yaw_err):.1f} deg",
        ]
        if mpc_solution is not None:
            cmd_stern, cmd_rudder = self._map_actuator_commands(mpc_solution)
            lines.append(
                f"  cmd stern={cmd_stern:.4f}  rudder={cmd_rudder:.4f}"
            )
        self._loginfo("\n".join(lines))

    def get_reference(self):
        # TODO: refactor this if-statement as function.
        if self.ref_is_traj and not self._initialized:
            self.trajectory = self._dive_sub.get_path()

            if self.trajectory is None:
                self._loginfo_once("No trajectory received")
                return False
            else:
                self.trajectory = np.array(
                    self.trajectory
                )  # Convert/make sure it is a numpy array
                if self.convert_trajectory_to_frd:
                    self.trajectory = self.convert_traj_flu_to_frd(self.trajectory)

            self._loginfo("get ref")

            # Declare duration of sim.
            self._loginfo(f"trajectory: {self.trajectory}")
            self.traj_len = self.trajectory.shape[0]

            # Pad trajectory to N_PHYS_STATES columns if the CSV has fewer
            n_phys = self.nmpc.N_PHYS_STATES  # 19
            if self.trajectory.shape[1] < n_phys:
                pad = np.zeros((self.traj_len, n_phys - self.trajectory.shape[1]))
                self.trajectory = np.concatenate((self.trajectory, pad), axis=1)

            # Insert theta column (index 19) and control ref columns (7)
            theta_col = np.zeros((self.traj_len, 1))
            Uref = np.zeros((self.traj_len, self.nu))  # 7 columns
            self.trajectory = np.concatenate(
                (self.trajectory, theta_col, Uref), axis=1
            )
            # self.trajectory now has shape (traj_len, 20 + 7) = (traj_len, 27)

            # Snap first waypoint to the vehicle's current position so the
            # spline starts where the AUV actually is.  Avoids initial lateral
            # correction from DR drift that can overshoot at high RPM.
            #if self._current_state is not None:
            #    self.trajectory[0, 0] = self._current_state.pose.pose.position.x
            #    self.trajectory[0, 1] = self._current_state.pose.pose.position.y
            #    self.trajectory[0, 2] = self._current_state.pose.pose.position.z
            #    self._loginfo(
            #        f"Snapped WP0 to vehicle position: "
            #        f"({self.trajectory[0, 0]:.3f}, {self.trajectory[0, 1]:.3f}, {self.trajectory[0, 2]:.3f})"
            #    )

            self._goal_pos = self.trajectory[-1, :3].copy()
            self._completion_debounce_count = 0

            # Compute arc-lengths for MPCC path parameterization
            self._compute_arc_lengths()

        elif not self.ref_is_traj:
            if not self._dive_sub.has_waypoint():
                self._loginfo(f"No waypoint available")
                return False

            # Get Waypoint information
            waypoint_in_mocap = self._dive_sub.get_waypoint()

            # FIXME: This might be useless.
            if waypoint_in_mocap is None:
                self._loginfo(f"waypoint_in_mocap is None")
                return False

            self.waypoint = self.convert_wp_to_odometry(waypoint_in_mocap)

            self.wp_array = self.get_wp_array(self.waypoint)

            # Store waypoint position for the braking constraint
            self._goal_pos = np.array([
                self.waypoint.pose.pose.position.x,
                self.waypoint.pose.pose.position.y,
                self.waypoint.pose.pose.position.z,
            ])

        return True

    def convert_traj_flu_to_frd(self, trajectory):
        """
        Convert trajectory states from FLU to FRD conventions.
        Expected columns:
        [x, y, z, qw, qx, qy, qz, u, v, w, p, q, r, ...]
        """
        traj_frd = np.array(trajectory, copy=True)

        # Quaternion conversion.
        for i in range(traj_frd.shape[0]):
            quat_frd = self.quat_flu_to_frd(traj_frd[i, 3:7])
            traj_frd[i, 3:7] = quat_frd

        # Body velocity/sign conversion, matching convert_flu_to_frd().
        traj_frd[:, 8] *= -1.0  # v
        traj_frd[:, 9] *= -1.0  # w
        traj_frd[:, 11] *= -1.0  # q
        traj_frd[:, 12] *= -1.0  # r

        return traj_frd

    def convert_flu_to_frd(self, flu_msg, convert_state=True):
        """
        If convert_state, it converts an odometry message from FLU to FRD

        """
        frd_odometry = Odometry()
        frd_odometry.header.frame_id = flu_msg.header.frame_id
        frd_odometry.header.stamp = flu_msg.header.stamp
        if convert_state:
            frd_odometry.pose.pose.position.x = flu_msg.pose.pose.position.x
            frd_odometry.pose.pose.position.y = flu_msg.pose.pose.position.y
            frd_odometry.pose.pose.position.z = flu_msg.pose.pose.position.z
            quat = self.quat_flu_to_frd(
                [
                    flu_msg.pose.pose.orientation.w,
                    flu_msg.pose.pose.orientation.x,
                    flu_msg.pose.pose.orientation.y,
                    flu_msg.pose.pose.orientation.z,
                ]
            )
            frd_odometry.pose.pose.orientation.x = quat[1]
            frd_odometry.pose.pose.orientation.y = quat[2]
            frd_odometry.pose.pose.orientation.z = quat[3]
            frd_odometry.pose.pose.orientation.w = quat[0]

            frd_odometry.twist.twist.linear.x = flu_msg.twist.twist.linear.x
            frd_odometry.twist.twist.linear.y = -flu_msg.twist.twist.linear.y
            frd_odometry.twist.twist.linear.z = -flu_msg.twist.twist.linear.z
            frd_odometry.twist.twist.angular.x = flu_msg.twist.twist.angular.x
            frd_odometry.twist.twist.angular.y = -flu_msg.twist.twist.angular.y
            frd_odometry.twist.twist.angular.z = -flu_msg.twist.twist.angular.z

        else:
            frd_odometry = flu_msg

        return frd_odometry

    def quat_flu_to_frd(self, q_flu):
        """
        quat_flu = [q0, q1, q2, q3], with q0 the scalar part
        """
        quat_flu = np.array([q_flu[1], q_flu[2], q_flu[3], q_flu[0]])

        rot = R.from_euler("x", 180, degrees=True)
        r_flu = R.from_quat(
            quat_flu
        )  # Convert ENU quaternion to rotation object, assumes scalar last
        r_frd = r_flu.as_matrix() @ rot.as_matrix()
        quat_frd = R.from_matrix(
            r_frd
        ).as_quat()  # Convert back to quaternion with scalar last
        quat_frd_right_order = np.array(
            [
                quat_frd[3],  # w
                quat_frd[0],  # x
                quat_frd[1],  # y
                quat_frd[2],  # z
            ]
        )
        return quat_frd_right_order

    def convert_wp_to_odometry(self, wp_msg):
        """
        Returns waypoint as Odometry
        """
        odom_wp = Odometry()

        if isinstance(wp_msg, PoseStamped):
            odom_wp.header.frame_id = wp_msg.header.frame_id
            odom_wp.header.stamp = wp_msg.header.stamp

            odom_wp.pose.pose = wp_msg.pose

        elif isinstance(wp_msg, Pose):
            odom_wp.header.frame_id = "/mocap"
            odom_wp.header.stamp = self._node.get_clock().now().to_msg()
            odom_wp.pose.pose.position = wp_msg.position
            odom_wp.pose.pose.orientation = wp_msg.orientation

        elif isinstance(wp_msg, Odometry):
            odom_wp = wp_msg

        else:
            return None

        return odom_wp

    def get_state_array(self, state_msg, control_msg, is_init_state=False, is_trajectory=False):
        """
        Build the augmented state vector x (20 elements):
          x[0:13]  = physical states (pos, quat, vel)
          x[13:19] = actuator states (VBS, LCG, stern, rudder, rpm1, rpm2)
          x[19]    = theta (MPCC arc-length progress)
        """
        x = np.zeros(self.nx)  # 20

        x[0] = state_msg.pose.pose.position.x
        x[1] = state_msg.pose.pose.position.y
        x[2] = state_msg.pose.pose.position.z
        x[3:7] = [
            state_msg.pose.pose.orientation.w,
            state_msg.pose.pose.orientation.x,
            state_msg.pose.pose.orientation.y,
            state_msg.pose.pose.orientation.z,
        ]
        x[7] = state_msg.twist.twist.linear.x
        x[8] = state_msg.twist.twist.linear.y
        x[9] = state_msg.twist.twist.linear.z
        x[10] = state_msg.twist.twist.angular.x
        x[11] = state_msg.twist.twist.angular.y
        x[12] = state_msg.twist.twist.angular.z
        x[13] = control_msg["vbs"]
        x[14] = control_msg["lcg"]

        # Thrust vectoring and RPM states come from internal estimators, not topic
        # echoes, so they are always consistent with the model's own integration.
        # No sign flip here — rpm_hat tracks the model-convention value; the sign
        # is applied to the published command in set_publishers via _rpm1_sign().
        x[15] = self.a_hat_stern
        x[16] = self.a_hat_rudder
        x[17] = self.rpm_hat_1
        x[18] = self.rpm_hat_2
        x[19] = self.theta
        x[20] = self.v_theta    # we need this in the OCP for the MPCC and the dynamics.

        if is_init_state and not is_trajectory:
            x[17] = 1e-6
            x[18] = 1e-6

        return x

    def get_wp_array(self, waypoint):

        ref = np.zeros(self.nx + self.nu)  # 27

        ref[0] = waypoint.pose.pose.position.x
        ref[1] = waypoint.pose.pose.position.y
        ref[2] = waypoint.pose.pose.position.z
        ref[3] = waypoint.pose.pose.orientation.w
        ref[4] = waypoint.pose.pose.orientation.x
        ref[5] = waypoint.pose.pose.orientation.y
        ref[6] = waypoint.pose.pose.orientation.z

        ref[7] = 0.2  # nominal cruise speed (for terminal cost)

        ref[13] = 50  # VBS neutral
        ref[14] = 50  # LCG neutral
        # ref[19] = theta_ref  (0 — set by the controller)
        # ref[20:27] = control rate refs (all zero)

        return ref

    def initialize_mpc(self):
        """
        Seed the solver with an initial guess.

        Position is linearly interpolated toward the first target.  Theta is
        linearly interpolated from the current projection to the path end.
        """
        # Clear stale internal state (multipliers, QP iterate) from any
        # previous run.  Without this, SQP_RTI can fail immediately on
        # restart because the cached iterate is far from the new initial state.
        try:
            self.ocp_solver.reset()
        except Exception:
            pass

        self._depth_locked = False
        self._wall_locked = False

        x0 = self.get_state_array(
            self._current_state,
            self._current_control,
            is_init_state=not self._initialized,
            is_trajectory=self.ref_is_traj,
        )

        target_pos = None
        if self.ref_is_traj and self.trajectory is not None:
            target_pos = self.trajectory[0, :3]
        elif not self.ref_is_traj and hasattr(self, "wp_array"):
            target_pos = self.wp_array[:3]

        v_init = 0.1
        rpm_warm = 300.0  # above the 200 RPM deadzone so SQP sees non-zero thrust
        self.rpm_hat_1 = rpm_warm
        self.rpm_hat_2 = rpm_warm

        # Project theta to the vehicle's actual position on the path so the
        # warm-start is consistent with where the vehicle already is, rather
        # than starting at theta=0 which may be behind the vehicle.
        if self.ref_is_traj and self.theta_total > 0:
            self.theta = self._project_onto_path(x0[:3])
            self.theta = np.clip(self.theta, 0.0, self.theta_total)
            self._loginfo(f"Init theta projected to {self.theta:.3f}/{self.theta_total:.3f}")

        for stage in range(self.N_horizon + 1):
            x_init = x0.copy()
            if target_pos is not None:
                t = stage / self.N_horizon
                x_init[:3] = x0[:3] + t * (target_pos - x0[:3])
            x_init[17] = rpm_warm
            x_init[18] = rpm_warm
            x_init[19] = min(
                self.theta + stage * self._dt * v_init,
                self.theta_total,
            )
            x_init[20] = v_init
            self.ocp_solver.set(stage, "x", x_init)

        u_init = np.zeros(self.nu)
        u_init[6] = 0.1  # positive delta_v_theta so SQP_RTI can see the progress reward
        for stage in range(self.N_horizon):
            self.ocp_solver.set(stage, "u", u_init)

        self._v_theta_prev = v_init

        # Run a few warm-up solves so SQP_RTI can converge the internal
        # iterate before the first real control step.  This prevents the
        # "crash on first solve" problem with cold starts.
        self.ocp_solver.set(0, "lbx", x0)
        self.ocp_solver.set(0, "ubx", x0)
        self.get_current_ref_array()
        decel_dist = 2.5
        for stage in range(self.N_horizon):
            ref_row = self.ref[stage, :] if stage < self.ref.shape[0] else self.ref[-1, :]
            p = np.r_[ref_row, self._goal_pos,
                       self.path_t_hat[stage], self.path_theta_hat[stage]]
            self.ocp_solver.set(stage, "p", p)
            yref_k = np.zeros(self.nmpc.n_stage_cost)
            if self.ref_is_traj and self.theta_total > 0:
                remaining_k = max(self.theta_total - self.path_theta_hat[stage], 0.0)
                yref_k[4] = self._v_target * min(remaining_k / decel_dist, 1.0)
            else:
                yref_k[4] = self._v_target
            self.ocp_solver.cost_set(stage, "yref", yref_k)
        terminal_ref = self.ref[-1, :]
        p_terminal = np.r_[terminal_ref, self._goal_pos,
                           self.path_t_hat[-1], self.path_theta_hat[-1]]
        self.ocp_solver.set(self.N_horizon, "p", p_terminal)
        yref_e = np.zeros(self.nmpc.n_terminal_cost)
        self.ocp_solver.cost_set(self.N_horizon, "yref", yref_e)

        n_warmup = 5
        for i in range(n_warmup):
            status = self.ocp_solver.solve()
            if status == 0:
                break
        self._loginfo(f"MPC warm-up: {i+1} solves, final status={status}")

        self._initialized = True

    def get_current_ref_array(self):
        """
        MPCC reference: compute per-stage path geometry (p_ref, t_hat, theta_hat)
        by manually propagating theta forward through the horizon using v_theta
        from the previous solve, then evaluating the cubic spline at each stage.

        For waypoint mode, the path is a straight line from the current
        position to the waypoint (no spline).
        """
        q_current_wxyz = np.array(
            [
                self._current_state.pose.pose.orientation.w,
                self._current_state.pose.pose.orientation.x,
                self._current_state.pose.pose.orientation.y,
                self._current_state.pose.pose.orientation.z,
            ]
        )

        if self.ref_is_traj:
            x_pos = self._current_state.pose.pose.position.x
            y_pos = self._current_state.pose.pose.position.y
            z_pos = self._current_state.pose.pose.position.z

            # ---- Propagate theta_hat forward through the horizon ----
            # Constant-speed propagation with a floor so the solver always
            # sees some path geometry ahead, even when the vehicle is at rest
            # or when delta_v_theta is negative during early solves.
            # No delta_v_theta in the propagation — avoids both the runaway
            # problem (delta_v_theta positive) and the collapse problem
            # (delta_v_theta negative).  The solver's internal theta is free
            # to advance at whatever rate the OCP finds optimal.
            theta_i = self.theta
            N_half = self.N_horizon // 2
            # Original values:
            # v_near = max(self.v_theta, 0.4)
            # v_far  = max(self.v_theta * 1.5, 0.8)
            # Cap lookahead speeds at the OCP's hard v_theta_max bound so the
            # linearization points never race ahead of where the solver can
            # actually advance theta.  On curved paths (dives) an over-
            # aggressive lookahead evaluates t_hat at unreachable arc-lengths,
            # corrupting the SQP gradient and causing QP failures.
            v_theta_max = 0.2
            v_near = min(max(self.v_theta, 0.1), v_theta_max)
            v_far  = min(max(self.v_theta * 1.2, 0.15), v_theta_max)

            # No lookahead ramp-down: the theta_total clamp below already
            # prevents theta_hat from overshooting the path end.  Without the
            # ramp, stages beyond the endpoint cluster at theta_total, and the
            # per-stage v_theta target (set in update()) drops to 0 for all of
            # them.  This gives the solver many stages showing "stop here,"
            # producing a strong deceleration gradient.
            for stage in range(self.N_horizon):
                v_stage = v_near if stage < N_half else v_far
                theta_i = min(theta_i + v_stage * self._dt, self.theta_total)
                self.path_theta_hat[stage] = theta_i

            # ---- Build reference array with path geometry per stage ----
            # The heading_offset lets the vehicle anticipate pitch changes
            # (important for sensor trim).  However, at sharp direction
            # reversals the offset tangent can flip 180°, corrupting the
            # contour/lag decomposition (the OCP uses one t_hat for both).
            # Guard: only apply the offset when the ahead-tangent roughly
            # agrees with the local tangent (cos > 0); fall back to the
            # local tangent at sharp reversals.
            heading_offset = 2.0  # [m] pitch-trim lookahead
            self.ref = np.zeros((self.N_horizon, self.nx + self.nu))
            for stage in range(self.N_horizon):
                p_ref, t_local, _ = self._get_path_geometry(self.path_theta_hat[stage])
                theta_ahead = min(self.path_theta_hat[stage] + heading_offset, self.theta_total)
                _, t_ahead, _ = self._get_path_geometry(theta_ahead)
                if np.dot(t_local, t_ahead) > 0.0:
                    t_hat = t_ahead
                else:
                    t_hat = t_local

                self.ref[stage, :3] = p_ref
                self.path_t_hat[stage] = t_hat
                

                # This is never used. The actual computational cost is based on t_hat and p_ref alone
                yaw = np.arctan2(t_hat[1], t_hat[0])
                pitch = -np.arcsin(np.clip(t_hat[2], -1.0, 1.0))
                
                cy, sy = np.cos(yaw / 2), np.sin(yaw / 2)
                cp, sp = np.cos(pitch / 2), np.sin(pitch / 2)
                self.ref[stage, 3] = cy * cp       # qw
                self.ref[stage, 4] = -sy * sp      # qx
                self.ref[stage, 5] = cy * sp       # qy
                self.ref[stage, 6] = sy * cp       # qz

            # Terminal reference: extend one step beyond the last propagated
            # theta_hat.  As the vehicle nears the end, path_theta_hat[-1]
            # naturally approaches theta_total (clamped in the propagation
            # loop), so the terminal reaches the endpoint organically.
            # Deceleration is handled by yref_e (v_theta target = 0 at
            # terminal), not by a hard position jump.
            theta_terminal = min(
                self.path_theta_hat[-1] + v_far * self._dt,
                self.theta_total,
            )
            p_term, t_term_local, _ = self._get_path_geometry(theta_terminal)
            theta_term_ahead = min(theta_terminal + heading_offset, self.theta_total)
            _, t_term_ahead, _ = self._get_path_geometry(theta_term_ahead)
            t_term = t_term_ahead if np.dot(t_term_local, t_term_ahead) > 0.0 else t_term_local


            self._terminal_ref = np.zeros(self.nx + self.nu)
            self._terminal_ref[:3] = p_term

            yaw_t = np.arctan2(t_term[1], t_term[0])
            pitch_t = -np.arcsin(np.clip(t_term[2], -1.0, 1.0))
           
            cy_t, sy_t = np.cos(yaw_t / 2), np.sin(yaw_t / 2)
            cp_t, sp_t = np.cos(pitch_t / 2), np.sin(pitch_t / 2)
            self._terminal_ref[3] = cy_t * cp_t
            self._terminal_ref[4] = -sy_t * sp_t
            self._terminal_ref[5] = cy_t * sp_t
            self._terminal_ref[6] = sy_t * cp_t

            self._enforce_reference_quaternion_continuity(q_current_wxyz)

            self._update_goal_pos_from_arc_length(
                np.array([x_pos, y_pos, z_pos])
            )

            # Update traj_index for progress reporting (not used by MPCC cost)
            if self.arc_lengths is not None and self.theta_total > 0:
                self.traj_index = int(
                    np.searchsorted(self.arc_lengths, self.theta, side="right") - 1
                )
                self.traj_index = np.clip(self.traj_index, 0, self.traj_len - 1)
            return

        # TODO: This can be removed since we don't have a waypoint mode anymore. 
        # Same with the ref_is_traj flag and eveyrthing else related to the wp mode.
        # Maybe add again later if needed.
        else:  # waypoint mode
            self.ref = np.zeros((self.N_horizon, self.nx + self.nu))
            self.ref[:, :] = self.wp_array

            x_pos = self._current_state.pose.pose.position.x
            y_pos = self._current_state.pose.pose.position.y
            z_pos = self._current_state.pose.pose.position.z
            wp_pos = self.wp_array[:3]
            diff = wp_pos - np.array([x_pos, y_pos, z_pos])
            norm = np.linalg.norm(diff) + 1e-8
            t_hat = diff / norm
            self.path_t_hat[:] = t_hat
            self.path_theta_hat[:] = 0.0
            self.theta_total = norm

            self._terminal_ref = self.wp_array.copy()
            self._terminal_ref[7:13] = 0.0
            self._enforce_reference_quaternion_continuity(q_current_wxyz)
            return

    def _update_goal_pos_from_arc_length(self, p_current):
        """Set _goal_pos so the OCP speed funnel sees remaining *path* distance.

        The OCP braking constraint computes Euclidean distance from the
        predicted state to _goal_pos.  For curved trajectories the straight-
        line shortcut to the final waypoint can be much shorter than the
        actual remaining path, causing the vehicle to brake prematurely.

        Fix: place _goal_pos along the line from p_current toward the final
        waypoint, but at a distance equal to the remaining arc length (from
        the MPCC progress variable theta).
        """
        final_pos = self.trajectory[-1, :3]
        euclidean = np.linalg.norm(p_current - final_pos)
        arc = max(self.theta_total - self.theta, 0.0)

        if arc > euclidean and euclidean > 1e-3:
            direction = (final_pos - p_current) / euclidean
            self._goal_pos = p_current + direction * arc
        else:
            self._goal_pos = final_pos.copy()

    def _enforce_reference_quaternion_continuity(self, q_current_wxyz):
        """Flip reference quaternions so they stay in the same hemisphere as the current state."""
        if self.ref is None or self.ref.shape[0] == 0:
            return

        prev_q = self._normalize_quat_wxyz(q_current_wxyz)
        for i in range(self.ref.shape[0]):
            q_i = self._align_quat_hemisphere(self.ref[i, 3:7], prev_q)
            self.ref[i, 3:7] = q_i
            prev_q = q_i

    @staticmethod
    def _normalize_quat_wxyz(q):
        n = np.linalg.norm(q)
        if n < 1e-9:
            return np.array([1.0, 0.0, 0.0, 0.0])
        return q / n

    def _align_quat_hemisphere(self, q_wxyz, q_ref_wxyz):
        q = self._normalize_quat_wxyz(q_wxyz)
        q_ref = self._normalize_quat_wxyz(q_ref_wxyz)
        return -q if np.dot(q, q_ref) < 0.0 else q

    RPM_MIN = -500.0
    RPM_MAX = 450.0

    def set_publishers(self, mpc_solution):
        """Publish actuator commands and update convenience topics."""
        u_vbs = mpc_solution[13]
        u_lcg = mpc_solution[14]
        u_stern, u_rudder = self._map_actuator_commands(mpc_solution)
        
        # Safety measure to really never exceed the RPM limits because we have an internal rpm state estimator
        u_rpm1 = np.clip(mpc_solution[17], self.RPM_MIN, self.RPM_MAX)
        u_rpm2 = np.clip(mpc_solution[18], self.RPM_MIN, self.RPM_MAX)

        self._dive_pub.set_vbs(u_vbs)
        self._dive_pub.set_lcg(u_lcg)
        self._dive_pub.set_thrust_vector(u_rudder, u_stern)
        self._dive_pub.set_rpm(u_rpm1, u_rpm2)

        self._input = ControlInput()
        self._input.vbs = u_vbs
        self._input.lcg = u_lcg
        self._input.thrustervertical = u_stern
        self._input.thrusterhorizontal = u_rudder
        self._input.thrusterrpm1 = float(u_rpm1)
        self._input.thrusterrpm2 = float(u_rpm2)

        if self.ref is not None:
            self._ref = Odometry()
            self._ref.pose.pose.position.x = self.ref[0, 0]
            self._ref.pose.pose.position.y = self.ref[0, 1]
            self._ref.pose.pose.position.z = self.ref[0, 2]
            self._ref.pose.pose.orientation.w = self.ref[0, 3]
            self._ref.pose.pose.orientation.x = self.ref[0, 4]
            self._ref.pose.pose.orientation.y = self.ref[0, 5]
            self._ref.pose.pose.orientation.z = self.ref[0, 6]
            self._ref.twist.twist.linear.x = self.ref[0, 7]
            self._ref.twist.twist.linear.y = self.ref[0, 8]
            self._ref.twist.twist.linear.z = self.ref[0, 9]
            self._ref.twist.twist.angular.x = self.ref[0, 10]
            self._ref.twist.twist.angular.y = self.ref[0, 11]
            self._ref.twist.twist.angular.z = self.ref[0, 12]

            self._control_ref = ControlInput()
            self._control_ref.vbs = self.ref[0, 13]
            self._control_ref.lcg = self.ref[0, 14]
            self._control_ref.thrustervertical = self.ref[0, 15]
            self._control_ref.thrusterhorizontal = self.ref[0, 16]
            self._control_ref.thrusterrpm1 = float(self.ref[0, 17])
            self._control_ref.thrusterrpm2 = float(self.ref[0, 18])

    def get_mpc_pred(self):
        """
        Get method for the MPC predictions
        """
        return self.pred_mpc

    def get_mpc_path_ref(self):
        return self.ref
    
    def get_spline_traj(self):
        if self.spl_eval_x is None or self.spl_eval_y is None or self.spl_eval_z is None:
            return None
        pos_spline = np.column_stack((self.spl_eval_x, self.spl_eval_y, self.spl_eval_z))
        quat_spline = np.zeros((self.n_eval, 4))
        for i in range(self.n_eval):
            quat_spline[i, :] = R.from_euler('xyz', [0, 0, 0]).as_quat()
        spline = np.column_stack((pos_spline, quat_spline))
        return spline

