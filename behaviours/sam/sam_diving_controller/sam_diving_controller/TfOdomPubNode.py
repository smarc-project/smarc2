#!/usr/bin/env python3
import math
from dataclasses import dataclass

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.time import Time

from nav_msgs.msg import Odometry

from tf2_ros import Buffer, TransformListener
from tf2_ros import LookupException, ConnectivityException, ExtrapolationException


def quat_normalize(q):
    x, y, z, w = q
    n = math.sqrt(x*x + y*y + z*z + w*w)
    if n <= 1e-12:
        return (0.0, 0.0, 0.0, 1.0)
    return (x/n, y/n, z/n, w/n)


def quat_conjugate(q):
    x, y, z, w = q
    return (-x, -y, -z, w)


def quat_multiply(q1, q2):
    # Hamilton product: q = q1 ⊗ q2
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2
    return (
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2,
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
    )


def quat_inverse(q):
    # assuming normalized
    return quat_conjugate(q)


def quat_to_rotmat(q):
    # q = (x,y,z,w), normalized
    x, y, z, w = quat_normalize(q)
    xx, yy, zz = x*x, y*y, z*z
    xy, xz, yz = x*y, x*z, y*z
    wx, wy, wz = w*x, w*y, w*z

    # Row-major 3x3
    return (
        (1.0 - 2.0*(yy + zz), 2.0*(xy - wz),       2.0*(xz + wy)),
        (2.0*(xy + wz),       1.0 - 2.0*(xx + zz), 2.0*(yz - wx)),
        (2.0*(xz - wy),       2.0*(yz + wx),       1.0 - 2.0*(xx + yy)),
    )


def rotmat_transpose(R):
    return (
        (R[0][0], R[1][0], R[2][0]),
        (R[0][1], R[1][1], R[2][1]),
        (R[0][2], R[1][2], R[2][2]),
    )


def matvec(R, v):
    return (
        R[0][0]*v[0] + R[0][1]*v[1] + R[0][2]*v[2],
        R[1][0]*v[0] + R[1][1]*v[1] + R[1][2]*v[2],
        R[2][0]*v[0] + R[2][1]*v[1] + R[2][2]*v[2],
    )


def quat_delta_to_omega(q_prev, q_curr, dt):
    """
    Compute angular velocity (omega) from q_prev -> q_curr over dt.
    Returned omega is expressed in the *world/parent* frame (here: odom),
    then you can rotate it into base_link if desired.
    """
    if dt <= 1e-6:
        return (0.0, 0.0, 0.0)

    q_prev = quat_normalize(q_prev)
    q_curr = quat_normalize(q_curr)

    # Relative rotation: q_rel = q_prev^{-1} ⊗ q_curr
    q_rel = quat_multiply(quat_inverse(q_prev), q_curr)
    q_rel = quat_normalize(q_rel)

    x, y, z, w = q_rel

    # Clamp for safety
    w = max(-1.0, min(1.0, w))

    # Axis-angle
    angle = 2.0 * math.acos(w)
    # Map angle to [-pi, pi] for the "short" rotation
    if angle > math.pi:
        angle -= 2.0 * math.pi

    s = math.sqrt(max(0.0, 1.0 - w*w))  # = |sin(angle/2)|
    if s < 1e-8 or abs(angle) < 1e-8:
        return (0.0, 0.0, 0.0)

    axis = (x / s, y / s, z / s)
    return (axis[0] * angle / dt, axis[1] * angle / dt, axis[2] * angle / dt)


@dataclass
class PrevState:
    t: Time
    p: tuple  # (x,y,z) in odom
    q: tuple  # (x,y,z,w) orientation of base_link in odom


