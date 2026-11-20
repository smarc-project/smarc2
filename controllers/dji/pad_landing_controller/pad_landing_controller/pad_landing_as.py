from .math_utils import (
    numpy_to_vector3,
    rotate_covariance,
    rotation,
    transform_point,
    vector3_to_numpy,
)
import numpy as np
from copy import deepcopy

import rclpy
from rclpy.node import Node
from rclpy.time import Time
from rclpy.qos import qos_profile_sensor_data
from rclpy.executors import MultiThreadedExecutor

from geometry_msgs.msg import Point, PoseWithCovariance, Quaternion
from nav_msgs.msg import Odometry

from smarc_action_base.gentler_action_server import GentlerActionServer
from smarc_georef_cpp import GeorefUtils, TransformException
from smarc_msgs.msg import Topics as SmarcTopics
from transforms3d.quaternions import mat2quat
from dji_msgs.msg import (
    ObjectEkfStatusArray,
    ObjectEkfStatus,
    ObjectPoseWithCovarianceArray,
    Topics as DJITopics,
    Links as DJILinks,
)
from .pad_motion_handler import PadMotionHandler

class PadLandingAS:
    """Action server for autonomous landing on pad:"
    "   --- Node (Done)
    "   --- GAS (Missing)
    "   --- Subs (Done)
    "   --- Pubs (Missing)
    "   Includes relative state estimation of the drone with respect to the landing pad,
    "   using the pad's EKF and prediction during detection loss.
    """

    PAD_CLASS_NAME = 'land_pad'
    ACTION_NAME = 'alars_land_on_pad'
    MAX_EKF_UPDATE_AGE_S = 0.35
    MAX_STATUS_AGE_S = 1.5
    MAX_PAD_POSITION_COV_TRACE= 3.0

    def __init__(self, node):
        self._node = node

        # TODO: Build the AS after adding FSM and control.
        # self._as: GentlerActionServer = GentlerActionServer(
        #     self._node, self.ACTION_NAME,
        #     self._on_goal_received, self._on_cancel_received, self._prepare_loop,
        #     self._loop_inner, self._give_feedback, loop_frequency=10.0)

        self._node.declare_parameter('robot_name', 'M350')
        
        self._node.declare_parameter('landing_relative_state.max_drone_age_s', 0.8)
        self._node.declare_parameter('landing_relative_state.max_pad_age_s', 1.5)
        
        # Enable only for estimation tests (change later with FSM final descent)
        self._node.declare_parameter('pad_odometry.enable_dropout_prediction', False)
        self._node.declare_parameter('pad_odometry.max_prediction_s', 10.0)

        self.ROBOT_NAME: str = self._node.get_parameter('robot_name').get_parameter_value().string_value.strip('/')
        
        self._max_drone_age_s: float = self._node.get_parameter('landing_relative_state.max_drone_age_s').get_parameter_value().double_value
        self._max_pad_age_s: float = self._node.get_parameter('landing_relative_state.max_pad_age_s').get_parameter_value().double_value
        
        self._enable_dropout_prediction: bool = self._node.get_parameter('pad_odometry.enable_dropout_prediction').get_parameter_value().bool_value
        self._max_prediction_s: float = self._node.get_parameter('pad_odometry.max_prediction_s').get_parameter_value().double_value

        self._TF_NS: str = f"{self.ROBOT_NAME}/"
        self.MAP_FRAME: str = self._TF_NS + DJILinks.MAP
        self.LANDING_GEAR_FRAME: str = self._TF_NS + DJILinks.LANDING_GEAR_CENTER

        self._georef: GeorefUtils = GeorefUtils(node=self._node)
        self._drone_odom: Odometry | None = None
        self._pad_odom: Odometry | None = None
        self._status: ObjectEkfStatus | None = None
        self._status_stamp: Time | None = None
        self._pad_tracker: PadMotionHandler = PadMotionHandler(
            max_observation_age_s=self._max_pad_age_s,
            max_prediction_s=self._max_prediction_s)
        self._relative_position: np.ndarray | None = None
        self._relative_velocity: np.ndarray | None = None
        
        self._pad_input_valid: bool = False
        self._previous_relative_state_valid: bool = False

        # Subscribers
        node.create_subscription(
            Odometry, 
            SmarcTopics.ODOM_TOPIC,
            self._drone_odom_callback, 
            qos_profile_sensor_data)
        
        node.create_subscription(
            ObjectPoseWithCovarianceArray, 
            DJITopics.PROJECTED_OBJECT_POSES_ARRAY_TOPIC,
            self._pose_array_callback, 
            qos_profile_sensor_data)
        
        node.create_subscription(
            ObjectEkfStatusArray, 
            DJITopics.OBJECT_EKF_STATUS_ARRAY_TOPIC,
            self._status_array_callback, 
            qos_profile_sensor_data)

        # TODO: Publisher for cmd_vel and landing_status (might be useful for FSM and control).
        
        # Refresh predictions and detect stale inputs.
        node.create_timer(0.05, self._update_relative_state)

    @property
    def now(self) -> Time:
        """Read the current time from the node's ros clock."""
        return self._node.get_clock().now()
    
    ### Auxiliary methods
    
    def _pose_to_map(self, pose: PoseWithCovariance, frame: str):
        """Transform pose/covariance to map and return the source-to-map rotation."""
        position = vector3_to_numpy(pose.pose.position)
        orientation = rotation(pose.pose.orientation)
        frame_rotation = np.eye(3)
        if frame != self.MAP_FRAME:
            transform = self._georef.lookup_transform(self.MAP_FRAME, frame, timeout_sec=0.02)
            position = transform_point(position, transform)
            frame_rotation = rotation(transform.transform.rotation)
            orientation = frame_rotation @ orientation
        
        covariance = rotate_covariance(pose.covariance, frame_rotation)
        if (not np.isfinite(np.concatenate((position, covariance.ravel()))).all()
                or np.any(np.diag(covariance) < 0)):
            raise ValueError('non-finite pose or invalid covariance')
        
        return position, orientation, covariance, frame_rotation
    
    def _make_odometry(self, header, child_frame, position, orientation, covariance, velocity):
        """Build map-frame odometry with linear velocity expressed in child axes."""
        odometry = Odometry()
        odometry.header = deepcopy(header)
        odometry.header.frame_id = self.MAP_FRAME
        odometry.child_frame_id = child_frame
        odometry.pose.pose.position = Point(x=float(position[0]), y=float(position[1]), z=float(position[2]))
        
        w, x, y, z = mat2quat(orientation)
        odometry.pose.pose.orientation = Quaternion(w=float(w), x=float(x), y=float(y), z=float(z))
        odometry.pose.covariance = covariance.ravel().tolist()
        odometry.twist.twist.linear = numpy_to_vector3(orientation.T @ velocity)
        return odometry

    def _is_ekf_status_valid(self, now) -> bool:
        """Check the latest ekf report and log failures."""
        logger = self._node.get_logger()
        status = self._status
        if status is None or not status.initialized:
            if not self._pad_tracker.prediction_active:
                logger.info('landing-pad EKF is not initialized', throttle_duration_sec=1.0)
            return False
        age = (now - self._status_stamp).nanoseconds * 1e-9
        
        if (self._status_stamp.nanoseconds == 0 or age < -0.05
                or age > self.MAX_STATUS_AGE_S):
            logger.info(f'EKF status timestamp stale or in the future ({age:.3f}s)', throttle_duration_sec=1.0)
            return False
        
        if not 0 <= status.time_since_last_update <= self.MAX_EKF_UPDATE_AGE_S:
            logger.info('EKF update is stale or invalid', throttle_duration_sec=1.0)
            return False
        if status.consecutive_outliers > 0 or status.consecutive_invalid_measurements > 0:
            logger.info('latest EKF measurement was rejected', throttle_duration_sec=1.0)
            return False
        return True

    def _are_relative_inputs_valid(self, now) -> bool:
        """Check the prepared odometries and log failures before relative calculations."""
        logger = self._node.get_logger()
        predicting = self._pad_tracker.prediction_active
        if not predicting and not self._is_ekf_status_valid(now):
            return False
        if self._drone_odom is None or self._pad_odom is None:
            logger.info('waiting for drone and pad data', throttle_duration_sec=1.0)
            return False
        if not predicting and not self._pad_input_valid:
            logger.info('latest pad input is invalid', throttle_duration_sec=1.0)
            return False
        
        drone_stamp = Time.from_msg(self._drone_odom.header.stamp)
        pad_stamp = Time.from_msg(self._pad_odom.header.stamp)
        for name, stamp, max_age in [
            ('drone', drone_stamp, self._max_drone_age_s),
            ('pad', pad_stamp, self._max_pad_age_s),
        ]:
            age = (now - stamp).nanoseconds * 1e-9
            if stamp.nanoseconds == 0 or age < -0.05 or age > max_age:
                logger.info(f'{name} timestamp stale or in the future ({age:.3f}s)', throttle_duration_sec=1.0)
                return False
        if not predicting and not self._pad_tracker.velocity_ready:
            logger.info('waiting for a second pad pose to estimate velocity', throttle_duration_sec=1.0)
            return False
        
        covariance = np.asarray(self._pad_odom.pose.covariance).reshape(6, 6)
        trace = np.trace(covariance[:3, :3])
        max_trace = self.MAX_PAD_POSITION_COV_TRACE
        if not np.isfinite(trace) or (max_trace >= 0 and trace > max_trace):
            logger.info('pad position covariance is too large', throttle_duration_sec=1.0)
            return False
        return True

    ### Callbacks

    def _drone_odom_callback(self, message: Odometry):
        try:
            position, orientation, pose_cov, pose_rotation = self._pose_to_map(message.pose, message.header.frame_id)

            # Rotate velocity from the odometry header frame into map.
            velocity = pose_rotation @ vector3_to_numpy(message.twist.twist.linear)
            angular = pose_rotation @ vector3_to_numpy(message.twist.twist.angular)
            twist_cov = rotate_covariance(message.twist.covariance, pose_rotation)
            child_frame = message.child_frame_id
            if self.LANDING_GEAR_FRAME != child_frame:
                gear_tf = self._georef.lookup_transform(child_frame, self.LANDING_GEAR_FRAME, timeout_sec=0.02)
                offset = orientation @ vector3_to_numpy(gear_tf.transform.translation)
                position = position + offset
                velocity = velocity + np.cross(angular, offset)
                orientation = orientation @ rotation(gear_tf.transform.rotation)
                child_frame = self.LANDING_GEAR_FRAME

            values = np.concatenate((position, velocity, angular, twist_cov.ravel()))
            if not np.isfinite(values).all() or np.any(np.diag(twist_cov) < 0):
                raise ValueError('non-finite state or invalid covariance')

            odometry = self._make_odometry(message.header, child_frame, position, orientation, pose_cov, velocity)
            odometry.twist.twist.angular = numpy_to_vector3(orientation.T @ angular)
            odometry.twist.covariance = rotate_covariance(twist_cov, orientation.T).ravel().tolist()
            self._drone_odom = odometry

        except (TransformException, ValueError) as error:
            self._drone_odom = None
            self._node.get_logger().info(f'drone transform failed: {error}', throttle_duration_sec=1.0)

    def _pose_array_callback(self, message: ObjectPoseWithCovarianceArray):
        target = self.PAD_CLASS_NAME
        estimate = next((item for item in message.objects if item.class_name == target), None)
        if estimate is None:
            return

        try:
            # Validate the pad estimate, convert it to map and update its motion history.
            header = deepcopy(estimate.header)
            if not header.frame_id:
                header.frame_id = message.header.frame_id
            if Time.from_msg(header.stamp).nanoseconds == 0:
                header.stamp = deepcopy(message.header.stamp)
            stamp = Time.from_msg(header.stamp)
            
            # Other classes can cause the ekf array to repeat this old track.
            last_stamp = self._pad_tracker.last_observation_stamp
            if last_stamp is not None and stamp <= last_stamp:
                return
            now = self.now
            age = (now - stamp).nanoseconds * 1e-9
            if stamp.nanoseconds == 0 or not 0 <= age <= self._pad_tracker.max_observation_age_s:
                raise ValueError('pad timestamp is stale or in the future')
            if not self._is_ekf_status_valid(now):
                self._pad_tracker.reject_observation()
                self._pad_input_valid = False
                return
            position, orientation, covariance, _ = self._pose_to_map(estimate.pose, header.frame_id)
            limit = self.MAX_PAD_POSITION_COV_TRACE
            if limit >= 0 and np.trace(covariance[:3, :3]) > limit:
                raise ValueError('pad position covariance is too large')

            odometry = self._make_odometry(header, self._TF_NS + target, position, orientation,
                covariance, np.zeros(3))
            self._pad_tracker.observe(odometry, now)
            self._pad_input_valid = True
    
        except (TransformException, ValueError) as error:
            self._pad_tracker.reject_observation()
            self._pad_input_valid = False
            self._node.get_logger().info(f'pad data invalid: {error}', throttle_duration_sec=1.0)

    def _status_array_callback(self, message: ObjectEkfStatusArray):
        target = self.PAD_CLASS_NAME
        self._status = next((status for status in message.statuses
                                if status.class_name == target), None)
        self._status_stamp = Time.from_msg(message.header.stamp)
        now = self.now
        if self._status is None or not self._status.initialized:
            # The ekf reset must not clear a bounded forecast that remains authorized.
            source_age = self._pad_tracker.observation_age(now)
            if not (self._enable_dropout_prediction
                    and 0 <= source_age <= self._pad_tracker.max_prediction_s):
                self._pad_tracker.reset()
        if not self._is_ekf_status_valid(now):
            self._pad_tracker.reject_observation()

    ### Relative state update (only a logger for now, might need a proper topic later with FSM)

    def _update_relative_state(self):
        """Update the relative position and velocity of the drone with respect to the pad."""
        now = self.now
        prediction = self._pad_tracker.predict(now, enabled=self._enable_dropout_prediction)
        self._pad_odom = (prediction if prediction is not None
                            else self._pad_tracker.last_observation)
        inputs_valid = self._are_relative_inputs_valid(now)
        if inputs_valid != self._previous_relative_state_valid:
            self._node.get_logger().info('Relative landing state is valid' if inputs_valid
                else 'Relative landing state is invalid')
        self._previous_relative_state_valid = inputs_valid
        if not inputs_valid:
            self._relative_position = self._relative_velocity = None
            return

        drone_pose = self._drone_odom.pose.pose
        pad_pose = self._pad_odom.pose.pose
        self._relative_position = (vector3_to_numpy(drone_pose.position) - vector3_to_numpy(pad_pose.position))
        
        # Odometry twists compare both velocities in map.
        drone_velocity = rotation(drone_pose.orientation) @ vector3_to_numpy(self._drone_odom.twist.twist.linear)
        pad_velocity = rotation(pad_pose.orientation) @ vector3_to_numpy(self._pad_odom.twist.twist.linear)
        self._relative_velocity = drone_velocity - pad_velocity
        p, v = self._relative_position, self._relative_velocity
        self._node.get_logger().info(
            f'Relative state in {self.MAP_FRAME} (drone - pad, '
            f'{"predicted" if self._pad_tracker.prediction_active else "observed"} pad, '
            f'observation age={self._pad_tracker.observation_age(now):.2f}s, '
            f'update gap={self._pad_tracker.update_gap(now):.2f}s): '
            f'position=[{p[0]:.2f}, {p[1]:.2f}, {p[2]:.2f}] m, '
            f'velocity=[{v[0]:.2f}, {v[1]:.2f}, {v[2]:.2f}] m/s, '
            f'xy={np.linalg.norm(p[:2]):.2f} m, height={p[2]:.2f} m',
            throttle_duration_sec=1.0)
    
def main(args=None):
    
    rclpy.init(args=args)
    node = Node('PadLandingNode')
    action = PadLandingAS(node)
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        action._georef.shutdown()
        action._as._server.destroy()
        node.destroy_node()
        rclpy.try_shutdown()