from types import SimpleNamespace
from unittest.mock import Mock, patch

from rclpy.node import Node
from sam_captain.sam_captain import SAMCaptain
from sensor_msgs.msg import BatteryState
from smarc_msgs.msg import GeofenceStatusStamped
from std_msgs.msg import String


class FakeTime:
    def __init__(self, elapsed_nanoseconds):
        self._elapsed_nanoseconds = elapsed_nanoseconds

    def __sub__(self, _):
        return SimpleNamespace(nanoseconds=self._elapsed_nanoseconds)


def make_captain():
    """Create a captain without starting ROS interfaces."""
    captain = SAMCaptain.__new__(SAMCaptain)
    captain.latest_battery_percent = None
    captain.latest_latlon = None
    captain.latest_altitude = None
    captain.latest_geofence_status = None
    captain.utm_frame = None
    captain._previous_pose_utm = object()
    captain._current_pose_utm = object()
    captain.latest_heading = 12.0
    captain.latest_course = 34.0
    captain._last_battery_time = None
    captain._last_global_navigation_time = None
    captain._last_geofence_status_time = None
    captain.get_logger = Mock(return_value=Mock())
    captain.get_clock = Mock()
    return captain


def test_battery_callback_stores_percentage_and_receipt_time():
    captain = make_captain()
    received_at = object()
    captain.get_clock.return_value.now.return_value = received_at

    captain._battery_callback(BatteryState(percentage=0.73))

    assert captain.latest_battery_percent == 0.73
    assert captain._last_battery_time is received_at


def test_constructor_initializes_the_internal_state_used_by_callbacks():
    """Keep initialization aligned with the callback and freshness code."""
    logger = Mock()
    robot_parameter = SimpleNamespace(
        get_parameter_value=Mock(
            return_value=SimpleNamespace(string_value='sam')
        )
    )
    with (
        patch.object(Node, '__init__', return_value=None),
        patch.object(Node, 'get_logger', return_value=logger),
        patch.object(SAMCaptain, 'declare_parameter'),
        patch.object(SAMCaptain, 'get_parameter', return_value=robot_parameter),
        patch.object(SAMCaptain, '_create_tf_listener'),
        patch.object(SAMCaptain, '_create_status_subscribers'),
        patch('sam_captain.sam_captain.SAMStatusPublisher'),
    ):
        captain = SAMCaptain()

    assert captain._previous_pose_utm is None
    assert captain._current_pose_utm is None
    assert captain._last_battery_time is None
    assert captain._last_global_navigation_time is None
    assert captain._last_geofence_status_time is None


def test_battery_callback_rejects_an_unavailable_percentage():
    captain = make_captain()
    unavailable_battery = BatteryState()
    unavailable_battery.percentage = None

    captain._battery_callback(unavailable_battery)

    assert captain.latest_battery_percent is None
    captain.get_logger.return_value.warn.assert_called_once_with(
        'Battery percentage not available.'
    )


def test_battery_freshness_uses_captain_receipt_time_and_threshold():
    captain = make_captain()
    captain._last_battery_time = object()
    captain.get_clock.return_value.now.return_value = FakeTime(5_000_000_000)

    assert captain.battery_is_fresh(5.0)
    assert not captain.battery_is_fresh(4.9)


def test_global_navigation_requires_coordinates_and_a_fresh_receipt():
    captain = make_captain()
    captain._last_global_navigation_time = object()
    captain.get_clock.return_value.now.return_value = FakeTime(1_000_000_000)

    assert not captain.global_navigation_is_fresh(2.0)

    captain.latest_latlon = object()
    assert captain.global_navigation_is_fresh(2.0)


def test_geofence_outside_requires_a_fresh_outside_status():
    captain = make_captain()
    captain.geofence_is_fresh = Mock(return_value=True)
    captain.latest_geofence_status = GeofenceStatusStamped(
        status=GeofenceStatusStamped.STATUS_OUTSIDE
    )

    assert captain.geofence_is_outside()

    captain.latest_geofence_status.status = GeofenceStatusStamped.STATUS_INSIDE
    assert not captain.geofence_is_outside()

    captain.geofence_is_fresh.return_value = False
    captain.latest_geofence_status.status = GeofenceStatusStamped.STATUS_OUTSIDE
    assert not captain.geofence_is_outside()


def test_utm_callback_resets_navigation_state_for_a_new_frame():
    captain = make_captain()
    captain.utm_frame = 'utm32'
    captain.latest_latlon = object()
    captain._last_global_navigation_time = object()

    captain._utm_callback(String(data='utm33'))

    assert captain.utm_frame == 'utm33'
    assert captain._previous_pose_utm is None
    assert captain._current_pose_utm is None
    assert captain.latest_latlon is None
    assert captain.latest_heading is None
    assert captain.latest_course is None
    assert captain._last_global_navigation_time is None


def test_utm_callback_ignores_the_current_frame():
    captain = make_captain()
    captain.utm_frame = 'utm32'
    previous_pose = captain._previous_pose_utm

    captain._utm_callback(String(data='utm32'))

    assert captain._previous_pose_utm is previous_pose
    captain.get_logger.return_value.info.assert_not_called()


def test_dvl_callback_updates_altitude():
    captain = make_captain()

    captain._dvl_callback(SimpleNamespace(altitude=4.5))

    assert captain.latest_altitude == 4.5


def test_captain_creates_input_subscriptions_with_its_callbacks():
    captain = SAMCaptain.__new__(SAMCaptain)
    subscriptions = [Mock() for _ in range(5)]
    captain.create_subscription = Mock(side_effect=subscriptions)

    captain._create_status_subscribers()

    assert captain.create_subscription.call_count == 5
    assert captain._battery_status_sub is subscriptions[0]
    assert captain._geofence_status_sub is subscriptions[-1]
    callbacks = [call.args[2].__name__ for call in captain.create_subscription.call_args_list]
    assert callbacks == [
        '_battery_callback',
        '_odom_callback',
        '_utm_callback',
        '_dvl_callback',
        '_geofence_status_callback',
    ]
