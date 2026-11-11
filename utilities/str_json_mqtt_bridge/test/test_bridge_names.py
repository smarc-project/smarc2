"""The name mapping between broker and ROS. No ROS graph needed."""

import pytest
from smarc_msgs.msg import Topics

from str_json_mqtt_bridge.names import mirror_target, mqtt_sensor_folder, unit_and_agent

PREFIX = Topics.WARA_PS_SENSOR_PREFIX
NAMESPACE = 'waraps/unit/subsurface/simulation/ozer_sam0'
UNIT, OWN = unit_and_agent(NAMESPACE)


def test_sensor_folder_is_the_last_segment_of_the_prefix():
    assert mqtt_sensor_folder(PREFIX) == 'sensor'
    assert mqtt_sensor_folder('/waraps/sensor/') == 'sensor'
    assert mqtt_sensor_folder('sensor') == 'sensor'


def test_unit_and_agent_split_the_mqtt_namespace():
    assert (UNIT, OWN) == ('waraps/unit/subsurface/simulation', 'ozer_sam0')
    assert unit_and_agent('/' + NAMESPACE + '/') == (UNIT, OWN)


@pytest.mark.parametrize('mqtt_topic, ros_topic', [
    (f'{UNIT}/kkalem_sam/sensor/position', f'/kkalem_sam/{Topics.WARA_PS_SENSOR_POSITION_TOPIC}'),
    (f'{UNIT}/stick_2/sensor/acoustic/stick_1', f'/stick_2/{PREFIX}/acoustic/stick_1'),   # slashes in the name
    (f'{UNIT}/{OWN}/sensor/position', None),                                            # our own agent
    (f'{UNIT}/kkalem_sam/heartbeat', None),                                             # not a sensor
    (f'{UNIT}/kkalem_sam/sensor', None),                                                # no name
    (f'{UNIT}/kkalem_sam/sensor/', None),                                               # empty name
    ('waraps/unit/air/simulation/drone/sensor/position', None),                         # other unit
    (f'{UNIT}/kkalem_sam/other/sensor/position', None),                                 # folder not right after the agent
])
def test_mirror_target(mqtt_topic, ros_topic):
    assert mirror_target(mqtt_topic, UNIT, OWN, PREFIX) == ros_topic
