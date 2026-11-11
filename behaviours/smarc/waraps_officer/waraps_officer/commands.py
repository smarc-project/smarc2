"""WARA-PS exec and TST commands, and the records the officer publishes.

No rclpy. A TST is a tree: ``seq`` and ``conc`` have children, a leaf has params.
This module accepts a root ``seq`` of leaves and rejects anything else; the
officer runs that seq one leaf at a time. The records are dataclasses.
``dumps`` is the JSON document, called at the publisher.
"""

import json
from dataclasses import dataclass, field

from smarc_msgs.msg import Topics

from waraps_officer.level1 import fresh
from waraps_officer.tasks import (
    TASK_SIGNALS,
    WaraPSTaskStates,
)

DEFAULT_MISSION_TIMEOUT_S = 1800.0
FLAT_SEQ_ONLY = 'rejected: only a flat seq is supported'


@dataclass(frozen=True)
class Rejection:
    com_uuid: str
    reason: str


@dataclass(frozen=True)
class Ping:
    com_uuid: str


@dataclass(frozen=True)
class StartTask:
    com_uuid: str
    task_uuid: str
    name: str
    params: dict
    description: str
    timeout_s: float | None


@dataclass(frozen=True)
class SignalTask:
    com_uuid: str
    task_uuid: str
    signal: str


@dataclass(frozen=True)
class SignalUnit:
    com_uuid: str
    signal: str


@dataclass(frozen=True)
class QueryTask:
    com_uuid: str
    task_uuid: str


@dataclass(frozen=True)
class Leaf:
    task_uuid: str
    name: str
    params: dict
    description: str
    timeout_s: float | None


@dataclass(frozen=True)
class Mission:
    com_uuid: str
    tst_uuid: str
    timeout_s: float
    leaves: list = field(default_factory=list)


def health_is_ready(value, stamp_s, now_s, timeout_s) -> bool:
    return value == Topics.VEHICLE_HEALTH_READY and fresh(stamp_s, now_s, timeout_s)


def health_word(value, is_fresh: bool) -> str:
    if not is_fresh:
        return 'silent'
    if value == Topics.VEHICLE_HEALTH_READY:
        return 'READY'
    if value == Topics.VEHICLE_HEALTH_WAITING:
        return 'WAITING'
    if value == Topics.VEHICLE_HEALTH_ERROR:
        return 'ERROR'
    return str(value)


def _timeout(params) -> float | None:
    value = params.get('timeout') if isinstance(params, dict) else None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        return None
    return float(value)


def _resolve_name(task: dict):
    """Return the action name, or a Rejection reason. custom-task reads params.action-name once."""
    name = task.get('name')
    if name != 'custom-task':
        return name
    params = task.get('params')
    if not isinstance(params, dict) or not params.get('action-name'):
        return Rejection('', "Rejected: Custom task missing 'action-name' in params")
    return params['action-name']


def parse_exec_command(command: dict):
    if not isinstance(command, dict) or command.get('command') is None:
        return Rejection('', "Invalid command: missing 'command' key")
    kind = command['command']
    com_uuid = command.get('com-uuid', '')

    if kind == 'ping':
        return Ping(com_uuid)
    if kind == 'query-task':
        if 'task-uuid' not in command:
            return Rejection(com_uuid, 'task not found')
        return QueryTask(com_uuid, command['task-uuid'])
    if kind == 'signal-task':
        if 'task-uuid' not in command:
            return Rejection(com_uuid, 'task not found')
        signal = command.get('signal')
        if signal not in TASK_SIGNALS:
            return Rejection(com_uuid, 'invalid signal')
        return SignalTask(com_uuid, command['task-uuid'], signal)
    if kind == 'signal-unit':
        signal = command.get('signal')
        if signal not in TASK_SIGNALS:
            return Rejection(com_uuid, 'invalid signal')
        return SignalUnit(com_uuid, signal)
    if kind != 'start-task':
        return Rejection(com_uuid, f'unknown command: {kind}')

    task = command.get('task')
    if not isinstance(task, dict) or 'name' not in task or 'task-uuid' not in command:
        return Rejection(com_uuid, 'task not found')
    name = _resolve_name(task)
    if isinstance(name, Rejection):
        return Rejection(com_uuid, name.reason)
    params = task['params'] if isinstance(task.get('params'), dict) else {}
    return StartTask(
        com_uuid, command['task-uuid'], name, params,
        task.get('description', ''), _timeout(params),
    )


