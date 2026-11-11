"""WarapsVehicle against a real rclpy graph on a private domain."""

import json
import math
import time

import pytest
from geographic_msgs.msg import GeoPoint
from nav_msgs.msg import Odometry
from rclpy.parameter import Parameter
from smarc_msgs.msg import Topics
from smarc_utilities.testing import wait_for
from std_msgs.msg import Float32, String
from transforms3d.euler import euler2quat

from waraps_officer.waraps_vehicle import WarapsVehicle

ROOT = '/sam0'
PREFIX = Topics.WARA_PS_SENSOR_PREFIX
LAT, LON, WATER_ALT, GROUND_ALT = 58.8, 17.6, -1.5, 4.2
DEPTH, ROLL, PITCH = 3.5, 0.1, 0.2


class Listener:
    """Last JSON payload and message count per WARA-PS topic."""

    def __init__(self, node, topics):
        self.last = {}
        self.count = {t: 0 for t in topics}
        for topic in topics:
            node.create_subscription(String, topic, self._cb(topic), 10)

    def _cb(self, topic):
        def cb(msg):
            self.last[topic] = json.loads(msg.data)
            self.count[topic] += 1
        return cb


class FakeVehicle:
    """Publishes the smarc/* vehicle topics at 20 Hz until stopped."""

    def __init__(self, node):
        self.depth = DEPTH
        self.ground_alt = GROUND_ALT
        self._latlon = node.create_publisher(GeoPoint, Topics.POS_LATLON_TOPIC, 10)
        self._depth = node.create_publisher(Float32, Topics.DEPTH_TOPIC, 10)
        self._altitude = node.create_publisher(Float32, Topics.ALTITUDE_TOPIC, 10)
        self._odom = node.create_publisher(Odometry, Topics.ODOM_TOPIC, 10)
        self._timer = node.create_timer(0.05, self._tick)

    def _tick(self):
        self._latlon.publish(GeoPoint(latitude=LAT, longitude=LON, altitude=WATER_ALT))
        self._depth.publish(Float32(data=self.depth))
        self._altitude.publish(Float32(data=self.ground_alt))
        odom = Odometry()
        w, x, y, z = euler2quat(ROLL, PITCH, 0.0)
        odom.pose.pose.orientation.w = w
        odom.pose.pose.orientation.x = x
        odom.pose.pose.orientation.y = y
        odom.pose.pose.orientation.z = z
        self._odom.publish(odom)

    def stop(self):
        self._timer.cancel()


@pytest.fixture
def vehicle(ros_graph):
    node = ros_graph('waraps_vehicle', ROOT, parameter_overrides=[
        Parameter('robot_name', value='sam0'),
        Parameter('agent_type', value='underwater'),
        Parameter('agent_uuid', value='test-uuid'),
        Parameter('pulse_rate', value=10.0),
        Parameter('stale_after_s', value=0.5),
    ])
    WarapsVehicle(node)
    return node


def test_robot_name_is_required(ros_graph):
    with pytest.raises(ValueError, match='robot_name'):
        WarapsVehicle(ros_graph('waraps_vehicle', ROOT))


def test_heartbeat_sensors_and_sensor_info(ros_graph, vehicle):
    FakeVehicle(ros_graph('fake_vehicle', ROOT))
    stick = ros_graph('stick', ROOT)
    stick.create_publisher(String, f'{PREFIX}/acoustic', 10)
    heard = Listener(ros_graph('listener', ROOT), [
        Topics.WARA_PS_HEARTBEAT_TOPIC, Topics.WARA_PS_SENSOR_INFO_TOPIC,
        Topics.WARA_PS_SENSOR_POSITION_TOPIC, Topics.WARA_PS_SENSOR_DEPTH_TOPIC,
        Topics.WARA_PS_SENSOR_ALTITUDE_TOPIC,
        Topics.WARA_PS_SENSOR_ROLL_TOPIC, Topics.WARA_PS_SENSOR_PITCH_TOPIC,
        Topics.WARA_PS_SENSOR_HEADING_TOPIC,
    ])

    hb = wait_for(lambda: heard.last.get(Topics.WARA_PS_HEARTBEAT_TOPIC))
    assert hb['type'] == 'HeartBeat'
    assert hb['name'] == 'sam0'
    assert hb['agent-type'] == 'underwater'
    assert hb['agent-uuid'] == 'test-uuid'
    assert hb['rate'] == 10.0
    assert hb['levels'] == ['sensor']

    position = wait_for(lambda: heard.last.get(Topics.WARA_PS_SENSOR_POSITION_TOPIC))
    assert position == {'latitude': LAT, 'longitude': LON, 'altitude': WATER_ALT, 'type': 'GeoPoint'}

    assert wait_for(lambda: heard.last.get(Topics.WARA_PS_SENSOR_DEPTH_TOPIC)) == DEPTH
    assert wait_for(lambda: heard.last.get(Topics.WARA_PS_SENSOR_ALTITUDE_TOPIC)) == pytest.approx(GROUND_ALT)
    assert wait_for(lambda: heard.last.get(Topics.WARA_PS_SENSOR_ROLL_TOPIC)) == pytest.approx(ROLL)
    assert wait_for(lambda: heard.last.get(Topics.WARA_PS_SENSOR_PITCH_TOPIC)) == pytest.approx(PITCH)

    # sensor_info is what is really on the graph: ours, the stick's, not heading (never published).
    expected = ['acoustic', 'altitude', 'depth', 'pitch', 'position', 'roll']
    info = wait_for(lambda: (heard.last.get(Topics.WARA_PS_SENSOR_INFO_TOPIC) or {}).get('sensor-data-provided') == expected
                    and heard.last[Topics.WARA_PS_SENSOR_INFO_TOPIC])
    assert info['sensor-data-provided'] == expected
    assert info['name'] == 'sam0'
    assert heard.count[Topics.WARA_PS_SENSOR_HEADING_TOPIC] == 0


