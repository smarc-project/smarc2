"""Officer.step against a fake client, one row of the status table at a time."""

import json
from types import SimpleNamespace

from smarc_action_base.smarc_action_base import ActionClientState
from smarc_msgs.msg import Topics

from waraps_officer.officer import Officer
from waraps_officer.tasks import WaraPSTaskStates

ROS = '/sam0/move_to'
NAME = 'move-to'


class FakeClient:
    def __init__(self):
        self.state = ActionClientState.READY
        self.feedback = ''
        self.timed_out = False
        self.sent = []
        self.cancels = 0

    def poll(self):
        return SimpleNamespace(state=self.state, feedback=self.feedback, timed_out=self.timed_out)

    def send(self, goal_json, timeout_s):
        self.sent.append((goal_json, timeout_s))
        self.state = ActionClientState.SENT
        return True

    def cancel(self):
        self.cancels += 1

    def get_ready(self):
        self.state = ActionClientState.READY

    def server_alive(self, timeout_s=0.0):
        self.state = ActionClientState.READY
        return True


def officer_with(state=ActionClientState.READY):
    client = FakeClient()
    client.state = state
    officer = Officer(lambda ros_name: client, 'sam0', 1.0, 10.0, 10.0)
    officer.on_health(Topics.VEHICLE_HEALTH_READY, 0.0)
    officer.on_action_heartbeat(ROS, 0.0)
    return officer, client


def start(officer, now=1.0, task_uuid='t1'):
    text = json.dumps({'command': 'start-task', 'com-uuid': 'c', 'task-uuid': task_uuid,
                        'task': {'name': NAME, 'params': {'rpm': 300, 'timeout': 8}}})
    return officer.on_exec(text, now)


def test_started_and_ready_sends_the_goal_then_a_busy_client_rejects_the_next():
    officer, client = officer_with()
    out = start(officer)
    assert out[0][1].status == 'started'
    assert officer.executing[0].status == WaraPSTaskStates.STARTED

    officer.step(1.1)
    assert client.sent == [('{"rpm": 300, "timeout": 8}', 8.0)]
    assert officer.executing[0].status == WaraPSTaskStates.RUNNING

    refused = start(officer, task_uuid='t2')
    assert refused[0][1].response == 'task already executing on move-to'


def test_paused_cancels_and_stays_resumed_sends_again():
    officer, client = officer_with(ActionClientState.RUNNING)
    start(officer)
    officer.executing[0].status = WaraPSTaskStates.PAUSED
    officer.step(1.0)
    assert client.cancels == 1
    assert officer.executing[0].status == WaraPSTaskStates.PAUSED

    client.state = ActionClientState.CANCELLED
    officer.step(1.1)
    assert client.state is ActionClientState.READY

    officer.on_exec(json.dumps({'command': 'signal-task', 'com-uuid': 'c', 'task-uuid': 't1', 'signal': '$continue'}), 1.2)
    officer.step(1.3)
    assert len(client.sent) == 1
    assert officer.executing[0].status == WaraPSTaskStates.RUNNING


def test_abort_and_enough_cancel_and_leave_the_list():
    officer, client = officer_with(ActionClientState.RUNNING)
    start(officer)
    officer.on_exec(json.dumps({'command': 'signal-task', 'com-uuid': 'c', 'task-uuid': 't1', 'signal': '$abort'}), 1.0)
    officer.step(1.1)
    assert client.cancels == 1
    assert officer.executing == []

    officer.on_health(Topics.VEHICLE_HEALTH_READY, 2.0)
    start(officer, now=2.1)
    officer.executing[0].status = WaraPSTaskStates.RUNNING
    client.state = ActionClientState.RUNNING
    officer.on_exec(json.dumps({'command': 'signal-task', 'com-uuid': 'c', 'task-uuid': 't1', 'signal': '$enough'}), 2.2)
    officer.step(2.3)
    assert officer.executing == []


