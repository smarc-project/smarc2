"""Publish mirrored WARA-PS agents as latlon and odom.

The node stays at ``/``. Each agent already has its namespace on the topic
(``<agent>/latlon``, ``<agent>/odom``). Putting this node under ``robot_name``
would nest that namespace a second time. ``robot_name`` is only the odom frame.
"""

from dataclasses import dataclass, field

import rclpy
from geographic_msgs.msg import GeoPoint
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from rclpy.duration import Duration
from rclpy.node import Node
from smarc_georef_cpp import GeorefUtils, TransformException
from smarc_msgs.msg import Topics
from smarc_utilities.topic_utils import STRING_MSG
from std_msgs.msg import String
from tf2_geometry_msgs import do_transform_pose_stamped

from waraps_officer.waraps_agents_encoding import (
    absolute,
    agent_roots,
    body_velocity,
    child_frame,
    chosen_heading,
    covariance_diagonal,
    enu_yaw,
    geopoint,
    odom_frame,
    orientation,
    pose_altitude,
    scalar,
    to_radians,
)

# A zero rate would make the timer period infinite.
_MIN_PUBLISH_HZ = 0.1
_WARN_EVERY = Duration(seconds=5.0)


@dataclass
class Agent:
    position: object = None
    stamp: object = None
    heading: float | None = None
    course: float | None = None
    speed: float | None = None
    roll: float | None = None
    pitch: float | None = None
    subscriptions: list = field(default_factory=list)
    latlon: object = None
    odom: object = None


def _string(node, name, default):
    node.declare_parameter(name, default)
    return node.get_parameter(name).get_parameter_value().string_value


def _double(node, name, default):
    node.declare_parameter(name, default)
    return node.get_parameter(name).get_parameter_value().double_value


def _bool(node, name, default):
    node.declare_parameter(name, default)
    return node.get_parameter(name).get_parameter_value().bool_value