def test_levels_follow_the_graph(ros_graph, vehicle):
    heard = Listener(ros_graph('listener', ROOT), [Topics.WARA_PS_HEARTBEAT_TOPIC])
    assert wait_for(lambda: heard.last.get(Topics.WARA_PS_HEARTBEAT_TOPIC))['levels'] == ['sensor']

    officer = ros_graph('officer', ROOT)
    officer.create_publisher(String, Topics.WARA_PS_DIRECT_EXECUTION_INFO_TOPIC, 10)
    assert wait_for(lambda: heard.last[Topics.WARA_PS_HEARTBEAT_TOPIC]['levels'] == ['sensor', 'direct_execution'])

    officer.create_publisher(String, Topics.WARA_PS_TST_EXEC_INFO_TOPIC, 10)
    assert wait_for(lambda: heard.last[Topics.WARA_PS_HEARTBEAT_TOPIC]['levels'] == ['sensor', 'direct_execution', 'tst_execution'])

    # An officer in another robot's namespace does not count.
    other = ros_graph('officer', '/sam1')
    other.create_publisher(String, Topics.WARA_PS_TST_EXEC_INFO_TOPIC, 10)
    officer.destroy_node()
    assert wait_for(lambda: heard.last[Topics.WARA_PS_HEARTBEAT_TOPIC]['levels'] == ['sensor'])


def test_nan_and_stale_readings_are_not_published(ros_graph, vehicle):
    sensors = FakeVehicle(ros_graph('fake_vehicle', ROOT))
    heard = Listener(ros_graph('listener', ROOT), [
        Topics.WARA_PS_HEARTBEAT_TOPIC, Topics.WARA_PS_SENSOR_POSITION_TOPIC,
        Topics.WARA_PS_SENSOR_DEPTH_TOPIC, Topics.WARA_PS_SENSOR_ALTITUDE_TOPIC])
    assert wait_for(lambda: heard.last.get(Topics.WARA_PS_SENSOR_DEPTH_TOPIC)) == DEPTH
    assert wait_for(lambda: heard.last.get(Topics.WARA_PS_SENSOR_POSITION_TOPIC))['altitude'] == WATER_ALT

    sensors.depth = math.nan
    sensors.ground_alt = math.nan
    time.sleep(0.3)                                   # let the NaN replace the good reading
    depth_count = heard.count[Topics.WARA_PS_SENSOR_DEPTH_TOPIC]
    alt_count = heard.count[Topics.WARA_PS_SENSOR_ALTITUDE_TOPIC]
    position_before = heard.count[Topics.WARA_PS_SENSOR_POSITION_TOPIC]
    time.sleep(0.5)
    assert heard.count[Topics.WARA_PS_SENSOR_DEPTH_TOPIC] == depth_count
    assert heard.count[Topics.WARA_PS_SENSOR_ALTITUDE_TOPIC] == alt_count
    assert heard.count[Topics.WARA_PS_SENSOR_POSITION_TOPIC] > position_before   # water-level altitude still fine
    assert heard.last[Topics.WARA_PS_SENSOR_POSITION_TOPIC]['altitude'] == WATER_ALT

    sensors.stop()
    time.sleep(0.8)                                   # stale_after_s is 0.5
    position_count = heard.count[Topics.WARA_PS_SENSOR_POSITION_TOPIC]
    hb_count = heard.count[Topics.WARA_PS_HEARTBEAT_TOPIC]
    time.sleep(0.5)
    assert heard.count[Topics.WARA_PS_SENSOR_POSITION_TOPIC] == position_count
    assert heard.count[Topics.WARA_PS_HEARTBEAT_TOPIC] > hb_count                 # heartbeat never stops
