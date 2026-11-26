"""WARA-PS exec and TST commands, and the records the officer publishes.

No rclpy. A TST is a tree of ``seq`` and ``conc``. ``open_run`` names the
leaves that start together; ``after_leaf`` names the next leaves and, when
``stop-on-first`` is set, the siblings to cancel. The officer sends and
cancels. The records are dataclasses. ``dumps`` is the JSON document,
called at the publisher.
"""

import json
from dataclasses import dataclass, field
from enum import Enum

from smarc_msgs.msg import Topics

from waraps_officer.level1 import fresh
from waraps_officer.tasks import (
    TASK_SIGNALS,
    WaraPSTaskStates,
)

DEFAULT_MISSION_TIMEOUT_S = 1800.0


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
class Seq:
    children: tuple


@dataclass(frozen=True)
class Conc:
    children: tuple
    stop_on_first: bool


@dataclass(frozen=True)
class Mission:
    com_uuid: str
    tst_uuid: str
    timeout_s: float
    root: object


def health_is_ready(value, stamp_s, now_s, timeout_s) -> bool:
    return value == Topics.VEHICLE_HEALTH_READY and fresh(stamp_s, now_s, timeout_s)


def officer_health(tasks, running_states, cancelling) -> int:
    """The officer's own health, using the vehicle health values.

    ERROR: a server refused a cancel and the action is still running.
    WAITING: a cancel was asked and has not been answered.
    READY: neither. A task that is simply running is READY.
    """
    if any(task.cancel_refused for task in tasks):
        return Topics.VEHICLE_HEALTH_ERROR
    stopping = (WaraPSTaskStates.ABORTED, WaraPSTaskStates.ENOUGH, WaraPSTaskStates.PAUSED)
    for task in tasks:
        state = task.client.state
        if state is cancelling or (task.status in stopping and state in running_states):
            return Topics.VEHICLE_HEALTH_WAITING
    return Topics.VEHICLE_HEALTH_READY


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
    if tst.get('name') not in ('seq', 'conc'):
        return Rejection(com_uuid, 'rejected: tst root must be seq or conc')

    timeout = tst.get('params', {}).get('timeout', DEFAULT_MISSION_TIMEOUT_S) if isinstance(tst.get('params'), dict) else DEFAULT_MISSION_TIMEOUT_S
    try:
        timeout = float(timeout)
    except (TypeError, ValueError):
        return Rejection(com_uuid, 'Rejected: Mission timeout value should be a float representing seconds')

    root = _node(tst, {})
    if isinstance(root, Rejection):
        return Rejection(com_uuid, root.reason)
    return Mission(com_uuid, tst.get('tst-uuid', ''), timeout, root)


def _node(task, inherited):
    """A seq, a conc, or a leaf. common-params flow down; a leaf's own params win."""
    if not isinstance(task, dict) or 'name' not in task:
        return Rejection('', 'Rejected: malformed task in mission')
    name = task['name']
    if name in ('seq', 'conc') or 'children' in task:
        if name not in ('seq', 'conc'):
            return Rejection('', 'Rejected: malformed task in mission')
        children = task.get('children')
        if not isinstance(children, list):
            return Rejection('', 'task not found')
        # An empty seq or conc means the mission was sent before it was fully planned.
        # Running the rest would do something nobody planned, so the whole TST is refused.
        if not children:
            return Rejection('', 'Rejected: empty seq or conc in mission')
        merged = dict(inherited)
        if isinstance(task.get('common-params'), dict):
            merged.update(task['common-params'])
        built = []
        for child in children:
            parsed = _node(child, merged)
            if isinstance(parsed, Rejection):
                return parsed
            built.append(parsed)
        if name == 'conc':
            params = task.get('params') if isinstance(task.get('params'), dict) else {}
            return Conc(tuple(built), params.get('stop-on-first') is True)
        return Seq(tuple(built))
    if 'task-uuid' not in task:
        return Rejection('', 'Rejected: malformed task in mission')
    resolved = _resolve_name(task)
    if isinstance(resolved, Rejection):
        return Rejection('', resolved.reason)
    params = dict(inherited)
    if isinstance(task.get('params'), dict):
        params.update(task['params'])
    return Leaf(task['task-uuid'], resolved, params, task.get('description', ''), _timeout(params))


def each_leaf(node):
    if isinstance(node, Leaf):
        yield node
        return
    for child in node.children:
        yield from each_leaf(child)


class Phase(Enum):
    IDLE = 'idle'
    LIVE = 'live'
    STOPPING = 'stopping'
    DONE = 'done'
    FAILED = 'failed'


