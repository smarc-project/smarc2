"""WARA-PS levels 2 and 3 over GentlerActionClient: the officer's logic.

``WarapsOfficer`` holds the tasks and decides. It makes no node: the node in
``ros2waraps_officer.py`` hands it one function per output topic and calls it
on a timer. A second task is rejected while its action server is busy. A TST
``seq`` starts its next leaf when the current one finishes. A ``conc`` starts
its children together.
"""

import json
from collections.abc import Callable

from smarc_action_base.gentler_action_client import ClientReport, GentlerActionClient
from smarc_action_base.smarc_action_base import SMARCActionClient

from waraps_officer.commands import (
    ExecReply,
    ExecutingRow,
    ExecutionInfo,
    Feedback,
    Follow,
    Leaf,
    Mission,
    Ping,
    QueryTask,
    Rejection,
    Run,
    SignalTask,
    SignalUnit,
    StartReply,
    StartTask,
    after_leaf,
    direct_execution_info,
    each_leaf,
    exec_response,
    executing_tasks,
    feedback,
    health_is_ready,
    health_word,
    officer_health,
    open_run,
    parse_exec_command,
    parse_tst,
    start_response,
    tst_execution_info,
)
from waraps_officer.level1 import fresh
from waraps_officer.tasks import (
    WaraPSCommandSignals,
    WaraPSTaskStates,
    AvailableTask,
    ExecutingTask,
    waraps_task_name,
)

_STOP = (WaraPSCommandSignals.ABORT, WaraPSCommandSignals.ENOUGH)
_STOP_STATUS = {
    WaraPSCommandSignals.ABORT: WaraPSTaskStates.ABORTED,
    WaraPSCommandSignals.ENOUGH: WaraPSTaskStates.ENOUGH,
}


