#!/usr/bin/python

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

from geometry_msgs.msg import Twist, Vector3
from yolo_msgs.msg import DetectionArray

from smarc_action_base.gentler_action_server import GentlerActionServer
from active_hook_msgs.msg import Topics as ActiveHookTopics


class SearchingSamAction():
    def __init__(self, node: Node):
        self._node = node

        self._node.declare_parameter("pitch_start", -50.0)   # negative because of sim
        self._node.declare_parameter("pitch_end", 50.0)      # positive because of sim
        self._node.declare_parameter("pitch_settle_tolerance", 5.0)   # tolerance for pitch settling

        self._node.declare_parameter("pitch_kp", 0.1)   
        self._node.declare_parameter("roll_kp", 0.06)    
        self._node.declare_parameter("max_pitch_cmd", 0.5)
        self._node.declare_parameter("max_roll_cmd", 1.0)

        self._node.declare_parameter("yaw_rate", 0.7)   # constant

        self._node.declare_parameter("timeout", 120.0)   # total safety cutoff, seconds, counted from goal start (climb included)

        self._node.declare_parameter("detection_topic", "yolo/detections")
        self._node.declare_parameter("target_class", "sam")
        self._node.declare_parameter("detection_min_score", 0.5)
        self._node.declare_parameter("detection_confirm_count", 3)   

        self._node.declare_parameter("loop_frequency", 20.0)

        self._pitch_start = self._node.get_parameter("pitch_start").value
        self._pitch_end = self._node.get_parameter("pitch_end").value
        self._pitch_settle_tolerance = self._node.get_parameter("pitch_settle_tolerance").value

        self._pitch_kp = self._node.get_parameter("pitch_kp").value
        self._roll_kp = self._node.get_parameter("roll_kp").value
        self._max_pitch_cmd = self._node.get_parameter("max_pitch_cmd").value
        self._max_roll_cmd = self._node.get_parameter("max_roll_cmd").value

        self._yaw_rate = self._node.get_parameter("yaw_rate").value

        self._timeout = self._node.get_parameter("timeout").value

        detection_topic = self._node.get_parameter("detection_topic").value
        self._default_target_class = self._node.get_parameter("target_class").value
        self._detection_min_score = self._node.get_parameter("detection_min_score").value
        self._detection_confirm_count = self._node.get_parameter("detection_confirm_count").value

        loop_freq = self._node.get_parameter("loop_frequency").value

        self._latest_attitude: Vector3 | None = None
        self._node.create_subscription(
            Vector3, ActiveHookTopics.ATTITUDE_TOPIC, self._attitude_callback, 10
        )

        self._node.create_subscription(
            DetectionArray, detection_topic, self._detection_callback, 10
        )

        self._cmd_vel_pub = self._node.create_publisher(
            Twist, ActiveHookTopics.AUTONOMY_CMD_VEL_TOPIC, 10
        )

        
        self._target_class = self._default_target_class
        self._start_time = None
        self._climbed = False
        self._spiral_start_time = None

        # yaw travel is only tracked for feedback
        self._prev_raw_yaw: float | None = None
        self._yaw_accum: float = 0.0

        self._confirm_streak: int = 0
        self._target_confirmed: bool = False

        self._last_pitch_target = 0.0

        self._as = GentlerActionServer(
            node, "searching_sam",
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency=loop_freq,
        )

    def _attitude_callback(self, msg: Vector3) -> None:
        self._latest_attitude = msg

    def _detection_callback(self, msg: DetectionArray) -> None:
        seen_this_frame = any(
            det.class_name == self._target_class and det.score >= self._detection_min_score
            for det in msg.detections
        )

        if seen_this_frame:
            self._confirm_streak += 1
        else:
            self._confirm_streak = 0

        if self._confirm_streak >= self._detection_confirm_count:
            self._target_confirmed = True

    def _on_goal_received(self, goal_request: dict) -> bool:
        if self._latest_attitude is None:
            self._node.get_logger().error("No attitude data received yet, rejecting goal")
            return False

        self._target_class = str(goal_request.get('target_class', self._default_target_class))
        return True

    def _on_cancel_received(self) -> bool:
        self._cmd_vel_pub.publish(Twist())
        return True

    def _prepare_loop(self) -> None:
        self._start_time = self._node.get_clock().now()
        self._climbed = False
        self._spiral_start_time = None
        self._prev_raw_yaw = None
        self._yaw_accum = 0.0
        self._confirm_streak = 0
        self._target_confirmed = False

    def _loop_inner(self) -> bool | None:
        if self._latest_attitude is None:
            return None

        elapsed = (self._node.get_clock().now() - self._start_time).nanoseconds / 1e9
        if elapsed >= self._timeout:
            self._node.get_logger().error(
                f"Search timed out after {elapsed:.1f}s without a confirmed "
                f"'{self._target_class}' detection."
            )
            self._cmd_vel_pub.publish(Twist())
            return False

        # --- if the target is confirmed, stop immediately ---
        if self._target_confirmed:
            self._node.get_logger().info(
                f"'{self._target_class}' confirmed ({self._detection_confirm_count} "
                f"consecutive frames) -- ending search."
            )
            self._cmd_vel_pub.publish(Twist())
            return True

        current_roll = self._latest_attitude.x
        current_pitch = self._latest_attitude.y
        current_yaw = self._latest_attitude.z   # sensor only ever reports (-180, 180]

        # roll target is always 0 (stay level), active in both phases.
        roll_error = ((0.0 - current_roll + 180.0) % 360.0) - 180.0
        roll_cmd = max(-self._max_roll_cmd, min(self._max_roll_cmd, -self._roll_kp * roll_error))

        if not self._climbed:
            # --- phase 1: get pitch to pitch_start first, yaw stays put ---
            pitch_error = self._pitch_start - current_pitch
            pitch_cmd = max(-self._max_pitch_cmd, min(self._max_pitch_cmd, self._pitch_kp * pitch_error))
            yaw_cmd = 0.0

            self._last_pitch_target = self._pitch_start

            if abs(current_pitch - self._pitch_start) < self._pitch_settle_tolerance:
                self._climbed = True
                self._spiral_start_time = self._node.get_clock().now()
                self._prev_raw_yaw = current_yaw
                self._yaw_accum = 0.0
        else:
            # --- phase 2: the actual spiral ---
            spiral_elapsed = (self._node.get_clock().now() - self._spiral_start_time).nanoseconds / 1e9
            progress = min(1.0, spiral_elapsed / self._timeout)
            pitch_target = self._pitch_start + (self._pitch_end - self._pitch_start) * progress

            self._last_pitch_target = pitch_target

            pitch_error = pitch_target - current_pitch
            pitch_cmd = max(-self._max_pitch_cmd, min(self._max_pitch_cmd, self._pitch_kp * pitch_error))

            # yaw: constant, open-loop spin -- see docstring for why this
            # is NOT closed-loop tracking a moving target
            yaw_cmd = self._yaw_rate

            # track how far we've actually spun, for feedback only 
            delta = current_yaw - self._prev_raw_yaw
            if delta > 180.0:
                delta -= 360.0
            elif delta < -180.0:
                delta += 360.0
            self._yaw_accum += delta
            self._prev_raw_yaw = current_yaw

        twist = Twist()
        twist.angular.x = roll_cmd
        twist.angular.y = pitch_cmd
        twist.angular.z = yaw_cmd
        self._cmd_vel_pub.publish(twist)

        return None

    def _give_feedback(self) -> str:
        phase = "spiral" if self._climbed else "climbing to start"
        return (
            f"[{phase}] roll {self._latest_attitude.x:.0f} | "
            f"pitch {self._latest_attitude.y:.0f}->{self._last_pitch_target:.0f} | "
            f"yaw {self._latest_attitude.z:.0f} (spun {abs(self._yaw_accum):.0f} deg so far) | "
            f"detection streak {self._confirm_streak}/{self._detection_confirm_count}"
        )


def main():
    rclpy.init()
    node = Node("searching_sam_action_server")
    SearchingSamAction(node)

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()