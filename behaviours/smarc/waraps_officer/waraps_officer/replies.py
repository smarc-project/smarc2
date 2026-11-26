"""The records the officer publishes, and their JSON. No rclpy.

The officer builds these dataclasses. Each one writes its own WARA-PS
document, so the hyphenated keys stay in this file; ``dumps`` is called at
the publisher.
"""

import json
from dataclasses import dataclass
from enum import Enum

from waraps_officer.commands import StartTask
from waraps_officer.tasks import AvailableTask, ExecutingTask, TASK_SIGNALS, WaraPSTaskStates


class ExecutionInfoKind(Enum):
    DIRECT = 'DirectExecutionInfo'
    TST = 'TSTExecutionInfo'


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

    def document(self) -> dict:
        return {
            'agent-uuid': self.agent_uuid,
            'com-uuid': self.com_uuid,
            'response': self.response,
            'response-to': self.com_uuid,
        }


@dataclass(frozen=True)
class StartReply:
    agent_uuid: str
    com_uuid: str
    task_uuid: str
    task: TaskBody
    status: str

    def document(self) -> dict:
        return {
            'agent-uuid': self.agent_uuid,
            'com-uuid': self.com_uuid,
            'task-uuid': self.task_uuid,
            'task': {'name': self.task.name, 'params': self.task.params, 'description': self.task.description},
            'status': self.status,
        }


@dataclass(frozen=True)
class Feedback:
    agent_uuid: str
    task_uuid: str
    feedback: str
    status: str
    tst_uuid: str | None = None

    def document(self) -> dict:
        body = {
            'agent-uuid': self.agent_uuid,
            'task-uuid': self.task_uuid,
            'feedback': self.feedback,
            'status': self.status,
        }
        # A direct task has no TST, so the key is left out.
        if self.tst_uuid is not None:
            body['tst-uuid'] = self.tst_uuid
        return body


@dataclass(frozen=True)
class AvailableRow:
    name: str
    signals: tuple[str, ...]
    last_seen: float
    ros_name: str

    def document(self) -> dict:
        return {
            'name': self.name,
            'signals': list(self.signals),
            'last_seen': self.last_seen,
            'ros_name': self.ros_name,
        }


@dataclass(frozen=True)
class ExecutingRow:
    task_uuid: str
    task_name: str
    status: str
    description: str

    def document(self) -> dict:
        return {
            'task-uuid': self.task_uuid,
            'task-name': self.task_name,
            'status': self.status,
            'description': self.description,
        }


@dataclass(frozen=True)
class ExecutionInfo:
    name: str
    rate: float
    kind: ExecutionInfoKind
    stamp: float
    available: tuple[AvailableRow, ...]
    executing: tuple[ExecutingRow, ...]

    def document(self) -> dict:
        return {
            'name': self.name,
            'rate': self.rate,
            'type': self.kind.value,
            'stamp': self.stamp,
            'tasks-available': [row.document() for row in self.available],
            'tasks-executing': [row.document() for row in self.executing],
        }


def start_response(agent_uuid: str, com_uuid: str, task: StartTask) -> StartReply:
    return StartReply(
        agent_uuid=agent_uuid,
        com_uuid=com_uuid,
        task_uuid=task.task_uuid,
        task=TaskBody(task.name, task.params, task.description),
        status=WaraPSTaskStates.STARTED,
    )


def execution_info(
    kind: ExecutionInfoKind,
    name: str,
    rate_hz: float,
    stamp_s: float,
    available: list[AvailableTask],
    executing: list[ExecutingTask],
) -> ExecutionInfo:
    return ExecutionInfo(
        name=name,
        rate=rate_hz,
        kind=kind,
        stamp=stamp_s,
        available=tuple(AvailableRow(task.name, TASK_SIGNALS, task.last_seen, task.ros_name) for task in available),
        executing=tuple(_executing_row(task) for task in executing),
    )


def executing_tasks(executing: list[ExecutingTask]) -> list[ExecutingRow]:
    return [_executing_row(task) for task in executing]


def _executing_row(task: ExecutingTask) -> ExecutingRow:
    return ExecutingRow(task.uuid, task.name, task.status, task.description)


def dumps(payload: ExecReply | StartReply | Feedback | ExecutionInfo | list[ExecutingRow]) -> str:
    """The JSON document for one published record. The executing-tasks topic carries a bare list of rows."""
    if isinstance(payload, list):
        return json.dumps([row.document() for row in payload])
    return json.dumps(payload.document())
