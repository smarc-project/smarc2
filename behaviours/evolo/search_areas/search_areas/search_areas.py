import rclpy
import json

from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle

from smarc_msgs.action import BaseAction
from smarc_utilities import georef_utils
from geographic_msgs.msg import GeoPoint
from smarc_msgs.msg import Topics as smarcTopics
from smarc_action_base.gentler_action_server import GentlerActionServer
from geometry_msgs.msg import PointStamped


_SPEED_MAP = {'fast': 6.0, 'slow': 4.0, 'standard': 5.0}


# ─────────────────────────────────────────────────────────────────────────
def _parse_speed(node: Node, speed_raw, default: float = 5.0) -> float:
    if isinstance(speed_raw, str):
        val = _SPEED_MAP.get(speed_raw.lower())
        if val is None:
            node.get_logger().warn(
                f"[Speed] Unrecognized speed level '{speed_raw}' "
                f"(expected one of {list(_SPEED_MAP)}) — using default {default} m/s"
            )
            return default
        return val
    try:
        return float(speed_raw)
    except (TypeError, ValueError):
        node.get_logger().warn(
            f"[Speed] Invalid speed value {speed_raw!r} — using default {default} m/s"
        )
        return default


# ─────────────────────────────────────────────────────────────────────────
def _valid_polygons(polygons: list) -> list:
    return [p for p in polygons if p and len(p) >= 3]


