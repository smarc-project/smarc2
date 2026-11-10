"""GentlerActionClient against a real GentlerActionServer on a private domain."""

import json
import time

import pytest

from smarc_action_base.gentler_action_client import GentlerActionClient
from smarc_action_base.gentler_action_server import GentlerActionServer
from smarc_action_base.smarc_action_base import ActionClientState

ACTION = 'wait'


class ScriptedServer:
    """A GentlerActionServer whose loop_inner follows a script.

    ``ticks_to_finish`` loop calls return None, then ``outcome`` is returned
    (True = succeed, False = fail, None = run until cancelled).
    ``accept_delay_s`` holds the goal response, so a test can act while the
    client is still SENT.
    """

    def __init__(self, node, ticks_to_finish=3, outcome=True, accept_goals=True,
                 accept_delay_s=0.0):
        self.ticks_to_finish = ticks_to_finish
        self.outcome = outcome
        self.accept_goals = accept_goals
        self.accept_delay_s = accept_delay_s
        self.goals = []
        self.cancels = 0
        self.ticks = 0
        self.server = GentlerActionServer(
            node, ACTION,
            self.on_goal, self.on_cancel, self.prepare, self.loop, self.feedback,
            loop_frequency=20.0)

    def on_goal(self, goal):
        time.sleep(self.accept_delay_s)
        self.goals.append(goal)
        return self.accept_goals

    def on_cancel(self):
        self.cancels += 1
        return True

    def prepare(self):
        self.ticks = 0

    def loop(self):
        self.ticks += 1
        if self.ticks < self.ticks_to_finish:
            return None
        return self.outcome

    def feedback(self):
        return f'tick {self.ticks}'


def wait_for(predicate, timeout_s=5.0, period_s=0.02):
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        result = predicate()
        if result:
            return result
        time.sleep(period_s)
    return predicate()


def finished(client):
    return client.poll().finished


def test_server_alive_is_false_without_a_server(ros_graph):
    client = GentlerActionClient(ros_graph('client'), ACTION)
    assert client.server_alive(timeout_s=0.3) is False
    assert client.state is ActionClientState.DISCONNECTED


def test_goal_runs_to_done_with_feedback(ros_graph):
    server = ScriptedServer(ros_graph('server'), ticks_to_finish=4, outcome=True)
    client = GentlerActionClient(ros_graph('client'), ACTION)
    assert client.server_alive()
    assert client.state is ActionClientState.READY

    assert client.send(json.dumps({'seconds': 1})) is True
    assert wait_for(lambda: finished(client))

    report = client.poll()
    assert report.succeeded
    assert report.state is ActionClientState.DONE
    assert report.feedback.startswith('tick ')
    assert report.timed_out is False
    assert report.elapsed_s > 0
    assert server.goals == [{'seconds': 1}]


def test_failed_goal_is_error(ros_graph):
    ScriptedServer(ros_graph('server'), ticks_to_finish=2, outcome=False)
    client = GentlerActionClient(ros_graph('client'), ACTION)
    assert client.server_alive()
    assert client.send('{}')
    assert wait_for(lambda: finished(client))
    assert client.poll().state is ActionClientState.ERROR


def test_rejected_goal_is_rejected(ros_graph):
    ScriptedServer(ros_graph('server'), accept_goals=False)
    client = GentlerActionClient(ros_graph('client'), ACTION)
    assert client.server_alive()
    assert client.send('{}')
    assert wait_for(lambda: finished(client))
    assert client.poll().state is ActionClientState.REJECTED


def test_cancel_mid_run(ros_graph):
    server = ScriptedServer(ros_graph('server'), outcome=None)
    client = GentlerActionClient(ros_graph('client'), ACTION)
    assert client.server_alive()
    assert client.send('{}')
    assert wait_for(lambda: client.poll().state is ActionClientState.RUNNING)

    client.cancel()
    assert wait_for(lambda: finished(client))
    assert client.poll().state is ActionClientState.CANCELLED
    assert server.cancels == 1


