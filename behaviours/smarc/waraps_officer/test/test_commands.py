"""Every rejection string the officer can hand back, and the payloads it sends."""

import json

from smarc_msgs.msg import Topics

from waraps_officer.commands import (
    Conc,
    Mission,
    Ping,
    QueryTask,
    Rejection,
    Seq,
    SignalTask,
    SignalUnit,
    StartTask,
    after_leaf,
    dumps,
    exec_response,
    feedback,
    health_is_ready,
    health_word,
    officer_health,
    open_run,
    parse_exec_command,
    parse_tst,
    start_response,
)


def test_ping_query_and_signals():
    assert parse_exec_command({'command': 'ping', 'com-uuid': 'c'}) == Ping('c')
    assert parse_exec_command({'command': 'query-task', 'com-uuid': 'c', 'task-uuid': 't'}) == QueryTask('c', 't')
    assert parse_exec_command({'command': 'signal-task', 'com-uuid': 'c', 'task-uuid': 't', 'signal': '$pause'}) == SignalTask('c', 't', '$pause')
    assert parse_exec_command({'command': 'signal-unit', 'com-uuid': 'c', 'signal': '$abort'}) == SignalUnit('c', '$abort')


def test_exec_rejections():
    assert parse_exec_command({}).reason == "Invalid command: missing 'command' key"
    assert parse_exec_command({'command': 'nope', 'com-uuid': 'c'}).reason == 'unknown command: nope'
    assert parse_exec_command({'command': 'start-task', 'com-uuid': 'c'}).reason == 'task not found'
    assert parse_exec_command({'command': 'start-task', 'com-uuid': 'c', 'task': {'name': 'wait'}}).reason == 'task not found'
    missing = parse_exec_command({'command': 'start-task', 'com-uuid': 'c', 'task-uuid': 't',
                                   'task': {'name': 'custom-task', 'params': {}}})
    assert missing.reason == "Rejected: Custom task missing 'action-name' in params"
    assert parse_exec_command({'command': 'signal-task', 'com-uuid': 'c'}).reason == 'task not found'
    assert parse_exec_command({'command': 'signal-task', 'com-uuid': 'c', 'task-uuid': 't', 'signal': '$nope'}).reason == 'invalid signal'
    assert parse_exec_command({'command': 'query-task', 'com-uuid': 'c'}).reason == 'task not found'
    assert parse_exec_command({'command': 'signal-unit', 'com-uuid': 'c', 'signal': '$nope'}).reason == 'invalid signal'
    assert parse_exec_command({'command': 'signal-unit', 'com-uuid': 'c', 'signal': '$cancel_abort'}).reason == 'invalid signal'


def test_start_task_resolves_custom_task_and_timeout():
    started = parse_exec_command({
        'command': 'start-task', 'com-uuid': 'c', 'task-uuid': 't',
        'task': {'name': 'custom-task', 'description': 'look', 'params': {'action-name': 'move-to', 'timeout': 12}},
    })
    assert started == StartTask('c', 't', 'move-to', {'action-name': 'move-to', 'timeout': 12}, 'look', 12.0)


def test_tst_flat_seq_merges_common_params_and_rejects_the_rest():
    mission = parse_tst({
        'command': 'start-tst', 'com-uuid': 'c',
        'tst': {
            'name': 'seq', 'tst-uuid': 'm',
            'common-params': {'rpm': 300},
            'children': [
                {'name': 'custom-task', 'task-uuid': 'a', 'params': {'action-name': 'move-to', 'rpm': 100}},
                {'name': 'wait', 'task-uuid': 'b'},
            ],
        },
    })
    assert isinstance(mission, Mission)
    assert isinstance(mission.root, Seq)
    assert mission.timeout_s == 1800.0
    assert mission.root.children[0].name == 'move-to'
    assert mission.root.children[0].params['rpm'] == 100   # the leaf wins over common-params
    assert mission.root.children[1].params == {'rpm': 300}
    assert mission.root.children[1].timeout_s is None

    empty = parse_tst({'command': 'start-tst', 'com-uuid': 'c', 'tst': {'name': 'conc', 'children': []}})
    assert isinstance(empty, Mission)
    assert isinstance(empty.root, Conc)
    assert empty.root.stop_on_first is False
    nested = {'command': 'start-tst', 'com-uuid': 'c', 'tst': {'name': 'seq', 'children': [{'name': 'seq', 'task-uuid': 'a', 'children': []}]}}
    parsed = parse_tst(nested)
    assert parsed.root.children == ()   # an empty container has nothing to run
    assert parse_tst({'command': 'start-tst', 'com-uuid': 'c'}).reason == 'task not found'
    assert parse_tst({'command': 'start-tst', 'com-uuid': 'c', 'tst': {'name': 'seq', 'children': [{}]}}).reason == 'Rejected: malformed task in mission'
    bad_timeout = {'command': 'start-tst', 'com-uuid': 'c', 'tst': {'name': 'seq', 'params': {'timeout': 'soon'}, 'children': []}}
    assert parse_tst(bad_timeout).reason == 'Rejected: Mission timeout value should be a float representing seconds'


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