@dataclass
class Slot:
    """One node of a running TST."""

    node: object
    parent: object = None
    children: list = field(default_factory=list)
    index: int = 0
    phase: Phase = Phase.IDLE
    fail: str | None = None


@dataclass(frozen=True)
class Follow:
    """Leaves to start, task uuids to cancel, and whether the TST is over."""

    start: tuple = ()
    cancel: tuple = ()
    done: bool = False


class Run:
    def __init__(self, root: Slot):
        self.root = root
        self.by_uuid = {}
        self._index(root)

    def _index(self, slot):
        if isinstance(slot.node, Leaf):
            self.by_uuid[slot.node.task_uuid] = slot
        for child in slot.children:
            self._index(child)


def open_run(root) -> tuple:
    """The leaves that start now. An empty tree is already done."""
    run = Run(_slot(root, None))
    start = []
    _arm(run.root, start)
    done = not start
    if done:
        run.root.phase = Phase.DONE
    return run, Follow(tuple(start), (), done)


def after_leaf(run: Run, uuid: str, status: str) -> Follow:
    """What to do once a leaf has left the executing list."""
    slot = run.by_uuid[uuid]
    slot.phase = Phase.DONE if status == WaraPSTaskStates.FINISHED else Phase.FAILED
    start, cancel = [], []
    done = _heard(slot.parent, slot, status, start, cancel)
    return Follow(tuple(start), tuple(cancel), done)


def _slot(node, parent):
    slot = Slot(node, parent)
    if not isinstance(node, Leaf):
        slot.children = [_slot(child, slot) for child in node.children]
    return slot


def _arm(slot, start):
    """Mark the leaves that can start without waiting for a sibling."""
    if slot.phase in (Phase.DONE, Phase.FAILED, Phase.STOPPING):
        return
    if isinstance(slot.node, Leaf):
        if slot.phase is Phase.IDLE:
            slot.phase = Phase.LIVE
            start.append(slot.node)
        return
    slot.phase = Phase.LIVE
    if isinstance(slot.node, Seq):
        if slot.index < len(slot.children):
            _arm(slot.children[slot.index], start)
        return
    for child in slot.children:
        _arm(child, start)


def _heard(parent, child, status, start, cancel) -> bool:
    if parent is None:
        return True
    if isinstance(parent.node, Seq):
        return _seq(parent, status, start, cancel)
    return _conc(parent, child, status, start, cancel)


def _seq(parent, status, start, cancel) -> bool:
    if parent.phase is Phase.STOPPING:
        return _quiet(parent, start, cancel)
    if status != WaraPSTaskStates.FINISHED:
        parent.phase = Phase.FAILED
        parent.fail = status
        return _heard(parent.parent, parent, status, start, cancel)
    parent.index += 1
    if parent.index < len(parent.children):
        _arm(parent.children[parent.index], start)
        return False
    parent.phase = Phase.DONE
    return _heard(parent.parent, parent, WaraPSTaskStates.FINISHED, start, cancel)


def _conc(parent, child, status, start, cancel) -> bool:
    if parent.phase is Phase.STOPPING:
        return _quiet(parent, start, cancel)
    if parent.node.stop_on_first or status != WaraPSTaskStates.FINISHED:
        parent.phase = Phase.STOPPING
        if status != WaraPSTaskStates.FINISHED:
            parent.fail = status
        _hold(parent, cancel, keep=child)
        return _quiet(parent, start, cancel)
    if all(item.phase is Phase.DONE for item in parent.children):
        parent.phase = Phase.DONE
        return _heard(parent.parent, parent, WaraPSTaskStates.FINISHED, start, cancel)
    return False


def _quiet(parent, start, cancel) -> bool:
    """The container is already stopping. It ends when no leaf is still out."""
    if _pending(parent):
        return False
    status = parent.fail or WaraPSTaskStates.FINISHED
    parent.phase = Phase.DONE if parent.fail is None else Phase.FAILED
    return _heard(parent.parent, parent, status, start, cancel)


def _hold(slot, cancel, keep):
    for child in slot.children:
        if child is keep:
            continue
        _freeze(child, cancel)


def _freeze(slot, cancel):
    if isinstance(slot.node, Leaf):
        if slot.phase is Phase.LIVE:
            slot.phase = Phase.STOPPING
            cancel.append(slot.node.task_uuid)
        elif slot.phase is Phase.IDLE:
            slot.phase = Phase.DONE
        return
    if slot.phase not in (Phase.DONE, Phase.FAILED):
        slot.phase = Phase.STOPPING
    for child in slot.children:
        _freeze(child, cancel)


def _pending(slot) -> bool:
    if isinstance(slot.node, Leaf):
        return slot.phase in (Phase.LIVE, Phase.STOPPING)
    return any(_pending(child) for child in slot.children)


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
