"""WARA-PS levels 2 and 3: one task at a time, over GentlerActionClient.

``Officer`` holds the tasks and decides. ``WarapsOfficer`` is the node: it
subscribes, publishes, and calls ``Officer`` on a timer. A second task is
rejected while one is running; a TST ``seq`` starts its next leaf when the
current one finishes.
"""

import json

import rclpy
from rclpy.node import Node
from smarc_action_base.smarc_action_base import SMARCActionClient
from smarc_msgs.msg import Topics
from std_msgs.msg import Empty, Int8, String

from waraps_officer.commands import (
    Mission,
    Ping,
    QueryTask,
    Rejection,
    SignalTask,
    SignalUnit,
    StartTask,
    direct_execution_info,
    dumps,
    exec_response,
    executing_tasks,
    feedback,
    health_is_ready,
    health_word,
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


class Officer:
    def __init__(self, client_factory, name, rate_hz, liveliness_s, health_timeout_s):
        self._client_factory = client_factory
        self._name = name
        self._rate_hz = rate_hz
        self._liveliness_s = liveliness_s
        self._health_timeout_s = health_timeout_s
        self.agent_uuid = ''
        self.available: dict[str, AvailableTask] = {}
        self.clients: dict[str, object] = {}
        self.executing: list[ExecutingTask] = []
        self._mission: Mission | None = None
        self._mission_started_s: float | None = None
        self._health_value = None
        self._health_stamp_s = None

    # ---- things other nodes say --------------------------------------------

    def on_level1_heartbeat(self, text) -> bool:
        """Take agent-uuid from the first heartbeat. True means unsubscribe."""
        if self.agent_uuid:
            return True
        try:
            payload = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return False
        uuid = payload.get('agent-uuid') if isinstance(payload, dict) else None
        if not uuid:
            return False
        self.agent_uuid = uuid
        return True

    def on_action_heartbeat(self, ros_name, now_s):
        ros_name = (ros_name or '').strip()
        if not ros_name:
            return
        name = waraps_task_name(ros_name)
        self.available[ros_name] = AvailableTask(name, ros_name, now_s)
        if ros_name not in self.clients:
            self.clients[ros_name] = self._client_factory(ros_name)

    def on_health(self, value, now_s):
        self._health_value = value
        self._health_stamp_s = now_s

    def on_exec(self, text, now_s):
        return self._dispatch(parse_exec_command(_load(text)), now_s, tst=False)

    def on_tst(self, text, now_s):
        return self._dispatch(parse_tst(_load(text)), now_s, tst=True)

    def on_waraps_abort(self, now_s):
        return self._stop_all(WaraPSTaskStates.ABORTED, unit=True)

    # ---- time ---------------------------------------------------------------

    def pulse(self, now_s):
        self._prune(now_s)
        available = list(self.available.values())
        out = [
            ('direct_info', direct_execution_info(self._name, self._rate_hz, now_s, available, self.executing)),
            ('tst_info', tst_execution_info(self._name, self._rate_hz, now_s, available, self.executing)),
            ('executing', executing_tasks(self.executing)),
        ]
        for task in self.executing:
            text = getattr(task.client.poll(), 'feedback', '')
            out.append(self._feedback(task, text))
        return out

    def step(self, now_s):
        out = []
        if not self._health_ready(now_s) and self.executing:
            word = health_word(self._health_value, fresh(self._health_stamp_s, now_s, self._health_timeout_s))
            out.extend(self._stop_all(WaraPSTaskStates.ABORTED, unit=False,
                                      text=f'cancelled: vehicle health {word}'))
        if self._mission_expired(now_s):
            out.extend(self._stop_all(WaraPSTaskStates.ABORTED, unit=False, text='mission timeout exceeded'))
        for task in list(self.executing):
            out.extend(self._advance(task, now_s))
        return out

    # ---- commands -----------------------------------------------------------

    def _dispatch(self, command, now_s, tst):
        channel = 'tst_response' if tst else 'exec_response'
        if isinstance(command, Rejection):
            return [(channel, exec_response(self.agent_uuid, command.com_uuid, command.reason))]
        if isinstance(command, Ping):
            return [(channel, exec_response(self.agent_uuid, command.com_uuid, 'pong'))]
        if isinstance(command, QueryTask):
            return [(channel, exec_response(self.agent_uuid, command.com_uuid, self._status_of(command.task_uuid)))]
        if isinstance(command, SignalTask):
            return self._signal_task(command)
        if isinstance(command, SignalUnit):
            return self._signal_unit(command, channel)
        if isinstance(command, StartTask):
            return self._start_one(command, now_s, tst_uuid=None)
        if isinstance(command, Mission):
            return self._start_mission(command, now_s)
        return []

    def _start_one(self, task: StartTask, now_s, tst_uuid):
        channel = 'tst_response' if tst_uuid is not None else 'exec_response'
        refusal = self._refuse(task.name, now_s)
        if refusal is not None:
            return [(channel, exec_response(self.agent_uuid, task.com_uuid, refusal))]
        available = self._find(task.name)
        self.executing.append(ExecutingTask(
            uuid=task.task_uuid, name=task.name, ros_name=available.ros_name, params=task.params,
            description=task.description, status=WaraPSTaskStates.STARTED, client=self.clients[available.ros_name],
            com_uuid=task.com_uuid, tst_uuid=tst_uuid, timeout_s=task.timeout_s,
        ))
        if tst_uuid is not None:
            return [(channel, exec_response(self.agent_uuid, task.com_uuid, 'accepted'))]
        return [('exec_response', start_response(self.agent_uuid, task.com_uuid, task))]

    def _start_mission(self, mission: Mission, now_s):
        if self.executing or self._mission is not None:
            name = self.executing[0].name if self.executing else 'a mission'
            return [('tst_response', exec_response(self.agent_uuid, mission.com_uuid, f'task already executing on {name}'))]
        for leaf in mission.leaves:
            if self._find(leaf.name) is None:
                return [('tst_response', exec_response(self.agent_uuid, mission.com_uuid, 'task not available'))]
        if not self._health_ready(now_s):
            return [('tst_response', exec_response(self.agent_uuid, mission.com_uuid, 'rejected: vehicle health status is not ok'))]
        self._mission = mission
        self._mission_started_s = now_s
        if not mission.leaves:
            self._mission = None
            return [('tst_response', exec_response(self.agent_uuid, mission.com_uuid, 'accepted'))]
        first, rest = mission.leaves[0], mission.leaves[1:]
        self._mission = Mission(mission.com_uuid, mission.tst_uuid, mission.timeout_s, rest)
        started = self._start_one(_leaf_as_start(mission.com_uuid, first), now_s, mission.tst_uuid)
        # _start_one would also refuse health; health was checked above.
        return started

    def _refuse(self, name, now_s):
        if not self._health_ready(now_s):
            return 'rejected: vehicle health status is not ok'
        if self._find(name) is None:
            return 'task not available'
        if self.executing:
            return f'task already executing on {self.executing[0].name}'
        return None

    def _signal_task(self, signal: SignalTask):
        task = next((item for item in self.executing if item.uuid == signal.task_uuid), None)
        if task is None:
            return [('exec_response', exec_response(self.agent_uuid, signal.com_uuid, 'task not in current tasks'))]
        if signal.signal == WaraPSCommandSignals.PAUSE:
            task.status = WaraPSTaskStates.PAUSED
        elif signal.signal == WaraPSCommandSignals.CONTINUE and task.status == WaraPSTaskStates.PAUSED:
            task.status = WaraPSTaskStates.RESUMED
        elif signal.signal in _STOP_STATUS:
            task.status = _STOP_STATUS[signal.signal]
        return [('exec_response', exec_response(self.agent_uuid, signal.com_uuid, 'ok'))]

    def _signal_unit(self, signal: SignalUnit, channel):
        if signal.signal == WaraPSCommandSignals.PAUSE:
            for task in self.executing:
                task.status = WaraPSTaskStates.PAUSED
        elif signal.signal == WaraPSCommandSignals.CONTINUE:
            for task in self.executing:
                if task.status == WaraPSTaskStates.PAUSED:
                    task.status = WaraPSTaskStates.RESUMED
        elif signal.signal in _STOP:
            return [(channel, exec_response(self.agent_uuid, signal.com_uuid, 'ok'))] + \
                self._stop_all(_STOP_STATUS[signal.signal], unit=signal.signal == WaraPSCommandSignals.ABORT)
        return [(channel, exec_response(self.agent_uuid, signal.com_uuid, 'ok'))]

    def _stop_all(self, status, unit, text=None):
        out = [('abort', None)] if unit else []
        for task in list(self.executing):
            task.status = status
            _cancel(task)
            if text is not None:
                out.append(self._feedback(task, text))
            self.executing.remove(task)
        self._mission = None
        return out

    # ---- one executing task -------------------------------------------------

    def _advance(self, task: ExecutingTask, now_s):
        report = task.client.poll()
        state = report.state
        if task.status in (WaraPSTaskStates.ABORTED, WaraPSTaskStates.ENOUGH):
            _cancel(task)
            self._retire(task)
            return []
        if task.status == WaraPSTaskStates.PAUSED:
            if state in SMARCActionClient.RUNNING_STATES:
                task.client.cancel()
            elif state is not SMARCActionClient.States.READY:
                task.client.get_ready()
            return []
        if task.status in (WaraPSTaskStates.STARTED, WaraPSTaskStates.RESUMED):
            if state is SMARCActionClient.States.DISCONNECTED:
                task.client.server_alive(timeout_s=0.0)
            elif state is SMARCActionClient.States.READY:
                if task.client.send(json.dumps(task.params), task.timeout_s):
                    task.status = WaraPSTaskStates.RUNNING
            return []
        if getattr(report, 'timed_out', False) or state in SMARCActionClient.FAILURE_STATES or state is SMARCActionClient.States.DONE:
            task.status = WaraPSTaskStates.FINISHED if state is SMARCActionClient.States.DONE else WaraPSTaskStates.ERROR
            text = report.feedback or f'Action client in failure state: {state}.'
            if state is SMARCActionClient.States.DONE:
                text = report.feedback
            out = [self._feedback(task, text)]
            self._retire(task)
            out.extend(self._next_leaf(now_s, task.status))
            return out
        return []

    def _next_leaf(self, now_s, status):
        mission = self._mission
        if mission is None:
            return []
        if status != WaraPSTaskStates.FINISHED or not mission.leaves:
            self._mission = None
            return []
        leaf, rest = mission.leaves[0], mission.leaves[1:]
        available = self._find(leaf.name)
        if available is None:
            self._mission = None
            return [('tst_feedback', feedback(self.agent_uuid, leaf.task_uuid, 'task not available', WaraPSTaskStates.ERROR, mission.tst_uuid))]
        self._mission = Mission(mission.com_uuid, mission.tst_uuid, mission.timeout_s, rest)
        self.executing.append(ExecutingTask(
            uuid=leaf.task_uuid, name=leaf.name, ros_name=available.ros_name, params=leaf.params,
            description=leaf.description, status=WaraPSTaskStates.STARTED, client=self.clients[available.ros_name],
            com_uuid=mission.com_uuid, tst_uuid=mission.tst_uuid, timeout_s=leaf.timeout_s,
        ))
        return []

    def _retire(self, task):
        if task in self.executing:
            self.executing.remove(task)

    def _feedback(self, task, text):
        kind = 'tst_feedback' if task.tst_uuid else 'exec_feedback'
        return (kind, feedback(self.agent_uuid, task.uuid, text, task.status, task.tst_uuid))

    # ---- lookups ------------------------------------------------------------

    def _find(self, name):
        for task in self.available.values():
            if task.name == name:
                return task
        return None

    def _status_of(self, task_uuid):
        for task in self.executing:
            if task.uuid == task_uuid:
                return task.status
        return 'task not found'

    def _prune(self, now_s):
        stale = [ros_name for ros_name, task in self.available.items()
                 if now_s - task.last_seen > self._liveliness_s
                 and ros_name not in {item.ros_name for item in self.executing}]
        for ros_name in stale:
            self.available.pop(ros_name, None)

    def _health_ready(self, now_s):
        return health_is_ready(self._health_value, self._health_stamp_s, now_s, self._health_timeout_s)

    def _mission_expired(self, now_s):
        if self._mission is None or self._mission_started_s is None:
            return False
        return now_s - self._mission_started_s > self._mission.timeout_s


def _load(text):
    try:
        payload = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _leaf_as_start(com_uuid, leaf):
    return StartTask(com_uuid, leaf.task_uuid, leaf.name, leaf.params, leaf.description, leaf.timeout_s)


def _cancel(task):
    report = task.client.poll()
    if report.state in SMARCActionClient.RUNNING_STATES:
        task.client.cancel()


def gentler_client(node, ros_name):
    from smarc_action_base.gentler_action_client import GentlerActionClient

    class _Client:
        """Hands the goal its own timeout. The client keeps one timeout_s for its life."""

        def __init__(self):
            self._client = GentlerActionClient(node, ros_name, timeout_s=None)

        def poll(self):
            return self._client.poll()

        def send(self, goal_json, timeout_s):
            self._client._timeout_s = timeout_s
            return self._client.send(goal_json)

        def cancel(self):
            self._client.cancel()

        def get_ready(self):
            self._client.get_ready()

        def server_alive(self, timeout_s=0.0):
            return self._client.server_alive(timeout_s=timeout_s)

    return _Client()


class WarapsOfficer:
    def __init__(self, node: Node):
        gp = node.declare_parameter
        robot_name = gp('robot_name', '').value
        if not robot_name:
            raise ValueError('robot_name parameter is required')
        pulse_rate = gp('pulse_rate', 1.0).value
        self._node = node
        self._officer = Officer(
            client_factory=lambda ros_name: gentler_client(node, ros_name),
            name=robot_name,
            rate_hz=pulse_rate,
            liveliness_s=gp('task_liveliness_timeout', 10.0).value,
            health_timeout_s=gp('health_timeout_s', 10.0).value,
        )
        self._publishers = {
            'direct_info': node.create_publisher(String, Topics.WARA_PS_DIRECT_EXECUTION_INFO_TOPIC, 10),
            'tst_info': node.create_publisher(String, Topics.WARA_PS_TST_EXEC_INFO_TOPIC, 10),
            'exec_response': node.create_publisher(String, Topics.WARA_PS_EXEC_RESPONSE_TOPIC, 10),
            'exec_feedback': node.create_publisher(String, Topics.WARA_PS_EXEC_FEEDBACK_TOPIC, 10),
            'tst_response': node.create_publisher(String, Topics.WARA_PS_TST_RESPONSE_TOPIC, 10),
            'tst_feedback': node.create_publisher(String, Topics.WARA_PS_TST_FEEDBACK_TOPIC, 10),
            'executing': node.create_publisher(String, Topics.WARA_PS_SENSOR_EXECUTING_TASKS_TOPIC, 10),
            'abort': node.create_publisher(Empty, Topics.ABORT_TOPIC, 10),
        }
        node.create_subscription(String, Topics.WARA_PS_EXEC_COMMAND_TOPIC, self._exec_cb, 10)
        node.create_subscription(String, Topics.WARA_PS_TST_COMMAND_TOPIC, self._tst_cb, 10)
        node.create_subscription(String, Topics.WARA_PS_ABORT_TOPIC, self._abort_cb, 10)
        node.create_subscription(String, Topics.WARA_PS_ACTION_SERVER_HB_TOPIC, self._action_hb_cb, 10)
        node.create_subscription(Int8, Topics.VEHICLE_HEALTH_TOPIC, self._health_cb, 10)
        self._level1_sub = node.create_subscription(String, Topics.WARA_PS_HEARTBEAT_TOPIC, self._level1_cb, 10)
        node.create_timer(1.0 / pulse_rate, self._pulse)
        node.create_timer(1.0 / gp('tick_rate', 10.0).value, self._step)
        node.get_logger().info(f"waraps_officer '{robot_name}', pulse {pulse_rate} Hz")

    def _now(self):
        return self._node.get_clock().now().nanoseconds * 1e-9

    def _emit(self, outgoing):
        for kind, payload in outgoing:
            if kind == 'abort':
                self._publishers['abort'].publish(Empty())
            else:
                self._publishers[kind].publish(String(data=dumps(payload)))

    def _exec_cb(self, msg):
        self._emit(self._officer.on_exec(msg.data, self._now()))

    def _tst_cb(self, msg):
        self._emit(self._officer.on_tst(msg.data, self._now()))

    def _abort_cb(self, msg):
        self._emit(self._officer.on_waraps_abort(self._now()))

    def _health_cb(self, msg):
        self._officer.on_health(msg.data, self._now())

    def _action_hb_cb(self, msg):
        self._officer.on_action_heartbeat(msg.data, self._now())

    def _level1_cb(self, msg):
        if self._officer.on_level1_heartbeat(msg.data) and self._level1_sub is not None:
            self._node.destroy_subscription(self._level1_sub)
            self._level1_sub = None

    def _pulse(self):
        self._emit(self._officer.pulse(self._now()))

    def _step(self):
        self._emit(self._officer.step(self._now()))


def main(args=None):
    rclpy.init(args=args)
    node = Node('waraps_officer')
    WarapsOfficer(node)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
