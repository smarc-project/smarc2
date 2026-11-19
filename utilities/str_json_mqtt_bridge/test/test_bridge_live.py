"""Discovery and agent mirroring on a real rclpy graph, with a fake broker."""

import json
import time

import rclpy
from smarc_msgs.msg import Topics
from std_msgs.msg import String

from str_json_mqtt_bridge.bridge import MqttAgentsToRos, RosToMqtt, discover_sensor_bridges

PREFIX = Topics.WARA_PS_SENSOR_PREFIX
ROOT = '/sam0'
NAMESPACE = 'waraps/unit/subsurface/simulation/ozer_sam0'
UNIT = 'waraps/unit/subsurface/simulation'


def spin_until(node, predicate, timeout_s=5.0):
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)
        result = predicate()
        if result:
            return result
    return predicate()


def test_discovery_opens_one_bridge_per_new_sensor_and_forwards(ros_graph, mqtt_client):
    bridge_node = ros_graph('bridge', f'{ROOT}/waraps')
    vehicle = ros_graph('vehicle', ROOT)
    stick = ros_graph('stick', '/stick_2')

    acoustic = vehicle.create_publisher(String, f'{PREFIX}/acoustic', 10)          # /sam0/waraps/sensor/acoustic
    vehicle.create_publisher(String, Topics.WARA_PS_SENSOR_POSITION_TOPIC, 10)                      # also in the yaml list below
    stick.create_publisher(String, f'{PREFIX}/acoustic', 10)                        # another robot, not ours
    bridge_node.create_publisher(String, f'/kkalem_sam/{Topics.WARA_PS_SENSOR_POSITION_TOPIC}', 10)      # our own mirror of an agent

    # What the yaml would have opened.
    bridges = [RosToMqtt(bridge_node, mqtt_client, bridge_node.resolve_topic_name('sensor/position'),
                         f'{NAMESPACE}/sensor/position')]

    def discover():
        return discover_sensor_bridges(bridge_node, mqtt_client, NAMESPACE, ROOT, bridges) or None

    opened = spin_until(bridge_node, discover)
    assert [b.ros_topic for b in opened] == [f'{ROOT}/{PREFIX}/acoustic']
    assert opened[0].mqtt_topic == f'{NAMESPACE}/sensor/acoustic'
    assert len(bridges) == 2                                        # position was not opened twice

    # Settled graph: nothing more to open.
    time.sleep(0.5)
    rclpy.spin_once(bridge_node, timeout_sec=0.1)
    assert discover_sensor_bridges(bridge_node, mqtt_client, NAMESPACE, ROOT, bridges) == []
    assert len(bridges) == 2

    # The discovered bridge is subscribed (the fake client says it is connected) and forwards JSON.
    acoustic.publish(String(data=json.dumps({'rtt_s': 1.25, 'peer': 'stick_1'})))
    published = spin_until(bridge_node, lambda: mqtt_client.published or None)
    assert published == [(f'{NAMESPACE}/sensor/acoustic', '{"rtt_s": 1.25, "peer": "stick_1"}')]


def test_ros_to_mqtt_subscribes_once(ros_graph, mqtt_client):
    node = ros_graph('bridge', f'{ROOT}/waraps')
    bridge = RosToMqtt(node, mqtt_client, f'{ROOT}/{PREFIX}/acoustic', f'{NAMESPACE}/sensor/acoustic')
    bridge.on_reconnect()
    bridge.on_reconnect()
    assert node.count_subscribers(f'{ROOT}/{PREFIX}/acoustic') == 1
    bridge.on_disconnect()
    bridge.on_disconnect()
    assert node.count_subscribers(f'{ROOT}/{PREFIX}/acoustic') == 0


def test_agents_are_mirrored_into_their_own_namespace(ros_graph, mqtt_client):
    bridge_node = ros_graph('bridge', f'{ROOT}/waraps')
    reader = ros_graph('reader', '/')
    got = []
    reader.create_subscription(String, f'/kkalem_sam/{Topics.WARA_PS_SENSOR_POSITION_TOPIC}', lambda m: got.append(m.data), 10)

    agents = MqttAgentsToRos(bridge_node, mqtt_client, NAMESPACE, ['kkalem_sam', 'ozer_sam0'])
    assert agents.filters == [f'{UNIT}/kkalem_sam/sensor/#']           # our own agent is dropped
    agents.on_reconnect()
    assert mqtt_client.subscribed == agents.filters
    assert set(mqtt_client.callbacks) == set(agents.filters)

    payload = '{"latitude": 58.8, "longitude": 17.6}'
    assert agents.mirror(f'{UNIT}/kkalem_sam/sensor/position', payload) == f'/kkalem_sam/{Topics.WARA_PS_SENSOR_POSITION_TOPIC}'
    assert agents.mirror(f'{UNIT}/ozer_sam0/sensor/position', payload) is None
    assert agents.mirror(f'{UNIT}/kkalem_sam/heartbeat', payload) is None

    assert spin_until(reader, lambda: got or None) == [payload]

    agents.mirror(f'{UNIT}/kkalem_sam/sensor/position', payload)
    assert bridge_node.count_publishers(f'/kkalem_sam/{Topics.WARA_PS_SENSOR_POSITION_TOPIC}') == 1   # one publisher per topic

    agents.on_disconnect()
    assert mqtt_client.subscribed == []
    assert mqtt_client.callbacks == {}


def test_hash_means_every_agent_in_the_unit(ros_graph, mqtt_client):
    bridge_node = ros_graph('bridge', f'{ROOT}/waraps')
    agents = MqttAgentsToRos(bridge_node, mqtt_client, NAMESPACE, ['#'])
    assert agents.filters == [f'{UNIT}/+/sensor/#']
    assert agents.mirror(f'{UNIT}/anyone/sensor/depth', '1.5') == f'/anyone/{Topics.WARA_PS_SENSOR_DEPTH_TOPIC}'
    assert agents.mirror(f'{UNIT}/ozer_sam0/sensor/depth', '1.5') is None


def test_another_robots_mirror_is_not_forwarded_back_out(ros_graph, mqtt_client):
    """Two robots on one graph (simulation). sam0's bridge mirrors kkalem_sam's
    position into /kkalem_sam/waraps/sensor/position. kkalem_sam's bridge must
    not forward that mirror, or it goes round the broker forever."""
    sam0_bridge = ros_graph('bridge', f'{ROOT}/waraps')
    kkalem_bridge = ros_graph('bridge', '/kkalem_sam/waraps')
    kkalem_vehicle = ros_graph('vehicle', '/kkalem_sam')

    MqttAgentsToRos(sam0_bridge, mqtt_client, NAMESPACE, ['kkalem_sam']).mirror(f'{UNIT}/kkalem_sam/sensor/position', '{}')
    kkalem_vehicle.create_publisher(String, Topics.WARA_PS_SENSOR_DEPTH_TOPIC, 10)        # a real sensor of kkalem_sam

    def discover():
        return discover_sensor_bridges(kkalem_bridge, mqtt_client, f'{UNIT}/kkalem_sam', '/kkalem_sam', []) or None

    found = spin_until(kkalem_bridge, discover)
    assert [b.ros_topic for b in found] == [f'/kkalem_sam/{Topics.WARA_PS_SENSOR_DEPTH_TOPIC}']
    time.sleep(0.5)
    rclpy.spin_once(kkalem_bridge, timeout_sec=0.1)
    assert [b.ros_topic for b in discover()] == [f'/kkalem_sam/{Topics.WARA_PS_SENSOR_DEPTH_TOPIC}']
