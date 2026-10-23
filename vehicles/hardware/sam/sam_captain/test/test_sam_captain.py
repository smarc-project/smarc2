from unittest.mock import MagicMock

from sam_captain.sam_captain import SAMCaptain
from smarc_msgs.msg import Topics as SmarcTopics
from std_msgs.msg import Int8


def make_captain():
    """Create a captain with its status publisher replaced by a mock."""
    captain = SAMCaptain.__new__(SAMCaptain)
    captain._status_publisher = MagicMock()
    captain._status_publisher.battery_percent = 0.8
    captain._status_publisher.battery_is_fresh.return_value = True
    captain._status_publisher.global_navigation_is_fresh.return_value = True
    captain._status_publisher.geofence_is_outside.return_value = False
    captain._max_battery_age = 10.0
    captain._max_nav_age = 10.0
    captain._battery_threshold = 0.3
    captain._vehicle_health = Int8(data=SmarcTopics.VEHICLE_HEALTH_WAITING)
    captain._vehicle_health_reason = 'Initial state'
    captain._vehicle_health_pub = MagicMock()
    captain.nav_str_pub = MagicMock()
    captain.get_logger = MagicMock(return_value=MagicMock())
    return captain


def test_health_is_ready_when_every_required_input_is_healthy():
    captain = make_captain()

    health, reason = captain._evaluate_vehicle_health()

    assert health == SmarcTopics.VEHICLE_HEALTH_READY
    assert reason == (
        '=========== All checks passed ===========\n'
        '=========== Vehicle health ready ==========='
    )
    captain._status_publisher.battery_is_fresh.assert_called_once_with(10.0)
    captain._status_publisher.global_navigation_is_fresh.assert_called_once_with(10.0)
    captain._status_publisher.geofence_is_outside.assert_called_once_with()


def test_health_waits_for_missing_or_stale_battery_data():
    captain = make_captain()
    captain._status_publisher.battery_percent = None

    assert captain._evaluate_vehicle_health() == (
        SmarcTopics.VEHICLE_HEALTH_WAITING,
        '>>>>>>>> Battery not fresh or None <<<<<<<<',
    )

    captain._status_publisher.battery_percent = 0.8
    captain._status_publisher.battery_is_fresh.return_value = False
    assert captain._evaluate_vehicle_health() == (
        SmarcTopics.VEHICLE_HEALTH_WAITING,
        '>>>>>>>> Battery not fresh or None <<<<<<<<',
    )


def test_low_battery_is_an_error_after_a_fresh_reading():
    captain = make_captain()
    captain._status_publisher.battery_percent = 0.29

    assert captain._evaluate_vehicle_health() == (
        SmarcTopics.VEHICLE_HEALTH_ERROR,
        '>>>>>>>> Battery below threshold <<<<<<<<',
    )


def test_health_waits_for_stale_global_navigation():
    captain = make_captain()
    captain._status_publisher.global_navigation_is_fresh.return_value = False

    assert captain._evaluate_vehicle_health() == (
        SmarcTopics.VEHICLE_HEALTH_WAITING,
        '>>>>>>>> Nav publisher not fresh <<<<<<<<',
    )


def test_health_reports_a_fresh_outside_geofence():
    captain = make_captain()
    captain._status_publisher.geofence_is_outside.return_value = True

    assert captain._evaluate_vehicle_health() == (
        SmarcTopics.VEHICLE_HEALTH_READY,
        '>>>>>>>> Geofence outside <<<<<<<<<<',
    )


def test_publish_vehicle_health_updates_the_cached_state_and_publishes_it():
    captain = make_captain()
    captain._evaluate_vehicle_health = MagicMock(
        return_value=(SmarcTopics.VEHICLE_HEALTH_READY, 'all inputs healthy')
    )

    captain._pub_vehicle_health()

    assert captain._vehicle_health.data == SmarcTopics.VEHICLE_HEALTH_READY
    assert captain._vehicle_health_reason == 'all inputs healthy'
    captain._vehicle_health_pub.publish.assert_called_once_with(
        captain._vehicle_health
    )


def test_health_str_handles_known_and_unknown_states():
    captain = make_captain()

    assert captain._health_str(SmarcTopics.VEHICLE_HEALTH_READY) == 'READY'
    assert captain._health_str(SmarcTopics.VEHICLE_HEALTH_WAITING) == 'WAITING'
    assert captain._health_str(SmarcTopics.VEHICLE_HEALTH_ERROR) == 'ERROR'
    assert captain._health_str(99) == 'UNKNOWN(99)'


def test_status_callback_combines_navigation_and_system_status():
    captain = make_captain()
    captain._status_publisher.nav_status_str.return_value = 'Navigation status'
    captain._status_publisher.status_str.return_value = 'System status'

    captain._status_str_callback()

    status_message = captain.nav_str_pub.publish.call_args.args[0]
    assert status_message.data == 'Navigation status\nSystem status'


def test_captain_creates_and_wires_all_status_interfaces():
    captain = SAMCaptain.__new__(SAMCaptain)
    captain._status_publisher = MagicMock()
    publishers = [MagicMock() for _ in range(8)]
    subscriptions = [MagicMock() for _ in range(5)]
    captain.create_publisher = MagicMock(side_effect=publishers)
    captain.create_subscription = MagicMock(side_effect=subscriptions)

    captain._create_status_publishers()
    captain._create_status_subscribers()

    assert captain.create_publisher.call_count == 8
    assert captain._status_publisher.battery_percent_pub is publishers[0]
    assert captain._status_publisher.altitude_pub is publishers[-1]
    assert captain.create_subscription.call_count == 5
    assert captain._battery_status_sub is subscriptions[0]
    assert captain._geofence_status_sub is subscriptions[-1]
