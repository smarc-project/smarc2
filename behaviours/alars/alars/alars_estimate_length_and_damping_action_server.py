import json

from enum import Enum, auto

import numpy as np

import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, QoSDurabilityPolicy

from geometry_msgs.msg import TwistStamped
from std_msgs.msg import Float64MultiArray, MultiArrayDimension
from dji_msgs.msg import Topics as DJITopics
from dji_msgs.msg import Links as DJILinks
from yolo_msgs.msg import DetectionArray

from smarc_action_base.gentler_action_server import GentlerActionServer


class _Phase(Enum):
    CAPTURE_EQUILIBRIUM = auto()
    EXCITING = auto()
    COLLECTING = auto()


class EstimateLengthAndDamping:

    G = 9.81

    def __init__(self, node: Node, robot_name: str):
        self._node: Node = node
        self._robot_name: str = robot_name

        self.BASE_FLAT_FRAME: str = self._robot_name + '/' + DJILinks.BASE_FLAT

        self._last_x: "float|None" = None   
        self._last_y: "float|None" = None   
        self._new_detection: bool = False   
        self._axis_index: "int|None" = None  
        self._axis_buffer: "list[tuple[float, float, float]]" = []

        self._create_subscriptions()
        self._create_publishers()

        self._as = GentlerActionServer(
            self._node,
            'estimate_length_and_damping',
            self._on_goal_received,
            self._on_cancel_received,
            self._prepare_loop,
            self._loop_inner,
            self._give_feedback,
            loop_frequency=50
        )

    @property
    def now_time(self) -> float:
        t = self._node.get_clock().now().to_msg()
        return t.sec + t.nanosec * 1e-9

    def log(self, msg: str):
        self._node.get_logger().info(msg)

    def _create_subscriptions(self):
        _detection_topic_name = DJITopics.YOLO_DETECTIONS
        self._detection_subscription = self._node.create_subscription(
            DetectionArray, _detection_topic_name, self._detection_callback, 10
        )

    def _create_publishers(self):
        qos_best_effort10 = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT,
                                        durability=QoSDurabilityPolicy.VOLATILE)
        self._ref_publisher = self._node.create_publisher(
            TwistStamped, DJITopics.VELOCITY_SETPOINT_TOPIC, qos_profile=qos_best_effort10
        )

        qos_latched = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                                 durability=QoSDurabilityPolicy.TRANSIENT_LOCAL)
        self._params_publisher = self._node.create_publisher(
            Float64MultiArray, DJITopics.HOOK_PENDULUM_PARAMETERS_IDENTIFIED,
            qos_profile=qos_latched
        )

    def _publish_identified_params(self, length: float, xi: float):
        msg = Float64MultiArray()
        msg.layout.dim = [MultiArrayDimension(label='length', size=1, stride=2),
                          MultiArrayDimension(label='damping', size=1, stride=1)]
        msg.data = [float(length), float(xi)]
        self._params_publisher.publish(msg)
        self.log('Published identified params on hook_pendulum_params_identified')

    def _detection_callback(self, msg):
        
        hook_dets = [d for d in msg.detections if d.class_name == "hook"]
        if not hook_dets:
            return

        self._last_x = sum(float(d.bbox.center.position.x) for d in hook_dets) / len(hook_dets)
        self._last_y = sum(float(d.bbox.center.position.y) for d in hook_dets) / len(hook_dets)
        self._new_detection = True

    def _publish_velocity_setpoint(self, vx: float, vy: float):
        setpoint = TwistStamped()
        setpoint.header.stamp = self._node.get_clock().now().to_msg()
        setpoint.header.frame_id = self.BASE_FLAT_FRAME
        setpoint.twist.linear.x = vx
        setpoint.twist.linear.y = vy
        self._ref_publisher.publish(setpoint)


    def _on_goal_received(self, goal_request: dict) -> bool:
        try:
            self._excitation_speed    = float(goal_request.get('excitation-speed', 1.0))
            self._excitation_duration = float(goal_request.get('excitation-duration', 3.0))
            self._collection_duration = float(goal_request.get('collection-duration', 20.0))
            self._min_periods         = int(goal_request.get('min-periods', 4))
            self._refractory_window   = float(goal_request.get('refractory-window', 1.5))
            self._smoothing_window    = int(goal_request.get('smoothing-window', 5))

            self._axis_selection_duration = float(goal_request.get('axis-selection-duration', 2.0))
            return True
        except Exception:
            self._node.get_logger().error("Failed to parse goal request")
            return False

    def _on_cancel_received(self) -> bool:
        self._publish_velocity_setpoint(0.0, 0.0)
        return True

    def _prepare_loop(self):
        self._phase = _Phase.CAPTURE_EQUILIBRIUM
        self._phase_start_time = self.now_time
        self._equilibrium: "float|None" = None
        self._result = {"success": False, "length": 0.0, "damping": 0.0, "message": ""}
        self._finalized = False
        self._reset_period_estimation()

    def _give_feedback(self) -> str:
        
        if self._finalized:
            return json.dumps(self._result)
        if self._phase == _Phase.CAPTURE_EQUILIBRIUM:
            return "Waiting for a hook detection to establish equilibrium..."
        if self._phase == _Phase.EXCITING:
            return f"Exciting: {self.now_time - self._phase_start_time:.1f}/{self._excitation_duration:.1f}s"
        if self._phase == _Phase.COLLECTING:
            return (f"Collecting: {self.now_time - self._phase_start_time:.1f}/{self._collection_duration:.1f}s, "
                    f"periods seen: {self._n_periods}, current period estimate: {self._period_estimate}")
        return "Done"

    def _loop_inner(self) -> "bool|None":
        now = self.now_time
        elapsed = now - self._phase_start_time

        if self._phase == _Phase.CAPTURE_EQUILIBRIUM:
            if self._last_x is None or self._last_y is None:
                if elapsed > 5.0:
                    self._result["message"] = "No hook detection available to establish equilibrium"
                    return False
                return None
            
            self._equilibrium = None
            self._phase = _Phase.EXCITING
            self._phase_start_time = now
            return None

        if self._phase == _Phase.EXCITING:
            if elapsed < self._excitation_duration:
                self._publish_velocity_setpoint(self._excitation_speed, 0.0)
                return None
            self._publish_velocity_setpoint(0.0, 0.0)
            self._phase = _Phase.COLLECTING
            self._phase_start_time = now
            return None

        if self._phase == _Phase.COLLECTING:
            if self._last_x is not None and self._last_y is not None and self._new_detection:
                self._new_detection = False
                if self._axis_index is None:
                    self._axis_buffer.append((now, self._last_x, self._last_y))
                    if now - self._phase_start_time >= self._axis_selection_duration:
                        self._select_axis()
                else:
                    self._process_measurement(now, (self._last_x, self._last_y)[self._axis_index])

            enough_periods = self._n_periods >= self._min_periods
            if elapsed >= self._collection_duration or enough_periods:
                return self._finalize()
            return None

        return None

    def _finalize(self) -> bool:
        if self._period_estimate is None:
            self._result["message"] = "No full period observed during collection window"
            return False

        wn = 2 * np.pi / self._period_estimate
        length = self.G / wn**2
        xi = self._estimate_damping(wn)

        self._result = {
            "success": True,
            "length": float(length),
            "damping": float(xi),
            "message": f"L={length:.3f}m, xi={xi:.4f}, from {self._n_periods} periods"
        }
        self._finalized = True
        self.log(self._result["message"])
        self._publish_identified_params(length, xi)

        return True


    def _select_axis(self):
        if not self._axis_buffer:
            self._axis_index = 0
            self._equilibrium = self._last_x
            return

        xs = [b[1] for b in self._axis_buffer]
        ys = [b[2] for b in self._axis_buffer]
        ptp_x = max(xs) - min(xs)
        ptp_y = max(ys) - min(ys)
        self._axis_index = 0 if ptp_x >= ptp_y else 1
        name = "image-horizontal" if self._axis_index == 0 else "image-vertical"

        largest = max(ptp_x, ptp_y)
        if largest <= 0.0:
            self.log('WARNING: the hook did not move on either axis, nothing to fit')
        else:
            rel_x, rel_y = ptp_x / largest, ptp_y / largest
            self.log(f'Fitting the period on the {name} axis - relative swing: '
                     f'horizontal {rel_x:.2f}, vertical {rel_y:.2f} '
                     f'(peak-to-peak {ptp_x:.1f} / {ptp_y:.1f} px)')
            secondary = min(rel_x, rel_y)
            if secondary > 0.5:
                self.log(f'WARNING: the smaller axis still swings {secondary:.0%} of the larger '
                         'one. The motion is not planar, so the period fit could be unreliable')

        series = xs if self._axis_index == 0 else ys
        self._equilibrium = series[0]
        for t, bx, by in self._axis_buffer:
            self._process_measurement(t, bx if self._axis_index == 0 else by)
        self._axis_buffer = []

    def _reset_period_estimation(self):
        self._raw_buffer: "list[float]" = []
        self._window: "list[tuple[float,float]]" = []
        self._extrema: "list[tuple[float,float,bool]]" = []
        self._last_extremum_time: "float|None" = None
        self._period_estimate: "float|None" = None
        self._n_periods: int = 0
        self._axis_index = None
        self._axis_buffer = []
        self._new_detection = False

    def _process_measurement(self, t: float, x: float):
        
        self._raw_buffer.append(x)
        if len(self._raw_buffer) > self._smoothing_window:
            self._raw_buffer.pop(0)
        smoothed_x = float(np.mean(self._raw_buffer))

        self._window.append((t, smoothed_x))
        if len(self._window) > 3:
            self._window.pop(0)
        if len(self._window) < 3:
            return

        (_, x0), (t1, x1), (_, x2) = self._window
        slope_before = x1 - x0
        slope_after  = x2 - x1
        is_max = slope_before > 0 and slope_after < 0
        is_min = slope_before < 0 and slope_after > 0
        if not (is_max or is_min):
            return

        if self._last_extremum_time is not None and (t1 - self._last_extremum_time) < self._refractory_window:
            return  

        self._accept_extremum(t1, x1, is_max)

    def _accept_extremum(self, t: float, x: float, is_max: bool):
        self._extrema.append((t, x, is_max))
        self._last_extremum_time = t

        same_side_prev = next(
            ((pt, px) for pt, px, pmax in reversed(self._extrema[:-1]) if pmax == is_max),
            None
        )
        if same_side_prev is None:
            return  

        period = t - same_side_prev[0]

        if self._period_estimate is None:
            self._period_estimate = period
            self._n_periods = 1
            self.log(f'First period (prior): {period:.3f}s')
        else:
            self._n_periods += 1
            self._period_estimate += (period - self._period_estimate) / self._n_periods
            self.log(f'Period #{self._n_periods}: {period:.3f}s, running average: {self._period_estimate:.3f}s')

    def _estimate_damping(self, wn: float) -> float:
        
        if len(self._extrema) < 3:
            return 0.0

        maxima = [x for _, x, is_max in self._extrema if is_max]
        minima = [x for _, x, is_max in self._extrema if not is_max]
        if maxima and minima:
            centre = 0.5 * (float(np.mean(maxima)) + float(np.mean(minima)))
        else:
            centre = float(np.mean([x for _, x, _ in self._extrema]))

        times = np.array([t for t, _, _ in self._extrema])
        amps  = np.array([abs(x - centre) for _, x, _ in self._extrema])
        amps  = np.clip(amps, 1e-9, None)  

        slope, _ = np.polyfit(times, np.log(amps), 1)
        return max(0.0, float(-slope / wn))


def main():
    rclpy.init()

    node = Node("estimate_length_and_damping_node")
    node.declare_parameter("robot_name", "M350")
    robot_name = node.get_parameter("robot_name").value

    EstimateLengthAndDamping(
        node,
        robot_name=robot_name,
    )

    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
