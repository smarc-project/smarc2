import rclpy
import json
import asyncio

from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.action import ActionClient, ActionServer
from rclpy.action.client import ClientGoalHandle

from smarc_msgs.action import BaseAction


class SearchAreas(Node):

    # Speed string → float conversion
    _SPEED_MAP = {'high': 10.0, 'medium': 5.0, 'low': 2.0}

    def __init__(self):
        super().__init__('search_areas')

        cbg = ReentrantCallbackGroup()

        self._search_area_client = ActionClient(
            self,
            BaseAction,
            'search_area',
            callback_group=cbg,
        )

        self._server = ActionServer(
            self,
            BaseAction,
            'search_areas',
            self._execute_callback,
            callback_group=cbg,
        )

        self.get_logger().info('SearchAreas orchestrator started')
        self.get_logger().info(
            f'Waiting for goals on: {self.get_namespace()}/search_areas'
        )

    # ─────────────────────────────────────────────────────────
    # Main action callback
    # ─────────────────────────────────────────────────────────
    async def _execute_callback(self, goal_handle):

        self.get_logger().info('[SearchAreas] Received multi-area mission')

        # ── Parse JSON ──────────────────────────────────────────────────────
        try:
            payload = json.loads(goal_handle.request.goal.data)
        except Exception as e:
            self.get_logger().error(f'Invalid JSON: {e}')
            goal_handle.abort()
            return BaseAction.Result()

        # ── Read client format ───────────────────────────────────────────────
        try:
            params    = payload['task']['params']
            areas     = params['areas']       # list of lists of GeoPoints
            speed_raw = params.get('speed', 'low')
        except (KeyError, TypeError) as e:
            self.get_logger().error(f'Missing task/params/areas in payload: {e}')
            goal_handle.abort()
            return BaseAction.Result()

        # "high" / "medium" / "low" → float, or already a float/int
        if isinstance(speed_raw, str):
            speed = self._SPEED_MAP.get(speed_raw.lower(), 5.0)
        else:
            speed = float(speed_raw)

        # ── Shared obstacles (island polygons) ───────────────────────────────
        # Format in payload: [{"name":..., "stay_inside": False, "points": [{"lat","lon"}]}]
        # Keep only those with stay_inside=False (actual obstacles)
        polygones = payload.get('polygones', [])
        obstacles_latlon = [
            [{'lat': pt['lat'], 'lon': pt['lon']} for pt in poly['points']]
            for poly in polygones
            if not poly.get('stay_inside', True) and len(poly.get('points', [])) >= 3
        ]

        if not areas:
            self.get_logger().error('No areas received in payload')
            goal_handle.abort()
            return BaseAction.Result()

        self.get_logger().info(
            f'[SearchAreas] {len(areas)} area(s) | speed={speed} | '
            f'{len(obstacles_latlon)} obstacle(s)'
        )

        # ── Wait for search_area server ──────────────────────────────────────
        if not self._search_area_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('search_area action server unavailable')
            goal_handle.abort()
            return BaseAction.Result()

        # ── Sequential loop over areas ───────────────────────────────────────
        for i, area_pts in enumerate(areas):
            zone_name = f'Area {i + 1}'

            if not area_pts or len(area_pts) < 3:
                self.get_logger().warn(
                    f'[SearchAreas] {zone_name} has < 3 points — skipping'
                )
                continue

            self.get_logger().info(
                f'[SearchAreas] Starting {zone_name} ({i + 1}/{len(areas)})'
            )

            self._publish_feedback(goal_handle, i, len(areas), zone_name, 'started')

            success = await self._run_area(area_pts, obstacles_latlon, speed, zone_name)

            if not success:
                self.get_logger().error(
                    f'[SearchAreas] {zone_name} failed — aborting mission'
                )
                goal_handle.abort()
                return BaseAction.Result()

            self.get_logger().info(
                f'[SearchAreas] {zone_name} completed ({i + 1}/{len(areas)})'
            )

            self._publish_feedback(goal_handle, i + 1, len(areas), zone_name, 'done')

        self.get_logger().info('[SearchAreas] All areas completed — mission succeeded')
        goal_handle.succeed()
        return BaseAction.Result()

    # ─────────────────────────────────────────────────────────
    # Send an area to search_area and wait for completion
    # ─────────────────────────────────────────────────────────
    async def _run_area(self, area_pts, obstacles_latlon, speed, zone_name) -> bool:
        """
        area_pts        : list of GeoPoints
                          [{"altitude":0, "latitude":..., "longitude":..., "rostype":"GeoPoint"}, ...]
        obstacles_latlon: list of obstacle polygons
                          [[{"lat":..., "lon":...}, ...], ...]
        speed           : float (m/s)

        Converts GeoPoints to {"lat","lon"} and sends to search_area in the format:
            {
                "speed":     float,
                "area":      [{"lat":..., "lon":...}, ...],
                "obstacles": [[{"lat":..., "lon":...}, ...], ...]
            }
        """
        # Convert GeoPoint → {"lat", "lon"}
        area_latlon = [
            {'lat': pt['latitude'], 'lon': pt['longitude']}
            for pt in area_pts
        ]

        zone_payload = {
            'speed':     speed,
            'area':      area_latlon,
            'obstacles': obstacles_latlon,
        }

        goal_msg           = BaseAction.Goal()
        goal_msg.goal.data = json.dumps(zone_payload)

        self.get_logger().info(
            f'  → Sending "{zone_name}" to search_area '
            f'({len(area_latlon)} zone points, {len(obstacles_latlon)} obstacle(s))'
        )

        send_future = self._search_area_client.send_goal_async(
            goal_msg,
            feedback_callback=self._search_area_feedback_cb,
        )

        goal_handle: ClientGoalHandle = await send_future

        if not goal_handle.accepted:
            self.get_logger().error(
                f'  search_area rejected goal for "{zone_name}"'
            )
            return False

        self.get_logger().info(f'  search_area accepted "{zone_name}" — waiting…')

        result = await goal_handle.get_result_async()

        # rclpy action status: 4 = SUCCEEDED, 6 = ABORTED, 5 = CANCELED
        if result.status == 4:
            return True

        self.get_logger().error(
            f'  search_area ended with status={result.status} for "{zone_name}"'
        )
        return False

    # ─────────────────────────────────────────────────────────
    # Relay feedback from search_area → our client
    # ─────────────────────────────────────────────────────────
    def _search_area_feedback_cb(self, feedback_msg):
        try:
            data = json.loads(feedback_msg.feedback.feedback.data)
            self.get_logger().debug(
                f'  [relay] precision={data.get("precision_pct", "?")}% | '
                f'dist={data.get("distance_travelled", "?")}m'
            )
        except Exception:
            pass

    # ─────────────────────────────────────────────────────────
    # Feedback toward our own client
    # ─────────────────────────────────────────────────────────
    def _publish_feedback(self, goal_handle, done: int, total: int,
                          zone_name: str, status: str):
        fb = BaseAction.Feedback()
        fb.feedback.data = json.dumps({
            'zones_done':   done,
            'zones_total':  total,
            'current_zone': zone_name,
            'status':       status,
        })
        goal_handle.publish_feedback(fb)


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
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