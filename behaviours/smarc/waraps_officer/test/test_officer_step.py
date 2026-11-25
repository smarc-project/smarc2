"""WarapsOfficer.advance_tasks against a fake client, one row of the status table at a time."""

import json
from collections.abc import Callable
from types import SimpleNamespace

from smarc_action_base.smarc_action_base import ActionClientState
from smarc_msgs.msg import Topics

from waraps_officer.commands import ExecReply, StartReply
from waraps_officer.officer import WarapsOfficer
from waraps_officer.tasks import WaraPSTaskStates

ROS = '/sam0/move_to'
NAME = 'move-to'


class FakeClient:
    def __init__(self) -> None:
        self.state = ActionClientState.READY
        self.feedback = ''
        self.timed_out = False
        self.sent = []
        self.cancels = 0
        self.cancel_refused = False
        self.refuse_cancel = False
        self.error_on_cancel = False

    def poll(self) -> SimpleNamespace:
        return SimpleNamespace(
            state=self.state, feedback=self.feedback, timed_out=self.timed_out,
            cancel_refused=self.cancel_refused)

    def send(self, goal_json: str, timeout_s: float | None) -> bool:
        self.sent.append((goal_json, timeout_s))
        self.state = ActionClientState.SENT
        return True

    def cancel(self) -> None:
        if self.state is ActionClientState.CANCELLING:
            return
        self.cancel_refused = False
        self.cancels += 1
        if self.refuse_cancel:
            self.cancel_refused = True
            self.state = ActionClientState.RUNNING
            return
        if self.error_on_cancel:
            self.state = ActionClientState.ERROR
            return
        self.state = ActionClientState.CANCELLING

    def get_ready(self) -> None:
        self.state = ActionClientState.READY

    def server_alive(self, timeout_s: float = 0.0) -> bool:
        self.state = ActionClientState.READY
        return True


class Published:
    """What the officer published since the last clear(), one list per output topic."""

    def __init__(self) -> None:
        self.clear()

    def clear(self) -> None:
        self.aborts = 0
        self.health = []
        self.exec_response = []
        self.tst_response = []
        self.exec_feedback = []
        self.tst_feedback = []
        self.direct_execution_info = []
        self.tst_execution_info = []
        self.executing_tasks = []

    def count_abort(self) -> None:
        self.aborts += 1


def officer_for(client_factory: Callable[[str], FakeClient], published: Published) -> WarapsOfficer:
    return WarapsOfficer(
        client_factory=client_factory,
        name='sam0',
        rate_hz=1.0,
        liveliness_s=10.0,
        health_timeout_s=10.0,
        publish_abort=published.count_abort,
        publish_health=lambda level: published.health.append(level),
        publish_exec_response=lambda reply: published.exec_response.append(reply),
        publish_tst_response=lambda reply: published.tst_response.append(reply),
        publish_exec_feedback=lambda message: published.exec_feedback.append(message),
        publish_tst_feedback=lambda message: published.tst_feedback.append(message),
        publish_direct_execution_info=lambda info: published.direct_execution_info.append(info),
        publish_tst_execution_info=lambda info: published.tst_execution_info.append(info),
        publish_executing_tasks=lambda rows: published.executing_tasks.append(rows),
    )


def officer_with(state: ActionClientState = ActionClientState.READY) -> tuple[WarapsOfficer, FakeClient, Published]:
    client = FakeClient()
    client.state = state
    published = Published()
    officer = officer_for(lambda ros_name: client, published)
    officer.update_vehicle_health(Topics.VEHICLE_HEALTH_READY, 0.0)
    officer.track_action_server(ROS, 0.0)
    return officer, client, published


def officer_with_clients(ros_names: list[str]) -> tuple[WarapsOfficer, dict[str, FakeClient], Published]:
    clients = {ros_name: FakeClient() for ros_name in ros_names}
    published = Published()
    officer = officer_for(lambda ros_name: clients[ros_name], published)
    officer.update_vehicle_health(Topics.VEHICLE_HEALTH_READY, 0.0)
    for ros_name in ros_names:
        officer.track_action_server(ros_name, 0.0)
    return officer, clients, published


