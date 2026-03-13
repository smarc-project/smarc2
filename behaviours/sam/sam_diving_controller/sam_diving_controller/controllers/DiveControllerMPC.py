#!/usr/bin/python3

import time

import casadi as ca
import numpy as np
from geometry_msgs.msg import Pose, PoseStamped
from nav_msgs.msg import Odometry
from scipy.spatial.transform import Rotation as R
from smarc_control_msgs.msg import ControlInput, ControlReference
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

        # Convenience Topics
        self._current_state = None
        self._current_state_in_odom = None
        self._current_state_in_mocap = None
        self._current_control = None
        self._ref = None
        self._error = None
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
        self._vel_stop_threshold = 0.05  # m/s

        # Position tolerance for completion detection at the final waypoint.
        self._final_pos_tolerance = 0.75  # m

        # Debounce counter for COMPLETED detection.  All stopping conditions must be
        # satisfied for this many consecutive control steps before the action is
        # declared COMPLETED.
        self._completion_debounce_required = 5   # steps (~0.5 s at 10 Hz)
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
        self.N_horizon = 40 #30  # Prediction horizon
        self.nmpc = NMPC(sam, self._dt, self.N_horizon, update_solver_settings=build)
        self.nx = self.nmpc.nx  # State vector length + control vector
        self.nu = self.nmpc.nu  # Control derivative vector length
        self.simU = np.zeros(self.nu)

        self.wp_array = np.zeros(self.nx + self.nu)

        self.ref = np.zeros((self.N_horizon, (self.nx + self.nu)))

        # Goal position [x, y, z] of the final trajectory waypoint.
        # Appended to every parameter vector sent to the OCP solver so the
        # braking/speed-funnel constraint can compute dist-to-goal at each stage.
        self._goal_pos = np.zeros(3)

        # Run the MPC setup
        self.ocp_solver, self.integrator = self.nmpc.setup()


        # NOTE: This needs to happen in the update function with some check
        # before proceeding. Otherwise, you don't get the right data from the
        # dive sub node, because it's not yet spinning and thus doesn't get the
        # topics yet.
        self._initialized = False
        self._prev_commanding = False

        self.ref_is_traj = ref_is_trajectory

        # ---- Horizon filling strategy -------------------------------------------
        # horizon_max_waypoints: how many trajectory waypoints to place in the
        #   prediction horizon.
        #   0 = full remaining trajectory (up to N_horizon stages), pad with last WP.
        #   1 = current waypoint only, repeated across the whole horizon.
        #   N = take the next N waypoints from traj_index, pad remainder with last.
        self._node.declare_parameter("horizon_max_waypoints", 0)
        self._horizon_max_waypoints = self._node.get_parameter(
            "horizon_max_waypoints"
        ).get_parameter_value().integer_value

        # horizon_current_wp_ratio: when > 0 and at least 2 waypoints remain,
        #   split the horizon into [current WP | next WP] instead of sequential
        #   packing.  The value is the fraction of horizon stages that show the
        #   current waypoint (e.g. 0.33 = 1/3 current, 2/3 next).
        #   0.0 = disabled (pack waypoints sequentially, 1 stage each, pad rest).
        self._node.declare_parameter("horizon_current_wp_ratio", 0.0)
        self._horizon_current_wp_ratio = self._node.get_parameter(
            "horizon_current_wp_ratio"
        ).get_parameter_value().double_value
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
        # Waypoint progression: require both position and heading within tolerance before advancing.
        # Tuning: looser yaw_tolerance reduces back-and-forth for nonholonomic turns but may advance early.
        self._node.declare_parameter("traj_d_tolerance_m", 0.25)
        self._node.declare_parameter("traj_yaw_tolerance_deg", 25.0)
        self._traj_d_tolerance = self._node.get_parameter(
            "traj_d_tolerance_m"
        ).get_parameter_value().double_value
        self._traj_yaw_tolerance_deg = self._node.get_parameter(
            "traj_yaw_tolerance_deg"
        ).get_parameter_value().double_value
        # Keep state and reference in the same frame convention.
        # NOTE: Set to False if trajectory is already generated in FRD/NED convention!
        # Your create_turbo_turn_path.py uses USE_NED_CONVENTION=True, so it's already FRD.
        self.convert_trajectory_to_frd = False

        # RPM1 sign from use_sim_time (already declared by node/launch): sim => +1, robot => -1
        self.flip_rpm1_command = self._node.get_parameter(
            "use_sim_time"
        ).get_parameter_value().bool_value

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

        # ---- Depth-aware reference quaternion ----------------------------------
        #
        # Problem: The MPC receives a flat (zero-pitch) quaternion reference even
        # when the target is at a different depth.  Quaternion cost (weight 500)
        # then RESISTS pitching, so the vehicle goes horizontally to the target
        # x,y and only dives afterwards.
        #
        # Fix: compute the reference quaternion from the vector to the goal so it
        # carries both the correct yaw (faces the waypoint → no phantom steering)
        # and the correct pitch (nose-down proportional to depth-to-go → early dive).
        #
        # enable_depth_pitch_ref: add a pitch component to the reference quaternion
        #   proportional to atan2(dz, d_horizontal) toward the goal depth.
        #   False = original behaviour (flat quaternion reference from waypoint).
        # max_depth_pitch_deg: cap on the reference pitch angle.  15° is a good
        #   starting point; increase if the AUV still barely pitches; decrease if
        #   it dives too aggressively.
        # enable_facing_yaw_ref: (waypoint mode only) compute yaw from current
        #   position → waypoint direction instead of the stored waypoint heading.
        #   Eliminates steering when the waypoint is on the same heading line.
        # depth_pitch_horiz_threshold_m: don't add pitch when the horizontal
        #   distance to goal is below this (avoid large pitch when stationary at goal).
        self._node.declare_parameter("enable_depth_pitch_ref", False)
        self._enable_depth_pitch_ref = (
            self._node.get_parameter("enable_depth_pitch_ref")
            .get_parameter_value().bool_value
        )
        self._node.declare_parameter("max_depth_pitch_deg", 15.0)
        self._max_depth_pitch_deg = (
            self._node.get_parameter("max_depth_pitch_deg")
            .get_parameter_value().double_value
        )
        self._node.declare_parameter("enable_facing_yaw_ref", False)
        self._enable_facing_yaw_ref = (
            self._node.get_parameter("enable_facing_yaw_ref")
            .get_parameter_value().bool_value
        )
        self._node.declare_parameter("depth_pitch_horiz_threshold_m", 0.5)
        self._depth_pitch_horiz_threshold_m = (
            self._node.get_parameter("depth_pitch_horiz_threshold_m")
            .get_parameter_value().double_value
        )

        # ---- Depth-aware actuator references -----------------------------------
        #
        # Sign conventions established from SAM_casadi model analysis:
        #
        #   Stern (δ_s, x[15]):  C_T2C = Ry_code(δ_s), which uses the TRANSPOSED
        #     rotation matrix convention (NED).  Positive δ_s tilts the thruster
        #     downward at the stern, creating an upward torque → nose UP.
        #     Therefore: NEGATIVE δ_s = nose DOWN = diving.
        #     stern_ref = clip( -atan2(dz, d_horiz), ±7° )
        #
        #   LCG (x[14]):  LCG moves forward in body +x as u[1] increases.
        #     Forward mass shift → nose heavy → nose DOWN = diving.
        #     lcg_ref = clip( 50 + depth_lcg_gain * dz, [0,100] )
        #
        #   VBS (x[13]):  Higher % → more water → negative buoyancy → sinks.
        #     vbs_ref = clip( 50 + depth_vbs_gain * dz, [0,100] )
        #
        # The stern reference is the most impactful: its Q weight is 500, so if
        # ref[15] = 0 the MPC actively RESISTS using the stern for depth control.
        # Setting ref[15] to match the desired dive angle removes that barrier.
        #
        # LCG and VBS references have tiny weights (1e-4, 1e-5) so they barely
        # influence the optimizer directly, but they signal the intended state and
        # prevent accumulation of large reference-tracking errors.
        #
        # enable_depth_actuator_ref: master switch for all three refs.
        # depth_stern_gain: multiplier on the pitch angle for stern (1.0 = 1:1).
        # depth_lcg_gain: LCG units per metre depth error (default 5 → 1m=5%).
        # depth_vbs_gain: VBS units per metre depth error (default 5 → 1m=5%).
        # depth_traj_facing_yaw: for single-waypoint trajectories (traj_len==1),
        #   recompute yaw from current→goal direction instead of using the stored
        #   trajectory quaternion yaw.  Fixes lateral steering when the waypoint is
        #   straight ahead.  For multi-waypoint trajectories (turbo turns etc.)
        #   the stored yaw is always kept regardless of this flag.
        self._node.declare_parameter("enable_depth_actuator_ref", True)
        self._enable_depth_actuator_ref = (
            self._node.get_parameter("enable_depth_actuator_ref")
            .get_parameter_value().bool_value
        )
        self._node.declare_parameter("depth_stern_gain", 5.0)
        self._depth_stern_gain = (
            self._node.get_parameter("depth_stern_gain")
            .get_parameter_value().double_value
        )
        self._node.declare_parameter("depth_lcg_gain", 5.0)
        self._depth_lcg_gain = (
            self._node.get_parameter("depth_lcg_gain")
            .get_parameter_value().double_value
        )
        self._node.declare_parameter("depth_vbs_gain", 5.0)
        self._depth_vbs_gain = (
            self._node.get_parameter("depth_vbs_gain")
            .get_parameter_value().double_value
        )
        self._node.declare_parameter("depth_traj_facing_yaw", True)
        self._depth_traj_facing_yaw = (
            self._node.get_parameter("depth_traj_facing_yaw")
            .get_parameter_value().bool_value
        )

    def update(self):
        """
        This is where all the magic happens.
        """
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

        # Get the current states
        convert_state = True  # Flag to convert states
        self._current_state_in_odom = self._dive_sub.get_states()
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
        self.get_current_ref_array()

        # Update reference vector
        # NOTE: we use p bc. we have a custom cost function.
        # The parameter vector is [state_ref (nx), control_ref (nu), goal_pos (3)].
        # goal_pos enables the braking/speed-funnel constraint in the OCP.
        for stage in range(self.N_horizon):
            if self.ref.shape[0] < self.N_horizon and self.ref.shape[0] != 0:
                p = np.r_[self.ref[self.ref.shape[0] - 1, :], self._goal_pos]
            else:
                p = np.r_[self.ref[stage, :], self._goal_pos]
            self.ocp_solver.set(stage, "p", p)

        # Terminal stage must use the same parameterized reference convention.
        terminal_ref = (
            self.ref[self.ref.shape[0] - 1, :]
            if self.ref.shape[0] < self.N_horizon and self.ref.shape[0] != 0
            else self.ref[-1, :]
        )
        self.ocp_solver.set(self.N_horizon, "p", np.r_[terminal_ref, self._goal_pos])

        # With custom x_error() outputs, yref should stay zero (error target),
        # not the raw state reference.
        self.ocp_solver.set(self.N_horizon, "yref", np.zeros(self.nmpc.n_terminal_cost))

        # Set current state
        self.ocp_solver.set(0, "lbx", x_current)
        self.ocp_solver.set(0, "ubx", x_current)

        # solve ocp and get next control input
        start_time = time.time()
        status = self.ocp_solver.solve()
        end_time = time.time()

        # Get slack variables.
        # Slack vector layout (from control.py): [sbx_x, sbx_y, sbx_z, sh_brake]
        for stage in range(self.N_horizon):
            sl = self.ocp_solver.get(stage, "sl")
            if (sl > 1e-6).any():
                x_stage = self.ocp_solver.get(stage, "x")
                x_min, x_max = 0.0, 8.0
                y_min, y_max = -1.75, 1.75
                z_min, z_max = -0.5, 3.0
                pos_sl  = sl[:3] if len(sl) >= 3 else sl
                brake_sl = sl[3] if len(sl) >= 4 else 0.0
                s = (
                    f"Stage {stage}: soft constraint violated — "
                    f"pos_slack={np.round(pos_sl, 4)}, brake_slack={brake_sl:.4f}, "
                    f"pred_pos=({x_stage[0]:.3f}, {x_stage[1]:.3f}, {x_stage[2]:.3f}), "
                    f"surge={x_stage[7]:.3f} m/s, "
                    f"dist_to_goal={np.linalg.norm(x_stage[:3] - self._goal_pos):.3f} m"
                )
                self._logwarn(s)

        # simulate system:
        # NOTE: May be possible to use get(0, "x") to acquire the actual control input.
        self.simU = self.ocp_solver.get(0, "u")
        simX = self.ocp_solver.get(0, "x")

        self.pred_mpc = []
        for j in range(self.N_horizon + 1):
            self.pred_mpc.append(self.ocp_solver.get(j, "x"))

        # The integrator of the control signal is needed, since u is the control derivative.
        mpc_solution = self.integrator.simulate(x=x_current, u=self.simU)

        if mpc_solution is None:
            self._set_actuators_neutral()
        elif status != 0:
            self._set_actuators_neutral()
        else:
            self.set_publishers(mpc_solution)
            # Optional: log reference vs state and actual rudder/stern command (after solve)
            if self._print_ref_state_debug:
                self._print_ref_state_throttle += 1
                if self._print_ref_state_throttle >= 10:
                    self._print_ref_state_throttle = 0
                    self.print_reference_vs_state_debug(x_current, mpc_solution=mpc_solution)

        # Actuator state estimators: integrate commanded rates to track actuator states
        # without relying on echo-back topics (avoids the algebraic loop and callback
        # timing issues). All rates are in model convention; only published commands
        # are flipped via _map_actuator_commands / _rpm1_sign().
        x_k = self.ocp_solver.get(0, "x")
        x_k1 = self.ocp_solver.get(1, "x")
        u_k = self.ocp_solver.get(0, "u")

        v_stern = u_k[2]  # stern rate  (model convention, rad/s)
        v_rudder = u_k[3]  # rudder rate (model convention, rad/s)
        self.a_hat_stern = np.clip(self.a_hat_stern + self._dt * v_stern, -0.122173, 0.122173)
        self.a_hat_rudder = np.clip(self.a_hat_rudder + self._dt * v_rudder, -0.122173, 0.122173)

        rpm_rate_1 = u_k[4]  # RPM1 rate (model convention, RPM/s)
        rpm_rate_2 = u_k[5]  # RPM2 rate (model convention, RPM/s)
        self.rpm_hat_1 = np.clip(self.rpm_hat_1 + self._dt * rpm_rate_1, -500.0, 450.0)
        self.rpm_hat_2 = np.clip(self.rpm_hat_2 + self._dt * rpm_rate_2, -500.0, 450.0)

        # FIXME: Remove all the print statements here. They only should appear in the convenience node
        np.set_printoptions(precision=3)
        s = f"\nNMPC INFO\n"  # {self._dive_sub.current_idx}/{self.traj_len}:\n"
        s += f"NMPC solver status: {status}\n"

        # s += f"NMPC solve time: {(end_time - start_time)*1000:.1f} ms\n"
        # s += f"Traj. index: {self._dive_sub.current_idx}/{self.traj_len}:\n" if self.ref_is_traj else f""
        s += f"current state: x: {x_current[0]:.3f}, y: {x_current[1]:.3f}, z: {x_current[2]:.3f}\n"
        s += f"velocities: u: {x_current[7]:.3f}, v: {x_current[8]:.3f}, w: {x_current[9]:.3f}, p: {x_current[10]:.3f}, q: {x_current[11]:.3f}, r: {x_current[12]:.3f}\n"
        s += f"MPC pred: x: {simX[0]:.3f}, y: {simX[1]:.3f}, z: {simX[2]:.3f}\n"
        s += f"traj idx: {self.traj_index}/{self.traj_len}, ref: {self.ref[0, :7]}\n"
        s += f"vel ref: u: {self.ref[0,7]:.3f}, v: {self.ref[0,8]:.3f}, w: {self.ref[0,9]:.3f}\n"
        s += f"u_vbs = {mpc_solution[13]:.3f}, u_lcg = {mpc_solution[14]:.3f} \n "
        s += f"ref: vbs={self.ref[0,13]:.1f}% lcg={self.ref[0,14]:.1f}% stern_ref={np.rad2deg(self.ref[0,15]):.1f}°, rpm_ref1 = {self.ref[0,17]:.3f}, rpm_ref2 = {self.ref[0,18]:.3f}\n"

        u_stern, u_rudder = self._map_actuator_commands(mpc_solution)
        s += f"MPC Output: u_stern = {u_stern:.3f} u_rudder = {u_rudder:.3f} \n"
        #s += f"MPC state: u_stern = {simX[15]:.3f} u_rudder = {simX[16]:.3f} \n"
        s += f" u_rpm1 = {mpc_solution[17]:.3f} u_rpm2 = {mpc_solution[18]:.3f}\n"

        # Print all rates
        # s += f"rate: vbs: {self.simU[0]:.3f}"
        # s += f" lcg: {self.simU[1]:.3f}"
        # s += f" rate: stern: {self.simU[2]:.3f}"
        # s += f" rudder: {self.simU[3]} \n"
        # s += f" diff rudder: {(mpc_solution[16] - x_current[16])/self._dt} \n"
        # s += f" rpm1: {self.simU[4]:.3f}"
        # s += f" rpm2: {self.simU[5]:.3f}\n"

        self._loginfo(s)

        # Completion detection: when the trajectory has been fully traversed,
        # check that the vehicle is close to the final waypoint and nearly stopped.
        # The OCP speed-funnel constraint handles deceleration; we only gate the
        # COMPLETED signal here.
        if self.ref_is_traj and self.traj_index >= self.traj_len - 1:
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

        return


    def _rpm1_sign(self):
        """Sign for rpm1: +1 when flip_rpm1_command (sim), -1 for robot. Use for feedback and command."""
        return 1 if self.flip_rpm1_command else -1

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

    def compute_x_error_numpy(self, x, ref, terminal=True):
        """
        NumPy version of x_error() for runtime debugging.  The CasADi cost
        residual structure is:
          - Stage:    [pos_error(3), q_att_error(4), surge_vel_error(1), u(6)] = 14
          - Terminal: [pos_error(3), q_att_error(4), vel_error(6)]              = 13

        All components are always returned for debug logging regardless of
        whether they appear in the active cost residual.
        """
        ref = np.asarray(ref).flatten()
        ref_pad = np.zeros(19)
        ref_pad[: min(len(ref), 19)] = ref[:19]

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

        return {
            "pos_error": pos_error,
            "q_att_error": q_att_error,
            "q_error_wxyz": np.array([q_err_w, q_err_x, q_err_y, q_err_z]),
            "vel_error": vel_error,
        }

    def print_reference_vs_state_debug(self, x_current, mpc_solution=None):
        """
        Log current reference, current state (position, orientation, velocity),
        and the MPC state vector. Helps debug port/starboard (e.g. zigzag turbo turn).
        If mpc_solution is provided, logs the actual commanded stern/rudder (after flip).

        State layout: x[0:3] pos, x[3:7] quat [w,x,y,z], x[7:10] u,v,w,
                      x[10:13] p,q,r, x[15] stern, x[16] rudder.
        Ref layout:   ref[0:3] pos, ref[3:7] quat, ref[7:10] u,v,w if trajectory.
        """
        if self.ref is None or self.ref.shape[0] == 0:
            self._loginfo("REF_STATE_DBG: no reference set")
            return
        r = self.ref[0, :]
        yaw_ref = self._yaw_from_state_quat(r[3:7])
        yaw_cur = self._yaw_from_state_quat(x_current[3:7])
        # Same convention as get_current_ref_array: yaw_error = current - ref (wrap to [-pi,pi])
        yaw_err = np.arctan2(
            np.sin(yaw_cur - yaw_ref), np.cos(yaw_cur - yaw_ref)
        )
        to_turn = "STARBOARD" if yaw_err < 0 else "PORT"
        lines = [
            "========== REFERENCE vs STATE (debug) ==========",
            f"  REFERENCE (traj_idx={self.traj_index}/{self.traj_len}):",
            f"    pos   = ({r[0]:.3f}, {r[1]:.3f}, {r[2]:.3f})",
            f"    yaw   = {np.rad2deg(yaw_ref):.2f} deg  (quat w,x,y,z = {r[3]:.3f}, {r[4]:.3f}, {r[5]:.3f}, {r[6]:.3f})",
        ]
        if self.ref.shape[1] > 10:
            lines.append(
                f"    vel   = u,v,w = ({r[7]:.3f}, {r[8]:.3f}, {r[9]:.3f})  p,q,r = ({r[10]:.3f}, {r[11]:.3f}, {r[12]:.3f})"
            )
        if self.ref.shape[1] > 16:
            lines.append(f"    stern = {r[15]:.3f}  rudder = {r[16]:.3f}")
        lines.extend([
            "  STATE (current):",
            f"    pos   = ({x_current[0]:.3f}, {x_current[1]:.3f}, {x_current[2]:.3f})",
            f"    yaw   = {np.rad2deg(yaw_cur):.2f} deg  (quat w,x,y,z = {x_current[3]:.3f}, {x_current[4]:.3f}, {x_current[5]:.3f}, {x_current[6]:.3f})",
            f"    vel   = u,v,w = ({x_current[7]:.3f}, {x_current[8]:.3f}, {x_current[9]:.3f})  p,q,r = ({x_current[10]:.3f}, {x_current[11]:.3f}, {x_current[12]:.3f})",
            f"    stern = {x_current[15]:.3f}  rudder = {x_current[16]:.3f}",
            "  ERROR (simple yaw):",
            f"    yaw_error = {np.rad2deg(yaw_err):.2f} deg  (cur - ref)",
            f"    To reach ref heading: turn {to_turn}  (positive yaw_error => turn PORT, negative => turn STARBOARD in FRD)",
        ])

        # MPC error: same as x_error() in the cost (NumPy so we can print it)
        err = self.compute_x_error_numpy(x_current, r, terminal=True)
        qe = err["q_error_wxyz"]
        angle_total_rad = 2.0 * np.arccos(np.clip(qe[0], -1.0, 1.0))
        yaw_from_q_err_rad = 2.0 * np.arctan2(qe[3], qe[0])
        lines.extend([
            "  MPC ERROR (x_error, as in cost):",
            f"    pos_error = ({err['pos_error'][0]:.3f}, {err['pos_error'][1]:.3f}, {err['pos_error'][2]:.3f})",
            f"    q_att_error = (1-w,x,y,z) = ({err['q_att_error'][0]:.3f}, {err['q_att_error'][1]:.3f}, {err['q_att_error'][2]:.3f}, {err['q_att_error'][3]:.3f})",
            f"    q_error (w,x,y,z) = ({qe[0]:.3f}, {qe[1]:.3f}, {qe[2]:.3f}, {qe[3]:.3f})  => angle = {np.rad2deg(angle_total_rad):.2f} deg  yaw_component = {np.rad2deg(yaw_from_q_err_rad):.2f} deg",
            f"    vel_error = u,v,w = ({err['vel_error'][0]:.3f}, {err['vel_error'][1]:.3f}, {err['vel_error'][2]:.3f})  p,q,r = ({err['vel_error'][3]:.3f}, {err['vel_error'][4]:.3f}, {err['vel_error'][5]:.3f})",
        ])
        lines.append(
            "  (Simple yaw_error and MPC yaw_component can have opposite signs (euler vs quat); "
            "for steering direction the sign matters—the optimizer uses it to choose rudder sign.)"
        )
        # Steering check: SAM_casadi is NED/FRD, positive rudder => starboard turn.
        # A "wrong" rudder sign can still appear in edge cases (large heading error, quat hemisphere
        # flip near 180°, or solver picking long way); the WARNING below flags when that happens.
        lines.extend([
            "  STEERING CHECK (NED/FRD: +rudder => starboard):",
            f"    Desired turn: {to_turn}  =>  expect {'positive' if to_turn == 'STARBOARD' else 'negative'} rudder from MPC.",
            f"    flip_rudder_command = {self.flip_rudder_command}  (if vehicle turns wrong way, set to True in launch/code).",
        ])
        if mpc_solution is not None:
            cmd_stern, cmd_rudder = self._map_actuator_commands(mpc_solution)
            lines.append(
                f"    Actual commanded: stern = {cmd_stern:.4f} rad ({np.rad2deg(cmd_stern):.2f} deg), rudder = {cmd_rudder:.4f} rad ({np.rad2deg(cmd_rudder):.2f} deg)."
            )
            # Rudder sign opposite to "desired turn" can be: long-way/quat edge case, or nonholonomic
            # (MPC may command a turn that looks wrong in one snapshot to set up the maneuver), or
            # due to using only the current waypoint so the horizon has no "next" direction.
            expect_pos_rudder = to_turn == "STARBOARD"
            actual_pos_rudder = cmd_rudder > 0
            if expect_pos_rudder != actual_pos_rudder and np.abs(yaw_err) > np.deg2rad(15):
                lines.append(
                    "    >>> WARNING: rudder sign opposite to desired turn (can be nonholonomic setup, "
                    "single-waypoint ref, or long-way/quat edge case)."
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

            # Augment the trajectory and control input reference
            Uref = np.zeros(
                (self.trajectory.shape[0], self.nu)
            )  # Derivative reference - set to 0 to penalize large rate of change
            self.trajectory = np.concatenate((self.trajectory, Uref), axis=1)

            # Store the final waypoint position for the OCP braking/speed-funnel constraint
            self._goal_pos = self.trajectory[-1, :3].copy()

            # Reset completion debounce for the new trajectory.
            self._completion_debounce_count = 0

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

    def convert_enu_to_ned(self, enu_msg, convert_state=True):
        """
        If convert_state, it converts an odometry message from ENU to NED

        """
        ned_odometry = Odometry()
        ned_odometry.header.frame_id = "/mocap"  # state_msg.header.frame_id# + "_conv"
        ned_odometry.header.stamp = enu_msg.header.stamp
        if convert_state:
            ned_odometry.pose.pose.position.x = enu_msg.pose.pose.position.y
            ned_odometry.pose.pose.position.y = enu_msg.pose.pose.position.x
            ned_odometry.pose.pose.position.z = -enu_msg.pose.pose.position.z
            ned_odometry.pose.pose.orientation = enu_msg.pose.pose.orientation

            quat = self.quat_enu_to_ned(
                [
                    enu_msg.pose.pose.orientation.w,
                    enu_msg.pose.pose.orientation.x,
                    enu_msg.pose.pose.orientation.y,
                    enu_msg.pose.pose.orientation.z,
                ]
            )
            ned_odometry.pose.pose.orientation.x = quat[1]
            ned_odometry.pose.pose.orientation.y = quat[2]
            ned_odometry.pose.pose.orientation.z = quat[3]
            ned_odometry.pose.pose.orientation.w = quat[0]

            ned_odometry.twist.twist.linear.x = enu_msg.twist.twist.linear.y
            ned_odometry.twist.twist.linear.y = enu_msg.twist.twist.linear.x
            ned_odometry.twist.twist.linear.z = -enu_msg.twist.twist.linear.z
            ned_odometry.twist.twist.angular.x = enu_msg.twist.twist.angular.y
            ned_odometry.twist.twist.angular.y = enu_msg.twist.twist.angular.x
            ned_odometry.twist.twist.angular.z = -enu_msg.twist.twist.angular.z

        else:
            ned_odometry = enu_msg

        return ned_odometry

    def quat_enu_to_ned(self, quat_enu):
        """
        Transform quaternion from ENU to NED.
        q = [q0, q1, q2, q3], where q0 is the scalar part.
        """

        q = quat_enu

        q_ned = (
            1
            / np.sqrt(2)
            * np.array([q[0] + q[3], q[1] + q[2], q[1] - q[2], q[0] - q[3]])
        )
        q_ned /= np.linalg.norm(q_ned)

        return q_ned

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

    def get_state_array( self, state_msg, control_msg, is_init_state=False, is_trajectory=False):
        """
        Merges states and controls into numpy array and returns the state of
        the controller as the state vector x (numpy array)

        convert_state: state_msg is in ENU, x will be in NED

        Note: The MPC wants the quaternion scalar part first, [w, x, y, z]!
        Also note: For running on SAM, the sign on the thrust vectoring has to
            be switched due to different ways of viewing the thrust vecotring
            angle in the model and on SAM.
        """
        x = np.zeros(19)

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

        # In waypoint (non-trajectory) mode the estimator starts at 0 by definition,
        # so no special init branch is needed. The tiny noise below is kept only for
        # trajectory mode to avoid a numerical zero-RPM singularity on the very first
        # step before the estimator has propagated.
        if is_init_state and not is_trajectory:
            x[17] = 1e-6
            x[18] = 1e-6

        return x

    def get_wp_array(self, waypoint):

        ref = np.zeros(self.nx + self.nu)

        ref[0] = waypoint.pose.pose.position.x
        ref[1] = waypoint.pose.pose.position.y
        ref[2] = waypoint.pose.pose.position.z
        ref[3] = waypoint.pose.pose.orientation.w
        ref[4] = waypoint.pose.pose.orientation.x
        ref[5] = waypoint.pose.pose.orientation.y
        ref[6] = waypoint.pose.pose.orientation.z

        ref[7] = 0.2  # nominal cruise speed — encourages forward motion

        # Neutral actuator reference for VBS and LCG. Rest is 0
        ref[13] = 50
        ref[14] = 50

        return ref

    def initialize_mpc(self):
        """
        Seed the solver with an initial guess that moves toward the first
        target instead of the default "stay still at current position".

        For trajectory mode the target is the first trajectory waypoint;
        for single-waypoint mode it is the waypoint position.  Position is
        linearly interpolated across the horizon so the solver starts from
        a rough "drive there" plan rather than a zero-motion guess.
        """
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

        for stage in range(self.N_horizon + 1):
            x_init = x0.copy()
            if target_pos is not None:
                t = stage / self.N_horizon
                x_init[:3] = x0[:3] + t * (target_pos - x0[:3])
            self.ocp_solver.set(stage, "x", x_init)

        for stage in range(self.N_horizon):
            self.ocp_solver.set(stage, "u", np.zeros(self.nu))

        self._initialized = True

    def get_current_ref_array(self):
        """
        Populate reference array depending on whether we have a trajectory or waypoint.

        For trajectories:
        - Waypoint progression: we advance traj_index only when BOTH position is within
          traj_d_tolerance_m of current waypoint AND heading is within traj_yaw_tolerance_deg.
          Tight yaw_tolerance with nonholonomic dynamics can cause back-and-forth (vehicle
          can't turn on the spot); loosening it may help but can advance before heading is aligned.
        - Horizon filling (controlled by horizon_max_waypoints + horizon_current_wp_ratio):
            max_wp=0: full remaining trajectory (up to N_horizon), padded with terminal WP.
            max_wp=1: current WP repeated across the horizon.
            max_wp=N: next N WPs sequentially, padded with the last.
          When horizon_current_wp_ratio > 0 and >= 2 WPs remain, the horizon is split into
          [current WP * ratio | next WP * (1-ratio)] instead of sequential packing.
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
            # Get current position
            x_current = self._current_state.pose.pose.position.x
            y_current = self._current_state.pose.pose.position.y
            z_current = self._current_state.pose.pose.position.z
            
            # ---- Sequential trajectory tracking ------------------------------------
            # Advance traj_index when the vehicle is close enough to the current
            # waypoint.  The planner provides the full path including orientation
            # guidance, so we never skip ahead -- just follow in order.
            # The OCP speed-funnel constraint handles deceleration near the goal.
            if self.traj_index < self.traj_len - 1:
                d_current = np.sqrt(
                    (x_current - self.trajectory[self.traj_index, 0]) ** 2
                    + (y_current - self.trajectory[self.traj_index, 1]) ** 2
                    + (z_current - self.trajectory[self.traj_index, 2]) ** 2
                )
                if d_current < self._traj_d_tolerance:
                    self.traj_index += 1

            # ---- Fill the MPC reference horizon ---------------------------------
            max_wp = self._horizon_max_waypoints
            ratio = self._horizon_current_wp_ratio
            remaining = self.traj_len - self.traj_index

            if ratio > 0 and remaining >= 2:
                split = max(1, int(ratio * self.N_horizon))
                self.ref = np.zeros((self.N_horizon, self.nx + self.nu))
                current_wp = self.trajectory[self.traj_index, :].copy()
                next_idx = min(self.traj_index + 1, self.traj_len - 1)
                next_wp = self.trajectory[next_idx, :].copy()
                self.ref[:split, :] = current_wp
                self.ref[split:, :] = next_wp
            else:
                n_take = min(remaining, self.N_horizon)
                if max_wp > 0:
                    n_take = min(max_wp, n_take)

                segment = self.trajectory[
                    self.traj_index : self.traj_index + n_take, :
                ].copy()
                if n_take < self.N_horizon:
                    pad_count = self.N_horizon - n_take
                    pad_rows = np.tile(segment[-1, :], (pad_count, 1))
                    self.ref = np.concatenate((segment, pad_rows), axis=0)
                else:
                    self.ref = segment

            # ---- Depth-aware actuator and quaternion references ------------------
            x_pos = self._current_state.pose.pose.position.x
            y_pos = self._current_state.pose.pose.position.y
            z_pos = self._current_state.pose.pose.position.z
            x_final = float(self.trajectory[-1, 0])
            y_final = float(self.trajectory[-1, 1])
            z_final = float(self.trajectory[-1, 2])

            if self._enable_depth_actuator_ref:
                vbs_ref, lcg_ref, stern_ref = self._depth_actuation_refs(
                    x_pos, y_pos, z_pos, x_final, y_final, z_final
                )
                self.ref[:, 13] = vbs_ref
                self.ref[:, 14] = lcg_ref
                self.ref[:, 15] = stern_ref
            else:
                self.ref[:, 13] = 50  # VBS neutral
                self.ref[:, 14] = 50  # LCG neutral

            if self._enable_depth_pitch_ref:
                use_facing_yaw = (
                    self.traj_len == 1 and self._depth_traj_facing_yaw
                )
                for i in range(self.ref.shape[0]):
                    base_q = self.ref[i, 3:7].copy()
                    q_new = self._compute_depth_aware_quat(
                        x_pos, y_pos, z_pos,
                        x_final, y_final, z_final,
                        base_quat_wxyz=base_q,
                        facing_yaw=use_facing_yaw,
                    )
                    self.ref[i, 3:7] = q_new

            self._enforce_reference_quaternion_continuity(q_current_wxyz)

            # Update the speed-funnel goal so the OCP sees remaining *path*
            # distance rather than Euclidean distance to the final waypoint.
            # For curved trajectories (circles, turbo turns) the Euclidean
            # shortcut can be much shorter, causing premature braking.
            self._update_goal_pos_from_arc_length(
                np.array([x_pos, y_pos, z_pos])
            )
            return

        else: # waypoint mode
            self.ref = np.zeros((self.N_horizon, (self.nx + self.nu)))
            self.ref[:, :] = self.wp_array

            # Depth-aware + facing-yaw quaternion reference for waypoint mode.
            #
            # The stored waypoint quaternion may point in a direction unrelated to
            # the current approach direction, causing (a) unnecessary steering when
            # the waypoint is on the same heading line, and (b) a flat pitch that
            # resists diving when the target has a different depth.
            #
            # Replace it with a quaternion whose:
            #   • yaw   = direction from current position to waypoint (facing_yaw=True)
            #             → MPC heads straight to the waypoint, no phantom rudder
            #   • pitch = -atan2(dz, d_horiz)  (negative = nose-down in FRD/NED)
            #             → MPC starts pitching forward early to reach target depth
            if self._enable_depth_pitch_ref or self._enable_facing_yaw_ref:
                x_pos = self._current_state.pose.pose.position.x
                y_pos = self._current_state.pose.pose.position.y
                z_pos = self._current_state.pose.pose.position.z
                x_goal = self.waypoint.pose.pose.position.x
                y_goal = self.waypoint.pose.pose.position.y
                z_goal = self.waypoint.pose.pose.position.z
                base_q = np.array([
                    self.waypoint.pose.pose.orientation.w,
                    self.waypoint.pose.pose.orientation.x,
                    self.waypoint.pose.pose.orientation.y,
                    self.waypoint.pose.pose.orientation.z,
                ])
                q_ref = self._compute_depth_aware_quat(
                    x_pos, y_pos, z_pos,
                    x_goal, y_goal, z_goal,
                    base_quat_wxyz=base_q,
                    facing_yaw=self._enable_facing_yaw_ref,
                )
                # Apply the depth-aware quaternion across the whole horizon.
                self.ref[:, 3:7] = q_ref

            self._enforce_reference_quaternion_continuity(q_current_wxyz)
            return
            
    def _yaw_from_odometry(self):
        """Extract current yaw (rad, FRD/NED convention) from the converted state."""
        q_current = [
            self._current_state.pose.pose.orientation.x,
            self._current_state.pose.pose.orientation.y,
            self._current_state.pose.pose.orientation.z,
            self._current_state.pose.pose.orientation.w,
        ]
        _, _, yaw = R.from_quat(q_current).as_euler("xyz")
        return yaw

    def compute_yaw_error(self):
        """Yaw error (rad, wrapped to [-π, π]) against the CURRENT traj_index waypoint.
        Used during normal tracking to decide waypoint progression."""
        yaw_current = self._yaw_from_odometry()
        q_ref_xyzw = [
            self.trajectory[self.traj_index, 4],
            self.trajectory[self.traj_index, 5],
            self.trajectory[self.traj_index, 6],
            self.trajectory[self.traj_index, 3],
        ]
        _, _, yaw_ref = R.from_quat(q_ref_xyzw).as_euler("xyz")
        return np.arctan2(np.sin(yaw_current - yaw_ref), np.cos(yaw_current - yaw_ref))

    def _update_goal_pos_from_arc_length(self, p_current):
        """Set _goal_pos so the OCP speed funnel sees remaining *path* distance.

        The OCP braking constraint computes Euclidean distance from the
        predicted state to _goal_pos.  For curved trajectories (circles,
        turbo turns) the straight-line shortcut to the final waypoint can be
        much shorter than the actual remaining path, causing the vehicle to
        brake prematurely.

        Fix: place _goal_pos along the line from p_current toward the final
        waypoint, but at a distance equal to the remaining arc length.  When
        the path is straight, arc length == Euclidean and nothing changes.
        """
        final_pos = self.trajectory[-1, :3]
        euclidean = np.linalg.norm(p_current - final_pos)

        # Remaining arc length: current pos -> current WP -> ... -> final WP
        arc = np.linalg.norm(
            self.trajectory[self.traj_index, :3] - p_current
        )
        for i in range(self.traj_index, self.traj_len - 1):
            arc += np.linalg.norm(
                self.trajectory[i + 1, :3] - self.trajectory[i, :3]
            )

        if arc > euclidean and euclidean > 1e-3:
            direction = (final_pos - p_current) / euclidean
            self._goal_pos = p_current + direction * arc
        else:
            self._goal_pos = final_pos.copy()

    def _compute_depth_aware_quat(
        self,
        x_pos, y_pos, z_pos,
        x_goal, y_goal, z_goal,
        base_quat_wxyz=None,
        facing_yaw=True,
    ):
        """Compute a reference quaternion with depth-proportional pitch and optional facing yaw.

        In FRD/NED convention:
          - Positive z  = deeper (downward)
          - Negative pitch = nose DOWN → vehicle dives while thrusting forward
          - Positive yaw   = clockwise from above (turn starboard)

        Args:
            x_pos, y_pos, z_pos: current vehicle position (NED/FRD)
            x_goal, y_goal, z_goal: goal position (NED/FRD)
            base_quat_wxyz: existing reference quaternion [w,x,y,z].
                If facing_yaw=False the stored yaw and roll are preserved so that
                turbo-turn trajectories keep their lateral guidance.
                If None, roll=0, yaw=0 are used.
            facing_yaw: when True the yaw is set to face the goal (fixes steering
                when the waypoint is on the same line as the current heading).
                When False the yaw from base_quat is kept (trajectory mode).

        Returns:
            q_wxyz (np.ndarray[4]): reference quaternion [w, x, y, z]
        """
        dx = x_goal - x_pos
        dy = y_goal - y_pos
        dz = z_goal - z_pos
        d_horiz = np.sqrt(dx**2 + dy**2)

        # Extract roll and yaw from the stored quaternion (if any).
        if base_quat_wxyz is not None and np.linalg.norm(base_quat_wxyz) > 0.5:
            r_base = R.from_quat(
                [base_quat_wxyz[1], base_quat_wxyz[2],
                 base_quat_wxyz[3], base_quat_wxyz[0]]
            )
            roll_stored, _, yaw_stored = r_base.as_euler("xyz")
        else:
            roll_stored = 0.0
            yaw_stored = 0.0

        # Yaw: optionally override with direction-to-goal (waypoint mode).
        # Threshold: don't recompute yaw if almost at the horizontal goal to avoid
        # numerical noise when dx≈0, dy≈0.
        if facing_yaw and d_horiz > self._depth_pitch_horiz_threshold_m:
            yaw = np.arctan2(dy, dx)   # NED: atan2(East, North)
        else:
            yaw = yaw_stored

        # Pitch: nose-down angle proportional to (depth-to-go / horizontal-to-go).
        # Negative pitch in FRD = nose tilts downward = vehicle dives.
        max_pitch = np.deg2rad(self._max_depth_pitch_deg)
        if d_horiz > self._depth_pitch_horiz_threshold_m:
            # atan2(dz, d_horiz): positive when goal is deeper (dz>0), giving a
            # negative (nose-down) pitch reference.
            pitch = np.clip(-np.arctan2(dz, d_horiz), -max_pitch, max_pitch)
        else:
            pitch = 0.0

        # Reconstruct quaternion: intrinsic ZYX ≡ extrinsic XYZ (aerospace standard).
        q_xyzw = R.from_euler("xyz", [roll_stored, pitch, yaw]).as_quat()
        # Scipy returns [x, y, z, w]; convert to [w, x, y, z].
        return np.array([q_xyzw[3], q_xyzw[0], q_xyzw[1], q_xyzw[2]])

    def _depth_actuation_refs(self, x_pos, y_pos, z_pos, x_goal, y_goal, z_goal):
        """Compute depth-aware references for VBS, LCG, and stern angle.

        Sign conventions (NED/FRD, derived from SAM_casadi model):

          Stern (δ_s, x[15]):
            C_T2C uses a transposed-NED Ry matrix, so positive δ_s tilts thrust
            DOWNWARD at stern → upward moment → nose UP.
            For diving (nose DOWN): δ_s must be NEGATIVE.
            stern_ref = clip( depth_stern_gain * (-atan2(dz, d_horiz)), ±7° )

          LCG (x[14], 0–100 %):
            Higher % moves the battery pack forward (+x body) → nose-heavy → nose DOWN.
            For diving: LCG_ref > 50.
            lcg_ref = clip( 50 + depth_lcg_gain * dz, [0,100] )

          VBS (x[13], 0–100 %):
            Higher % = more water in tank = heavier = sinks.
            For diving: VBS_ref > 50.
            vbs_ref = clip( 50 + depth_vbs_gain * dz, [0,100] )

        In all formulae dz = z_goal - z_pos, positive = goal is deeper (NED).

        Args:
            x/y/z_pos:  current vehicle position in NED/FRD
            x/y/z_goal: goal position in NED/FRD

        Returns:
            (vbs_ref, lcg_ref, stern_ref)  — scalar floats
        """
        dz = z_goal - z_pos
        dx = x_goal - x_pos
        dy = y_goal - y_pos
        d_horiz = np.sqrt(dx**2 + dy**2)

        max_stern = np.deg2rad(7)  # hardware limit

        if d_horiz > self._depth_pitch_horiz_threshold_m:
            # Pitch angle toward goal depth (negative = nose down = diving in FRD).
            # Multiply by gain so the user can scale aggressiveness (1.0 = 1:1 mapping
            # to dive angle; increase above 1 for a more aggressive stern command).
            dive_angle = np.arctan2(dz, d_horiz)   # positive when goal is deeper
            stern_ref = float(
                np.clip(-self._depth_stern_gain * dive_angle, -max_stern, max_stern)
            )
        else:
            # At or past the horizontal goal — return to level
            stern_ref = 0.0

        vbs_ref = float(np.clip(50.0 + self._depth_vbs_gain * dz, 0.0, 100.0))
        lcg_ref = float(np.clip(50.0 + self._depth_lcg_gain * dz, 0.0, 100.0))

        return vbs_ref, lcg_ref, stern_ref

    def _enforce_reference_quaternion_continuity(self, q_current_wxyz):
        """
        We do this here instead of in the OCP, basically
        making sure that the quaternion error is always positive.
        """
        if self.ref is None or self.ref.shape[0] == 0:
            return

        prev_q = self._normalize_quat_wxyz(q_current_wxyz)

        # DEBUG: Check initial alignment
        q_ref_orig = self.ref[0, 3:7].copy()
        dot_before = np.dot(prev_q, q_ref_orig)

        for i in range(self.ref.shape[0]):
            q_i = self.ref[i, 3:7]
            q_i = self._align_quat_hemisphere(q_i, prev_q)
            self.ref[i, 3:7] = q_i
            prev_q = q_i

        # DEBUG: Log if first reference was flipped
        #dot_after = np.dot(self._normalize_quat_wxyz(q_current_wxyz), self.ref[0, 3:7])
        #if abs(dot_before) < 0.9 or abs(dot_after) < 0.9:
        #    self._logwarn(
        #        f"Quat continuity: dot_before={dot_before:.3f} dot_after={dot_after:.3f} (flipped={dot_before < 0})"
        #    )

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

    def set_publishers(self, mpc_solution):
        """
        Set the corresponding publishers for the actuators and convenience topics
        """
        # Assign the calculated control signal to actuators
        # NOTE: We change the thrust vectoring sign bc. the MPC computes it
        # w.r.t. the C frame, while on SAM the sign is w.r.t the yaw angle of
        # SAM
        # Update on that note: I have my doubts about it. Looking at it again,
        # and it seems we don't need to flip the sign after all. Unclear where
        # it came from.
        u_vbs = mpc_solution[13]
        u_lcg = mpc_solution[14]
        u_stern, u_rudder = self._map_actuator_commands(mpc_solution)
        u_rpm1 = self._rpm1_sign() * mpc_solution[17]
        u_rpm2 = mpc_solution[18]

        # Publish the control input
        self._dive_pub.set_vbs(u_vbs)
        self._dive_pub.set_lcg(u_lcg)
        self._dive_pub.set_thrust_vector(u_rudder, u_stern)
        self._dive_pub.set_rpm(u_rpm1, u_rpm2)

        # Set control input (For convenience topics)
        self._input = ControlInput()
        self._input.vbs = u_vbs
        self._input.lcg = u_lcg
        self._input.thrustervertical = u_stern
        self._input.thrusterhorizontal = u_rudder
        self._input.thrusterrpm1 = float(u_rpm1)
        self._input.thrusterrpm2 = float(u_rpm2)

        # Convenience Topics
        # FIXME: This if statement is weird.
        if self.ref is not None:
            # self._ref = ControlReference()
            # self._ref.x = self.ref[0, 0]
            # self._ref.y = self.ref[0, 1]
            # self._ref.z = self.ref[0, 2]

            # r = R.from_quat([self.ref[0, 4],  # x
            #                 self.ref[0, 5],  # y
            #                 self.ref[0, 6],  # z
            #                 self.ref[0, 3]])  # w
            # euler_angles = r.as_euler('xyz', degrees=False)
            # self._ref.roll = euler_angles[0]
            # self._ref.pitch = euler_angles[1]
            # self._ref.yaw = euler_angles[2]

            # self._ref.qx = self.ref[0, 4]
            # self._ref.qy = self.ref[0, 5]
            # self._ref.qz = self.ref[0, 6]
            # self._ref.qw = self.ref[0, 3]

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

    def get_ref_input(self):
        return self._control_ref
