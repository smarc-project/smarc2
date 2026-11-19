"""WarapsOfficer on a private graph, with a GentlerActionServer as the task."""

import json

import pytest
from rclpy.parameter import Parameter
from smarc_action_base.gentler_action_server import GentlerActionServer
from smarc_msgs.msg import Topics
from smarc_utilities.testing import wait_for
from std_msgs.msg import Int8, String

from waraps_officer.officer import WarapsOfficer

ROOT = '/sam0'


class Heard:
    def __init__(self, node, topics):
        self.last = {}
        for topic in topics:
            node.create_subscription(String, topic, self._cb(topic), 10)

    def _cb(self, topic):
        def cb(msg):
            self.last[topic] = json.loads(msg.data)
        return cb


def _officer(ros_graph, **params):
    overrides = [Parameter('robot_name', value='sam0'), Parameter('pulse_rate', value=10.0),
                 Parameter('tick_rate', value=20.0), Parameter('health_timeout_s', value=5.0)]
    overrides += [Parameter(name, value=value) for name, value in params.items()]
    node = ros_graph('waraps_officer', ROOT, parameter_overrides=overrides)
    WarapsOfficer(node)
    return node


def test_robot_name_is_required(ros_graph):
    with pytest.raises(ValueError, match='robot_name'):
        WarapsOfficer(ros_graph('waraps_officer', ROOT))


def test_health_error_rejects_the_start(ros_graph):
    _officer(ros_graph)
    captain = ros_graph('captain', ROOT)
    health = captain.create_publisher(Int8, Topics.VEHICLE_HEALTH_TOPIC, 10)
    command = captain.create_publisher(String, Topics.WARA_PS_EXEC_COMMAND_TOPIC, 10)
    heard = Heard(ros_graph('listener', ROOT), [Topics.WARA_PS_EXEC_RESPONSE_TOPIC])

    def send():
        health.publish(Int8(data=Topics.VEHICLE_HEALTH_ERROR))
        command.publish(String(data=json.dumps({
            'command': 'start-task', 'com-uuid': 'c', 'task-uuid': 't',
            'task': {'name': 'wait', 'params': {}},
        })))
        return heard.last.get(Topics.WARA_PS_EXEC_RESPONSE_TOPIC)

    response = wait_for(send)
    assert response['response'] == 'rejected: vehicle health status is not ok'


def test_a_task_runs_and_the_executing_list_empties(ros_graph):
    ticks = {'n': 0}

    def loop():
        ticks['n'] += 1
        return True if ticks['n'] >= 3 else None

    server = ros_graph('wait_server', ROOT)
    GentlerActionServer(server, 'wait', lambda goal: True, lambda: True, lambda: None, loop, lambda: 'working', 20.0)
    _officer(ros_graph)

    captain = ros_graph('captain', ROOT)
    health = captain.create_publisher(Int8, Topics.VEHICLE_HEALTH_TOPIC, 10)
    heartbeats = captain.create_publisher(String, Topics.WARA_PS_ACTION_SERVER_HB_TOPIC, 10)
    command = captain.create_publisher(String, Topics.WARA_PS_EXEC_COMMAND_TOPIC, 10)
    heard = Heard(ros_graph('listener', ROOT), [
        Topics.WARA_PS_DIRECT_EXECUTION_INFO_TOPIC,
        Topics.WARA_PS_EXEC_RESPONSE_TOPIC,
        Topics.WARA_PS_EXEC_FEEDBACK_TOPIC,
        Topics.WARA_PS_SENSOR_EXECUTING_TASKS_TOPIC,
    ])
    def advertise():
        health.publish(Int8(data=Topics.VEHICLE_HEALTH_READY))
        heartbeats.publish(String(data='/sam0/wait'))
        info = heard.last.get(Topics.WARA_PS_DIRECT_EXECUTION_INFO_TOPIC) or {}
        return any(task['name'] == 'wait' for task in info.get('tasks-available', []))

    wait_for(advertise)

    def start():
        health.publish(Int8(data=Topics.VEHICLE_HEALTH_READY))
        command.publish(String(data=json.dumps({
            'command': 'start-task', 'com-uuid': 'c', 'task-uuid': 't',
            'task': {'name': 'wait', 'params': {}},
        })))
        response = heard.last.get(Topics.WARA_PS_EXEC_RESPONSE_TOPIC) or {}
        return response if response.get('status') == 'started' else None

    started = wait_for(start)
    assert started['task-uuid'] == 't'
    feedback = wait_for(lambda: heard.last.get(Topics.WARA_PS_EXEC_FEEDBACK_TOPIC))
    assert feedback['task-uuid'] == 't'
    assert wait_for(lambda: heard.last.get(Topics.WARA_PS_SENSOR_EXECUTING_TASKS_TOPIC) == [])
