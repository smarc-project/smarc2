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


def test_only_string_topics_published_from_under_the_root(ros_graph):
    bridge = ros_graph('bridge', f'{ROOT}/waraps')
    vehicle = ros_graph('vehicle', ROOT)
    stick = ros_graph('stick', '/stick_2')
    other_bridge = ros_graph('bridge', '/kkalem_sam/waraps')

    vehicle.create_publisher(String, f'{PREFIX}/acoustic', 10)                         # /sam0/waraps/sensor/acoustic
    vehicle.create_publisher(Float32, Topics.WARA_PS_SENSOR_DEPTH_TOPIC, 10)            # wrong type
    vehicle.create_publisher(String, f'other/{PREFIX}/value', 10)                      # prefix later in the name
    stick.create_publisher(String, f'{PREFIX}/acoustic', 10)                           # another root
    other_bridge.create_publisher(String, f'{ROOT}/{Topics.WARA_PS_SENSOR_POSITION_TOPIC}', 10)   # another robot's mirror of us
    vehicle.create_subscription(String, f'{PREFIX}/subscribed_only', lambda m: None, 10)

    found = spin_until(bridge, lambda: node_string_topics_under(bridge, ROOT, PREFIX) or None)
    assert [t.absolute for t in found] == [f'{ROOT}/{PREFIX}/acoustic']
    assert found[0].name == 'acoustic'

    # Still only the one once the graph has settled.
    time.sleep(0.5)
    rclpy.spin_once(bridge, timeout_sec=0.1)
    assert [t.name for t in node_string_topics_under(bridge, ROOT, PREFIX)] == ['acoustic']


def test_vehicle_lists_its_own_sensors_and_the_sticks(ros_graph):
    vehicle = ros_graph('vehicle', ROOT)
    stick = ros_graph('stick', ROOT)
    stick.create_publisher(String, f'{PREFIX}/acoustic/stick_1', 10)
    vehicle.create_publisher(String, Topics.WARA_PS_SENSOR_POSITION_TOPIC, 10)

    def both_seen():
        found = node_string_topics_under(vehicle, vehicle.get_namespace(), PREFIX)
        return found if len(found) == 2 else None

    found = spin_until(vehicle, both_seen)
    assert [t.name for t in found] == ['acoustic/stick_1', 'position']
