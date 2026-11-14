"""WARA-PS sensor strings to a lat/lon and an ENU yaw. No rclpy.

``agent_roots`` finds other agents the bridge has mirrored. The bridge
publishes ``/<agent>/waraps/sensor/*`` from our vehicle's namespace, so the
publisher-under-root filter in ``node_string_topics_under`` hides every one
of them. The prefix and the position topic are the Topics constants, matched
whole.
"""

import json
import math
from dataclasses import dataclass

from smarc_utilities.topic_utils import STRING_MSG, string_topics_under
from transforms3d.euler import euler2quat


@dataclass(frozen=True)
class GeoSample:
    latitude: float
    longitude: float
    altitude: float
    unexpected_type: str | None = None


@dataclass(frozen=True)
class MirroredAgent:
    """One other agent. ``root`` has no leading slash. ``position`` is the
    graph name of its position string, used to check a publisher exists."""

    root: str
    position: str


def absolute(root, name):
    return f"{root.strip('/')}/{name.strip('/')}"


def odom_frame(robot_name, odom_link):
    return f"{robot_name.strip('/')}/{odom_link.strip('/')}"


def child_frame(root, base_link):
    return f"{root.strip('/')}/{base_link.strip('/')}"


def geopoint(text):
    """A WARA-PS GeoPoint JSON object, or None when the three fields are missing.

    A ``type`` other than ``GeoPoint`` is kept on ``unexpected_type`` and the
    numbers are still returned. The C++ node warned and used them.
    """
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    if not all(key in payload for key in ('latitude', 'longitude', 'altitude')):
        return None
    latitude = _number(payload['latitude'])
    longitude = _number(payload['longitude'])
    altitude = _number(payload['altitude'])
    if latitude is None or longitude is None or altitude is None:
        return None
    kind = payload.get('type')
    unexpected = kind if isinstance(kind, str) and kind != 'GeoPoint' else None
    return GeoSample(latitude, longitude, altitude, unexpected)


def scalar(text):
    """A JSON number, a JSON string of a number, or a bare float. None otherwise."""
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = text.strip()
    number = _number(parsed)
    if number is not None:
        return number
    if isinstance(parsed, str):
        try:
            return float(parsed)
        except ValueError:
            return None
    return None


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _in_radians(unit):
    return unit in ('rad', 'radian', 'radians')


def to_radians(angle, unit):
    if _in_radians(unit):
        return angle
    return math.radians(angle)


def enu_yaw(angle, unit):
    """Heading to ENU yaw. 0 (north) is pi/2. 90 degrees (east) is 0."""
    return math.pi / 2.0 - to_radians(angle, unit)


def chosen_heading(heading, course, prefer_heading):
    if prefer_heading:
        return heading if heading is not None else course
    return course if course is not None else heading


def pose_altitude(altitude):
    """Non-finite UTM altitude is pose z 0. The GeoPoint keeps the raw value."""
    if math.isfinite(altitude):
        return altitude
    return 0.0


def covariance_diagonal(ellipse_x, ellipse_y, ellipse_z):
    return ellipse_x ** 2, ellipse_y ** 2, ellipse_z ** 2


def orientation(roll, pitch, yaw):
    """``tf2`` setRPY order. Returns x, y, z, w."""
    w, x, y, z = euler2quat(roll, pitch, yaw, axes='sxyz')
    return x, y, z, w


def _roots_before(topics, prefix):
    """Namespaces that have a String topic under ``prefix``, with a name after it."""
    head = [part for part in prefix.split('/') if part]
    if not head:
        return []
    width = len(head)
    roots = []
    for absolute_name, types in topics:
        if STRING_MSG not in types:
            continue
        segments = [part for part in absolute_name.split('/') if part]
        for start in range(1, len(segments) - width):
            if segments[start:start + width] != head:
                continue
            roots.append('/'.join(segments[:start]))
            break
    return roots


def agent_roots(topics, prefix, position_topic, own_root):
    """Agents whose position string is on the graph. ``own_root`` is skipped.

    ``prefix`` is ``Topics.WARA_PS_SENSOR_PREFIX``. ``position_topic`` is
    ``Topics.WARA_PS_SENSOR_POSITION_TOPIC``. A heading with no position is
    not an agent yet: latlon needs the GeoPoint.
    """
    own = own_root.strip('/')
    found = []
    seen = set()
    for root in _roots_before(topics, prefix):
        if not root or root == own or root in seen:
            continue
        wanted = absolute(root, position_topic)
        under = string_topics_under(topics, root, prefix)
        match = next((item for item in under if item.absolute.strip('/') == wanted), None)
        if match is None:
            continue
        seen.add(root)
        found.append(MirroredAgent(root, match.absolute))
    found.sort(key=lambda item: item.root)
    return found