def test_cancel_right_after_send_still_cancels(ros_graph):
    """The server has not answered yet, so there is no goal handle to cancel.
    The cancel must be kept and sent once the goal is accepted."""
    server = ScriptedServer(ros_graph('server'), outcome=None, accept_delay_s=0.3)
    client = GentlerActionClient(ros_graph('client'), ACTION)
    assert client.server_alive()
    assert client.send('{}')
    assert client.state is ActionClientState.SENT
    client.cancel()
    assert client.state is ActionClientState.SENT               # nothing to cancel yet

    assert wait_for(lambda: finished(client))
    assert client.poll().state is ActionClientState.CANCELLED
    assert server.cancels == 1


def test_cancel_right_after_a_second_send_cancels_the_second_goal(ros_graph):
    """After one finished goal the client still holds that goal's handle.
    A cancel during the next SENT must wait for the new handle, not fire on
    the old one."""
    server = ScriptedServer(ros_graph('server'), ticks_to_finish=2, outcome=True,
                            accept_delay_s=0.3)
    client = GentlerActionClient(ros_graph('client'), ACTION)
    assert client.server_alive()
    assert client.send(json.dumps({'n': 1}))
    assert wait_for(lambda: finished(client))
    assert client.poll().succeeded

    server.outcome = None
    client.get_ready()
    assert client.send(json.dumps({'n': 2}))
    client.cancel()

    assert wait_for(lambda: finished(client))
    assert client.poll().state is ActionClientState.CANCELLED
    assert server.goals == [{'n': 1}, {'n': 2}]
    assert server.cancels == 1


def test_timeout_cancels_from_the_client_side(ros_graph):
    server = ScriptedServer(ros_graph('server'), outcome=None)
    client = GentlerActionClient(ros_graph('client'), ACTION, timeout_s=0.5)
    assert client.server_alive()
    assert client.send('{}')

    assert wait_for(lambda: finished(client), timeout_s=5.0)
    report = client.poll()
    assert report.timed_out is True
    assert report.state is ActionClientState.CANCELLED
    assert report.elapsed_s >= 0.5
    assert server.cancels == 1


def test_send_is_refused_unless_ready(ros_graph):
    ScriptedServer(ros_graph('server'), outcome=None)
    client = GentlerActionClient(ros_graph('client'), ACTION)
    assert client.send('{}') is False                       # DISCONNECTED
    assert client.server_alive()
    assert client.send('{}') is True
    assert client.send('{}') is False                       # already running
    client.cancel()
    assert wait_for(lambda: finished(client))
    assert client.send('{}') is False                       # finished, not reset


def test_get_ready_allows_a_second_goal(ros_graph):
    server = ScriptedServer(ros_graph('server'), ticks_to_finish=2, outcome=True)
    client = GentlerActionClient(ros_graph('client'), ACTION)
    assert client.server_alive()

    assert client.send(json.dumps({'n': 1}))
    assert wait_for(lambda: finished(client))
    assert client.poll().succeeded

    client.get_ready()
    report = client.poll()
    assert report.state is ActionClientState.READY
    assert report.feedback == ''
    assert report.elapsed_s == 0.0

    assert client.send(json.dumps({'n': 2}))
    assert wait_for(lambda: finished(client))
    assert client.poll().succeeded
    assert server.goals == [{'n': 1}, {'n': 2}]


@pytest.mark.parametrize('state, running, done', [
    (ActionClientState.READY, False, False),
    (ActionClientState.SENT, True, False),
    (ActionClientState.RUNNING, True, False),
    (ActionClientState.CANCELLING, True, False),
    (ActionClientState.DONE, False, True),
    (ActionClientState.ERROR, False, True),
    (ActionClientState.REJECTED, False, True),
    (ActionClientState.CANCELLED, False, True),
    (ActionClientState.DISCONNECTED, False, True),
])
def test_report_classifies_states(state, running, done):
    from smarc_action_base.gentler_action_client import ClientReport
    report = ClientReport(state, '', 0.0, False)
    assert report.running is running
    assert report.finished is done
    assert report.succeeded is (state is ActionClientState.DONE)