class TfToOdometryNode(Node):
    def __init__(self):
        super().__init__("tf_to_odometry")

        # Frames / timing
        self.declare_parameter("parent_frame", "sam_david/odom")
        self.declare_parameter("child_frame", "sam_david/base_link")
        self.declare_parameter("odom_topic", "sam_david/odom_tf")
        self.declare_parameter("publish_rate_hz", 50.0)
        self.declare_parameter("tf_timeout_sec", 0.1)

        # Velocity filtering (optional)
        # alpha=1.0 means no filtering; smaller => smoother/slower
        self.declare_parameter("vel_lpf_alpha", 1.0)

        self.parent_frame = self.get_parameter("parent_frame").value
        self.child_frame = self.get_parameter("child_frame").value
        self.odom_topic = self.get_parameter("odom_topic").value
        self.publish_rate_hz = float(self.get_parameter("publish_rate_hz").value)
        self.tf_timeout_sec = float(self.get_parameter("tf_timeout_sec").value)
        self.vel_lpf_alpha = float(self.get_parameter("vel_lpf_alpha").value)

        self.vel_lpf_alpha = max(0.0, min(1.0, self.vel_lpf_alpha))

        self.pub = self.create_publisher(Odometry, self.odom_topic, 10)

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.prev: PrevState | None = None
        self.filt_v = (0.0, 0.0, 0.0)     # filtered linear vel in base_link
        self.filt_w = (0.0, 0.0, 0.0)     # filtered angular vel in base_link

        period = 1.0 / max(self.publish_rate_hz, 1e-6)
        self.timer = self.create_timer(period, self.on_timer)

        self.get_logger().info(
            f"TF->Odom: {self.parent_frame} -> {self.child_frame}, publishing '{self.odom_topic}', "
            f"{self.publish_rate_hz:.1f} Hz, vel_lpf_alpha={self.vel_lpf_alpha:.2f}"
        )

    def on_timer(self):
        try:
            tf = self.tf_buffer.lookup_transform(
                self.parent_frame,
                self.child_frame,
                rclpy.time.Time(),  # latest
                timeout=Duration(seconds=self.tf_timeout_sec),
            )
        except (LookupException, ConnectivityException, ExtrapolationException) as e:
            self.get_logger().warn(
                f"TF lookup failed ({self.parent_frame} -> {self.child_frame}): {e}",
                throttle_duration_sec=2.0,
            )
            return

        # Use the TF timestamp for consistent dt
        t_tf = Time.from_msg(tf.header.stamp)

        p = (
            tf.transform.translation.x,
            tf.transform.translation.y,
            tf.transform.translation.z,
        )
        q = (
            tf.transform.rotation.x,
            tf.transform.rotation.y,
            tf.transform.rotation.z,
            tf.transform.rotation.w,
        )
        q = quat_normalize(q)

        # Compute twist by differencing, then express in base_link.
        # When dt is invalid (first message or duplicate/non-increasing TF stamp), keep previous
        # filtered velocity so we don't publish zero "every now and then" and confuse the MPC.
        if self.prev is not None:
            dt = (t_tf - self.prev.t).nanoseconds * 1e-9
            if dt > 1e-6:
                # linear velocity in odom (world) frame
                v_odom = (
                    (p[0] - self.prev.p[0]) / dt,
                    (p[1] - self.prev.p[1]) / dt,
                    (p[2] - self.prev.p[2]) / dt,
                )

                # angular velocity in odom frame (approx)
                w_odom = quat_delta_to_omega(self.prev.q, q, dt)

                # rotate both into base_link: v_base = R^T * v_odom
                R = quat_to_rotmat(q)          # maps base->odom
                Rt = rotmat_transpose(R)       # maps odom->base
                v_base = matvec(Rt, v_odom)
                w_base = matvec(Rt, w_odom)

                # optional low-pass filter
                a = self.vel_lpf_alpha
                self.filt_v = (
                    a * v_base[0] + (1.0 - a) * self.filt_v[0],
                    a * v_base[1] + (1.0 - a) * self.filt_v[1],
                    a * v_base[2] + (1.0 - a) * self.filt_v[2],
                )
                self.filt_w = (
                    a * w_base[0] + (1.0 - a) * self.filt_w[0],
                    a * w_base[1] + (1.0 - a) * self.filt_w[1],
                    a * w_base[2] + (1.0 - a) * self.filt_w[2],
                )

        # Always publish current filtered velocity (avoids zeros when dt too small or duplicate TF stamps)
        v_base = self.filt_v
        w_base = self.filt_w

        # Update prev AFTER computations
        self.prev = PrevState(t=t_tf, p=p, q=q)

        # Publish Odometry
        msg = Odometry()
        # You can choose node clock time or tf time; tf time is often preferable for fusion
        msg.header.stamp = tf.header.stamp
        msg.header.frame_id = self.parent_frame
        msg.child_frame_id = self.child_frame

        msg.pose.pose.position.x = p[0]
        msg.pose.pose.position.y = p[1]
        msg.pose.pose.position.z = p[2]
        msg.pose.pose.orientation.x = q[0]
        msg.pose.pose.orientation.y = q[1]
        msg.pose.pose.orientation.z = q[2]
        msg.pose.pose.orientation.w = q[3]

        # Twist expressed in child frame (base_link) by convention
        msg.twist.twist.linear.x = v_base[0]
        msg.twist.twist.linear.y = v_base[1]
        msg.twist.twist.linear.z = v_base[2]
        msg.twist.twist.angular.x = w_base[0]
        msg.twist.twist.angular.y = w_base[1]
        msg.twist.twist.angular.z = w_base[2]

        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TfToOdometryNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