class AgentsToRos:
    def __init__(self, node):
        self._node = node
        self._robot_name = _string(node, 'robot_name', 'evolo')
        self._latlon_name = _string(node, 'latlon_name', 'latlon')
        self._odom_name = _string(node, 'odom_name', 'odom')
        odom_link = _string(node, 'odom_link', 'odom')
        self._base_link = _string(node, 'base_link', 'base_link')
        self.odom_frame = odom_frame(self._robot_name, odom_link)
        self._utm_override = _string(node, 'utm_frame_override', '')
        self._rate = _double(node, 'publish_rate_hz', 1.0)
        self._timeout = _double(node, 'transform_timeout_s', 10.0)
        self._prefer_heading = _bool(node, 'prefer_heading', True)
        self._angle_unit = _string(node, 'angle_unit', 'deg')
        ellipse_x = _double(node, 'position_covariance.ellipse_x_m', 5.0)
        ellipse_y = _double(node, 'position_covariance.ellipse_y_m', 5.0)
        ellipse_z = _double(node, 'position_covariance.ellipse_z_m', 0.0)
        self._cov = covariance_diagonal(ellipse_x, ellipse_y, ellipse_z)

        self._agents = {}
        self._cache = {}
        self._warned = {}
        self._georef = GeorefUtils(node=node)
        period = 1.0 / max(self._rate, _MIN_PUBLISH_HZ)
        self._timer = node.create_timer(period, self._tick)

        node.get_logger().info(
            f'Publishing mirrored agents as {self._latlon_name} and {self._odom_name} '
            f'in frame {self.odom_frame}')
        node.get_logger().info(
            f'Position covariance ellipse is {ellipse_x:.3f} m x {ellipse_y:.3f} m x '
            f'{ellipse_z:.3f} m (diag {self._cov[0]:.3f}, {self._cov[1]:.3f}, {self._cov[2]:.3f})')

    def _tick(self):
        self._discover()
        for root, agent in self._agents.items():
            self._send(root, agent)

    def _discover(self):
        topics = self._node.get_topic_names_and_types()
        for mirrored in agent_roots(
                topics,
                Topics.WARA_PS_SENSOR_PREFIX,
                Topics.WARA_PS_SENSOR_POSITION_TOPIC,
                self._robot_name):
            if mirrored.root in self._agents:
                continue
            publishers = self._node.get_publishers_info_by_topic(mirrored.position)
            if not any(info.topic_type == STRING_MSG for info in publishers):
                continue
            self._open(mirrored)

    def _open(self, mirrored):
        root = mirrored.root
        agent = Agent()
        self._agents[root] = agent
        agent.subscriptions.append(self._node.create_subscription(
            String,
            absolute(root, Topics.WARA_PS_SENSOR_POSITION_TOPIC),
            lambda msg, name=root: self._on_position(name, msg),
            10))
        self._listen(agent, root, Topics.WARA_PS_SENSOR_HEADING_TOPIC,
                     lambda value, name=root: self._set_heading(name, value))
        self._listen(agent, root, Topics.WARA_PS_SENSOR_COURSE_TOPIC,
                     lambda value, name=root: self._set_course(name, value))
        self._listen(agent, root, Topics.WARA_PS_SENSOR_SPEED_TOPIC,
                     lambda value, name=root: self._set_speed(name, value))
        self._listen(agent, root, Topics.WARA_PS_SENSOR_ROLL_TOPIC,
                     lambda value, name=root: self._set_roll(name, value))
        self._listen(agent, root, Topics.WARA_PS_SENSOR_PITCH_TOPIC,
                     lambda value, name=root: self._set_pitch(name, value))
        agent.latlon = self._node.create_publisher(
            GeoPoint, absolute(root, self._latlon_name), 10)
        agent.odom = self._node.create_publisher(
            Odometry, absolute(root, self._odom_name), 10)
        self._node.get_logger().info(
            f'Publishing {root} as {absolute(root, self._latlon_name)} and '
            f'{absolute(root, self._odom_name)} in {self.odom_frame}')

    def _listen(self, agent, root, constant, save):
        def on_msg(msg):
            value = scalar(msg.data)
            if value is None:
                self._warn(
                    absolute(root, constant),
                    f'Ignoring malformed scalar payload on {absolute(root, constant)}: {msg.data}')
                return
            save(value)

        agent.subscriptions.append(self._node.create_subscription(
            String, absolute(root, constant), on_msg, 10))

    def _set_heading(self, root, value):
        self._agents[root].heading = value

    def _set_course(self, root, value):
        self._agents[root].course = value

    def _set_speed(self, root, value):
        self._agents[root].speed = value

    def _set_roll(self, root, value):
        self._agents[root].roll = value

    def _set_pitch(self, root, value):
        self._agents[root].pitch = value

    def _on_position(self, root, msg):
        sample = geopoint(msg.data)
        if sample is None:
            self._warn(root, f'Ignoring malformed position payload: {msg.data}')
            return
        if sample.unexpected_type:
            self._warn(root, f'Position payload type is not GeoPoint: {msg.data}')
        agent = self._agents[root]
        agent.position = sample
        agent.stamp = self._node.get_clock().now()

    def _send(self, root, agent):
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
            self._warn(root, f'Ignoring position that is not a UTM point: {error}')
            return
        frame = self._utm_override or utm.header.frame_id
        transform = self._transform(frame)
        if transform is None:
            return

        pose = PoseStamped()
        pose.header.stamp = (agent.stamp or self._node.get_clock().now()).to_msg()
        pose.header.frame_id = frame
        pose.pose.position.x = utm.point.x
        pose.pose.position.y = utm.point.y
        pose.pose.position.z = pose_altitude(utm.point.z)
        heading = chosen_heading(agent.heading, agent.course, self._prefer_heading)
        yaw = enu_yaw(heading, self._angle_unit) if heading is not None else 0.0
        roll = to_radians(0.0 if agent.roll is None else agent.roll, self._angle_unit)
        pitch = to_radians(0.0 if agent.pitch is None else agent.pitch, self._angle_unit)
        x, y, z, w = orientation(roll, pitch, yaw)
        pose.pose.orientation.x = x
        pose.pose.orientation.y = y
        pose.pose.orientation.z = z
        pose.pose.orientation.w = w

        odom_pose = do_transform_pose_stamped(pose, transform)
        odom = Odometry()
        odom.header = odom_pose.header
        odom.child_frame_id = child_frame(root, self._base_link)
        odom.pose.pose = odom_pose.pose
        odom.pose.covariance[0] = self._cov[0]
        odom.pose.covariance[7] = self._cov[1]
        odom.pose.covariance[14] = self._cov[2]
        if agent.speed is not None:
            facing = chosen_heading(agent.heading, agent.course, self._prefer_heading)
            facing_yaw = enu_yaw(facing, self._angle_unit) if facing is not None else 0.0
            course_yaw = enu_yaw(agent.course, self._angle_unit) if agent.course is not None else None
            odom.twist.twist.linear.x, odom.twist.twist.linear.y = body_velocity(
                agent.speed, facing_yaw, course_yaw)
        agent.odom.publish(odom)

    def close(self):
        self._georef.shutdown()

    def _transform(self, utm_frame):
        cached = self._cache.get(utm_frame)
        if cached is not None:
            return cached
        try:
            found = self._georef.lookup_transform(
                self.odom_frame, utm_frame, self._timeout)
        except TransformException as error:
            self._warn(
                utm_frame,
                f'Cannot cache transform from {utm_frame} to {self.odom_frame}: {error}')
            return None
        self._cache[utm_frame] = found
        self._node.get_logger().info(
            f'Cached constant transform {utm_frame} -> {self.odom_frame}')
        return found

    def _warn(self, key, text):
        now = self._node.get_clock().now()
        last = self._warned.get(key)
        if last is not None and now - last < _WARN_EVERY:
            return
        self._warned[key] = now
        self._node.get_logger().warning(text)


def main(args=None):
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