def start(
    officer: WarapsOfficer,
    published: Published,
    now: float = 1.0,
    task_uuid: str = 't1',
    name: str = NAME,
) -> StartReply | ExecReply:
    """Send a start-task; return the exec response it got."""
    text = json.dumps({'command': 'start-task', 'com-uuid': 'c', 'task-uuid': task_uuid,
                        'task': {'name': name, 'params': {'rpm': 300, 'timeout': 8}}})
    published.clear()
    officer.handle_exec_command(text, now)
    return published.exec_response[-1]


def test_started_and_ready_sends_the_goal_then_a_busy_client_rejects_the_next() -> None:
    officer, client, published = officer_with()
    started = start(officer, published)
    assert started.status == 'started'
    assert officer.executing[0].status == WaraPSTaskStates.STARTED

    officer.advance_tasks(1.1)
    assert client.sent == [('{"rpm": 300, "timeout": 8}', 8.0)]
    assert officer.executing[0].status == WaraPSTaskStates.RUNNING

    refused = start(officer, published, task_uuid='t2')
    assert refused.response == 'task already executing on move-to'


def test_paused_cancels_and_stays_resumed_sends_again() -> None:
    officer, client, published = officer_with(ActionClientState.RUNNING)
    start(officer, published)
    officer.executing[0].status = WaraPSTaskStates.PAUSED
    officer.advance_tasks(1.0)
    assert client.cancels == 1
    assert officer.executing[0].status == WaraPSTaskStates.PAUSED

    client.state = ActionClientState.CANCELLED
    officer.advance_tasks(1.1)
    assert client.state is ActionClientState.READY

    officer.handle_exec_command(json.dumps({'command': 'signal-task', 'com-uuid': 'c', 'task-uuid': 't1', 'signal': '$continue'}), 1.2)
    officer.advance_tasks(1.3)
    assert len(client.sent) == 1
    assert officer.executing[0].status == WaraPSTaskStates.RUNNING


def test_abort_waits_until_the_server_accepts_and_blocks_a_new_start() -> None:
    officer, client, published = officer_with(ActionClientState.RUNNING)
    start(officer, published)
    officer.handle_exec_command(json.dumps({'command': 'signal-task', 'com-uuid': 'c', 'task-uuid': 't1', 'signal': '$abort'}), 1.0)
    officer.advance_tasks(1.1)
    assert client.cancels == 1
    assert client.state is ActionClientState.CANCELLING
    assert [task.uuid for task in officer.executing] == ['t1']
    refused = start(officer, published, now=1.2, task_uuid='t2')
    assert refused.response == 'task already executing on move-to'

    client.state = ActionClientState.CANCELLED
    published.clear()
    officer.advance_tasks(1.3)
    assert officer.executing == []
    assert published.exec_feedback[0].feedback == 'cancelled'
    assert published.exec_feedback[0].status == 'aborted'

    officer.update_vehicle_health(Topics.VEHICLE_HEALTH_READY, 2.0)
    start(officer, published, now=2.1)
    officer.executing[0].status = WaraPSTaskStates.RUNNING
    client.state = ActionClientState.RUNNING
    officer.handle_exec_command(json.dumps({'command': 'signal-task', 'com-uuid': 'c', 'task-uuid': 't1', 'signal': '$enough'}), 2.2)
    officer.advance_tasks(2.3)
    assert officer.executing
    client.state = ActionClientState.CANCELLED
    officer.advance_tasks(2.4)
    assert officer.executing == []


def test_officer_health_is_waiting_then_error_then_ready() -> None:
    officer, client, published = officer_with(ActionClientState.RUNNING)
    start(officer, published)
    assert officer.health() == Topics.VEHICLE_HEALTH_READY

    officer.handle_exec_command(json.dumps({'command': 'signal-task', 'com-uuid': 'c', 'task-uuid': 't1', 'signal': '$abort'}), 1.0)
    published.clear()
    officer.advance_tasks(1.1)
    assert officer.health() == Topics.VEHICLE_HEALTH_WAITING
    assert published.health[-1] == Topics.VEHICLE_HEALTH_WAITING
    assert published.aborts == 0

    client.refuse_cancel = True
    client.state = ActionClientState.RUNNING
    officer.handle_exec_command(json.dumps({'command': 'signal-task', 'com-uuid': 'c', 'task-uuid': 't1', 'signal': '$abort'}), 1.2)
    officer.advance_tasks(1.3)
    assert officer.health() == Topics.VEHICLE_HEALTH_ERROR

    client.refuse_cancel = False
    client.state = ActionClientState.CANCELLED
    officer.advance_tasks(1.4)
    assert officer.executing == []
    assert officer.health() == Topics.VEHICLE_HEALTH_READY


