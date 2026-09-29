#!/usr/bin/python

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

from geometry_msgs.msg import Twist, Vector3
from yolo_msgs.msg import DetectionArray

from smarc_action_base.gentler_action_server import GentlerActionServer
from active_hook_msgs.msg import Topics as ActiveHookTopics


class ApproachingSamAction():
    def __init__(self, node: Node):
        self._node = node

        self._node.declare_parameter("detection_topic", "yolo/detections")
        self._node.declare_parameter("target_class", "sam")
        self._node.declare_parameter("detection_min_score", 0.5)

        self._node.declare_parameter("image_width", 640.0)
        self._node.declare_parameter("image_height", 480.0)
        self._node.declare_parameter("yaw_kp", 1.5)     # horizontal centering gain
        self._node.declare_parameter("pitch_kp", 1.0)   # vertical centering gain

        self._node.declare_parameter("roll_kp", 0.06)   
        self._node.declare_parameter("max_roll_cmd", 1.0)

        self._node.declare_parameter("forward_kp", 2.0)            
        self._node.declare_parameter("max_forward_cmd", 0.85)      
        self._node.declare_parameter("target_bbox_width", 550.0)   # stop once sam's bbox is at least this wide, in pixels

        self._node.declare_parameter("lost_timeout", 3.0)   # give up if sam isn't seen for this long, seconds
        self._node.declare_parameter("timeout", 120.0)      # overall safety cutoff (seconds)
        self._node.declare_parameter("loop_frequency", 20.0)

        detection_topic = self._node.get_parameter("detection_topic").value
        self._default_target_class = self._node.get_parameter("target_class").value
        self._detection_min_score = self._node.get_parameter("detection_min_score").value

        self._image_width = self._node.get_parameter("image_width").value
        self._image_height = self._node.get_parameter("image_height").value
        self._yaw_kp = self._node.get_parameter("yaw_kp").value
        self._pitch_kp = self._node.get_parameter("pitch_kp").value

        self._roll_kp = self._node.get_parameter("roll_kp").value
        self._max_roll_cmd = self._node.get_parameter("max_roll_cmd").value

        self._forward_kp = self._node.get_parameter("forward_kp").value
        self._max_forward_cmd = self._node.get_parameter("max_forward_cmd").value
        self._target_bbox_width = self._node.get_parameter("target_bbox_width").value

        self._lost_timeout = self._node.get_parameter("lost_timeout").value
        self._timeout = self._node.get_parameter("timeout").value
        loop_freq = self._node.get_parameter("loop_frequency").value

        self._node.create_subscription(
            DetectionArray, detection_topic, self._detection_callback, 10
        )
        self._node.create_subscription(
            Vector3, ActiveHookTopics.ATTITUDE_TOPIC, self._attitude_callback, 10
        )
        self._cmd_vel_pub = self._node.create_publisher(
            Twist, ActiveHookTopics.AUTONOMY_CMD_VEL_TOPIC, 10
        )

        self._target_class = self._default_target_class
        self._start_time = None
        self._latest_bbox = None
        self._last_seen_time = None
        self._latest_attitude: Vector3 | None = None

        self._as = GentlerActionServer(
            node, "approaching_sam",
            self._on_goal_received, self._on_cancel_received,
            self._prepare_loop, self._loop_inner, self._give_feedback,
            loop_frequency=loop_freq,
        )

    def _detection_callback(self, msg: DetectionArray) -> None:
        candidates = [
            det for det in msg.detections
            if det.class_name == self._target_class and det.score >= self._detection_min_score
        ]
        if not candidates:
            return

        best = max(candidates, key=lambda det: det.score)
        self._latest_bbox = best.bbox
        self._last_seen_time = self._node.get_clock().now()

    def _attitude_callback(self, msg: Vector3) -> None:
        self._latest_attitude = msg

    def _on_goal_received(self, goal_request: dict) -> bool:
        self._target_class = str(goal_request.get('target_class', self._default_target_class))

        if self._latest_bbox is None:
            self._node.get_logger().error(
                f"No recent '{self._target_class}' detection yet, rejecting goal"
            )
            return False

        return True

    def _on_cancel_received(self) -> bool:
        self._cmd_vel_pub.publish(Twist())
        return True

    def _prepare_loop(self) -> None:
        self._start_time = self._node.get_clock().now()

    def _loop_inner(self) -> bool | None:
        elapsed = (self._node.get_clock().now() - self._start_time).nanoseconds / 1e9
        if elapsed >= self._timeout:
            self._node.get_logger().error(f"Approach timed out after {elapsed:.1f}s.")
            self._cmd_vel_pub.publish(Twist())
            return False

        since_seen = (self._node.get_clock().now() - self._last_seen_time).nanoseconds / 1e9
        if since_seen >= self._lost_timeout:
            self._node.get_logger().error(
                f"Lost '{self._target_class}' for {since_seen:.1f}s -- giving up."
            )
            self._cmd_vel_pub.publish(Twist())
            return False

        bbox = self._latest_bbox

        if bbox.size.x >= self._target_bbox_width:
            self._node.get_logger().info(f"Close enough to '{self._target_class}' -- stopping.")
            self._cmd_vel_pub.publish(Twist())
            return True

        # forward speed
        size_error = self._target_bbox_width - bbox.size.x
        normalized_size_error = max(0.0, min(1.0, size_error / self._target_bbox_width))
        forward_cmd = max(0.0, min(self._max_forward_cmd, self._forward_kp * normalized_size_error))

        # center horizontally (yaw) and vertically (pitch): error and command
        error_x = bbox.center.position.x - self._image_width / 2.0
        error_y = bbox.center.position.y - self._image_height / 2.0

        yaw_cmd = self._yaw_kp * (error_x / (self._image_width / 2.0))
        pitch_cmd = self._pitch_kp * (error_y / (self._image_height / 2.0))

        # roll-hold: cancels the roll drift that pitch+yaw induce together
        if self._latest_attitude is not None:
            current_roll = self._latest_attitude.x
            roll_error = ((0.0 - current_roll + 180.0) % 360.0) - 180.0
            roll_cmd = max(-self._max_roll_cmd, min(self._max_roll_cmd, -self._roll_kp * roll_error))
        else:
            roll_cmd = 0.0

        twist = Twist()
        twist.linear.x = forward_cmd
        twist.angular.x = roll_cmd
        twist.angular.y = pitch_cmd
        twist.angular.z = yaw_cmd
        self._cmd_vel_pub.publish(twist)

        return None

    def _give_feedback(self) -> str:
        if self._latest_bbox is None:
            return "no detection yet"
        roll_str = f"{self._latest_attitude.x:.0f}" if self._latest_attitude is not None else "?"
        return (
            f"roll {roll_str} | "
            f"bbox_center=({self._latest_bbox.center.position.x:.0f},{self._latest_bbox.center.position.y:.0f}) "
            f"bbox_width={self._latest_bbox.size.x:.0f}/{self._target_bbox_width:.0f}"
        )


def main():
    rclpy.init()
    node = Node("approaching_sam_action_server")
    ApproachingSamAction(node)

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