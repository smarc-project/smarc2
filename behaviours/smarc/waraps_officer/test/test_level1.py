"""Payload shapes, with no ROS running."""

import json
import math

import pytest

from waraps_officer.level1 import (
    Agent,
    finite,
    fresh,
    heartbeat_json,
    levels,
    position_json,
    scalar_json,
    sensor_info_json,
)

AGENT = Agent(agent_type='underwater', agent_uuid='abc-123', name='sam0', rate_hz=2.0)


def test_scalar_is_a_json_number():
    assert json.loads(scalar_json(12.5)) == 12.5
    assert json.loads(scalar_json(3)) == 3.0


def test_position_is_a_geopoint():
    assert json.loads(position_json(58.8, 17.6, -2.5)) == {
        'latitude': 58.8, 'longitude': 17.6, 'altitude': -2.5, 'type': 'GeoPoint'}


def test_heartbeat_shape():
    hb = json.loads(heartbeat_json(AGENT, ['sensor', 'direct_execution'], 1700000000.5))
    assert hb == {
        'agent-type': 'underwater',
        'agent-uuid': 'abc-123',
        'levels': ['sensor', 'direct_execution'],
        'name': 'sam0',
        'rate': 2.0,
        'stamp': 1700000000.5,
        'type': 'HeartBeat',
    }


def test_sensor_info_shape():
    info = json.loads(sensor_info_json(AGENT, ['depth', 'position'], 12.0))
    assert info == {
        'name': 'sam0',
        'rate': 2.0,
        'sensor-data-provided': ['depth', 'position'],
        'stamp': 12.0,
        'type': 'SensorInfo',
    }


@pytest.mark.parametrize('direct, tst, expected', [
    (False, False, ['sensor']),
    (True, False, ['sensor', 'direct_execution']),
    (False, True, ['sensor', 'tst_execution']),
    (True, True, ['sensor', 'direct_execution', 'tst_execution']),
])
def test_levels_follow_who_is_there(direct, tst, expected):
    assert levels(direct, tst) == expected


def test_finite_rejects_nan_inf_and_non_numbers():
    assert finite(1.0, -2, 0.0)
    assert not finite(math.nan)
    assert not finite(1.0, math.inf)
    assert not finite(None)
    assert not finite('1.0')


def test_fresh_window():
    assert fresh(stamp_s=100.0, now_s=105.0, stale_after_s=10.0)
    assert fresh(stamp_s=100.0, now_s=110.0, stale_after_s=10.0)
    assert not fresh(stamp_s=100.0, now_s=110.1, stale_after_s=10.0)
    assert not fresh(stamp_s=None, now_s=110.0, stale_after_s=10.0)
    assert not fresh(stamp_s=200.0, now_s=110.0, stale_after_s=10.0)   # from the future (sim time reset)