def test_a_refused_cancel_stays_running_and_is_reported() -> None:
    officer, client, published = officer_with(ActionClientState.RUNNING)
    start(officer, published)
    client.refuse_cancel = True
    officer.handle_exec_command(json.dumps({'command': 'signal-task', 'com-uuid': 'c', 'task-uuid': 't1', 'signal': '$abort'}), 1.0)
    published.clear()
    officer.advance_tasks(1.1)
    assert client.cancels == 1
    assert officer.executing[0].status == WaraPSTaskStates.RUNNING
    assert published.exec_feedback[0].feedback == 'cancel refused: action still running'
    assert published.aborts == 0
    refused = start(officer, published, now=1.2, task_uuid='t2')
    assert refused.response == 'task already executing on move-to'
    officer.advance_tasks(1.3)
    assert client.cancels == 1


def test_a_refused_pause_is_reported_once() -> None:
    officer, client, published = officer_with(ActionClientState.RUNNING)
    start(officer, published)
    client.refuse_cancel = True
    officer.executing[0].status = WaraPSTaskStates.PAUSED
    officer.advance_tasks(1.0)
    assert client.cancels == 1
    published.clear()
    officer.advance_tasks(1.1)
    assert published.exec_feedback[0].feedback == 'cancel refused: action still running'
    assert officer.executing[0].status == WaraPSTaskStates.PAUSED
    officer.advance_tasks(1.2)
    assert client.cancels == 1


def test_health_reports_a_refusal_instead_of_asking_again() -> None:
    officer, client, published = officer_with(ActionClientState.RUNNING)
    start(officer, published)
    officer.executing[0].status = WaraPSTaskStates.RUNNING
    officer.update_vehicle_health(Topics.VEHICLE_HEALTH_ERROR, 1.0)
    officer.advance_tasks(1.1)
    assert client.cancels == 1
    client.state = ActionClientState.RUNNING
    client.cancel_refused = True
    published.clear()
    officer.advance_tasks(1.2)
    assert client.cancels == 1
    assert published.exec_feedback[0].feedback == 'cancel refused: action still running'
    assert officer.executing[0].status == WaraPSTaskStates.RUNNING


def test_health_asks_once_after_a_different_stop_was_refused() -> None:
    officer, client, published = officer_with(ActionClientState.RUNNING)
    start(officer, published)
    client.refuse_cancel = True
    officer.handle_exec_command(json.dumps({'command': 'signal-task', 'com-uuid': 'c', 'task-uuid': 't1', 'signal': '$abort'}), 1.0)
    officer.advance_tasks(1.1)
    assert officer.executing[0].status == WaraPSTaskStates.RUNNING
    assert client.cancels == 1
    client.refuse_cancel = False
    officer.update_vehicle_health(Topics.VEHICLE_HEALTH_ERROR, 2.0)
    officer.advance_tasks(2.1)
    assert client.cancels == 2
    assert client.state is ActionClientState.CANCELLING


def test_a_refused_pause_that_finishes_leaves_the_list() -> None:
    officer, client, published = officer_with(ActionClientState.RUNNING)
    start(officer, published)
    client.refuse_cancel = True
    officer.executing[0].status = WaraPSTaskStates.PAUSED
    officer.advance_tasks(1.0)
    officer.advance_tasks(1.1)
    assert officer.executing[0].status == WaraPSTaskStates.PAUSED
    client.state = ActionClientState.DONE
    client.feedback = 'there'
    published.clear()
    officer.advance_tasks(1.2)
    assert officer.executing == []
    assert published.exec_feedback[0].status == 'finished'
    assert published.exec_feedback[0].feedback == 'there'


