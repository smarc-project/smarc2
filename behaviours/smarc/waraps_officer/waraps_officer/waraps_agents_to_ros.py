"""Publish mirrored WARA-PS agents as latlon and odom.

The node stays at ``/``. Each agent already has its namespace on the topic
(``<agent>/latlon``, ``<agent>/odom``). Putting this node under ``robot_name``
would nest that namespace a second time. ``robot_name`` is only the odom frame.
"""

from collections.abc import Callable
from dataclasses import dataclass, field

import rclpy
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PoseStamped, TransformStamped
from nav_msgs.msg import Odometry
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.publisher import Publisher
from rclpy.subscription import Subscription
from rclpy.time import Time
from smarc_georef_cpp import GeorefUtils, TransformException
from smarc_msgs.msg import Topics
from smarc_utilities.topic_utils import STRING_MSG
from std_msgs.msg import String
from tf2_geometry_msgs import do_transform_pose_stamped

from waraps_officer.waraps_agents_encoding import (
    GeoSample,
    MirroredAgent,
    body_velocity,
    chosen_heading,
    covariance_diagonal,
    enu_yaw,
    mirrored_agents,
    namespaced,
    parse_geopoint,
    parse_scalar,
    pose_altitude,
    quaternion_xyzw,
    to_radians,
)

# A zero rate would make the timer period infinite.
_MIN_PUBLISH_HZ = 0.1
_WARN_EVERY = Duration(seconds=5.0)


@dataclass
class TrackedAgent:
    """The latest readings of one mirrored agent, and the topics it has here."""

    latlon: Publisher
    odom: Publisher
    # Set together in _store_position: a position always has its arrival stamp.
    position: GeoSample | None = None
    stamp: Time | None = None
    heading: float | None = None
    course: float | None = None
    speed: float | None = None
    roll: float | None = None
    pitch: float | None = None
    subscriptions: list[Subscription] = field(default_factory=list)

    def set_heading(self, value: float) -> None:
        self.heading = value

    def set_course(self, value: float) -> None:
        self.course = value

    def set_speed(self, value: float) -> None:
        self.speed = value

    def set_roll(self, value: float) -> None:
        self.roll = value

    def set_pitch(self, value: float) -> None:
        self.pitch = value


