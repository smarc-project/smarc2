import inspect
import threading
from types import SimpleNamespace

from smarc_msgs.msg import Topics
from str_json_mqtt_bridge.bridge import (
    RosToMqtt,
    WaraMQTTNode,
    string_topics_under_sensor as bridge_topics,
)
from wasp_bt.waraps.waraps_vehicle import (
    WaraPSVehicle,
    string_topics_under_sensor as vehicle_topics,
)

POSITION = Topics.WARA_PS_SENSOR_POSITION_TOPIC
STRING = 'std_msgs/msg/String'


def _publishers(names):
    return lambda topic: topic in names


def test_copies_match():
    assert inspect.getsource(vehicle_topics) == inspect.getsource(bridge_topics)


def test_vehicle_and_bridge_namespaces():
    topics = [
        ('/sam0/waraps/sensor/position', [STRING]),
        ('/sam0/waraps/sensor/heading', [STRING]),
        ('/sam0/waraps/sensor/acoustic', [STRING]),
        ('/sam0/waraps/sensor/foo/bar', [STRING]),
        ('/sam0/waraps/sensor/bt', [STRING]),
        ('/sam0/waraps/sensor/executing_tasks', [STRING]),
        ('/sam0/waraps/sensor_info', [STRING]),
        ('/sam0/waraps/heartbeat', [STRING]),
        ('/sam0/waraps/exec/response', [STRING]),
        ('/sam0/waraps/tst/feedback', [STRING]),
        ('/sam0/waraps/sensor/speed_ms', ['std_msgs/msg/Float64']),
        ('/sam0/waraps/sensor/ghost', [STRING]),
        ('/stick_2/waraps/sensor/acoustic', [STRING]),
    ]
    publishing = {
        '/sam0/waraps/sensor/position',
        '/sam0/waraps/sensor/heading',
        '/sam0/waraps/sensor/acoustic',
        '/sam0/waraps/sensor/foo/bar',
        '/sam0/waraps/sensor/bt',
        '/sam0/waraps/sensor/executing_tasks',
        '/sam0/waraps/sensor_info',
        '/sam0/waraps/heartbeat',
        '/sam0/waraps/exec/response',
        '/sam0/waraps/tst/feedback',
        '/stick_2/waraps/sensor/acoustic',
    }
    is_pub = _publishers(publishing)

    vehicle = vehicle_topics(topics, '/sam0', POSITION, is_pub)
    bridge = bridge_topics(topics, '/sam0/waraps', POSITION, is_pub)
    assert vehicle == bridge_topics(topics, '/sam0', POSITION, is_pub)

    assert [name for _rel, name in vehicle] == [
        'acoustic', 'bt', 'executing_tasks', 'foo/bar', 'heading', 'position',
    ]
    assert [rel for rel, _name in vehicle] == [
        'waraps/sensor/acoustic',
        'waraps/sensor/bt',
        'waraps/sensor/executing_tasks',
        'waraps/sensor/foo/bar',
        'waraps/sensor/heading',
        'waraps/sensor/position',
    ]
    assert [rel for rel, _name in bridge] == [
        'sensor/acoustic',
        'sensor/bt',
        'sensor/executing_tasks',
        'sensor/foo/bar',
        'sensor/heading',
        'sensor/position',
    ]

    yaml = {
        'heartbeat',
        'sensor_info',
        'sensor/position',
        'sensor/heading',
        'sensor/executing_tasks',
        'sensor/bt',
        'exec/response',
        'tst/feedback',
    }
    assert [rel for rel, _name in bridge if rel not in yaml] == [
        'sensor/acoustic',
        'sensor/foo/bar',
    ]


def test_root_namespace():
    topics = [('/waraps/sensor/acoustic', [STRING])]
    found = vehicle_topics(topics, '/', POSITION, lambda _topic: True)
    assert found == [('waraps/sensor/acoustic', 'acoustic')]


