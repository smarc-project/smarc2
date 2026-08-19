import numpy   as np
import control as ct 

import rclpy
from rclpy.node         import Node
from rclpy.executors    import MultiThreadedExecutor
from rclpy.qos          import QoSProfile, ReliabilityPolicy, QoSDurabilityPolicy
from rcl_interfaces.msg import ParameterDescriptor, ParameterType

from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg   import PoseStamped, TwistStamped, Vector3Stamped
from nav_msgs.msg        import Odometry
from sensor_msgs.msg     import JointState
from std_msgs.msg        import Float64MultiArray


from smarc_action_base.gentler_action_server import GentlerActionServer

from alars.alars_common import DroneState
from alars.speed_names import SpeedNames

from dji_msgs.msg import Topics as DJITopics
from dji_msgs.msg import Links  as DJILinks
from smarc_msgs.msg import Topics as SmarcTopics

import traceback
import time

from sway_controller import PathParametrizer, ZVD, LQR

G = 9.81

class MoveToDampedAction():
    def __init__(self, node:Node):
        self._node:Node = node 

        self._get_node_parameters()
        self._create_publishers()

        self.BASE_FLAT_FRAME : str = self._robot_name + '/' + DJILinks.BASE_FLAT
        self._drone_state = DroneState(node, self._robot_name)

        
        self._lqr:None|LQR = None
        self._lqr_stabilize:None|LQR = None
        self._swing_state:None|JointState = None
        self._pendulum_params:None|tuple = None
        self._drone_velocity_base_flat:None|np.ndarray = None
        self._create_subscriptions()

        self._phase:str = 'MOVING'

        self._goal_in_map:None|PoseStamped = None
        self._distance_from_goal:None|float = None

        self._as = GentlerActionServer(
                    node,
                    'alars_move_to_damped',
                    self._on_goal_received,
                    self._on_cancel_received,
                    self._prepare_loop,
                    self._loop_inner,
                    self._give_feedback,
                    loop_frequency = 50
                )        

    def _build_transfer_function(self, path:str):
        d = np.load(path)

        self._tf_x = ct.tf(
        d['b__FLU_axes_0__to__FLUvelocity_ground_fused_x'],
        d['a__FLU_axes_0__to__FLUvelocity_ground_fused_x']
        )
        self._tf_y = ct.tf(
            d['b__FLU_axes_1__to__FLUvelocity_ground_fused_y'],
            d['a__FLU_axes_1__to__FLUvelocity_ground_fused_y']
        )
        self._tf_z = ct.tf(
            d['b__FLU_axes_2__to__FLUvelocity_ground_fused_z'],
            d['a__FLU_axes_2__to__FLUvelocity_ground_fused_z']
        )

    def _declare_parameters(self):
        int_desc = ParameterDescriptor(type=ParameterType.PARAMETER_INTEGER)
        double_desc = ParameterDescriptor(type=ParameterType.PARAMETER_DOUBLE)
        string_desc = ParameterDescriptor(type=ParameterType.PARAMETER_STRING)
        bool_desc = ParameterDescriptor(type=ParameterType.PARAMETER_BOOL)

        node = self._node
        node.declare_parameter('robot_name', 'M350', string_desc)
        node.declare_parameter('continuous_model_path', '', string_desc)
        node.declare_parameter('discrete_model_path', '', string_desc)
        node.declare_parameter('goal_tolerance', 0.2, double_desc)
        node.declare_parameter('max_speed', 1.0, double_desc)
        node.declare_parameter('max_acceleration', 2.0, double_desc)
        node.declare_parameter('settle_extra', 20.0, double_desc)
        node.declare_parameter('speeds', [0.5, 1.0, 2.0])
        node.declare_parameter('altitude_tolerance', 0.5, double_desc)
        
        
        node.declare_parameter('enable_lqg', True, bool_desc)
        
        node.declare_parameter('lqg_rho', 10.0, double_desc)
        node.declare_parameter('lqg_theta_max', 0.3, double_desc)
        node.declare_parameter('lqg_position_max', 0.3, double_desc)
        
        node.declare_parameter('max_estimate_age', 0.5, double_desc)
        
        node.declare_parameter('max_trim_speed', 0.5, double_desc)
        node.declare_parameter('max_theta_for_lqg', 0.35, double_desc)

        node.declare_parameter('stabilize_before_mission', True, bool_desc)
        node.declare_parameter('stabilize_theta_tol', 0.02, double_desc)    # rad
        node.declare_parameter('stabilize_omega_tol', 0.05, double_desc)    # rad/s
        node.declare_parameter('stabilize_settle_time', 1.0, double_desc)   # s within tol
        node.declare_parameter('stabilize_timeout', 45.0, double_desc)      # s
        node.declare_parameter('stabilize_rho', 2.0, double_desc)
        node.declare_parameter('stabilize_theta_max', 0.3, double_desc)     # rad
        node.declare_parameter('stabilize_position_max', 2.0, double_desc)  # m


    def _get_node_parameters(self):
        self._declare_parameters()

        self._robot_name = self._node.get_parameter('robot_name').get_parameter_value().string_value
        _continuous_model_path = self._node.get_parameter('continuous_model_path').get_parameter_value().string_value
        _discrete_model_path = self._node.get_parameter('discrete_model_path').get_parameter_value().string_value

        self._build_transfer_function(_continuous_model_path)

        num_array_x = self._tf_x.num[0][0]  
        den_array_x = self._tf_x.den[0][0]
        self._k_x = num_array_x[0]
        self._tau_x = den_array_x[1]

        num_array_y = self._tf_y.num[0][0]  
        den_array_y = self._tf_y.den[0][0]
        self._k_y = num_array_y[0]
        self._tau_y = den_array_y[1]

        num_array_z = self._tf_z.num[0][0]  
        den_array_z = self._tf_z.den[0][0]
        self._k_z = num_array_z[0]
        self._tau_z = den_array_z[1]

        self._default_goal_tolerance = self._node.get_parameter('goal_tolerance').get_parameter_value().double_value
        self._max_speed = self._node.get_parameter('max_speed').get_parameter_value().double_value
        self._max_acceleration = self._node.get_parameter('max_acceleration').get_parameter_value().double_value
        self._settle_extra = self._node.get_parameter('settle_extra').get_parameter_value().double_value


        self._enable_lqg = self._node.get_parameter('enable_lqg').get_parameter_value().bool_value
        self._lqg_rho = self._node.get_parameter('lqg_rho').get_parameter_value().double_value
        self._lqg_theta_max = self._node.get_parameter('lqg_theta_max').get_parameter_value().double_value
        self._lqg_position_max = self._node.get_parameter('lqg_position_max').get_parameter_value().double_value
        self._max_estimate_age = self._node.get_parameter('max_estimate_age').get_parameter_value().double_value
        self._max_trim_speed = self._node.get_parameter('max_trim_speed').get_parameter_value().double_value
        self._max_theta_for_lqg = self._node.get_parameter('max_theta_for_lqg').get_parameter_value().double_value

        self._stabilize_before_mission = self._node.get_parameter('stabilize_before_mission').get_parameter_value().bool_value
        self._stabilize_theta_tol = self._node.get_parameter('stabilize_theta_tol').get_parameter_value().double_value
        self._stabilize_omega_tol = self._node.get_parameter('stabilize_omega_tol').get_parameter_value().double_value
        self._stabilize_settle_time = self._node.get_parameter('stabilize_settle_time').get_parameter_value().double_value
        self._stabilize_timeout = self._node.get_parameter('stabilize_timeout').get_parameter_value().double_value
        self._stabilize_rho = self._node.get_parameter('stabilize_rho').get_parameter_value().double_value
        self._stabilize_theta_max = self._node.get_parameter('stabilize_theta_max').get_parameter_value().double_value
        self._stabilize_position_max = self._node.get_parameter('stabilize_position_max').get_parameter_value().double_value

    def _resolve_goal_speed(self, goal_request: dict) -> float:
        """waraps-style speed: a name ('slow'/'standard'/'fast') or a number.

        Note this also becomes v_max for the LQR, since Q and R are both
        normalised by it - a 'fast' goal is therefore flown with a
        proportionally different trim authority, not just a higher cap.
        """
        speeds = self._node.get_parameter('speeds').get_parameter_value().double_array_value
        table = {SpeedNames.SLOW: speeds[0],
                 SpeedNames.STANDARD: speeds[1],
                 SpeedNames.FAST: speeds[2]}

        speed_str = goal_request.get('speed', 'standard')
        try:
            return float(speed_str)
        except (TypeError, ValueError):
            try:
                return table[SpeedNames[str(speed_str).upper()]]
            except KeyError:
                self.log(f"Unknown speed name: '{speed_str}', defaulting to STANDARD")
                return table[SpeedNames.STANDARD]

    def _refresh_tuning_parameters(self):
        g = lambda n: self._node.get_parameter(n).get_parameter_value()
        self._enable_lqg = g('enable_lqg').bool_value
        self._lqg_rho = g('lqg_rho').double_value
        self._lqg_theta_max = g('lqg_theta_max').double_value
        self._lqg_position_max = g('lqg_position_max').double_value
        self._max_trim_speed = g('max_trim_speed').double_value
        self._max_theta_for_lqg = g('max_theta_for_lqg').double_value
        self._stabilize_rho = g('stabilize_rho').double_value
        self._stabilize_theta_max = g('stabilize_theta_max').double_value
        self._stabilize_position_max = g('stabilize_position_max').double_value
        self._max_speed = g('max_speed').double_value
        self.log(f'LQG tuning for this mission: rho={self._lqg_rho:.2f} '
                 f'stab_rho={self._stabilize_rho:.2f} '
                 f'theta_max={self._lqg_theta_max:.3f} '
                 f'stab_theta_max={self._stabilize_theta_max:.3f} '
                 f'max_trim={self._max_trim_speed:.2f} v_max={self._max_speed:.2f}')

    def _wait_for_pendulum_params(self, timeout: float = 30.0) -> bool:
        if self._pendulum_params is not None:
            return True
        start = self.now_time
        while (self.now_time - start) < timeout:
            if self._pendulum_params is not None:
                return True
            self._node.get_logger().info(
                f'Waiting for {self._params_topic} - is hook_kalman_filter_node '
                'running and has its identification finished?',
                throttle_duration_sec=2.0
            )
            time.sleep(0.5)
        return False

    def _load_identified_pendulum_params(self) -> "tuple[float, float]|None":
        if not self._wait_for_pendulum_params():
            self._node.get_logger().error(
                f'No {self._params_topic} after 30s - rejecting the goal rather '
                'than guessing L/xi.'
            )
            return None

        L, xi = self._pendulum_params
        if not (L > 0.0):
            self._node.get_logger().error(f'Received non-positive rope length {L} - rejecting the goal')
            return None
        if not (0.0 < xi < 1.0):
            self.log(f'Identified xi={xi} outside (0,1), clamping for the controllers')
            xi = min(max(xi, 1e-3), 0.99)
        self.log(f'Using pendulum params from {self._params_topic}: L={L:.3f}m, xi={xi:.4f}')
        return L, xi

    def _create_subscriptions(self):
        qos_best_effort10 = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT,
                                        durability=QoSDurabilityPolicy.VOLATILE)

        self._hook_swing_topic:str = DJITopics.HOOK_STATE_ANGULAR
        self._node.create_subscription(
            JointState, self._hook_swing_topic,
            self._swing_state_callback, qos_best_effort10
        )
        self._node.create_subscription(
            Odometry, SmarcTopics.ODOM_TOPIC,
            self._odom_callback, 10
        )
        
        qos_latched = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                                 durability=QoSDurabilityPolicy.TRANSIENT_LOCAL)
        self._params_topic:str = DJITopics.HOOK_PENDULUM_PARAMETERS
        self._node.create_subscription(
            Float64MultiArray, self._params_topic,
            self._pendulum_params_callback, qos_latched
        )

    def _pendulum_params_callback(self, msg:Float64MultiArray):
        if len(msg.data) >= 2:
            self._pendulum_params = (float(msg.data[0]), float(msg.data[1]))

    def _swing_state_callback(self, msg:JointState):
        self._swing_state = msg

    def _odom_callback(self, msg:Odometry):
        vel_in = Vector3Stamped()
        vel_in.header.stamp = msg.header.stamp
        vel_in.header.frame_id = msg.header.frame_id
        vel_in.vector = msg.twist.twist.linear

        vel_bf = self._drone_state.vector_stamped_in_base_flat(vel_in)
        if vel_bf is None:
            return
        self._drone_velocity_base_flat = np.array(
            [vel_bf.vector.x, vel_bf.vector.y, vel_bf.vector.z], float
        )

    def _create_publishers(self):
        qos_best_effort10 = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT, durability=QoSDurabilityPolicy.VOLATILE)
        self.ref_publisher             = self._node.create_publisher(TwistStamped, 
                                                                     DJITopics.VELOCITY_SETPOINT_TOPIC, 
                                                                     qos_profile=qos_best_effort10)

        _drone_frame_ref_topic:str = DJITopics.CMD_VELOCITY_DRONE_FRAME
        self.drone_frame_ref_publisher = self._node.create_publisher(Vector3Stamped,
                                                                     _drone_frame_ref_topic,
                                                                     qos_profile=qos_best_effort10)


    @property
    def now_stamp(self):
        return self._node.get_clock().now().to_msg()
    
    @property
    def now_time(self):
        return self.now_stamp.sec + self.now_stamp.nanosec * 1e-9
    
    def log(self, msg: str):
        self._node.get_logger().info(msg)

    def _have_position(self, timeout:float = 5.0) -> bool:
        start_time = self.now_time
        flag = False

        while (self.now_time - start_time) < timeout:
            if self._drone_state._drone_in_map is not None:
                flag = True
                break
            self._node.get_logger().info('Waiting for drone in map position', throttle_duration_sec=2.0)
            time.sleep(0.5)
        
        if not flag:
            self._node.get_logger().error('Error: no trone in map position')

        return flag 

    def _on_goal_received(self, goal_request:dict) -> bool:
        try:
            gp : GeoPoint = GeoPoint()
            gp.latitude = goal_request['waypoint']['latitude']
            gp.longitude = goal_request['waypoint']['longitude']
            gp.altitude = goal_request['waypoint']['altitude']

            self._goal_in_map = self._drone_state.geopoint_to_pose_stamped_map(gp)
            if self._goal_in_map is None:
                self._node.get_logger().error('Failed to transform goal from latlon to map frame')
                return False
            self._goal_in_base_flat = self._drone_state.pose_stamped_in_base_flat(self._goal_in_map)
            if self._goal_in_base_flat is None:
                self._node.get_logger().error('Failed to transform goal from map frame to base_flat frame')
                return False
            
            self._goal_tolerance = float(goal_request['waypoint']['tolerance']) if 'tolerance' in goal_request['waypoint'] else self._default_goal_tolerance

            pos = self._goal_in_map.pose.position

            self.log(
                f'Received goal in map: [{pos.x:.2f},{pos.y:.2f},{pos.z:.2f}], tolerance: {self._goal_tolerance}\n This is an altitude-constant mission, only x and y coordinates will be considere'
            )

            pos_base_flat = self._goal_in_base_flat.pose.position
            self.log(
                f'Same goal in base_flat: [{pos_base_flat.x:.2f},{pos_base_flat.y:.2f},{pos_base_flat.z:.2f}]'
            )

            if not self._have_position():  
                self._node.get_logger().error('Error: no trone in map position')
                return False 
            
            self._refresh_tuning_parameters()

            self._max_speed = self._resolve_goal_speed(goal_request)
            open_loop = bool(goal_request.get('open-loop', not self._enable_lqg))
            self._enable_lqg = not open_loop
            self.log(
                f'Goal options: speed={self._max_speed:.2f} m/s, '
                f'open-loop={open_loop} '
                f'({"ZVD feedforward only" if open_loop else "ZVD + LQG trim"})'
            )

            drone_pose = self._drone_state._drone_in_map.pose.position
            drone_position = np.asarray([drone_pose.x, drone_pose.y], float)
            target_position = np.array([pos.x, pos.y], float)
            self._path_parametrizer = PathParametrizer(drone_position, target_position,
                                                         self._max_speed, self._max_acceleration)

            self._altitude_tolerance = self._node.get_parameter(
                'altitude_tolerance').get_parameter_value().double_value
            self._target_altitude_map = float(pos.z)
            altitude_error = self._target_altitude_map - float(drone_pose.z)
            self._needs_altitude_leg = abs(altitude_error) > self._altitude_tolerance
            if self._needs_altitude_leg:
                self.log(
                    f'Goal altitude {self._target_altitude_map:.2f} m is '
                    f'{altitude_error:+.2f} m from the current {drone_pose.z:.2f} m '
                    f'(tol {self._altitude_tolerance:.2f}) - flying a plain vertical '
                    f'leg first, no sway control.'
                )

            identified = self._load_identified_pendulum_params()
            if identified is None:
                return False
            L, xi = identified
            self._mission_L, self._mission_xi = L, xi

            self.zvd = ZVD(L, xi)
            self.Ai, self.Ti = self.zvd.computeZVDMatrix()

            if self._enable_lqg:
                self._lqr = LQR(
                    L=L, xi=xi,
                    k_x=self._k_x, tau_x=self._tau_x,
                    k_y=self._k_y, tau_y=self._tau_y,
                    k_z=self._k_z, tau_z=self._tau_z,
                    v_max=self._max_speed,
                    rho=self._lqg_rho,
                    p_max=self._lqg_position_max,
                    pz_max=self._lqg_position_max,
                    theta_max=self._lqg_theta_max,
                )
                slowest = max(e.real for e in self._lqr.closed_loop_eigenvalues)
                self.log(f'LQG enabled: closed-loop slowest pole {slowest:+.3f} '
                         f'(open-loop swing decay was {-xi*np.sqrt(G/L):+.4f})')

                self._lqr_stabilize = LQR(
                    L=L, xi=xi,
                    k_x=self._k_x, tau_x=self._tau_x,
                    k_y=self._k_y, tau_y=self._tau_y,
                    k_z=self._k_z, tau_z=self._tau_z,
                    v_max=self._max_speed,
                    rho=self._stabilize_rho,
                    p_max=self._stabilize_position_max,
                    pz_max=self._stabilize_position_max,
                    theta_max=self._stabilize_theta_max,
                )
            else:
                self._lqr = None
                self._lqr_stabilize = None
                self.log('LQG disabled (enable_lqg=False) - flying the ZVD feedforward open loop')

            self._phase = ('ALTITUDE' if self._needs_altitude_leg
                           else self._phase_after_altitude())
            self._stabilize_started = self.now_time
            self._within_tol_since:None|float = None
            self._hold_position_map:None|np.ndarray = None

            shaper_duration = self.Ti[-1]
            self._start_mission_time = self.now_time
            self._t_end = self._start_mission_time + self._path_parametrizer._missionTime + shaper_duration + self._settle_extra
            

            return True

        except:
            self._node.get_logger().error('Failed to parse goal request')
            traceback.print_exc()
            return False
    
    def _on_cancel_received(self) -> bool:
        self.log('Cancel requested, stopping...')
        self._goal_in_map = None
        return True
    
    def _prepare_loop(self) -> None:
        goal_error = np.array([
            self._goal_in_base_flat.pose.position.x,
            self._goal_in_base_flat.pose.position.y
        ])
        self._distance_from_goal = np.linalg.norm(goal_error)
        self.log(f'Goal error: [{goal_error[0]:.2f}, {goal_error[1]:.2f}] \n Total distance: {self._distance_from_goal:.2f}')
        return
    
    def _give_feedback(self) -> str:
        if self._distance_from_goal is not None:
            return f'Distance remaining: {self._distance_from_goal:.2f} (tolerance: {self._goal_tolerance:.2f}m)'
        else:
            return 'No distance remaining info'

    def _lqg_correction(self, position_reference_map, velocity_reference_base_flat):
        if self._lqr is None:
            return None

        if self._swing_state is None:
            self._node.get_logger().warning(
                f'No {self._hook_swing_topic} yet - flying feedforward only. Is '
                'hook_kalman_filter_node running?', throttle_duration_sec=5.0
            )
            return None

        stamp = self._swing_state.header.stamp
        age = self.now_time - (stamp.sec + stamp.nanosec * 1e-9)
        if age > self._max_estimate_age:
            self._node.get_logger().warning(
                f'{self._hook_swing_topic} is {age:.2f}s old (limit {self._max_estimate_age:.2f}s) '
                f'- flying feedforward only', throttle_duration_sec=5.0
            )
            return None

        if self._drone_velocity_base_flat is None:
            self._node.get_logger().warning(
                'No drone velocity yet - flying feedforward only', throttle_duration_sec=5.0
            )
            return None

        drone_in_map = self._drone_state.drone_in_map_numpy
        if drone_in_map is None:
            return None

        err_map = Vector3Stamped()
        err_map.header.stamp = self.now_stamp
        err_map.header.frame_id = self._drone_state.MAP_FRAME
        err_map.vector.x = float(drone_in_map[0] - position_reference_map[0])
        err_map.vector.y = float(drone_in_map[1] - position_reference_map[1])
        err_map.vector.z = 0.0   
        err_bf = self._drone_state.vector_stamped_in_base_flat(err_map)
        if err_bf is None:
            return None

        i = LQR.IDX
        x = np.zeros(LQR.N_STATES)
        r = np.zeros(LQR.N_STATES)

        x[i['p_x']] = err_bf.vector.x
        x[i['p_y']] = err_bf.vector.y
        x[i['p_z']] = 0.0

        x[i['v_x']] = self._drone_velocity_base_flat[0]
        x[i['v_y']] = self._drone_velocity_base_flat[1]
        x[i['v_z']] = self._drone_velocity_base_flat[2]
        r[i['v_x']] = velocity_reference_base_flat.vector.x
        r[i['v_y']] = velocity_reference_base_flat.vector.y
        r[i['v_z']] = 0.0

        x[i['theta_x']] = self._swing_state.position[0]
        x[i['theta_y']] = self._swing_state.position[1]
        x[i['omega_x']] = self._swing_state.velocity[0]
        x[i['omega_y']] = self._swing_state.velocity[1]

        theta_mag = max(abs(x[i['theta_x']]), abs(x[i['theta_y']]))
        if theta_mag > self._max_theta_for_lqg:
            self._node.get_logger().warning(
                f'|theta| {theta_mag:.3f} rad exceeds {self._max_theta_for_lqg:.3f} - '
                f'outside the linear model, dropping feedback this tick',
                throttle_duration_sec=2.0
            )
            return None

        u_fb = self._lqr.controlAction(x, r)

        trim_speed = float(np.linalg.norm(u_fb[:2]))
        if trim_speed > self._max_trim_speed:
            u_fb = u_fb * (self._max_trim_speed / trim_speed)

        self._node.get_logger().info(
            f'[lqg] theta=[{x[i["theta_x"]]:+.3f},{x[i["theta_y"]]:+.3f}]rad '
            f'pos_err=[{x[i["p_x"]]:+.2f},{x[i["p_y"]]:+.2f}]m '
            f'trim=[{u_fb[0]:+.3f},{u_fb[1]:+.3f}]m/s '
            f'est_age={age*1000:.0f}ms',
            throttle_duration_sec=2.0
        )
        return u_fb

    def _stabilize_tick(self) -> bool|None:
        if self._hold_position_map is None:
            here = self._drone_state.drone_in_map_numpy
            if here is None:
                return None
            self._hold_position_map = here.copy()
            self.log(f'Stabilising payload before departure (tol {self._stabilize_theta_tol:.3f} rad '
                     f'for {self._stabilize_settle_time:.1f}s, timeout {self._stabilize_timeout:.1f}s)')

        now = self.now_time
        elapsed = now - self._stabilize_started

        mission_lqr, self._lqr = self._lqr, self._lqr_stabilize
        mission_cap, self._max_trim_speed = self._max_trim_speed, self._max_speed
        hold_velocity = Vector3Stamped()
        hold_velocity.header.stamp = self.now_stamp
        hold_velocity.header.frame_id = self.BASE_FLAT_FRAME   
        u = self._lqg_correction(self._hold_position_map[:2], hold_velocity)
        self._lqr = mission_lqr
        self._max_trim_speed = mission_cap

        if u is None:
            
            if elapsed > self._stabilize_timeout:
                self._node.get_logger().warning(
                    'Could not stabilise (no usable swing estimate) - starting the mission anyway'
                )
                self._begin_mission()
            self._publish_velocity(np.zeros(2))
            return None

        theta = np.array([self._swing_state.position[0], self._swing_state.position[1]])
        omega = np.array([self._swing_state.velocity[0], self._swing_state.velocity[1]])
        settled = (np.max(np.abs(theta)) < self._stabilize_theta_tol and
                   np.max(np.abs(omega)) < self._stabilize_omega_tol)

        if settled:
            if self._within_tol_since is None:
                self._within_tol_since = now
            if (now - self._within_tol_since) >= self._stabilize_settle_time:
                self.log(f'Payload stable after {elapsed:.1f}s '
                         f'(|theta| {np.max(np.abs(theta)):.4f} rad) - starting the mission')
                self._begin_mission()
                return None
        else:
            self._within_tol_since = None

        if elapsed > self._stabilize_timeout:
            self._node.get_logger().warning(
                f'Payload did not settle within {self._stabilize_timeout:.1f}s '
                f'(|theta| {np.max(np.abs(theta)):.4f} rad, tol {self._stabilize_theta_tol:.3f}) '
                f'- starting the mission anyway'
            )
            self._begin_mission()
            return None

        self._node.get_logger().info(
            f'[stabilize] t={elapsed:.1f}s/{self._stabilize_timeout:.0f}s '
            f'|theta|={np.max(np.abs(theta)):.4f}/{self._stabilize_theta_tol:.3f}rad '
            f'theta=[{theta[0]:+.4f},{theta[1]:+.4f}]rad '
            f'omega=[{omega[0]:+.4f},{omega[1]:+.4f}]rad/s u=[{u[0]:+.3f},{u[1]:+.3f}]m/s',
            throttle_duration_sec=1.0
        )
        self._publish_velocity(u[:2])
        return None

    def _phase_after_altitude(self) -> str:
        return ('STABILIZING'
                if (self._stabilize_before_mission and self._lqr_stabilize is not None)
                else 'MOVING')

    def _altitude_tick(self) -> bool|None:
        here = self._drone_state.drone_in_map_numpy
        if here is None:
            self.log('No drone position yet, holding during the altitude leg.')
            self._publish_velocity(np.zeros(2))
            return None

        altitude_error = self._target_altitude_map - float(here[2])

        if abs(altitude_error) <= self._altitude_tolerance:
            self.log(f'Reached goal altitude ({here[2]:.2f} m, error {altitude_error:+.2f} m) '
                     f'- starting the sway-damped mission.')
            self._publish_velocity(np.zeros(2), vz=0.0)
            drone_now = self._drone_state.drone_in_map_numpy
            goal = self._goal_in_map.pose.position
            self._path_parametrizer = PathParametrizer(
                np.asarray([drone_now[0], drone_now[1]], float),
                np.asarray([goal.x, goal.y], float),
                self._max_speed, self._max_acceleration)
            self._stabilize_started = self.now_time
            self._within_tol_since = None
            self._hold_position_map = None
            next_phase = self._phase_after_altitude()
            if next_phase == 'MOVING':
                self._begin_mission()
            else:
                self._phase = next_phase
            return None

        vz = float(np.clip(altitude_error, -self._max_speed, self._max_speed))
        self._node.get_logger().info(
            f'[altitude] {here[2]:.2f} -> {self._target_altitude_map:.2f} m '
            f'(error {altitude_error:+.2f} m, vz={vz:+.2f} m/s)',
            throttle_duration_sec=1.0
        )
        self._publish_velocity(np.zeros(2), vz=vz)
        return None

    def _begin_mission(self):
        self._phase = 'MOVING'
        self._start_mission_time = self.now_time
        self._t_end = (self._start_mission_time + self._path_parametrizer._missionTime
                       + self.Ti[-1] + self._settle_extra)

    def _publish_velocity(self, u_xy:np.ndarray, vz: float = 0.0) -> np.ndarray:
        speed = float(np.linalg.norm(u_xy))
        if speed > self._max_speed:
            u_xy = u_xy * (self._max_speed / speed)
        setpoint = TwistStamped()
        setpoint.header.stamp = self.now_stamp
        setpoint.header.frame_id = self.BASE_FLAT_FRAME
        setpoint.twist.linear.x = float(u_xy[0])
        setpoint.twist.linear.y = float(u_xy[1])
        setpoint.twist.linear.z = float(vz)
        self.ref_publisher.publish(setpoint)

        drone_frame_cmd = Vector3Stamped()
        drone_frame_cmd.header.stamp = setpoint.header.stamp
        drone_frame_cmd.header.frame_id = self.BASE_FLAT_FRAME
        drone_frame_cmd.vector.x = float(u_xy[0])
        drone_frame_cmd.vector.y = float(u_xy[1])
        self.drone_frame_ref_publisher.publish(drone_frame_cmd)
        return u_xy

    def _loop_inner(self) -> bool|None:
        if self._phase == 'ALTITUDE':
            return self._altitude_tick()

        if self._phase == 'STABILIZING':
            return self._stabilize_tick()

        goal_in_base_flat_now = self._drone_state.pose_stamped_in_base_flat(self._goal_in_map)
        if goal_in_base_flat_now is None:
            self.log("Failed to transform goal into current base_flat frame, skipping this tick.")
            return None

        goal_error = np.array([
            goal_in_base_flat_now.pose.position.x,
            goal_in_base_flat_now.pose.position.y
        ])
        self._distance_from_goal = np.linalg.norm(goal_error)

        if self._distance_from_goal < self._goal_tolerance:
            self.log(f'Goal reaced withing tolerance {self._goal_tolerance}, return SUCCESS')
            return True
        #self.log(f'Distance remaining: {self._distance_from_goal:.2f}')

        now = self.now_time
        elapsed_time = now - self._start_mission_time

        if now > self._t_end:
            self._node.get_logger().error('Goal not reached within mission time, return FAILURE')
            return False

        position_references, velocity_references = self.zvd.shapeReferences(
            self.Ai, self.Ti, self._path_parametrizer, elapsed_time
        )

        time_remaining = self._path_parametrizer._missionTime - elapsed_time
        self._node.get_logger().info(
            f'[debug] t_remaining_in_plan: {time_remaining:.2f}s '
            f'(elapsed: {elapsed_time:.2f}s / missionTime: {self._path_parametrizer._missionTime:.2f}s), '
            f'v_map: [{velocity_references[0]:+.3f}, {velocity_references[1]:+.3f}]',
            throttle_duration_sec=2.0
        )

        vel_in_map = Vector3Stamped()
        vel_in_map.header.stamp = self.now_stamp
        vel_in_map.header.frame_id = self._drone_state.MAP_FRAME
        vel_in_map.vector.x = float(velocity_references[0])
        vel_in_map.vector.y = float(velocity_references[1])

        vel_in_base_flat = self._drone_state.vector_stamped_in_base_flat(vel_in_map)
        if vel_in_base_flat is None:
            self.log("Failed to transform velocity reference into base_flat frame, skipping this tick.")
            return None

        u = np.array([vel_in_base_flat.vector.x, vel_in_base_flat.vector.y], float)

        correction = self._lqg_correction(position_references, vel_in_base_flat)
        if correction is not None:
            u = u + correction[:2]

        self._publish_velocity(u)

        self._node.get_logger().info(
            f'[debug] v_base_flat published (pre-saturation): [{u[0]:+.3f}, {u[1]:+.3f}]',
            throttle_duration_sec=2.0
        )

        return None

def main(args=None):
    rclpy.init(args=args)
    node = Node("alars_move_to_damped_action_server")
    move_to_damped_action_server = MoveToDampedAction(node)
    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)
    node.destroy_node()
    rclpy.shutdown()