def test_continue_after_a_refused_pause_keeps_the_running_goal() -> None:
    officer, client, published = officer_with(ActionClientState.RUNNING)
    start(officer, published)
    client.refuse_cancel = True
    officer.executing[0].status = WaraPSTaskStates.PAUSED
    officer.advance_tasks(1.0)
    officer.advance_tasks(1.1)
    assert officer.executing[0].status == WaraPSTaskStates.PAUSED
    officer.handle_exec_command(json.dumps({'command': 'signal-task', 'com-uuid': 'c', 'task-uuid': 't1', 'signal': '$continue'}), 1.2)
    assert officer.executing[0].status == WaraPSTaskStates.RUNNING
    officer.advance_tasks(1.3)
    assert client.sent == []
    assert client.cancels == 1


def test_a_refused_timeout_is_reported_and_the_task_stays() -> None:
    officer, client, published = officer_with(ActionClientState.RUNNING)
    start(officer, published)
    officer.executing[0].status = WaraPSTaskStates.RUNNING
    client.timed_out = True
    client.cancel_refused = True
    published.clear()
    officer.advance_tasks(1.0)
    assert published.exec_feedback[0].feedback == 'cancel refused: action still running'
    assert officer.executing
    officer.advance_tasks(1.1)
    assert officer.executing[0].status == WaraPSTaskStates.RUNNING


def test_a_cancel_that_errors_is_reported_on_the_task() -> None:
    officer, client, published = officer_with(ActionClientState.RUNNING)
    start(officer, published)
    client.error_on_cancel = True
    officer.handle_exec_command(json.dumps({'command': 'signal-task', 'com-uuid': 'c', 'task-uuid': 't1', 'signal': '$abort'}), 1.0)
    published.clear()
    officer.advance_tasks(1.1)
    assert officer.executing == []
    assert published.exec_feedback[0].status == 'error'
    assert 'ERROR' in published.exec_feedback[0].feedback
    assert published.aborts == 0


def test_done_finishes_and_error_reports_the_client_state() -> None:
    officer, client, published = officer_with(ActionClientState.DONE)
    client.feedback = 'there'
    start(officer, published)
    officer.executing[0].status = WaraPSTaskStates.RUNNING
    published.clear()
    officer.advance_tasks(1.0)
    assert officer.executing == []
    assert published.exec_feedback[0].status == 'finished'
    assert published.exec_feedback[0].feedback == 'there'

    client.state = ActionClientState.ERROR
    client.feedback = ''
    start(officer, published, now=2.0)
    officer.update_vehicle_health(Topics.VEHICLE_HEALTH_READY, 2.0)
    officer.executing[0].status = WaraPSTaskStates.RUNNING
    published.clear()
    officer.advance_tasks(2.1)
    assert published.exec_feedback[0].status == 'error'
    assert 'ERROR' in published.exec_feedback[0].feedback


def test_timeout_waits_for_the_cancel_then_is_an_error() -> None:
    officer, client, published = officer_with(ActionClientState.RUNNING)
    client.timed_out = True
    start(officer, published)
    officer.executing[0].status = WaraPSTaskStates.RUNNING
    officer.advance_tasks(1.0)
    assert officer.executing
    client.state = ActionClientState.CANCELLED
    published.clear()
    officer.advance_tasks(1.1)
    assert published.exec_feedback[0].status == 'error'
    assert officer.executing == []


def test_a_second_server_runs_beside_the_first_and_both_can_finish() -> None:
    officer, clients, published = officer_with_clients([ROS, '/sam0/wait'])
    start(officer, published)
    other = start(officer, published, now=1.1, task_uuid='t2', name='wait')
    assert other.status == 'started'
    assert [task.uuid for task in officer.executing] == ['t1', 't2']
    officer.advance_tasks(1.2)
    assert len(clients[ROS].sent) == 1
    assert len(clients['/sam0/wait'].sent) == 1
    clients[ROS].state = ActionClientState.DONE
    clients['/sam0/wait'].state = ActionClientState.DONE
    published.clear()
    officer.advance_tasks(1.3)
    assert officer.executing == []
    assert [message.status for message in published.exec_feedback] == ['finished', 'finished']


