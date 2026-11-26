"""WARA-PS exec and TST commands, parsed into dataclasses. No rclpy.

The command words (``ping``, ``start-task``, ``seq``, ...) are the WARA-PS
protocol's own, so they stay strings here; the officer gets a ``StartTask``,
a ``Mission``, or a ``Rejection`` carrying the reply text. Signals
(``$abort``, ``$pause``, ...) go through as the WARA-PS strings in
``tasks.WaraPSCommandSignals``.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from waraps_officer.tasks import TASK_SIGNALS

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
    children: tuple[Leaf | Seq | Conc, ...]


@dataclass(frozen=True)
class Conc:
    children: tuple[Leaf | Seq | Conc, ...]
    stop_on_first: bool


@dataclass(frozen=True)
class Mission:
    com_uuid: str
    tst_uuid: str
    timeout_s: float
    root: Seq | Conc


def parse_exec_command(command: dict) -> Rejection | Ping | QueryTask | SignalTask | SignalUnit | StartTask:
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
        return _parse_signal_unit(command, com_uuid)
    if kind != 'start-task':
        return Rejection(com_uuid, f'unknown command: {kind}')

    task = command.get('task')
    if not isinstance(task, dict) or 'name' not in task or 'task-uuid' not in command:
        return Rejection(com_uuid, 'task not found')
    name = _action_name(task, com_uuid)
    if isinstance(name, Rejection):
        return name
    params = task['params'] if isinstance(task.get('params'), dict) else {}
    return StartTask(
        com_uuid=com_uuid,
        task_uuid=command['task-uuid'],
        name=name,
        params=params,
        description=task.get('description', ''),
        timeout_s=_timeout_s(params),
    )


def parse_tst(command: dict) -> Rejection | SignalUnit | Mission:
    if not isinstance(command, dict) or command.get('command') is None:
        return Rejection('', "Invalid command: missing 'command' key")
    kind = command['command']
    com_uuid = command.get('com-uuid', '')
    if kind == 'signal-unit':
        return _parse_signal_unit(command, com_uuid)
    if kind != 'start-tst':
        return Rejection(com_uuid, f'unknown command: {kind}')

    tst = command.get('tst')
    if not isinstance(tst, dict):
        return Rejection(com_uuid, 'task not found')
    if tst.get('name') not in ('seq', 'conc'):
        return Rejection(com_uuid, 'rejected: tst root must be seq or conc')

    params = tst.get('params')
    timeout = params.get('timeout', DEFAULT_MISSION_TIMEOUT_S) if isinstance(params, dict) else DEFAULT_MISSION_TIMEOUT_S
    try:
        timeout = float(timeout)
    except (TypeError, ValueError):
        return Rejection(com_uuid, 'Rejected: Mission timeout value should be a float representing seconds')

    root = _parse_subtree(tst, {}, com_uuid)
    if isinstance(root, Rejection):
        return root
    return Mission(com_uuid, tst.get('tst-uuid', ''), timeout, root)


def leaves(node: Leaf | Seq | Conc) -> Iterator[Leaf]:
    if isinstance(node, Leaf):
        yield node
        return
    for child in node.children:
        yield from leaves(child)


def _parse_signal_unit(command: dict, com_uuid: str) -> SignalUnit | Rejection:
    """signal-unit is valid on both the exec and the TST topic."""
    signal = command.get('signal')
    if signal not in TASK_SIGNALS:
        return Rejection(com_uuid, 'invalid signal')
    return SignalUnit(com_uuid, signal)


def _action_name(task: dict, com_uuid: str) -> str | Rejection:
    """The action to start. A custom-task names it in params.action-name instead of name."""
    name = task.get('name')
    if name != 'custom-task':
        return name
    params = task.get('params')
    if not isinstance(params, dict) or not params.get('action-name'):
        return Rejection(com_uuid, "Rejected: Custom task missing 'action-name' in params")
    return params['action-name']


def _timeout_s(params: dict) -> float | None:
    """params.timeout in seconds. A bool, a non-number, or zero and below mean no timeout."""
    value = params.get('timeout')
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        return None
    return float(value)


def _parse_subtree(task: dict, inherited: dict, com_uuid: str) -> Leaf | Seq | Conc | Rejection:
    """A seq, a conc, or a leaf. common-params flow down; a leaf's own params win."""
    if not isinstance(task, dict) or 'name' not in task:
        return Rejection(com_uuid, 'Rejected: malformed task in mission')
    name = task['name']
    # A task that has children must be a seq or a conc.
    if name in ('seq', 'conc') or 'children' in task:
        if name not in ('seq', 'conc'):
            return Rejection(com_uuid, 'Rejected: malformed task in mission')
        children = task.get('children')
        if not isinstance(children, list):
            return Rejection(com_uuid, 'task not found')
        merged = dict(inherited)
        if isinstance(task.get('common-params'), dict):
            merged.update(task['common-params'])
        built = []
        for child in children:
            parsed = _parse_subtree(child, merged, com_uuid)
            # One bad leaf rejects the whole mission: half a TST is not what the operator sent.
            if isinstance(parsed, Rejection):
                return parsed
            built.append(parsed)
        if name == 'conc':
            params = task.get('params') if isinstance(task.get('params'), dict) else {}
            return Conc(tuple(built), params.get('stop-on-first') is True)
        return Seq(tuple(built))

    if 'task-uuid' not in task:
        return Rejection(com_uuid, 'Rejected: malformed task in mission')
    action = _action_name(task, com_uuid)
    if isinstance(action, Rejection):
        return action
    params = dict(inherited)
    if isinstance(task.get('params'), dict):
        params.update(task['params'])
    return Leaf(
        task_uuid=task['task-uuid'],
        name=action,
        params=params,
        description=task.get('description', ''),
        timeout_s=_timeout_s(params),
    )