def test_done_finishes_and_error_reports_the_client_state():
    officer, client = officer_with(ActionClientState.DONE)
    client.feedback = 'there'
    start(officer)
    officer.executing[0].status = WaraPSTaskStates.RUNNING
    out = officer.step(1.0)
    assert officer.executing == []
    assert out[0][1].status == 'finished'
    assert out[0][1].feedback == 'there'

    client.state = ActionClientState.ERROR
    client.feedback = ''
    start(officer, now=2.0)
    officer.on_health(Topics.VEHICLE_HEALTH_READY, 2.0)
    officer.executing[0].status = WaraPSTaskStates.RUNNING
    out = officer.step(2.1)
    assert out[0][1].status == 'error'
    assert 'ERROR' in out[0][1].feedback


def test_timeout_is_an_error():
    officer, client = officer_with(ActionClientState.RUNNING)
    client.timed_out = True
    start(officer)
    officer.executing[0].status = WaraPSTaskStates.RUNNING
    out = officer.step(1.0)
    assert out[0][1].status == 'error'
    assert officer.executing == []


def test_seq_starts_the_next_leaf_when_the_current_one_finishes():
    officer, client = officer_with()
    text = json.dumps({'command': 'start-tst', 'com-uuid': 'c', 'tst': {
        'name': 'seq', 'tst-uuid': 'm', 'children': [
            {'name': NAME, 'task-uuid': 'a', 'params': {'n': 1}},
            {'name': NAME, 'task-uuid': 'b', 'params': {'n': 2}},
        ]}})
    out = officer.on_tst(text, 1.0)
    assert out[0][1].response == 'accepted'
    assert officer.executing[0].uuid == 'a'

    officer.step(1.1)                              # send the first goal
    client.state = ActionClientState.DONE
    officer.step(1.2)
    assert [task.uuid for task in officer.executing] == ['b']
    assert officer.executing[0].status == WaraPSTaskStates.STARTED


def test_health_not_ready_rejects_a_start_and_cancels_what_is_running():
    officer, client = officer_with(ActionClientState.RUNNING)
    refused = start(officer, now=100.0)            # the ready sample at 0.0 is stale
    assert refused[0][1].response == 'rejected: vehicle health status is not ok'

    officer.on_health(Topics.VEHICLE_HEALTH_READY, 0.0)
    start(officer, now=1.0)
    officer.executing[0].status = WaraPSTaskStates.RUNNING
    officer.on_health(Topics.VEHICLE_HEALTH_ERROR, 2.0)
    out = officer.step(2.1)
    assert officer.executing == []
    assert out[0][1].feedback == 'cancelled: vehicle health ERROR'
    assert client.cancels == 1
    assert all(kind != 'abort' for kind, _ in out)


def test_signal_unit_on_exec_replies_there_and_aborts():
    officer, _ = officer_with(ActionClientState.RUNNING)
    start(officer)
    out = officer.on_exec(json.dumps({'command': 'signal-unit', 'com-uuid': 'c', 'signal': '$abort'}), 1.0)
    assert officer.executing == []
    assert out[0][0] == 'exec_response'
    assert out[0][1].response == 'ok'
    assert ('abort', None) in out


def test_unit_abort_cancels_and_publishes_the_smarc_abort():
    officer, client = officer_with(ActionClientState.RUNNING)
    start(officer)
    out = officer.on_waraps_abort(1.0)
    assert officer.executing == []
    assert ('abort', None) in out


def test_a_task_that_stops_heartbeating_is_forgotten():
    officer, _ = officer_with()
    officer.pulse(20.0)
    assert officer.available == {}


def test_unknown_task_is_rejected():
    officer, _ = officer_with()
    text = json.dumps({'command': 'start-task', 'com-uuid': 'c', 'task-uuid': 't', 'task': {'name': 'nope', 'params': {}}})
    out = officer.on_exec(text, 1.0)
    assert out[0][1].response == 'task not available'
