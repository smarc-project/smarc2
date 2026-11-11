"""WARA-PS level 1 payloads. Pure; no rclpy.

Everything the vehicle node puts on the wire is built here, so the shapes
are tested without a ROS graph. Every payload is ``json.dumps`` output; the
bridge forwards it unchanged.
"""

import json
import math
from dataclasses import dataclass

SENSOR_LEVEL = 'sensor'
DIRECT_EXECUTION_LEVEL = 'direct_execution'
TST_EXECUTION_LEVEL = 'tst_execution'


@dataclass(frozen=True)
class Agent:
    """Who this heartbeat is about."""
    agent_type: str
    agent_uuid: str
    name: str
    rate_hz: float


@dataclass(frozen=True)
class Reading:
    """One float from a vehicle topic and when it arrived (ROS seconds)."""
    value: float
    stamp_s: float


@dataclass(frozen=True)
class LatLon:
    latitude: float
    longitude: float
    stamp_s: float


def finite(*values) -> bool:
    return all(isinstance(v, (int, float)) and math.isfinite(v) for v in values)


def fresh(stamp_s, now_s, stale_after_s) -> bool:
    """True while a reading stamped ``stamp_s`` is young enough to publish."""
    return stamp_s is not None and 0.0 <= now_s - stamp_s <= stale_after_s


def levels(direct_execution: bool, tst_execution: bool) -> list:
    out = [SENSOR_LEVEL]
    if direct_execution:
        out.append(DIRECT_EXECUTION_LEVEL)
    if tst_execution:
        out.append(TST_EXECUTION_LEVEL)
    return out


def scalar_json(value) -> str:
    return json.dumps(float(value))


def position_json(latitude, longitude, altitude) -> str:
    return json.dumps({
        'latitude': float(latitude),
        'longitude': float(longitude),
        'altitude': float(altitude),
        'type': 'GeoPoint',
    })


def heartbeat_json(agent: Agent, agent_levels, stamp_s) -> str:
    return json.dumps({
        'agent-type': agent.agent_type,
        'agent-uuid': agent.agent_uuid,
        'levels': list(agent_levels),
        'name': agent.name,
        'rate': agent.rate_hz,
        'stamp': stamp_s,
        'type': 'HeartBeat',
    })


def sensor_info_json(agent: Agent, sensor_names, stamp_s) -> str:
    return json.dumps({
        'name': agent.name,
        'rate': agent.rate_hz,
        'sensor-data-provided': list(sensor_names),
        'stamp': stamp_s,
        'type': 'SensorInfo',
    })
