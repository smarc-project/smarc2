"""The whole node against a real broker: a mosquitto on a random port, the
WaraMQTTNode spinning in a thread, and a second paho client as the "cloud".
Skipped when mosquitto is not installed."""

import json
import random
import shutil
import socket
import subprocess
import threading
import time

import paho.mqtt.client as mqtt
import pytest
import rclpy
from rclpy.parameter import Parameter
from smarc_msgs.msg import Topics
from std_msgs.msg import String

from str_json_mqtt_bridge.bridge import WaraMQTTNode

PREFIX = Topics.WARA_PS_SENSOR_PREFIX
ROBOT = 'sam0'
UNIT = 'waraps/unit/subsurface/simulation'
NAMESPACE = f'{UNIT}/test_{ROBOT}'

pytestmark = pytest.mark.skipif(shutil.which('mosquitto') is None, reason='mosquitto not installed')


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


@pytest.fixture
def broker():
    port = free_port()
    proc = subprocess.Popen(['mosquitto', '-p', str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        try:
            socket.create_connection(('127.0.0.1', port), timeout=0.2).close()
            break
        except OSError:
            time.sleep(0.05)
    try:
        yield port
    finally:
        proc.terminate()
        proc.wait(timeout=5)


def paho_client():
    kwargs = {}
    if hasattr(mqtt, 'CallbackAPIVersion'):
        kwargs['callback_api_version'] = mqtt.CallbackAPIVersion.VERSION1
    return mqtt.Client(**kwargs)


def wait_for(predicate, timeout_s=10.0):
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        result = predicate()
        if result:
            return result
        time.sleep(0.05)
    return predicate()


def test_sensor_goes_to_broker_and_agent_comes_back(ros_graph, broker):
    overrides = [
        Parameter('robot_name', value=ROBOT),
        Parameter('mqtt.namespace', value=NAMESPACE),
        Parameter('mqtt.connection.host', value='127.0.0.1'),
        Parameter('mqtt.connection.port', value=broker),
        Parameter('mqtt.connection.keepalive', value=30),
        Parameter('mqtt.to_mqtt', value=['heartbeat']),
        Parameter('mqtt.to_ros', value=['exec/command']),
        Parameter('mqtt.to_ros_agents', value=['kkalem_sam']),
    ]
    bridge_node = ros_graph('waraps_bridge', f'/{ROBOT}/waraps',
                            allow_undeclared_parameters=True,
                            automatically_declare_parameters_from_overrides=True,
                            parameter_overrides=overrides)
    vehicle = ros_graph('vehicle', f'/{ROBOT}')
    reader = ros_graph('reader', '/')

    bridge = WaraMQTTNode(bridge_node)
    bridge._mqtt_client.loop_start()
    executor = rclpy.executors.SingleThreadedExecutor()
    executor.add_node(bridge_node)
    executor.add_node(reader)
    spinner = threading.Thread(target=executor.spin, daemon=True)
    spinner.start()
    try:
        # The cloud side.
        cloud_got = []
        cloud = paho_client()
        cloud.on_message = lambda c, u, m: cloud_got.append((m.topic, m.payload.decode()))
        cloud.connect('127.0.0.1', broker)
        cloud.subscribe(f'{NAMESPACE}/sensor/#')
        cloud.loop_start()
        assert wait_for(cloud.is_connected)
        assert wait_for(bridge._mqtt_client.is_connected)

        # A sensor nobody listed in yaml appears on the vehicle; the bridge finds it and forwards it.
        acoustic = vehicle.create_publisher(String, f'{PREFIX}/acoustic', 10)
        assert wait_for(lambda: vehicle.count_subscribers(f'{PREFIX}/acoustic') == 1)
        acoustic.publish(String(data=json.dumps({'rtt_s': 1.25})))
        assert wait_for(lambda: cloud_got or None) == [(f'{NAMESPACE}/sensor/acoustic', '{"rtt_s": 1.25}')]

        # Another agent publishes a sensor on the broker; it shows up in ROS under that agent.
        # The ROS publisher is created on the first message, so the reader may miss that one; keep sending.
        mirrored = []
        reader.create_subscription(String, f'/kkalem_sam/{Topics.WARA_PS_SENSOR_POSITION_TOPIC}', lambda m: mirrored.append(m.data), 10)
        position = '{"latitude": 58.8, "longitude": 17.6}'
        deadline = time.monotonic() + 10.0
        while not mirrored and time.monotonic() < deadline:
            cloud.publish(f'{UNIT}/kkalem_sam/sensor/position', position)
            time.sleep(0.2)
        assert mirrored and mirrored[0] == position

        # Our own sensor on the broker is not mirrored back, and the mirror is not forwarded out again.
        cloud.publish(f'{NAMESPACE}/sensor/position', position)
        time.sleep(1.5)
        assert [t for t, _ in cloud_got] == [f'{NAMESPACE}/sensor/acoustic', f'{NAMESPACE}/sensor/position']
        assert bridge_node.count_publishers(f'/{ROBOT}/{Topics.WARA_PS_SENSOR_POSITION_TOPIC}') == 0

        cloud.loop_stop()
        cloud.disconnect()
    finally:
        bridge._mqtt_client.disconnect()
        bridge._mqtt_client.loop_stop()
        executor.shutdown()
        spinner.join(timeout=5)
