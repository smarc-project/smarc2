"""A running TST: what starts, what gets cancelled, and when it is over."""

from waraps_officer.commands import parse_tst
from waraps_officer.mission_run import next_after_leaf, start_run


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
    run, first_steps = start_run(mission.root)
    assert [leaf.task_uuid for leaf in first_steps.start] == ['a', 'c']
    nxt = next_after_leaf(run, 'a', 'finished')
    assert [leaf.task_uuid for leaf in nxt.start] == ['b']
    assert nxt.cancel == ()
    assert nxt.done is False
    stopped = next_after_leaf(run, 'b', 'finished')
    assert stopped.start == ()
    assert stopped.cancel == ('c',)
    assert stopped.done is False
    ended = next_after_leaf(run, 'c', 'enough')
    assert ended.done is True
    assert ended.cancel == ()


def test_an_empty_tst_is_done_before_it_starts():
    mission = parse_tst({'command': 'start-tst', 'com-uuid': 'c', 'tst': {'name': 'conc', 'children': []}})
    _, first_steps = start_run(mission.root)
    assert first_steps.start == ()
    assert first_steps.done is True
