"""node_string_topics_under against a real rclpy graph on a private domain."""

import time

import rclpy
from smarc_msgs.msg import Topics
from std_msgs.msg import Float32, String

from smarc_utilities.topic_utils import node_string_topics_under

PREFIX = Topics.WARA_PS_SENSOR_PREFIX
ROOT = '/sam0'


def spin_until(node, predicate, timeout_s=5.0):
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)
        result = predicate()
        if result:
            return result
    return predicate()


def test_bridge_sees_others_but_not_its_own_mirrors(ros_graph):
    bridge = ros_graph('bridge', f'{ROOT}/waraps')
    vehicle = ros_graph('vehicle', ROOT)
    stick = ros_graph('stick', '/stick_2')

    vehicle.create_publisher(String, f'{PREFIX}/acoustic', 10)           # /sam0/waraps/sensor/acoustic
    vehicle.create_publisher(Float32, f'{PREFIX}/depth', 10)             # wrong type
    vehicle.create_publisher(String, f'other/{PREFIX}/value', 10)        # prefix later in the name
    stick.create_publisher(String, f'{PREFIX}/acoustic', 10)             # other root
    bridge.create_publisher(String, f'{ROOT}/{PREFIX}/mirrored', 10)     # the bridge's own mirror
    vehicle.create_subscription(String, f'{PREFIX}/subscribed_only', lambda m: None, 10)

    found = spin_until(
        bridge,
        lambda: node_string_topics_under(bridge, ROOT, PREFIX, include_own=False) or None,
    )
    assert [t.absolute for t in found] == [f'{ROOT}/{PREFIX}/acoustic']
    assert found[0].name == 'acoustic'

    # Still only the one once the graph has settled.
    time.sleep(0.5)
    rclpy.spin_once(bridge, timeout_sec=0.1)
    assert [t.name for t in node_string_topics_under(bridge, ROOT, PREFIX, include_own=False)] == ['acoustic']

    # The bridge's own mirror shows up only when asked for.
    with_own = node_string_topics_under(bridge, ROOT, PREFIX, include_own=True)
    assert [t.name for t in with_own] == ['acoustic', 'mirrored']


def test_vehicle_lists_its_own_sensors_and_the_sticks(ros_graph):
    vehicle = ros_graph('vehicle', ROOT)
    stick = ros_graph('stick', ROOT)
    stick.create_publisher(String, f'{PREFIX}/acoustic/stick_1', 10)
    vehicle.create_publisher(String, f'{PREFIX}/position', 10)

    def both_seen():
        found = node_string_topics_under(vehicle, vehicle.get_namespace(), PREFIX, include_own=True)
        return found if len(found) == 2 else None

    found = spin_until(vehicle, both_seen)
    assert [t.name for t in found] == ['acoustic/stick_1', 'position']

    others = node_string_topics_under(vehicle, vehicle.get_namespace(), PREFIX, include_own=False)
    assert [t.name for t in others] == ['acoustic/stick_1']