def parse_tst(command: dict):
    if not isinstance(command, dict) or command.get('command') is None:
        return Rejection('', "Invalid command: missing 'command' key")
    kind = command['command']
    com_uuid = command.get('com-uuid', '')
    if kind == 'signal-unit':
        return parse_exec_command(command)
    if kind != 'start-tst':
        return Rejection(com_uuid, f'unknown command: {kind}')

    tst = command.get('tst')
    if not isinstance(tst, dict):
        return Rejection(com_uuid, 'task not found')
    if tst.get('name') != 'seq' or _nested(tst):
        return Rejection(com_uuid, FLAT_SEQ_ONLY)

    timeout = tst.get('params', {}).get('timeout', DEFAULT_MISSION_TIMEOUT_S) if isinstance(tst.get('params'), dict) else DEFAULT_MISSION_TIMEOUT_S
    try:
        timeout = float(timeout)
    except (TypeError, ValueError):
        return Rejection(com_uuid, 'Rejected: Mission timeout value should be a float representing seconds')

    children = tst.get('children')
    if not isinstance(children, list):
        return Rejection(com_uuid, 'task not found')
    common = tst['common-params'] if isinstance(tst.get('common-params'), dict) else {}
    leaves = []
    for child in children:
        if not isinstance(child, dict) or 'name' not in child or 'task-uuid' not in child:
            return Rejection(com_uuid, 'Rejected: malformed task in mission')
        name = _resolve_name(child)
        if isinstance(name, Rejection):
            return Rejection(com_uuid, name.reason)
        params = dict(common)
        if isinstance(child.get('params'), dict):
            params.update(child['params'])
        leaves.append(Leaf(child['task-uuid'], name, params, child.get('description', ''), _timeout(params)))
    return Mission(com_uuid, tst.get('tst-uuid', ''), timeout, leaves)


def _nested(tst: dict) -> bool:
    """A child that is itself a container, even an empty one."""
    for child in tst.get('children') or []:
        if isinstance(child, dict) and (child.get('name') in ('seq', 'conc') or 'children' in child):
            return True
    return False


@dataclass(frozen=True)
class TaskBody:
    name: str
    params: dict
    description: str


@dataclass(frozen=True)
class ExecReply:
    agent_uuid: str
    com_uuid: str
    response: str


@dataclass(frozen=True)
class StartReply:
    agent_uuid: str
    com_uuid: str
    task_uuid: str
    task: TaskBody
    status: str


@dataclass(frozen=True)
class Feedback:
    agent_uuid: str
    task_uuid: str
    feedback: str
    status: str
    tst_uuid: str | None = None


@dataclass(frozen=True)
class AvailableRow:
    name: str
    signals: tuple
    last_seen: float
    ros_name: str


@dataclass(frozen=True)
class ExecutingRow:
    task_uuid: str
    task_name: str
    status: str
    description: str


@dataclass(frozen=True)
class ExecutionInfo:
    name: str
    rate: float
    kind: str
    stamp: float
    available: tuple
    executing: tuple


def exec_response(agent_uuid, com_uuid, response) -> ExecReply:
    return ExecReply(agent_uuid, com_uuid, response)


def start_response(agent_uuid, com_uuid, task: StartTask) -> StartReply:
    return StartReply(
        agent_uuid, com_uuid, task.task_uuid,
        TaskBody(task.name, task.params, task.description),
        WaraPSTaskStates.STARTED,
    )


def feedback(agent_uuid, task_uuid, text, status, tst_uuid=None) -> Feedback:
    return Feedback(agent_uuid, task_uuid, text, status, tst_uuid)


def direct_execution_info(name, rate_hz, stamp_s, available, executing) -> ExecutionInfo:
    return ExecutionInfo(
        name, rate_hz, 'DirectExecutionInfo', stamp_s,
        tuple(AvailableRow(task.name, TASK_SIGNALS, task.last_seen, task.ros_name) for task in available),
        tuple(_executing_row(task) for task in executing),
    )


def tst_execution_info(name, rate_hz, stamp_s, available, executing) -> ExecutionInfo:
    info = direct_execution_info(name, rate_hz, stamp_s, available, executing)
    return ExecutionInfo(info.name, info.rate, 'TSTExecutionInfo', info.stamp, info.available, info.executing)


def executing_tasks(executing) -> list:
    return [_executing_row(task) for task in executing]


def _executing_row(task) -> ExecutingRow:
    return ExecutingRow(task.uuid, task.name, task.status, task.description)


def dumps(payload) -> str:
    """The JSON document for one published record. The dict stays in here."""

    def document(value):
        if isinstance(value, ExecReply):
            return {
                'agent-uuid': value.agent_uuid, 'com-uuid': value.com_uuid,
                'response': value.response, 'response-to': value.com_uuid,
            }
        if isinstance(value, StartReply):
            return {
                'agent-uuid': value.agent_uuid, 'com-uuid': value.com_uuid,
                'task-uuid': value.task_uuid,
                'task': {'name': value.task.name, 'params': value.task.params, 'description': value.task.description},
                'status': value.status,
            }
        if isinstance(value, Feedback):
            body = {
                'agent-uuid': value.agent_uuid, 'task-uuid': value.task_uuid,
                'feedback': value.feedback, 'status': value.status,
            }
            if value.tst_uuid is not None:
                body['tst-uuid'] = value.tst_uuid
            return body
        if isinstance(value, ExecutionInfo):
            return {
                'name': value.name, 'rate': value.rate, 'type': value.kind, 'stamp': value.stamp,
                'tasks-available': [document(row) for row in value.available],
                'tasks-executing': [document(row) for row in value.executing],
            }
        if isinstance(value, AvailableRow):
            return {'name': value.name, 'signals': list(value.signals), 'last_seen': value.last_seen, 'ros_name': value.ros_name}
        if isinstance(value, ExecutingRow):
            return {'task-uuid': value.task_uuid, 'task-name': value.task_name, 'status': value.status, 'description': value.description}
        if isinstance(value, list):
            return [document(item) for item in value]
        raise TypeError(type(value))

    return json.dumps(document(payload))
