"""Every rejection string the parser can hand back, and what a parsed TST looks like."""

from waraps_officer.commands import (
    Conc,
    Leaf,
    Mission,
    Ping,
    QueryTask,
    Rejection,
    Seq,
    SignalTask,
    SignalUnit,
    StartTask,
    leaves,
    parse_exec_command,
    parse_tst,
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

    assert parse_tst({'command': 'start-tst', 'com-uuid': 'c'}).reason == 'task not found'
    assert parse_tst({'command': 'start-tst', 'com-uuid': 'c', 'tst': {'name': 'seq', 'children': [{}]}}).reason == 'Rejected: malformed task in mission'
    bad_timeout = {'command': 'start-tst', 'com-uuid': 'c', 'tst': {'name': 'seq', 'params': {'timeout': 'soon'}, 'children': []}}
    assert parse_tst(bad_timeout).reason == 'Rejected: Mission timeout value should be a float representing seconds'


def test_a_bad_leaf_deep_in_a_mission_rejects_it_with_the_commands_com_uuid():
    bad_leaf = {'name': 'custom-task', 'task-uuid': 'x', 'params': {}}
    rejected = parse_tst({
        'command': 'start-tst',
        'com-uuid': 'c',
        'tst': {'name': 'seq', 'children': [{'name': 'conc', 'children': [bad_leaf]}]},
    })
    assert rejected.com_uuid == 'c'
    assert rejected.reason == "Rejected: Custom task missing 'action-name' in params"


def test_leaves_walks_the_tree_in_order():
    a = Leaf('a', 'wait', {}, '', None)
    b = Leaf('b', 'wait', {}, '', None)
    c = Leaf('c', 'wait', {}, '', None)
    tree = Seq((a, Conc((b, c), stop_on_first=False)))
    assert list(leaves(tree)) == [a, b, c]


def test_a_tst_with_an_empty_seq_or_conc_anywhere_is_refused():
    def mission(tst):
        return parse_tst({'command': 'start-tst', 'com-uuid': 'c', 'tst': tst})

    wait = {'name': 'wait', 'task-uuid': 'x'}
    for tst in (
        {'name': 'conc', 'children': []},
        {'name': 'seq', 'children': [{'name': 'conc', 'children': []}, wait]},
        {'name': 'seq', 'children': [wait, {'name': 'seq', 'children': [{'name': 'conc', 'children': []}]}]},
        {'name': 'conc', 'params': {'stop-on-first': True}, 'children': [{'name': 'seq', 'children': []}, wait]},
    ):
        assert mission(tst) == Rejection('c', 'Rejected: empty seq or conc in mission')