def test_a_third_start_on_a_busy_server_is_rejected() -> None:
    officer, _clients, published = officer_with_clients([ROS, '/sam0/wait'])
    start(officer, published)
    refused = start(officer, published, now=1.1, task_uuid='t2')
    assert refused.response == 'task already executing on move-to'
    other = start(officer, published, now=1.2, task_uuid='t3', name='wait')
    assert other.status == 'started'
    assert [task.uuid for task in officer.executing] == ['t1', 't3']


def test_stop_on_first_cancels_the_slower_task_and_waits() -> None:
    officer, clients, published = officer_with_clients([ROS, '/sam0/wait'])
    text = json.dumps({'command': 'start-tst', 'com-uuid': 'c', 'tst': {
        'name': 'conc', 'tst-uuid': 'm', 'params': {'stop-on-first': True}, 'children': [
            {'name': NAME, 'task-uuid': 'a', 'params': {}},
            {'name': 'wait', 'task-uuid': 'b', 'params': {}},
        ]}})
    published.clear()
    officer.handle_tst_command(text, 1.0)
    assert published.tst_response[0].response == 'accepted'
    assert [task.uuid for task in officer.executing] == ['a', 'b']
    officer.advance_tasks(1.1)
    clients[ROS].state = ActionClientState.DONE
    published.clear()
    officer.advance_tasks(1.2)
    assert [task.uuid for task in officer.executing] == ['b']
    assert clients['/sam0/wait'].cancels == 1
    assert clients['/sam0/wait'].state is ActionClientState.CANCELLING
    assert officer.health() == Topics.VEHICLE_HEALTH_WAITING
    assert any(message.feedback == 'cancelling: stop-on-first' for message in published.tst_feedback)
    clients['/sam0/wait'].state = ActionClientState.CANCELLED
    published.clear()
    officer.advance_tasks(1.3)
    assert officer.executing == []
    assert published.tst_feedback[0].feedback == 'cancelled: stop-on-first'
    assert officer.health() == Topics.VEHICLE_HEALTH_READY


def test_a_seq_inside_a_conc_runs_in_order() -> None:
    officer, clients, published = officer_with_clients([ROS, '/sam0/wait'])
    text = json.dumps({'command': 'start-tst', 'com-uuid': 'c', 'tst': {
        'name': 'conc', 'tst-uuid': 'm', 'children': [
            {'name': 'seq', 'children': [
                {'name': NAME, 'task-uuid': 'a', 'params': {'n': 1}},
                {'name': NAME, 'task-uuid': 'b', 'params': {'n': 2}},
            ]},
            {'name': 'wait', 'task-uuid': 'c', 'params': {}},
        ]}})
    officer.handle_tst_command(text, 1.0)
    assert [task.uuid for task in officer.executing] == ['a', 'c']
    officer.advance_tasks(1.1)
    clients[ROS].state = ActionClientState.DONE
    officer.advance_tasks(1.2)
    assert [task.uuid for task in officer.executing] == ['c', 'b']
    assert clients['/sam0/wait'].cancels == 0
    officer.advance_tasks(1.3)
    assert len(clients[ROS].sent) == 2
    assert [task.status for task in officer.executing if task.uuid == 'b'] == [WaraPSTaskStates.RUNNING]


def test_seq_starts_the_next_leaf_when_the_current_one_finishes() -> None:
    officer, client, published = officer_with()
    text = json.dumps({'command': 'start-tst', 'com-uuid': 'c', 'tst': {
        'name': 'seq', 'tst-uuid': 'm', 'children': [
            {'name': NAME, 'task-uuid': 'a', 'params': {'n': 1}},
            {'name': NAME, 'task-uuid': 'b', 'params': {'n': 2}},
        ]}})
    published.clear()
    officer.handle_tst_command(text, 1.0)
    assert published.tst_response[0].response == 'accepted'
    assert officer.executing[0].uuid == 'a'

    officer.advance_tasks(1.1)                              # send the first goal
    client.state = ActionClientState.DONE
    officer.advance_tasks(1.2)
    assert [task.uuid for task in officer.executing] == ['b']
    assert officer.executing[0].status == WaraPSTaskStates.STARTED
    officer.advance_tasks(1.3)
    assert len(client.sent) == 2
    assert officer.executing[0].status == WaraPSTaskStates.RUNNING


