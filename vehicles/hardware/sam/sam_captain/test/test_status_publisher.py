from types import SimpleNamespace
from unittest.mock import Mock

from geographic_msgs.msg import GeoPoint
from nav_msgs.msg import Odometry
from sam_captain.SAMStatusPublisher import SAMStatusPublisher
from sam_msgs.msg import Topics as SamTopics
from smarc_msgs.msg import Topics as SmarcTopics
from std_msgs.msg import Float32, Int8, String


def make_captain_state():
    return SimpleNamespace(
        latest_battery_percent=None,
        latest_odom=None,
        latest_depth=None,
        latest_altitude=None,
        latest_latlon=None,
        latest_heading=None,
        latest_course=None,
        latest_speed=None,
        utm_frame=None,
        battery_is_fresh=Mock(return_value=True),
        global_navigation_is_fresh=Mock(return_value=True),
        geofence_is_outside=Mock(return_value=False),
        get_logger=Mock(return_value=Mock()),
    )


def make_status_publisher():
    """Create a status publisher without creating ROS interfaces."""
    publisher = SAMStatusPublisher.__new__(SAMStatusPublisher)
    publisher.cap = make_captain_state()
    publisher._max_battery_age = 10.0
    publisher._max_nav_age = 10.0
    publisher._battery_threshold = 0.3
    publisher._vehicle_health = Int8(data=SmarcTopics.VEHICLE_HEALTH_WAITING)
    publisher._vehicle_health_reason = 'Initial state'
    publisher._battery_percent_pub = Mock()
    publisher._odom_pub = Mock()
    publisher._depth_pub = Mock()
    publisher._latlon_pub = Mock()
    publisher._heading_pub = Mock()
    publisher._course_pub = Mock()
    publisher._speed_pub = Mock()
    publisher._altitude_pub = Mock()
    publisher._status_string_pub = Mock()
    publisher._vehicle_health_pub = Mock()
    return publisher


def test_status_publisher_registers_outputs_and_publish_timer():
    captain = Mock()
    publishers = [Mock() for _ in range(10)]
    captain.create_publisher.side_effect = publishers

    status = SAMStatusPublisher(captain)

    assert status._battery_percent_pub is publishers[7]
    assert status._status_string_pub is publishers[8]
    assert status._vehicle_health_pub is publishers[9]
    assert captain.create_publisher.call_args_list[8].args[:2] == (
        String,
        SamTopics.STATUS_STRING_TOPIC,
    )
    assert captain.create_publisher.call_args_list[9].args[:2] == (
        Int8,
        SmarcTopics.VEHICLE_HEALTH_TOPIC,
    )
    captain.create_timer.assert_called_once_with(10.0, status._publish_status)


def test_publish_status_reads_current_state_from_the_captain():
    publisher = make_status_publisher()
    publisher.cap.latest_battery_percent = 0.73
    publisher.cap.latest_odom = Odometry()
    publisher.cap.latest_depth = 2.5
    publisher.cap.latest_altitude = 4.0
    publisher.cap.latest_latlon = GeoPoint(latitude=58.0, longitude=11.0)
    publisher.cap.latest_heading = 15.0
    publisher.cap.latest_course = 20.0
    publisher.cap.latest_speed = 1.5

    publisher._publish_status()

    battery = publisher._battery_percent_pub.publish.call_args.args[0]
    depth = publisher._depth_pub.publish.call_args.args[0]
    summary = publisher._status_string_pub.publish.call_args.args[0]
    assert isinstance(battery, Float32)
    assert battery.data == 0.73
    assert isinstance(depth, Float32)
    assert depth.data == 2.5
    assert isinstance(summary, String)
    publisher._odom_pub.publish.assert_called_once_with(publisher.cap.latest_odom)
    publisher._latlon_pub.publish.assert_called_once_with(publisher.cap.latest_latlon)


