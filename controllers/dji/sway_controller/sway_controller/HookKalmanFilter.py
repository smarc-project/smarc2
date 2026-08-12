from rclpy.node     import Node
from rclpy.qos      import QoSProfile, ReliabilityPolicy, QoSDurabilityPolicy
from rclpy.time     import Time
from rclpy.duration import Duration

from dji_msgs.msg       import Topics, Links
from yolo_msgs.msg      import DetectionArray
from smarc_msgs.msg     import Topics as SmarcTopics 
from geometry_msgs.msg  import Vector3Stamped
from nav_msgs.msg       import Odometry
from sensor_msgs.msg    import CameraInfo, JointState
from std_msgs.msg       import Float64MultiArray, MultiArrayDimension
from tf2_ros            import Buffer, TransformListener
from tf2_geometry_msgs  import do_transform_vector3

import os
import yaml
import numpy   as np
import control as ct

from ament_index_python import get_package_share_directory

class HookKalmanFilter:
    def __init__(self, node:Node ,robot_name:str, 
                 use_simtime:bool,loop_freq:int, 
                 L:float, xi:float,
                 taux:float, tauy:float,
                 kx:float, ky:float, 
                 qc:float, sigma_initial:float,
                 mahalanobis_thr:float,
                 camera_calibration_file:str,
                 max_boresight_tilt_deg:float = 45.0):

        self._node:Node = node
        self._robot_name:str = robot_name
        self._T:float = 1/loop_freq
        self._mahalanobis_thr = mahalanobis_thr
        self._max_boresight_tilt_deg:float = max_boresight_tilt_deg

        self._camera_config_path:None|str = None 
        self._image_width:float  
        self._image_height:float 
        self._fx:float
        self._fy:float
        self._cx:float 
        self._cy:float 
        self._loaded_camera_parameters: bool = False

        pkg_share = get_package_share_directory('auv_state_estimation')
        self._camera_config_path = os.path.join(pkg_share, 'config', camera_calibration_file)

        self._read_camera_params()

        self._camera_frame:str    = self._robot_name + '/' + Links.GIMBAL_OPTICAL_FRAME
        self._base_flat_frame:str = self._robot_name + '/' + Links.BASE_FLAT
        
        self._pivot_frame:str     = self._robot_name + '/' + Links.ROPE_BASE_LINK
        
        self._pivot_in_base_flat:np.ndarray = np.zeros(3)
        self._tf_buffer   = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self._node)

        self._last_meas:np.ndarray[None|float] = np.full(2, None) #[theta_x, theta_y]
        self._vmeas:np.ndarray[None|float]     = np.full(2, None)

        wn:float         = np.sqrt(9.81/L)
        self._L:float    = L
        self._taux:float = taux
        self._tauy:float = tauy
        self._kx:float   = kx
        self._ky:float   = ky
        self._qc:float   = qc

        self._Ac:np.ndarray = np.array([
                                    [0,       1,       0,      0      ],   #theta_x
                                    [-wn**2, -2*xi*wn, 0,      0      ],   #omega_x
                                    [0,       0,       0,      1      ],   #theta_y
                                    [0,       0,      -wn**2, -2*xi*wn]    #omega_x
                                 ])

        self._Bc:np.ndarray = np.array([
                                    [0,    0  ],
                                    [-1/L, 0  ],
                                    [0,    0  ],
                                    [0,   -1/L]
                                 ])

        self._Cd:np.ndarray = np.array([
                                            [1, 0, 0,   0],
                                            [0, 0, 1.0, 0]
                                       ])
        self._Dc:np.ndarray = np.zeros((2, 2))

        self._last_tick_time = None
        self._last_accepted_meas_time = None
        self._typical_dt: "float|None" = None

        # [cmd_x, cmd_y], cmd_z dropped since it is assume the drone to move on the X-Y plane
        self._last_input:np.ndarray[float] = np.zeros(2)  
        self._mu_bar:np.ndarray[float]     = np.zeros(4) # estimated state after the prediction step
        self._mu:np.ndarray[float]         = np.zeros(4) # estimated state after the update step 

        self._sigma_px:float = 10.0 #pixels
        self._sigma_py:float = 10.0 #pixels

        self._R:np.ndarray[float]
        self._update_measurement_noise()

        self._Sigma_bar:np.ndarray[float] = sigma_initial * np.eye(4)
        self._Sigma:np.ndarray[float] = sigma_initial * np.eye(4)

        self._create_node_subscriptions()
        self._create_publishers()
        self._publish_pendulum_params(L, xi)

        self._timer = self._node.create_timer(timer_period_sec=self._T, callback=self._prediction)

    def _read_camera_params(self):
        
        with open(self._camera_config_path, 'r') as file:
            try:
                config = yaml.safe_load(file)
            except yaml.YAMLError as exc:
                self._node.get_logger().info(f"Error reading YAML file: {exc}")

        self._image_width  = config['image_width']
        self._image_height = config['image_height']
        self._fx           = config['camera_matrix']['data'][0]
        self._fy           = config['camera_matrix']['data'][4]
        self._cx           = config['camera_matrix']['data'][2]
        self._cy           = config['camera_matrix']['data'][5]

        self._loaded_camera_parameters = True 
        self._node.get_logger().info(f'Camera parameter loaded from:{self._camera_config_path}')
        

    def _create_publishers(self):
        qos_best_effort10 = QoSProfile(depth=10, 
                                               reliability=ReliabilityPolicy.BEST_EFFORT, 
                                               durability=QoSDurabilityPolicy.VOLATILE)
        _hook_state_topic:str = Topics.HOOK_STATE_CARTESIAN
        self._hook_state_pub = self._node.create_publisher(Odometry, _hook_state_topic, qos_best_effort10)
        self._node.get_logger().info(f'Publishing hook state on:{_hook_state_topic}')

        _hook_raw_meas_topic:str = Topics.HOOK_RAW_MEASUREMENT
        self._hook_raw_meas_pub = self._node.create_publisher(Odometry, _hook_raw_meas_topic, qos_best_effort10)
        self._node.get_logger().info(f'Publishing raw hook measurement on:{_hook_raw_meas_topic}')

        qos_latched = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                                 durability=QoSDurabilityPolicy.TRANSIENT_LOCAL)
        _params_topic:str = Topics.HOOK_PENDULUM_PARAMETERS
        self._pendulum_params_pub = self._node.create_publisher(
            Float64MultiArray, _params_topic, qos_latched)
        self._node.get_logger().info(f'Publishing identified pendulum params on:{_params_topic}')

        _hook_swing_topic:str = Topics.HOOK_STATE_ANGULAR
        self._hook_swing_pub = self._node.create_publisher(JointState, _hook_swing_topic, qos_best_effort10)
        self._node.get_logger().info(f'Publishing hook swing state on:{_hook_swing_topic}')

    def _create_node_subscriptions(self):
        
        _detection_topic_name:str = Topics.YOLO_DETECTIONS
        self._detection_subscription = self._node.create_subscription(DetectionArray,
                                                                      _detection_topic_name,
                                                                      self._detection_callback,
                                                                      10)
        self._node.get_logger().info(f'Succesfully subscribed to:{_detection_topic_name}')

        qos_best_effort10 = QoSProfile(depth=10, 
                                       reliability=ReliabilityPolicy.BEST_EFFORT, 
                                       durability=QoSDurabilityPolicy.VOLATILE)

        _cmd_vel_topic:str = Topics.CMD_VELOCITY_DRONE_FRAME
        self._cmd_vel_subscriber = self._node.create_subscription(Vector3Stamped, 
                                                                  _cmd_vel_topic, 
                                                                  self._cmd_vel_callback, 
                                                                  qos_profile=qos_best_effort10)
        self._node.get_logger().info(f'Succesfully subscribed to:{_cmd_vel_topic}')

        # Correct info from topic 
        _camera_info_topic:str = Topics.GIMBAL_CAMERA_INFO_TOPIC
        self._camera_info_subscription = self._node.create_subscription(CameraInfo,
                                                                        _camera_info_topic,
                                                                        self._camera_info_callback,
                                                                        10)
        self._node.get_logger().info(f'Succesfully subscribed to:{_camera_info_topic}')

        _odom_topic:str = SmarcTopics.ODOM_TOPIC
        self._odom_subscription = self._node.create_subscription(Odometry,
                                                                 _odom_topic,
                                                                 self._odom_callback,
                                                                 10)
        self._node.get_logger().info(f'Succesfully subscribed to:{_odom_topic}')

    def _lookup_pivot(self) -> "np.ndarray|None":
        
        try:
            tf = self._tf_buffer.lookup_transform(
                self._base_flat_frame, self._pivot_frame, Time(), timeout=Duration(seconds=0.05)
            )
        except Exception as e:
            self._node.get_logger().warning(
                f'Could not transform {self._pivot_frame} -> {self._base_flat_frame}, '
                f'treating the camera as the pivot (adds a systematic offset): {e}',
                throttle_duration_sec=5.0
            )
            return None
        return np.array([tf.transform.translation.x,
                         tf.transform.translation.y,
                         tf.transform.translation.z])

    def _camera_info_callback(self, msg:CameraInfo):
        """Adopt the intrinsics the camera itself publishes, overriding the yaml.
           Implemented owed to great discrepancy in the sim
        """
        fx, fy = float(msg.k[0]), float(msg.k[4])
        cx, cy = float(msg.k[2]), float(msg.k[5])
        if fx <= 0.0 or fy <= 0.0:
            self._node.get_logger().warning(
                f'Ignoring CameraInfo with non-positive focal lengths (fx={fx}, fy={fy})',
                throttle_duration_sec=10.0
            )
            return

        unchanged = (self._loaded_camera_parameters
                     and abs(fx - self._fx) < 1e-6 and abs(fy - self._fy) < 1e-6
                     and abs(cx - self._cx) < 1e-6 and abs(cy - self._cy) < 1e-6)
        if unchanged:
            return

        self._node.get_logger().info(
            f'Using intrinsics from CameraInfo: fx={fx:.2f} fy={fy:.2f} cx={cx:.2f} cy={cy:.2f} '
            f'(yaml had fx={self._fx:.2f} fy={self._fy:.2f} cx={self._cx:.2f} cy={self._cy:.2f})'
        )
        self._fx, self._fy, self._cx, self._cy = fx, fy, cx, cy
        if msg.width > 0 and msg.height > 0:
            self._image_width, self._image_height = float(msg.width), float(msg.height)
        self._loaded_camera_parameters = True
        
        self._update_measurement_noise()

    def _update_measurement_noise(self):
        self._R = np.array([
            [(self._sigma_px / self._fx)**2, 0                             ],
            [0,                              (self._sigma_py / self._fy)**2]
        ])

    def _cmd_vel_callback(self, msg:Vector3Stamped):
        self._last_input[0] = msg.vector.x
        self._last_input[1] = msg.vector.y

    def _detection_callback(self, msg):
        if not self._loaded_camera_parameters:
            self._node.get_logger().warning('Camera parameters not loaded yet, skipping measurement')
            return 

        hook_dets = [d for d in msg.detections if d.class_name == "hook"]
        if not hook_dets:
            self._node.get_logger().info(f'No hook detection in this frame', throttle_duration_sec=1.0)
            return

        u:float = sum(float(d.bbox.center.position.x) for d in hook_dets) / len(hook_dets)
        v:float = sum(float(d.bbox.center.position.y) for d in hook_dets) / len(hook_dets)

        ray_in = Vector3Stamped()
        
        ray_in.header.stamp = msg.header.stamp
        ray_in.header.frame_id = self._camera_frame
        ray_in.vector.x = (u - self._cx) / self._fx
        ray_in.vector.y = (v - self._cy) / self._fy
        ray_in.vector.z = 1.0

        try:
            transform = self._tf_buffer.lookup_transform(
                self._base_flat_frame, self._camera_frame, Time(), timeout=Duration(seconds=0.2)
            )
        except Exception as e:
            self._node.get_logger().warning(
                f'Could not transform {self._camera_frame} -> {self._base_flat_frame}, '
                f'skipping this detection: {e}',
                throttle_duration_sec=1.0
            )
            return

        ray_out = do_transform_vector3(ray_in, transform)

        boresight = Vector3Stamped()
        boresight.header.frame_id = self._camera_frame
        boresight.vector.z = 1.0
        bs = do_transform_vector3(boresight, transform).vector
        tilt_from_down_deg = float(np.degrees(np.arccos(np.clip(-bs.z, -1.0, 1.0))))
        if tilt_from_down_deg > self._max_boresight_tilt_deg:
            self._node.get_logger().warning(
                f'Camera boresight is {tilt_from_down_deg:.0f}deg off straight-down '
                f'(limit {self._max_boresight_tilt_deg:.0f}deg) - the pendulum-angle '
                f'measurement is not valid in this pose, skipping this detection. ',
                throttle_duration_sec=5.0
            )
            return

        pivot = self._lookup_pivot()
        if pivot is None:
            
            self._last_meas[0] = np.arctan2(ray_out.vector.x, -ray_out.vector.z)
            self._last_meas[1] = np.arctan2(ray_out.vector.y, -ray_out.vector.z)
            self._pivot_in_base_flat = np.zeros(3)
        else:
            cam = np.array([transform.transform.translation.x,
                            transform.transform.translation.y,
                            transform.transform.translation.z])
            d = np.array([ray_out.vector.x, ray_out.vector.y, ray_out.vector.z])
            norm = np.linalg.norm(d)
            if norm <= 0.0:
                return
            d = d / norm

            w = cam - pivot
            wd = float(w @ d)
            disc = wd * wd - float(w @ w) + self._L * self._L
            if disc < 0.0:
                
                self._node.get_logger().warning(
                    'Hook detection ray does not intersect the pendulum sphere '
                    f'(L={self._L:.2f}m) - skipping it',
                    throttle_duration_sec=5.0
                )
                return
            s = -wd + np.sqrt(disc)   
            if s <= 0.0:
                self._node.get_logger().warning(
                    'Hook intersection resolved behind the camera - skipping it',
                    throttle_duration_sec=5.0
                )
                return

            r = cam + s * d - pivot   # hook position relative to the pivot
            self._last_meas[0] = np.arctan2(r[0], -r[2])
            self._last_meas[1] = np.arctan2(r[1], -r[2])
            self._pivot_in_base_flat = pivot
        
        self._publish_raw_measurement(msg.header.stamp)

        self._update()

    def _publish_raw_measurement(self, stamp):
        
        theta_x, theta_y = self._last_meas
        msg = Odometry()
        msg.header.stamp = stamp
        msg.header.frame_id = self._base_flat_frame
        msg.child_frame_id = self._robot_name + '/hook'
        
        msg.pose.pose.position.x = float(self._pivot_in_base_flat[0] + self._L * np.sin(theta_x))
        msg.pose.pose.position.y = float(self._pivot_in_base_flat[1] + self._L * np.sin(theta_y))
        msg.pose.pose.position.z = 0.0
        msg.pose.pose.orientation.w = 1.0
        self._hook_raw_meas_pub.publish(msg)

    def _odom_callback(self, msg:Odometry):
        
        vel_in = Vector3Stamped()
        vel_in.header.stamp = msg.header.stamp
        vel_in.header.frame_id = msg.header.frame_id
        vel_in.vector = msg.twist.twist.linear

        try:
            transform = self._tf_buffer.lookup_transform(
                self._base_flat_frame, msg.header.frame_id, Time(), timeout=Duration(seconds=0.1)
            )
        except Exception as e:
            self._node.get_logger().warning(
                f'Could not transform odom velocity {msg.header.frame_id} -> '
                f'{self._base_flat_frame}, keeping previous value: {e}',
                throttle_duration_sec=5.0
            )
            return

        vel_body = do_transform_vector3(vel_in, transform).vector
        self._vmeas[0] = vel_body.x
        self._vmeas[1] = vel_body.y

    def _prediction(self):
        now = self._node.get_clock().now()

        if self._last_tick_time is None:
            self._last_tick_time = now
            return

        dt:float = (now - self._last_tick_time).nanoseconds * 1e-9
        self._last_tick_time = now

        if dt == 0.0:
            return

        if dt < 0.0:
            self._node.get_logger().warning(
                f'Clock went backwards ({dt:.3f}s between predictions), resynchronising',
                throttle_duration_sec=5.0
            )
            return

        if self._typical_dt is None:
            self._typical_dt = dt
        else:
            self._typical_dt += 0.05 * (dt - self._typical_dt)   

        if dt > 3 * self._typical_dt and dt > 3 * self._T:
            self._node.get_logger().warning(
                f'_prediction() stalled: this tick took {dt:.3f}s vs a typical '
                f'{self._typical_dt:.3f}s ({1/self._typical_dt:.1f} Hz)',
                throttle_duration_sec=10.0
            )

        if self._vmeas[0] is None or self._vmeas[1] is None:
            self._node.get_logger().warning('No Odometry msg recieved yet. Skipping the update')
            return

        discrete_ss = ct.c2d(ct.ss(self._Ac, self._Bc, self._Cd, self._Dc), dt, 'zoh')
        Ad:np.ndarray = np.asarray(discrete_ss.A)
        Bd:np.ndarray = np.asarray(discrete_ss.B)

        Q_axis:np.ndarray = self._qc * np.array([[dt**3 / 3, dt**2 / 2],
                                                   [dt**2 / 2, dt       ]])
        Q:np.ndarray = np.block([
            [Q_axis,               np.zeros_like(Q_axis)],
            [np.zeros_like(Q_axis), Q_axis]
        ])

        a:np.ndarray = np.array([
                                   -self._taux * self._vmeas[0] + self._kx * self._last_input[0],
                                   -self._tauy * self._vmeas[1] + self._ky * self._last_input[1]
                                ])

        self._mu_bar = Ad @ self._mu + Bd @ a
        sigma_bar_update:np.ndarray[float] = Ad @ self._Sigma @ Ad.T + Q
        self._Sigma_bar = (sigma_bar_update + sigma_bar_update.T) / 2

        self._mu = self._mu_bar
        self._Sigma = self._Sigma_bar

        self._publish_hook_state()

    def _publish_hook_state(self):
        theta_x, omega_x, theta_y, omega_y = self._mu

        sin_tx, cos_tx = np.sin(theta_x), np.cos(theta_x)
        sin_ty, cos_ty = np.sin(theta_y), np.cos(theta_y)

        x  = self._pivot_in_base_flat[0] + self._L * sin_tx
        y  = self._pivot_in_base_flat[1] + self._L * sin_ty
        vx = self._L * cos_tx * omega_x
        vy = self._L * cos_ty * omega_y

        
        Sigma_x = self._Sigma[0:2, 0:2]  
        Jx  = np.array([self._L * cos_tx, 0.0])
        Jvx = np.array([-self._L * sin_tx * omega_x, self._L * cos_tx])
        var_x  = float(Jx  @ Sigma_x @ Jx.T)
        var_vx = float(Jvx @ Sigma_x @ Jvx.T)

        Sigma_y = self._Sigma[2:4, 2:4]  
        Jy  = np.array([self._L * cos_ty, 0.0])
        Jvy = np.array([-self._L * sin_ty * omega_y, self._L * cos_ty])
        var_y  = float(Jy  @ Sigma_y @ Jy.T)
        var_vy = float(Jvy @ Sigma_y @ Jvy.T)

        msg = Odometry()
        msg.header.stamp = self._node.get_clock().now().to_msg()
        msg.header.frame_id = self._robot_name + '/' + Links.BASE_FLAT
        msg.child_frame_id = self._robot_name + '/hook'

        msg.pose.pose.position.x = float(x)
        msg.pose.pose.position.y = float(y)
        msg.pose.pose.position.z = 0.0
        msg.pose.pose.orientation.w = 1.0  

        msg.twist.twist.linear.x = float(vx)
        msg.twist.twist.linear.y = float(vy)
        msg.twist.twist.linear.z = 0.0

        msg.pose.covariance[0]  = var_x   # (x, x)
        msg.pose.covariance[7]  = var_y   # (y, y)
        msg.twist.covariance[0] = var_vx  # (vx, vx)
        msg.twist.covariance[7] = var_vy  # (vy, vy)

        self._hook_state_pub.publish(msg)
        self._publish_swing_state(msg.header.stamp)

        if self._last_accepted_meas_time is not None:
            meas_age = (self._node.get_clock().now() - self._last_accepted_meas_time).nanoseconds * 1e-9
            self._node.get_logger().info(
                f'[meas] newest accepted detection is {meas_age*1000:.0f}ms old',
                throttle_duration_sec=2.0
            )

    def _publish_pendulum_params(self, L: float, xi: float):
        """
        Publish the L/xi this filter is actually running with, once, latched.

        """
        msg = Float64MultiArray()
        msg.layout.dim = [MultiArrayDimension(label='length', size=1, stride=2),
                          MultiArrayDimension(label='damping', size=1, stride=1)]
        msg.data = [float(L), float(xi)]
        self._pendulum_params_pub.publish(msg)

    def _publish_swing_state(self, stamp):
        """The raw filter state [theta_x, omega_x, theta_y, omega_y]"""
        theta_x, omega_x, theta_y, omega_y = self._mu

        msg = JointState()
        msg.header.stamp = stamp
        msg.header.frame_id = self._base_flat_frame
        msg.name = ['hook_theta_x', 'hook_theta_y']
        msg.position = [float(theta_x), float(theta_y)]
        msg.velocity = [float(omega_x), float(omega_y)]
        msg.effort = [float(self._Sigma[0, 0]), float(self._Sigma[2, 2])]

        self._hook_swing_pub.publish(msg)

    def _update(self):
        y:np.ndarray[float] = self._last_meas - self._Cd @ self._mu_bar

        S:np.ndarray[float]     = self._Cd @ self._Sigma_bar @ self._Cd.T + self._R
        S_inv:np.ndarray[float] = np.linalg.inv(S)
        K:np.ndarray[float]     = self._Sigma_bar @ self._Cd.T @ S_inv

        d2:float = float(y.T @ S_inv @ y)
        if d2 > self._mahalanobis_thr:
            self._node.get_logger().warn(f'Hook detection rejected as outlier:{d2} > {self._mahalanobis_thr}')
            self._mu = self._mu_bar
            self._Sigma = self._Sigma_bar
            return 

        self._last_accepted_meas_time = self._node.get_clock().now()
        self._mu = self._mu_bar + K @ (self._last_meas - self._Cd @ self._mu_bar)

        term = np.eye(len(self._mu)) - K @ self._Cd
        sigma_update:np.ndarray[float] = term @ self._Sigma_bar @ term.T + K @ self._R @ K.T
        self._Sigma = (sigma_update + sigma_update.T) / 2

        if (np.trace(self._Sigma_bar) - np.trace(self._Sigma)<0):
            self._node.get_logger().warning(f'Uncertainty INCREASED after the update')