def test_health_not_ready_rejects_a_start_and_cancels_what_is_running() -> None:
    officer, client, published = officer_with(ActionClientState.RUNNING)
    refused = start(officer, published, now=100.0)            # the ready sample at 0.0 is stale
    assert refused.response == 'rejected: vehicle health status is not ok'

    officer.update_vehicle_health(Topics.VEHICLE_HEALTH_READY, 0.0)
    start(officer, published, now=1.0)
    officer.executing[0].status = WaraPSTaskStates.RUNNING
    officer.update_vehicle_health(Topics.VEHICLE_HEALTH_ERROR, 2.0)
    published.clear()
    officer.advance_tasks(2.1)
    assert [task.uuid for task in officer.executing] == ['t1']
    assert published.exec_feedback[0].feedback == 'cancelling: vehicle health ERROR'
    assert client.cancels == 1
    assert published.aborts == 0
    client.state = ActionClientState.CANCELLED
    published.clear()
    officer.advance_tasks(2.2)
    assert officer.executing == []
    assert published.exec_feedback[0].feedback == 'cancelled: vehicle health ERROR'


def test_signal_unit_on_exec_replies_there_and_aborts() -> None:
    officer, client, published = officer_with(ActionClientState.RUNNING)
    start(officer, published)
    published.clear()
    officer.handle_exec_command(json.dumps({'command': 'signal-unit', 'com-uuid': 'c', 'signal': '$abort'}), 1.0)
    assert [task.uuid for task in officer.executing] == ['t1']
    assert client.state is ActionClientState.CANCELLING
    assert published.exec_response[0].response == 'ok'
    assert published.aborts == 1


def test_unit_abort_cancels_and_publishes_the_smarc_abort() -> None:
    officer, client, published = officer_with(ActionClientState.RUNNING)
    start(officer, published)
    published.clear()
    officer.abort_all(1.0)
    assert [task.uuid for task in officer.executing] == ['t1']
    assert published.aborts == 1
    client.state = ActionClientState.CANCELLED
    officer.advance_tasks(1.1)
    assert officer.executing == []


def test_a_task_that_stops_heartbeating_is_forgotten() -> None:
    officer, _, published = officer_with()
    officer.publish_status(20.0)
    assert officer.available == {}


def test_unknown_task_is_rejected() -> None:
    officer, _, published = officer_with()
    text = json.dumps({'command': 'start-task', 'com-uuid': 'c', 'task-uuid': 't', 'task': {'name': 'nope', 'params': {}}})
    published.clear()
    officer.handle_exec_command(text, 1.0)
    assert published.exec_response[0].response == 'task not available'


def test_a_mission_times_out_on_the_officers_clock() -> None:
    officer, client, published = officer_with(ActionClientState.RUNNING)
    text = json.dumps({'command': 'start-tst', 'com-uuid': 'c', 'tst': {
        'name': 'seq', 'tst-uuid': 'm', 'params': {'timeout': 5}, 'children': [
            {'name': NAME, 'task-uuid': 'a', 'params': {}},
        ]}})
    officer.handle_tst_command(text, 1.0)
    officer.update_vehicle_health(Topics.VEHICLE_HEALTH_READY, 5.0)

    officer.advance_tasks(5.9)
    assert client.cancels == 0

    published.clear()
    officer.update_vehicle_health(Topics.VEHICLE_HEALTH_READY, 6.1)
    officer.advance_tasks(6.1)
    assert client.cancels == 1
    assert published.tst_feedback[0].feedback == 'cancelling: mission timeout exceeded'


def test_a_server_running_our_task_is_not_forgotten_when_it_skips_heartbeats() -> None:
    officer, client, published = officer_with(ActionClientState.RUNNING)
    start(officer, published)

    officer.publish_status(20.0)

    assert ROS in officer.available
    officer.update_vehicle_health(Topics.VEHICLE_HEALTH_READY, 20.0)
    refused = start(officer, published, now=20.0, task_uuid='t2')
    assert refused.response == 'task already executing on move-to'
