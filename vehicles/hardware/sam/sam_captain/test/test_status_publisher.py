from types import SimpleNamespace
from unittest.mock import MagicMock

from sam_captain.SAMStatusPublisher import SAMStatusPublisher
from sensor_msgs.msg import BatteryState
from smarc_msgs.msg import GeofenceStatusStamped
from std_msgs.msg import Float32


class FakeTime:
    def __init__(self, elapsed_nanoseconds):
        self._elapsed_nanoseconds = elapsed_nanoseconds

    def __sub__(self, _):
        return SimpleNamespace(nanoseconds=self._elapsed_nanoseconds)


def make_status_publisher():
    """Create a status publisher without starting ROS interfaces or TF."""
    publisher = SAMStatusPublisher.__new__(SAMStatusPublisher)
    publisher._node = MagicMock()
    publisher.battery_percent_pub = MagicMock()
    publisher._battery_percent = None
    publisher._last_battery_time = None
    publisher._geofence_status = None
    publisher._last_geofence_status_time = None
    publisher._max_geofence_status_age = 5.0
    return publisher


def test_battery_callback_publishes_the_received_percentage_and_records_time():
    publisher = make_status_publisher()
    received_at = object()
    publisher._node.get_clock().now.return_value = received_at

    publisher._battery_callback(BatteryState(percentage=0.73))

    published = publisher.battery_percent_pub.publish.call_args.args[0]
    assert isinstance(published, Float32)
    assert published.data == 0.73
    assert publisher.battery_percent == 0.73
    assert publisher._last_battery_time is received_at


def test_battery_callback_skips_unavailable_or_non_finite_percentage():
    publisher = make_status_publisher()

    unavailable_battery = BatteryState()
    unavailable_battery.percentage = None
    publisher._battery_callback(unavailable_battery)
    publisher._battery_callback(BatteryState(percentage=float('nan')))

    publisher.battery_percent_pub.publish.assert_not_called()
    assert publisher._node.get_logger().warn.call_count == 2


def test_battery_freshness_uses_the_configured_maximum_age():
    publisher = make_status_publisher()
    publisher._last_battery_time = object()
    publisher._node.get_clock().now.return_value = FakeTime(5_000_000_000)

    assert publisher.battery_is_fresh(5.0)
    assert not publisher.battery_is_fresh(4.9)


def test_status_string_converts_battery_fraction_to_percent():
    publisher = make_status_publisher()
    publisher._battery_percent = 0.73

    assert publisher.status_str() == 'Status:\n  Battery Percent: 73.0%\n'


def test_geofence_callback_caches_status_and_receipt_time():
    publisher = make_status_publisher()
    geofence = GeofenceStatusStamped()
    received_at = object()
    publisher._node.get_clock().now.return_value = received_at

    publisher._geofence_status_callback(geofence)

    assert publisher._geofence_status is geofence
    assert publisher._last_geofence_status_time is received_at


def test_geofence_freshness_expires_using_local_receipt_time():
    publisher = make_status_publisher()
    publisher._last_geofence_status_time = object()
    publisher._node.get_clock().now.return_value = FakeTime(5_000_000_000)
    assert publisher.geofence_is_fresh()

    publisher._node.get_clock().now.return_value = FakeTime(5_000_000_001)
    assert not publisher.geofence_is_fresh()


def test_geofence_is_outside_requires_a_fresh_outside_status():
    publisher = make_status_publisher()
    publisher._last_geofence_status_time = object()
    publisher._node.get_clock().now.return_value = FakeTime(0)
    publisher._geofence_status = GeofenceStatusStamped(
        status=GeofenceStatusStamped.STATUS_OUTSIDE
    )
    assert publisher.geofence_is_outside()

    publisher._geofence_status.status = GeofenceStatusStamped.STATUS_INSIDE
    assert not publisher.geofence_is_outside()

    publisher._geofence_status.status = GeofenceStatusStamped.STATUS_OUTSIDE
    publisher._node.get_clock().now.return_value = FakeTime(5_000_000_001)
    assert not publisher.geofence_is_outside()
