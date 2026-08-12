#!/usr/bin/env python3

import os
import time

import control as ct
import numpy as np
import rclpy
from ament_index_python.packages import get_package_share_directory
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, QoSDurabilityPolicy
from dji_msgs.msg import Topics as DJITopics
from smarc_msgs.action import BaseAction
from std_msgs.msg import String, Float64MultiArray

from sway_controller.HookKalmanFilter import HookKalmanFilter


def _load_identified_gains(model_path: str):
    
    d = np.load(model_path)

    tf_x = ct.tf(
        d['b__FLU_axes_0__to__FLUvelocity_ground_fused_x'],
        d['a__FLU_axes_0__to__FLUvelocity_ground_fused_x'],
    )
    tf_y = ct.tf(
        d['b__FLU_axes_1__to__FLUvelocity_ground_fused_y'],
        d['a__FLU_axes_1__to__FLUvelocity_ground_fused_y'],
    )

    k_x = float(tf_x.num[0][0][0])
    tau_x = float(tf_x.den[0][0][1])
    k_y = float(tf_y.num[0][0][0])
    tau_y = float(tf_y.den[0][0][1])

    return k_x, tau_x, k_y, tau_y


def _wait_for_identified_params(node: Node,
                                timeout_sec: float = 5.0) -> "tuple[float, float]|None":
    
    received: dict = {}
    qos_latched = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                             durability=QoSDurabilityPolicy.TRANSIENT_LOCAL)

    def _cb(msg):
        if len(msg.data) >= 2:
            received['L'] = float(msg.data[0])
            received['xi'] = float(msg.data[1])

    sub = node.create_subscription(
        Float64MultiArray, DJITopics.HOOK_PENDULUM_PARAMETERS_IDENTIFIED, _cb, qos_latched)
    deadline = time.time() + timeout_sec
    while time.time() < deadline and not received:
        rclpy.spin_once(node, timeout_sec=0.05)
    node.destroy_subscription(sub)

    if not received:
        return None
    return received['L'], received['xi']


def _run_identification_action(node: Node, timeout_sec: float = 60.0) -> bool:
    
    action_name = 'estimate_length_and_damping'
    client = ActionClient(node, BaseAction, action_name)

    node.get_logger().info(f'Waiting for action server {action_name}...')
    if not client.wait_for_server(timeout_sec=timeout_sec):
        node.get_logger().warning(f'Action server {action_name} not available after {timeout_sec}s')
        return False

    def _on_feedback(fb):
        node.get_logger().info(f'[identification] {fb.feedback.feedback.data}',
                               throttle_duration_sec=1.0)

    goal = BaseAction.Goal()
    goal.goal = String(data='{}')

    node.get_logger().info('Requesting hook pendulum identification (this will excite a swing)...')
    send_goal_future = client.send_goal_async(goal, feedback_callback=_on_feedback)
    rclpy.spin_until_future_complete(node, send_goal_future, timeout_sec=timeout_sec)
    goal_handle = send_goal_future.result()
    if goal_handle is None or not goal_handle.accepted:
        node.get_logger().warning('estimate_length_and_damping goal was rejected')
        return False

    result_future = goal_handle.get_result_async()
    rclpy.spin_until_future_complete(node, result_future, timeout_sec=timeout_sec)
    response = result_future.result()
    if response is None:
        node.get_logger().warning('estimate_length_and_damping did not complete in time')
        return False

    return bool(response.result.success)


def main():
    rclpy.init()

    node = Node("hook_kalman_filter_node")
    node.declare_parameter("robot_name", "M350")
    node.declare_parameter("loop_freq", 50)
    node.declare_parameter("L", -1.0)
    node.declare_parameter("xi", -1.0)
    node.declare_parameter("qc", 3.1)
    node.declare_parameter("sigma_initial", 1.0)
    node.declare_parameter("mahalanobis_thr", 16.0)
    node.declare_parameter("max_boresight_tilt_deg", 45.0)
    node.declare_parameter("continuous_model_path", "")
    node.declare_parameter("camera_calibration_file", "z1_720p_cam_params.yaml")
    robot_name = node.get_parameter("robot_name").value

    try:
        continuous_model_path = node.get_parameter("continuous_model_path").value
        if not continuous_model_path:
            continuous_model_path = os.path.join(
                get_package_share_directory("dji_captain"),
                "models", robot_name,
                "continuous_model", "model_bla_diag_cmdvle.npz",
            )

        k_x, tau_x, k_y, tau_y = _load_identified_gains(continuous_model_path)
        node.get_logger().info(
            f"Loaded identified gains from {continuous_model_path}: "
            f"k_x={k_x}, tau_x={tau_x}, k_y={k_y}, tau_y={tau_y}"
        )

        L = node.get_parameter("L").value
        xi = node.get_parameter("xi").value
        if L < 0 or xi < 0:
            ok = _run_identification_action(node)
            identified = _wait_for_identified_params(node) if ok else None
            if identified is not None and identified[0] > 0.0:
                if L < 0:
                    L = identified[0]
                if xi < 0:
                    xi = identified[1]
                node.get_logger().info(f'Using identified L={L}, xi={xi} from the action')
            else:
                node.get_logger().error(
                    'estimate_length_and_damping did not return usable L/xi '
                    f'(action ok={ok}, params={identified}).'
                )
                node.destroy_node()
                if rclpy.ok():
                    rclpy.shutdown()
                return

        HookKalmanFilter(
            node,
            robot_name=robot_name,
            use_simtime=node.get_parameter("use_sim_time").value,
            loop_freq=node.get_parameter("loop_freq").value,
            L=L,
            xi=xi,
            taux=tau_x,
            tauy=tau_y,
            kx=k_x,
            ky=k_y,
            qc=node.get_parameter("qc").value,
            sigma_initial=node.get_parameter("sigma_initial").value,
            mahalanobis_thr=node.get_parameter("mahalanobis_thr").value,
            camera_calibration_file=node.get_parameter("camera_calibration_file").value,
            max_boresight_tilt_deg=node.get_parameter("max_boresight_tilt_deg").value,
        )

        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
