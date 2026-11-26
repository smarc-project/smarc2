"""Pure conversions. No rclpy."""

import math

from smarc_msgs.msg import Topics
from smarc_utilities.topic_utils import STRING_MSG

from waraps_officer.waraps_agents_encoding import (
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

PREFIX = Topics.WARA_PS_SENSOR_PREFIX
POSITION = Topics.WARA_PS_SENSOR_POSITION_TOPIC
HEADING = Topics.WARA_PS_SENSOR_HEADING_TOPIC


def test_parse_geopoint_reads_the_three_fields():
    sample = parse_geopoint('{"type": "GeoPoint", "latitude": 58.85, "longitude": 17.67, "altitude": 1.5}')
    assert sample.latitude == 58.85
    assert sample.longitude == 17.67
    assert sample.altitude == 1.5
    assert sample.unexpected_type is None


def test_parse_geopoint_keeps_numbers_when_the_type_is_something_else():
    sample = parse_geopoint('{"type": "Point", "latitude": 1, "longitude": 2, "altitude": 3}')
    assert (sample.latitude, sample.longitude, sample.altitude) == (1.0, 2.0, 3.0)
    assert sample.unexpected_type == 'Point'


def test_parse_geopoint_rejects_a_payload_without_altitude():
    assert parse_geopoint('{"latitude": 1, "longitude": 2}') is None
    assert parse_geopoint('not json') is None
    assert parse_geopoint('{"latitude": "58", "longitude": 2, "altitude": 3}') is None


def test_parse_scalar_accepts_a_number_a_string_and_a_bare_float():
    assert parse_scalar('1.5') == 1.5
    assert parse_scalar('"2.5"') == 2.5
    assert parse_scalar(' 3 ') == 3.0
    assert parse_scalar('nope') is None
    assert parse_scalar('true') is None
    assert parse_scalar('"nope"') is None


def test_north_is_enu_yaw_pi_over_2_and_east_is_zero():
    assert enu_yaw(0.0, 'deg') == math.pi / 2
    assert enu_yaw(90.0, 'deg') == 0.0
    assert enu_yaw(math.pi / 2, 'rad') == 0.0
    assert to_radians(180.0, 'degrees') == math.pi
    assert to_radians(math.pi, 'radians') == math.pi


def test_speed_along_the_course_is_sideways_when_the_nose_points_north():
    facing = enu_yaw(0.0, 'deg')
    course = enu_yaw(90.0, 'deg')
    forward, left = body_velocity(1.25, facing, course)
    assert abs(forward) < 1e-9
    assert abs(left - -1.25) < 1e-9
    assert body_velocity(1.25, facing, None) == (1.25, 0.0)
    assert body_velocity(1.25, facing, facing) == (1.25, 0.0)


def test_heading_wins_unless_the_flag_says_course():
    assert chosen_heading(10.0, 20.0, True) == 10.0
    assert chosen_heading(None, 20.0, True) == 20.0
    assert chosen_heading(10.0, 20.0, False) == 20.0
    assert chosen_heading(10.0, None, False) == 10.0


def test_covariance_is_the_ellipse_squared_and_bad_altitude_is_zero():
    assert covariance_diagonal(1.0, 0.5, 0.0) == (1.0, 0.25, 0.0)
    assert pose_altitude(1.5) == 1.5
    assert pose_altitude(math.nan) == 0.0


def test_a_pure_yaw_of_pi_over_2_is_the_half_turn_quaternion():
    x, y, z, w = quaternion_xyzw(0.0, 0.0, math.pi / 2)
    assert abs(x) < 1e-12
    assert abs(y) < 1e-12
    assert abs(z - math.sin(math.pi / 4)) < 1e-12
    assert abs(w - math.cos(math.pi / 4)) < 1e-12


def test_frames_are_the_robot_and_the_agent():
    assert namespaced('evolo', 'odom') == 'evolo/odom'
    assert namespaced('aldo_evolo', 'base_link') == 'aldo_evolo/base_link'


def _graph(root, constant, types=None):
    return ('/' + namespaced(root, constant), types or [STRING_MSG])


def test_mirrored_agents_keep_a_mirrored_position_and_skip_our_robot():
    topics = [
        _graph('evolo', POSITION),
        _graph('aldo_evolo', POSITION),
        _graph('aldo_evolo', HEADING),
        _graph('heading_only', HEADING),
        _graph('ghost', POSITION, ['geographic_msgs/msg/GeoPoint']),
    ]
    found = mirrored_agents(topics, PREFIX, POSITION, 'evolo')
    assert [item.root for item in found] == ['aldo_evolo']
    assert found[0].position == '/' + namespaced('aldo_evolo', POSITION)
