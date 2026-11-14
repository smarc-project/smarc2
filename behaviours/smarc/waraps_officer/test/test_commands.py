"""Every rejection string the officer can hand back, and the payloads it sends."""

import json

from smarc_msgs.msg import Topics

from waraps_officer.commands import (
    FLAT_SEQ_ONLY,
    Mission,
    Ping,
    QueryTask,
    Rejection,
    SignalTask,
    SignalUnit,
    StartTask,
    dumps,
    exec_response,
    feedback,
    health_is_ready,
    health_word,
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
    assert mission.timeout_s == 1800.0
    assert mission.leaves[0].name == 'move-to'
    assert mission.leaves[0].params['rpm'] == 100          # the leaf wins over common-params
    assert mission.leaves[1].params == {'rpm': 300}
    assert mission.leaves[1].timeout_s is None

    assert parse_tst({'command': 'start-tst', 'com-uuid': 'c', 'tst': {'name': 'conc', 'children': []}}).reason == FLAT_SEQ_ONLY
    nested = {'command': 'start-tst', 'com-uuid': 'c', 'tst': {'name': 'seq', 'children': [{'name': 'seq', 'task-uuid': 'a', 'children': []}]}}
    assert parse_tst(nested).reason == FLAT_SEQ_ONLY
    assert parse_tst({'command': 'start-tst', 'com-uuid': 'c'}).reason == 'task not found'
    assert parse_tst({'command': 'start-tst', 'com-uuid': 'c', 'tst': {'name': 'seq', 'children': [{}]}}).reason == 'Rejected: malformed task in mission'
    bad_timeout = {'command': 'start-tst', 'com-uuid': 'c', 'tst': {'name': 'seq', 'params': {'timeout': 'soon'}, 'children': []}}
    assert parse_tst(bad_timeout).reason == 'Rejected: Mission timeout value should be a float representing seconds'


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
    assert isinstance(parse_exec_command({'command': 'ping'}), Ping)
    assert isinstance(parse_tst({'command': 'start-tst'}), Rejection)
