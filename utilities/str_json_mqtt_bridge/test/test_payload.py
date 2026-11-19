"""What the bridge puts on the broker for a given ROS String."""

import pytest

from str_json_mqtt_bridge.payload import to_json_payload


@pytest.mark.parametrize('ros_string, mqtt_payload', [
    # JSON in, JSON out. This is the contract.
    ('1.5', '1.5'),
    ('-3', '-3'),
    ('{"a": 1}', '{"a": 1}'),
    ('{"ok": true}', '{"ok": true}'),                     # dropped before this change
    ('{"x": null}', '{"x": null}'),                       # dropped before this change
    ('[1, 2.5, "s"]', '[1, 2.5, "s"]'),
    ('{"latitude": 58.8, "longitude": 17.6, "type": "GeoPoint"}',
     '{"latitude": 58.8, "longitude": 17.6, "type": "GeoPoint"}'),
    ('"ok"', '"ok"'),                                     # a JSON string is JSON too
    # Older habits, still accepted, same output as before.
    ("{'x': None, 'ok': True}", '{"x": null, "ok": true}'),   # str(dict)
    ('\'{"a": 1}\'', '{"a": 1}'),                             # JSON wrapped in single quotes
    ('"{"a": 1}"', '{"a": 1}'),                               # or double quotes
    # Not JSON.
    ('hello', None),
    ('', None),
    ('{"a": 1', None),
])
def test_to_json_payload(ros_string, mqtt_payload):
    assert to_json_payload(ros_string) == mqtt_payload