def test_payloads_and_health():
    task = StartTask('c', 't', 'wait', {}, '', None)
    assert start_response('agent', 'c', task).status == 'started'
    assert exec_response('agent', 'c', 'pong').response == 'pong'
    assert feedback('agent', 't', 'hi', 'running', 'm').tst_uuid == 'm'
    assert json.loads(dumps(exec_response('a', 'c', 'ok')))['response-to'] == 'c'
    assert health_is_ready(Topics.VEHICLE_HEALTH_READY, 1.0, 5.0, 10.0)
    assert not health_is_ready(Topics.VEHICLE_HEALTH_READY, 1.0, 20.0, 10.0)
    assert not health_is_ready(Topics.VEHICLE_HEALTH_ERROR, 1.0, 2.0, 10.0)
    assert health_word(Topics.VEHICLE_HEALTH_WAITING, True) == 'WAITING'
    assert health_word(Topics.VEHICLE_HEALTH_READY, False) == 'silent'
    assert officer_health([], {'running'}, 'cancelling') == Topics.VEHICLE_HEALTH_READY
    assert isinstance(parse_exec_command({'command': 'ping'}), Ping)
    assert isinstance(parse_tst({'command': 'start-tst'}), Rejection)


def test_stop_on_first_cancels_the_sibling_after_a_seq_runs_in_order():
    mission = parse_tst({
        'command': 'start-tst', 'com-uuid': 'c',
        'tst': {
            'name': 'conc', 'params': {'stop-on-first': True}, 'children': [
                {'name': 'seq', 'children': [
                    {'name': 'move-to', 'task-uuid': 'a'},
                    {'name': 'move-to', 'task-uuid': 'b'},
                ]},
                {'name': 'wait', 'task-uuid': 'c'},
            ],
        },
    })
    run, follow = open_run(mission.root)
    assert [leaf.task_uuid for leaf in follow.start] == ['a', 'c']
    nxt = after_leaf(run, 'a', 'finished')
    assert [leaf.task_uuid for leaf in nxt.start] == ['b']
    assert nxt.cancel == ()
    assert nxt.done is False
    stopped = after_leaf(run, 'b', 'finished')
    assert stopped.start == ()
    assert stopped.cancel == ('c',)
    assert stopped.done is False
    ended = after_leaf(run, 'c', 'enough')
    assert ended.done is True
    assert ended.cancel == ()


def test_an_empty_container_inside_a_seq_is_dropped():
    def mission(children):
        return parse_tst({'command': 'start-tst', 'com-uuid': 'c', 'tst': {'name': 'seq', 'children': children}})

    empty_first = mission([{'name': 'conc', 'children': []}, {'name': 'wait', 'task-uuid': 'x'}])
    run, follow = open_run(empty_first.root)
    assert [leaf.task_uuid for leaf in follow.start] == ['x']
    assert follow.done is False

    empty_between = mission([
        {'name': 'wait', 'task-uuid': 'x'},
        {'name': 'seq', 'children': [{'name': 'conc', 'children': []}]},
        {'name': 'wait', 'task-uuid': 'y'},
    ])
    run, follow = open_run(empty_between.root)
    after_x = after_leaf(run, 'x', 'finished')
    assert [leaf.task_uuid for leaf in after_x.start] == ['y']
    assert after_leaf(run, 'y', 'finished').done is True


def test_an_empty_child_of_a_conc_is_dropped_and_does_not_stop_it_first():
    def mission(params):
        children = [{'name': 'seq', 'children': []}, {'name': 'wait', 'task-uuid': 'x'}, {'name': 'wait', 'task-uuid': 'y'}]
        return parse_tst({'command': 'start-tst', 'com-uuid': 'c', 'tst': {'name': 'conc', 'params': params, 'children': children}})

    run, follow = open_run(mission({}).root)
    assert [leaf.task_uuid for leaf in follow.start] == ['x', 'y']
    assert after_leaf(run, 'x', 'finished').done is False
    assert after_leaf(run, 'y', 'finished').done is True

    run, follow = open_run(mission({'stop-on-first': True}).root)
    assert [leaf.task_uuid for leaf in follow.start] == ['x', 'y']
    assert follow.done is False