def test_yaml_topic_is_not_opened_twice():
    node = WaraMQTTNode.__new__(WaraMQTTNode)
    node._bridges_lock = threading.Lock()
    node._mqtt_namespace = 'waraps/unit/subsurface/simulation/sam_test'
    node._mqtt_client = SimpleNamespace(is_connected=lambda: False)
    node.node = SimpleNamespace()
    prefix = POSITION.rpartition('/')[0]
    sensor_dir = prefix.split('/', 1)[1]
    leaf = POSITION.rpartition('/')[2]
    position_rel = sensor_dir + '/' + leaf
    acoustic_rel = sensor_dir + '/acoustic'
    existing = RosToMqtt.__new__(RosToMqtt)
    existing._ros_topic = position_rel
    node.ros_to_mqtt_bridges = [existing]
    opened = []
    node._log = opened.append

    node._open_ros_to_mqtt(position_rel)
    assert node.ros_to_mqtt_bridges == [existing]
    assert opened == []

    node._open_ros_to_mqtt(acoustic_rel)
    assert [bridge._ros_topic for bridge in node.ros_to_mqtt_bridges] == [
        position_rel,
        acoustic_rel,
    ]
    assert opened == ['ROS to MQTT sensor topic: ' + acoustic_rel]
    assert node.ros_to_mqtt_bridges[1]._subscription is None


def test_live_graph_advertises_without_subscribing():
    import rclpy
    from std_msgs.msg import Float64, String

    rclpy.init()
    vehicle_node = bridge_node = other = None
    try:
        vehicle_node = rclpy.create_node('waraps_vehicle', namespace='/sam0')
        bridge_node = rclpy.create_node('mqtt_bridge_cloud', namespace='/sam0/waraps')
        other = rclpy.create_node('stick', namespace='/stick_2')
        wara = WaraPSVehicle(vehicle_node, None, {
            'agent-type': 'air',
            'agent-uuid': 'u',
            'levels': ['sensor'],
            'name': 'sam0',
            'pulse_rate': 1.0,
        })
        prefix = POSITION.rpartition('/')[0]
        acoustic_topic = prefix + '/acoustic'
        nested_topic = prefix + '/foo/bar'
        speed_topic = prefix + '/speed_ms'
        foreign_topic = prefix + '/foreign'
        ghost_topic = prefix + '/ghost'
        hold = [
            vehicle_node.create_publisher(String, acoustic_topic, 10),
            vehicle_node.create_publisher(String, nested_topic, 10),
            vehicle_node.create_publisher(Float64, speed_topic, 10),
            other.create_publisher(String, foreign_topic, 10),
            vehicle_node.create_subscription(String, ghost_topic, lambda _msg: None, 10),
        ]
        subs_before = len(list(vehicle_node.subscriptions))
        names = []
        for _ in range(40):
            rclpy.spin_once(vehicle_node, timeout_sec=0.05)
            rclpy.spin_once(bridge_node, timeout_sec=0.05)
            rclpy.spin_once(other, timeout_sec=0.05)
            wara._refresh_sensor_data_provided()
            names = list(wara._sensor_info_data['sensor-data-provided'])
            if {'position', 'heading', 'acoustic', 'foo/bar'} <= set(names):
                break

        assert 'position' in names
        assert 'heading' in names
        assert 'course' in names
        assert 'speed' in names
        assert 'roll' in names
        assert 'pitch' in names
        assert 'depth' in names
        assert 'acoustic' in names
        assert 'foo/bar' in names
        assert 'foreign' not in names
        assert 'ghost' not in names
        assert 'speed_ms' not in names
        assert 'sensor_info' not in names
        assert 'heartbeat' not in names
        assert 'executing_tasks' not in names
        assert 'bt' not in names
        assert len(list(vehicle_node.subscriptions)) == subs_before

        def is_string_publisher(topic, node=bridge_node):
            return any(
                info.topic_type == STRING
                for info in node.get_publishers_info_by_topic(topic)
            )

        bridged = bridge_topics(
            bridge_node.get_topic_names_and_types(),
            bridge_node.get_namespace(),
            POSITION,
            is_string_publisher,
        )
        relatives = [rel for rel, _name in bridged]
        assert 'sensor/position' in relatives
        assert 'sensor/acoustic' in relatives
        assert 'sensor/foo/bar' in relatives
        assert 'heartbeat' not in relatives
        assert 'sensor_info' not in relatives
        assert 'sensor/foreign' not in relatives
        assert hold
    finally:
        for node in (vehicle_node, bridge_node, other):
            if node is not None:
                node.destroy_node()
        rclpy.shutdown()