class WarapsOfficer:
    def __init__(
        self,
        client_factory: Callable[[str], GentlerActionClient],
        name: str,
        rate_hz: float,
        liveliness_s: float,
        health_timeout_s: float,
        publish_abort: Callable[[], None],
        publish_health: Callable[[int], None],
        publish_exec_response: Callable[[ExecReply | StartReply], None],
        publish_tst_response: Callable[[ExecReply], None],
        publish_exec_feedback: Callable[[Feedback], None],
        publish_tst_feedback: Callable[[Feedback], None],
        publish_direct_execution_info: Callable[[ExecutionInfo], None],
        publish_tst_execution_info: Callable[[ExecutionInfo], None],
        publish_executing_tasks: Callable[[list[ExecutingRow]], None],
    ) -> None:
        self._client_factory = client_factory
        self._name = name
        self._rate_hz = rate_hz
        self._liveliness_s = liveliness_s
        self._health_timeout_s = health_timeout_s
        self._publish_abort = publish_abort
        self._publish_health = publish_health
        self._publish_exec_response = publish_exec_response
        self._publish_tst_response = publish_tst_response
        self._publish_exec_feedback = publish_exec_feedback
        self._publish_tst_feedback = publish_tst_feedback
        self._publish_direct_execution_info = publish_direct_execution_info
        self._publish_tst_execution_info = publish_tst_execution_info
        self._publish_executing_tasks = publish_executing_tasks
        self.agent_uuid = ''
        self.available: dict[str, AvailableTask] = {}
        self.clients: dict[str, GentlerActionClient] = {}
        self.executing: list[ExecutingTask] = []
        self._mission: Mission | None = None
        self._run: Run | None = None
        self._mission_started_s: float | None = None
        self._health_value: int | None = None
        self._health_stamp_s: float | None = None

    # ---- things other nodes say --------------------------------------------

    def learn_agent_uuid(self, heartbeat_json: str) -> bool:
        """Take agent-uuid from the first heartbeat. True once it is known."""
        if self.agent_uuid:
            return True
        try:
            payload = json.loads(heartbeat_json)
        except (json.JSONDecodeError, TypeError):
            return False
        uuid = payload.get('agent-uuid') if isinstance(payload, dict) else None
        if not uuid:
            return False
        self.agent_uuid = uuid
        return True

    def track_action_server(self, ros_name: str, now_s: float) -> None:
        ros_name = (ros_name or '').strip()
        if not ros_name:
            return
        name = waraps_task_name(ros_name)
        self.available[ros_name] = AvailableTask(name, ros_name, now_s)
        if ros_name not in self.clients:
            self.clients[ros_name] = self._client_factory(ros_name)

    def update_vehicle_health(self, level: int, now_s: float) -> None:
        self._health_value = level
        self._health_stamp_s = now_s

    def handle_exec_command(self, command_json: str, now_s: float) -> None:
        self._dispatch(parse_exec_command(_load(command_json)), now_s, tst=False)

    def handle_tst_command(self, command_json: str, now_s: float) -> None:
        self._dispatch(parse_tst(_load(command_json)), now_s, tst=True)

    def abort_all(self, now_s: float) -> None:
        self._stop_all(WaraPSTaskStates.ABORTED, unit=True, retry=True)

    # ---- time ---------------------------------------------------------------

    def publish_status(self, now_s: float) -> None:
        self._forget_silent_servers(now_s)
        available = list(self.available.values())
        self._publish_direct_execution_info(
            direct_execution_info(self._name, self._rate_hz, now_s, available, self.executing))
        self._publish_tst_execution_info(
            tst_execution_info(self._name, self._rate_hz, now_s, available, self.executing))
        self._publish_executing_tasks(executing_tasks(self.executing))
        for task in self.executing:
            text = getattr(task.client.poll(), 'feedback', '')
            self._send_feedback(task, text)
        self._publish_health(self.health())

    def health(self) -> int:
        return officer_health(
            self.executing, SMARCActionClient.RUNNING_STATES, SMARCActionClient.States.CANCELLING)

    def advance_tasks(self, now_s: float) -> None:
        if not self._health_ready(now_s) and self.executing:
            word = health_word(self._health_value, fresh(self._health_stamp_s, now_s, self._health_timeout_s))
            self._stop_all(WaraPSTaskStates.ABORTED, unit=False, text=f'vehicle health {word}')
        if self._mission_expired(now_s):
            self._stop_all(WaraPSTaskStates.ABORTED, unit=False, text='mission timeout exceeded')
        for task in list(self.executing):
            self._advance_task(task, now_s)
        self._publish_health(self.health())

    # ---- commands -----------------------------------------------------------

    def _dispatch(
        self,
        command: Rejection | Ping | QueryTask | SignalTask | SignalUnit | StartTask | Mission,
        now_s: float,
        tst: bool,
    ) -> None:
        respond = self._publish_tst_response if tst else self._publish_exec_response
        if isinstance(command, Rejection):
            respond(exec_response(self.agent_uuid, command.com_uuid, command.reason))
        elif isinstance(command, Ping):
            respond(exec_response(self.agent_uuid, command.com_uuid, 'pong'))
        elif isinstance(command, QueryTask):
            respond(exec_response(self.agent_uuid, command.com_uuid, self._status_of(command.task_uuid)))
        elif isinstance(command, SignalTask):
            self._signal_task(command)
        elif isinstance(command, SignalUnit):
            self._signal_unit(command, respond)
        elif isinstance(command, StartTask):
            self._start_one(command, now_s, tst_uuid=None)
        elif isinstance(command, Mission):
            self._start_mission(command, now_s)

    def _start_one(self, task: StartTask, now_s: float, tst_uuid: str | None) -> None:
        respond = self._publish_tst_response if tst_uuid is not None else self._publish_exec_response
        refusal = self._refusal_for(task.name, now_s)
        if refusal is not None:
            respond(exec_response(self.agent_uuid, task.com_uuid, refusal))
            return
        server = self._server_for(task.name)
        self.executing.append(ExecutingTask(
            uuid=task.task_uuid,
            name=task.name,
            ros_name=server.ros_name,
            params=task.params,
            description=task.description,
            status=WaraPSTaskStates.STARTED,
            client=self.clients[server.ros_name],
            com_uuid=task.com_uuid,
            tst_uuid=tst_uuid,
            timeout_s=task.timeout_s,
        ))
        if tst_uuid is not None:
            respond(exec_response(self.agent_uuid, task.com_uuid, 'accepted'))
            return
        self._publish_exec_response(start_response(self.agent_uuid, task.com_uuid, task))

    def _start_mission(self, mission: Mission, now_s: float) -> None:
        def reject(reason: str) -> None:
            self._publish_tst_response(exec_response(self.agent_uuid, mission.com_uuid, reason))

        if self._mission is not None:
            reject('task already executing on a mission')
            return
        for leaf in each_leaf(mission.root):
            server = self._server_for(leaf.name)
            if server is None:
                reject('task not available')
                return
            busy = self._task_on_server(server.ros_name)
            if busy is not None:
                reject(f'task already executing on {busy.name}')
                return
        if not self._health_ready(now_s):
            reject('rejected: vehicle health status is not ok')
            return
        run, follow = open_run(mission.root)
        seen = set()
        for leaf in follow.start:
            ros_name = self._server_for(leaf.name).ros_name
            if ros_name in seen:
                reject(f'rejected: {leaf.name} would run twice at once')
                return
            seen.add(ros_name)
        self._mission = mission
        self._mission_started_s = now_s
        self._run = run
        self._publish_tst_response(exec_response(self.agent_uuid, mission.com_uuid, 'accepted'))
        if follow.done:
            self._mission = None
            self._run = None
            return
        for leaf in follow.start:
            self._start_leaf(leaf, now_s)

    def _refusal_for(self, name: str, now_s: float) -> str | None:
        if not self._health_ready(now_s):
            return 'rejected: vehicle health status is not ok'
        server = self._server_for(name)
        if server is None:
            return 'task not available'
        busy = self._task_on_server(server.ros_name)
        if busy is not None:
            return f'task already executing on {busy.name}'
        return None

    def _task_on_server(self, ros_name: str) -> ExecutingTask | None:
        for task in self.executing:
            if task.ros_name == ros_name:
                return task
        return None

    def _signal_task(self, signal: SignalTask) -> None:
        task = next((item for item in self.executing if item.uuid == signal.task_uuid), None)
        if task is None:
            self._publish_exec_response(exec_response(self.agent_uuid, signal.com_uuid, 'task not in current tasks'))
            return
        if signal.signal == WaraPSCommandSignals.PAUSE:
            task.status = WaraPSTaskStates.PAUSED
        elif signal.signal == WaraPSCommandSignals.CONTINUE and task.status == WaraPSTaskStates.PAUSED:
            task.status = _status_after_continue(task)
        elif signal.signal in _STOP_STATUS:
            task.cancel_refused = False
            self._mission = None
            self._run = None
            self._mark_stopping(task, _STOP_STATUS[signal.signal], reason=None)
        self._publish_exec_response(exec_response(self.agent_uuid, signal.com_uuid, 'ok'))

    def _signal_unit(self, signal: SignalUnit, respond: Callable[[ExecReply], None]) -> None:
        if signal.signal == WaraPSCommandSignals.PAUSE:
            for task in self.executing:
                task.status = WaraPSTaskStates.PAUSED
        elif signal.signal == WaraPSCommandSignals.CONTINUE:
            for task in self.executing:
                if task.status == WaraPSTaskStates.PAUSED:
                    task.status = _status_after_continue(task)
        respond(exec_response(self.agent_uuid, signal.com_uuid, 'ok'))
        if signal.signal in _STOP:
            self._stop_all(
                _STOP_STATUS[signal.signal],
                unit=signal.signal == WaraPSCommandSignals.ABORT,
                retry=True,
            )

    def _stop_all(
        self,
        status: WaraPSTaskStates,
        unit: bool,
        text: str | None = None,
        retry: bool = False,
    ) -> None:
        """Ask every executing task to stop. The task stays until the server answers."""
        if unit:
            self._publish_abort()
        for task in list(self.executing):
            if task.cancel_refused and not retry:
                if task.stop_reason == text:
                    continue
                task.cancel_refused = False
            if retry:
                task.cancel_refused = False
            if task.status in (WaraPSTaskStates.ABORTED, WaraPSTaskStates.ENOUGH):
                if not retry and task.client.poll().cancel_refused:
                    continue
                _cancel(task)
                continue
            self._mark_stopping(task, status, text)
            if text is not None:
                self._send_feedback(task, f'cancelling: {text}')
        self._mission = None
        self._run = None

    # ---- one executing task -------------------------------------------------

    def _advance_task(self, task: ExecutingTask, now_s: float) -> None:
        report = task.client.poll()
        state = report.state
        # The server refused the cancel and keeps the goal running. Report that once and
        # treat the task as running again; only a new stop (health, abort, timeout) asks again.
        if report.cancel_refused and not task.cancel_refused:
            if task.status != WaraPSTaskStates.PAUSED:
                task.status = WaraPSTaskStates.RUNNING
            task.cancel_refused = True
            self._send_feedback(task, 'cancel refused: action still running')
            return
        # A stop was asked for; the task only leaves once the server answers the cancel.
        if task.status in (WaraPSTaskStates.ABORTED, WaraPSTaskStates.ENOUGH):
            self._see_cancel_through(task, report, now_s)
            return
        # WARA-PS pause has no action-level equivalent: a paused task cancels its goal and
        # sends a fresh one on continue. READY after a pause just waits for that continue.
        if task.status == WaraPSTaskStates.PAUSED:
            if state in SMARCActionClient.RUNNING_STATES:
                if not task.cancel_refused:
                    task.client.cancel()
                return
            if state is SMARCActionClient.States.CANCELLED:
                task.client.get_ready()
                return
            if state is SMARCActionClient.States.READY:
                return
        # A new or resumed task has no goal out yet. A server that went quiet is pinged
        # instead of sent to, so the goal is not lost into a dead server.
        if task.status in (WaraPSTaskStates.STARTED, WaraPSTaskStates.RESUMED):
            if state is SMARCActionClient.States.DISCONNECTED:
                task.client.server_alive(timeout_s=0.0)
            elif state is SMARCActionClient.States.READY:
                if task.client.send(json.dumps(task.params), task.timeout_s):
                    task.status = WaraPSTaskStates.RUNNING
            return
        # The client has already asked a timed-out goal to cancel. Until the server lets
        # go it is still moving the vehicle, so it stays on the list.
        if report.timed_out and state in SMARCActionClient.RUNNING_STATES:
            return
        if report.timed_out or state in SMARCActionClient.FAILURE_STATES or state is SMARCActionClient.States.DONE:
            task.status = WaraPSTaskStates.FINISHED if state is SMARCActionClient.States.DONE else WaraPSTaskStates.ERROR
            text = report.feedback or f'Action client in failure state: {state}.'
            if state is SMARCActionClient.States.DONE:
                text = report.feedback
            self._send_feedback(task, text)
            self._remove_from_executing(task)
            self._continue_mission_after(task, now_s)

    def _see_cancel_through(self, task: ExecutingTask, report: ClientReport, now_s: float) -> None:
        """A cancel is a request. The task leaves when the server answers it."""
        state = report.state
        # Still running: the cancel has not landed yet. _cancel re-sends only when the goal
        # is not already CANCELLING, so this does not repeat a cancel that is in flight.
        if state in SMARCActionClient.RUNNING_STATES:
            _cancel(task)
            return
        # The server let go of the goal: this stop is done.
        if state is SMARCActionClient.States.CANCELLED or state is SMARCActionClient.States.READY:
            text = f'cancelled: {task.stop_reason}' if task.stop_reason else 'cancelled'
        # It finished before the cancel arrived, so it is reported as finished, not cancelled.
        elif state is SMARCActionClient.States.DONE:
            task.status = WaraPSTaskStates.FINISHED
            text = report.feedback
        else:
            task.status = WaraPSTaskStates.ERROR
            text = report.feedback or f'Action client in failure state: {state}.'
        self._send_feedback(task, text)
        self._remove_from_executing(task)
        self._continue_mission_after(task, now_s)

    def _continue_mission_after(self, task: ExecutingTask, now_s: float) -> None:
        if self._run is None or task.uuid not in self._run.by_uuid:
            return
        self._apply_mission_step(after_leaf(self._run, task.uuid, task.status), now_s)

    def _apply_mission_step(self, step: Follow, now_s: float) -> None:
        self._cancel_siblings(step.cancel)
        for leaf in step.start:
            self._start_leaf(leaf, now_s)
        if step.done:
            self._mission = None
            self._run = None

    def _cancel_siblings(self, uuids: list[str]) -> None:
        """Ask those tasks to cancel, and wait. Same path as any other cancel."""
        if not uuids:
            return
        wanted = set(uuids)
        for task in list(self.executing):
            if task.uuid not in wanted:
                continue
            task.cancel_refused = False
            self._mark_stopping(task, WaraPSTaskStates.ENOUGH, 'stop-on-first')
            self._send_feedback(task, 'cancelling: stop-on-first')

    def _mark_stopping(self, task: ExecutingTask, status: WaraPSTaskStates, reason: str | None) -> None:
        task.status = status
        task.stop_reason = reason
        _cancel(task)

    def _start_leaf(self, leaf: Leaf, now_s: float) -> None:
        mission = self._mission
        server = self._server_for(leaf.name) if mission is not None else None
        busy = None if server is None else self._task_on_server(server.ros_name)
        if server is None or busy is not None:
            reason = 'task not available' if busy is None else f'task already executing on {busy.name}'
            tst = None if mission is None else mission.tst_uuid
            self._publish_tst_feedback(feedback(self.agent_uuid, leaf.task_uuid, reason, WaraPSTaskStates.ERROR, tst))
            if self._run is not None and leaf.task_uuid in self._run.by_uuid:
                self._apply_mission_step(after_leaf(self._run, leaf.task_uuid, WaraPSTaskStates.ERROR), now_s)
            return
        self.executing.append(ExecutingTask(
            uuid=leaf.task_uuid,
            name=leaf.name,
            ros_name=server.ros_name,
            params=leaf.params,
            description=leaf.description,
            status=WaraPSTaskStates.STARTED,
            client=self.clients[server.ros_name],
            com_uuid=mission.com_uuid,
            tst_uuid=mission.tst_uuid,
            timeout_s=leaf.timeout_s,
        ))

    def _remove_from_executing(self, task: ExecutingTask) -> None:
        if task in self.executing:
            self.executing.remove(task)
        task.client.get_ready()

    def _send_feedback(self, task: ExecutingTask, text: str) -> None:
        """A task from a mission reports on the TST feedback topic, a direct one on exec."""
        message = feedback(self.agent_uuid, task.uuid, text, task.status, task.tst_uuid)
        if task.tst_uuid:
            self._publish_tst_feedback(message)
        else:
            self._publish_exec_feedback(message)

    # ---- lookups ------------------------------------------------------------

    def _server_for(self, name: str) -> AvailableTask | None:
        for task in self.available.values():
            if task.name == name:
                return task
        return None

    def _status_of(self, task_uuid: str) -> str:
        for task in self.executing:
            if task.uuid == task_uuid:
                return task.status
        return 'task not found'

    def _forget_silent_servers(self, now_s: float) -> None:
        # A server busy with one of our goals stays known even if it skips heartbeats.
        busy = {item.ros_name for item in self.executing}
        stale = [ros_name for ros_name, task in self.available.items()
                 if now_s - task.last_seen > self._liveliness_s and ros_name not in busy]
        for ros_name in stale:
            self.available.pop(ros_name, None)

    def _health_ready(self, now_s: float) -> bool:
        return health_is_ready(self._health_value, self._health_stamp_s, now_s, self._health_timeout_s)

    def _mission_expired(self, now_s: float) -> bool:
        if self._mission is None or self._mission_started_s is None:
            return False
        return now_s - self._mission_started_s > self._mission.timeout_s


def _load(text: str) -> dict:
    try:
        payload = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _status_after_continue(task: ExecutingTask) -> WaraPSTaskStates:
    """A refused pause left the goal running. Continue means that, not a new send.

    Read ``state`` directly. ``poll()`` cancels a goal that has timed out.
    """
    if task.client.state is SMARCActionClient.States.RUNNING:
        return WaraPSTaskStates.RUNNING
    return WaraPSTaskStates.RESUMED


def _cancel(task: ExecutingTask) -> None:
    report = task.client.poll()
    if report.state in SMARCActionClient.RUNNING_STATES and report.state is not SMARCActionClient.States.CANCELLING:
        task.client.cancel()
