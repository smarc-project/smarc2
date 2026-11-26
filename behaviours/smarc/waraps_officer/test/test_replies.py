"""The published records and the JSON WARA-PS reads."""

import json

from waraps_officer.commands import StartTask
from waraps_officer.replies import (
    ExecReply,
    ExecutionInfoKind,
    Feedback,
    dumps,
    execution_info,
    start_response,
)
from waraps_officer.tasks import AvailableTask


def test_replies_and_feedback_documents():
    task = StartTask('c', 't', 'wait', {}, '', None)
    assert start_response('agent', 'c', task).status == 'started'
    assert json.loads(dumps(ExecReply('a', 'c', 'ok')))['response-to'] == 'c'
    with_tst = json.loads(dumps(Feedback('agent', 't', 'hi', 'running', 'm')))
    assert with_tst['tst-uuid'] == 'm'
    direct = json.loads(dumps(Feedback('agent', 't', 'hi', 'running')))
    assert 'tst-uuid' not in direct


def test_execution_info_type_is_the_wara_ps_word():
    available = [AvailableTask('move-to', '/sam0/move_to', 3.0)]
    direct = json.loads(dumps(execution_info(ExecutionInfoKind.DIRECT, 'sam0', 1.0, 4.0, available, [])))
    tst = json.loads(dumps(execution_info(ExecutionInfoKind.TST, 'sam0', 1.0, 4.0, available, [])))
    assert direct['type'] == 'DirectExecutionInfo'
    assert tst['type'] == 'TSTExecutionInfo'
    assert tst['tasks-available'] == direct['tasks-available']