def test_publish_status_skips_values_not_yet_received_by_the_captain():
    publisher = make_status_publisher()

    publisher._publish_status()

    for output in (
        publisher._battery_percent_pub,
        publisher._odom_pub,
        publisher._depth_pub,
        publisher._latlon_pub,
        publisher._heading_pub,
        publisher._course_pub,
        publisher._speed_pub,
        publisher._altitude_pub,
    ):
        output.publish.assert_not_called()
    publisher._status_string_pub.publish.assert_called_once_with(
        String(data=publisher.status_str())
    )


def test_status_string_reads_state_from_the_captain():
    publisher = make_status_publisher()
    publisher.cap.latest_battery_percent = 0.73
    publisher.cap.latest_depth = 3.0
    publisher.cap.utm_frame = 'utm32'
    publisher.cap.latest_latlon = GeoPoint(latitude=58.1234567, longitude=11.7654321)

    assert publisher.status_str() == (
        'Status:\n'
        '  Battery Percent: 73.0%\n'
        'Navigation:\n'
        '  UTM Frame: utm32\n'
        '  Position: 58.123457, 11.765432\n'
        '  Depth: 3.00 m\n'
        '  Altitude: N/A\n'
        '  Heading: N/A\n'
        '  Course: N/A\n'
        '  Speed: N/A\n'
    )


def test_vehicle_health_is_ready_when_every_required_input_is_healthy():
    publisher = make_status_publisher()
    publisher.cap.latest_battery_percent = 0.8

    health, reason = publisher._evaluate_vehicle_health()

    assert health == SmarcTopics.VEHICLE_HEALTH_READY
    assert reason == (
        '=========== All checks passed ===========\n'
        '=========== Vehicle health ready ==========='
    )
    publisher.cap.battery_is_fresh.assert_called_once_with(10.0)
    publisher.cap.global_navigation_is_fresh.assert_called_once_with(10.0)
    publisher.cap.geofence_is_outside.assert_called_once_with()


def test_vehicle_health_waits_for_missing_battery_or_navigation():
    publisher = make_status_publisher()

    assert publisher._evaluate_vehicle_health() == (
        SmarcTopics.VEHICLE_HEALTH_WAITING,
        '>>>>>>>> Battery not fresh or None <<<<<<<<',
    )

    publisher.cap.latest_battery_percent = 0.8
    publisher.cap.global_navigation_is_fresh.return_value = False
    assert publisher._evaluate_vehicle_health() == (
        SmarcTopics.VEHICLE_HEALTH_WAITING,
        '>>>>>>>> Nav publisher not fresh <<<<<<<<',
    )


def test_vehicle_health_reports_low_battery_and_outside_geofence():
    publisher = make_status_publisher()
    publisher.cap.latest_battery_percent = 0.29

    assert publisher._evaluate_vehicle_health() == (
        SmarcTopics.VEHICLE_HEALTH_ERROR,
        '>>>>>>>> Battery below threshold <<<<<<<<',
    )

    publisher.cap.latest_battery_percent = 0.8
    publisher.cap.geofence_is_outside.return_value = True
    assert publisher._evaluate_vehicle_health() == (
        SmarcTopics.VEHICLE_HEALTH_WAITING,
        '>>>>>>>> Geofence outside <<<<<<<<<<',
    )


def test_publish_vehicle_health_updates_cached_state_and_publishes_it():
    publisher = make_status_publisher()
    publisher._evaluate_vehicle_health = Mock(
        return_value=(SmarcTopics.VEHICLE_HEALTH_READY, 'all inputs healthy')
    )

    publisher._pub_vehicle_health()

    assert publisher._vehicle_health.data == SmarcTopics.VEHICLE_HEALTH_READY
    assert publisher._vehicle_health_reason == 'all inputs healthy'
    publisher._vehicle_health_pub.publish.assert_called_once_with(
        publisher._vehicle_health
    )


def test_health_str_handles_known_and_unknown_states():
    publisher = make_status_publisher()

    assert publisher._health_str(SmarcTopics.VEHICLE_HEALTH_READY) == 'READY'
    assert publisher._health_str(SmarcTopics.VEHICLE_HEALTH_WAITING) == 'WAITING'
    assert publisher._health_str(SmarcTopics.VEHICLE_HEALTH_ERROR) == 'ERROR'
    assert publisher._health_str(99) == 'UNKNOWN(99)'
