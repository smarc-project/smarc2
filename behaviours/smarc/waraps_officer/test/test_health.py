"""The vehicle health as the officer reads it, and the officer's own."""

from smarc_msgs.msg import Topics

from waraps_officer.health import health_is_ready, health_label, officer_health


class _Fix:
    def __init__(self, status, state, refused=False):
        self.status = status
        self.cancel_refused = refused
        self.client = type('Client', (), {'state': state})()


def test_officer_health_uses_the_vehicle_values():
    running = {'running', 'cancelling'}
    cancelling = 'cancelling'
    assert officer_health([_Fix('running', 'running')], running, cancelling) == Topics.VEHICLE_HEALTH_READY
    assert officer_health([_Fix('aborted', 'cancelling')], running, cancelling) == Topics.VEHICLE_HEALTH_WAITING
    assert officer_health([_Fix('paused', 'ready')], running, cancelling) == Topics.VEHICLE_HEALTH_READY
    refused = _Fix('running', 'running', refused=True)
    waiting = _Fix('aborted', 'cancelling')
    assert officer_health([waiting, refused], running, cancelling) == Topics.VEHICLE_HEALTH_ERROR


def test_vehicle_health_needs_ready_and_fresh():
    assert health_is_ready(Topics.VEHICLE_HEALTH_READY, 1.0, 5.0, 10.0)
    assert not health_is_ready(Topics.VEHICLE_HEALTH_READY, 1.0, 20.0, 10.0)
    assert not health_is_ready(Topics.VEHICLE_HEALTH_ERROR, 1.0, 2.0, 10.0)
    assert health_label(Topics.VEHICLE_HEALTH_WAITING, True) == 'WAITING'
    assert health_label(Topics.VEHICLE_HEALTH_READY, False) == 'silent'
    assert officer_health([], {'running'}, 'cancelling') == Topics.VEHICLE_HEALTH_READY
