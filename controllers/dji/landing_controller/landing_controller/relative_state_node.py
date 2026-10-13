from dataclasses import dataclass
from typing import Optional

import numpy as np
import rclpy
from dji_msgs.msg import LandingRelativeState, Links as DJILinks, Topics as DJITopics
from nav_msgs.msg import Odometry
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from smarc_msgs.msg import Topics as SmarcTopics
from tf2_ros import Buffer, TransformException, TransformListener

from .math_utils import (
    numpy_to_point,
    numpy_to_vector3,
    point_to_numpy,
    quaternion_to_rotation_matrix,
    transform_point,
    transform_vector,
    vector3_to_numpy,
)

@dataclass
class StateSample:
    position: np.ndarray
    velocity: np.ndarray
    stamp: Time
    pose_cov_trace: float
    twist_cov_trace: float

class RelativeStateNode(Node):
    def __init__(self, **node_kwargs) -> None:
        super().__init__("landing_relative_state", **node_kwargs)

        self.declare_parameter("drone_odom_topic", SmarcTopics.ODOM_TOPIC)
        self.declare_parameter("pad_odom_topic", DJITopics.PAD_ODOM_TOPIC)
        self.declare_parameter("output_topic", DJITopics.RELATIVE_STATE_TOPIC)
        self.declare_parameter("map_frame", DJILinks.MAP)
        # A frame rigidly attached to the odometry child. Empty keeps the
        # original odometry reference point; the stack selects the landing gear.
        self.declare_parameter("drone_reference_frame", "")
        self.declare_parameter("publish_rate_hz", 50.0)
        self.declare_parameter("max_drone_age_s", 0.20)
        self.declare_parameter("max_pad_age_s", 0.25)
        self.declare_parameter("max_pad_position_cov_trace", 1.0)
        self.declare_parameter("max_pad_velocity_cov_trace", 2.0)
        self.declare_parameter("zero_covariance_is_valid", True)
        self.declare_parameter("latency_compensation", True)
        self.declare_parameter("max_prediction_horizon_s", 0.30)
        self.declare_parameter("tf_timeout_s", 0.05)
        self.declare_parameter("tf_fallback_to_latest", True)
        self.declare_parameter("replace_zero_stamp_with_now", True)
        self.declare_parameter("drone_twist_frame_mode", "child")
        self.declare_parameter("pad_twist_frame_mode", "header")
        self.declare_parameter("drone_twist_frame", "")
        self.declare_parameter("pad_twist_frame", "")

        self._map_frame = self.get_parameter("map_frame").value
        self._tf_timeout = float(self.get_parameter("tf_timeout_s").value)
        self._tf_fallback = bool(self.get_parameter("tf_fallback_to_latest").value)
        self._buffer = Buffer(node=self)
        self._listener = TransformListener(self._buffer, self)

        self._latest_drone: Optional[Odometry] = None
        self._latest_pad: Optional[Odometry] = None

        self.create_subscription(
            Odometry,
            str(self.get_parameter("drone_odom_topic").value),
            self._drone_callback,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            Odometry,
            str(self.get_parameter("pad_odom_topic").value),
            self._pad_callback,
            qos_profile_sensor_data,
        )
        self._publisher = self.create_publisher(
            LandingRelativeState,
            str(self.get_parameter("output_topic").value),
            20,
        )

        rate = float(self.get_parameter("publish_rate_hz").value)
        if rate <= 0.0:
            raise ValueError("publish_rate_hz must be positive")
        self.create_timer(1.0 / rate, self._timer_callback)

    def _drone_callback(self, message: Odometry) -> None:
        self._latest_drone = message

    def _pad_callback(self, message: Odometry) -> None:
        self._latest_pad = message

    @staticmethod
    def _covariance_trace(covariance: list[float] | tuple[float, ...]) -> float:
        if len(covariance) < 15:
            return float("inf")
        return float(covariance[0] + covariance[7] + covariance[14])

    def _lookup_transform(self, target: str, source: str, stamp: Time):
        if target == source or source == "":
            return None
        try:
            return self._buffer.lookup_transform(
                target,
                source,
                stamp,
                timeout=Duration(seconds=self._tf_timeout),
            )
        except TransformException:
            if not self._tf_fallback:
                raise
            return self._buffer.lookup_transform(
                target,
                source,
                Time(),
                timeout=Duration(seconds=self._tf_timeout),
            )

    def _twist_frame(self, message: Odometry, prefix: str) -> str:
        explicit = str(self.get_parameter(f"{prefix}_twist_frame").value)
        if explicit:
            return explicit
        mode = str(self.get_parameter(f"{prefix}_twist_frame_mode").value).lower()
        if mode == "header":
            return message.header.frame_id
        if mode == "child":
            return message.child_frame_id or message.header.frame_id
        raise ValueError(f"{prefix}_twist_frame_mode must be 'header' or 'child'")

    def _convert_odom(self, message: Odometry, prefix: str) -> StateSample:
        pose_frame = message.header.frame_id or self._map_frame
        stamp = Time.from_msg(message.header.stamp)
        if stamp.nanoseconds == 0 and bool(
            self.get_parameter("replace_zero_stamp_with_now").value
        ):
            stamp = self.get_clock().now()
        position = point_to_numpy(message.pose.pose.position)
        pose_tf = None
        if pose_frame != self._map_frame:
            pose_tf = self._lookup_transform(self._map_frame, pose_frame, stamp)
            if pose_tf is not None:
                position = transform_point(position, pose_tf)

        velocity = vector3_to_numpy(message.twist.twist.linear)
        velocity_frame = self._twist_frame(message, prefix)
        velocity_tf = None
        if velocity_frame != self._map_frame:
            velocity_tf = self._lookup_transform(self._map_frame, velocity_frame, stamp)
            if velocity_tf is not None:
                velocity = transform_vector(velocity, velocity_tf)

        if prefix == "drone":
            reference_frame = str(self.get_parameter("drone_reference_frame").value)
            if reference_frame and reference_frame != message.child_frame_id:
                if not message.child_frame_id:
                    raise ValueError(
                        "drone child_frame_id is required to locate the landing reference frame"
                    )
                # Use odometry's pose at its own timestamp and only the rigid
                # body-to-gear TF. No independent world/body or pad ground-truth
                # transform is substituted for the measured drone position.
                reference_tf = self._lookup_transform(
                    message.child_frame_id, reference_frame, stamp
                )
                rotation = quaternion_to_rotation_matrix(message.pose.pose.orientation)
                if pose_tf is not None:
                    rotation = (
                        quaternion_to_rotation_matrix(pose_tf.transform.rotation) @ rotation
                    )
                offset = rotation @ vector3_to_numpy(reference_tf.transform.translation)
                position = position + offset

                # Velocity at the gear differs from body-origin velocity during
                # roll/pitch/yaw motion: v_gear = v_body + omega x offset.
                angular_velocity = vector3_to_numpy(message.twist.twist.angular)
                if velocity_tf is not None:
                    angular_velocity = transform_vector(angular_velocity, velocity_tf)
                velocity = velocity + np.cross(angular_velocity, offset)

        return StateSample(
            position=position,
            velocity=velocity,
            stamp=stamp,
            pose_cov_trace=self._covariance_trace(message.pose.covariance),
            twist_cov_trace=self._covariance_trace(message.twist.covariance),
        )

    def _timer_callback(self) -> None:
        now = self.get_clock().now()
        output = LandingRelativeState()
        output.header.stamp = now.to_msg()
        output.header.frame_id = self._map_frame

        reasons: list[str] = []
        drone: Optional[StateSample] = None
        pad: Optional[StateSample] = None

        if self._latest_drone is None:
            reasons.append("no drone odometry")
        else:
            try:
                drone = self._convert_odom(self._latest_drone, "drone")
            except (TransformException, ValueError) as error:
                reasons.append(f"drone transform failed: {error}")

        if self._latest_pad is None:
            reasons.append("no pad odometry")
        else:
            try:
                pad = self._convert_odom(self._latest_pad, "pad")
            except (TransformException, ValueError) as error:
                reasons.append(f"pad transform failed: {error}")

        if drone is None or pad is None:
            output.valid = False
            output.invalid_reason = "; ".join(reasons)
            self._publisher.publish(output)
            return

        drone_age = max(0.0, (now - drone.stamp).nanoseconds * 1e-9)
        pad_age = max(0.0, (now - pad.stamp).nanoseconds * 1e-9)
        output.drone_age = drone_age
        output.pad_age = pad_age
        output.pad_position_covariance_trace = pad.pose_cov_trace
        output.pad_velocity_covariance_trace = pad.twist_cov_trace

        max_drone_age = float(self.get_parameter("max_drone_age_s").value)
        max_pad_age = float(self.get_parameter("max_pad_age_s").value)
        if drone_age > max_drone_age:
            reasons.append(f"drone state stale ({drone_age:.3f}s)")
        if pad_age > max_pad_age:
            reasons.append(f"pad state stale ({pad_age:.3f}s)")

        zero_cov_valid = bool(self.get_parameter("zero_covariance_is_valid").value)
        position_limit = float(self.get_parameter("max_pad_position_cov_trace").value)
        velocity_limit = float(self.get_parameter("max_pad_velocity_cov_trace").value)
        if not (zero_cov_valid and abs(pad.pose_cov_trace) < 1e-12):
            if position_limit >= 0.0 and pad.pose_cov_trace > position_limit:
                reasons.append(
                    f"pad position covariance trace too high ({pad.pose_cov_trace:.3g})"
                )
        if not (zero_cov_valid and abs(pad.twist_cov_trace) < 1e-12):
            if velocity_limit >= 0.0 and pad.twist_cov_trace > velocity_limit:
                reasons.append(
                    f"pad velocity covariance trace too high ({pad.twist_cov_trace:.3g})"
                )

        if bool(self.get_parameter("latency_compensation").value):
            horizon = float(self.get_parameter("max_prediction_horizon_s").value)
            drone_prediction = min(drone_age, horizon)
            pad_prediction = min(pad_age, horizon)
            drone.position = drone.position + drone.velocity * drone_prediction
            pad.position = pad.position + pad.velocity * pad_prediction

        relative_position = drone.position - pad.position
        relative_velocity = drone.velocity - pad.velocity

        output.drone_position = numpy_to_point(drone.position)
        output.drone_velocity = numpy_to_vector3(drone.velocity)
        output.pad_position = numpy_to_point(pad.position)
        output.pad_velocity = numpy_to_vector3(pad.velocity)
        output.relative_position = numpy_to_vector3(relative_position)
        output.relative_velocity = numpy_to_vector3(relative_velocity)
        output.valid = len(reasons) == 0
        output.invalid_reason = "; ".join(reasons)
        self._publisher.publish(output)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = RelativeStateNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        # ROS may already have shut the context down while handling SIGINT.
        if rclpy.ok():
            rclpy.shutdown()
