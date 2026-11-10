"""How sensor names map between the broker and ROS. Pure; no rclpy.

ROS:    /<robot>/waraps/sensor/<name>        (Topics.WARA_PS_SENSOR_PREFIX)
broker: <unit>/<agent>/sensor/<name>         (<unit>/<agent> is mqtt.namespace)
"""

ALL_AGENTS = '#'


def mqtt_sensor_folder(sensor_prefix: str) -> str:
    """The broker's sensor folder: the last segment of Topics.WARA_PS_SENSOR_PREFIX.
    'waraps/sensor' -> 'sensor'. This is the one place that split happens."""
    return sensor_prefix.strip('/').rpartition('/')[2]


def unit_and_agent(mqtt_namespace: str) -> tuple[str, str]:
    """'waraps/unit/subsurface/simulation/ozer_sam0' -> ('waraps/unit/subsurface/simulation', 'ozer_sam0')."""
    unit, _, agent = mqtt_namespace.strip('/').rpartition('/')
    return unit, agent


def mirror_target(mqtt_topic: str, unit: str, own_agent: str, sensor_prefix: str) -> str | None:
    """ROS topic for a sensor string another agent put on the broker, or None.

    '<unit>/<agent>/sensor/<name>' -> '/<agent>/<sensor_prefix>/<name>'. The name
    may contain slashes. Our own agent and anything outside the unit are None.
    """
    unit_parts = unit.strip('/').split('/')
    parts = mqtt_topic.split('/')
    if parts[:len(unit_parts)] != unit_parts:
        return None
    rest = parts[len(unit_parts):]
    if len(rest) < 3 or rest[1] != mqtt_sensor_folder(sensor_prefix):
        return None
    agent, name = rest[0], '/'.join(rest[2:])
    if not agent or agent == own_agent or '' in rest[2:]:
        return None
    return f'/{agent}/{sensor_prefix.strip("/")}/{name}'