class AgentsToRos:
    def __init__(self, node: Node) -> None:
        self._node = node
        self._robot_name = node.declare_parameter('robot_name', 'evolo').get_parameter_value().string_value
        self._latlon_name = node.declare_parameter('latlon_name', 'latlon').get_parameter_value().string_value
        self._odom_name = node.declare_parameter('odom_name', 'odom').get_parameter_value().string_value
        odom_link = node.declare_parameter('odom_link', 'odom').get_parameter_value().string_value
        self._base_link = node.declare_parameter('base_link', 'base_link').get_parameter_value().string_value
        self.odom_frame = namespaced(self._robot_name, odom_link)
        self._utm_override = node.declare_parameter('utm_frame_override', '').get_parameter_value().string_value
        self._rate_hz = node.declare_parameter('publish_rate_hz', 1.0).get_parameter_value().double_value
        self._transform_timeout_s = node.declare_parameter('transform_timeout_s', 10.0).get_parameter_value().double_value
        self._prefer_heading = node.declare_parameter('prefer_heading', True).get_parameter_value().bool_value
        self._angle_unit = node.declare_parameter('angle_unit', 'deg').get_parameter_value().string_value
        ellipse_x = node.declare_parameter('position_covariance.ellipse_x_m', 5.0).get_parameter_value().double_value
        ellipse_y = node.declare_parameter('position_covariance.ellipse_y_m', 5.0).get_parameter_value().double_value
        ellipse_z = node.declare_parameter('position_covariance.ellipse_z_m', 0.0).get_parameter_value().double_value
        self._covariance = covariance_diagonal(ellipse_x, ellipse_y, ellipse_z)

        self._agents: dict[str, TrackedAgent] = {}
        self._utm_to_odom_cache: dict[str, TransformStamped] = {}
        self._last_warned: dict[str, Time] = {}
        self._georef = GeorefUtils(node=node)
        period = 1.0 / max(self._rate_hz, _MIN_PUBLISH_HZ)
        self._timer = node.create_timer(period, self._publish_agents)

        node.get_logger().info(
            f'Publishing mirrored agents as {self._latlon_name} and {self._odom_name} '
            f'in frame {self.odom_frame}')
        node.get_logger().info(
            f'Position covariance ellipse is {ellipse_x:.3f} m x {ellipse_y:.3f} m x '
            f'{ellipse_z:.3f} m (diag {self._covariance[0]:.3f}, {self._covariance[1]:.3f}, '
            f'{self._covariance[2]:.3f})')

    def _publish_agents(self) -> None:
        self._track_new_agents()
        for root, agent in self._agents.items():
            self._publish_agent(root, agent)

    def _track_new_agents(self) -> None:
        topics = self._node.get_topic_names_and_types()
        for mirrored in mirrored_agents(
                topics,
                Topics.WARA_PS_SENSOR_PREFIX,
                Topics.WARA_PS_SENSOR_POSITION_TOPIC,
                self._robot_name):
            if mirrored.root in self._agents:
                continue
            # Track an agent only once something publishes its position as a String.
            publishers = self._node.get_publishers_info_by_topic(mirrored.position)
            if not any(info.topic_type == STRING_MSG for info in publishers):
                continue
            self._start_tracking(mirrored)

    def _start_tracking(self, mirrored: MirroredAgent) -> None:
        root = mirrored.root
        agent = TrackedAgent(
            latlon=self._node.create_publisher(GeoPoint, namespaced(root, self._latlon_name), 10),
            odom=self._node.create_publisher(Odometry, namespaced(root, self._odom_name), 10),
        )
        self._agents[root] = agent
        agent.subscriptions = [
            self._node.create_subscription(
                String,
                mirrored.position,
                lambda msg: self._store_position(root, agent, msg),
                10),
            self._subscribe_scalar(root, Topics.WARA_PS_SENSOR_HEADING_TOPIC, agent.set_heading),
            self._subscribe_scalar(root, Topics.WARA_PS_SENSOR_COURSE_TOPIC, agent.set_course),
            self._subscribe_scalar(root, Topics.WARA_PS_SENSOR_SPEED_TOPIC, agent.set_speed),
            self._subscribe_scalar(root, Topics.WARA_PS_SENSOR_ROLL_TOPIC, agent.set_roll),
            self._subscribe_scalar(root, Topics.WARA_PS_SENSOR_PITCH_TOPIC, agent.set_pitch),
        ]
        self._node.get_logger().info(
            f'Publishing {root} as {namespaced(root, self._latlon_name)} and '
            f'{namespaced(root, self._odom_name)} in {self.odom_frame}')

    def _subscribe_scalar(
        self,
        root: str,
        constant: str,
        save: Callable[[float], None],
    ) -> Subscription:
        topic = namespaced(root, constant)

        def store(msg: String) -> None:
            value = parse_scalar(msg.data)
            if value is None:
                self._warn_throttled(topic, f'Ignoring malformed scalar payload on {topic}: {msg.data}')
                return
            save(value)

        return self._node.create_subscription(String, topic, store, 10)

    def _store_position(self, root: str, agent: TrackedAgent, msg: String) -> None:
        sample = parse_geopoint(msg.data)
        if sample is None:
            self._warn_throttled(root, f'Ignoring malformed position payload: {msg.data}')
            return
        # The C++ node warned and still used the numbers; so does this one.
        if sample.unexpected_type:
            self._warn_throttled(root, f'Position payload type is not GeoPoint: {msg.data}')
        agent.position = sample
        agent.stamp = self._node.get_clock().now()

    def _publish_agent(self, root: str, agent: TrackedAgent) -> None:
        if agent.position is None:
            return
        point = GeoPoint()
        point.latitude = agent.position.latitude
        point.longitude = agent.position.longitude
        point.altitude = agent.position.altitude
        agent.latlon.publish(point)

        try:
            utm = self._georef.geopoint_to_point_stamped(point)
        except TransformException as error:
            self._warn_throttled(root, f'Ignoring position that is not a UTM point: {error}')
            return
        frame = self._utm_override or utm.header.frame_id
        transform = self._utm_to_odom(frame)
        if transform is None:
            return

        pose = PoseStamped()
        pose.header.stamp = agent.stamp.to_msg()
        pose.header.frame_id = frame
        pose.pose.position.x = utm.point.x
        pose.pose.position.y = utm.point.y
        pose.pose.position.z = pose_altitude(utm.point.z)
        heading = chosen_heading(agent.heading, agent.course, self._prefer_heading)
        yaw = enu_yaw(heading, self._angle_unit) if heading is not None else 0.0
        roll = to_radians(0.0 if agent.roll is None else agent.roll, self._angle_unit)
        pitch = to_radians(0.0 if agent.pitch is None else agent.pitch, self._angle_unit)
        x, y, z, w = quaternion_xyzw(roll, pitch, yaw)
        pose.pose.orientation.x = x
        pose.pose.orientation.y = y
        pose.pose.orientation.z = z
        pose.pose.orientation.w = w

        odom_pose = do_transform_pose_stamped(pose, transform)
        odom = Odometry()
        odom.header = odom_pose.header
        odom.child_frame_id = namespaced(root, self._base_link)
        odom.pose.pose = odom_pose.pose
        odom.pose.covariance[0] = self._covariance[0]
        odom.pose.covariance[7] = self._covariance[1]
        odom.pose.covariance[14] = self._covariance[2]
        # WARA-PS speed is along the course; the twist is in the body frame, so it is split.
        if agent.speed is not None:
            course_yaw = enu_yaw(agent.course, self._angle_unit) if agent.course is not None else None
            odom.twist.twist.linear.x, odom.twist.twist.linear.y = body_velocity(agent.speed, yaw, course_yaw)
        agent.odom.publish(odom)

    def close(self) -> None:
        self._georef.shutdown()

    def _utm_to_odom(self, utm_frame: str) -> TransformStamped | None:
        """The UTM zone and the odom frame do not move relative to each other, so one lookup is kept."""
        cached = self._utm_to_odom_cache.get(utm_frame)
        if cached is not None:
            return cached
        try:
            found = self._georef.lookup_transform(
                self.odom_frame, utm_frame, self._transform_timeout_s)
        except TransformException as error:
            self._warn_throttled(
                utm_frame,
                f'Cannot cache transform from {utm_frame} to {self.odom_frame}: {error}')
            return None
        self._utm_to_odom_cache[utm_frame] = found
        self._node.get_logger().info(
            f'Cached constant transform {utm_frame} -> {self.odom_frame}')
        return found

    def _warn_throttled(self, key: str, text: str) -> None:
        now = self._node.get_clock().now()
        last = self._last_warned.get(key)
        if last is not None and now - last < _WARN_EVERY:
            return
        self._last_warned[key] = now
        self._node.get_logger().warning(text)


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = Node('waraps_agents_to_ros')
    agents = AgentsToRos(node)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        agents.close()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