# ─────────────────────────────────────────────────────────────────────────
class SearchAreas(Node):
    """
    Multi-zone orchestrator. Fans out one 'search_area' sub-goal per search
    zone, using the exact same WARAPS payload convention that 'search_area'
    itself expects — a caller with a single zone can call 'search_area'
    directly instead of going through this node; a caller with several
    zones goes through this one.

    Goal payload (flat WARAPS behavior-tree convention, no "task" wrapper):
        {
          "speed": "low" | "medium" | "high" | "standard" | <float>,
          "areas": [
              [{"latitude":.., "longitude":..}, ...],    # zone 1
              [{"latitude":.., "longitude":..}, ...],    # zone 2, ...
              ...
          ]
        }

    Note the "area" key holds a list of *polygons* here (one per zone) —
    the same key name as 'search_area' uses for a single polygon (list of
    points). The nesting level is what distinguishes the two, matching the
    real BT payload format.
    """

    def __init__(self):
        super().__init__('search_areas')

        cbg = ReentrantCallbackGroup()


        self._search_area_client = ActionClient(self, BaseAction, 'search_area', callback_group=cbg,)

        self._areas: list = []          
        self._speed: float = 5.0

        self._current_area_index: int = 0
        self._current_goal_handle: ClientGoalHandle | None = None
        self._area_future = None
        self._result_future = None
        self._last_feedback: dict = {}

        # ── GentlerActionServer ───────────────────────────────────────────────
        self._server = GentlerActionServer(
            node=self,
            action_name='search_areas',
            on_goal_received=self._on_goal_received,
            on_cancel_received=self._on_cancel_received,
            prepare_loop=self._prepare_loop,
            loop_inner=self._loop_inner,
            give_feedback=self._give_feedback,
            loop_frequency=5.0,
        )

        self.get_logger().info('SearchAreas orchestrator started')
        self.get_logger().info(
            f'Waiting for goals on: {self.get_namespace()}/search_areas'
        )

    # ─────────────────────────────────────────────────────────────────────────
    def _on_goal_received(self, payload: dict) -> bool:
        areas = _valid_polygons(payload.get('areas', []))

        if not areas:
            self.get_logger().error('[Goal] No valid area polygon (>=3 points) found under "area"')
            return False

        self._pending_payload = payload
        return True


    # ─────────────────────────────────────────────────────────────────────────
    def _on_cancel_received(self) -> bool:
        self.get_logger().info('[SearchAreas] Cancel requested')
        if self._current_goal_handle is not None:
            self.get_logger().info('[SearchAreas] Cancelling active search_area sub-goal')
            self._current_goal_handle.cancel_goal_async()

        return True


    # ─────────────────────────────────────────────────────────────────────────
    def _prepare_loop(self) -> None:
        """Called once before loop_inner starts. Parse payload, reset state."""
        payload   = self._pending_payload
        speed_raw = payload.get('speed', 'low')

        self._areas = _valid_polygons(payload.get('areas', []))
        self._speed = _parse_speed(self, speed_raw, default=5.0)
        self._spacing = payload.get('spacing', None) 


        self._current_area_index = 0
        self._current_goal_handle = None
        self._area_future  = None
        self._result_future = None
        self._last_feedback = {}

        self.get_logger().info(
            f'[SearchAreas] Mission ready: {len(self._areas)} area(s) | '
            f'speed={self._speed}')

        if not self._search_area_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('search_area action server unavailable')
            self._server_unavailable = True
        else:
            self._server_unavailable = False


    # ─────────────────────────────────────────────────────────────────────────
    def _loop_inner(self) -> bool | None:

        if getattr(self, '_server_unavailable', False):
            return False

        if self._current_area_index >= len(self._areas):
            self.get_logger().info('[SearchAreas] All areas completed')
            return True

        area_pts  = self._areas[self._current_area_index]
        zone_name = f'Area {self._current_area_index + 1}'

        # ── Phase 1: send the goal (once) ─────────────────────────────────────
        if self._area_future is None and self._result_future is None:

            zone_payload = {
                'speed':    self._speed,
                'area':     area_pts
            }
            if self._spacing is not None:    
                zone_payload['spacing'] = self._spacing

            goal_msg           = BaseAction.Goal()
            goal_msg.goal.data = json.dumps(zone_payload)

            self.get_logger().info(
                f'[SearchAreas] Sending {zone_name} to search_area '
                f'({len(area_pts)} pts'
            )
            self._area_future = self._search_area_client.send_goal_async(
                goal_msg,
                feedback_callback=self._search_area_feedback_cb,
            )
            return None 

        # ── Phase 2: goal sent — wait for acceptance ──────────────────────────
        if self._area_future is not None and self._result_future is None:
            if not self._area_future.done():
                return None 

            self._current_goal_handle = self._area_future.result()
            self._area_future = None

            if not self._current_goal_handle.accepted:
                self.get_logger().error(
                    f'[SearchAreas] search_area rejected {zone_name}'
                )
                return False

            self.get_logger().info(
                f'[SearchAreas] search_area accepted {zone_name} — waiting for result…'
            )
            self._result_future = self._current_goal_handle.get_result_async()
            return None

        # ── Phase 3: goal accepted — wait for result ──────────────────────────
        if self._result_future is not None:
            if not self._result_future.done():
                return None  

            result = self._result_future.result()
            self._result_future = None
            self._current_goal_handle = None

            if result.status == 4:
                self.get_logger().info(
                    f'[SearchAreas] {zone_name} completed '
                    f'({self._current_area_index + 1}/{len(self._areas)})'
                )
                self._current_area_index += 1
                return None 
            else:
                self.get_logger().error(
                    f'[SearchAreas] {zone_name} failed with status={result.status}'
                )
                return False

        return None 


    # ─────────────────────────────────────────────────────────────────────────
    def _give_feedback(self) -> str:
        """Return a JSON feedback string for the outer client."""
        zone_name = (
            f'Area {self._current_area_index + 1}'
            if self._current_area_index < len(self._areas)
            else 'done'
        )
        return json.dumps({
            'zones_done':   self._current_area_index,
            'zones_total':  len(self._areas),
            'current_zone': zone_name,
            'sub_feedback': self._last_feedback,
        })


    # ─────────────────────────────────────────────────────────────────────────
    def _search_area_feedback_cb(self, feedback_msg):
        try:
            self._last_feedback = json.loads(
                feedback_msg.feedback.feedback.data
            )
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
def main(args=None):
    rclpy.init(args=args)
    node = SearchAreas()

    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard interrupt')
    finally:
        executor.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()